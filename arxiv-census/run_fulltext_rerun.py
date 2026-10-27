#!/usr/bin/env python3
"""
Authoritative fulltext census re-run from lock-order start.
Fetch PDF → extract ALL text → score → persist. Abstract-only is not used.
"""
from __future__ import annotations

import argparse
import json
import sqlite3
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

from fulltext_extract import extract_arxiv, id_key
from score_fulltext import score_fulltext

ROOT = Path(__file__).resolve().parent
WORK_DB = Path("/tmp/arxiv-census/census.sqlite")
API = "https://export.arxiv.org/api/query"
UA = "arxiv-census-fulltext-rerun/1.0"
ATOM_NS = {
    "atom": "http://www.w3.org/2005/Atom",
    "opensearch": "http://a9.com/-/spec/opensearch/1.1/",
    "arxiv": "http://arxiv.org/schemas/atom",
}
SLEEP = 3.5


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_categories() -> list[str]:
    return list(json.loads((ROOT / "categories.json").read_text())["categories"])



def _ensure_cols(conn: sqlite3.Connection, table: str, cols: list[tuple[str, str]]) -> None:
    existing = {r[1] for r in conn.execute(f"PRAGMA table_info({table})").fetchall()}
    for name, typ in cols:
        if name not in existing:
            conn.execute(f"ALTER TABLE {table} ADD COLUMN {name} {typ}")

def ensure_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS fulltext (
            arxiv_id TEXT PRIMARY KEY,
            path TEXT,
            pdf_path TEXT,
            sha256 TEXT,
            chars INTEGER,
            extractor TEXT,
            source TEXT,
            flags TEXT,
            ok INTEGER,
            fetched_at TEXT,
            score_labels TEXT,
            score_primary TEXT,
            score_rationale TEXT,
            score_valid INTEGER,
            scored_at TEXT,
            title TEXT,
            categories TEXT,
            published TEXT,
            harvest_category TEXT,
            wave TEXT
        );
        CREATE TABLE IF NOT EXISTS fulltext_cursor (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            category_index INTEGER,
            category TEXT,
            yyyymm TEXT,
            start_index INTEGER,
            n_fulltext_ok INTEGER,
            n_extract_fail INTEGER,
            n_aid_sports INTEGER,
            n_aid_poker INTEGER,
            n_aid_crypto INTEGER,
            n_transfer INTEGER,
            n_uncertain INTEGER,
            n_no_aid INTEGER,
            updated_at TEXT
        );
        """
    )
    _ensure_cols(conn, "fulltext", [
        ("title", "TEXT"), ("categories", "TEXT"), ("published", "TEXT"),
        ("harvest_category", "TEXT"), ("wave", "TEXT"),
    ])
    _ensure_cols(conn, "papers", [
        ("score_phase", "TEXT"), ("score_valid", "INTEGER"), ("interim_note", "TEXT"),
    ])
    if not conn.execute("SELECT id FROM fulltext_cursor WHERE id=1").fetchone():
        conn.execute(
            """
            INSERT INTO fulltext_cursor (
              id, category_index, category, yyyymm, start_index,
              n_fulltext_ok, n_extract_fail, n_aid_sports, n_aid_poker, n_aid_crypto,
              n_transfer, n_uncertain, n_no_aid, updated_at
            ) VALUES (1, 0, '', '199201', 0, 0, 0, 0, 0, 0, 0, 0, 0, ?)
            """,
            (utc_now(),),
        )
    conn.commit()


class MetaFetchError(RuntimeError):
    """API/meta failure — must NOT be treated as an empty month (zero-miss)."""


def fetch_meta_page(category: str, yyyymm: str, start: int, page_size: int) -> tuple[int, list[dict]]:
    from calendar import monthrange

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
    url = API + "?" + params
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    time.sleep(SLEEP)
    # Never return (0, []) on transport/API failure — that skips months (zero-miss breach).
    xml_bytes = None
    for attempt in range(24):
        try:
            with urllib.request.urlopen(req, timeout=180) as resp:
                xml_bytes = resp.read()
            break
        except Exception as e:
            # Cap backoff high for 429; keep retrying this same window
            wait = min(300, max(SLEEP * (2 ** min(attempt, 6)), 15))
            print(f"meta fetch err {e}; sleep {wait} (attempt {attempt+1}/24)", flush=True)
            time.sleep(wait)
    if xml_bytes is None:
        raise MetaFetchError(f"meta fetch failed after retries: {category} {yyyymm} start={start}")
    root = ET.fromstring(xml_bytes)
    total_el = root.find("opensearch:totalResults", ATOM_NS)
    total = int(total_el.text) if total_el is not None and total_el.text else 0
    entries = []
    for entry in root.findall("atom:entry", ATOM_NS):
        id_el = entry.find("atom:id", ATOM_NS)
        title_el = entry.find("atom:title", ATOM_NS)
        summary_el = entry.find("atom:summary", ATOM_NS)
        published_el = entry.find("atom:published", ATOM_NS)
        primary_el = entry.find("arxiv:primary_category", ATOM_NS)
        cats = [c.get("term", "") for c in entry.findall("atom:category", ATOM_NS) if c.get("term")]
        raw = (id_el.text or "").replace("http://arxiv.org/abs/", "").replace("https://arxiv.org/abs/", "")
        import re

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


def next_month(yyyymm: str) -> str:
    y, m = int(yyyymm[:4]), int(yyyymm[4:6])
    m += 1
    if m > 12:
        y += 1
        m = 1
    return f"{y:04d}{m:02d}"


def save_ft_cursor(conn: sqlite3.Connection, cur: dict) -> None:
    cur = dict(cur)
    cur["updated_at"] = utc_now()
    conn.execute(
        """
        UPDATE fulltext_cursor SET
          category_index=?, category=?, yyyymm=?, start_index=?,
          n_fulltext_ok=?, n_extract_fail=?, n_aid_sports=?, n_aid_poker=?, n_aid_crypto=?,
          n_transfer=?, n_uncertain=?, n_no_aid=?, updated_at=?
        WHERE id=1
        """,
        (
            cur["category_index"],
            cur["category"],
            cur["yyyymm"],
            cur["start_index"],
            cur["n_fulltext_ok"],
            cur["n_extract_fail"],
            cur["n_aid_sports"],
            cur["n_aid_poker"],
            cur["n_aid_crypto"],
            cur["n_transfer"],
            cur["n_uncertain"],
            cur["n_no_aid"],
            cur["updated_at"],
        ),
    )
    conn.commit()
    (ROOT / "state" / "fulltext_cursor.json").write_text(json.dumps(cur, indent=2) + "\n", encoding="utf-8")


def get_ft_cursor(conn: sqlite3.Connection) -> dict:
    cols = [
        "category_index",
        "category",
        "yyyymm",
        "start_index",
        "n_fulltext_ok",
        "n_extract_fail",
        "n_aid_sports",
        "n_aid_poker",
        "n_aid_crypto",
        "n_transfer",
        "n_uncertain",
        "n_no_aid",
        "updated_at",
    ]
    row = conn.execute(f"SELECT {', '.join(cols)} FROM fulltext_cursor WHERE id=1").fetchone()
    return dict(zip(cols, row))


def persist_fulltext_score(conn: sqlite3.Connection, meta: dict, score: dict, ent: dict, category: str, wave: str) -> None:
    conn.execute(
        """
        INSERT OR REPLACE INTO fulltext (
          arxiv_id, path, pdf_path, sha256, chars, extractor, source, flags, ok, fetched_at,
          score_labels, score_primary, score_rationale, score_valid, scored_at,
          title, categories, published, harvest_category, wave
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """,
        (
            ent["arxiv_id"],
            meta.get("path"),
            meta.get("pdf_path"),
            meta.get("sha256"),
            meta.get("chars") or 0,
            meta.get("extractor"),
            meta.get("source"),
            json.dumps(meta.get("flags") or []),
            int(bool(meta.get("ok"))),
            utc_now(),
            json.dumps(score.get("labels") or []),
            score.get("primary"),
            score.get("rationale"),
            int(bool(score.get("score_valid"))),
            utc_now(),
            ent.get("title"),
            json.dumps(ent.get("categories") or []),
            ent.get("published"),
            category,
            wave,
        ),
    )
    # Upsert papers row as fulltext-authoritative when extract ok
    if score.get("score_valid"):
        conn.execute(
            """
            INSERT INTO papers (
              arxiv_id, version, title, abstract, primary_category, categories,
              published, updated, labels, primary_label,
              aid_sports, aid_poker, aid_crypto, transfer, uncertain, no_aid,
              rationale, harvest_category, scored_at, wave, score_phase, score_valid
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            ON CONFLICT(arxiv_id) DO UPDATE SET
              labels=excluded.labels,
              primary_label=excluded.primary_label,
              aid_sports=excluded.aid_sports,
              aid_poker=excluded.aid_poker,
              aid_crypto=excluded.aid_crypto,
              transfer=excluded.transfer,
              uncertain=excluded.uncertain,
              no_aid=excluded.no_aid,
              rationale=excluded.rationale,
              scored_at=excluded.scored_at,
              wave=excluded.wave,
              score_phase='fulltext',
              score_valid=1
            """,
            (
                ent["arxiv_id"],
                "",
                ent.get("title"),
                "",  # abstract not used for scoring
                ent.get("primary_category"),
                json.dumps(ent.get("categories") or []),
                ent.get("published"),
                "",
                json.dumps(score.get("labels") or []),
                score.get("primary"),
                int(score.get("aid_sports") or 0),
                int(score.get("aid_poker") or 0),
                int(score.get("aid_crypto") or 0),
                int(score.get("transfer") or 0),
                int(score.get("uncertain") or 0),
                int(score.get("no_aid") or 0),
                score.get("rationale"),
                category,
                utc_now(),
                wave,
                "fulltext",
                1,
            ),
        )
    conn.commit()


def run(wave: str, max_papers: int | None, max_seconds: float | None, page_size: int, reset: bool) -> dict:
    cats = load_categories()
    WORK_DB.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(WORK_DB))
    ensure_schema(conn)
    # ensure papers has score_phase cols
    cols = {r[1] for r in conn.execute("PRAGMA table_info(papers)").fetchall()}
    if "score_phase" not in cols:
        conn.execute("ALTER TABLE papers ADD COLUMN score_phase TEXT")
    if "score_valid" not in cols:
        conn.execute("ALTER TABLE papers ADD COLUMN score_valid INTEGER DEFAULT 0")
    conn.commit()

    if reset:
        conn.execute(
            """
            UPDATE fulltext_cursor SET category_index=0, category=?, yyyymm='199201', start_index=0,
              n_fulltext_ok=0, n_extract_fail=0, n_aid_sports=0, n_aid_poker=0, n_aid_crypto=0,
              n_transfer=0, n_uncertain=0, n_no_aid=0, updated_at=?
            WHERE id=1
            """,
            (cats[0], utc_now()),
        )
        conn.commit()

    cur = get_ft_cursor(conn)
    if not cur["category"]:
        cur["category"] = cats[cur["category_index"]]
        cur["yyyymm"] = cur["yyyymm"] or "199201"

    t0 = time.time()
    batch_scored = 0
    batch_fail = 0
    qa_samples: list[dict] = []
    jsonl_path = ROOT / "batches" / f"fulltext-rerun-{utc_now().replace(':', '')}.jsonl"
    jsonl_path.parent.mkdir(parents=True, exist_ok=True)
    jf = jsonl_path.open("a", encoding="utf-8")

    print(
        f"FULLTEXT RERUN start cat_idx={cur['category_index']} cat={cur['category']} "
        f"yyyymm={cur['yyyymm']} start={cur['start_index']}",
        flush=True,
    )

    try:
        while cur["category_index"] < len(cats):
            if max_papers is not None and batch_scored + batch_fail >= max_papers:
                break
            if max_seconds is not None and (time.time() - t0) >= max_seconds:
                break

            category = cats[cur["category_index"]]
            cur["category"] = category
            yyyymm = cur["yyyymm"] or "199201"
            start = int(cur["start_index"] or 0)
            empty_streak = 0
            seen = False

            while yyyymm <= "202610":
                if max_papers is not None and batch_scored + batch_fail >= max_papers:
                    break
                if max_seconds is not None and (time.time() - t0) >= max_seconds:
                    break

                try:
                    total, entries = fetch_meta_page(category, yyyymm, start, page_size)
                except MetaFetchError as e:
                    # Stay on same window — never treat API failure as empty month
                    print(f"META HARD FAIL (no month advance): {e}; cool-down 120s", flush=True)
                    time.sleep(120)
                    continue
                print(
                    f"[FT {cur['category_index']}/{len(cats)}] {category} {yyyymm} "
                    f"start={start} got={len(entries)} total={total} ok={cur['n_fulltext_ok']} fail={cur['n_extract_fail']}",
                    flush=True,
                )
                if total == 0 or not entries:
                    if seen:
                        empty_streak += 1
                    if seen and empty_streak >= 8:
                        break
                    yyyymm = next_month(yyyymm)
                    start = 0
                    cur["yyyymm"] = yyyymm
                    cur["start_index"] = 0
                    save_ft_cursor(conn, cur)
                    continue

                seen = True
                empty_streak = 0
                for ent in entries:
                    if max_papers is not None and batch_scored + batch_fail >= max_papers:
                        break
                    if max_seconds is not None and (time.time() - t0) >= max_seconds:
                        break
                    # Skip if already fulltext-valid
                    row = conn.execute(
                        "SELECT score_valid FROM fulltext WHERE arxiv_id=? AND ok=1 AND score_valid=1",
                        (ent["arxiv_id"],),
                    ).fetchone()
                    if row:
                        continue

                    meta = extract_arxiv(ent["arxiv_id"], sleep=SLEEP)
                    text = ""
                    if meta.get("ok") and meta.get("abs_path"):
                        try:
                            text = Path(meta["abs_path"]).read_text(encoding="utf-8", errors="replace")
                        except Exception:
                            text = ""
                    # ZERO truncation — score entire extract
                    score = score_fulltext(
                        title=ent["title"], fulltext=text, categories=ent["categories"]
                    )
                    if not meta.get("ok"):
                        score = {
                            "labels": ["EXTRACT_FAIL"],
                            "primary": "EXTRACT_FAIL",
                            "aid_sports": False,
                            "aid_poker": False,
                            "aid_crypto": False,
                            "transfer": False,
                            "uncertain": False,
                            "no_aid": False,
                            "rationale": f"extract failed: {meta.get('flags')}",
                            "phase": "fulltext",
                            "score_valid": False,
                        }
                        cur["n_extract_fail"] += 1
                        batch_fail += 1
                    else:
                        cur["n_fulltext_ok"] += 1
                        batch_scored += 1
                        if score.get("aid_sports"):
                            cur["n_aid_sports"] += 1
                        if score.get("aid_poker"):
                            cur["n_aid_poker"] += 1
                        if score.get("aid_crypto"):
                            cur["n_aid_crypto"] += 1
                        if score.get("transfer"):
                            cur["n_transfer"] += 1
                        if score.get("uncertain"):
                            cur["n_uncertain"] += 1
                        if score.get("no_aid"):
                            cur["n_no_aid"] += 1

                    persist_fulltext_score(conn, meta, score, ent, category, wave)
                    rec = {
                        "arxiv_id": ent["arxiv_id"],
                        "title": ent["title"],
                        "published": ent["published"],
                        "meta": {k: meta.get(k) for k in ("ok", "source", "extractor", "chars", "sha256", "path", "flags")},
                        "score": score,
                        "scored_at": utc_now(),
                    }
                    jf.write(json.dumps(rec, ensure_ascii=False) + "\n")
                    jf.flush()
                    if len(qa_samples) < 50:
                        qa_samples.append(rec)
                    print(
                        f"  {ent['arxiv_id']} chars={meta.get('chars')} "
                        f"flags={meta.get('flags')} label={score.get('primary')}",
                        flush=True,
                    )

                start += max(len(entries), page_size)
                cur["start_index"] = start
                cur["yyyymm"] = yyyymm
                save_ft_cursor(conn, cur)
                if start >= total:
                    yyyymm = next_month(yyyymm)
                    start = 0
                    cur["yyyymm"] = yyyymm
                    cur["start_index"] = 0
                    save_ft_cursor(conn, cur)

            # next category
            cur["category_index"] += 1
            cur["start_index"] = 0
            cur["yyyymm"] = "199201"
            if cur["category_index"] < len(cats):
                cur["category"] = cats[cur["category_index"]]
            save_ft_cursor(conn, cur)
    finally:
        jf.close()
        save_ft_cursor(conn, cur)
        conn.close()

    summary = {
        "wave": wave,
        "batch_fulltext_ok": batch_scored,
        "batch_extract_fail": batch_fail,
        "elapsed_s": round(time.time() - t0, 1),
        "cursor": get_ft_cursor(sqlite3.connect(str(WORK_DB))),
        "qa_samples": qa_samples[:20],
        "batch_jsonl": str(jsonl_path),
    }
    sqlite3.connect(str(WORK_DB)).close()
    (ROOT / "state" / "fulltext-rerun-summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    return summary


def run_from_queue(wave: str, max_papers: int | None, max_seconds: float | None) -> dict:
    """Drain Phase0 FULLTEXT_QUEUE / UNCERTAIN_FULLTEXT / audit SKIP_HARD preferentially.

    Order choice (documented in docs/arxiv-census-skip-filter.md):
      1) Finish Phase0 lock-order pass first (this runner is the deep-read stage).
      2) Within deep-read: FULLTEXT_QUEUE → UNCERTAIN_FULLTEXT → SKIP audit.
      3) Within each band: high-transfer categories first, then published/scored_at.
    """
    from score_phase0 import high_transfer_rank

    WORK_DB.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(WORK_DB))
    ensure_schema(conn)
    t0 = time.time()
    batch_scored = 0
    batch_fail = 0
    raw = conn.execute(
        """
        SELECT arxiv_id, title, abstract, primary_category, categories, published, harvest_category, phase0_label, scored_at
        FROM phase0
        WHERE phase0_label IN ('FULLTEXT_QUEUE','UNCERTAIN_FULLTEXT')
           OR (phase0_label='SKIP_HARD' AND audit_fulltext=1)
        """
    ).fetchall()
    label_pri = {"FULLTEXT_QUEUE": 0, "UNCERTAIN_FULLTEXT": 1}

    def _sort_key(row):
        arxiv_id, title, abstract, prim, cats_j, published, hcat, p0lab, scored_at = row
        cats = json.loads(cats_j or "[]")
        return (
            label_pri.get(p0lab, 2),
            high_transfer_rank(prim or hcat, cats),
            published or "",
            scored_at or "",
            arxiv_id,
        )

    rows = sorted(raw, key=_sort_key)
    print(
        f"FULLTEXT FROM-QUEUE candidates={len(rows)} "
        f"(band→high-transfer→date)",
        flush=True,
    )
    jsonl_path = ROOT / "batches" / f"fulltext-queue-{utc_now().replace(':', '')}.jsonl"
    jsonl_path.parent.mkdir(parents=True, exist_ok=True)
    jf = jsonl_path.open("a", encoding="utf-8")
    try:
        for arxiv_id, title, abstract, prim, cats_j, published, hcat, p0lab, _scored_at in rows:
            if max_papers is not None and batch_scored + batch_fail >= max_papers:
                break
            if max_seconds is not None and (time.time() - t0) >= max_seconds:
                break
            existing = conn.execute(
                "SELECT score_valid FROM fulltext WHERE arxiv_id=? AND ok=1 AND score_valid=1",
                (arxiv_id,),
            ).fetchone()
            if existing:
                continue
            cats = json.loads(cats_j or "[]")
            ent = {
                "arxiv_id": arxiv_id,
                "title": title or "",
                "abstract": abstract or "",
                "published": published or "",
                "primary_category": prim or hcat or "",
                "categories": cats,
            }
            meta = extract_arxiv(arxiv_id, sleep=SLEEP)
            text = ""
            if meta.get("ok") and meta.get("abs_path"):
                try:
                    text = Path(meta["abs_path"]).read_text(encoding="utf-8", errors="replace")
                except Exception:
                    text = ""
            score = score_fulltext(title=ent["title"], fulltext=text, categories=cats)
            if not meta.get("ok"):
                score = {
                    "labels": ["EXTRACT_FAIL"],
                    "primary": "EXTRACT_FAIL",
                    "aid_sports": False,
                    "aid_poker": False,
                    "aid_crypto": False,
                    "transfer": False,
                    "uncertain": False,
                    "no_aid": False,
                    "rationale": f"extract failed: {meta.get('flags')}",
                    "phase": "fulltext",
                    "score_valid": False,
                }
                batch_fail += 1
            else:
                batch_scored += 1
            persist_fulltext_score(conn, meta, score, ent, hcat or prim or "", wave)
            jf.write(
                json.dumps(
                    {
                        "arxiv_id": arxiv_id,
                        "phase0_label": p0lab,
                        "meta": {k: meta.get(k) for k in ("ok", "chars", "flags", "extractor")},
                        "score": score,
                        "scored_at": utc_now(),
                    },
                    ensure_ascii=False,
                )
                + "\n"
            )
            jf.flush()
            print(
                f"  [Q:{p0lab}] {arxiv_id} chars={meta.get('chars')} label={score.get('primary')}",
                flush=True,
            )
    finally:
        jf.close()
        conn.close()
    return {
        "wave": wave,
        "mode": "from-queue",
        "batch_fulltext_ok": batch_scored,
        "batch_extract_fail": batch_fail,
        "elapsed_s": round(time.time() - t0, 1),
        "batch_jsonl": str(jsonl_path),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--wave", default="fulltext-rerun")
    ap.add_argument("--max-papers", type=int, default=None)
    ap.add_argument("--max-seconds", type=float, default=None)
    ap.add_argument("--page-size", type=int, default=20)
    ap.add_argument("--reset", action="store_true", help="restart fulltext cursor at cat 0")
    ap.add_argument(
        "--from-queue",
        action="store_true",
        help="Drain Phase0 FULLTEXT_QUEUE / UNCERTAIN / audit SKIP (prefer after Phase0 pass)",
    )
    args = ap.parse_args()
    if args.from_queue:
        s = run_from_queue(args.wave, args.max_papers, args.max_seconds)
        print(json.dumps(s, indent=2))
    else:
        s = run(args.wave, args.max_papers, args.max_seconds, args.page_size, args.reset)
        print(json.dumps({k: s[k] for k in ("wave", "batch_fulltext_ok", "batch_extract_fail", "elapsed_s", "batch_jsonl")}, indent=2))
        print("cursor=", json.dumps(s["cursor"], indent=2))


if __name__ == "__main__":
    main()
