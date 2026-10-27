#!/usr/bin/env python3
"""Continue census across categories.json after current window category is exhausted."""
from __future__ import annotations

import argparse
import json
import sqlite3
import time
from pathlib import Path

from run_census import ROOT, get_cursor, init_db, load_categories, save_cursor, utc_now
from run_census_windows import atomic_write_json, run as run_windows


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--wave", type=int, default=3)
    ap.add_argument("--max-seconds", type=float, default=1800)
    ap.add_argument("--page-size", type=int, default=100)
    ap.add_argument("--empty-month-stop", type=int, default=6, help="stop cat after N consecutive empty months")
    ap.add_argument("--start-yyyymm", default="199201")
    ap.add_argument("--end-yyyymm", default="202610")
    args = ap.parse_args()

    cats = load_categories()
    work_db = Path("/tmp/arxiv-census/census.sqlite")
    conn = init_db(work_db)
    cur = get_cursor(conn)
    conn.close()

    t0 = time.time()
    win_path = ROOT / "state" / "window.json"
    win = json.loads(win_path.read_text()) if win_path.exists() else {}

    cat_idx = int(cur.get("category_index") or 0)
    # If window says we're past useful astro-ph content, advance
    if win.get("category") == "astro-ph" and str(win.get("yyyymm", "0")) >= "201001":
        # umbrella essentially exhausted; move to next cat in lock order
        if cat_idx == 0:
            cat_idx = 1
            atomic_write_json(
                win_path,
                {
                    "category": cats[cat_idx],
                    "yyyymm": args.start_yyyymm,
                    "start": 0,
                    "updated_at": utc_now(),
                    "note": "advanced after astro-ph umbrella near-exhaustion",
                },
            )

    while cat_idx < len(cats):
        remaining = args.max_seconds - (time.time() - t0)
        if remaining < 60:
            break
        category = cats[cat_idx]
        # sync category_index
        conn = init_db(work_db)
        cur = get_cursor(conn)
        cur["category_index"] = cat_idx
        cur["category"] = category
        cur["wave"] = args.wave
        save_cursor(conn, cur)
        conn.close()

        win = json.loads(win_path.read_text()) if win_path.exists() else {}
        start_ym = win.get("yyyymm", args.start_yyyymm) if win.get("category") == category else args.start_yyyymm
        print(f"=== CONTINUE cat_idx={cat_idx} cat={category} from={start_ym} budget={remaining:.0f}s", flush=True)

        # Run windows with early empty-month stop via wrapping end year gradually
        # Use run_windows but stop early by capping end and detecting stagnation
        summary = run_windows(
            wave=args.wave,
            category=category,
            start_yyyymm=str(start_ym),
            end_yyyymm=args.end_yyyymm,
            max_papers=None,
            max_seconds=min(remaining, 900),
            page_size=args.page_size,
        )
        print("summary_wave_scored", summary.get("wave_scored"), "next", summary.get("next_yyyymm"), flush=True)

        # Decide whether category is done: next_yyyymm near end and little new scoring
        next_ym = str(summary.get("next_yyyymm") or start_ym)
        if summary.get("wave_scored", 0) == 0 and next_ym > str(start_ym):
            # advanced through empty range with no new papers
            cat_idx += 1
            if cat_idx < len(cats):
                atomic_write_json(
                    win_path,
                    {
                        "category": cats[cat_idx],
                        "yyyymm": args.start_yyyymm,
                        "start": 0,
                        "updated_at": utc_now(),
                    },
                )
            continue
        if next_ym >= args.end_yyyymm:
            cat_idx += 1
            if cat_idx < len(cats):
                atomic_write_json(
                    win_path,
                    {
                        "category": cats[cat_idx],
                        "yyyymm": args.start_yyyymm,
                        "start": 0,
                        "updated_at": utc_now(),
                    },
                )
            continue
        # still mid-category; loop will resume same cat with updated window
        # refresh idx from cursor
        conn = init_db(work_db)
        cur = get_cursor(conn)
        cur["category_index"] = cat_idx
        save_cursor(conn, cur)
        conn.close()

    conn = init_db(work_db)
    print("DONE continue", json.dumps(get_cursor(conn), indent=2))
    conn.close()


if __name__ == "__main__":
    main()
