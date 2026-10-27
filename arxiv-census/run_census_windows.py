#!/usr/bin/env python3
"""
Date-windowed harvest continuation for a category (avoids deep Atom start offsets).
Strict order preserved: same category, submittedDate ascending via monthly windows.
Dedup by arXiv id against existing census.sqlite.
"""
from __future__ import annotations

import argparse
import json
import sqlite3
import time
from calendar import monthrange
from datetime import datetime, timezone
from pathlib import Path

from run_census import (
    ROOT,
    SLEEP_S,
    ShardWriter,
    bump_counts,
    fetch_page,
    get_cursor,
    init_db,
    save_cursor,
    sync_db_to_store,
    utc_now,
)
from score_abstract import score_abstract


def atomic_write_json(path: Path, obj: dict) -> None:
    """Write JSON with retries; fall back to /tmp mirror on store FS EAGAIN."""
    text = json.dumps(obj, indent=2) + "\n"
    tmp_fallback = Path("/tmp/arxiv-census") / path.name
    tmp_fallback.parent.mkdir(parents=True, exist_ok=True)
    for attempt in range(6):
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
            return
        except (BlockingIOError, OSError) as e:
            print(f"state write warn {path.name}: {e}; attempt {attempt+1}", flush=True)
            time.sleep(0.4 * (attempt + 1))
    tmp_fallback.write_text(text, encoding="utf-8")
    try:
        path.write_text(text, encoding="utf-8")
    except (BlockingIOError, OSError):
        print(f"state write kept in {tmp_fallback}", flush=True)


def fetch_page_window(category: str, yyyymm_start: str, yyyymm_end: str, start: int, max_results: int):
    """submittedDate window inclusive; yyyymm as YYYYMM."""
    y1, m1 = int(yyyymm_start[:4]), int(yyyymm_start[4:6])
    y2, m2 = int(yyyymm_end[:4]), int(yyyymm_end[4:6])
    d2 = monthrange(y2, m2)[1]
    q = (
        f"cat:{category} AND submittedDate:"
        f"[{y1:04d}{m1:02d}010000 TO {y2:04d}{m2:02d}{d2:02d}2359]"
    )
    # reuse fetch machinery by temporarily swapping — call API directly via patched params
    import urllib.parse
    import urllib.request
    import urllib.error
    import xml.etree.ElementTree as ET
    from run_census import API, UA, ATOM_NS, normalize_id, SLEEP_S

    params = {
        "search_query": q,
        "start": str(start),
        "max_results": str(max_results),
        "sortBy": "submittedDate",
        "sortOrder": "ascending",
    }
    url = API + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    xml_bytes = b""
    for attempt in range(12):
        try:
            with urllib.request.urlopen(req, timeout=180) as resp:
                xml_bytes = resp.read()
            break
        except urllib.error.HTTPError as e:
            if e.code in {429, 503, 502, 500}:
                wait = min(120.0, SLEEP_S * (2 ** attempt))
                print(f"HTTP {e.code}; sleep {wait:.1f}s (attempt {attempt+1})", flush=True)
                time.sleep(wait)
                continue
            raise
        except urllib.error.URLError as e:
            wait = min(120.0, SLEEP_S * (2 ** attempt))
            print(f"URL error {e}; sleep {wait:.1f}s", flush=True)
            time.sleep(wait)
            continue
    else:
        raise RuntimeError(f"failed {url}")

    root = ET.fromstring(xml_bytes)
    total_el = root.find("opensearch:totalResults", ATOM_NS)
    total = int(total_el.text) if total_el is not None and total_el.text else 0
    entries = []
    for entry in root.findall("atom:entry", ATOM_NS):
        id_el = entry.find("atom:id", ATOM_NS)
        title_el = entry.find("atom:title", ATOM_NS)
        summary_el = entry.find("atom:summary", ATOM_NS)
        published_el = entry.find("atom:published", ATOM_NS)
        updated_el = entry.find("atom:updated", ATOM_NS)
        primary_el = entry.find("arxiv:primary_category", ATOM_NS)
        cats = [c.get("term", "") for c in entry.findall("atom:category", ATOM_NS) if c.get("term")]
        raw_id = id_el.text if id_el is not None else ""
        arxiv_id, version = normalize_id(raw_id or "")
        title = " ".join((title_el.text or "").split()) if title_el is not None else ""
        abstract = " ".join((summary_el.text or "").split()) if summary_el is not None else ""
        entries.append(
            {
                "arxiv_id": arxiv_id,
                "version": version,
                "title": title,
                "abstract": abstract,
                "primary_category": (
                    primary_el.get("term") if primary_el is not None else (cats[0] if cats else category)
                ),
                "categories": cats,
                "published": published_el.text if published_el is not None else "",
                "updated": updated_el.text if updated_el is not None else "",
            }
        )
    return total, entries


def next_month(yyyymm: str) -> str:
    y, m = int(yyyymm[:4]), int(yyyymm[4:6])
    m += 1
    if m > 12:
        y += 1
        m = 1
    return f"{y:04d}{m:02d}"


def run(wave: int, category: str, start_yyyymm: str, end_yyyymm: str, max_papers: int | None, max_seconds: float | None, page_size: int) -> dict:
    import shutil

    work_dir = Path("/tmp/arxiv-census")
    work_dir.mkdir(parents=True, exist_ok=True)
    work_db = work_dir / "census.sqlite"
    store_db = ROOT / "census.sqlite"
    # Never clobber a larger intact work DB with a missing/empty store file.
    if store_db.exists() and store_db.stat().st_size > 10_000:
        if (not work_db.exists()) or store_db.stat().st_size > work_db.stat().st_size * 1.05:
            try:
                shutil.copy2(store_db, work_db)
            except OSError as e:
                print(f"skip store->work copy: {e}", flush=True)

    # Score shards on /tmp to avoid agent-store EIO; compact gz synced at wave end.
    scores_dir = work_dir / "scores"
    batch_dir = work_dir / "batches"
    scores_dir.mkdir(parents=True, exist_ok=True)
    batch_dir.mkdir(parents=True, exist_ok=True)
    (ROOT / "state").mkdir(parents=True, exist_ok=True)

    conn = init_db(work_db)
    cur = get_cursor(conn)
    cur["wave"] = wave
    cur["category"] = category

    t0 = time.time()
    wave_scored = 0
    wave_aid_hits: list[dict] = []
    stamp = utc_now().replace(":", "")
    scores_w = ShardWriter(scores_dir, f"scores-wave{wave}", shard_lines=200)
    batch_w = ShardWriter(batch_dir, f"wave{wave}-win-{stamp}", shard_lines=500)

    # resume window from state if present
    win_path = ROOT / "state" / "window.json"
    if win_path.exists():
        win = json.loads(win_path.read_text(encoding="utf-8"))
        if win.get("category") == category:
            start_yyyymm = win.get("yyyymm", start_yyyymm)
            win_start = int(win.get("start", 0))
        else:
            win_start = 0
    else:
        win_start = 0

    yyyymm = start_yyyymm
    empty_streak = 0
    empty_stop = 8  # consecutive empty months AFTER content seen → category exhausted
    seen_content = False
    print(f"windowed harvest cat={category} from={yyyymm} to={end_yyyymm} win_start={win_start}", flush=True)

    try:
        while yyyymm <= end_yyyymm:
            if max_papers is not None and wave_scored >= max_papers:
                break
            if max_seconds is not None and (time.time() - t0) >= max_seconds:
                break

            start = win_start
            win_start = 0  # only first window resumes mid-page
            month_new = 0
            while True:
                if max_papers is not None and wave_scored >= max_papers:
                    break
                if max_seconds is not None and (time.time() - t0) >= max_seconds:
                    break

                time.sleep(SLEEP_S)
                total, entries = fetch_page_window(category, yyyymm, yyyymm, start, page_size)
                print(
                    f"[{category}] {yyyymm} start={start} got={len(entries)} total={total} "
                    f"wave_scored={wave_scored} ledger={cur['n_scored']}",
                    flush=True,
                )
                if total == 0 or not entries:
                    break

                page_new = 0
                for ent in entries:
                    if max_papers is not None and wave_scored >= max_papers:
                        break
                    exists = conn.execute(
                        "SELECT 1 FROM papers WHERE arxiv_id=?", (ent["arxiv_id"],)
                    ).fetchone()
                    if exists:
                        cur["n_skipped_dup"] += 1
                        continue
                    score = score_abstract(
                        title=ent["title"], abstract=ent["abstract"], categories=ent["categories"]
                    )
                    scored_at = utc_now()
                    rec = {**ent, **score, "harvest_category": category, "scored_at": scored_at, "wave": wave}
                    conn.execute(
                        """
                        INSERT INTO papers (
                          arxiv_id, version, title, abstract, primary_category, categories,
                          published, updated, labels, primary_label,
                          aid_sports, aid_poker, aid_crypto, transfer, uncertain, no_aid,
                          rationale, harvest_category, scored_at, wave
                        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                        """,
                        (
                            ent["arxiv_id"], ent["version"], ent["title"], ent["abstract"],
                            ent["primary_category"], json.dumps(ent["categories"]),
                            ent["published"], ent["updated"],
                            json.dumps(score["labels"]), score["primary"],
                            int(score["aid_sports"]), int(score["aid_poker"]),
                            int(score["aid_crypto"]), int(score["transfer"]),
                            int(score["uncertain"]), int(score["no_aid"]),
                            score["rationale"], category, scored_at, wave,
                        ),
                    )
                    line = json.dumps(rec, ensure_ascii=False)
                    scores_w.write(line)
                    batch_w.write(line)
                    bump_counts(cur, score)
                    cur["n_scored"] += 1
                    wave_scored += 1
                    page_new += 1
                    if score["aid_sports"] or score["aid_poker"] or score["aid_crypto"]:
                        wave_aid_hits.append(
                            {
                                "arxiv_id": ent["arxiv_id"],
                                "title": ent["title"],
                                "labels": score["labels"],
                                "published": ent["published"],
                                "primary_category": ent["primary_category"],
                                "rationale": score["rationale"],
                            }
                        )

                conn.commit()
                scores_w.flush()
                batch_w.flush()
                start += max(len(entries), page_size)
                # approximate global start_index for continuity reporting
                cur["start_index"] = cur["n_scored"]  # window mode: ledger size as progress proxy
                cur["total_in_cat"] = max(cur.get("total_in_cat") or 0, 105380)
                save_cursor(conn, cur)
                sync_db_to_store(work_db, store_db)
                atomic_write_json(
                    win_path,
                    {
                        "category": category,
                        "yyyymm": yyyymm,
                        "start": start,
                        "updated_at": utc_now(),
                    },
                )
                print(f"  page_new={page_new} aids=S{cur['n_aid_sports']}/P{cur['n_aid_poker']}/C{cur['n_aid_crypto']} T{cur['n_transfer']} U{cur['n_uncertain']}", flush=True)
                month_new += page_new
                if start >= total:
                    break

            # Only truly empty months count toward exhaustion. All-dup months are progress.
            if total == 0:
                if seen_content:
                    empty_streak += 1
            else:
                seen_content = True
                empty_streak = 0
            if seen_content and empty_streak >= empty_stop:
                print(f"empty-month stop after {empty_streak} at {yyyymm}", flush=True)
                yyyymm = next_month(yyyymm)
                atomic_write_json(
                    win_path,
                    {
                        "category": category,
                        "yyyymm": yyyymm,
                        "start": 0,
                        "updated_at": utc_now(),
                        "exhausted": True,
                    },
                )
                break

            yyyymm = next_month(yyyymm)
            atomic_write_json(
                win_path,
                {"category": category, "yyyymm": yyyymm, "start": 0, "updated_at": utc_now()},
            )
    finally:
        scores_w.close()
        batch_w.close()
        save_cursor(conn, cur)
        sync_db_to_store(work_db, store_db)
        conn.close()

    summary = {
        "wave": wave,
        "mode": "date_windows",
        "wave_scored": wave_scored,
        "elapsed_s": round(time.time() - t0, 1),
        "n_aid_hits_wave": len(wave_aid_hits),
        "aid_hits_wave": wave_aid_hits[:200],
        "next_yyyymm": yyyymm,
        "cursor": get_cursor(init_db(work_db)),
    }
    init_db(work_db).close()
    (ROOT / "state" / f"wave{wave}-windows-summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    return summary


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--wave", type=int, default=1)
    ap.add_argument("--category", default="astro-ph")
    ap.add_argument("--start-yyyymm", required=True)
    ap.add_argument("--end-yyyymm", default="202610")
    ap.add_argument("--max-papers", type=int, default=None)
    ap.add_argument("--max-seconds", type=float, default=None)
    ap.add_argument("--page-size", type=int, default=100)
    args = ap.parse_args()
    summary = run(
        args.wave,
        args.category,
        args.start_yyyymm,
        args.end_yyyymm,
        args.max_papers,
        args.max_seconds,
        args.page_size,
    )
    print(json.dumps({k: summary[k] for k in ("wave", "wave_scored", "elapsed_s", "n_aid_hits_wave", "next_yyyymm")}, indent=2))


if __name__ == "__main__":
    main()
