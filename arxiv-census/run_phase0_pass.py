#!/usr/bin/env python3
"""
Phase0 fast census: Atom title+abstract+category → SKIP_HARD | FULLTEXT_QUEUE | UNCERTAIN_FULLTEXT.
No PDF. Every id recorded. Prefer finish this pass, then drain queue via run_fulltext_rerun --from-queue.
"""
from __future__ import annotations

import argparse
import json
import os
import random
import sqlite3
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from calendar import monthrange
from datetime import datetime, timezone
from pathlib import Path

from db_sync import ensure_work_db, export_phase0_compact, mirror_gzip
from score_phase0 import score_phase0

ROOT = Path(__file__).resolve().parent
WORK_DB = Path("/tmp/arxiv-census/census.sqlite")
API = "https://export.arxiv.org/api/query"
UA = "arxiv-census-phase0/1.0"
ATOM_NS = {
    "atom": "http://www.w3.org/2005/Atom",
    "opensearch": "http://a9.com/-/spec/opensearch/1.1/",
    "arxiv": "http://arxiv.org/schemas/atom",
}
SLEEP = 3.0
AUDIT_SKIP_RATE = 0.01  # 1% of SKIP_HARD marked for fulltext audit
# Empirical fulltext floor (~3.5s/PDF + extract) for rate comparison in SKIP_LIVE
FULLTEXT_RATE_BASELINE_PER_HOUR = 100.0
SYNC_EVERY_N = 500


class MetaFetchError(RuntimeError):
    pass


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_categories() -> list[str]:
    return list(json.loads((ROOT / "categories.json").read_text())["categories"])


def next_month(yyyymm: str) -> str:
    y, m = int(yyyymm[:4]), int(yyyymm[4:6])
    m += 1
    if m > 12:
        y += 1
        m = 1
    return f"{y:04d}{m:02d}"


def ensure_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS phase0 (
            arxiv_id TEXT PRIMARY KEY,
            title TEXT,
            abstract TEXT,
            primary_category TEXT,
            categories TEXT,
            published TEXT,
            harvest_category TEXT,
            phase0_label TEXT,
            phase0_reason TEXT,
            audit_fulltext INTEGER DEFAULT 0,
            scored_at TEXT,
            wave TEXT
        );
        CREATE INDEX IF NOT EXISTS idx_phase0_label ON phase0(phase0_label);
        CREATE INDEX IF NOT EXISTS idx_phase0_audit ON phase0(audit_fulltext);
        CREATE TABLE IF NOT EXISTS phase0_cursor (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            category_index INTEGER,
            category TEXT,
            yyyymm TEXT,
            start_index INTEGER,
            n_phase0 INTEGER,
            n_skip_hard INTEGER,
            n_fulltext_queue INTEGER,
            n_uncertain INTEGER,
            n_audit INTEGER,
            updated_at TEXT
        );
        """
    )
    if not conn.execute("SELECT id FROM phase0_cursor WHERE id=1").fetchone():
        cats = load_categories()
        conn.execute(
            """INSERT INTO phase0_cursor (
              id, category_index, category, yyyymm, start_index,
              n_phase0, n_skip_hard, n_fulltext_queue, n_uncertain, n_audit, updated_at
            ) VALUES (1, 0, ?, '199201', 0, 0, 0, 0, 0, 0, ?)""",
            (cats[0], utc_now()),
        )
    conn.commit()


def save_cursor(conn: sqlite3.Connection, cur: dict) -> None:
    cur = dict(cur)
    cur["updated_at"] = utc_now()
    conn.execute(
        """UPDATE phase0_cursor SET
          category_index=?, category=?, yyyymm=?, start_index=?,
          n_phase0=?, n_skip_hard=?, n_fulltext_queue=?, n_uncertain=?, n_audit=?, updated_at=?
        WHERE id=1""",
        (
            cur["category_index"],
            cur["category"],
            cur["yyyymm"],
            cur["start_index"],
            cur["n_phase0"],
            cur["n_skip_hard"],
            cur["n_fulltext_queue"],
            cur["n_uncertain"],
            cur["n_audit"],
            cur["updated_at"],
        ),
    )
    conn.commit()
    (ROOT / "state").mkdir(parents=True, exist_ok=True)
    (ROOT / "state" / "phase0_cursor.json").write_text(json.dumps(cur, indent=2) + "\n")


def get_cursor(conn: sqlite3.Connection) -> dict:
    cols = [
        "category_index", "category", "yyyymm", "start_index",
        "n_phase0", "n_skip_hard", "n_fulltext_queue", "n_uncertain", "n_audit", "updated_at",
    ]
    row = conn.execute(f"SELECT {', '.join(cols)} FROM phase0_cursor WHERE id=1").fetchone()
    return dict(zip(cols, row))


def fetch_meta_page(category: str, yyyymm: str, start: int, page_size: int) -> tuple[int, list[dict]]:
    y, m = int(yyyymm[:4]), int(yyyymm[4:6])
    d2 = monthrange(y, m)[1]
    q = f"cat:{category} AND submittedDate:[{y:04d}{m:02d}010000 TO {y:04d}{m:02d}{d2:02d}2359]"
    params = urllib.parse.urlencode(
        {
            "search_query": q,
            "start": str(start),
            "max_results": str(page_size),
            "sortBy": "submittedDate",
            "sortOrder": "ascending",
        }
    )
    req = urllib.request.Request(API + "?" + params, headers={"User-Agent": UA})
    time.sleep(SLEEP)
    xml_bytes = None
    for attempt in range(24):
        try:
            with urllib.request.urlopen(req, timeout=180) as resp:
                xml_bytes = resp.read()
            break
        except Exception as e:
            wait = min(300, max(SLEEP * (2 ** min(attempt, 6)), 15))
            print(f"phase0 meta err {e}; sleep {wait} (attempt {attempt+1}/24)", flush=True)
            time.sleep(wait)
            req = urllib.request.Request(API + "?" + params, headers={"User-Agent": UA})
    if xml_bytes is None:
        raise MetaFetchError(f"phase0 meta failed: {category} {yyyymm} start={start}")
    root = ET.fromstring(xml_bytes)
    total_el = root.find("opensearch:totalResults", ATOM_NS)
    total = int(total_el.text) if total_el is not None and total_el.text else 0
    import re

    entries = []
    for entry in root.findall("atom:entry", ATOM_NS):
        id_el = entry.find("atom:id", ATOM_NS)
        title_el = entry.find("atom:title", ATOM_NS)
        summary_el = entry.find("atom:summary", ATOM_NS)
        published_el = entry.find("atom:published", ATOM_NS)
        primary_el = entry.find("arxiv:primary_category", ATOM_NS)
        cats = [c.get("term", "") for c in entry.findall("atom:category", ATOM_NS) if c.get("term")]
        raw = (id_el.text or "").replace("http://arxiv.org/abs/", "").replace("https://arxiv.org/abs/", "")
        m = re.search(r"(v\d+)$", raw)
        if m:
            raw = raw[: m.start()]
        entries.append(
            {
                "arxiv_id": raw,
                "title": " ".join((title_el.text or "").split()) if title_el is not None else "",
                "abstract": " ".join((summary_el.text or "").split()) if summary_el is not None else "",
                "published": published_el.text if published_el is not None else "",
                "primary_category": primary_el.get("term") if primary_el is not None else (cats[0] if cats else category),
                "categories": cats,
            }
        )
    return total, entries


def persist_phase0(conn: sqlite3.Connection, ent: dict, gate: dict, category: str, wave: str, audit: int) -> None:
    conn.execute(
        """
        INSERT INTO phase0 (
          arxiv_id, title, abstract, primary_category, categories, published,
          harvest_category, phase0_label, phase0_reason, audit_fulltext, scored_at, wave
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
        ON CONFLICT(arxiv_id) DO UPDATE SET
          phase0_label=excluded.phase0_label,
          phase0_reason=excluded.phase0_reason,
          audit_fulltext=excluded.audit_fulltext,
          scored_at=excluded.scored_at,
          wave=excluded.wave,
          title=excluded.title,
          abstract=excluded.abstract
        """,
        (
            ent["arxiv_id"],
            ent.get("title"),
            ent.get("abstract"),
            ent.get("primary_category"),
            json.dumps(ent.get("categories") or []),
            ent.get("published"),
            category,
            gate["phase0_label"],
            gate["phase0_reason"],
            audit,
            utc_now(),
            wave,
        ),
    )
    conn.commit()


def write_status(conn: sqlite3.Connection, *, t0: float, batch_n: int, pid: int | None, running: bool = True) -> dict:
    cur = get_cursor(conn)
    elapsed = max(time.time() - t0, 1e-6)
    rate = batch_n / elapsed * 3600
    by = dict(conn.execute("SELECT phase0_label, COUNT(*) FROM phase0 GROUP BY 1").fetchall())
    n = conn.execute("SELECT COUNT(*) FROM phase0").fetchone()[0]
    n_skip = by.get("SKIP_HARD", 0)
    n_queue = by.get("FULLTEXT_QUEUE", 0)
    n_unc = by.get("UNCERTAIN_FULLTEXT", 0)
    speedup = (rate / FULLTEXT_RATE_BASELINE_PER_HOUR) if FULLTEXT_RATE_BASELINE_PER_HOUR else None
    status = {
        "status": "SKIP_LIVE" if running else "SKIP_IDLE",
        "n_phase0_scored_cum": n,
        "n_skip": n_skip,
        "n_skip_hard": n_skip,
        "n_queue": n_queue,
        "n_fulltext_queue": n_queue,
        "n_uncertain_fulltext": n_unc,
        "n_audit_marked": conn.execute("SELECT COUNT(*) FROM phase0 WHERE audit_fulltext=1").fetchone()[0],
        "phase0_throughput_per_hour_est": round(rate, 1),
        "fulltext_throughput_per_hour_baseline": FULLTEXT_RATE_BASELINE_PER_HOUR,
        "phase0_vs_fulltext_speedup_est": round(speedup, 1) if speedup is not None else None,
        "batch_n": batch_n,
        "batch_elapsed_s": round(elapsed, 1),
        "next_pointer": {
            "category_index": cur["category_index"],
            "category": cur["category"],
            "yyyymm": cur["yyyymm"],
            "start_index": cur["start_index"],
        },
        "fulltext_queue_pending": n_queue + n_unc,
        "pipeline_order": "phase0_lock_order_then_queue_high_transfer",
        "updated_at": utc_now(),
        "cloud_pid": pid,
        "doc": "docs/arxiv-census-skip-filter.md",
    }
    (ROOT / "state").mkdir(parents=True, exist_ok=True)
    (ROOT / "state" / "phase0-status.json").write_text(json.dumps(status, indent=2) + "\n")
    return status


def run(
    wave: str,
    max_papers: int | None,
    max_seconds: float | None,
    page_size: int,
    reset: bool,
) -> dict:
    ensure_work_db()
    WORK_DB.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(WORK_DB))
    ensure_schema(conn)
    cats = load_categories()
    if reset:
        conn.execute(
            """UPDATE phase0_cursor SET category_index=0, category=?, yyyymm='199201', start_index=0,
              n_phase0=0, n_skip_hard=0, n_fulltext_queue=0, n_uncertain=0, n_audit=0, updated_at=?""",
            (cats[0], utc_now()),
        )
        conn.commit()

    # Reconcile cursor counters from table if table empty but JSON claimed progress
    n_existing = conn.execute("SELECT COUNT(*) FROM phase0").fetchone()[0]
    cur = get_cursor(conn)
    if n_existing == 0 and (cur.get("n_phase0") or 0) > 0:
        print("PHASE0 reconcile: empty table — reset cursor to lock start", flush=True)
        cur.update(
            {
                "category_index": 0,
                "category": cats[0],
                "yyyymm": "199201",
                "start_index": 0,
                "n_phase0": 0,
                "n_skip_hard": 0,
                "n_fulltext_queue": 0,
                "n_uncertain": 0,
                "n_audit": 0,
            }
        )
        save_cursor(conn, cur)

    if not cur["category"]:
        cur["category"] = cats[cur["category_index"]]
        cur["yyyymm"] = cur["yyyymm"] or "199201"

    t0 = time.time()
    batch_n = 0
    last_sync_at = 0
    pid = os.getpid()
    write_status(conn, t0=t0, batch_n=0, pid=pid, running=True)
    print(
        f"PHASE0 start pid={pid} cat_idx={cur['category_index']} cat={cur['category']} "
        f"yyyymm={cur['yyyymm']} start={cur['start_index']} page_size={page_size}",
        flush=True,
    )

    try:
        while cur["category_index"] < len(cats):
            if max_papers is not None and batch_n >= max_papers:
                break
            if max_seconds is not None and (time.time() - t0) >= max_seconds:
                break

            category = cats[cur["category_index"]]
            cur["category"] = category
            yyyymm = cur["yyyymm"] or "199201"
            start = int(cur["start_index"] or 0)
            empty_streak = 0
            seen = False
            stop_batch = False
            category_done = False

            while yyyymm <= "202610":
                if max_papers is not None and batch_n >= max_papers:
                    stop_batch = True
                    break
                if max_seconds is not None and (time.time() - t0) >= max_seconds:
                    stop_batch = True
                    break

                try:
                    total, entries = fetch_meta_page(category, yyyymm, start, page_size)
                except MetaFetchError as e:
                    print(f"PHASE0 META HARD FAIL (no advance): {e}; cool-down 120s", flush=True)
                    write_status(conn, t0=t0, batch_n=batch_n, pid=pid, running=True)
                    time.sleep(120)
                    continue

                print(
                    f"[P0 {cur['category_index']}/{len(cats)}] {category} {yyyymm} "
                    f"start={start} got={len(entries)} total={total} "
                    f"n={cur['n_phase0']} skip={cur['n_skip_hard']} q={cur['n_fulltext_queue']} unc={cur['n_uncertain']}",
                    flush=True,
                )

                if total == 0 or not entries:
                    if seen:
                        empty_streak += 1
                    if seen and empty_streak >= 8:
                        category_done = True
                        break
                    yyyymm = next_month(yyyymm)
                    start = 0
                    cur["yyyymm"] = yyyymm
                    cur["start_index"] = 0
                    save_cursor(conn, cur)
                    write_status(conn, t0=t0, batch_n=batch_n, pid=pid, running=True)
                    continue

                seen = True
                empty_streak = 0
                for ent in entries:
                    if max_papers is not None and batch_n >= max_papers:
                        stop_batch = True
                        break
                    if max_seconds is not None and (time.time() - t0) >= max_seconds:
                        stop_batch = True
                        break
                    # Skip if already phase0'd
                    if conn.execute("SELECT 1 FROM phase0 WHERE arxiv_id=?", (ent["arxiv_id"],)).fetchone():
                        continue

                    gate = score_phase0(
                        title=ent["title"],
                        abstract=ent["abstract"],
                        categories=ent["categories"],
                        primary_category=ent["primary_category"],
                    )
                    audit = 0
                    lab = gate["phase0_label"]
                    if lab == "SKIP_HARD":
                        cur["n_skip_hard"] += 1
                        if random.random() < AUDIT_SKIP_RATE:
                            audit = 1
                            cur["n_audit"] += 1
                    elif lab == "FULLTEXT_QUEUE":
                        cur["n_fulltext_queue"] += 1
                    else:
                        cur["n_uncertain"] += 1

                    persist_phase0(conn, ent, gate, category, wave, audit)
                    cur["n_phase0"] += 1
                    batch_n += 1
                    if batch_n % 50 == 0:
                        print(
                            f"  … {ent['arxiv_id']} → {lab} | cum={cur['n_phase0']} "
                            f"skip={cur['n_skip_hard']} q={cur['n_fulltext_queue']}",
                            flush=True,
                        )
                    if batch_n - last_sync_at >= SYNC_EVERY_N:
                        try:
                            export_phase0_compact(conn)
                            mirror_gzip(WORK_DB)
                            last_sync_at = batch_n
                            print(f"  mirrored census.sqlite.gz + phase0-scores at n={batch_n}", flush=True)
                        except Exception as e:
                            print(f"  mirror warn: {e}", flush=True)
                            try:
                                export_phase0_compact(conn)
                            except Exception as e2:
                                print(f"  compact export warn: {e2}", flush=True)

                if stop_batch:
                    # Stay on this month/offset for resume — do NOT advance category
                    cur["yyyymm"] = yyyymm
                    cur["start_index"] = start
                    save_cursor(conn, cur)
                    write_status(conn, t0=t0, batch_n=batch_n, pid=pid, running=True)
                    break

                start += max(len(entries), page_size)
                cur["start_index"] = start
                cur["yyyymm"] = yyyymm
                save_cursor(conn, cur)
                write_status(conn, t0=t0, batch_n=batch_n, pid=pid, running=True)
                if start >= total:
                    yyyymm = next_month(yyyymm)
                    start = 0
                    cur["yyyymm"] = yyyymm
                    cur["start_index"] = 0
                    save_cursor(conn, cur)

            if stop_batch:
                break

            # Only advance category after finishing its months (or empty streak)
            if not category_done and yyyymm > "202610":
                category_done = True
            cur["category_index"] += 1
            cur["start_index"] = 0
            cur["yyyymm"] = "199201"
            if cur["category_index"] < len(cats):
                cur["category"] = cats[cur["category_index"]]
            save_cursor(conn, cur)
            write_status(conn, t0=t0, batch_n=batch_n, pid=pid, running=True)
    finally:
        save_cursor(conn, cur)
        try:
            export_phase0_compact(conn)
            mirror_gzip(WORK_DB)
        except Exception as e:
            print(f"final mirror warn: {e}", flush=True)
            try:
                export_phase0_compact(conn)
            except Exception as e2:
                print(f"final compact warn: {e2}", flush=True)
        still_going = cur["category_index"] < len(cats)
        status = write_status(conn, t0=t0, batch_n=batch_n, pid=pid, running=still_going)
        if still_going:
            status["status"] = "SKIP_LIVE"
        else:
            status["status"] = "SKIP_DONE"
        (ROOT / "state" / "phase0-status.json").write_text(json.dumps(status, indent=2) + "\n")
        conn.close()

    return status


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--wave", default="phase0")
    ap.add_argument("--max-papers", type=int, default=None)
    ap.add_argument("--max-seconds", type=float, default=None)
    ap.add_argument("--page-size", type=int, default=100)
    ap.add_argument("--reset", action="store_true")
    args = ap.parse_args()
    s = run(args.wave, args.max_papers, args.max_seconds, args.page_size, args.reset)
    print(json.dumps(s, indent=2))


if __name__ == "__main__":
    main()
