#!/usr/bin/env python3
"""Sports unbound exhaustion sims — NEW families beyond betting-methods-exhaustion DONE map.

£0 / no synthetic / no bookie login / beats_book=false unless proven.
Uses existing locked NBA OOS lean join, big-four ATS/totals prediction dumps, Football-Data EPL CSVs.
"""
from __future__ import annotations

import csv
import json
import math
import os
from collections import defaultdict
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

STORE = Path("/cursor/stores/bc-28a8dd7c-8662-49a7-9938-a5fa31b1d070")
SIMS = STORE / "internal/sims"
OUT = SIMS / "sports-unbound-exhaustion"
RAW = OUT / "raw"
START_BR = 80.0
FLAT = 5.0
JUICE_AMERICAN = -110  # standard ATS/totals price when line-only


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def am_to_dec(ml: float) -> float:
    ml = float(ml)
    if ml > 0:
        return 1.0 + ml / 100.0
    return 1.0 + 100.0 / abs(ml)


def am_to_impl(ml: float) -> float:
    return 1.0 / am_to_dec(ml)


def pnl_flat(won: bool, ml: float, stake: float = FLAT) -> float:
    if won:
        return stake * (am_to_dec(ml) - 1.0)
    return -stake


def bankroll_path(
    bets: List[Dict[str, Any]],
    stake_fn: Callable[[Dict[str, Any], float], float],
    start: float = START_BR,
    stop_loss: Optional[float] = None,
) -> Dict[str, Any]:
    br = start
    peak = start
    max_dd = 0.0
    n = 0
    wins = 0
    staked = 0.0
    pl = 0.0
    bust = False
    games_to_bust = None
    skipped = 0
    for i, b in enumerate(bets):
        if stop_loss is not None and br < stop_loss:
            skipped += 1
            continue
        if br <= 0:
            bust = True
            if games_to_bust is None:
                games_to_bust = i
            break
        stake = stake_fn(b, br)
        if stake is None or stake <= 0 or stake > br:
            skipped += 1
            continue
        won = bool(b["won"])
        delta = pnl_flat(won, b["ml"], stake)
        br += delta
        pl += delta
        staked += stake
        n += 1
        if won:
            wins += 1
        peak = max(peak, br)
        max_dd = max(max_dd, peak - br)
        if br <= 0:
            bust = True
            games_to_bust = n
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
        "games_to_bust": games_to_bust,
        "skipped": skipped,
        "clears_draft": (not bust) and br >= 70.0 and (br - start) >= 0,
    }


def weekday(date_s: str) -> int:
    # YYYY-MM-DD
    y, m, d = map(int, date_s[:10].split("-"))
    return datetime(y, m, d).weekday()  # Mon=0


def load_nba_locked() -> List[Dict[str, Any]]:
    lean = json.loads((SIMS / "nba-clv-probe/locked_oos_joined_lean.json").read_text())
    out = []
    for b in lean["bets"]:
        if b.get("picked_ml") is None or b.get("won") is None or not b.get("date"):
            continue
        row = {
            "date": b["date"][:10],
            "season": int(b["season"]),
            "home": b["home"],
            "away": b["away"],
            "pick": b["pick"],
            "ml": float(b["picked_ml"]),
            "won": bool(b["won"]),
            "clv": b.get("clv_fair_pts"),
            "fair_open": b.get("fair_open"),
            "fair_close": b.get("fair_close"),
            "quality": bool(b.get("quality_side_ok") and b.get("quality_close_agree") and b.get("clv_fair_pts") is not None),
            "joined": bool(b.get("joined")),
        }
        out.append(row)
    out.sort(key=lambda r: (r["date"], r["home"], r["away"]))
    return out


def stake_flat(_b, _br):
    return FLAT


def stake_pct(pct: float):
    def fn(_b, br):
        s = br * pct
        if s < 0.50:
            return None
        return min(s, br * 0.05)  # hard 5% cap hygiene

    return fn


def stake_dd_scaled(base_pct: float = 0.01, floor_pct: float = 0.005):
    """Reduce stake as drawdown from peak grows (new staking family)."""
    state = {"peak": START_BR}

    def fn(_b, br):
        state["peak"] = max(state["peak"], br)
        dd = (state["peak"] - br) / state["peak"] if state["peak"] else 0
        pct = base_pct * max(0.25, 1.0 - 2.0 * dd)  # cut to 25% of base at 37.5%+ DD
        pct = max(floor_pct * 0.5, pct)
        s = br * pct
        return None if s < 0.50 else min(s, br * 0.03)

    return fn


def stake_vol_target(target_hit: float = 0.45, window: int = 20, base: float = FLAT):
    """Scale flat stake by recent hit-rate vs target (market-structure-adjacent staking)."""
    hist: List[int] = []

    def fn(b, br):
        if len(hist) >= 5:
            hr = sum(hist[-window:]) / min(len(hist), window)
            # if cold, shrink; if hot, mild expand — never chase hard
            scale = 0.5 + 0.5 * (hr / target_hit)
            scale = max(0.35, min(1.25, scale))
        else:
            scale = 1.0
        s = base * scale
        s = min(s, br * 0.05)
        # record outcome after sizing using this bet's result (for next)
        hist.append(1 if b["won"] else 0)
        return None if s < 0.50 else s

    return fn


def density_filter(bets: List[Dict[str, Any]], max_per_day: int) -> List[Dict[str, Any]]:
    counts: Dict[str, int] = defaultdict(int)
    out = []
    for b in bets:
        if counts[b["date"]] >= max_per_day:
            continue
        counts[b["date"]] += 1
        out.append(b)
    return out


def run_nba_staking_and_structure(bets: List[Dict[str, Any]]) -> Dict[str, Any]:
    families = {}
    # Baseline cite
    families["flat_5_all"] = {"family": "staking", "note": "baseline locked selection", **bankroll_path(bets, stake_flat)}
    families["pct_1"] = {"family": "staking", **bankroll_path(bets, stake_pct(0.01))}
    families["pct_1_5"] = {"family": "staking", **bankroll_path(bets, stake_pct(0.015))}
    families["dd_scaled_1pct"] = {
        "family": "staking_new",
        "status_intent": "NEW beyond ¼/½/Walters",
        **bankroll_path(bets, stake_dd_scaled(0.01)),
    }
    families["vol_target_flat"] = {
        "family": "staking_new",
        "status_intent": "NEW volatility-target stake",
        **bankroll_path(bets, stake_vol_target()),
    }
    families["flat_5_stop_loss_40"] = {
        "family": "staking_new",
        "status_intent": "NEW hard stop-loss gate BR<40",
        **bankroll_path(bets, stake_flat, stop_loss=40.0),
    }
    # Market structure / calendar
    weekend = [b for b in bets if weekday(b["date"]) >= 4]
    weekday_only = [b for b in bets if weekday(b["date"]) <= 3]
    families["weekend_only_flat5"] = {
        "family": "market_structure_calendar",
        "status_intent": "NEW hard weekend-only selection (not just slice report)",
        "n_candidates": len(weekend),
        **bankroll_path(weekend, stake_flat),
    }
    families["weekday_skip_flat5"] = {
        "family": "market_structure_calendar",
        "n_candidates": len(weekday_only),
        **bankroll_path(weekday_only, stake_flat),
    }
    dens1 = density_filter(bets, 1)
    dens2 = density_filter(bets, 2)
    families["density_max1_flat5"] = {
        "family": "staking_density",
        "status_intent": "NEW max1/night vs locked max2",
        **bankroll_path(dens1, stake_flat),
    }
    families["density_max2_flat5"] = {"family": "staking_density", **bankroll_path(dens2, stake_flat)}
    # Price-structure bands on locked dogs
    mild_dogs = [b for b in bets if 100 <= b["ml"] <= 200]
    long_dogs = [b for b in bets if b["ml"] > 200]
    families["mild_dog_plus100_200_flat5"] = {
        "family": "market_structure_price",
        "status_intent": "NEW price-band within locked dogs",
        "n_candidates": len(mild_dogs),
        **bankroll_path(mild_dogs, stake_flat),
    }
    families["long_dog_gt200_flat5"] = {
        "family": "market_structure_price",
        "n_candidates": len(long_dogs),
        **bankroll_path(long_dogs, stake_flat),
    }
    # Juice/overround proxy via |fair_close - 0.5| distance when quality join exists
    return families


def run_nba_clv_gates(bets: List[Dict[str, Any]]) -> Dict[str, Any]:
    q = [b for b in bets if b["quality"]]
    # Lean stores playbook sign (fair_open - fair_close). Standard beat-close = fair_close - fair_open.
    for b in q:
        b["clv_std"] = -float(b["clv"]) if b["clv"] is not None else None
    # Walk-forward: train seasons 2020-2021 decide bands; OOS 2022-2023 apply
    train = [b for b in q if b["season"] in (2020, 2021)]
    oos = [b for b in q if b["season"] in (2022, 2023)]
    out: Dict[str, Any] = {
        "n_quality": len(q),
        "n_train": len(train),
        "n_oos": len(oos),
        "sign_note": "gates use standard CLV = fair_close - fair_open (+ = beat close)",
        "mean_clv_std_all": round(sum(b["clv_std"] for b in q) / len(q), 6) if q else None,
        "pct_plus_clv_std_all": round(sum(1 for b in q if b["clv_std"] > 0) / len(q), 4) if q else None,
    }
    # Gate A: only bet if this game's open→close would be +CLV — LOOKAHEAD (document as invalid selection)
    plus = [b for b in oos if b["clv_std"] > 0]
    out["lookahead_plus_clv_only_INVALID"] = {
        "family": "clv",
        "status": "NEVER_as_selection",
        "note": "Uses same-game close — lookahead. Scored only to show temptation bias.",
        "n": len(plus),
        **bankroll_path(plus, stake_flat),
    }
    # Gate B: historical mean CLV by price band on train; keep bands with mean std-CLV>0 on train
    def band(ml: float) -> str:
        if ml <= 130:
            return "100_130"
        if ml <= 180:
            return "131_180"
        if ml <= 250:
            return "181_250"
        return "251_plus"

    train_bands: Dict[str, List[float]] = defaultdict(list)
    for b in train:
        train_bands[band(b["ml"])].append(b["clv_std"])
    keep_bands = {k for k, vs in train_bands.items() if vs and (sum(vs) / len(vs)) > 0}
    out["train_band_mean_clv_std"] = {k: round(sum(v) / len(v), 6) for k, v in train_bands.items()}
    out["keep_bands_train_plus"] = sorted(keep_bands)
    filtered = [b for b in oos if band(b["ml"]) in keep_bands]
    out["clv_band_gate_wf"] = {
        "family": "clv_new",
        "status_intent": "NEW CLV-as-selection via train band means (was OUT_OF_SCOPE)",
        "n_oos_kept": len(filtered),
        "note": "empty keep_bands → no bets (honest shutoff when all bands −CLV on train)",
        **(bankroll_path(filtered, stake_flat) if filtered else {"n": 0, "end": START_BR, "bust": False, "clears_draft": False, "pl": 0, "win_pct": None, "max_dd": 0, "skipped": 0, "wins": 0, "staked": 0, "roi_bank": 0}),
    }
    # Gate C: only continue method if rolling prior-20 mean std-CLV > 0 (causal)
    kept = []
    hist = []
    for b in q:
        if len(hist) >= 20 and (sum(hist[-20:]) / 20.0) <= 0:
            hist.append(b["clv_std"])
            continue
        if len(hist) >= 20:
            kept.append(b)
        hist.append(b["clv_std"])
    out["rolling_prior20_clv_gate"] = {
        "family": "clv_new",
        "status_intent": "NEW causal rolling +CLV process gate",
        "n_kept": len(kept),
        **(bankroll_path(kept, stake_flat) if kept else {"n": 0, "end": START_BR, "bust": False, "clears_draft": False, "pl": 0, "win_pct": None, "max_dd": 0, "skipped": 0, "wins": 0, "staked": 0, "roi_bank": 0}),
    }
    out["process_score"] = {
        "beats_book": False,
        "reason": "mean std-CLV negative (~−5.8pp); 12.8% +CLV — gates shut off or fail; no beats_book flip",
    }
    return out


def ats_stake_pnl(cover: int, push: bool, stake: float = FLAT) -> float:
    if push:
        return 0.0
    if cover:
        return stake * (am_to_dec(JUICE_AMERICAN) - 1.0)
    return -stake


def run_ats_totals() -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    # NFL totals — NEW family beyond ML exhaustion
    tot = json.loads((SIMS / "big-four-maxout/americanfootball_nfl_totals_predictions.json").read_text())["rows"]
    tot = [r for r in tot if r.get("total_line") is not None and r.get("p_over") is not None and not r.get("push")]
    tot.sort(key=lambda r: r["date"])

    def totals_select(rows, edge_min: float, side: str = "over"):
        picks = []
        for r in rows:
            p = float(r["p_over"])
            fair = 0.5  # -110 two-way approx fair each side after de-vig ~0.5
            if side == "over":
                edge = p - fair
                won = int(r["over_cover"]) == 1
                if edge > edge_min:
                    picks.append({"date": r["date"][:10], "season": r["season"], "won": won, "ml": JUICE_AMERICAN, "edge": edge})
            else:
                edge = (1.0 - p) - fair
                won = int(r["over_cover"]) == 0
                if edge > edge_min:
                    picks.append({"date": r["date"][:10], "season": r["season"], "won": won, "ml": JUICE_AMERICAN, "edge": edge})
        return picks

    # Train ≤2018 / OOS ≥2019 freeze edge on train cover
    def wf_totals(edge_grid):
        """Freeze side+edge on TRAIN bankroll only; score OOS once (no OOS peek)."""
        best = None
        for e in edge_grid:
            for side in ("over", "under", "both"):
                if side == "both":
                    train = totals_select([r for r in tot if r["season"] <= 2018], e, "over") + totals_select(
                        [r for r in tot if r["season"] <= 2018], e, "under"
                    )
                    oos = totals_select([r for r in tot if r["season"] >= 2019], e, "over") + totals_select(
                        [r for r in tot if r["season"] >= 2019], e, "under"
                    )
                    train = sorted(train, key=lambda x: x["date"])
                    oos = sorted(oos, key=lambda x: x["date"])
                else:
                    train = totals_select([r for r in tot if r["season"] <= 2018], e, side)
                    oos = totals_select([r for r in tot if r["season"] >= 2019], e, side)
                if len(train) < 50 or len(oos) < 50:
                    continue
                tr = bankroll_path(train, stake_flat)
                # Train selection score only
                score = (
                    (tr["end"] if not tr["bust"] else -1e9),
                    tr["win_pct"] or 0,
                    -tr["max_dd"],
                )
                cand = {
                    "edge_min": e,
                    "side": side,
                    "train": tr,
                    "n_train": len(train),
                    "n_oos": len(oos),
                    "_oos_rows": oos,
                    "_score": score,
                }
                if best is None or score > best["_score"]:
                    best = cand
        if not best:
            return None
        oo = bankroll_path(best.pop("_oos_rows"), stake_flat)
        best.pop("_score", None)
        best["oos"] = oo
        best["clears_ats_proxy"] = (
            (best["train"]["win_pct"] or 0) >= 0.524
            and (oo["win_pct"] or 0) >= 0.524
            and not best["train"]["bust"]
            and not oo["bust"]
            and best["train"]["end"] >= 70
            and oo["end"] >= 70
            and best["train"]["roi_bank"] >= 0
            and oo["roi_bank"] >= 0
        )
        return best

    out["nfl_totals"] = {
        "family": "totals_new",
        "status_intent": "NEW — prior map PARTIAL/OUT_OF_SCOPE totals",
        "n_rows": len(tot),
        "baseline_over_all_flat": bankroll_path(
            [
                {
                    "date": r["date"][:10],
                    "won": int(r["over_cover"]) == 1,
                    "ml": JUICE_AMERICAN,
                }
                for r in tot
                if r["season"] >= 2019
            ],
            stake_flat,
        ),
        "wf_best": wf_totals([0.0, 0.02, 0.03, 0.05, 0.08, 0.10]),
    }

    # NFL ATS injury / personnel filters — NEW use as ML-style bankroll selection (prior KILL as ridge)
    ats = json.loads((SIMS / "big-four-maxout/americanfootball_nfl_ats_maxout_predictions.json").read_text())["rows"]
    ats = [r for r in ats if r.get("home_spread") is not None and r.get("p_home_cover") is not None and not r.get("push")]
    ats.sort(key=lambda r: r["date"])

    def ats_picks(rows, edge_min, injury_only=False, injury_exclude=False):
        picks = []
        for r in rows:
            if injury_only and float(r.get("injury_filter") or 0) == 0:
                continue
            if injury_exclude and float(r.get("injury_filter") or 0) != 0:
                continue
            p = float(r["p_home_cover"])
            # bet home if edge, else away
            if p - 0.5 > edge_min:
                picks.append(
                    {
                        "date": r["date"][:10],
                        "season": r["season"],
                        "won": int(r["home_cover"]) == 1,
                        "ml": JUICE_AMERICAN,
                    }
                )
            elif (1 - p) - 0.5 > edge_min:
                picks.append(
                    {
                        "date": r["date"][:10],
                        "season": r["season"],
                        "won": int(r["home_cover"]) == 0,
                        "ml": JUICE_AMERICAN,
                    }
                )
        return picks

    def wf_ats(label, injury_only=False, injury_exclude=False):
        best = None
        for e in [0.0, 0.02, 0.03, 0.05, 0.08]:
            train = ats_picks([r for r in ats if r["season"] <= 2018], e, injury_only, injury_exclude)
            oos = ats_picks([r for r in ats if r["season"] >= 2019], e, injury_only, injury_exclude)
            if len(train) < 40 or len(oos) < 40:
                continue
            tr = bankroll_path(train, stake_flat)
            score = ((tr["end"] if not tr["bust"] else -1e9), tr["win_pct"] or 0, -tr["max_dd"])
            cand = {
                "edge_min": e,
                "n_train": len(train),
                "n_oos": len(oos),
                "train": tr,
                "_oos_rows": oos,
                "_score": score,
            }
            if best is None or score > best["_score"]:
                best = cand
        if not best:
            return {"label": label, "best": None}
        oo = bankroll_path(best.pop("_oos_rows"), stake_flat)
        best.pop("_score", None)
        best["oos"] = oo
        best["clears_ats_proxy"] = (
            (best["train"]["win_pct"] or 0) >= 0.524
            and (oo["win_pct"] or 0) >= 0.524
            and not best["train"]["bust"]
            and not oo["bust"]
            and best["train"]["end"] >= 70
            and oo["end"] >= 70
            and best["train"]["roi_bank"] >= 0
            and oo["roi_bank"] >= 0
        )
        return {"label": label, "best": best}

    out["nfl_ats_injury_families"] = {
        "family": "injuries_free_new",
        "status_intent": "NEW — free injury filter as bankroll selection (prior ATS ridge KILL)",
        "all": wf_ats("all"),
        "injury_flag_only": wf_ats("injury_flag_only", injury_only=True),
        "exclude_injury_flag": wf_ats("exclude_injury_flag", injury_exclude=True),
    }

    # NBA ATS ensemble: blend pred_margin with market -home_spread (shrink-to-market)
    nba = json.loads((SIMS / "big-four-maxout/basketball_nba_ats_maxout_predictions.json").read_text())["rows"]
    nba = [r for r in nba if r.get("home_spread") is not None and r.get("pred_margin") is not None and not r.get("push") and r.get("home_cover") is not None]
    nba.sort(key=lambda r: r["date"])

    def nba_ensemble_picks(rows, w_model: float, edge_min: float):
        picks = []
        for r in rows:
            # market implied margin ≈ -home_spread
            mkt = -float(r["home_spread"])
            ens = w_model * float(r["pred_margin"]) + (1 - w_model) * mkt
            # convert ensemble margin edge vs line
            # cover home if ens > -spread (home expected margin beats spread)
            edge_pts = ens - mkt  # >0 means model-ish more bullish home than market
            # use p_home_cover when w=1 else logistic on edge_pts
            if w_model >= 0.999:
                p = float(r["p_home_cover"])
            else:
                p = 1.0 / (1.0 + math.exp(-edge_pts / 4.0))
            if p - 0.5 > edge_min:
                picks.append({"date": r["date"][:10], "season": int(r["season"]), "won": int(r["home_cover"]) == 1, "ml": JUICE_AMERICAN})
            elif (1 - p) - 0.5 > edge_min:
                picks.append({"date": r["date"][:10], "season": int(r["season"]), "won": int(r["home_cover"]) == 0, "ml": JUICE_AMERICAN})
        return picks

    best_ens = None
    for w in [1.0, 0.7, 0.5, 0.3]:
        for e in [0.0, 0.02, 0.05, 0.08]:
            train = nba_ensemble_picks([r for r in nba if int(r["season"]) <= 2018], w, e)
            oos = nba_ensemble_picks([r for r in nba if int(r["season"]) >= 2019], w, e)
            if len(train) < 80 or len(oos) < 80:
                continue
            tr = bankroll_path(train, stake_flat)
            score = ((tr["end"] if not tr["bust"] else -1e9), tr["win_pct"] or 0, -tr["max_dd"])
            cand = {
                "w_model": w,
                "edge_min": e,
                "n_train": len(train),
                "n_oos": len(oos),
                "train": tr,
                "_oos_rows": oos,
                "_score": score,
            }
            if best_ens is None or score > best_ens["_score"]:
                best_ens = cand
    if best_ens:
        oo = bankroll_path(best_ens.pop("_oos_rows"), stake_flat)
        best_ens.pop("_score", None)
        best_ens["oos"] = oo
        best_ens["clears_ats_proxy"] = (
            (best_ens["train"]["win_pct"] or 0) >= 0.524
            and (oo["win_pct"] or 0) >= 0.524
            and not best_ens["train"]["bust"]
            and not oo["bust"]
            and best_ens["train"]["end"] >= 70
            and oo["end"] >= 70
            and best_ens["train"]["roi_bank"] >= 0
            and oo["roi_bank"] >= 0
        )
    out["nba_ats_shrink_ensemble"] = {
        "family": "ensemble_new",
        "status_intent": "NEW shrink-to-market ensemble on free ATS rows",
        "best": best_ens,
        "n_rows": len(nba),
    }
    return out


def fair_three(h, d, a):
    ih, id_, ia = 1 / float(h), 1 / float(d), 1 / float(a)
    s = ih + id_ + ia
    return ih / s, id_ / s, ia / s


def run_soccer_clv(fd_dir: Path) -> Dict[str, Any]:
    rows = []
    for p in sorted(fd_dir.glob("E0_*.csv")):
        with p.open(newline="", encoding="utf-8", errors="replace") as f:
            rdr = csv.DictReader(f)
            for r in rdr:
                try:
                    oh, od, oa = float(r["B365H"]), float(r["B365D"]), float(r["B365A"])
                    ch, cd, ca = float(r["B365CH"]), float(r["B365CD"]), float(r["B365CA"])
                except (KeyError, ValueError, TypeError):
                    continue
                ftr = r.get("FTR")
                if ftr not in ("H", "D", "A"):
                    continue
                fo = fair_three(oh, od, oa)
                fc = fair_three(ch, cd, ca)
                # CLV if bet open on eventual winner side
                side = {"H": 0, "D": 1, "A": 2}[ftr]
                clv = fo[side] - fc[side]  # + = open better than close on winning side (process on winner — biased)
                # better: CLV on each side independently for selection research — use home side open vs close
                clv_home = fo[0] - fc[0]
                clv_draw = fo[1] - fc[1]
                clv_away = fo[2] - fc[2]
                date = r.get("Date") or ""
                # DD/MM/YYYY
                try:
                    dd, mm, yy = date.split("/")
                    yyyy = int(yy) if len(yy) == 4 else (2000 + int(yy))
                    iso = f"{yyyy:04d}-{int(mm):02d}-{int(dd):02d}"
                except Exception:
                    continue
                season = yyyy if int(mm) >= 7 else yyyy  # rough
                rows.append(
                    {
                        "date": iso,
                        "season": season,
                        "ftr": ftr,
                        "clv_home": clv_home,
                        "clv_away": clv_away,
                        "clv_draw": clv_draw,
                        "oh": oh,
                        "oa": oa,
                        "od": od,
                        "ch": ch,
                        "ca": ca,
                        "cd": cd,
                        "winner_clv_open_side": clv,
                    }
                )
    rows.sort(key=lambda x: x["date"])
    # Process: mean |open-close| fair move; % home +CLV
    if not rows:
        return {"status": "HARD_STOP", "reason": "no FD rows parsed"}
    mean_home_clv = sum(r["clv_home"] for r in rows) / len(rows)
    pct_home_plus = sum(1 for r in rows if r["clv_home"] > 0) / len(rows)
    # Selection fantasy: bet home at open when Avg-like B365 home is dog and home CLV historically... 
    # Honest: bet home open only when open home decimal > close (lookahead INVALID) vs causal skip
    # Causal: use rolling mean home CLV of prior 50; if prior mean <0, fade home opens (bet away when away open longer)
    picks = []
    hist = []
    for r in rows:
        prior = (sum(hist[-50:]) / len(hist[-50:])) if len(hist) >= 50 else None
        hist.append(r["clv_home"])
        if prior is None:
            continue
        # If market has been offering -CLV on home (home shortening), prefer away dogs at open when oa>oh
        if prior < 0 and r["oa"] > r["oh"]:
            won = r["ftr"] == "A"
            # settle at open away price
            ml_approx = (r["oa"] - 1) * 100 if r["oa"] >= 2 else -100 / (r["oa"] - 1)
            picks.append({"date": r["date"], "won": won, "ml": ml_approx})
    path = bankroll_path(picks, stake_flat) if picks else None
    return {
        "family": "clv_soccer_new",
        "status_intent": "NEW — FD open/close CLV (was OUT_OF_SCOPE Dec1)",
        "n": len(rows),
        "mean_home_clv_fair": round(mean_home_clv, 6),
        "pct_home_plus_clv": round(pct_home_plus, 4),
        "beats_book": False,
        "causal_fade_home_shortening_away_dog": {
            "n": len(picks),
            "path": path,
            "clears_flood_proxy": bool(path and path["clears_draft"] and (path["win_pct"] or 0) > 0.4),
        },
        "note": "Soccer paper remains OFF unless dual-clear; this is process/exhaustion only.",
    }


def other_sports_census() -> Dict[str, Any]:
    mx = SIMS / "other-sports-maxout"
    census = {}
    for p in sorted(mx.glob("*.json")):
        if p.name.startswith("index"):
            continue
        try:
            d = json.loads(p.read_text())
        except Exception as e:
            census[p.stem] = {"status": "READ_FAIL", "error": str(e)}
            continue
        status = d.get("status") or d.get("verdict") or d.get("hard_stop") or d.get("action")
        census[p.stem] = {
            "status": status,
            "beats_book": d.get("beats_book", False),
            "keys": list(d.keys())[:12],
        }
    hard = json.loads((mx / "college_hard_stops.json").read_text()) if (mx / "college_hard_stops.json").exists() else {}
    return {"family": "other_sports", "maxout_census": census, "college_hard_stops": hard}


def calibration_temperature_proxy() -> Dict[str, Any]:
    """Temperature scaling needs per-bet p_cal — not in store dumps.

    Score NBA ATS p_home_cover reliability + try temperature on ATS probabilities (honest free data).
    """
    nba = json.loads((SIMS / "big-four-maxout/basketball_nba_ats_maxout_predictions.json").read_text())["rows"]
    nba = [r for r in nba if r.get("p_home_cover") is not None and r.get("home_cover") is not None and not r.get("push")]
    train = [r for r in nba if int(r["season"]) <= 2018]
    oos = [r for r in nba if int(r["season"]) >= 2019]

    def brier(rows, T: float):
        s = 0.0
        n = 0
        for r in rows:
            p = float(r["p_home_cover"])
            # temperature on logit
            p = min(max(p, 1e-6), 1 - 1e-6)
            logit = math.log(p / (1 - p)) / T
            pt = 1 / (1 + math.exp(-logit))
            y = float(r["home_cover"])
            s += (pt - y) ** 2
            n += 1
        return s / n if n else None

    grid = {}
    for T in [0.7, 0.85, 1.0, 1.15, 1.3, 1.5]:
        grid[str(T)] = {"train_brier": brier(train, T), "oos_brier": brier(oos, T)}
    best_T = min(grid.keys(), key=lambda k: grid[k]["train_brier"] or 9)
    # Apply best train T as selection sharpness: bet when tempered |p-0.5| large
    T = float(best_T)
    picks = []
    for r in oos:
        p = float(r["p_home_cover"])
        p = min(max(p, 1e-6), 1 - 1e-6)
        logit = math.log(p / (1 - p)) / T
        pt = 1 / (1 + math.exp(-logit))
        if pt - 0.5 > 0.05:
            picks.append({"date": r["date"][:10], "won": int(r["home_cover"]) == 1, "ml": JUICE_AMERICAN})
        elif (1 - pt) - 0.5 > 0.05:
            picks.append({"date": r["date"][:10], "won": int(r["home_cover"]) == 0, "ml": JUICE_AMERICAN})
    path = bankroll_path(picks, stake_flat)
    return {
        "family": "calibration_new",
        "status_intent": "NEW temperature scaling (was OUT_OF_SCOPE) on NBA ATS p_cover — ML p_cal dump absent",
        "ml_p_cal_dump": "ABSENT — ⅛-Kelly/Platt-on-NBA locked ML not re-scored here (refuse synthetic p)",
        "ats_temperature_grid": grid,
        "chosen_T_train": T,
        "oos_edge5_path": path,
        "clears_ats_proxy": bool(path["clears_draft"] and (path["win_pct"] or 0) >= 0.524),
    }


def decide_paper(results: Dict[str, Any]) -> Dict[str, Any]:
    """Strict paper gate for NEW families only.

    - Do not 'enable' re-scores of already-live NBA dog+isotonic (already paper).
    - ATS/totals require dual-clear (train+OOS) via clears_ats_proxy.
    - CLV / soccer stay off unless +CLV process AND dual-clear (not met).
    - New NBA staking/calendar ops: recommend only if improves maxDD vs flat without
      wrecking end — still ops note, not new method_id (selection frozen).
    """
    enables = []
    holds = []
    ops_notes = []

    nba = results.get("nba_staking_structure", {})
    base = nba.get("flat_5_all") or {}
    # Ops-only candidates on frozen selection
    for k in ("dd_scaled_1pct", "weekend_only_flat5", "density_max1_flat5", "vol_target_flat", "flat_5_stop_loss_40"):
        v = nba.get(k)
        if not v:
            continue
        better_dd = (v.get("max_dd") or 9e9) < (base.get("max_dd") or 0) and not v.get("bust") and (v.get("end") or 0) >= 70
        if better_dd and k in ("dd_scaled_1pct", "density_max1_flat5", "weekend_only_flat5"):
            ops_notes.append(
                {
                    "name": f"nba_ops::{k}",
                    "action": "OPS_NOTE_ONLY",
                    "reason": "Improves DD or end on frozen selection — not a new method_id; Catakid already nba_only+¼-Kelly≤2/night",
                    "path": v,
                }
            )
        else:
            holds.append({"name": f"nba_ops::{k}", "reason": "no material ops lift vs flat or already covered", "path": v})

    clv = results.get("nba_clv", {})
    for k in ("clv_band_gate_wf", "rolling_prior20_clv_gate"):
        if k in clv:
            holds.append({"name": f"nba_clv::{k}", "reason": "mean CLV negative / no beats_book flip", "path": clv[k]})

    def consider_ats(name, block):
        if not block:
            holds.append({"name": name, "reason": "no block"})
            return
        if block.get("clears_ats_proxy"):
            enables.append({"name": name, "block": block})
        else:
            holds.append({"name": name, "reason": "fails dual-clear ATS proxy", "block": block})

    nt = results.get("ats_totals", {}).get("nfl_totals", {})
    consider_ats("nfl_totals::wf_best", nt.get("wf_best"))
    for label, block in (results.get("ats_totals", {}).get("nfl_ats_injury_families") or {}).items():
        if label in ("family", "status_intent"):
            continue
        if isinstance(block, dict):
            consider_ats(f"nfl_ats::{label}", block.get("best"))
    consider_ats("nba_ats::shrink_ensemble", results.get("ats_totals", {}).get("nba_ats_shrink_ensemble", {}).get("best"))

    cal = results.get("calibration", {})
    if cal.get("oos_edge5_path"):
        holds.append(
            {
                "name": "nba_ats::temperature",
                "reason": "T fit train-only but ATS paper bar historically not cleared; OOS path alone insufficient without train dual-clear",
                "path": cal["oos_edge5_path"],
                "clears_flag": cal.get("clears_ats_proxy"),
            }
        )
    soc = results.get("soccer_clv", {}).get("causal_fade_home_shortening_away_dog", {})
    holds.append({"name": "soccer_clv::fade", "reason": "soccer paper OFF; dual-clear 0 history; process only", "path": soc.get("path")})

    return {
        "paper_enable": enables,
        "ops_notes": ops_notes,
        "hold": holds,
        "catakid_changes": "none" if not enables else "review enables — still require Bartosz yes",
        "beats_book": False,
        "note": "Already-live nba_dog_conf_edge_8pct_isotonic unchanged. NEW enables only if dual-clear ATS/totals.",
    }


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    RAW.mkdir(parents=True, exist_ok=True)
    nba = load_nba_locked()
    results = {
        "protocol": "sports_unbound_exhaustion",
        "generated_at": utc_now(),
        "constraints": {
            "cost": "£0",
            "synthetic": False,
            "bookie_login_automation": False,
            "beats_book_default": False,
            "cloud_only": True,
            "prior_map": "docs/betting-methods-exhaustion.md",
        },
        "nba_locked_n": len(nba),
        "nba_staking_structure": run_nba_staking_and_structure(nba),
        "nba_clv": run_nba_clv_gates(nba),
        "ats_totals": run_ats_totals(),
        "calibration": calibration_temperature_proxy(),
        "soccer_clv": run_soccer_clv(Path("/tmp/sports-unbound")),
        "other_sports": other_sports_census(),
    }
    results["paper_decision"] = decide_paper(results)

    # Copy FD samples meta
    meta = {"files": [], "fetched_at": utc_now()}
    for p in sorted(Path("/tmp/sports-unbound").glob("E0_*.csv")):
        meta["files"].append({"name": p.name, "bytes": p.stat().st_size, "lines": sum(1 for _ in p.open())})
        # keep tiny head sample only
        (RAW / p.name).write_text("\n".join(p.read_text(encoding="utf-8", errors="replace").splitlines()[:5]))
    (RAW / "football_data_meta.json").write_text(json.dumps(meta, indent=2))

    (OUT / "result.json").write_text(json.dumps(results, indent=2, default=str))
    # Compact index
    index = {
        "generated_at": results["generated_at"],
        "nba_locked_n": results["nba_locked_n"],
        "families_scored": [
            "staking_new",
            "market_structure",
            "clv_gates",
            "calibration_temperature_ats",
            "ensemble_shrink_ats",
            "injuries_free_ats",
            "totals_nfl",
            "soccer_fd_clv",
            "other_sports_census",
        ],
        "paper_enable_count": len(results["paper_decision"]["paper_enable"]),
        "paper_enable": results["paper_decision"]["paper_enable"],
        "catakid": "untouched",
        "beats_book": False,
        "result": "result.json",
    }
    (OUT / "index.json").write_text(json.dumps(index, indent=2, default=str))
    print(json.dumps(index, indent=2, default=str))


if __name__ == "__main__":
    main()
