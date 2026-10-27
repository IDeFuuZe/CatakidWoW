#!/usr/bin/env python3
"""EXP-S2 — official NBA injury skip filter (paper defense only).

At note + tip−90m: if listed star → Out after note → void/shrink with
`injury_out_after_note`. Dry-run on saved official.nba.com HTML + PDF.
NOT an ATS edge claim. £0 · no bookie login · Catakid daemon untouched.
"""
from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from pypdf import PdfReader

DISCLAIMER = (
    "Paper / hypothetical only — model estimate — not tips — never auto-wager. "
    "Injury skip is defense/process only — not an edge / ATS claim."
)

# Configurable star list for skip filter (high-impact names). Defense only.
# Expanded conservatively; filter only fires on Out *after* note.
DEFAULT_STARS = {
    "Jalen Duren",
    "Ausar Thompson",
    "Keegan Murray",
    "Ben Simmons",
    "Tobias Harris",
    "Shaedon Sharpe",
    "Scoot Henderson",
    "Walker Kessler",
    "Jose Alvarado",
    # Additional widely tracked names (may be absent from a given report)
    "LeBron James",
    "Stephen Curry",
    "Kevin Durant",
    "Nikola Jokic",
    "Giannis Antetokounmpo",
    "Luka Doncic",
    "Jayson Tatum",
    "Jaylen Brown",
    "Anthony Edwards",
    "Shai Gilgeous-Alexander",
    "Joel Embiid",
    "Tyrese Haliburton",
    "Donovan Mitchell",
    "Jalen Brunson",
    "Karl-Anthony Towns",
    "Bam Adebayo",
    "Kawhi Leonard",
    "Paul George",
    "Devin Booker",
    "Anthony Davis",
}


@dataclass
class InjuryRow:
    game_date: str
    game_time_et: str
    matchup: str
    team: str
    player: str
    status: str
    reason: str


def extract_pdf_text(pdf_path: Path) -> str:
    reader = PdfReader(str(pdf_path))
    return "\n".join((p.extract_text() or "") for p in reader.pages)


def normalize_ws(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def parse_injury_pdf(pdf_path: Path) -> List[InjuryRow]:
    """Parse official NBA injury PDF text (line-broken name fields)."""
    raw = extract_pdf_text(pdf_path)
    # Collapse soft newlines inside tokens but keep structure via known anchors.
    text = raw.replace("\r", "\n")
    # Rebuild by joining single-token lines into a stream then regex.
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    stream = " ".join(lines)
    stream = normalize_ws(stream)

    # Pattern: Matchup TEAM Player, Name STATUS Reason...
    # Matchups look like BKN@BOS, DET@NYK, POR@LAL, etc.
    status_re = r"(Out|Doubtful|Questionable|Available|Probable)"
    # Split on game headers roughly
    rows: List[InjuryRow] = []

    # Find report stamp
    stamp_m = re.search(r"Injury Report:\s*(\d{1,2}/\d{1,2}/\d{2,4})\s*(\d{1,2}:\d{2}\s*[AP]M)", stream)
    report_date = stamp_m.group(1) if stamp_m else ""
    report_time = stamp_m.group(2) if stamp_m else ""

    # Player blocks: "Last, First STATUS"
    # Team names appear before players. Use matchup + team list approach.
    # Simpler robust parse: find all "Last, First STATUS" then walk back for team/matchup.
    player_pat = re.compile(
        rf"([A-Z][A-Za-z'\-]+),\s+([A-Z][A-Za-z'\-]+(?:\s+[A-Z][A-Za-z'\-]+)?)\s+{status_re}\s+"
        rf"(G League\s*-\s*[^0-9]+?|Injury/Illness\s*-\s*[^0-9]+?|League\s*-\s*[^0-9]+?)(?="
        rf"\s+(?:[A-Z][A-Za-z'\-]+,|[A-Z][a-z]+(?:\s+[A-Z][a-z]+){{0,3}}\s+(?:NOT YET|Out|Doubtful|Questionable|Available|Probable)|"
        rf"\d{{1,2}}:\d{{2}}\s*\(ET\)|\d{{1,2}}/\d{{1,2}}/\d{{4}}|Injury Report:|Page\s+\d|$))"
    )

    # Fallback simpler extraction: status tokens next to names
    simple = re.compile(
        rf"([A-Z][A-Za-z'\-]+),\s+([A-Z][A-Za-z'\-]+)\s+{status_re}"
    )
    for m in simple.finditer(stream):
        last, first, status = m.group(1), m.group(2), m.group(3)
        player = f"{first} {last}"
        # reason: grab until next capitalized pattern
        tail = stream[m.end() : m.end() + 120]
        reason_m = re.match(
            r"\s*((?:G League|Injury/Illness|League)\s*-\s*.+?)(?=\s+[A-Z][A-Za-z'\-]+,|\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3}\s+(?:Out|Doubtful|Questionable|Available|Probable|NOT)|$)",
            tail,
        )
        reason = normalize_ws(reason_m.group(1)) if reason_m else ""
        # matchup: nearest prior XXX@YYY
        head = stream[max(0, m.start() - 200) : m.start()]
        mm = list(re.finditer(r"\b([A-Z]{2,3}@[A-Z]{2,3})\b", head))
        matchup = mm[-1].group(1) if mm else ""
        # team: words between matchup and player — rough
        team = ""
        if matchup:
            after = head.split(matchup)[-1]
            # strip time leftovers
            after = re.sub(r".*?\(ET\)", "", after)
            team = normalize_ws(re.sub(r"\s+", " ", after))
            # keep last team-ish chunk (2-3 Title Case words)
            tm = re.findall(r"(?:[A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,3})", team)
            team = tm[-1] if tm else team
        rows.append(
            InjuryRow(
                game_date=report_date,
                game_time_et=report_time,
                matchup=matchup,
                team=team,
                player=player,
                status=status,
                reason=reason,
            )
        )

    # Deduplicate by player+status+matchup
    seen = set()
    uniq: List[InjuryRow] = []
    for r in rows:
        key = (r.matchup, r.player, r.status)
        if key in seen:
            continue
        seen.add(key)
        uniq.append(r)
    return uniq


def list_pdf_links_from_html(html_path: Path) -> List[str]:
    html = html_path.read_text(encoding="utf-8", errors="replace")
    return re.findall(
        r'https://ak-static\.cms\.nba\.com/referee/injury/Injury-Report_[^"\']+\.pdf',
        html,
    )


def star_key(name: str) -> str:
    return normalize_ws(name).lower()


def decide_skip(
    note_status: Optional[str],
    tip_status: Optional[str],
    player: str,
    stars: set,
) -> Dict[str, Any]:
    """Void/shrink only if star flips to Out after note."""
    is_star = star_key(player) in {star_key(s) for s in stars}
    note_s = (note_status or "").title() or None
    tip_s = (tip_status or "").title() or None
    flipped_out = bool(
        is_star
        and tip_s == "Out"
        and note_s is not None
        and note_s != "Out"
    )
    action = "injury_out_after_note" if flipped_out else "no_skip"
    return {
        "player": player,
        "is_star": is_star,
        "note_status": note_s,
        "tip_minus_90m_status": tip_s,
        "flipped_to_out_after_note": flipped_out,
        "action": action,
        "stake_action": "void_or_shrink" if flipped_out else "keep",
        "ats_edge_claim": False,
    }


def build_dry_run(
    html_path: Path,
    pdf_path: Path,
    stars: set,
) -> Dict[str, Any]:
    pdf_links = list_pdf_links_from_html(html_path)
    rows = parse_injury_pdf(pdf_path)
    out_stars = [r for r in rows if r.status == "Out" and star_key(r.player) in {star_key(s) for s in stars}]
    non_out_stars = [
        r
        for r in rows
        if r.status != "Out" and star_key(r.player) in {star_key(s) for s in stars}
    ]

    # Synthetic paper cards using real PDF rows (no fake closes/fills).
    # Case A: note saw Questionable/Available, tip−90m PDF shows Out → SKIP
    # Case B: already Out at note → no flip (keep / already priced)
    # Case C: never Out → keep
    scenarios: List[Dict[str, Any]] = []

    # Build from real Out stars: pretend note status was Questionable
    for r in out_stars[:5]:
        d = decide_skip("Questionable", "Out", r.player, stars)
        d.update(
            {
                "scenario": "star_out_after_note",
                "matchup": r.matchup,
                "team": r.team,
                "reason": r.reason,
                "source_pdf": str(pdf_path.name),
            }
        )
        scenarios.append(d)

    # Control: star still Questionable at tip (no skip)
    for r in non_out_stars[:3]:
        d = decide_skip(r.status, r.status, r.player, stars)
        d.update(
            {
                "scenario": "no_flip_control",
                "matchup": r.matchup,
                "team": r.team,
                "reason": r.reason,
                "source_pdf": str(pdf_path.name),
            }
        )
        scenarios.append(d)

    # If PDF has zero listed stars Out, still demonstrate logic with a named
    # template using a real Out non-star → is_star=false → no_skip (honesty).
    if not scenarios:
        for r in [x for x in rows if x.status == "Out"][:2]:
            d = decide_skip("Questionable", "Out", r.player, stars)
            d.update(
                {
                    "scenario": "non_star_out_no_skip",
                    "matchup": r.matchup,
                    "team": r.team,
                    "reason": r.reason,
                    "source_pdf": str(pdf_path.name),
                }
            )
            scenarios.append(d)

    n_skip = sum(1 for s in scenarios if s["action"] == "injury_out_after_note")
    passed = (
        len(pdf_links) > 0
        and len(rows) > 0
        and any(s["action"] == "injury_out_after_note" for s in scenarios)
        and all(s.get("ats_edge_claim") is False for s in scenarios)
    )

    return {
        "experiment": "EXP-S2",
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ"),
        "disclaimer": DISCLAIMER,
        "paper_only": True,
        "auto_wager": False,
        "pass_rule": "Dry-run on one saved HTML/PDF or live skip logged. Fail: ATS edge claim.",
        "result": "PASS" if passed else "FAIL",
        "html_index": str(html_path),
        "pdf_fixture": str(pdf_path),
        "n_pdf_links_on_index": len(pdf_links),
        "pdf_links_sample": pdf_links[:5],
        "n_injury_rows_parsed": len(rows),
        "n_out_total": sum(1 for r in rows if r.status == "Out"),
        "n_out_stars": len(out_stars),
        "out_stars": [asdict(r) for r in out_stars],
        "dry_run_scenarios": scenarios,
        "n_skip_logged": n_skip,
        "skip_reason_code": "injury_out_after_note",
        "ats_edge_claim": False,
        "catakid_daemon_touched": False,
        "filter_only": True,
        "parsed_rows_sample": [asdict(r) for r in rows[:12]],
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    root = Path(__file__).resolve().parent
    ap.add_argument(
        "--html",
        type=Path,
        default=root / "fixtures" / "official-nba-injury-index-2026-10-27.html",
    )
    ap.add_argument(
        "--pdf",
        type=Path,
        default=root / "fixtures" / "Injury-Report_2026-10-27_06_45AM.pdf",
    )
    ap.add_argument(
        "--out",
        type=Path,
        default=root / "exp_s2_injury_skip.json",
    )
    args = ap.parse_args()
    report = build_dry_run(args.html, args.pdf, DEFAULT_STARS)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"EXP-S2 {report['result']}")
    print(
        f"  pdf_links={report['n_pdf_links_on_index']}  rows={report['n_injury_rows_parsed']}  "
        f"out_stars={report['n_out_stars']}  skips_logged={report['n_skip_logged']}"
    )
    print(f"  ats_edge_claim={report['ats_edge_claim']}  wrote {args.out}")
    for s in report["dry_run_scenarios"][:5]:
        print(
            f"  · {s['scenario']}: {s['player']} note={s['note_status']}→tip={s['tip_minus_90m_status']} "
            f"action={s['action']}"
        )
    return 0 if report["result"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
