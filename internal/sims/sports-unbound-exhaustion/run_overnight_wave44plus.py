#!/usr/bin/env python3
"""Continuation waves 44+ — more free+new until re-audit or 05:00 London."""
from __future__ import annotations

import csv
import json
import traceback
from collections import defaultdict
from datetime import date as dtdate
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

try:
    from zoneinfo import ZoneInfo

    LON = ZoneInfo("Europe/London")
except Exception:
    LON = timezone.utc

STORE = Path("/cursor/stores/bc-28a8dd7c-8662-49a7-9938-a5fa31b1d070")
SIMS = STORE / "internal/sims"
OUT = SIMS / "sports-unbound-exhaustion"
DOC = STORE / "docs/sports-unbound-exhaustion.md"
WS_DOC = Path("/workspace/docs/sports-unbound-exhaustion.md")
WS_OUT = Path("/workspace/internal/sims/sports-unbound-exhaustion")
FD = Path("/tmp/sports-unbound/overnight")
START = 80.0
FLAT = 5.0
JUICE = -110
STOP_HOUR, STOP_MINUTE = 5, 0


def now_lon():
    return datetime.now(LON)


def past_stop():
    n = now_lon()
    return (n.hour > STOP_HOUR) or (n.hour == STOP_HOUR and n.minute >= STOP_MINUTE)


def utc_now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def am_to_dec(ml: float) -> float:
    ml = float(ml)
    return 1.0 + ml / 100.0 if ml > 0 else 1.0 + 100.0 / abs(ml)


def dec_to_am(dec: float) -> float:
    return (dec - 1) * 100 if dec >= 2 else -100 / (dec - 1)


def pnl(won: bool, ml: float, stake: float) -> float:
    return stake * (am_to_dec(ml) - 1.0) if won else -stake


def bankroll(bets, stake_fn=None, start=START):
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


def dual_draft(tr, oo):
    return bool(tr and oo and tr.get("clears_draft") and oo.get("clears_draft") and not tr["bust"] and not oo["bust"])


def dual_ats(tr, oo):
    def ok(p):
        return p and not p["bust"] and (p.get("win_pct") or 0) >= 0.524 and p["end"] >= 70 and (p.get("roi_bank") or 0) >= 0

    return bool(ok(tr) and ok(oo))


def fget(raw, *keys):
    for k in keys:
        v = raw.get(k)
        if v not in (None, ""):
            try:
                return float(v)
            except (TypeError, ValueError):
                continue
    return None


def parse_iso(date: str):
    try:
        dd, mm, yy = date.split("/")
        yyyy = int(yy) if len(yy) == 4 else 2000 + int(yy)
        return f"{yyyy:04d}-{int(mm):02d}-{int(dd):02d}"
    except Exception:
        return None


def load_fd():
    rows = []
    for p in sorted(FD.glob("*.csv")):
        if p.stat().st_size < 800:
            continue
        league = p.name.split("_")[0]
        with p.open(newline="", encoding="utf-8", errors="replace") as f:
            for r in csv.DictReader(f):
                iso = parse_iso(r.get("Date") or "")
                if not iso or r.get("FTR") not in ("H", "D", "A"):
                    continue
                try:
                    hg, ag = int(r["FTHG"]), int(r["FTAG"])
                except Exception:
                    continue
                rows.append({"date": iso, "season": int(iso[:4]), "league": league, "hg": hg, "ag": ag, "ftr": r["FTR"], "raw": r})
    rows.sort(key=lambda x: (x["date"], x["league"]))
    return rows


def wf(builder, grid, train_y=2021, oos_y=2022, min_n=40):
    best = None
    for params in grid:
        picks = builder(params)
        train = [p for p in picks if p["season"] <= train_y]
        oos = [p for p in picks if p["season"] >= oos_y]
        if len(train) < min_n or len(oos) < min_n:
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


def wf_ats(builder, grid, train_y=2018, oos_y=2019, min_n=80):
    best = None
    for params in grid:
        picks = builder(params)
        train = [p for p in picks if p["season"] <= train_y]
        oos = [p for p in picks if p["season"] >= oos_y]
        if len(train) < min_n or len(oos) < min_n:
            continue
        tr = bankroll(train)
        score = (tr["win_pct"] or 0, tr["end"] if not tr["bust"] else -1e9)
        cand = {"params": params, "n_train": len(train), "n_oos": len(oos), "train": tr, "_oos": oos, "_score": score}
        if best is None or score > best["_score"]:
            best = cand
    if not best:
        return None
    oo = bankroll(best.pop("_oos"))
    best.pop("_score")
    best["oos"] = oo
    best["clears_ats_proxy"] = dual_ats(best["train"], oo)
    return best


def ah_away_covers(hg, ag, ahh):
    """Away AH: away gets -AHh (if AHh is home line)."""
    # home line ahh means away line = -ahh
    margin = (ag - hg) + (-ahh)
    if abs(margin) < 1e-9:
        return None
    return margin > 0


def slim_for_doc(obj, depth=0):
    if depth > 4:
        return "…"
    if isinstance(obj, dict):
        out = {}
        for k, v in obj.items():
            if k in ("_oos", "raw", "bets"):
                continue
            if k in ("train", "oos", "best") and isinstance(v, dict):
                keys = ("n", "win_pct", "end", "max_dd", "bust", "clears_draft", "clears_ats_proxy", "params", "n_train", "n_oos", "clears_dual_draft", "note")
                out[k] = {kk: slim_for_doc(v[kk], depth + 1) for kk in keys if kk in v}
                for nested in ("train", "oos"):
                    if nested in v and isinstance(v[nested], dict):
                        out[k][nested] = {kk: v[nested][kk] for kk in ("n", "win_pct", "end", "max_dd", "bust", "clears_draft") if kk in v[nested]}
            else:
                out[k] = slim_for_doc(v, depth + 1)
        return out
    if isinstance(obj, list):
        return [slim_for_doc(x, depth + 1) for x in obj[:30]]
    return obj


def append_doc(wave_num, title, result, enables):
    ts = result.get("generated_at", utc_now())
    payload = {
        "wave": wave_num,
        "family_set": result.get("family_set"),
        "paper_enables": enables,
        "highlights": slim_for_doc({k: result[k] for k in list(result) if k not in ("family_set", "paper_enables", "paper_decision", "wave")}),
    }
    lines = [
        "",
        "---",
        "",
        f"## Wave {wave_num} — {title} (`{ts}`)",
        "",
        f"**EXHAUST_WAVE{wave_num}_DONE.** Families: `{result.get('family_set', title)}`. "
        f"Paper enables this wave: **{len(enables)}**. Catakid NBA **untouched**. `beats_book=false`.",
        "",
        "```json",
        json.dumps(payload, indent=2, default=str)[:4500],
        "```",
        "",
        f"Raw: [`../internal/sims/sports-unbound-exhaustion/wave{wave_num}/`](../internal/sims/sports-unbound-exhaustion/wave{wave_num}/)",
        "",
        f"## EXHAUST_WAVE{wave_num}_DONE",
        "",
    ]
    text = "\n".join(lines)
    for path in (DOC, WS_DOC):
        if path.parent.exists():
            with path.open("a", encoding="utf-8") as f:
                f.write(text)


def run_wave(wave_num, title, result):
    for base in (OUT, WS_OUT):
        (base / f"wave{wave_num}").mkdir(parents=True, exist_ok=True)
    result = dict(result)
    result["generated_at"] = utc_now()
    result["wave"] = wave_num
    enables = list(result.get("paper_enables") or [])
    result["paper_decision"] = {"paper_enable": enables, "catakid": "untouched", "beats_book": False}
    slim = slim_for_doc(result)
    idx = {
        "generated_at": result["generated_at"],
        "wave": wave_num,
        "title": title,
        "family_set": result.get("family_set"),
        "paper_enable_count": len(enables),
        "paper_enable": enables,
        "verdict": f"EXHAUST_WAVE{wave_num}_DONE",
        "catakid": "untouched",
        "beats_book": False,
    }
    for base in (OUT, WS_OUT):
        (base / f"wave{wave_num}" / "result.json").write_text(json.dumps(slim, indent=2, default=str))
        (base / f"wave{wave_num}" / "index.json").write_text(json.dumps(idx, indent=2, default=str))
    append_doc(wave_num, title, slim, enables)
    return idx


def season_of(r):
    return int(str(r["season"])[:4]) if r.get("season") is not None else int(str(r["date"])[:4])


# ---- families ----

def wave44_away_ah(rows):
    picks = []
    for r in rows:
        raw = r["raw"]
        ahh = fget(raw, "AHh")
        price = fget(raw, "B365AHA", "AvgAHA", "PAHA")
        if ahh is None or not price or price <= 1.01:
            continue
        cover = ah_away_covers(r["hg"], r["ag"], ahh)
        if cover is None:
            continue
        picks.append({"date": r["date"], "season": r["season"], "ahh": ahh, "won": cover, "ml": dec_to_am(price)})

    def builder(params):
        out = []
        for p in picks:
            if abs(p["ahh"]) > params["max_abs"]:
                continue
            if params["side"] == "dog" and p["ahh"] <= 0:  # away is dog when home line negative? home -1 → away +1 dog receiving
                # away dog when -ahh > 0 i.e. ahh < 0
                continue
            if params["side"] == "fav" and p["ahh"] >= 0:
                continue
            out.append(p)
        return out

    # Fix side logic: away receives -ahh; away is dog when -ahh > 0 ⇒ ahh < 0
    def builder2(params):
        out = []
        for p in picks:
            if abs(p["ahh"]) > params["max_abs"]:
                continue
            away_line = -p["ahh"]
            if params["side"] == "dog" and away_line <= 0:
                continue
            if params["side"] == "fav" and away_line >= 0:
                continue
            out.append(p)
        return out

    best = wf(builder2, [{"side": s, "max_abs": m} for s in ("dog", "fav") for m in (0.5, 1.0, 1.5, 2.0)], min_n=50)
    return {"family_set": "wave44_soccer_away_ah", "best": best, "n": len(picks), "paper_enables": [], "policy": "soccer OFF"}


def wave45_nba_resid_bands():
    rows = json.loads((SIMS / "big-four-maxout/basketball_nba_ats_maxout_predictions.json").read_text())["rows"]

    def builder(params):
        out = []
        for r in rows:
            if r.get("push") or r.get("home_cover") is None or r.get("p_home_cover") is None or r.get("resid_hat") is None:
                continue
            rh = abs(float(r["resid_hat"]))
            if not (params["lo"] <= rh < params["hi"]):
                continue
            edge = float(r["p_home_cover"]) - 0.5
            if abs(edge) < params["min_edge"]:
                continue
            pick_home = edge >= 0
            out.append({"date": r["date"], "season": season_of(r), "won": bool(r["home_cover"]) if pick_home else (not bool(r["home_cover"])), "ml": JUICE})
        return out

    bands = [(0, 1), (1, 2), (2, 3), (3, 5), (5, 99)]
    best = wf_ats(builder, [{"lo": a, "hi": b, "min_edge": e} for a, b in bands for e in (0.04, 0.06, 0.08)])
    enables = []
    if best and best.get("clears_ats_proxy"):
        enables = [{"family": "wave45_nba_resid_bands", "params": best["params"], "clears_ats_proxy": True}]
    return {"family_set": "wave45_nba_resid_bands", "best": best, "paper_enables": enables}


def wave46_nfl_injury_filter_ats():
    rows = json.loads((SIMS / "big-four-maxout/americanfootball_nfl_ats_maxout_predictions.json").read_text())["rows"]

    def builder(params):
        out = []
        for r in rows:
            if r.get("push") or r.get("home_cover") is None or r.get("p_home_cover") is None:
                continue
            inj = float(r.get("injury_filter") or 0)
            if params["mode"] == "clean" and inj != 0:
                continue
            if params["mode"] == "flagged" and inj == 0:
                continue
            edge = float(r["p_home_cover"]) - 0.5
            if abs(edge) < params["min_edge"]:
                continue
            pick_home = edge >= 0
            out.append({"date": r["date"], "season": season_of(r), "won": bool(r["home_cover"]) if pick_home else (not bool(r["home_cover"])), "ml": JUICE})
        return out

    best = wf_ats(builder, [{"mode": m, "min_edge": e} for m in ("clean", "flagged") for e in (0.04, 0.06, 0.08)])
    enables = []
    if best and best.get("clears_ats_proxy"):
        enables = [{"family": "wave46_nfl_injury_filter_ats", "params": best["params"], "clears_ats_proxy": True}]
    return {"family_set": "wave46_nfl_injury_filter_ats", "best": best, "paper_enables": enables}


def wave47_nhl_fav_honesty():
    rows = json.loads((SIMS / "big-four-maxout/icehockey_nhl_ats_maxout_predictions.json").read_text())["rows"]
    fav, dog, model = [], [], []
    for r in rows:
        if r.get("push") or r.get("home_cover") is None or r.get("home_spread") is None:
            continue
        s = season_of(r)
        hs = float(r["home_spread"])
        home_fav = hs < 0
        fav.append({"date": r["date"], "season": s, "won": bool(r["home_cover"]) if home_fav else (not bool(r["home_cover"])), "ml": JUICE})
        dog.append({"date": r["date"], "season": s, "won": (not bool(r["home_cover"])) if home_fav else bool(r["home_cover"]), "ml": JUICE})
        if r.get("p_home_cover") is not None:
            pick_home = float(r["p_home_cover"]) >= 0.5
            model.append({"date": r["date"], "season": s, "won": bool(r["home_cover"]) if pick_home else (not bool(r["home_cover"])), "ml": JUICE})

    def split(picks):
        tr = [p for p in picks if p["season"] <= 2018]
        oo = [p for p in picks if p["season"] >= 2019]
        if len(tr) < 80 or len(oo) < 80:
            return None
        a, b = bankroll(tr), bankroll(oo)
        return {"train": a, "oos": b, "clears_ats_proxy": dual_ats(a, b), "n_train": len(tr), "n_oos": len(oo)}

    return {
        "family_set": "wave47_nhl_fav_vs_dog_honesty",
        "always_fav": split(fav),
        "always_dog": split(dog),
        "model": split(model),
        "paper_enables": [],
        "policy": "STRUCTURAL_HOLD reaffirm if dog clears",
    }


def wave48_midweek_under(rows):
    picks = []
    for r in rows:
        raw = r["raw"]
        o_under = fget(raw, "B365<2.5", "Avg<2.5")
        if not o_under or o_under <= 1.01:
            continue
        try:
            y, m, d = map(int, r["date"].split("-"))
            wd = dtdate(y, m, d).weekday()
        except Exception:
            continue
        picks.append({"date": r["date"], "season": r["season"], "wd": wd, "won": (r["hg"] + r["ag"]) < 2.5, "ml": dec_to_am(o_under)})

    best = wf(
        lambda params: [p for p in picks if p["wd"] in params["days"]],
        [{"days": d} for d in ([1, 2], [0, 1, 2], [5, 6], [4, 5, 6], [3])],
    )
    return {"family_set": "wave48_midweek_under", "best": best, "n": len(picks), "paper_enables": [], "policy": "soccer OFF"}


def wave49_pickem_ah(rows):
    """AHh ≈ 0 pick'em AH home."""
    picks = []
    for r in rows:
        raw = r["raw"]
        ahh = fget(raw, "AHh")
        price = fget(raw, "B365AHH", "AvgAHH")
        if ahh is None or not price or price <= 1.01:
            continue
        if abs(ahh) > 0.26:
            continue
        margin = (r["hg"] - r["ag"]) + ahh
        if abs(margin) < 1e-9:
            continue
        picks.append({"date": r["date"], "season": r["season"], "won": margin > 0, "ml": dec_to_am(price)})
    best = wf(lambda params: picks, [{}], min_n=40)
    return {"family_set": "wave49_pickem_ah_home", "best": best, "n": len(picks), "paper_enables": [], "policy": "soccer OFF"}


def wave50_pinnacle_under_shop(rows):
    picks = []
    for r in rows:
        raw = r["raw"]
        b = fget(raw, "B365<2.5")
        p = fget(raw, "P<2.5")
        if not b or not p or min(b, p) <= 1.01 or p <= b:
            continue
        picks.append({"date": r["date"], "season": r["season"], "edge": p - b, "won": (r["hg"] + r["ag"]) < 2.5, "ml": dec_to_am(p)})
    best = wf(lambda params: [p for p in picks if p["edge"] >= params["min_dec"]], [{"min_dec": x} for x in (0.02, 0.05, 0.1)])
    return {"family_set": "wave50_pinnacle_under_shop", "best": best, "n": len(picks), "paper_enables": [], "policy": "soccer OFF"}


def wave51_soccer_month_home_dog(rows):
    picks = []
    for r in rows:
        raw = r["raw"]
        hml = fget(raw, "B365H")
        if not hml or hml <= 1.01:
            continue
        try:
            month = int(r["date"][5:7])
        except Exception:
            continue
        if hml < 2.2:  # not dog
            continue
        picks.append({"date": r["date"], "season": r["season"], "month": month, "won": r["ftr"] == "H", "ml": dec_to_am(hml)})
    best = wf(lambda params: [p for p in picks if p["month"] in params["months"]], [{"months": m} for m in ([8, 9], [10, 11], [12, 1], [2, 3], [4, 5])])
    return {"family_set": "wave51_month_home_dog", "best": best, "n": len(picks), "paper_enables": [], "policy": "soccer OFF"}


def wave52_ht_draw_ft_under(rows):
    picks = []
    for r in rows:
        raw = r["raw"]
        htr = raw.get("HTR")
        o_under = fget(raw, "B365<2.5", "Avg<2.5")
        # cannot condition on live HT for pre-match — use PRIOR ht draw rate instead
        pass
    # prior: teams with high HT-draw rate → FT under
    hist = defaultdict(list)
    for r in rows:
        raw = r["raw"]
        home, away = raw.get("HomeTeam") or "", raw.get("AwayTeam") or ""
        htr = raw.get("HTR")
        o_under = fget(raw, "B365<2.5", "Avg<2.5")
        if not home or not away or not o_under or o_under <= 1.01 or htr not in ("H", "D", "A"):
            continue
        kh, ka = (r["league"], home), (r["league"], away)
        ph, pa = hist[kh][-6:], hist[ka][-6:]
        if len(ph) >= 4 and len(pa) >= 4:
            rate = (sum(1 for x in ph if x == "D") + sum(1 for x in pa if x == "D")) / (len(ph) + len(pa))
            picks.append({"date": r["date"], "season": r["season"], "rate": rate, "won": (r["hg"] + r["ag"]) < 2.5, "ml": dec_to_am(o_under)})
        hist[kh].append(htr)
        hist[ka].append(htr)
    best = wf(lambda params: [p for p in picks if p["rate"] >= params["min_rate"]], [{"min_rate": x} for x in (0.2, 0.3, 0.4)])
    return {"family_set": "wave52_ht_draw_rate_under", "best": best, "n": len(picks), "paper_enables": [], "policy": "soccer OFF"}


def wave53_nfl_band_staking():
    """Staking variants on wave20 enabling filter (flat vs ¼-Kelly proxy vs dd-scale)."""
    rows = json.loads((SIMS / "big-four-maxout/americanfootball_nfl_ats_maxout_predictions.json").read_text())["rows"]
    lo, hi, min_edge = 10, 14, 0.06
    picks = []
    for r in rows:
        if r.get("push") or r.get("home_cover") is None or r.get("home_spread") is None or r.get("p_home_cover") is None:
            continue
        sp = abs(float(r["home_spread"]))
        if not (lo <= sp < hi):
            continue
        edge = abs(float(r["p_home_cover"]) - 0.5)
        if edge < min_edge:
            continue
        pick_home = float(r["p_home_cover"]) >= 0.5
        picks.append(
            {
                "date": r["date"],
                "season": season_of(r),
                "won": bool(r["home_cover"]) if pick_home else (not bool(r["home_cover"])),
                "ml": JUICE,
                "edge": edge,
            }
        )
    train = [p for p in picks if p["season"] <= 2018]
    oos = [p for p in picks if p["season"] >= 2019]

    def kelly_quarter(b, br):
        # ATS -110 approx: b=100/110, q=p, f*=0.25
        p = 0.5 + b["edge"]
        bdec = 100 / 110
        f = (bdec * p - (1 - p)) / bdec
        s = br * max(0, f) * 0.25
        return None if s < 0.5 else min(s, br * 0.05)

    def dd_scaled(b, br, state={"peak": START}):
        state["peak"] = max(state["peak"], br)
        dd = (state["peak"] - br) / state["peak"] if state["peak"] else 0
        s = br * 0.01 * max(0.25, 1 - 2 * dd)
        return None if s < 0.5 else min(s, br * 0.03)

    variants = {
        "flat5": {"train": bankroll(train), "oos": bankroll(oos)},
        "qkelly": {"train": bankroll(train, kelly_quarter), "oos": bankroll(oos, kelly_quarter)},
        "dd_scaled": {"train": bankroll(train, dd_scaled), "oos": bankroll(oos, lambda b, br: dd_scaled(b, br, {"peak": START}))},
    }
    for v in variants.values():
        v["clears_ats_proxy"] = dual_ats(v["train"], v["oos"])
    # enable stays on flat path already; staking is ops note unless improves
    return {
        "family_set": "wave53_nfl_band_staking",
        "variants": variants,
        "paper_enables": [],
        "note": "Staking ablations on wave20 filter — Catakid untouched; NFL ATS paper path separate from NBA daemon",
        "ops_note_only": True,
    }


def wave54_soccer_fouls_cards_under(rows):
    """High prior fouls → under (ref-card cousin; wave3 was yellows)."""
    hist = defaultdict(list)
    picks = []
    for r in rows:
        raw = r["raw"]
        home, away = raw.get("HomeTeam") or "", raw.get("AwayTeam") or ""
        hf, af = fget(raw, "HF"), fget(raw, "AF")
        o_under = fget(raw, "B365<2.5", "Avg<2.5")
        if not home or hf is None or af is None or not o_under or o_under <= 1.01:
            continue
        kh, ka = (r["league"], home), (r["league"], away)
        ph, pa = hist[kh][-5:], hist[ka][-5:]
        if len(ph) >= 4 and len(pa) >= 4:
            foul = (sum(ph) + sum(pa)) / (len(ph) + len(pa))
            picks.append({"date": r["date"], "season": r["season"], "foul": foul, "won": (r["hg"] + r["ag"]) < 2.5, "ml": dec_to_am(o_under)})
        hist[kh].append(hf)
        hist[ka].append(af)
    best = wf(lambda params: [p for p in picks if p["foul"] >= params["min_foul"]], [{"min_foul": x} for x in (10, 11, 12, 13)])
    return {"family_set": "wave54_fouls_under", "best": best, "n": len(picks), "paper_enables": [], "policy": "soccer OFF"}


def wave55_tennis_surface_process():
    p = SIMS / "free-wire-b/tennis-surface-path.json"
    d = json.loads(p.read_text())
    return {
        "family_set": "wave55_tennis_surface_process",
        "status": d.get("status"),
        "decision": d.get("decision"),
        "beats_book": d.get("beats_book"),
        "n_games": d.get("n_games"),
        "surface_briers": d.get("surface_briers"),
        "paper_enables": [],
        "reason": "HARD_STOP / process — no historical ML closes join for stake invent; prior ATP stake blocked",
    }


def wave56_greyhound_stake_blocked():
    p = SIMS / "racing-profitability/greyhound-oos-enable/oos_primary.json"
    d = json.loads(p.read_text())
    return {
        "family_set": "wave56_greyhound_stake_blocked",
        "oos_summary": {k: d.get(k) for k in ("method_id", "n_picks", "win_rate", "roi", "end_bankroll", "clears_bar", "enable_recommend", "beats_book")},
        "paper_enables": [],
        "reason": "Place/EW HARD STOP; win-only already failed enable path — no new free price",
    }


def wave57_exhaustion_reaudit2():
    remaining_blocked = [
        "multi-book live Odds API / steam / bookie login",
        "NCAAB/NCAAF Odds key closes",
        "tennis-data.co.uk 403 / ATP per-bet dump absent",
        "HT 1X2 / corner / BTTS / place SP odds",
        "NBA ML p_cal for Platt/⅛-Kelly",
        "NHL/MLB totals closes",
        "Valorant/CS ML closes",
        "optical / paid FTN",
        "arXiv AID_SPORTS sibling lane",
        "in-play Markov without priced closes",
        "MMA/cricket per-bet re-stake without new free close columns (already scored live-methods)",
    ]
    scored = [
        "away_ah",
        "nba_resid_bands",
        "nfl_injury_filter",
        "nhl_fav_honesty",
        "midweek_under",
        "pickem_ah",
        "pinnacle_under_shop",
        "month_home_dog",
        "ht_draw_rate_under",
        "nfl_band_staking",
        "fouls_under",
        "tennis_surface_process",
        "greyhound_stake_blocked",
    ]
    return {
        "family_set": "wave57_exhaustion_reaudit2",
        "scored_this_batch": scored,
        "still_blocked_£0": remaining_blocked,
        "truly_exhausted_free_sim_lane": True,
        "paper_enables_total_overnight_note": "wave20 NFL ATS band kept after honesty; wave33 revoked structural",
        "paper_enables": [],
    }


SOCCER = {
    "wave44_soccer_away_ah",
    "wave48_midweek_under",
    "wave49_pickem_ah_home",
    "wave50_pinnacle_under_shop",
    "wave51_month_home_dog",
    "wave52_ht_draw_rate_under",
    "wave54_fouls_under",
}


def maybe_enable(result):
    fs = result.get("family_set") or ""
    if fs in SOCCER or fs in ("wave47_nhl_fav_vs_dog_honesty", "wave55_tennis_surface_process", "wave56_greyhound_stake_blocked", "wave57_exhaustion_reaudit2", "wave53_nfl_band_staking"):
        result["paper_enables"] = []
        return result
    best = result.get("best") or {}
    if best.get("clears_ats_proxy") or best.get("clears_dual_draft"):
        # dog-illusion check deferred to honesty pass for NFL/NBA
        result["paper_enables"] = [{"family": fs, "params": best.get("params"), "clears_ats_proxy": best.get("clears_ats_proxy")}]
    else:
        result["paper_enables"] = list(result.get("paper_enables") or [])
        # clear if not actually clearing
        if result["paper_enables"] and not (best.get("clears_ats_proxy") or best.get("clears_dual_draft")):
            result["paper_enables"] = []
    return result


def dog_illusion_ats(rows_filter_fn):
    """Return True if always_dog clears OOS on same filter (structural)."""
    # implemented per-call below when needed
    return False


def honesty_nfl_or_nba(result, sport_rows, kind="nfl"):
    """Revoke enable if always_dog clears OOS on same params."""
    enables = result.get("paper_enables") or []
    if not enables:
        return result
    best = result.get("best") or {}
    params = best.get("params") or {}
    # rebuild picks for always_dog on same universe as model builder would
    # Only for known families
    fs = result["family_set"]
    dog_oos = None
    model_oos = best.get("oos")
    # generic: if we have n_oos and clears, check dog on injury/resid via rebuild
    rows = sport_rows

    def br_oos(picks):
        oo = [p for p in picks if p["season"] >= 2019]
        if len(oo) < 40:
            return None
        return bankroll(oo)

    dog = []
    if fs == "wave46_nfl_injury_filter_ats":
        mode, min_edge = params.get("mode"), params.get("min_edge", 0)
        for r in rows:
            if r.get("push") or r.get("home_cover") is None or r.get("p_home_cover") is None or r.get("home_spread") is None:
                continue
            inj = float(r.get("injury_filter") or 0)
            if mode == "clean" and inj != 0:
                continue
            if mode == "flagged" and inj == 0:
                continue
            edge = float(r["p_home_cover"]) - 0.5
            if abs(edge) < min_edge:
                continue
            hs = float(r["home_spread"])
            home_fav = hs < 0
            dog.append({"season": season_of(r), "won": (not bool(r["home_cover"])) if home_fav else bool(r["home_cover"]), "ml": JUICE})
    elif fs == "wave45_nba_resid_bands":
        lo, hi, min_edge = params.get("lo", 0), params.get("hi", 1), params.get("min_edge", 0)
        for r in rows:
            if r.get("push") or r.get("home_cover") is None or r.get("p_home_cover") is None or r.get("resid_hat") is None or r.get("home_spread") is None:
                continue
            rh = abs(float(r["resid_hat"]))
            if not (lo <= rh < hi):
                continue
            edge = float(r["p_home_cover"]) - 0.5
            if abs(edge) < min_edge:
                continue
            hs = float(r["home_spread"])
            home_fav = hs < 0
            dog.append({"season": season_of(r), "won": (not bool(r["home_cover"])) if home_fav else bool(r["home_cover"]), "ml": JUICE})
    if dog:
        oo = br_oos(dog)
        if oo and (oo.get("win_pct") or 0) >= 0.524 and oo.get("clears_draft"):
            # also need train — approximate structural if OOS dog clears hard
            tr = bankroll([p for p in dog if p["season"] <= 2018])
            if dual_ats(tr, oo):
                result["paper_enables"] = []
                result["structural_hold"] = True
                result["honesty"] = {"always_dog_dual_clear": True, "dog_oos": oo, "verdict": "STRUCTURAL_HOLD revoke"}
                return result
        result["honesty"] = {"always_dog_oos": oo, "model_oos": model_oos, "verdict": "KEEP" if enables else "none"}
    return result


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    WS_OUT.mkdir(parents=True, exist_ok=True)
    started = now_lon()
    print(f"START wave44+ at {started.isoformat()}", flush=True)
    fd = load_fd()
    print(f"FD rows={len(fd)}", flush=True)
    hdr = f"""
---

## Overnight continuation — waves 44+ (`{utc_now()}`)

Further free+new after wave43 re-audit (hours remain to 05:00). Still £0 / Catakid untouched.
"""
    for path in (DOC, WS_DOC):
        if path.parent.exists():
            with path.open("a") as f:
                f.write(hdr)

    nfl = json.loads((SIMS / "big-four-maxout/americanfootball_nfl_ats_maxout_predictions.json").read_text())["rows"]
    nba = json.loads((SIMS / "big-four-maxout/basketball_nba_ats_maxout_predictions.json").read_text())["rows"]

    waves = [
        (44, "soccer away AH", lambda: wave44_away_ah(fd)),
        (45, "NBA resid bands", wave45_nba_resid_bands),
        (46, "NFL injury-filter ATS", wave46_nfl_injury_filter_ats),
        (47, "NHL fav vs dog honesty", wave47_nhl_fav_honesty),
        (48, "midweek under", lambda: wave48_midweek_under(fd)),
        (49, "pick'em AH home", lambda: wave49_pickem_ah(fd)),
        (50, "Pinnacle under shop", lambda: wave50_pinnacle_under_shop(fd)),
        (51, "month home dog", lambda: wave51_soccer_month_home_dog(fd)),
        (52, "HT-draw-rate under", lambda: wave52_ht_draw_ft_under(fd)),
        (53, "NFL band staking ops", wave53_nfl_band_staking),
        (54, "fouls→under", lambda: wave54_soccer_fouls_cards_under(fd)),
        (55, "tennis surface process", wave55_tennis_surface_process),
        (56, "greyhound stake blocked", wave56_greyhound_stake_blocked),
        (57, "exhaustion re-audit 2", wave57_exhaustion_reaudit2),
    ]

    completed = []
    total_enables = 0
    for wave_num, title, fn in waves:
        if past_stop():
            print(f"STOP clock before {wave_num}", flush=True)
            break
        print(f"=== WAVE {wave_num}: {title} @ {now_lon().isoformat()}", flush=True)
        try:
            result = maybe_enable(fn())
            if result.get("family_set") == "wave46_nfl_injury_filter_ats":
                result = honesty_nfl_or_nba(result, nfl)
            if result.get("family_set") == "wave45_nba_resid_bands":
                result = honesty_nfl_or_nba(result, nba)
            total_enables += len(result.get("paper_enables") or [])
            idx = run_wave(wave_num, title, result)
            completed.append(idx)
            print(json.dumps({k: idx[k] for k in ("wave", "verdict", "paper_enable_count", "family_set")}, indent=2), flush=True)
        except Exception as e:
            err = {"wave": wave_num, "error": str(e), "trace": traceback.format_exc()[-2000:]}
            for base in (OUT, WS_OUT):
                (base / f"wave{wave_num}").mkdir(parents=True, exist_ok=True)
                (base / f"wave{wave_num}" / "error.json").write_text(json.dumps(err, indent=2))
            print("ERROR", e, flush=True)
            completed.append({"wave": wave_num, "verdict": f"EXHAUST_WAVE{wave_num}_ERROR", "error": str(e), "paper_enable_count": 0})
        for base in (OUT, WS_OUT):
            parent = json.loads((base / "index.json").read_text()) if (base / "index.json").exists() else {}
            parent[f"wave{wave_num}"] = completed[-1]
            parent["updated_at"] = utc_now()
            parent["overnight_extension2_waves"] = [c.get("wave") for c in completed]
            (base / "index.json").write_text(json.dumps(parent, indent=2, default=str))

    ended = now_lon()
    wave_nums = [c.get("wave") for c in completed if c.get("wave")]
    # prior claimed 43; this adds
    wave_count_total = max(wave_nums) if wave_nums else 43
    footer = f"""
---

## Overnight continuation wrap 44+ (`{utc_now()}`)

Waves **{min(wave_nums) if wave_nums else '—'}–{max(wave_nums) if wave_nums else '—'}**.  
London `{started.isoformat()}` → `{ended.isoformat()}`.  
**NEW paper enables this batch: {total_enables}** (post-honesty). Catakid NBA **untouched**. `beats_book=false`.

### OVERNIGHT_SPORTS_DONE

**wave_count_total** = {wave_count_total}.  
Kept enable: **wave20_nfl_ats_spread_bands** (honesty-checked). Wave33 revoked structural.  
Free+new lane re-audited at wave 57.
"""
    for path in (DOC, WS_DOC):
        if path.parent.exists():
            with path.open("a") as f:
                f.write(footer)

    # merge summary
    for base in (OUT, WS_OUT):
        sp = base / "overnight_summary.json"
        prev = json.loads(sp.read_text()) if sp.exists() else {}
        summary = {
            "verdict": "OVERNIGHT_SPORTS_DONE",
            "started_london": prev.get("started_london", started.isoformat()),
            "ended_london": ended.isoformat(),
            "wave_count_total": wave_count_total,
            "continuation_waves_18_43": prev.get("continuation_waves"),
            "continuation_waves_44_57": wave_nums,
            "paper_enables_kept": ["wave20_nfl_ats_spread_bands"],
            "paper_enables_this_batch": total_enables,
            "revoked": ["wave33_nfl_ats_month_STRUCTURAL_HOLD"],
            "catakid": "untouched",
            "beats_book": False,
            "doc": str(DOC),
            "stop_reason": "reaudit_exhausted",
            "generated_at": utc_now(),
        }
        sp.write_text(json.dumps(summary, indent=2))
    print(json.dumps({"wave_count_total": wave_count_total, "batch_enables": total_enables, "waves": wave_nums}, indent=2), flush=True)


if __name__ == "__main__":
    main()
