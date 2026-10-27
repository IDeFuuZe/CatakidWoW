#!/usr/bin/env python3
"""
Resumable arXiv FULL CENSUS runner — metadata+abstract, zero keyword pre-filter.
Strict order: lexicographic category → submittedDate ascending. Dedup by arXiv id.
"""
from __future__ import annotations

import argparse
import json
import re
import sqlite3
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

from score_abstract import score_abstract

re_version = re.compile(r"(v\d+)$")

ROOT = Path(__file__).resolve().parent
ATOM_NS = {
    "atom": "http://www.w3.org/2005/Atom",
    "opensearch": "http://a9.com/-/spec/opensearch/1.1/",
    "arxiv": "http://arxiv.org/schemas/atom",
}
API = "https://export.arxiv.org/api/query"
UA = "arxiv-census/1.0 (IDeFuuZe Dec1 full-census; mailto:none; respects 3s rate limit)"
SLEEP_S = 3.5
PAGE_SIZE = 200  # bulk metadata; 500 can trigger arXiv 5xx under load


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_categories() -> list[str]:
    path = ROOT / "categories.json"
    if not path.exists():
        raise SystemExit("categories.json missing — run build_categories.py first")
    data = json.loads(path.read_text(encoding="utf-8"))
    return list(data["categories"])


def init_db(db_path: Path) -> sqlite3.Connection:
    # Agent store FS can reject WAL; use DELETE journal + short timeout.
    conn = sqlite3.connect(str(db_path), timeout=60)
    conn.execute("PRAGMA journal_mode=DELETE")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS papers (
            arxiv_id TEXT PRIMARY KEY,
            version TEXT,
            title TEXT,
            abstract TEXT,
            primary_category TEXT,
            categories TEXT,
            published TEXT,
            updated TEXT,
            labels TEXT,
            primary_label TEXT,
            aid_sports INTEGER,
            aid_poker INTEGER,
            aid_crypto INTEGER,
            transfer INTEGER,
            uncertain INTEGER,
            no_aid INTEGER,
            rationale TEXT,
            harvest_category TEXT,
            scored_at TEXT,
            wave INTEGER
        );
        CREATE TABLE IF NOT EXISTS cursor_state (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            category_index INTEGER,
            category TEXT,
            start_index INTEGER,
            total_in_cat INTEGER,
            n_scored INTEGER,
            n_skipped_dup INTEGER,
            n_aid_sports INTEGER,
            n_aid_poker INTEGER,
            n_aid_crypto INTEGER,
            n_transfer INTEGER,
            n_uncertain INTEGER,
            n_no_aid INTEGER,
            updated_at TEXT,
            wave INTEGER
        );
        CREATE INDEX IF NOT EXISTS idx_papers_primary ON papers(primary_label);
        CREATE INDEX IF NOT EXISTS idx_papers_pub ON papers(published);
        """
    )
    row = conn.execute("SELECT id FROM cursor_state WHERE id=1").fetchone()
    if not row:
        conn.execute(
            """
            INSERT INTO cursor_state (
              id, category_index, category, start_index, total_in_cat,
              n_scored, n_skipped_dup, n_aid_sports, n_aid_poker, n_aid_crypto,
              n_transfer, n_uncertain, n_no_aid, updated_at, wave
            ) VALUES (1, 0, '', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, ?, 1)
            """,
            (utc_now(),),
        )
        conn.commit()
    return conn


def get_cursor(conn: sqlite3.Connection) -> dict:
    cols = [
        "category_index", "category", "start_index", "total_in_cat", "n_scored",
        "n_skipped_dup", "n_aid_sports", "n_aid_poker", "n_aid_crypto",
        "n_transfer", "n_uncertain", "n_no_aid", "updated_at", "wave",
    ]
    row = conn.execute(
        f"SELECT {', '.join(cols)} FROM cursor_state WHERE id=1"
    ).fetchone()
    return dict(zip(cols, row))


def save_cursor(conn: sqlite3.Connection, cur: dict) -> None:
    cur = dict(cur)
    cur["updated_at"] = utc_now()
    conn.execute(
        """
        UPDATE cursor_state SET
          category_index=?, category=?, start_index=?, total_in_cat=?,
          n_scored=?, n_skipped_dup=?, n_aid_sports=?, n_aid_poker=?, n_aid_crypto=?,
          n_transfer=?, n_uncertain=?, n_no_aid=?, updated_at=?, wave=?
        WHERE id=1
        """,
        (
            cur["category_index"], cur["category"], cur["start_index"], cur["total_in_cat"],
            cur["n_scored"], cur["n_skipped_dup"], cur["n_aid_sports"], cur["n_aid_poker"],
            cur["n_aid_crypto"], cur["n_transfer"], cur["n_uncertain"], cur["n_no_aid"],
            cur["updated_at"], cur["wave"],
        ),
    )
    conn.commit()
    cursor_path = ROOT / "state" / "cursor.json"
    text = json.dumps(cur, indent=2) + "\n"
    for attempt in range(6):
        try:
            cursor_path.write_text(text, encoding="utf-8")
            break
        except (BlockingIOError, OSError) as e:
            print(f"cursor write warn: {e}; attempt {attempt+1}", flush=True)
            time.sleep(0.4 * (attempt + 1))
    else:
        fb = Path("/tmp/arxiv-census/cursor.json")
        fb.write_text(text, encoding="utf-8")
        print(f"cursor kept in {fb}", flush=True)


def normalize_id(raw: str) -> tuple[str, str]:
    # http://arxiv.org/abs/astro-ph/0612773v1 → (astro-ph/0612773, v1)
    # http://arxiv.org/abs/1706.03762v1 → (1706.03762, v1)
    s = raw.strip()
    s = s.replace("http://arxiv.org/abs/", "").replace("https://arxiv.org/abs/", "")
    s = s.replace("http://www.arxiv.org/abs/", "")
    version = ""
    m = re_version.search(s)
    if m:
        version = m.group(1)
        s = s[: m.start()]
    return s, version


def fetch_page(category: str, start: int, max_results: int) -> tuple[int, list[dict]]:
    params = {
        "search_query": f"cat:{category}",
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
            print(f"URL error {e}; sleep {wait:.1f}s (attempt {attempt+1})", flush=True)
            time.sleep(wait)
            continue
    else:
        raise RuntimeError(f"failed to fetch {url}")

    root = ET.fromstring(xml_bytes)
    total_el = root.find("opensearch:totalResults", ATOM_NS)
    total = int(total_el.text) if total_el is not None and total_el.text else 0
    entries: list[dict] = []
    for entry in root.findall("atom:entry", ATOM_NS):
        id_el = entry.find("atom:id", ATOM_NS)
        title_el = entry.find("atom:title", ATOM_NS)
        summary_el = entry.find("atom:summary", ATOM_NS)
        published_el = entry.find("atom:published", ATOM_NS)
        updated_el = entry.find("atom:updated", ATOM_NS)
        primary_el = entry.find("arxiv:primary_category", ATOM_NS)
        cats = [
            c.get("term", "")
            for c in entry.findall("atom:category", ATOM_NS)
            if c.get("term")
        ]
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
                "primary_category": (primary_el.get("term") if primary_el is not None else (cats[0] if cats else category)),
                "categories": cats,
                "published": published_el.text if published_el is not None else "",
                "updated": updated_el.text if updated_el is not None else "",
            }
        )
    return total, entries


def bump_counts(cur: dict, score: dict) -> None:
    if score["aid_sports"]:
        cur["n_aid_sports"] += 1
    if score["aid_poker"]:
        cur["n_aid_poker"] += 1
    if score["aid_crypto"]:
        cur["n_aid_crypto"] += 1
    if score["transfer"]:
        cur["n_transfer"] += 1
    if score["uncertain"]:
        cur["n_uncertain"] += 1
    if score["no_aid"]:
        cur["n_no_aid"] += 1


def sync_db_to_store(work_db: Path, store_db: Path) -> None:
    """Best-effort store sync. Prefer gzip — raw sqlite often EIO/ENOSPC on agent-store."""
    import gzip
    import shutil

    try:
        gz = store_db.with_suffix(store_db.suffix + ".gz")
        with open(work_db, "rb") as src, gzip.open(gz, "wb", compresslevel=1) as dst:
            shutil.copyfileobj(src, dst, length=1024 * 1024)
    except OSError as e:
        print(f"store db gz sync warn: {e}", flush=True)
    # Skip raw sqlite copy by default (large-file store FS failures).


class ShardWriter:
    """Append JSONL in ~shard_lines chunks to avoid store FS quirks on huge files."""

    def __init__(self, dir_path: Path, prefix: str, shard_lines: int = 200) -> None:
        self.dir_path = dir_path
        self.prefix = prefix
        self.shard_lines = shard_lines
        self.dir_path.mkdir(parents=True, exist_ok=True)
        self.part = 0
        self.count_in_part = 0
        self.current_path: Path | None = None
        self._fh = None
        self.paths: list[str] = []
        self._open_next()

    def _safe_close(self) -> None:
        fh = self._fh
        self._fh = None
        if not fh:
            return
        for attempt in range(5):
            try:
                if not fh.closed:
                    fh.flush()
                    fh.close()
                break
            except (BlockingIOError, OSError, ValueError):
                time.sleep(0.5 * (attempt + 1))

    def _open_next(self) -> None:
        self._safe_close()
        self.part += 1
        self.count_in_part = 0
        self.current_path = self.dir_path / f"{self.prefix}-{self.part:05d}.jsonl"
        for attempt in range(5):
            try:
                self._fh = self.current_path.open("a", encoding="utf-8")
                break
            except (BlockingIOError, OSError):
                time.sleep(0.5 * (attempt + 1))
        else:
            # last resort: write under /tmp and note path
            alt = Path("/tmp/arxiv-census") / self.current_path.name
            alt.parent.mkdir(parents=True, exist_ok=True)
            self._fh = alt.open("a", encoding="utf-8")
            self.current_path = alt
        self.paths.append(str(self.current_path))

    def write(self, line: str) -> None:
        assert self._fh is not None
        if self.count_in_part >= self.shard_lines:
            self._open_next()
        for attempt in range(5):
            try:
                self._fh.write(line + "\n")
                break
            except (BlockingIOError, OSError):
                time.sleep(0.3 * (attempt + 1))
                if attempt == 4:
                    self._open_next()
                    self._fh.write(line + "\n")
        self.count_in_part += 1

    def flush(self) -> None:
        if self._fh:
            try:
                self._fh.flush()
            except (BlockingIOError, OSError):
                pass

    def close(self) -> None:
        self._safe_close()


def run(wave: int, max_papers: int | None, max_seconds: float | None, page_size: int) -> dict:
    import shutil

    cats = load_categories()
    work_dir = Path("/tmp/arxiv-census")
    work_dir.mkdir(parents=True, exist_ok=True)
    work_db = work_dir / "census.sqlite"
    store_db = ROOT / "census.sqlite"
    # Resume from store copy if present and work db empty/missing
    if store_db.exists() and (
        not work_db.exists()
        or work_db.stat().st_size < store_db.stat().st_size
    ):
        try:
            shutil.copy2(store_db, work_db)
        except OSError:
            pass

    scores_dir = ROOT / "scores"
    batch_dir = ROOT / "batches"
    scores_dir.mkdir(parents=True, exist_ok=True)
    batch_dir.mkdir(parents=True, exist_ok=True)
    (ROOT / "state").mkdir(parents=True, exist_ok=True)

    conn = init_db(work_db)
    cur = get_cursor(conn)
    cur["wave"] = wave
    if not cur["category"] and cur["category_index"] < len(cats):
        cur["category"] = cats[cur["category_index"]]
        cur["start_index"] = cur["start_index"] or 0

    t0 = time.time()
    wave_scored = 0
    wave_aid_hits: list[dict] = []
    stamp = utc_now().replace(":", "")
    scores_w = ShardWriter(scores_dir, f"scores-wave{wave}", shard_lines=200)
    batch_w = ShardWriter(batch_dir, f"wave{wave}-{stamp}", shard_lines=500)

    print(
        f"resume cat_idx={cur['category_index']} cat={cur['category']} "
        f"start={cur['start_index']} n_scored={cur['n_scored']}",
        flush=True,
    )

    try:
        while cur["category_index"] < len(cats):
            if max_papers is not None and wave_scored >= max_papers:
                break
            if max_seconds is not None and (time.time() - t0) >= max_seconds:
                break

            category = cats[cur["category_index"]]
            cur["category"] = category
            start = int(cur["start_index"])

            time.sleep(SLEEP_S)
            try:
                total, entries = fetch_page(category, start, page_size)
            except RuntimeError as e:
                print(f"page fetch failed ({e}); backing off 60s then retry loop", flush=True)
                time.sleep(60)
                try:
                    total, entries = fetch_page(category, start, page_size)
                except RuntimeError as e2:
                    print(f"page fetch failed again ({e2}); saving cursor and stopping wave", flush=True)
                    save_cursor(conn, cur)
                    sync_db_to_store(work_db, store_db)
                    break
            cur["total_in_cat"] = total
            print(
                f"[{cur['category_index']}/{len(cats)}] {category} start={start} "
                f"got={len(entries)} total={total}",
                flush=True,
            )

            if total == 0 or (not entries and start >= total):
                cur["category_index"] += 1
                cur["start_index"] = 0
                cur["total_in_cat"] = 0
                if cur["category_index"] < len(cats):
                    cur["category"] = cats[cur["category_index"]]
                save_cursor(conn, cur)
                sync_db_to_store(work_db, store_db)
                continue

            page_new = 0
            for ent in entries:
                if max_papers is not None and wave_scored >= max_papers:
                    break
                if max_seconds is not None and (time.time() - t0) >= max_seconds:
                    break

                exists = conn.execute(
                    "SELECT 1 FROM papers WHERE arxiv_id=?", (ent["arxiv_id"],)
                ).fetchone()
                if exists:
                    cur["n_skipped_dup"] += 1
                    continue

                score = score_abstract(
                    title=ent["title"],
                    abstract=ent["abstract"],
                    categories=ent["categories"],
                )
                scored_at = utc_now()
                rec = {
                    **ent,
                    **score,
                    "harvest_category": category,
                    "scored_at": scored_at,
                    "wave": wave,
                }
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

            # advance start; if page empty but start < total, still advance to avoid stall
            new_start = start + max(len(entries), page_size)
            if not entries:
                new_start = start + page_size
            cur["start_index"] = new_start
            if new_start >= total:
                cur["category_index"] += 1
                cur["start_index"] = 0
                cur["total_in_cat"] = 0
                if cur["category_index"] < len(cats):
                    cur["category"] = cats[cur["category_index"]]
            save_cursor(conn, cur)
            sync_db_to_store(work_db, store_db)
            print(
                f"  page_new={page_new} wave_scored={wave_scored} "
                f"total_scored={cur['n_scored']} aids="
                f"S{cur['n_aid_sports']}/P{cur['n_aid_poker']}/C{cur['n_aid_crypto']} "
                f"T{cur['n_transfer']} U{cur['n_uncertain']}",
                flush=True,
            )
    finally:
        batch_w.close()
        scores_w.close()
        save_cursor(conn, cur)
        sync_db_to_store(work_db, store_db)
        conn.close()

    conn2 = init_db(work_db)
    summary = {
        "wave": wave,
        "wave_scored": wave_scored,
        "elapsed_s": round(time.time() - t0, 1),
        "cursor": get_cursor(conn2),
        "score_shards": scores_w.paths,
        "batch_shards": batch_w.paths,
        "aid_hits_wave": wave_aid_hits[:200],
        "n_aid_hits_wave": len(wave_aid_hits),
    }
    conn2.close()
    (ROOT / "state" / f"wave{wave}-summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    # Convenience pointer for monolithic consumers
    (ROOT / "scores.jsonl.README").write_text(
        "Scores are sharded under scores/scores-waveN-XXXXX.jsonl (store FS safety).\n"
        "Authoritative query surface: census.sqlite (+ /tmp/arxiv-census/census.sqlite work copy).\n",
        encoding="utf-8",
    )
    return summary


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--wave", type=int, default=1)
    ap.add_argument("--max-papers", type=int, default=None)
    ap.add_argument("--max-seconds", type=float, default=None)
    ap.add_argument("--page-size", type=int, default=PAGE_SIZE)
    args = ap.parse_args()
    summary = run(args.wave, args.max_papers, args.max_seconds, args.page_size)
    print(json.dumps({
        k: summary[k]
        for k in ("wave", "wave_scored", "elapsed_s", "n_aid_hits_wave", "score_shards", "batch_shards")
        if k in summary
    }, indent=2))
    print("cursor=", json.dumps(summary["cursor"], indent=2))


if __name__ == "__main__":
    main()
