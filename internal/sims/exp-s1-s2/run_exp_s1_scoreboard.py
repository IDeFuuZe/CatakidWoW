#!/usr/bin/env python3
"""EXP-S1 — paper CLV scoreboard (+ S3 rlm_proxy + S4 note_lag_h).

£0 · paper-only · no bookie login · no CLV selection gate.
Reads ledger.jsonl; scores settled NBA rows when free open+close exist.
Honest empty: fields always printed even if n_with_clv=0.
"""
from __future__ import annotations

import argparse
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

DISCLAIMER = (
    "Paper / hypothetical only — model estimate — not tips — never auto-wager. "
    "No real book placement. Empty slate when no real upcoming fixtures."
)

NBA_METHOD_PREFIXES = ("nba_",)
NBA_SPORTS = {"nba", "basketball_nba"}
NBA_DESKS = {"basketball_nba"}


def parse_ts(s: Optional[str]) -> Optional[datetime]:
    if not s or not isinstance(s, str):
        return None
    t = s.strip()
    if t.endswith("Z"):
        t = t[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(t)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def american_to_decimal(ml: Any) -> Optional[float]:
    try:
        a = float(ml)
    except (TypeError, ValueError):
        return None
    if a == 0:
        return None
    if a > 0:
        return 1.0 + a / 100.0
    return 1.0 + 100.0 / abs(a)


def implied_from_decimal(d: Optional[float]) -> Optional[float]:
    if d is None or d <= 1.0:
        return None
    return 1.0 / d


def two_way_fair(p_pick_raw: float, p_opp_raw: float) -> Optional[float]:
    s = p_pick_raw + p_opp_raw
    if s <= 0:
        return None
    return p_pick_raw / s


def fair_pick_from_decimals(
    pick_dec: Optional[float], opp_dec: Optional[float]
) -> Optional[float]:
    ip = implied_from_decimal(pick_dec)
    io = implied_from_decimal(opp_dec)
    if ip is None or io is None:
        return None
    return two_way_fair(ip, io)


def is_nba_row(row: Dict[str, Any]) -> bool:
    mid = str(row.get("method_id") or "")
    sport = str(row.get("sport") or "").lower()
    desk = str(row.get("desk_key") or "").lower()
    if any(mid.startswith(p) for p in NBA_METHOD_PREFIXES):
        return True
    if sport in NBA_SPORTS or desk in NBA_DESKS:
        return True
    return False


def load_ledger(path: Path) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line:
            continue
        rows.append(json.loads(line))
    return rows


def index_by_bet(rows: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """Latest place/settle/void per bet_id."""
    out: Dict[str, Dict[str, Any]] = {}
    for r in rows:
        bid = r.get("bet_id")
        if not bid:
            continue
        bucket = out.setdefault(bid, {"place": None, "settle": None, "voids": []})
        kind = r.get("kind")
        if kind == "place":
            bucket["place"] = r
        elif kind == "settle":
            bucket["settle"] = r
        elif kind == "void":
            bucket["voids"].append(r)
    return out


def pick_side_decimals(place: Dict[str, Any]) -> Tuple[Optional[float], Optional[float]]:
    pick = str(place.get("pick") or "").lower()
    home_d = place.get("home_back_decimal")
    away_d = place.get("away_back_decimal")
    note_d = place.get("decimal_odds")
    if pick == "home":
        pick_d = note_d if note_d is not None else home_d
        opp_d = away_d
    elif pick == "away":
        pick_d = note_d if note_d is not None else away_d
        opp_d = home_d
    else:
        pick_d = note_d
        opp_d = None
    try:
        pick_d = float(pick_d) if pick_d is not None else None
    except (TypeError, ValueError):
        pick_d = None
    try:
        opp_d = float(opp_d) if opp_d is not None else None
    except (TypeError, ValueError):
        opp_d = None
    return pick_d, opp_d


def close_pick_decimals(
    place: Dict[str, Any], settle: Dict[str, Any]
) -> Tuple[Optional[float], Optional[float]]:
    """Free close when settle/place carry close_* fields; else None (honest empty)."""
    pick = str(place.get("pick") or "").lower()
    # Prefer explicit close fields if ever present on settle/place.
    for src in (settle, place):
        close_pick = src.get("close_decimal") or src.get("close_pick_decimal")
        close_opp = src.get("close_opp_decimal")
        close_home = src.get("close_home_decimal") or src.get("close_home_back_decimal")
        close_away = src.get("close_away_decimal") or src.get("close_away_back_decimal")
        if close_pick is not None:
            try:
                cp = float(close_pick)
            except (TypeError, ValueError):
                cp = None
            try:
                co = float(close_opp) if close_opp is not None else None
            except (TypeError, ValueError):
                co = None
            if cp is not None:
                return cp, co
        if close_home is not None and close_away is not None:
            try:
                ch, ca = float(close_home), float(close_away)
            except (TypeError, ValueError):
                continue
            if pick == "home":
                return ch, ca
            if pick == "away":
                return ca, ch
    # American close ML pair if present
    for src in (settle, place):
        ch_ml = src.get("close_home_ml")
        ca_ml = src.get("close_away_ml")
        if ch_ml is None or ca_ml is None:
            continue
        ch = american_to_decimal(ch_ml)
        ca = american_to_decimal(ca_ml)
        if ch is None or ca is None:
            continue
        if pick == "home":
            return ch, ca
        if pick == "away":
            return ca, ch
    return None, None


def rlm_proxy(open_pick_d: Optional[float], close_pick_d: Optional[float]) -> Optional[str]:
    """Open→close price path on pick side (free proxy; no paid ticket splits)."""
    if open_pick_d is None or close_pick_d is None:
        return None
    if close_pick_d < open_pick_d - 1e-9:
        return "shorten_into_pick"  # market moved toward our side after note
    if close_pick_d > open_pick_d + 1e-9:
        return "drift_against_pick"
    return "flat"


def note_lag_hours(place: Dict[str, Any]) -> Optional[float]:
    """Hours from note timestamp to tip (positive = noted before tip)."""
    note = parse_ts(place.get("captured_at") or place.get("ts"))
    tip = parse_ts(place.get("kickoff"))
    if note is None or tip is None:
        return None
    return (tip - note).total_seconds() / 3600.0


def clv_pp(fair_open: float, fair_close: float) -> float:
    """Standard beat-close: fair_close − fair_open on pick side (pp = *100)."""
    return (fair_close - fair_open) * 100.0


def score_nba(bets: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    settled_rows: List[Dict[str, Any]] = []
    open_nba = 0
    voided = 0
    for bid, bucket in bets.items():
        place = bucket.get("place")
        settle = bucket.get("settle")
        voids = bucket.get("voids") or []
        if not place or not is_nba_row(place):
            # settle-only NBA (method_id on settle)
            if settle and is_nba_row(settle) and voids:
                voided += 1
            continue
        if voids:
            voided += 1
            continue
        if settle is None:
            if place.get("status") in (None, "awaiting_result", "open"):
                open_nba += 1
            continue

        open_pick_d, open_opp_d = pick_side_decimals(place)
        close_pick_d, close_opp_d = close_pick_decimals(place, settle)
        fair_o = fair_pick_from_decimals(open_pick_d, open_opp_d)
        fair_c = fair_pick_from_decimals(close_pick_d, close_opp_d)
        # Also accept settle.clv if already computed by Catakid (fractional fair pts)
        settle_clv = settle.get("clv")
        clv_points = None
        if fair_o is not None and fair_c is not None:
            clv_points = clv_pp(fair_o, fair_c)
        elif settle_clv is not None:
            try:
                # store may already be fair-prob points or fraction; detect
                v = float(settle_clv)
                clv_points = v * 100.0 if abs(v) <= 1.0 else v
            except (TypeError, ValueError):
                clv_points = None

        settled_rows.append(
            {
                "bet_id": bid,
                "method_id": place.get("method_id") or settle.get("method_id"),
                "event_id": place.get("event_id"),
                "pick": place.get("pick"),
                "open_pick_decimal": open_pick_d,
                "close_pick_decimal": close_pick_d,
                "fair_open": fair_o,
                "fair_close": fair_c,
                "clv_pp": clv_points,
                "rlm_proxy": rlm_proxy(open_pick_d, close_pick_d),
                "note_lag_h": note_lag_hours(place),
                "pl": settle.get("pl"),
                "won": settle.get("won"),
                "selection_gate": False,  # EXP-S1 FAIL condition: never gate on CLV
            }
        )

    with_clv = [r for r in settled_rows if r["clv_pp"] is not None]
    n_with_clv = len(with_clv)
    mean_clv_pp = (
        sum(r["clv_pp"] for r in with_clv) / n_with_clv if n_with_clv else None
    )
    pct_plus_clv = (
        100.0 * sum(1 for r in with_clv if r["clv_pp"] > 0) / n_with_clv
        if n_with_clv
        else None
    )

    rlm_counts: Dict[str, int] = {}
    for r in settled_rows:
        k = r["rlm_proxy"] or "missing_close"
        rlm_counts[k] = rlm_counts.get(k, 0) + 1

    lag_vals = [r["note_lag_h"] for r in settled_rows if r["note_lag_h"] is not None]
    mean_note_lag_h = sum(lag_vals) / len(lag_vals) if lag_vals else None

    return {
        "sport_filter": "NBA settled only",
        "n_settled_nba": len(settled_rows),
        "n_open_nba": open_nba,
        "n_voided_nba": voided,
        "n_with_clv": n_with_clv,
        "pct_plus_clv": pct_plus_clv,  # %+CLV
        "mean_CLV_pp": mean_clv_pp,
        "rlm_proxy_counts": rlm_counts,
        "note_lag_h_n": len(lag_vals),
        "note_lag_h_mean": mean_note_lag_h,
        "clv_selection_gate": False,
        "rows": settled_rows,
    }


def build_scoreboard(ledger_path: Path) -> Dict[str, Any]:
    rows = load_ledger(ledger_path)
    bets = index_by_bet(rows)
    nba = score_nba(bets)
    # Sanity: fields must exist even when empty
    required = ["n_with_clv", "pct_plus_clv", "mean_CLV_pp", "rlm_proxy_counts", "note_lag_h_mean"]
    missing = [k for k in required if k not in nba]
    passed = (
        not missing
        and nba["clv_selection_gate"] is False
        and isinstance(nba["n_with_clv"], int)
    )
    return {
        "experiment": "EXP-S1",
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ"),
        "disclaimer": DISCLAIMER,
        "paper_only": True,
        "auto_wager": False,
        "ledger": str(ledger_path),
        "pass_rule": "Scoreboard shows %+CLV, mean_CLV_pp, n_with_clv, rlm_proxy, note_lag_h even if n_with_clv=0. Fail: CLV selection gate.",
        "result": "PASS" if passed else "FAIL",
        "fail_reasons": missing
        + (["clv_selection_gate_true"] if nba["clv_selection_gate"] else []),
        "nba_clv_scoreboard": nba,
        "embeds": {"S3": "rlm_proxy", "S4": "note_lag_h"},
        "catakid_daemon_touched": False,
        "beats_book_claim": False,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--ledger",
        type=Path,
        default=Path(__file__).resolve().parent / "fixtures" / "ledger.jsonl",
    )
    ap.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).resolve().parent / "exp_s1_scoreboard.json",
    )
    args = ap.parse_args()
    sb = build_scoreboard(args.ledger)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(sb, indent=2) + "\n", encoding="utf-8")
    nba = sb["nba_clv_scoreboard"]
    print(f"EXP-S1 {sb['result']}")
    print(
        f"  n_settled_nba={nba['n_settled_nba']}  n_with_clv={nba['n_with_clv']}  "
        f"%+CLV={nba['pct_plus_clv']}  mean_CLV_pp={nba['mean_CLV_pp']}"
    )
    print(f"  rlm_proxy={nba['rlm_proxy_counts']}  note_lag_h_mean={nba['note_lag_h_mean']}")
    print(f"  clv_selection_gate={nba['clv_selection_gate']}  wrote {args.out}")
    return 0 if sb["result"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
