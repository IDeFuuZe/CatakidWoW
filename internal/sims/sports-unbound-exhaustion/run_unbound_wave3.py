#!/usr/bin/env python3
"""Sports unbound WAVE 3 — NEW families not in wave 1/2.

£0 / train-frozen WF / no Catakid / no bookie login / beats_book=false.
"""
from __future__ import annotations

import csv
import json
import math
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

STORE = Path("/cursor/stores/bc-28a8dd7c-8662-49a7-9938-a5fa31b1d070")
SIMS = STORE / "internal/sims"
OUT = SIMS / "sports-unbound-exhaustion"
W3 = OUT / "wave3"
FD = Path("/tmp/sports-unbound/w2")
START = 80.0
FLAT = 5.0
JUICE = -110


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def am_to_dec(ml: float) -> float:
    ml = float(ml)
    return 1.0 + ml / 100.0 if ml > 0 else 1.0 + 100.0 / abs(ml)


def dec_to_am(dec: float) -> float:
    return (dec - 1) * 100 if dec >= 2 else -100 / (dec - 1)


def pnl(won: bool, ml: float, stake: float) -> float:
    return stake * (am_to_dec(ml) - 1.0) if won else -stake


def bankroll(bets: List[Dict[str, Any]], stake_fn: Optional[Callable] = None, start: float = START) -> Dict[str, Any]:
    if stake_fn is None:
        stake_fn = lambda b, br: FLAT
    br = start
    peak = start
    max_dd = pl = staked = 0.0
    n = wins = skipped = 0
    bust = False
    for b in bets:
        if br <= 0:
            bust = True
            br = 0.0
            break
        s = stake_fn(b, br)
        if s is None or s <= 0 or s > br:
            skipped += 1
            continue
        d = pnl(bool(b["won"]), float(b["ml"]), s)
        br += d
        pl += d
        staked += s
        n += 1
        wins += int(b["won"])
        peak = max(peak, br)
        max_dd = max(max_dd, peak - br)
        if br <= 0:
            bust = True
            br = 0.0
            break
    return {
        "n": n,
        "wins": wins,
        "win_pct": (wins / n) if n else None,
        "pl": round(pl, 4),
        "staked": round(staked, 4),
        "end": round(br, 4),
        "roi_bank": round((br - start) / start, 6) if start else None,
        "max_dd": round(max_dd, 4),
        "bust": bust,
        "skipped": skipped,
        "clears_draft": (not bust) and br >= 70 and (br - start) >= 0,
    }


def dual_draft(tr: Dict, oo: Dict) -> bool:
    return bool(tr and oo and tr.get("clears_draft") and oo.get("clears_draft") and not tr["bust"] and not oo["bust"])


def dual_ats(tr: Dict, oo: Dict) -> bool:
    def ok(p):
        return p and not p["bust"] and (p.get("win_pct") or 0) >= 0.524 and p["end"] >= 70 and (p.get("roi_bank") or 0) >= 0

    return bool(ok(tr) and ok(oo))


def parse_iso(date: str) -> Optional[str]:
    try:
        dd, mm, yy = date.split("/")
        yyyy = int(yy) if len(yy) == 4 else 2000 + int(yy)
        return f"{yyyy:04d}-{int(mm):02d}-{int(dd):02d}"
    except Exception:
        return None


def load_fd_rows() -> List[Dict[str, Any]]:
    rows = []
    for p in sorted(FD.glob("*.csv")):
        league = p.name.split("_")[0]
        with p.open(newline="", encoding="utf-8", errors="replace") as f:
            for r in csv.DictReader(f):
                iso = parse_iso(r.get("Date") or "")
                if not iso:
                    continue
                try:
                    hg, ag = int(r["FTHG"]), int(r["FTAG"])
                except Exception:
                    continue
                mm = int(iso[5:7])
                yyyy = int(iso[:4])
                season = yyyy  # calendar proxy
                row = {
                    "date": iso,
                    "season": season,
                    "league": league,
                    "hg": hg,
                    "ag": ag,
                    "ftr": r.get("FTR"),
                    "hthg": r.get("HTHG"),
                    "htag": r.get("HTAG"),
                    "htr": r.get("HTR"),
                    "referee": (r.get("Referee") or "").strip(),
                    "time": r.get("Time") or "",
                    "hy": r.get("HY"),
                    "ay": r.get("AY"),
                    "raw": r,
                }
                rows.append(row)
    rows.sort(key=lambda x: (x["date"], x["league"]))
    return rows


def ah_cover(hg: int, ag: int, ahh: float, side: str) -> Optional[bool]:
    """Asian handicap settle. ahh is home line (e.g. -0.5, +1.5).
    side home: home margin + (-ahh wait): standard: home gives ahh when ahh negative.
    Football-Data AHh: home handicap. Home cover if (hg-ag) + AHh > 0; push ==0 for whole balls.
    Half lines never push.
    """
    try:
        line = float(ahh)
    except Exception:
        return None
    margin = (hg - ag) + line  # home perspective after handicap
    if abs(margin) < 1e-9:
        return None  # push — skip
    home_covers = margin > 0
    return home_covers if side == "home" else (not home_covers)


def run_soccer_ah(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    picks_all = []
    for r in rows:
        raw = r["raw"]
        try:
            ahh = float(raw.get("AHh") or "")
            oh = float(raw.get("B365AHH") or raw.get("AvgAHH") or "")
            oa = float(raw.get("B365AHA") or raw.get("AvgAHA") or "")
        except (TypeError, ValueError):
            continue
        if oh <= 1.01 or oa <= 1.01:
            continue
        # model-free: bet home AH when line is plus (home dog on AH) and oh>=1.85
        # and alternate: bet side with higher decimal (longer AH price)
        for side, dec, mode in (
            ("home", oh, "home_plus_only" if ahh > 0 else "home_any"),
            ("away", oa, "away_any"),
        ):
            cov = ah_cover(r["hg"], r["ag"], ahh, side)
            if cov is None:
                continue
            picks_all.append(
                {
                    "date": r["date"],
                    "season": r["season"],
                    "league": r["league"],
                    "side": side,
                    "ahh": ahh,
                    "dec": dec,
                    "won": cov,
                    "ml": dec_to_am(dec),
                    "mode_tag": mode,
                }
            )

    def select(mode: str, min_dec: float):
        out = []
        for p in picks_all:
            if p["dec"] < min_dec:
                continue
            if mode == "home_plus":
                if p["side"] != "home" or p["ahh"] <= 0:
                    continue
            elif mode == "longer_side":
                # keep only if this side is the longer of the two for that match — approximate via tag pass
                pass
            elif mode == "home_any":
                if p["side"] != "home":
                    continue
            elif mode == "away_any":
                if p["side"] != "away":
                    continue
            out.append(p)
        # longer_side: rebuild per match
        if mode == "longer_side":
            by = defaultdict(list)
            for p in picks_all:
                if p["dec"] < min_dec:
                    continue
                by[(p["date"], p["league"])].append(p)
            out = []
            for ps in by.values():
                best = max(ps, key=lambda x: x["dec"])
                out.append(best)
        return sorted(out, key=lambda x: x["date"])

    best = None
    for mode in ("home_plus", "home_any", "away_any", "longer_side"):
        for min_dec in (1.70, 1.85, 2.00):
            picks = select(mode, min_dec)
            train = [p for p in picks if p["season"] <= 2021]
            oos = [p for p in picks if p["season"] >= 2022]
            if len(train) < 40 or len(oos) < 40:
                continue
            tr = bankroll(train)
            score = (tr["end"] if not tr["bust"] else -1e9, tr["win_pct"] or 0)
            cand = {
                "mode": mode,
                "min_dec": min_dec,
                "n_train": len(train),
                "n_oos": len(oos),
                "train": tr,
                "_oos": oos,
                "_score": score,
            }
            if best is None or score > best["_score"]:
                best = cand
    if not best:
        return {"family": "soccer_ah_new", "best": None, "n_ah_quotes": len(picks_all)}
    oo = bankroll(best.pop("_oos"))
    best.pop("_score")
    best["oos"] = oo
    best["clears_dual_draft"] = dual_draft(best["train"], oo)
    return {
        "family": "soccer_ah_new",
        "status_intent": "NEW Asian Handicap bankroll from FD AHh/B365AH",
        "n_ah_quotes": len(picks_all),
        "best": best,
        "beats_book": False,
    }


def run_soccer_ht(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Bet HT result using HT book if present — FD has HTR but not always HT odds.
    Fallback: use FT B365 as proxy ONLY for settle HT with FT prices = misspec — refuse.
    Instead: process win% of HT home vs base rate; bankroll only if BbAH or similar.
    Check for B365CH as FT close — no HT odds in modern FD.
    HARD STOP bankroll if no HT odds; score HT→FT correlation process.
    """
    n = 0
    ht_home = ht_draw = ht_away = 0
    ht_home_wins_ft = 0
    for r in rows:
        htr = r.get("htr")
        if htr not in ("H", "D", "A"):
            continue
        n += 1
        if htr == "H":
            ht_home += 1
            if r.get("ftr") == "H":
                ht_home_wins_ft += 1
        elif htr == "D":
            ht_draw += 1
        else:
            ht_away += 1
    return {
        "family": "soccer_ht_process_new",
        "status_intent": "NEW HT/FT process — no free HT odds in FD ⇒ no bankroll paper",
        "n": n,
        "ht_home_rate": round(ht_home / n, 4) if n else None,
        "ht_draw_rate": round(ht_draw / n, 4) if n else None,
        "p_ft_home_given_ht_home": round(ht_home_wins_ft / ht_home, 4) if ht_home else None,
        "paper_enable_possible": False,
        "reason": "HARD_STOP — Football-Data lacks HT 1X2 odds columns in these CSVs",
        "beats_book": False,
    }


def run_soccer_ref_cards_under(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Referee prior yellow rate → bet under 2.5 when ref historically card-heavy (game slow?).
    Honest: card-heavy may not imply under — still score.
    """
    # need OU prices
    hist_cards = defaultdict(list)
    picks = []
    for r in rows:
        raw = r["raw"]
        ref = r["referee"]
        if not ref:
            continue
        try:
            hy, ay = int(raw.get("HY") or 0), int(raw.get("AY") or 0)
            o_u = float(raw.get("B365<2.5") or raw.get("Avg<2.5") or "")
        except (TypeError, ValueError):
            continue
        if o_u <= 1.01:
            continue
        prior = hist_cards[ref]
        mean_cards = (sum(prior[-30:]) / len(prior[-30:])) if len(prior) >= 15 else None
        hist_cards[ref].append(hy + ay)
        if mean_cards is None:
            continue
        # freeze thresholds on train later
        picks.append(
            {
                "date": r["date"],
                "season": r["season"],
                "mean_cards": mean_cards,
                "won": (r["hg"] + r["ag"]) <= 2,  # under 2.5
                "ml": dec_to_am(o_u),
                "dec": o_u,
            }
        )

    best = None
    for card_min in (3.5, 4.0, 4.5, 5.0):
        for min_dec in (1.70, 1.85):
            sel = [p for p in picks if p["mean_cards"] >= card_min and p["dec"] >= min_dec]
            train = [p for p in sel if p["season"] <= 2021]
            oos = [p for p in sel if p["season"] >= 2022]
            if len(train) < 30 or len(oos) < 30:
                continue
            tr = bankroll(train)
            score = (tr["end"] if not tr["bust"] else -1e9, tr["win_pct"] or 0)
            cand = {
                "card_min": card_min,
                "min_dec": min_dec,
                "n_train": len(train),
                "n_oos": len(oos),
                "train": tr,
                "_oos": oos,
                "_score": score,
            }
            if best is None or score > best["_score"]:
                best = cand
    if not best:
        return {"family": "soccer_ref_cards_under_new", "best": None, "n_candidates": len(picks)}
    oo = bankroll(best.pop("_oos"))
    best.pop("_score")
    best["oos"] = oo
    best["clears_dual_draft"] = dual_draft(best["train"], oo)
    return {
        "family": "soccer_ref_cards_under_new",
        "status_intent": "NEW referee prior yellows → under 2.5",
        "n_candidates": len(picks),
        "best": best,
        "beats_book": False,
    }


def run_soccer_kickoff_buckets(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Evening vs afternoon: bet home at B365H in evening kickoffs only (market structure)."""
    picks = {"early": [], "evening": []}
    for r in rows:
        t = r.get("time") or ""
        if not t or ":" not in t:
            continue
        try:
            hour = int(t.split(":")[0])
            oh = float(r["raw"].get("B365H") or "")
        except (TypeError, ValueError):
            continue
        if oh <= 1.01 or r.get("ftr") not in ("H", "D", "A"):
            continue
        bucket = "evening" if hour >= 18 else "early"
        # home ML
        picks[bucket].append(
            {
                "date": r["date"],
                "season": r["season"],
                "won": r["ftr"] == "H",
                "ml": dec_to_am(oh),
            }
        )
    out = {}
    for b, ps in picks.items():
        train = [p for p in ps if p["season"] <= 2021]
        oos = [p for p in ps if p["season"] >= 2022]
        out[b] = {
            "n_train": len(train),
            "n_oos": len(oos),
            "train": bankroll(train) if len(train) >= 20 else None,
            "oos": bankroll(oos) if len(oos) >= 20 else None,
        }
        if out[b]["train"] and out[b]["oos"]:
            out[b]["clears_dual_draft"] = dual_draft(out[b]["train"], out[b]["oos"])
        else:
            out[b]["clears_dual_draft"] = False
    return {
        "family": "soccer_kickoff_home_new",
        "status_intent": "NEW kickoff-hour home ML buckets",
        "buckets": out,
        "beats_book": False,
    }


def run_fd_max_shop(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    """£0 'line shop' proxy: when MaxH > B365H by enough, bet home at MaxH (best FD tape)."""
    picks = []
    for r in rows:
        raw = r["raw"]
        try:
            b365 = float(raw.get("B365H") or "")
            mx = float(raw.get("MaxH") or "")
        except (TypeError, ValueError):
            continue
        if b365 <= 1.01 or mx <= 1.01 or r.get("ftr") not in ("H", "D", "A"):
            continue
        edge_dec = mx - b365
        picks.append(
            {
                "date": r["date"],
                "season": r["season"],
                "edge_dec": edge_dec,
                "won": r["ftr"] == "H",
                "ml": dec_to_am(mx),
                "mx": mx,
                "b365": b365,
            }
        )
    best = None
    for min_edge in (0.05, 0.10, 0.15, 0.20):
        sel = [p for p in picks if p["edge_dec"] >= min_edge]
        train = [p for p in sel if p["season"] <= 2021]
        oos = [p for p in sel if p["season"] >= 2022]
        if len(train) < 40 or len(oos) < 40:
            continue
        tr = bankroll(train)
        score = (tr["end"] if not tr["bust"] else -1e9, tr["win_pct"] or 0)
        cand = {
            "min_max_minus_b365": min_edge,
            "n_train": len(train),
            "n_oos": len(oos),
            "train": tr,
            "_oos": oos,
            "_score": score,
        }
        if best is None or score > best["_score"]:
            best = cand
    # control: always B365H home
    ctrl_train = [
        {"date": p["date"], "won": p["won"], "ml": dec_to_am(p["b365"])}
        for p in picks
        if p["season"] <= 2021
    ]
    ctrl_oos = [
        {"date": p["date"], "won": p["won"], "ml": dec_to_am(p["b365"])}
        for p in picks
        if p["season"] >= 2022
    ]
    if not best:
        return {"family": "fd_max_shop_new", "best": None}
    oo = bankroll(best.pop("_oos"))
    best.pop("_score")
    best["oos"] = oo
    best["clears_dual_draft"] = dual_draft(best["train"], oo)
    return {
        "family": "fd_max_shop_new",
        "status_intent": "NEW FD MaxH vs B365H shop proxy (still single-tape, not live multi-book)",
        "best": best,
        "control_b365_home": {
            "train": bankroll(ctrl_train[:5000]) if ctrl_train else None,
            "oos": bankroll(ctrl_oos[:5000]) if ctrl_oos else None,
            "note": "capped path length for control smoke",
        },
        "beats_book": False,
        "caveat": "MaxH is archive best — not executable CLV; process/shop hygiene only",
    }


def run_nba_sigma_resid() -> Dict[str, Any]:
    rows = json.loads((SIMS / "big-four-maxout/basketball_nba_ats_maxout_predictions.json").read_text())["rows"]
    rows = [r for r in rows if not r.get("push") and r.get("p_home_cover") is not None and r.get("home_cover") is not None and r.get("sigma") is not None]
    rows.sort(key=lambda r: r["date"])
    train = [r for r in rows if int(r["season"]) <= 2018]
    oos = [r for r in rows if int(r["season"]) >= 2019]
    # terciles from train sigma
    sigs = sorted(float(r["sigma"]) for r in train)
    if len(sigs) < 100:
        return {"family": "nba_sigma_resid_ats_new", "best": None}
    t1, t2 = sigs[len(sigs) // 3], sigs[(2 * len(sigs)) // 3]

    def picks(rs, band: str, edge: float, resid_max: Optional[float]):
        out = []
        for r in rs:
            s = float(r["sigma"])
            if band == "low" and s > t1:
                continue
            if band == "mid" and not (t1 < s <= t2):
                continue
            if band == "high" and s <= t2:
                continue
            if resid_max is not None and abs(float(r.get("resid_hat") or 0)) > resid_max:
                continue
            p = float(r["p_home_cover"])
            if p - 0.5 > edge:
                out.append({"date": r["date"][:10], "won": int(r["home_cover"]) == 1, "ml": JUICE})
            elif (1 - p) - 0.5 > edge:
                out.append({"date": r["date"][:10], "won": int(r["home_cover"]) == 0, "ml": JUICE})
        return out

    best = None
    for band in ("low", "mid", "high", "all"):
        for edge in (0.0, 0.05, 0.08):
            for resid_max in (None, 2.0, 3.0):

                def picks_all(rs, edge=edge, resid_max=resid_max, band=band):
                    out = []
                    for r in rs:
                        s = float(r["sigma"])
                        if band == "low" and s > t1:
                            continue
                        if band == "mid" and not (t1 < s <= t2):
                            continue
                        if band == "high" and s <= t2:
                            continue
                        # band == "all": no sigma filter
                        if resid_max is not None and abs(float(r.get("resid_hat") or 0)) > resid_max:
                            continue
                        p = float(r["p_home_cover"])
                        if p - 0.5 > edge:
                            out.append({"date": r["date"][:10], "won": int(r["home_cover"]) == 1, "ml": JUICE})
                        elif (1 - p) - 0.5 > edge:
                            out.append({"date": r["date"][:10], "won": int(r["home_cover"]) == 0, "ml": JUICE})
                    return out

                tr_p = picks_all(train)
                oo_p = picks_all(oos)
                if len(tr_p) < 60 or len(oo_p) < 60:
                    continue
                tr = bankroll(tr_p)
                score = (tr["end"] if not tr["bust"] else -1e9, tr["win_pct"] or 0)
                cand = {
                    "sigma_band": band,
                    "edge_min": edge,
                    "resid_max": resid_max,
                    "sigma_breaks": [round(t1, 3), round(t2, 3)],
                    "n_train": len(tr_p),
                    "n_oos": len(oo_p),
                    "train": tr,
                    "_oos": oo_p,
                    "_score": score,
                }
                if best is None or score > best["_score"]:
                    best = cand
    if not best:
        return {"family": "nba_sigma_resid_ats_new", "best": None}
    oo = bankroll(best.pop("_oos"))
    best.pop("_score")
    best["oos"] = oo
    best["clears_ats_proxy"] = dual_ats(best["train"], oo)
    return {
        "family": "nba_sigma_resid_ats_new",
        "status_intent": "NEW NBA ATS sigma tercile + residual filter",
        "best": best,
        "beats_book": False,
    }


def run_nba_locked_extras() -> Dict[str, Any]:
    lean = json.loads((SIMS / "nba-clv-probe/locked_oos_joined_lean.json").read_text())
    bets = []
    for b in lean["bets"]:
        if b.get("picked_ml") is None or b.get("won") is None:
            continue
        bets.append(
            {
                "date": b["date"][:10],
                "pick": b["pick"],
                "ml": float(b["picked_ml"]),
                "won": bool(b["won"]),
            }
        )
    bets.sort(key=lambda x: x["date"])
    home = [b for b in bets if b["pick"] == "home"]
    away = [b for b in bets if b["pick"] == "away"]

    # cooling-off: skip next K after L consecutive losses
    def cooled(seq, L=3, K=2):
        out = []
        losses = 0
        skip = 0
        for b in seq:
            if skip > 0:
                skip -= 1
                # still update loss streak from skipped? no — don't observe for streak on skipped
                continue
            out.append(b)
            if b["won"]:
                losses = 0
            else:
                losses += 1
                if losses >= L:
                    skip = K
                    losses = 0
        return out

    cool = cooled(bets)
    return {
        "family": "nba_locked_home_away_cooloff_new",
        "status_intent": "NEW home/away split + loss cool-off on frozen dog set",
        "home_flat5": bankroll(home),
        "away_flat5": bankroll(away),
        "cooloff_3loss_skip2": bankroll(cool),
        "baseline_flat5": bankroll(bets),
        "note": "ops/structure on locked selection — not new method_id",
        "beats_book": False,
    }


def run_greyhound_fade() -> Dict[str, Any]:
    races = json.loads((SIMS / "racing-profitability/greyhound_races.json").read_text())
    races = [r for r in races if not r.get("synthetic") and r.get("fav_sp_dec") and r.get("fav_won") is not None]
    races.sort(key=lambda r: r["date"])
    best = None
    for min_field in (6, 8):
        for max_dec in (2.0, 2.5, 3.0):
            picks = [r for r in races if int(r.get("field") or 0) >= min_field and float(r["fav_sp_dec"]) <= max_dec]
            if len(picks) < 40:
                continue
            mid = picks[len(picks) // 2]["date"]
            train = [r for r in picks if r["date"] <= mid]
            oos = [r for r in picks if r["date"] > mid]
            if len(train) < 20 or len(oos) < 20:
                continue

            def stats(rs):
                n = len(rs)
                fw = sum(1 for r in rs if r["fav_won"])
                impl = sum(1 / float(r["fav_sp_dec"]) for r in rs) / n
                return {"n": n, "fav_win_pct": round(fw / n, 4), "mean_sp_implied": round(impl, 4), "gap": round(fw / n - impl, 4)}

            tr, oo = stats(train), stats(oos)
            score = -tr["gap"]
            cand = {
                "min_field": min_field,
                "max_fav_dec": max_dec,
                "train": tr,
                "oos": oo,
                "fade_signal_train": tr["gap"] < -0.02,
                "fade_holds_oos": oo["gap"] < -0.02,
                "_score": score,
            }
            if best is None or score > best["_score"]:
                best = cand
    if best:
        best.pop("_score")
    return {
        "family": "greyhound_fade_fav_process_new",
        "status_intent": "NEW greyhound short-fav fade process (no place/lay — HARD STOP paper)",
        "best": best,
        "paper_enable_possible": False,
        "beats_book": False,
    }


def run_blocked_notes() -> Dict[str, Any]:
    return {
        "family": "wave3_blocked_census",
        "tennis_data_co_uk": "HTTP 403 this cloud — ATP surface re-split BLOCKED_£0 this pass (prior Platt path remains secondary KEEP/shadow)",
        "cricket_bankroll": "advance-* cal only — no free priced closes for bankroll enable",
        "wnba_closes": "other-sports-maxout closes HARD STOP — skip",
        "ht_odds": "FD no HT 1X2 odds — process only",
    }


def decide_paper(w3: Dict[str, Any]) -> Dict[str, Any]:
    enables, holds = [], []

    def hold(name, reason, block=None):
        holds.append({"name": name, "reason": reason, "block": block})

    ah = w3.get("soccer_ah", {}).get("best")
    if ah and ah.get("clears_dual_draft"):
        # soccer still OFF unless dual-clear flood-style — draft dual alone insufficient per prefs
        hold("soccer_ah", "soccer paper policy OFF — dual draft alone not enable (prefs 1X2/soccer hold)", ah)
    else:
        hold("soccer_ah", "fails dual draft", ah)

    for key, dual_key in (
        ("soccer_ref_cards_under", "clears_dual_draft"),
        ("fd_max_shop", "clears_dual_draft"),
    ):
        best = w3.get(key, {}).get("best")
        if best and best.get(dual_key):
            hold(key, "clears draft dual but soccer/shop caveat — refuse Catakid enable without beats_book", best)
        else:
            hold(key, "fails dual draft", best)

    ko = w3.get("soccer_kickoff_home", {}).get("buckets", {})
    for b, v in ko.items():
        if v.get("clears_dual_draft"):
            hold(f"soccer_kickoff_{b}", "soccer home ML bucket — policy OFF", v)
        else:
            hold(f"soccer_kickoff_{b}", "fails dual", v)

    hold("soccer_ht", "HARD STOP no HT odds", w3.get("soccer_ht"))

    nba_sr = w3.get("nba_sigma_resid", {}).get("best")
    if nba_sr and nba_sr.get("clears_ats_proxy"):
        enables.append({"name": "nba_sigma_resid_ats", "best": nba_sr})
    else:
        hold("nba_sigma_resid_ats", "fails ATS dual", nba_sr)

    hold("nba_locked_cooloff", "ops on frozen selection only", w3.get("nba_locked_extras"))
    hold("greyhound_fade", "HARD STOP no place/lay", w3.get("greyhound_fade"))
    hold("blocked_census", "documented", w3.get("blocked"))

    return {
        "paper_enable": enables,
        "hold": holds,
        "catakid_changes": "none — leave NBA daemon alone",
        "beats_book": False,
    }


def main():
    W3.mkdir(parents=True, exist_ok=True)
    rows = load_fd_rows()
    results: Dict[str, Any] = {
        "protocol": "sports_unbound_exhaustion_wave3",
        "generated_at": utc_now(),
        "constraints": {
            "cost": "£0",
            "synthetic": False,
            "catakid": "untouched",
            "bookie_login_automation": False,
            "oos_peek": False,
            "beats_book_default": False,
        },
        "n_fd_rows": len(rows),
        "soccer_ah": run_soccer_ah(rows),
        "soccer_ht": run_soccer_ht(rows),
        "soccer_ref_cards_under": run_soccer_ref_cards_under(rows),
        "soccer_kickoff_home": run_soccer_kickoff_buckets(rows),
        "fd_max_shop": run_fd_max_shop(rows),
        "nba_sigma_resid": run_nba_sigma_resid(),
        "nba_locked_extras": run_nba_locked_extras(),
        "greyhound_fade": run_greyhound_fade(),
        "blocked": run_blocked_notes(),
    }
    results["paper_decision"] = decide_paper(results)
    (W3 / "result.json").write_text(json.dumps(results, indent=2, default=str))
    idx = {
        "generated_at": results["generated_at"],
        "wave": 3,
        "families_scored": [
            "soccer_ah",
            "soccer_ht_process",
            "soccer_ref_cards_under",
            "soccer_kickoff_home",
            "fd_max_shop",
            "nba_sigma_resid_ats",
            "nba_home_away_cooloff",
            "greyhound_fade_fav_process",
            "blocked_census",
        ],
        "paper_enable_count": len(results["paper_decision"]["paper_enable"]),
        "paper_enable": results["paper_decision"]["paper_enable"],
        "catakid": "untouched",
        "beats_book": False,
        "verdict": "EXHAUST_WAVE3_DONE",
        "result": "wave3/result.json",
    }
    (W3 / "index.json").write_text(json.dumps(idx, indent=2, default=str))
    parent = json.loads((OUT / "index.json").read_text())
    parent["wave3"] = idx
    parent["updated_at"] = results["generated_at"]
    (OUT / "index.json").write_text(json.dumps(parent, indent=2))
    print(json.dumps(idx, indent=2, default=str))


if __name__ == "__main__":
    main()
