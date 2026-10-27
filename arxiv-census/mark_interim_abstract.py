#!/usr/bin/env python3
"""Stamp all abstract-only scores as INTERIM_ABSTRACT_ONLY — not valid for AID decisions."""
from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

WORK = Path("/tmp/arxiv-census/census.sqlite")
ROOT = Path(__file__).resolve().parent


def main() -> None:
    if not WORK.exists() or WORK.stat().st_size < 10_000:
        raise SystemExit(f"missing work db {WORK}")
    conn = sqlite3.connect(str(WORK))
    # schema upgrades
    cols = {r[1] for r in conn.execute("PRAGMA table_info(papers)").fetchall()}
    alters = []
    if "score_phase" not in cols:
        alters.append("ALTER TABLE papers ADD COLUMN score_phase TEXT")
    if "score_valid" not in cols:
        alters.append("ALTER TABLE papers ADD COLUMN score_valid INTEGER DEFAULT 0")
    if "interim_note" not in cols:
        alters.append("ALTER TABLE papers ADD COLUMN interim_note TEXT")
    for a in alters:
        conn.execute(a)
    conn.execute(
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
            scored_at TEXT
        )
        """
    )
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    n = conn.execute("SELECT count(*) FROM papers").fetchone()[0]
    # Preserve prior labels in interim_note; invalidate for AID
    conn.execute(
        """
        UPDATE papers SET
          score_phase = 'INTERIM_ABSTRACT_ONLY',
          score_valid = 0,
          interim_note = COALESCE(interim_note, '') || 
            printf(' | abstract_labels=%s @ %s', labels, ?),
          primary_label = 'INTERIM_ABSTRACT_ONLY',
          labels = '["INTERIM_ABSTRACT_ONLY"]',
          aid_sports = 0, aid_poker = 0, aid_crypto = 0,
          transfer = 0, uncertain = 0, no_aid = 0,
          rationale = 'INTERIM_ABSTRACT_ONLY — abstract pass invalid for AID; awaiting fulltext'
        WHERE COALESCE(score_phase, '') != 'fulltext' OR score_valid IS NULL OR score_valid = 0
        """,
        (now,),
    )
    # Don't wipe rows already fulltext-valid if any
    conn.execute(
        """
        UPDATE papers SET score_phase='INTERIM_ABSTRACT_ONLY', score_valid=0
        WHERE score_phase IS NULL OR score_phase IN ('abstract', 'abstract_interim', '')
        """
    )
    changed = conn.total_changes
    conn.commit()
    # refresh cursor stamp
    cur_path = ROOT / "state" / "cursor.json"
    if cur_path.exists():
        cur = json.loads(cur_path.read_text())
        cur["abstract_invalidated_at"] = now
        cur["abstract_rows_marked_interim"] = n
        cur["note"] = "Abstract-only scores INVALID for AID; fulltext re-run is authoritative"
        cur_path.write_text(json.dumps(cur, indent=2) + "\n")
    (ROOT / "state" / "interim_abstract_stamp.json").write_text(
        json.dumps(
            {
                "stamped_at": now,
                "n_papers": n,
                "label": "INTERIM_ABSTRACT_ONLY",
                "aid_valid": False,
            },
            indent=2,
        )
        + "\n"
    )
    conn.close()
    print(json.dumps({"stamped": n, "changes": changed, "at": now}, indent=2))


if __name__ == "__main__":
    main()
