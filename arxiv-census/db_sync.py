#!/usr/bin/env python3
"""Work-DB inflate + gzip mirror to agent store (raw sqlite often too large for store FS)."""
from __future__ import annotations

import gzip
import shutil
import sqlite3
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
WORK_DB = Path("/tmp/arxiv-census/census.sqlite")
STORE_GZ = ROOT / "census.sqlite.gz"


def ensure_work_db() -> Path:
    WORK_DB.parent.mkdir(parents=True, exist_ok=True)
    if WORK_DB.exists() and WORK_DB.stat().st_size > 0:
        return WORK_DB
    if STORE_GZ.exists():
        with gzip.open(STORE_GZ, "rb") as src, open(WORK_DB, "wb") as dst:
            shutil.copyfileobj(src, dst)
    else:
        conn = sqlite3.connect(str(WORK_DB))
        conn.close()
    return WORK_DB


def mirror_gzip(work_db: Path | None = None, compresslevel: int = 1) -> Path:
    """Gzip to /tmp then replace store mirror. Deletes old gz first to stay under quota."""
    src = work_db or WORK_DB
    # Clean leftover failed replaces
    for p in STORE_GZ.parent.glob("census.sqlite.gz.tmp*"):
        try:
            p.unlink()
        except OSError:
            pass
    with tempfile.NamedTemporaryFile(prefix="census-sqlite-", suffix=".gz", dir="/tmp", delete=False) as tmpf:
        tmp_path = Path(tmpf.name)
    try:
        with open(src, "rb") as fsrc, gzip.open(tmp_path, "wb", compresslevel=compresslevel) as fdst:
            shutil.copyfileobj(fsrc, fdst)
        # Free quota before copy: remove previous mirror
        if STORE_GZ.exists():
            STORE_GZ.unlink()
        shutil.copy2(tmp_path, STORE_GZ)
    finally:
        try:
            tmp_path.unlink(missing_ok=True)
        except OSError:
            pass
    return STORE_GZ


def export_phase0_compact(conn: sqlite3.Connection, out: Path | None = None) -> Path:
    """Smaller durable Phase0 export when full DB gzip is tight on quota."""
    import json

    out = out or (ROOT / "phase0-scores.json.gz")
    rows = conn.execute(
        """SELECT arxiv_id, primary_category, categories, published, harvest_category,
                  phase0_label, phase0_reason, audit_fulltext, scored_at
           FROM phase0 ORDER BY scored_at"""
    )
    tmp = Path("/tmp/phase0-scores.jsonl.gz")
    with gzip.open(tmp, "wt", encoding="utf-8") as f:
        for r in rows:
            f.write(
                json.dumps(
                    {
                        "arxiv_id": r[0],
                        "primary_category": r[1],
                        "categories": json.loads(r[2] or "[]"),
                        "published": r[3],
                        "harvest_category": r[4],
                        "phase0_label": r[5],
                        "phase0_reason": r[6],
                        "audit_fulltext": r[7],
                        "scored_at": r[8],
                    },
                    ensure_ascii=False,
                )
                + "\n"
            )
    if out.exists():
        out.unlink()
    shutil.copy2(tmp, out)
    tmp.unlink(missing_ok=True)
    return out
