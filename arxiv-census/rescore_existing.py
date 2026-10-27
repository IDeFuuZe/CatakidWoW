#!/usr/bin/env python3
"""Re-apply Phase-A scorer to all ledger rows (fix FP lexicon updates)."""
from __future__ import annotations

import json
import shutil
import sqlite3
from pathlib import Path

from score_abstract import score_abstract

ROOT = Path(__file__).resolve().parent
WORK = Path("/tmp/arxiv-census/census.sqlite")
STORE = ROOT / "census.sqlite"


def main() -> None:
    WORK.parent.mkdir(parents=True, exist_ok=True)
    # Prefer larger intact work DB; never clobber work with empty/corrupt store.
    def _ok(path: Path) -> bool:
        if not path.exists() or path.stat().st_size < 10_000:
            return False
        try:
            c = sqlite3.connect(str(path))
            n = c.execute("SELECT count(*) FROM papers").fetchone()[0]
            c.close()
            return n > 0
        except Exception:
            return False
    if _ok(WORK):
        db = WORK
    elif _ok(STORE):
        shutil.copy2(STORE, WORK)
        db = WORK
    else:
        raise SystemExit("no intact census DB in /tmp or store")
    conn = sqlite3.connect(str(db))
    rows = conn.execute(
        "SELECT arxiv_id, title, abstract, categories FROM papers"
    ).fetchall()
    n_changed = 0
    counts = {
        "aid_sports": 0,
        "aid_poker": 0,
        "aid_crypto": 0,
        "transfer": 0,
        "uncertain": 0,
        "no_aid": 0,
    }
    for arxiv_id, title, abstract, categories_json in rows:
        cats = json.loads(categories_json) if categories_json else []
        score = score_abstract(title=title or "", abstract=abstract or "", categories=cats)
        conn.execute(
            """
            UPDATE papers SET
              labels=?, primary_label=?,
              aid_sports=?, aid_poker=?, aid_crypto=?,
              transfer=?, uncertain=?, no_aid=?, rationale=?
            WHERE arxiv_id=?
            """,
            (
                json.dumps(score["labels"]),
                score["primary"],
                int(score["aid_sports"]),
                int(score["aid_poker"]),
                int(score["aid_crypto"]),
                int(score["transfer"]),
                int(score["uncertain"]),
                int(score["no_aid"]),
                score["rationale"],
                arxiv_id,
            ),
        )
        if score["aid_sports"]:
            counts["aid_sports"] += 1
        if score["aid_poker"]:
            counts["aid_poker"] += 1
        if score["aid_crypto"]:
            counts["aid_crypto"] += 1
        if score["transfer"]:
            counts["transfer"] += 1
        if score["uncertain"]:
            counts["uncertain"] += 1
        if score["no_aid"]:
            counts["no_aid"] += 1
        n_changed += 1
    # refresh aggregate cursor counters (preserve position)
    conn.execute(
        """
        UPDATE cursor_state SET
          n_aid_sports=?, n_aid_poker=?, n_aid_crypto=?,
          n_transfer=?, n_uncertain=?, n_no_aid=?
        WHERE id=1
        """,
        (
            counts["aid_sports"],
            counts["aid_poker"],
            counts["aid_crypto"],
            counts["transfer"],
            counts["uncertain"],
            counts["no_aid"],
        ),
    )
    conn.commit()
    try:
        shutil.copy2(db, STORE)
    except OSError as e:
        print("store sqlite sync failed:", e)
        # keep gzip mirror
        import gzip, subprocess
        gz = STORE.with_suffix(STORE.suffix + ".gz")
        try:
            subprocess.check_call(["gzip", "-c", "-1", str(db)], stdout=open(gz, "wb"))
            print("wrote", gz)
        except Exception as e2:
            print("gz fallback failed", e2)
    # refresh cursor.json
    from run_census import get_cursor, save_cursor

    cur = get_cursor(conn)
    save_cursor(conn, cur)
    conn.close()
    print(json.dumps({"rescored": n_changed, "counts": counts}, indent=2))


if __name__ == "__main__":
    main()
