#!/usr/bin/env python3
"""
Daily new-paper scan (Catakid login cadence): weekdays 16:00 / weekends 09:00 Europe/London.
All new arXiv submissions since last daily cursor — FULL PDF extract + score. No pre-filter.
"""
from __future__ import annotations

import argparse
import json
import sqlite3
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

from fulltext_extract import extract_arxiv
from run_fulltext_rerun import ensure_schema, persist_fulltext_score, utc_now
from score_fulltext import score_fulltext

ROOT = Path(__file__).resolve().parent
WORK_DB = Path("/tmp/arxiv-census/census.sqlite")
DOCS = ROOT.parent.parent / "docs"  # stores/.../docs via relative? 
# Prefer absolute store docs
DOCS = Path("/cursor/stores/bc-28a8dd7c-8662-49a7-9938-a5fa31b1d070/docs")
API = "https://export.arxiv.org/api/query"
UA = "arxiv-census-daily/1.0"
ATOM_NS = {
    "atom": "http://www.w3.org/2005/Atom",
    "opensearch": "http://a9.com/-/spec/opensearch/1.1/",
    "arxiv": "http://arxiv.org/schemas/atom",
}
LONDON = ZoneInfo("Europe/London")
SLEEP = 3.5


def load_daily_cursor() -> dict:
    p = ROOT / "state" / "daily_cursor.json"
    if p.exists():
        return json.loads(p.read_text())
    # default: yesterday 00:00 London
    yday = datetime.now(LONDON).date() - timedelta(days=1)
    return {"last_submitted_to": yday.strftime("%Y%m%d") + "0000", "updated_at": None}


def save_daily_cursor(cur: dict) -> None:
    (ROOT / "state").mkdir(parents=True, exist_ok=True)
    (ROOT / "state" / "daily_cursor.json").write_text(json.dumps(cur, indent=2) + "\n")


def fetch_new_since(submitted_from: str, submitted_to: str, start: int, page_size: int) -> tuple[int, list[dict]]:
    # all categories — no cat filter
    q = f"submittedDate:[{submitted_from} TO {submitted_to}]"
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
    with urllib.request.urlopen(req, timeout=180) as resp:
        xml_bytes = resp.read()
    root = ET.fromstring(xml_bytes)
    total_el = root.find("opensearch:totalResults", ATOM_NS)
    total = int(total_el.text) if total_el is not None and total_el.text else 0
    import re

    entries = []
    for entry in root.findall("atom:entry", ATOM_NS):
        id_el = entry.find("atom:id", ATOM_NS)
        title_el = entry.find("atom:title", ATOM_NS)
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
                "published": published_el.text if published_el is not None else "",
                "primary_category": primary_el.get("term") if primary_el is not None else (cats[0] if cats else ""),
                "categories": cats,
            }
        )
    return total, entries


def run(dry_run: bool = False) -> dict:
    now_l = datetime.now(LONDON)
    # window: last cursor → now
    dcur = load_daily_cursor()
    submitted_from = dcur.get("last_submitted_to") or (now_l - timedelta(days=1)).strftime("%Y%m%d0000")
    submitted_to = now_l.strftime("%Y%m%d%H%M")
    day = now_l.strftime("%Y-%m-%d")

    WORK_DB.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(WORK_DB))
    ensure_schema(conn)

    results = []
    start = 0
    page_size = 50
    total_seen = 0
    while True:
        total, entries = fetch_new_since(submitted_from, submitted_to, start, page_size)
        if start == 0:
            print(f"daily delta {submitted_from}→{submitted_to} total={total}", flush=True)
        if not entries:
            break
        for ent in entries:
            total_seen += 1
            if dry_run:
                results.append({"arxiv_id": ent["arxiv_id"], "title": ent["title"], "dry_run": True})
                continue
            exists = conn.execute(
                "SELECT 1 FROM fulltext WHERE arxiv_id=? AND ok=1 AND score_valid=1",
                (ent["arxiv_id"],),
            ).fetchone()
            if exists:
                continue
            meta = extract_arxiv(ent["arxiv_id"], sleep=SLEEP)
            text = ""
            if meta.get("ok") and meta.get("abs_path"):
                text = Path(meta["abs_path"]).read_text(encoding="utf-8", errors="replace")
            score = score_fulltext(title=ent["title"], fulltext=text, categories=ent["categories"])
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
            persist_fulltext_score(conn, meta, score, ent, ent.get("primary_category") or "daily", "daily")
            results.append(
                {
                    "arxiv_id": ent["arxiv_id"],
                    "title": ent["title"],
                    "labels": score.get("labels"),
                    "primary": score.get("primary"),
                    "chars": meta.get("chars"),
                    "flags": meta.get("flags"),
                    "rationale": score.get("rationale"),
                }
            )
        start += page_size
        if start >= total:
            break

    conn.close()
    save_daily_cursor({"last_submitted_to": submitted_to, "updated_at": utc_now(), "n_processed": len(results)})

    aid = [r for r in results if any(x in (r.get("labels") or []) for x in ("AID_SPORTS", "AID_POKER", "AID_CRYPTO"))]
    transfer = [r for r in results if "TRANSFER" in (r.get("labels") or [])]
    DOCS.mkdir(parents=True, exist_ok=True)
    report = DOCS / f"arxiv-daily-{day}.md"
    lines = [
        f"# arXiv daily delta — {day}",
        "",
        f"**Window:** `{submitted_from}` → `{submitted_to}` (Europe/London run {now_l.isoformat()})",
        f"**Processed (new fulltext scores):** {len(results)}",
        f"**AID hits:** {len(aid)} · **TRANSFER:** {len(transfer)}",
        "",
        "## AID hits",
        "",
    ]
    if not aid:
        lines.append("_None._")
    else:
        for r in aid:
            lines.append(f"- `{r['arxiv_id']}` **{r.get('primary')}** — {r.get('title')} — {r.get('rationale')}")
    lines += ["", "## TRANSFER", ""]
    if not transfer:
        lines.append("_None._")
    else:
        for r in transfer[:50]:
            lines.append(f"- `{r['arxiv_id']}` — {r.get('title')}")
    lines += ["", "## Extraction QA sample", ""]
    for r in results[:20]:
        lines.append(f"- `{r.get('arxiv_id')}` chars={r.get('chars')} flags={r.get('flags')} label={r.get('primary')}")
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {report}", flush=True)
    return {"day": day, "n": len(results), "aid": len(aid), "report": str(report)}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    print(json.dumps(run(dry_run=args.dry_run), indent=2))


if __name__ == "__main__":
    main()
