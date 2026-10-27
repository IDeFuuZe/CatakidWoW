#!/usr/bin/env python3
"""Sports unbound WAVE 2 — NEW families not scored in wave 1.

£0 / no synthetic / no Catakid / no bookie login / train-frozen WF / beats_book=false.
"""
from __future__ import annotations

import csv
import json
import math
import random
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

STORE = Path("/cursor/stores/bc-28a8dd7c-8662-49a7-9938-a5fa31b1d070")
SIMS = STORE / "internal/sims"
OUT = SIMS / "sports-unbound-exhaustion"
W2 = OUT / "wave2"
START_BR = 80.0
FLAT = 5.0
JUICE = -110


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def am_to_dec(ml: float) -> float:
    ml = float(ml)
    return 1.0 + ml / 100.0 if ml > 0 else 1.0 + 100.0 / abs(ml)


def pnl(won: bool, ml: float, stake: float) -> float:
    return stake * (am_to_dec(ml) - 1.0) if won else -stake


def bankroll(
    bets: List[Dict[str, Any]],
    stake_fn: Optional[Callable] = None,
    start: float = START_BR,
) -> Dict[str, Any]:
    if stake_fn is None:
        stake_fn = lambda b, br: FLAT
    br = start
    peak = start
    max_dd = 0.0
    n = wins = 0
    staked = pl = 0.0
    bust = False
    skipped = 0
    for b in bets:
        if br <= 0:
            bust = True
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


def dual_ats(train_path: Dict, oos_path: Dict) -> bool:
    def ok(p):
        return (
            p
            and not p["bust"]
            and (p.get("win_pct") or 0) >= 0.524
            and p["end"] >= 70
            and (p.get("roi_bank") or 0) >= 0
        )

    return bool(ok(train_path) and ok(oos_path))


def weekday(date_s: str) -> int:
    y, m, d = map(int, date_s[:10].split("-"))
    return datetime(y, m, d).weekday()


# ---------- shared ATS helpers ----------
def load_ats(path: Path) -> List[Dict[str, Any]]:
    rows = json.loads(path.read_text())["rows"]
    out = []
    for r in rows:
        if r.get("push") or r.get("home_spread") is None or r.get("p_home_cover") is None or r.get("home_cover") is None:
            continue
        out.append(r)
    out.sort(key=lambda r: r["date"])
    return out


def ats_edge_picks(rows, edge_min: float, side_mode: str = "model") -> List[Dict[str, Any]]:
    """side_mode: model | always_dog | always_fav | rest_home_plus | rest_away_plus | qb_out | pers11"""
    picks = []
    for r in rows:
        p = float(r["p_home_cover"])
        hs = float(r["home_spread"])
        if side_mode == "always_dog":
            # bet dog at -110
            if hs > 0:
                won = int(r["home_cover"]) == 1
            elif hs < 0:
                won = int(r["home_cover"]) == 0
            else:
                continue
            picks.append({"date": r["date"][:10], "season": int(r["season"]), "won": won, "ml": JUICE})
            continue
        if side_mode == "always_fav":
            if hs < 0:
                won = int(r["home_cover"]) == 1
            elif hs > 0:
                won = int(r["home_cover"]) == 0
            else:
                continue
            picks.append({"date": r["date"][:10], "season": int(r["season"]), "won": won, "ml": JUICE})
            continue
        if side_mode == "rest_home_plus":
            if float(r.get("rest_diff") or 0) < 1:
                continue
        if side_mode == "rest_away_plus":
            # away more rested => rest_diff negative for home
            if float(r.get("rest_diff") or 0) > -1:
                continue
        if side_mode == "qb_out":
            if float(r.get("qb_out_edge") or 0) == 0:
                continue
        if side_mode == "pers11":
            if abs(float(r.get("pers11_edge") or 0)) < 0.01:
                continue
        # model edge
        if p - 0.5 > edge_min:
            picks.append({"date": r["date"][:10], "season": int(r["season"]), "won": int(r["home_cover"]) == 1, "ml": JUICE})
        elif (1 - p) - 0.5 > edge_min:
            picks.append({"date": r["date"][:10], "season": int(r["season"]), "won": int(r["home_cover"]) == 0, "ml": JUICE})
    return picks


def wf_ats_family(rows, label: str, modes, edge_grid, train_max=2018, oos_min=2019, min_n=40):
    train_rows = [r for r in rows if int(r["season"]) <= train_max]
    oos_rows = [r for r in rows if int(r["season"]) >= oos_min]
    best = None
    for mode in modes:
        for e in edge_grid:
            # always_dog/fav ignore edge
            if mode in ("always_dog", "always_fav"):
                if e != 0.0:
                    continue
            tr_picks = ats_edge_picks(train_rows, e, mode)
            oo_picks = ats_edge_picks(oos_rows, e, mode)
            if len(tr_picks) < min_n or len(oo_picks) < min_n:
                continue
            tr = bankroll(tr_picks)
            score = ((tr["end"] if not tr["bust"] else -1e9), tr["win_pct"] or 0, -tr["max_dd"])
            cand = {
                "mode": mode,
                "edge_min": e,
                "n_train": len(tr_picks),
                "n_oos": len(oo_picks),
                "train": tr,
                "_oos": oo_picks,
                "_score": score,
            }
            if best is None or score > best["_score"]:
                best = cand
    if not best:
        return {"label": label, "best": None}
    oo = bankroll(best.pop("_oos"))
    best.pop("_score")
    best["oos"] = oo
    best["clears_ats_proxy"] = dual_ats(best["train"], oo)
    return {"label": label, "best": best}


# ---------- NBA locked ML extras ----------
def load_nba_locked():
    lean = json.loads((SIMS / "nba-clv-probe/locked_oos_joined_lean.json").read_text())
    bets = []
    for b in lean["bets"]:
        if b.get("picked_ml") is None or b.get("won") is None:
            continue
        bets.append(
            {
                "date": b["date"][:10],
                "season": int(b["season"]),
                "ml": float(b["picked_ml"]),
                "won": bool(b["won"]),
                "clv_std": (-float(b["clv_fair_pts"])) if b.get("clv_fair_pts") is not None else None,
                "quality": bool(b.get("quality_side_ok") and b.get("quality_close_agree") and b.get("clv_fair_pts") is not None),
            }
        )
    bets.sort(key=lambda x: x["date"])
    return bets


def season_half(date_s: str) -> str:
    # NBA: Oct-Jan early, Feb-Jun late (rough)
    m = int(date_s[5:7])
    return "early" if m >= 10 or m <= 1 else "late"


def shannon_stake(edge: float, dec: float, br: float, frac: float = 1.0, cap: float = 0.02):
    # f* = edge / (dec-1) for known edge in prob; stake = frac * f* * br
    b = dec - 1.0
    if b <= 0 or edge <= 0:
        return None
    f = edge / b
    s = frac * f * br
    s = min(s, br * cap)
    return None if s < 0.5 else s


def run_nba_wave2(bets: List[Dict[str, Any]]) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    # Season regime
    early = [b for b in bets if season_half(b["date"]) == "early"]
    late = [b for b in bets if season_half(b["date"]) == "late"]
    out["season_regime"] = {
        "family": "market_structure_season",
        "early_flat5": bankroll(early),
        "late_flat5": bankroll(late),
    }
    # Anti-martingale: after win stake 1.5x next (cap £7.5), after loss reset £5
    state = {"mult": 1.0}

    def press_fn(b, br):
        s = min(FLAT * state["mult"], br * 0.08, 7.5)
        # update after knowing result — use this bet
        state["mult"] = 1.5 if b["won"] else 1.0
        return None if s < 0.5 else s

    out["anti_martingale_press"] = {
        "family": "staking_progression_new",
        "status_intent": "NEW win-press / anti-martingale on locked dogs",
        **bankroll(bets, press_fn),
    }
    # Martingale-ish loss press (expect ruin) — honesty kill
    state2 = {"mult": 1.0}

    def loss_press(b, br):
        s = min(FLAT * state2["mult"], br, 20.0)
        state2["mult"] = min(state2["mult"] * 2.0, 4.0) if not b["won"] else 1.0
        return None if s < 0.5 else s

    out["loss_press_cap4x"] = {
        "family": "staking_progression_new",
        "status_intent": "NEW loss-press (expect fail)",
        **bankroll(bets, loss_press),
    }
    # Bootstrap honesty on weekend-only flat (meta)
    weekend = [b for b in bets if weekday(b["date"]) >= 4]
    rng = random.Random(42)
    ends = []
    if weekend:
        for _ in range(400):
            sample = [weekend[rng.randrange(len(weekend))] for _ in range(len(weekend))]
            ends.append(bankroll(sample)["end"])
        ends.sort()
        out["bootstrap_weekend_flat5"] = {
            "family": "honesty_meta_new",
            "status_intent": "NEW bootstrap CI on weekend-only path",
            "n": len(weekend),
            "point_end": bankroll(weekend)["end"],
            "p05": round(ends[int(0.05 * len(ends))], 2),
            "p50": round(ends[int(0.50 * len(ends))], 2),
            "p95": round(ends[int(0.95 * len(ends))], 2),
            "frac_below_70": round(sum(1 for e in ends if e < 70) / len(ends), 4),
            "frac_bust_proxy_end0": round(sum(1 for e in ends if e <= 0) / len(ends), 4),
        }
    # RLM proxy: quality bets where line moved against pick (clv_std < 0) vs with
    q = [b for b in bets if b["quality"] and b["clv_std"] is not None]
    against = [b for b in q if b["clv_std"] < 0]  # close shorter than open on pick = -CLV
    with_move = [b for b in q if b["clv_std"] > 0]
    out["rlm_proxy_slices"] = {
        "family": "market_structure_rlm_new",
        "status_intent": "NEW reverse-line-movement slice (ex-post; not causal select)",
        "note": "Ex-post slices — NOT a causal gate (same-game close). Process only.",
        "n_against": len(against),
        "against_flat5": bankroll(against),
        "n_with": len(with_move),
        "with_flat5": bankroll(with_move),
    }
    # Month-of-year structure
    by_month = defaultdict(list)
    for b in bets:
        by_month[int(b["date"][5:7])].append(b)
    out["month_structure"] = {
        "family": "market_structure_calendar_new",
        "by_month": {str(m): bankroll(v) for m, v in sorted(by_month.items()) if len(v) >= 15},
    }
    return out


# ---------- Shannon on ATS using p_cover edge ----------
def run_shannon_ats(nba_rows) -> Dict[str, Any]:
    train = [r for r in nba_rows if int(r["season"]) <= 2018]
    oos = [r for r in nba_rows if int(r["season"]) >= 2019]
    # freeze edge on train cover rate of model side
    best = None
    for e in [0.02, 0.05, 0.08]:
        for frac in [0.25, 0.5, 1.0]:
            def make_picks(rows):
                picks = []
                for r in rows:
                    p = float(r["p_home_cover"])
                    if p - 0.5 > e:
                        edge = p - 0.5
                        won = int(r["home_cover"]) == 1
                    elif (1 - p) - 0.5 > e:
                        edge = (1 - p) - 0.5
                        won = int(r["home_cover"]) == 0
                    else:
                        continue
                    picks.append({"date": r["date"][:10], "won": won, "ml": JUICE, "edge": edge})
                return picks

            tr_p = make_picks(train)
            oo_p = make_picks(oos)
            if len(tr_p) < 80 or len(oo_p) < 80:
                continue

            def sfn(b, br, fr=frac):
                return shannon_stake(b["edge"], am_to_dec(JUICE), br, frac=fr, cap=0.02)

            tr = bankroll(tr_p, sfn)
            score = (tr["end"] if not tr["bust"] else -1e9, tr["win_pct"] or 0)
            cand = {"edge_min": e, "shannon_frac": frac, "n_train": len(tr_p), "n_oos": len(oo_p), "train": tr, "_oo": oo_p, "_score": score, "_fr": frac}
            if best is None or score > best["_score"]:
                best = cand
    if not best:
        return {"family": "staking_shannon_new", "best": None}
    fr = best.pop("_fr")
    oo_p = best.pop("_oo")
    best.pop("_score")

    def sfn(b, br, frr=fr):
        return shannon_stake(b["edge"], am_to_dec(JUICE), br, frac=frr, cap=0.02)

    oo = bankroll(oo_p, sfn)
    best["oos"] = oo
    best["clears_ats_proxy"] = dual_ats(best["train"], oo)
    return {"family": "staking_shannon_new", "status_intent": "NEW Shannon/fortune stake on NBA ATS p_cover edge", "best": best}


# ---------- Soccer OU 2.5 + DNB from FD ----------
def parse_fd_ou(fd_dir: Path) -> List[Dict[str, Any]]:
    rows = []
    for p in sorted(fd_dir.glob("*.csv")):
        league = p.name.split("_")[0]
        with p.open(newline="", encoding="utf-8", errors="replace") as f:
            rdr = csv.DictReader(f)
            for r in rdr:
                try:
                    o_over = float(r.get("B365>2.5") or r.get("Avg>2.5") or "")
                    o_under = float(r.get("B365<2.5") or r.get("Avg<2.5") or "")
                    c_over = float(r.get("B365C>2.5") or r.get("AvgC>2.5") or "")
                    c_under = float(r.get("B365C<2.5") or r.get("AvgC<2.5") or "")
                    hg, ag = int(r["FTHG"]), int(r["FTAG"])
                except (KeyError, ValueError, TypeError):
                    continue
                if min(o_over, o_under, c_over, c_under) <= 1.01:
                    continue
                date = r.get("Date") or ""
                try:
                    dd, mm, yy = date.split("/")
                    yyyy = int(yy) if len(yy) == 4 else 2000 + int(yy)
                    iso = f"{yyyy:04d}-{int(mm):02d}-{int(dd):02d}"
                except Exception:
                    continue
                total = hg + ag
                # fair open/close two-way
                fo = (1 / o_over) / (1 / o_over + 1 / o_under)
                fc = (1 / c_over) / (1 / c_over + 1 / c_under)
                rows.append(
                    {
                        "date": iso,
                        "season": yyyy if int(mm) >= 7 else yyyy,
                        "league": league,
                        "total": total,
                        "over_won": total > 2.5,
                        "o_over": o_over,
                        "o_under": o_under,
                        "clv_over_std": fc - fo,  # + = over shortened = under beat close if bet under? 
                        # For over side: beat close if open over decimal better than close => o_over > c_over
                        "open_better_over": o_over > c_over,
                        "fo_over": fo,
                        "fc_over": fc,
                    }
                )
    rows.sort(key=lambda x: (x["date"], x["league"]))
    return rows


def dec_to_am(dec: float) -> float:
    if dec >= 2:
        return (dec - 1) * 100
    return -100 / (dec - 1)


def run_soccer_ou(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    # Simple rolling league over-rate prior: bet over when prior 50-game over-rate > 0.55 and price >= 1.85
    # Train freeze threshold on seasons <=2021, OOS >=2022
    def simulate(thresh: float, min_dec: float, side: str):
        hist = defaultdict(list)
        picks = []
        for r in rows:
            key = r["league"]
            prior = hist[key]
            rate = (sum(prior[-50:]) / len(prior[-50:])) if len(prior) >= 50 else None
            hist[key].append(1 if r["over_won"] else 0)
            if rate is None:
                continue
            if side == "over":
                if rate > thresh and r["o_over"] >= min_dec:
                    picks.append(
                        {
                            "date": r["date"],
                            "season": r["season"],
                            "won": r["over_won"],
                            "ml": dec_to_am(r["o_over"]),
                            "league": r["league"],
                        }
                    )
            else:
                if rate < (1 - thresh) and r["o_under"] >= min_dec:
                    picks.append(
                        {
                            "date": r["date"],
                            "season": r["season"],
                            "won": not r["over_won"],
                            "ml": dec_to_am(r["o_under"]),
                            "league": r["league"],
                        }
                    )
        return picks

    best = None
    for thresh in [0.52, 0.55, 0.58, 0.60]:
        for min_dec in [1.70, 1.85, 2.00]:
            for side in ("over", "under"):
                picks = simulate(thresh, min_dec, side)
                train = [p for p in picks if p["season"] <= 2021]
                oos = [p for p in picks if p["season"] >= 2022]
                if len(train) < 40 or len(oos) < 40:
                    continue
                tr = bankroll(train)
                score = (tr["end"] if not tr["bust"] else -1e9, tr["win_pct"] or 0)
                cand = {
                    "thresh": thresh,
                    "min_dec": min_dec,
                    "side": side,
                    "n_train": len(train),
                    "n_oos": len(oos),
                    "train": tr,
                    "_oos": oos,
                    "_score": score,
                }
                if best is None or score > best["_score"]:
                    best = cand
    if not best:
        return {"family": "soccer_ou25_new", "best": None, "n_rows": len(rows)}
    oo = bankroll(best.pop("_oos"))
    best.pop("_score")
    best["oos"] = oo
    # soccer flood-ish: use draft dual on train+oos
    best["clears_dual_draft"] = bool(best["train"]["clears_draft"] and oo["clears_draft"] and not best["train"]["bust"] and not oo["bust"])
    # CLV process on overs
    overs = rows
    mean_clv = sum((r["fc_over"] - r["fo_over"]) for r in overs) / len(overs) if overs else None
    # +CLV for betting open over when fo < fc (over shortened)
    pct_plus = sum(1 for r in overs if r["fo_over"] < r["fc_over"]) / len(overs) if overs else None
    return {
        "family": "soccer_ou25_new",
        "status_intent": "NEW soccer OU 2.5 rolling-rate (multi-league FD)",
        "n_rows": len(rows),
        "leagues": sorted({r["league"] for r in rows}),
        "process_clv_over_mean_fc_minus_fo": round(mean_clv, 6) if mean_clv is not None else None,
        "pct_open_over_beats_close": round(pct_plus, 4) if pct_plus is not None else None,
        "best": best,
        "beats_book": False,
    }


def run_soccer_dnb_book(fd_dir: Path) -> Dict[str, Any]:
    """Draw-no-bet using book open 1X2: bet favorite DNB (draw void). No model — book-implied."""
    picks = []
    for p in sorted(fd_dir.glob("E0_*.csv")):
        with p.open(newline="", encoding="utf-8", errors="replace") as f:
            for r in csv.DictReader(f):
                try:
                    oh, od, oa = float(r["B365H"]), float(r["B365D"]), float(r["B365A"])
                    ftr = r["FTR"]
                except (KeyError, ValueError, TypeError):
                    continue
                date = r.get("Date") or ""
                try:
                    dd, mm, yy = date.split("/")
                    yyyy = int(yy) if len(yy) == 4 else 2000 + int(yy)
                    iso = f"{yyyy:04d}-{int(mm):02d}-{int(dd):02d}"
                except Exception:
                    continue
                # fav side
                if oh <= oa:
                    # home fav DNB: win if H, void if D, lose if A
                    if ftr == "D":
                        continue
                    won = ftr == "H"
                    # DNB price approx remove draw: fair from H vs A only
                    ih, ia = 1 / oh, 1 / oa
                    p_home = ih / (ih + ia)
                    dec = 1 / p_home  # rough de-vig two-way stake-at-risk price
                    picks.append({"date": iso, "season": yyyy, "won": won, "ml": dec_to_am(dec)})
                else:
                    if ftr == "D":
                        continue
                    won = ftr == "A"
                    ih, ia = 1 / oh, 1 / oa
                    p_away = ia / (ih + ia)
                    dec = 1 / p_away
                    picks.append({"date": iso, "season": yyyy, "won": won, "ml": dec_to_am(dec)})
    train = [x for x in picks if x["season"] <= 2021]
    oos = [x for x in picks if x["season"] >= 2022]
    return {
        "family": "soccer_dnb_book_new",
        "status_intent": "NEW DNB favorite using book prices only (no model edge)",
        "n": len(picks),
        "train": bankroll(train) if train else None,
        "oos": bankroll(oos) if oos else None,
        "clears_dual_draft": bool(train and oos and bankroll(train)["clears_draft"] and bankroll(oos)["clears_draft"]),
        "note": "Expect fail — betting book favorite DNB is not +EV inventing",
        "beats_book": False,
    }


# ---------- Horse: fade favourite NEW ----------
def run_horse_fade_fav() -> Dict[str, Any]:
    races = json.loads((SIMS / "racing-profitability/horse_racing_races.json").read_text())
    races = [r for r in races if not r.get("synthetic") and r.get("fav_sp_dec") and r.get("fav_won") is not None]
    races.sort(key=lambda r: r["date"])
    # Fade fav when field >= N and fav_sp_dec <= S (short fav in big field)
    best = None
    for min_field in [8, 10, 12]:
        for max_fav_dec in [2.0, 2.5, 3.0]:
            picks = []
            for r in races:
                if int(r.get("field") or 0) < min_field:
                    continue
                if float(r["fav_sp_dec"]) > max_fav_dec:
                    continue
                # "fade fav" as speculative: we don't have place SP — use win market only as:
                # bet that fav loses — but that's not a listed book price without lay exchange.
                # Approximate: equal-stake portfolio on a random non-fav is synthetic — REFUSED.
                # Instead score FAV WIN rate vs implied 1/sp — process edge claim only.
                picks.append(r)
            if len(picks) < 30:
                continue
            # split by date mid
            mid = picks[len(picks) // 2]["date"]
            train = [r for r in picks if r["date"] <= mid]
            oos = [r for r in picks if r["date"] > mid]
            if len(train) < 20 or len(oos) < 20:
                continue

            def stats(rs):
                n = len(rs)
                fav_wins = sum(1 for r in rs if r["fav_won"])
                # implied win from SP
                impl = [1 / float(r["fav_sp_dec"]) for r in rs]
                mean_impl = sum(impl) / n
                # fair-ish overround unknown in multi-runner — report raw
                return {
                    "n": n,
                    "fav_win_pct": round(fav_wins / n, 4),
                    "mean_sp_implied": round(mean_impl, 4),
                    "fav_wins_minus_implied": round(fav_wins / n - mean_impl, 4),
                }

            tr_s, oo_s = stats(train), stats(oos)
            # "edge" if fav wins less than implied on train (fade candidate)
            score = -tr_s["fav_wins_minus_implied"]  # want negative fav overperformance
            cand = {
                "min_field": min_field,
                "max_fav_dec": max_fav_dec,
                "train": tr_s,
                "oos": oo_s,
                "fade_signal_train": tr_s["fav_wins_minus_implied"] < -0.02,
                "fade_holds_oos": oo_s["fav_wins_minus_implied"] < -0.02,
                "_score": score,
            }
            if best is None or score > best["_score"]:
                best = cand
    if best:
        best.pop("_score")
    return {
        "family": "racing_fade_fav_process_new",
        "status_intent": "NEW horse short-fav fade process (no place SP — no bankroll paper)",
        "best": best,
        "paper_enable_possible": False,
        "reason": "No free fixed place/lay price — HARD STOP for bankroll path (prior map)",
        "beats_book": False,
    }


def dog_pick_rate(rows, edge_min: float) -> Optional[float]:
    n = dogish = 0
    for r in rows:
        p = float(r["p_home_cover"])
        hs = float(r["home_spread"])
        if p - 0.5 > edge_min:
            n += 1
            dogish += 1 if hs > 0 else 0
        elif (1 - p) - 0.5 > edge_min:
            n += 1
            dogish += 1 if hs < 0 else 0
    return (dogish / n) if n else None


def decide_paper(w2: Dict[str, Any]) -> Dict[str, Any]:
    enables = []
    holds = []

    def hold(name, reason, block=None):
        holds.append({"name": name, "reason": reason, "block": block})

    # ATS families — refuse ±1.5 structural dog illusion even if dual-clear numbers look green
    for key in ("nhl_ats", "mlb_ats", "nba_rest_ats", "nfl_qb_pers_ats"):
        block = w2.get(key)
        if not block:
            continue
        if isinstance(block, dict) and "best" in block and "label" in block:
            best = block["best"]
            name = block["label"]
        else:
            name = key
            best = block.get("best") if isinstance(block, dict) else None
        if not best:
            hold(name, "no best")
            continue
        structural = block.get("structural_dog_illusion")
        if structural:
            hold(
                name,
                "STRUCTURAL_HOLD — always-dog also dual-clears / model≈dog picker; not juice-beat (gold-standard ceiling)",
                {**best, "structural": structural},
            )
            continue
        if best.get("clears_ats_proxy"):
            enables.append({"name": name, "best": best})
        else:
            hold(name, "fails dual-clear ATS proxy", best)

    sh = w2.get("shannon_nba_ats", {}).get("best")
    if sh and sh.get("clears_ats_proxy"):
        enables.append({"name": "shannon_nba_ats", "best": sh})
    else:
        hold("shannon_nba_ats", "fails dual-clear", sh)

    sou = w2.get("soccer_ou25", {}).get("best")
    if sou and sou.get("clears_dual_draft"):
        # still soccer — require explicit dual + not just draft; keep off unless strong
        hold("soccer_ou25", "soccer paper policy OFF unless dual-clear flood; draft dual alone insufficient", sou)
    else:
        hold("soccer_ou25", "fails dual draft", sou)

    dnb = w2.get("soccer_dnb_book")
    if dnb and dnb.get("clears_dual_draft"):
        hold("soccer_dnb_book", "book-fav DNB clearing draft is not beats_book — refuse enable", dnb)
    else:
        hold("soccer_dnb_book", "fails", dnb)

    hold("racing_fade_fav", "HARD STOP no place/lay price", w2.get("racing_fade_fav"))
    hold("nba_progressions", "staking toys on locked selection — ops only / fail", w2.get("nba_ml_extras"))

    return {
        "paper_enable": enables,
        "hold": holds,
        "catakid_changes": "none — leave NBA daemon alone",
        "beats_book": False,
    }


def main():
    W2.mkdir(parents=True, exist_ok=True)
    nba_locked = load_nba_locked()
    nba_ats = load_ats(SIMS / "big-four-maxout/basketball_nba_ats_maxout_predictions.json")
    nhl_ats = load_ats(SIMS / "big-four-maxout/icehockey_nhl_ats_maxout_predictions.json")
    mlb_ats = load_ats(SIMS / "big-four-maxout/baseball_mlb_ats_maxout_predictions.json")
    nfl_ats = load_ats(SIMS / "big-four-maxout/americanfootball_nfl_ats_maxout_predictions.json")

    results: Dict[str, Any] = {
        "protocol": "sports_unbound_exhaustion_wave2",
        "generated_at": utc_now(),
        "constraints": {
            "cost": "£0",
            "synthetic": False,
            "catakid": "untouched",
            "bookie_login_automation": False,
            "beats_book_default": False,
            "oos_peek": False,
        },
        "nba_ml_extras": run_nba_wave2(nba_locked),
        "shannon_nba_ats": run_shannon_ats(nba_ats),
        "nhl_ats": wf_ats_family(
            nhl_ats,
            "nhl_ats_wave2",
            modes=["always_dog", "always_fav", "model"],
            edge_grid=[0.0, 0.05, 0.08],
            min_n=80,
        ),
        "mlb_ats": wf_ats_family(
            mlb_ats,
            "mlb_ats_wave2",
            modes=["always_dog", "always_fav", "model"],
            edge_grid=[0.0, 0.05, 0.08],
            train_max=2022,
            oos_min=2023,
            min_n=80,
        ),
        "nba_rest_ats": wf_ats_family(
            nba_ats,
            "nba_rest_ats_wave2",
            modes=["rest_home_plus", "rest_away_plus", "model"],
            edge_grid=[0.0, 0.05, 0.08],
            min_n=60,
        ),
        "nfl_qb_pers_ats": wf_ats_family(
            nfl_ats,
            "nfl_qb_pers_ats_wave2",
            modes=["qb_out", "pers11", "model"],
            edge_grid=[0.0, 0.05, 0.08],
            min_n=40,
        ),
    }
    # Stamp structural dog illusion for NHL/MLB (model≈always_dog)
    for sport_key, rows, train_max, oos_min in (
        ("nhl_ats", nhl_ats, 2018, 2019),
        ("mlb_ats", mlb_ats, 2022, 2023),
    ):
        block = results[sport_key]
        best = block.get("best")
        oos_rows = [r for r in rows if int(r["season"]) >= oos_min]
        train_rows = [r for r in rows if int(r["season"]) <= train_max]
        dog_tr = bankroll(ats_edge_picks(train_rows, 0.0, "always_dog")) if train_rows else None
        dog_oo = bankroll(ats_edge_picks(oos_rows, 0.0, "always_dog")) if oos_rows else None
        dpr = dog_pick_rate(oos_rows, best["edge_min"] if best and best["mode"] == "model" else 0.0) if best else None
        block["structural_dog_illusion"] = {
            "always_dog_dual_clear": bool(dog_tr and dog_oo and dual_ats(dog_tr, dog_oo)),
            "always_dog_train": dog_tr,
            "always_dog_oos": dog_oo,
            "model_dog_pick_rate_oos": dpr,
            "refuse_paper": True,
            "cite": "docs/big-four-data-maxout.md puck/run-line ceiling",
        }
        # Prefer reporting model best for transparency but paper gate uses structural flag
        if best and best["mode"] == "always_dog":
            block["note"] = "train-frozen best was always_dog itself — structural base-rate"
    fd = Path("/tmp/sports-unbound/w2")
    ou_rows = parse_fd_ou(fd)
    results["soccer_ou25"] = run_soccer_ou(ou_rows)
    results["soccer_dnb_book"] = run_soccer_dnb_book(fd)
    results["racing_fade_fav"] = run_horse_fade_fav()

    # Structural honesty note for NHL/MLB dogs
    results["structural_dog_honesty"] = {
        "nhl_always_dog_cover_full": results["nhl_ats"]["best"]["train"]["win_pct"]
        if results["nhl_ats"]["best"] and results["nhl_ats"]["best"]["mode"] == "always_dog"
        else None,
        "note": "Puck-line/run-line ±1.5 always-dog cover >>52.4% is structural base-rate, not juice-beat after vig path unless dual-clear bankroll — prior maxout ceiling.",
    }
    results["paper_decision"] = decide_paper(results)

    (W2 / "result.json").write_text(json.dumps(results, indent=2, default=str))
    idx = {
        "generated_at": results["generated_at"],
        "wave": 2,
        "families_scored": [
            "nba_season_regime",
            "anti_martingale",
            "loss_press",
            "bootstrap_weekend",
            "rlm_proxy",
            "month_structure",
            "shannon_ats",
            "nhl_ats",
            "mlb_ats",
            "nba_rest_ats",
            "nfl_qb_pers_ats",
            "soccer_ou25",
            "soccer_dnb_book",
            "racing_fade_fav_process",
        ],
        "paper_enable_count": len(results["paper_decision"]["paper_enable"]),
        "paper_enable": results["paper_decision"]["paper_enable"],
        "catakid": "untouched",
        "beats_book": False,
        "verdict": "EXHAUST_WAVE2_DONE",
        "result": "wave2/result.json",
    }
    (W2 / "index.json").write_text(json.dumps(idx, indent=2, default=str))
    # merge pointer into parent index
    parent = json.loads((OUT / "index.json").read_text())
    parent["wave2"] = idx
    parent["updated_at"] = results["generated_at"]
    (OUT / "index.json").write_text(json.dumps(parent, indent=2))
    print(json.dumps(idx, indent=2, default=str))


if __name__ == "__main__":
    main()
