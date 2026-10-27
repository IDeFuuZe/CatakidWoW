#!/usr/bin/env python3
"""Sports unbound WAVE 4 — NEW families not in waves 1–3.

£0 / train-frozen WF / no Catakid / no bookie login / beats_book=false.
"""
from __future__ import annotations

import csv
import json
import math
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

STORE = Path("/cursor/stores/bc-28a8dd7c-8662-49a7-9938-a5fa31b1d070")
SIMS = STORE / "internal/sims"
OUT = SIMS / "sports-unbound-exhaustion"
W4 = OUT / "wave4"
FD = Path("/tmp/sports-unbound/w4")
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


def dual_draft(tr, oo) -> bool:
    return bool(tr and oo and tr.get("clears_draft") and oo.get("clears_draft") and not tr["bust"] and not oo["bust"])


def dual_ats(tr, oo) -> bool:
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


def fget(raw, *keys):
    for k in keys:
        v = raw.get(k)
        if v not in (None, ""):
            try:
                return float(v)
            except (TypeError, ValueError):
                continue
    return None


def load_fd() -> List[Dict[str, Any]]:
    rows = []
    for p in sorted(FD.glob("*.csv")):
        if p.stat().st_size < 500:
            continue
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
                if r.get("FTR") not in ("H", "D", "A"):
                    continue
                rows.append(
                    {
                        "date": iso,
                        "season": int(iso[:4]),
                        "league": league,
                        "hg": hg,
                        "ag": ag,
                        "ftr": r["FTR"],
                        "raw": r,
                    }
                )
    rows.sort(key=lambda x: (x["date"], x["league"]))
    return rows


def wf_pick_best(candidates_builder, grid, train_pred, oos_pred):
    best = None
    for params in grid:
        picks = candidates_builder(params)
        train = [p for p in picks if train_pred(p)]
        oos = [p for p in picks if oos_pred(p)]
        if len(train) < 40 or len(oos) < 40:
            continue
        tr = bankroll(train)
        score = (tr["end"] if not tr["bust"] else -1e9, tr["win_pct"] or 0)
        cand = {"params": params, "n_train": len(train), "n_oos": len(oos), "train": tr, "_oos": oos, "_score": score}
        if best is None or score > best["_score"]:
            best = cand
    if not best:
        return None
    oo = bankroll(best.pop("_oos"))
    best.pop("_score")
    best["oos"] = oo
    best["clears_dual_draft"] = dual_draft(best["train"], oo)
    return best


# ----- 1. Pinnacle/PS vs B365 shop -----
def run_ps_vs_b365(rows):
    picks = []
    for r in rows:
        raw = r["raw"]
        b365 = fget(raw, "B365H")
        ps = fget(raw, "PSH")
        if b365 is None or ps is None or b365 <= 1.01 or ps <= 1.01:
            continue
        picks.append(
            {
                "date": r["date"],
                "season": r["season"],
                "edge": ps - b365,
                "won": r["ftr"] == "H",
                "ml": dec_to_am(ps),
            }
        )

    def builder(params):
        return [p for p in picks if p["edge"] >= params["min_edge"]]

    best = wf_pick_best(
        builder,
        [{"min_edge": e} for e in (0.02, 0.05, 0.08, 0.12, 0.15)],
        lambda p: p["season"] <= 2021,
        lambda p: p["season"] >= 2022,
    )
    return {
        "family": "ps_vs_b365_shop_new",
        "status_intent": "NEW Pinnacle/PSH vs B365H shop proxy (FD tape)",
        "n": len(picks),
        "best": best,
        "beats_book": False,
        "caveat": "Archive PSH not live fill — process/shop hygiene",
    }


# ----- 2. AH open→close CLV process -----
def run_ah_clv(rows):
    vals = []
    for r in rows:
        raw = r["raw"]
        ahh = fget(raw, "AHh")
        ahch = fget(raw, "AHCh")
        oh = fget(raw, "B365AHH", "AvgAHH")
        ch = fget(raw, "B365CAHH", "AvgCAHH")
        if None in (ahh, ahch, oh, ch) or oh <= 1.01 or ch <= 1.01:
            continue
        # home AH fair-ish from two-way open/close if away also present
        oa = fget(raw, "B365AHA", "AvgAHA")
        ca = fget(raw, "B365CAHA", "AvgCAHA")
        if oa is None or ca is None or oa <= 1.01 or ca <= 1.01:
            continue
        fo = (1 / oh) / (1 / oh + 1 / oa)
        fc = (1 / ch) / (1 / ch + 1 / ca)
        vals.append(
            {
                "date": r["date"],
                "line_move": ahch - ahh,
                "clv_home_std": fc - fo,  # + = home AH shortened
                "open_better_home_dec": oh > ch,
            }
        )
    if not vals:
        return {"family": "ah_clv_process_new", "n": 0}
    n = len(vals)
    return {
        "family": "ah_clv_process_new",
        "status_intent": "NEW Asian Handicap open→close CLV process",
        "n": n,
        "mean_clv_home_std": round(sum(v["clv_home_std"] for v in vals) / n, 6),
        "pct_open_better_home_dec": round(sum(1 for v in vals if v["open_better_home_dec"]) / n, 4),
        "mean_abs_line_move": round(sum(abs(v["line_move"]) for v in vals) / n, 4),
        "beats_book": False,
        "note": "Process only — no causal same-game gate",
    }


# ----- 3. Double chance 1X / X2 -----
def run_double_chance(rows):
    """DC price approx from 1X2: 1X = 1/(ph+pd) after de-vig three-way."""

    def dc_dec(h, d, a, which: str):
        ih, id_, ia = 1 / h, 1 / d, 1 / a
        s = ih + id_ + ia
        ph, pd, pa = ih / s, id_ / s, ia / s
        if which == "1X":
            return 1 / (ph + pd)
        return 1 / (pd + pa)

    picks = []
    for r in rows:
        raw = r["raw"]
        h, d, a = fget(raw, "B365H"), fget(raw, "B365D"), fget(raw, "B365A")
        if None in (h, d, a) or min(h, d, a) <= 1.01:
            continue
        for which, won in (
            ("1X", r["ftr"] in ("H", "D")),
            ("X2", r["ftr"] in ("A", "D")),
        ):
            dec = dc_dec(h, d, a, which)
            picks.append(
                {
                    "date": r["date"],
                    "season": r["season"],
                    "which": which,
                    "dec": dec,
                    "won": won,
                    "ml": dec_to_am(dec),
                    "home_dec": h,
                }
            )

    def builder(params):
        out = []
        for p in picks:
            if p["which"] != params["which"]:
                continue
            if p["dec"] < params["min_dec"]:
                continue
            # only when home is not huge chalk for 1X
            if params["which"] == "1X" and p["home_dec"] < params.get("min_home_dec", 1.01):
                continue
            out.append(p)
        return out

    grid = []
    for which in ("1X", "X2"):
        for min_dec in (1.25, 1.35, 1.45):
            for min_home_dec in (1.01, 1.80, 2.20):
                if which == "X2" and min_home_dec != 1.01:
                    continue
                grid.append({"which": which, "min_dec": min_dec, "min_home_dec": min_home_dec})
    best = wf_pick_best(builder, grid, lambda p: p["season"] <= 2021, lambda p: p["season"] >= 2022)
    return {
        "family": "soccer_double_chance_new",
        "status_intent": "NEW double-chance 1X/X2 from de-vig B365 1X2",
        "best": best,
        "beats_book": False,
    }


# ----- 4. Long draw -----
def run_long_draw(rows):
    picks = []
    for r in rows:
        d = fget(r["raw"], "B365D")
        if d is None or d <= 1.01:
            continue
        picks.append({"date": r["date"], "season": r["season"], "dec": d, "won": r["ftr"] == "D", "ml": dec_to_am(d)})

    def builder(params):
        return [p for p in picks if p["dec"] >= params["min_dec"]]

    best = wf_pick_best(
        builder,
        [{"min_dec": x} for x in (3.0, 3.4, 3.8, 4.2, 5.0)],
        lambda p: p["season"] <= 2021,
        lambda p: p["season"] >= 2022,
    )
    return {
        "family": "soccer_long_draw_new",
        "status_intent": "NEW long-draw filter on B365D",
        "best": best,
        "beats_book": False,
    }


# ----- 5. Rolling GD form → home/away -----
def run_rolling_gd(rows):
    # per league team rolling GD last N
    hist = defaultdict(list)  # (league, team) -> list of GD from team perspective
    picks = []
    for r in rows:
        raw = r["raw"]
        home = raw.get("HomeTeam") or raw.get("Home") or ""
        away = raw.get("AwayTeam") or raw.get("Away") or ""
        if not home or not away:
            continue
        h = fget(raw, "B365H")
        a = fget(raw, "B365A")
        if h is None or a is None or min(h, a) <= 1.01:
            continue
        key_h, key_a = (r["league"], home), (r["league"], away)
        gh = hist[key_h][-8:]
        ga = hist[key_a][-8:]
        if len(gh) >= 5 and len(ga) >= 5:
            form_h = sum(gh) / len(gh)
            form_a = sum(ga) / len(ga)
            delta = form_h - form_a
            picks.append(
                {
                    "date": r["date"],
                    "season": r["season"],
                    "delta": delta,
                    "side": "home" if delta >= 0 else "away",
                    "won": (r["ftr"] == "H") if delta >= 0 else (r["ftr"] == "A"),
                    "ml": dec_to_am(h if delta >= 0 else a),
                    "abs_delta": abs(delta),
                }
            )
        # update hist after pick (blind)
        hist[key_h].append(r["hg"] - r["ag"])
        hist[key_a].append(r["ag"] - r["hg"])

    def builder(params):
        out = []
        for p in picks:
            if p["abs_delta"] < params["min_abs_delta"]:
                continue
            if params["side"] != "either" and p["side"] != params["side"]:
                continue
            out.append(p)
        return out

    grid = []
    for min_abs in (0.5, 0.8, 1.2, 1.5):
        for side in ("either", "home", "away"):
            grid.append({"min_abs_delta": min_abs, "side": side})
    best = wf_pick_best(builder, grid, lambda p: p["season"] <= 2021, lambda p: p["season"] >= 2022)
    return {
        "family": "soccer_rolling_gd_form_new",
        "status_intent": "NEW rolling goal-diff form → 1X2 side",
        "n": len(picks),
        "best": best,
        "beats_book": False,
    }


# ----- 6. Overround regime -----
def run_overround(rows):
    picks = []
    for r in rows:
        raw = r["raw"]
        h, d, a = fget(raw, "B365H"), fget(raw, "B365D"), fget(raw, "B365A")
        if None in (h, d, a) or min(h, d, a) <= 1.01:
            continue
        ov = 1 / h + 1 / d + 1 / a
        # bet home when overround low (sharper book?)
        picks.append(
            {
                "date": r["date"],
                "season": r["season"],
                "overround": ov,
                "won": r["ftr"] == "H",
                "ml": dec_to_am(h),
            }
        )

    def builder(params):
        return [p for p in picks if p["overround"] <= params["max_ov"]]

    best = wf_pick_best(
        builder,
        [{"max_ov": x} for x in (1.03, 1.04, 1.05, 1.06, 1.08)],
        lambda p: p["season"] <= 2021,
        lambda p: p["season"] >= 2022,
    )
    return {
        "family": "soccer_overround_regime_new",
        "status_intent": "NEW low-overround home ML regime",
        "best": best,
        "beats_book": False,
    }


# ----- 7. NBA elo vs eff disagreement -----
def run_nba_elo_eff():
    rows = json.loads((SIMS / "big-four-maxout/basketball_nba_ats_maxout_predictions.json").read_text())["rows"]
    rows = [
        r
        for r in rows
        if not r.get("push")
        and r.get("home_cover") is not None
        and r.get("elo_margin") is not None
        and r.get("eff_margin") is not None
        and r.get("p_home_cover") is not None
    ]
    rows.sort(key=lambda r: r["date"])
    train = [r for r in rows if int(r["season"]) <= 2018]
    oos = [r for r in rows if int(r["season"]) >= 2019]

    def make(rs, min_disagree, edge, agree: bool):
        out = []
        for r in rs:
            elo, eff = float(r["elo_margin"]), float(r["eff_margin"])
            disagree = abs(elo - eff)
            if disagree < min_disagree:
                continue
            same_sign = (elo >= 0 and eff >= 0) or (elo < 0 and eff < 0)
            if agree and not same_sign:
                continue
            if (not agree) and same_sign:
                continue
            p = float(r["p_home_cover"])
            if p - 0.5 > edge:
                out.append({"date": r["date"][:10], "won": int(r["home_cover"]) == 1, "ml": JUICE})
            elif (1 - p) - 0.5 > edge:
                out.append({"date": r["date"][:10], "won": int(r["home_cover"]) == 0, "ml": JUICE})
        return out

    best = None
    for min_d in (1.0, 2.0, 3.0, 4.0):
        for edge in (0.0, 0.05, 0.08):
            for agree in (True, False):
                tr_p = make(train, min_d, edge, agree)
                oo_p = make(oos, min_d, edge, agree)
                if len(tr_p) < 60 or len(oo_p) < 60:
                    continue
                tr = bankroll(tr_p)
                score = (tr["end"] if not tr["bust"] else -1e9, tr["win_pct"] or 0)
                cand = {
                    "min_disagree": min_d,
                    "edge_min": edge,
                    "require_sign_agree": agree,
                    "n_train": len(tr_p),
                    "n_oos": len(oo_p),
                    "train": tr,
                    "_oos": oo_p,
                    "_score": score,
                }
                if best is None or score > best["_score"]:
                    best = cand
    if not best:
        return {"family": "nba_elo_eff_disagree_new", "best": None}
    oo = bankroll(best.pop("_oos"))
    best.pop("_score")
    best["oos"] = oo
    best["clears_ats_proxy"] = dual_ats(best["train"], oo)
    return {
        "family": "nba_elo_eff_disagree_new",
        "status_intent": "NEW Elo vs efficiency margin disagreement ATS filter",
        "best": best,
        "beats_book": False,
    }


# ----- 8. NBA sim_win_pct vs p_cover -----
def run_nba_sim_vs_p():
    rows = json.loads((SIMS / "big-four-maxout/basketball_nba_ats_maxout_predictions.json").read_text())["rows"]
    rows = [
        r
        for r in rows
        if not r.get("push")
        and r.get("home_cover") is not None
        and r.get("sim_home_win_pct") is not None
        and r.get("p_home_cover") is not None
    ]
    rows.sort(key=lambda r: r["date"])
    train = [r for r in rows if int(r["season"]) <= 2018]
    oos = [r for r in rows if int(r["season"]) >= 2019]
    best = None
    for min_gap in (0.03, 0.05, 0.08, 0.10):
        for edge in (0.0, 0.05, 0.08):
            def make(rs, min_gap=min_gap, edge=edge):
                out = []
                for r in rs:
                    gap = abs(float(r["sim_home_win_pct"]) - float(r["p_home_cover"]))
                    if gap < min_gap:
                        continue
                    # trust sim when gap large: side from sim
                    sim = float(r["sim_home_win_pct"])
                    if sim - 0.5 > edge:
                        out.append({"date": r["date"][:10], "won": int(r["home_cover"]) == 1, "ml": JUICE})
                    elif (1 - sim) - 0.5 > edge:
                        out.append({"date": r["date"][:10], "won": int(r["home_cover"]) == 0, "ml": JUICE})
                return out

            tr_p, oo_p = make(train), make(oos)
            if len(tr_p) < 60 or len(oo_p) < 60:
                continue
            tr = bankroll(tr_p)
            score = (tr["end"] if not tr["bust"] else -1e9, tr["win_pct"] or 0)
            cand = {
                "min_gap": min_gap,
                "edge_min": edge,
                "n_train": len(tr_p),
                "n_oos": len(oo_p),
                "train": tr,
                "_oos": oo_p,
                "_score": score,
            }
            if best is None or score > best["_score"]:
                best = cand
    if not best:
        return {"family": "nba_sim_vs_pcover_new", "best": None}
    oo = bankroll(best.pop("_oos"))
    best.pop("_score")
    best["oos"] = oo
    best["clears_ats_proxy"] = dual_ats(best["train"], oo)
    return {
        "family": "nba_sim_vs_pcover_new",
        "status_intent": "NEW sim_home_win_pct vs p_home_cover gap → trust sim side",
        "best": best,
        "beats_book": False,
    }


# ----- 9. NFL totals + ATS correlation cap -----
def run_nfl_corr_cap():
    tot = json.loads((SIMS / "big-four-maxout/americanfootball_nfl_totals_predictions.json").read_text())["rows"]
    ats = json.loads((SIMS / "big-four-maxout/americanfootball_nfl_ats_maxout_predictions.json").read_text())["rows"]
    tot = [r for r in tot if not r.get("push") and r.get("p_over") is not None and r.get("over_cover") is not None]
    ats = [r for r in ats if not r.get("push") and r.get("p_home_cover") is not None and r.get("home_cover") is not None]
    # index ATS by game_id or date+home
    ats_ix = {}
    for r in ats:
        ats_ix[(r["date"][:10], r["home"], r["away"])] = r

    def build(edge_t, edge_a, max_per_game):
        # produce chronological bets with optional cap 1 per game across markets
        events = []
        for r in tot:
            key = (r["date"][:10], r["home"], r["away"])
            p = float(r["p_over"])
            if p - 0.5 > edge_t:
                events.append({"date": r["date"][:10], "key": key, "mkt": "tot", "won": int(r["over_cover"]) == 1, "ml": JUICE, "edge": p - 0.5})
            elif (1 - p) - 0.5 > edge_t:
                events.append({"date": r["date"][:10], "key": key, "mkt": "tot", "won": int(r["over_cover"]) == 0, "ml": JUICE, "edge": (1 - p) - 0.5})
            a = ats_ix.get(key)
            if a:
                pa = float(a["p_home_cover"])
                if pa - 0.5 > edge_a:
                    events.append({"date": a["date"][:10], "key": key, "mkt": "ats", "won": int(a["home_cover"]) == 1, "ml": JUICE, "edge": pa - 0.5})
                elif (1 - pa) - 0.5 > edge_a:
                    events.append({"date": a["date"][:10], "key": key, "mkt": "ats", "won": int(a["home_cover"]) == 0, "ml": JUICE, "edge": (1 - pa) - 0.5})
        events.sort(key=lambda x: (x["date"], -x["edge"], x["mkt"]))
        if max_per_game == 1:
            seen = set()
            capped = []
            for e in events:
                if e["key"] in seen:
                    continue
                seen.add(e["key"])
                capped.append(e)
            events = capped
        return events

    best = None
    for edge_t in (0.02, 0.05, 0.08):
        for edge_a in (0.02, 0.05, 0.08):
            for cap in (1, 2):
                ev = build(edge_t, edge_a, cap)
                # season from date year approx using ATS season if join — use year
                for e in ev:
                    e["season"] = int(e["date"][:4])
                train = [e for e in ev if e["season"] <= 2018]
                oos = [e for e in ev if e["season"] >= 2019]
                if len(train) < 50 or len(oos) < 50:
                    continue
                tr = bankroll(train)
                score = (tr["end"] if not tr["bust"] else -1e9, tr["win_pct"] or 0)
                cand = {
                    "edge_totals": edge_t,
                    "edge_ats": edge_a,
                    "max_per_game": cap,
                    "n_train": len(train),
                    "n_oos": len(oos),
                    "train": tr,
                    "_oos": oos,
                    "_score": score,
                }
                if best is None or score > best["_score"]:
                    best = cand
    if not best:
        return {"family": "nfl_totals_ats_corr_cap_new", "best": None}
    oo = bankroll(best.pop("_oos"))
    best.pop("_score")
    best["oos"] = oo
    best["clears_ats_proxy"] = dual_ats(best["train"], oo)
    return {
        "family": "nfl_totals_ats_corr_cap_new",
        "status_intent": "NEW NFL totals+ATS joint book with per-game exposure cap",
        "best": best,
        "beats_book": False,
    }


# ----- 10. Locked NBA mean-reversion + stop-win -----
def run_nba_locked_mr_stop():
    lean = json.loads((SIMS / "nba-clv-probe/locked_oos_joined_lean.json").read_text())
    bets = []
    for b in lean["bets"]:
        if b.get("picked_ml") is None or b.get("won") is None:
            continue
        bets.append({"date": b["date"][:10], "ml": float(b["picked_ml"]), "won": bool(b["won"])})
    bets.sort(key=lambda x: x["date"])

    # mean reversion: only bet after 2 consecutive wins (expect fade)
    def after_wins(seq, w=2):
        out = []
        streak = 0
        for b in seq:
            if streak >= w:
                out.append(b)
            streak = streak + 1 if b["won"] else 0
        return out

    # stop-win: halt when BR >= start+40
    def stop_win_path(seq, target=40.0):
        br = START
        peak = START
        max_dd = pl = staked = 0.0
        n = wins = 0
        for b in seq:
            if br >= START + target:
                break
            s = FLAT
            if s > br:
                break
            d = pnl(b["won"], b["ml"], s)
            br += d
            pl += d
            staked += s
            n += 1
            wins += int(b["won"])
            peak = max(peak, br)
            max_dd = max(max_dd, peak - br)
        return {
            "n": n,
            "wins": wins,
            "win_pct": (wins / n) if n else None,
            "pl": round(pl, 4),
            "end": round(br, 4),
            "roi_bank": round((br - START) / START, 6),
            "max_dd": round(max_dd, 4),
            "bust": br <= 0,
            "clears_draft": br >= 70 and (br - START) >= 0 and br > 0,
            "stopped_at_target": br >= START + target,
        }

    return {
        "family": "nba_locked_meanrev_stopwin_new",
        "status_intent": "NEW mean-reversion-after-wins + stop-win on frozen dogs",
        "baseline": bankroll(bets),
        "after_2wins_flat5": bankroll(after_wins(bets, 2)),
        "after_3wins_flat5": bankroll(after_wins(bets, 3)),
        "stop_win_plus40": stop_win_path(bets, 40),
        "stop_win_plus20": stop_win_path(bets, 20),
        "beats_book": False,
    }


# ----- 11. Other desks reaffirm -----
def run_other_reaffirm():
    base = SIMS / "other-sports-maxout"
    out = {}
    for name in ("mma_mixed_martial_arts.json", "esports_cs.json", "esports_valorant.json"):
        d = json.loads((base / name).read_text())
        out[name.replace(".json", "")] = {
            "beats_book": d.get("beats_book", False),
            "closes": d.get("closes_status") or d.get("closes_join") or d.get("closes_note"),
            "path_decision": d.get("path_decision"),
            "paper": "no — prior OOS/disable or closes partial",
        }
    return {
        "family": "other_desks_reaffirm_wave4",
        "status_intent": "Reaffirm MMA/CS/Valorant not Dec1 paper (no new priced enable)",
        "desks": out,
    }


def decide_paper(w4: Dict[str, Any]) -> Dict[str, Any]:
    enables, holds = [], []

    def hold(name, reason, block=None):
        holds.append({"name": name, "reason": reason, "block": block})

    for key in ("ps_vs_b365", "double_chance", "long_draw", "rolling_gd", "overround"):
        best = w4.get(key, {}).get("best")
        if best and best.get("clears_dual_draft"):
            hold(key, "soccer/shop dual draft alone — policy OFF / no beats_book", best)
        else:
            hold(key, "fails dual draft", best)

    hold("ah_clv", "process only", w4.get("ah_clv"))

    for key in ("nba_elo_eff", "nba_sim_vs_p", "nfl_corr_cap"):
        best = w4.get(key, {}).get("best")
        if best and best.get("clears_ats_proxy"):
            enables.append({"name": key, "best": best})
        else:
            hold(key, "fails ATS dual-clear", best)

    hold("nba_mr_stop", "ops on frozen selection", w4.get("nba_mr_stop"))
    hold("other_reaffirm", "no enable", w4.get("other_reaffirm"))

    return {
        "paper_enable": enables,
        "hold": holds,
        "catakid_changes": "none — leave NBA daemon alone",
        "beats_book": False,
    }


def main():
    W4.mkdir(parents=True, exist_ok=True)
    rows = load_fd()
    results = {
        "protocol": "sports_unbound_exhaustion_wave4",
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
        "ps_vs_b365": run_ps_vs_b365(rows),
        "ah_clv": run_ah_clv(rows),
        "double_chance": run_double_chance(rows),
        "long_draw": run_long_draw(rows),
        "rolling_gd": run_rolling_gd(rows),
        "overround": run_overround(rows),
        "nba_elo_eff": run_nba_elo_eff(),
        "nba_sim_vs_p": run_nba_sim_vs_p(),
        "nfl_corr_cap": run_nfl_corr_cap(),
        "nba_mr_stop": run_nba_locked_mr_stop(),
        "other_reaffirm": run_other_reaffirm(),
    }
    results["paper_decision"] = decide_paper(results)
    (W4 / "result.json").write_text(json.dumps(results, indent=2, default=str))
    idx = {
        "generated_at": results["generated_at"],
        "wave": 4,
        "families_scored": [
            "ps_vs_b365_shop",
            "ah_clv_process",
            "soccer_double_chance",
            "soccer_long_draw",
            "soccer_rolling_gd",
            "soccer_overround",
            "nba_elo_eff_disagree",
            "nba_sim_vs_pcover",
            "nfl_totals_ats_corr_cap",
            "nba_meanrev_stopwin",
            "other_desks_reaffirm",
        ],
        "paper_enable_count": len(results["paper_decision"]["paper_enable"]),
        "paper_enable": results["paper_decision"]["paper_enable"],
        "catakid": "untouched",
        "beats_book": False,
        "verdict": "EXHAUST_WAVE4_DONE",
        "result": "wave4/result.json",
    }
    (W4 / "index.json").write_text(json.dumps(idx, indent=2, default=str))
    parent = json.loads((OUT / "index.json").read_text())
    parent["wave4"] = idx
    parent["updated_at"] = results["generated_at"]
    (OUT / "index.json").write_text(json.dumps(parent, indent=2))
    print(json.dumps(idx, indent=2, default=str))


if __name__ == "__main__":
    main()
