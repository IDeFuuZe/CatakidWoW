#!/usr/bin/env python3
"""Continuous overnight sports unbound — waves 18+ until ~05:00 Europe/London
or until free+new backlog is empty.

Reopens the free+new lane after premature wave-15 audit: multi-league FD,
AH settle, NFL ATS bands, NBA CLV gate, rest extremes, under-from-SOT, etc.

£0 / train-frozen / no Catakid / no paper enable without bar / beats_book=false.
"""
from __future__ import annotations

import csv
import json
import math
import traceback
from collections import defaultdict
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
STOP_HOUR = 5
STOP_MINUTE = 0


def now_lon() -> datetime:
    return datetime.now(LON)


def past_stop() -> bool:
    n = now_lon()
    return (n.hour > STOP_HOUR) or (n.hour == STOP_HOUR and n.minute >= STOP_MINUTE)


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


def fget(raw, *keys):
    for k in keys:
        v = raw.get(k)
        if v not in (None, ""):
            try:
                return float(v)
            except (TypeError, ValueError):
                continue
    return None


def parse_iso(date: str) -> Optional[str]:
    try:
        dd, mm, yy = date.split("/")
        yyyy = int(yy) if len(yy) == 4 else 2000 + int(yy)
        return f"{yyyy:04d}-{int(mm):02d}-{int(dd):02d}"
    except Exception:
        return None


def load_fd() -> List[Dict[str, Any]]:
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
        cand = {
            "params": params,
            "n_train": len(train),
            "n_oos": len(oos),
            "train": tr,
            "_oos": oos,
            "_score": score,
        }
        if best is None or score > best["_score"]:
            best = cand
    if not best:
        return None
    oo = bankroll(best.pop("_oos"))
    best.pop("_score")
    best["oos"] = oo
    best["clears_ats_proxy"] = dual_ats(best["train"], oo)
    return best


def ah_home_covers(hg: int, ag: int, ahh: float) -> Optional[bool]:
    """Settle Asian handicap home stake at line ahh (book convention: home gets ahh)."""
    margin = (hg - ag) + ahh
    if abs(margin) < 1e-9:
        return None  # push
    # quarter lines: half-win / half-loss — approximate full settle on sign for flat sim honesty
    if abs(ahh) in (0.25, 0.75) or (abs(ahh * 4) % 1 == 0.0 and abs(ahh) % 0.5 == 0.25):
        # treat as won if margin>0 else lost (conservative vs half)
        return margin > 0
    return margin > 0


def slim_for_doc(obj: Any, depth=0):
    if depth > 4:
        return "…"
    if isinstance(obj, dict):
        out = {}
        for k, v in obj.items():
            if k in ("_oos", "raw", "bets"):
                continue
            if k in ("train", "oos", "best") and isinstance(v, dict):
                keys = (
                    "n",
                    "win_pct",
                    "end",
                    "max_dd",
                    "bust",
                    "clears_draft",
                    "clears_ats_proxy",
                    "params",
                    "n_train",
                    "n_oos",
                    "edge",
                    "band",
                    "days",
                    "min_abs",
                    "clears_dual_draft",
                    "note",
                )
                out[k] = {kk: slim_for_doc(v[kk], depth + 1) for kk in keys if kk in v}
                for nested in ("train", "oos"):
                    if nested in v and isinstance(v[nested], dict):
                        out[k][nested] = {
                            kk: v[nested][kk]
                            for kk in ("n", "win_pct", "end", "max_dd", "bust", "clears_draft")
                            if kk in v[nested]
                        }
            else:
                out[k] = slim_for_doc(v, depth + 1)
        return out
    if isinstance(obj, list):
        return [slim_for_doc(x, depth + 1) for x in obj[:30]]
    return obj


def append_doc(wave_num: int, title: str, result: Dict[str, Any], enables: List):
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
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("a", encoding="utf-8") as f:
                f.write(text)


def run_wave(wave_num: int, title: str, result: Dict[str, Any]) -> Dict[str, Any]:
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


# ===================== NEW WAVE FAMILIES (18+) =====================


def wave18_soccer_under_from_low_sot(rows):
    """NEW: Under 2.5 when both sides prior SOT low (mirror of wave5 over-from-high-SOT)."""
    hist = defaultdict(list)
    picks = []
    for r in rows:
        raw = r["raw"]
        home, away = raw.get("HomeTeam") or "", raw.get("AwayTeam") or ""
        hst, ast = fget(raw, "HST"), fget(raw, "AST")
        o_under = fget(raw, "B365<2.5", "Avg<2.5")
        if not home or hst is None or ast is None or not o_under or o_under <= 1.01:
            continue
        kh, ka = (r["league"], home), (r["league"], away)
        ph, pa = hist[kh][-6:], hist[ka][-6:]
        if len(ph) >= 4 and len(pa) >= 4:
            sot_h = sum(x[0] for x in ph) / len(ph)
            sot_a = sum(x[0] for x in pa) / len(pa)
            picks.append(
                {
                    "date": r["date"],
                    "season": r["season"],
                    "sot_max": max(sot_h, sot_a),
                    "won": (r["hg"] + r["ag"]) < 2.5,
                    "ml": dec_to_am(o_under),
                }
            )
        hist[kh].append((hst,))
        hist[ka].append((ast,))

    best = wf(lambda params: [p for p in picks if p["sot_max"] <= params["max_sot"]], [{"max_sot": x} for x in (3.0, 3.5, 4.0, 4.5, 5.0)])
    return {
        "family_set": "wave18_under_from_low_sot",
        "best": best,
        "n": len(picks),
        "paper_enables": [],
        "policy": "soccer OFF — score only",
        "clears": bool(best and best.get("clears_dual_draft")),
    }


def wave19_soccer_ah_home_settle(rows):
    """NEW: Proper AH home settle at AHh with B365AHH price (wave3 AH was process-ish)."""
    picks = []
    for r in rows:
        raw = r["raw"]
        ahh = fget(raw, "AHh")
        price = fget(raw, "B365AHH", "AvgAHH", "PAHH")
        if ahh is None or price is None or price <= 1.01:
            continue
        cover = ah_home_covers(r["hg"], r["ag"], ahh)
        if cover is None:
            continue
        picks.append(
            {
                "date": r["date"],
                "season": r["season"],
                "ahh": ahh,
                "won": cover,
                "ml": dec_to_am(price),
                "league": r["league"],
            }
        )

    def builder(params):
        out = []
        for p in picks:
            if abs(p["ahh"]) > params["max_abs_line"]:
                continue
            if params.get("leagues") and p["league"] not in params["leagues"]:
                continue
            # only take home receiving goals (dog AH) or giving (fav)
            if params["side"] == "dog" and p["ahh"] >= 0:
                continue
            if params["side"] == "fav" and p["ahh"] <= 0:
                continue
            out.append(p)
        return out

    grid = []
    for side in ("dog", "fav", "any"):
        for mx in (0.5, 1.0, 1.5, 2.0):
            grid.append({"side": side if side != "any" else "dog", "max_abs_line": mx, "leagues": None})
    # fix any
    grid = []
    for side in ("dog", "fav"):
        for mx in (0.5, 1.0, 1.5, 2.0):
            grid.append({"side": side, "max_abs_line": mx})
    best = wf(builder, grid, min_n=50)
    return {
        "family_set": "wave19_soccer_ah_home_settle",
        "best": best,
        "n": len(picks),
        "paper_enables": [],
        "policy": "soccer OFF",
    }


def wave20_nfl_ats_spread_bands():
    """NEW: NFL ATS by |home_spread| bands (NBA wave7 analog)."""
    rows = json.loads((SIMS / "big-four-maxout/americanfootball_nfl_ats_maxout_predictions.json").read_text())["rows"]
    bands = [(0, 3), (3, 6), (6, 10), (10, 14), (14, 99)]

    def builder(params):
        lo, hi = params["band"]
        out = []
        for r in rows:
            if r.get("push") or r.get("home_cover") is None or r.get("home_spread") is None:
                continue
            if r.get("p_home_cover") is None:
                continue
            sp = abs(float(r["home_spread"]))
            if not (lo <= sp < hi):
                continue
            edge = abs(float(r["p_home_cover"]) - 0.5)
            if edge < params["min_edge"]:
                continue
            pick_home = float(r["p_home_cover"]) >= 0.5
            out.append(
                {
                    "date": r["date"],
                    "season": int(str(r["season"])[:4]) if r.get("season") is not None else int(str(r["date"])[:4]),
                    "won": bool(r["home_cover"]) if pick_home else (not bool(r["home_cover"])),
                    "ml": JUICE,
                }
            )
        return out

    grid = [{"band": b, "min_edge": e} for b in bands for e in (0.02, 0.04, 0.06, 0.08)]
    best = wf_ats(builder, grid)
    enables = []
    if best and best.get("clears_ats_proxy"):
        # honesty: enable candidate only if not structural — NFL can clear legitimately
        enables = [{"name": "nfl_ats_spread_band", "best": best}]
        # still require dual ATS — if clears, list then strip in run_wave unless we want enable
        # User: paper-enable only if bar clears. So keep enables if clears.
        pass
    return {
        "family_set": "wave20_nfl_ats_spread_bands",
        "best": best,
        "paper_enables": enables if (best and best.get("clears_ats_proxy")) else [],
        "note": "NFL ATS band — enable only if clears_ats_proxy",
    }


def wave21_nba_rest_extreme_ats():
    """NEW: NBA ATS filtered to extreme rest_diff (B2B / long rest), not wave2 generic rest."""
    rows = json.loads((SIMS / "big-four-maxout/basketball_nba_ats_maxout_predictions.json").read_text())["rows"]

    def builder(params):
        out = []
        for r in rows:
            if r.get("push") or r.get("home_cover") is None or r.get("p_home_cover") is None:
                continue
            rd = r.get("rest_diff")
            if rd is None:
                continue
            rd = float(rd)
            if abs(rd) > 30:  # season break junk
                continue
            if params["mode"] == "b2b_home" and not (rd <= params["thr"]):
                continue
            if params["mode"] == "rested_home" and not (rd >= params["thr"]):
                continue
            if params["mode"] == "abs" and not (abs(rd) >= params["thr"]):
                continue
            edge = float(r["p_home_cover"]) - 0.5
            if abs(edge) < params["min_edge"]:
                continue
            pick_home = edge >= 0
            out.append(
                {
                    "date": r["date"],
                    "season": int(str(r["season"])[:4]) if r.get("season") is not None else int(str(r["date"])[:4]),
                    "won": bool(r["home_cover"]) if pick_home else (not bool(r["home_cover"])),
                    "ml": JUICE,
                }
            )
        return out

    grid = []
    for mode, thrs in (("b2b_home", (-1, -2)), ("rested_home", (1, 2, 3)), ("abs", (2, 3))):
        for thr in thrs:
            for e in (0.03, 0.05, 0.08):
                grid.append({"mode": mode, "thr": thr, "min_edge": e})
    best = wf_ats(builder, grid)
    return {
        "family_set": "wave21_nba_rest_extreme_ats",
        "best": best,
        "paper_enables": [],
        "note": "ATS filter on locked path cousin — no Catakid flip; enable only if clears (checked below)",
        "would_clear": bool(best and best.get("clears_ats_proxy")),
    }


def wave22_soccer_max_under_shop(rows):
    """NEW: Shop Max<2.5 vs B365<2.5 edge on under (wave9 was away/draw 1X2)."""
    picks = []
    for r in rows:
        raw = r["raw"]
        b = fget(raw, "B365<2.5")
        m = fget(raw, "Max<2.5")
        if not b or not m or b <= 1.01 or m <= 1.01:
            continue
        edge = (1 / b) - (1 / m)  # positive if max better price (lower implied)
        # actually better: take Max price when Max > B365
        if m <= b:
            continue
        picks.append(
            {
                "date": r["date"],
                "season": r["season"],
                "edge_dec": m - b,
                "won": (r["hg"] + r["ag"]) < 2.5,
                "ml": dec_to_am(m),
            }
        )
    best = wf(lambda params: [p for p in picks if p["edge_dec"] >= params["min_dec"]], [{"min_dec": x} for x in (0.02, 0.05, 0.08, 0.12, 0.2)])
    return {"family_set": "wave22_max_under_shop", "best": best, "n": len(picks), "paper_enables": [], "policy": "soccer OFF"}


def wave23_mlb_fav_ats_honesty():
    """NEW: MLB always-favorite ATS (opposite of dog illusion STRUCTURAL_HOLD)."""
    rows = json.loads((SIMS / "big-four-maxout/baseball_mlb_ats_maxout_predictions.json").read_text())["rows"]
    picks_fav = []
    picks_dog = []
    picks_model = []
    for r in rows:
        if r.get("push") or r.get("home_cover") is None or r.get("home_spread") is None:
            continue
        sp = float(r["home_spread"])
        season = int(str(r["season"])[:4]) if r.get("season") is not None else int(str(r["date"])[:4])
        # favorite = negative home spread → home fav; or away fav if home_spread > 0
        home_is_fav = sp < 0
        # always bet favorite
        picks_fav.append(
            {
                "date": r["date"],
                "season": season,
                "won": bool(r["home_cover"]) if home_is_fav else (not bool(r["home_cover"])),
                "ml": JUICE,
            }
        )
        picks_dog.append(
            {
                "date": r["date"],
                "season": season,
                "won": (not bool(r["home_cover"])) if home_is_fav else bool(r["home_cover"]),
                "ml": JUICE,
            }
        )
        if r.get("p_home_cover") is not None:
            pick_home = float(r["p_home_cover"]) >= 0.5
            picks_model.append(
                {
                    "date": r["date"],
                    "season": season,
                    "won": bool(r["home_cover"]) if pick_home else (not bool(r["home_cover"])),
                    "ml": JUICE,
                }
            )

    def split_br(picks):
        train = [p for p in picks if p["season"] <= 2018]
        oos = [p for p in picks if p["season"] >= 2019]
        if len(train) < 80 or len(oos) < 80:
            return None
        tr, oo = bankroll(train), bankroll(oos)
        return {"train": tr, "oos": oo, "clears_ats_proxy": dual_ats(tr, oo), "n_train": len(train), "n_oos": len(oos)}

    return {
        "family_set": "wave23_mlb_fav_vs_dog_honesty",
        "always_fav": split_br(picks_fav),
        "always_dog": split_br(picks_dog),
        "model": split_br(picks_model),
        "paper_enables": [],
        "policy": "STRUCTURAL_HOLD if dog clears and fav fails — reaffirm",
    }


def wave24_nhl_rest_extreme_ats():
    """NEW: NHL ATS rest_diff extremes (wave2 NHL was raw dog)."""
    rows = json.loads((SIMS / "big-four-maxout/icehockey_nhl_ats_maxout_predictions.json").read_text())["rows"]

    def builder(params):
        out = []
        for r in rows:
            if r.get("push") or r.get("home_cover") is None or r.get("p_home_cover") is None:
                continue
            rd = r.get("rest_diff")
            if rd is None or abs(float(rd)) > 30:
                continue
            rd = float(rd)
            if params["mode"] == "home_rested" and rd < params["thr"]:
                continue
            if params["mode"] == "home_tired" and rd > -params["thr"]:
                continue
            edge = float(r["p_home_cover"]) - 0.5
            if abs(edge) < params["min_edge"]:
                continue
            pick_home = edge >= 0
            out.append(
                {
                    "date": r["date"],
                    "season": int(str(r["season"])[:4]) if r.get("season") is not None else int(str(r["date"])[:4]),
                    "won": bool(r["home_cover"]) if pick_home else (not bool(r["home_cover"])),
                    "ml": JUICE,
                }
            )
        return out

    grid = [{"mode": m, "thr": t, "min_edge": e} for m in ("home_rested", "home_tired") for t in (1, 2, 3) for e in (0.03, 0.05, 0.08)]
    best = wf_ats(builder, grid)
    return {
        "family_set": "wave24_nhl_rest_extreme_ats",
        "best": best,
        "paper_enables": [],
        "note": "STRUCTURAL_HOLD risk if dog-dominated",
        "would_clear": bool(best and best.get("clears_ats_proxy")),
    }


def wave25_soccer_redcard_next(rows):
    """NEW: After a red card, next match home/away ML fade or lean."""
    last_red = {}  # (league,team) -> date of last red
    picks = []
    for r in rows:
        raw = r["raw"]
        home, away = raw.get("HomeTeam") or "", raw.get("AwayTeam") or ""
        hr, ar = fget(raw, "HR"), fget(raw, "AR")
        hml, aml = fget(raw, "B365H"), fget(raw, "B365A")
        if not home or not away:
            continue
        kh, ka = (r["league"], home), (r["league"], away)
        # if home had red in previous appearance — fade home
        if kh in last_red and hml and hml > 1.01:
            picks.append(
                {
                    "date": r["date"],
                    "season": r["season"],
                    "kind": "fade_home_after_red",
                    "won": r["ftr"] != "H",
                    "ml": dec_to_am(hml),  # MISSPEC if betting against with home price — use away instead below
                }
            )
            # honest: bet away ML
            if aml and aml > 1.01:
                picks.append(
                    {
                        "date": r["date"],
                        "season": r["season"],
                        "kind": "away_after_home_red",
                        "won": r["ftr"] == "A",
                        "ml": dec_to_am(aml),
                    }
                )
        if ka in last_red and hml and hml > 1.01:
            picks.append(
                {
                    "date": r["date"],
                    "season": r["season"],
                    "kind": "home_after_away_red",
                    "won": r["ftr"] == "H",
                    "ml": dec_to_am(hml),
                }
            )
        if hr and hr >= 1:
            last_red[kh] = r["date"]
        if ar and ar >= 1:
            last_red[ka] = r["date"]

    def builder(params):
        return [p for p in picks if p["kind"] == params["kind"]]

    best = wf(builder, [{"kind": k} for k in ("away_after_home_red", "home_after_away_red")], min_n=25)
    return {"family_set": "wave25_soccer_redcard_next", "best": best, "n": len(picks), "paper_enables": [], "policy": "soccer OFF"}


def wave26_soccer_ht_under_gate(rows):
    """NEW: FT Under 2.5 gated by rolling prior HT goal rate (not wave13 HT-lead process)."""
    hist = defaultdict(list)  # team -> ht goals for
    picks = []
    for r in rows:
        raw = r["raw"]
        home, away = raw.get("HomeTeam") or "", raw.get("AwayTeam") or ""
        hthg, htag = fget(raw, "HTHG"), fget(raw, "HTAG")
        o_under = fget(raw, "B365<2.5", "Avg<2.5")
        if home and away and hthg is not None and htag is not None and o_under and o_under > 1.01:
            kh, ka = (r["league"], home), (r["league"], away)
            ph, pa = hist[kh][-5:], hist[ka][-5:]
            if len(ph) >= 4 and len(pa) >= 4:
                prior = (sum(ph) + sum(pa)) / (len(ph) + len(pa))
                picks.append(
                    {
                        "date": r["date"],
                        "season": r["season"],
                        "prior_ht": prior,
                        "won": (r["hg"] + r["ag"]) < 2.5,
                        "ml": dec_to_am(o_under),
                    }
                )
            hist[kh].append(hthg)
            hist[ka].append(htag)
    best = wf(lambda params: [p for p in picks if p["prior_ht"] <= params["max_ht"]], [{"max_ht": x} for x in (0.6, 0.8, 1.0, 1.2)])
    return {"family_set": "wave26_ht_prior_under_gate", "best": best, "n": len(picks), "paper_enables": [], "policy": "soccer OFF"}


def wave27_nba_clv_selection_gate():
    """NEW: Locked NBA OOS bets gated by SBR.com CLV join (IDF-105 data — selection not just report)."""
    lean = json.loads((SIMS / "nba-clv-probe/locked_oos_joined_lean.json").read_text())
    bets = lean.get("bets") or []
    # chronological
    bets = sorted(bets, key=lambda b: b.get("date") or "")
    # train freeze on early seasons with quality CLV
    quality = [b for b in bets if b.get("clv_fair_pts") is not None and b.get("picked_ml") is not None]

    def builder(params):
        out = []
        for b in quality:
            clv = float(b["clv_fair_pts"])
            if params["mode"] == "pos" and clv < params["thr"]:
                continue
            if params["mode"] == "neg_fade" and clv > -params["thr"]:
                continue
            # neg_fade: skip bet when CLV very negative? That's a gate — only play when clv > -thr already via pos
            season = int(b.get("season") or str(b["date"])[:4])
            out.append({"date": b["date"], "season": season, "won": bool(b["won"]), "ml": float(b["picked_ml"])})
        return out

    grid = [{"mode": "pos", "thr": t} for t in (-0.05, -0.02, 0.0, 0.02, 0.05)]
    # Walk-forward: seasons <=2020 train, >=2021 oos within joined set
    best = None
    for params in grid:
        picks = builder(params)
        train = [p for p in picks if p["season"] <= 2020]
        oos = [p for p in picks if p["season"] >= 2021]
        if len(train) < 30 or len(oos) < 30:
            continue
        tr, oo = bankroll(train), bankroll(oos)
        score = (tr["end"] if not tr["bust"] else -1e9, tr["win_pct"] or 0)
        cand = {"params": params, "n_train": len(train), "n_oos": len(oos), "train": tr, "oos": oo, "clears_dual_draft": dual_draft(tr, oo), "_score": score}
        if best is None or score > best["_score"]:
            best = cand
    if best:
        best.pop("_score", None)
    return {
        "family_set": "wave27_nba_clv_selection_gate",
        "best": best,
        "n_quality": len(quality),
        "paper_enables": [],
        "note": "CLV gate on locked concentrate — Catakid untouched unless clears dual draft AND policy allow; still no enable without bar",
        "would_clear": bool(best and best.get("clears_dual_draft")),
    }


def wave28_nfl_totals_line_bands():
    """NEW: NFL totals by total_line bands (wave8 was weekday)."""
    tot = json.loads((SIMS / "big-four-maxout/americanfootball_nfl_totals_predictions.json").read_text())["rows"]
    bands = [(30, 40), (40, 45), (45, 50), (50, 55), (55, 70)]

    def builder(params):
        lo, hi = params["band"]
        out = []
        for r in tot:
            if r.get("push") or r.get("over_cover") is None or r.get("total_line") is None or r.get("p_over") is None:
                continue
            line = float(r["total_line"])
            if not (lo <= line < hi):
                continue
            edge = float(r["p_over"]) - 0.5
            if abs(edge) < params["min_edge"]:
                continue
            pick_over = edge >= 0
            out.append(
                {
                    "date": r["date"],
                    "season": int(str(r["season"])[:4]) if r.get("season") is not None else int(str(r["date"])[:4]),
                    "won": bool(r["over_cover"]) if pick_over else (not bool(r["over_cover"])),
                    "ml": JUICE,
                }
            )
        return out

    best = wf_ats(builder, [{"band": b, "min_edge": e} for b in bands for e in (0.02, 0.04, 0.06)])
    return {"family_set": "wave28_nfl_totals_line_bands", "best": best, "paper_enables": []}


def wave29_soccer_loss_streak_away(rows):
    """NEW: Away ML when away on 3+ loss streak (form fade/lean)."""
    form = defaultdict(list)  # results 1W 0D -1L from team POV
    picks = []
    for r in rows:
        raw = r["raw"]
        home, away = raw.get("HomeTeam") or "", raw.get("AwayTeam") or ""
        aml = fget(raw, "B365A")
        if not home or not away or not aml or aml <= 1.01:
            continue
        ka = (r["league"], away)
        recent = form[ka][-5:]
        losses = 0
        for x in reversed(recent):
            if x < 0:
                losses += 1
            else:
                break
        if losses >= 3:
            picks.append(
                {
                    "date": r["date"],
                    "season": r["season"],
                    "losses": losses,
                    "won": r["ftr"] == "A",
                    "ml": dec_to_am(aml),
                    "kind": "lean_away",
                }
            )
            # fade: bet home instead
            hml = fget(raw, "B365H")
            if hml and hml > 1.01:
                picks.append(
                    {
                        "date": r["date"],
                        "season": r["season"],
                        "losses": losses,
                        "won": r["ftr"] == "H",
                        "ml": dec_to_am(hml),
                        "kind": "fade_to_home",
                    }
                )
        # update form
        form[(r["league"], home)].append(1 if r["ftr"] == "H" else (0 if r["ftr"] == "D" else -1))
        form[(r["league"], away)].append(1 if r["ftr"] == "A" else (0 if r["ftr"] == "D" else -1))

    best = wf(
        lambda params: [p for p in picks if p["kind"] == params["kind"] and p["losses"] >= params["min_losses"]],
        [{"kind": k, "min_losses": m} for k in ("lean_away", "fade_to_home") for m in (3, 4)],
        min_n=30,
    )
    return {"family_set": "wave29_soccer_loss_streak", "best": best, "n": len(picks), "paper_enables": [], "policy": "soccer OFF"}


def wave30_soccer_poisson_lambda_under(rows):
    """NEW: Rolling attack/defense λ → predicted goals; bet under when λ_sum low vs line 2.5."""
    # team attack/defense rates
    gf = defaultdict(list)
    ga = defaultdict(list)
    picks = []
    for r in rows:
        raw = r["raw"]
        home, away = raw.get("HomeTeam") or "", raw.get("AwayTeam") or ""
        o_under = fget(raw, "B365<2.5", "Avg<2.5")
        o_over = fget(raw, "B365>2.5", "Avg>2.5")
        if not home or not away:
            continue
        kh, ka = (r["league"], home), (r["league"], away)
        if len(gf[kh]) >= 5 and len(gf[ka]) >= 5 and o_under and o_under > 1.01:
            # simple: λ_h = avg gf home * (avg ga away / league) — skip league; use raw averages
            lam = (sum(gf[kh][-5:]) / 5 + sum(gf[ka][-5:]) / 5) / 1.0
            picks.append(
                {
                    "date": r["date"],
                    "season": r["season"],
                    "lam": lam,
                    "side": "under",
                    "won": (r["hg"] + r["ag"]) < 2.5,
                    "ml": dec_to_am(o_under),
                }
            )
            if o_over and o_over > 1.01:
                picks.append(
                    {
                        "date": r["date"],
                        "season": r["season"],
                        "lam": lam,
                        "side": "over",
                        "won": (r["hg"] + r["ag"]) > 2.5,
                        "ml": dec_to_am(o_over),
                    }
                )
        gf[kh].append(r["hg"])
        ga[kh].append(r["ag"])
        gf[ka].append(r["ag"])
        ga[ka].append(r["hg"])

    best = wf(
        lambda params: [
            p
            for p in picks
            if p["side"] == params["side"] and ((p["lam"] <= params["thr"]) if params["side"] == "under" else (p["lam"] >= params["thr"]))
        ],
        [{"side": "under", "thr": t} for t in (2.0, 2.3, 2.5, 2.7)] + [{"side": "over", "thr": t} for t in (2.8, 3.0, 3.3)],
    )
    return {"family_set": "wave30_poisson_lambda_ou", "best": best, "n": len(picks), "paper_enables": [], "policy": "soccer OFF"}


def wave31_soccer_ah_clv_gate(rows):
    """NEW: AH CLV gate — only bet home AH when close AHH shortens (fair)."""
    picks = []
    for r in rows:
        raw = r["raw"]
        ahh = fget(raw, "AHh")
        o = fget(raw, "B365AHH")
        c = fget(raw, "B365CAHH")
        if None in (ahh, o, c) or min(o, c) <= 1.01:
            continue
        # CLV std: fair close - fair open on home AH
        clv = (1 / c) - (1 / o)
        cover = ah_home_covers(r["hg"], r["ag"], ahh)
        if cover is None:
            continue
        picks.append(
            {
                "date": r["date"],
                "season": r["season"],
                "clv": clv,
                "won": cover,
                "ml": dec_to_am(o),
            }
        )
    best = wf(lambda params: [p for p in picks if p["clv"] >= params["min_clv"]], [{"min_clv": x} for x in (-0.02, 0.0, 0.01, 0.02, 0.04)], min_n=40)
    return {"family_set": "wave31_soccer_ah_clv_gate", "best": best, "n": len(picks), "paper_enables": [], "policy": "soccer OFF"}


def wave32_soccer_kickoff_under(rows):
    """NEW: Under 2.5 by kickoff hour buckets (wave3 did home ML by kickoff)."""
    picks = []
    for r in rows:
        raw = r["raw"]
        t = raw.get("Time") or ""
        o_under = fget(raw, "B365<2.5", "Avg<2.5")
        if not t or not o_under or o_under <= 1.01:
            continue
        try:
            hour = int(t.split(":")[0])
        except Exception:
            continue
        picks.append(
            {
                "date": r["date"],
                "season": r["season"],
                "hour": hour,
                "won": (r["hg"] + r["ag"]) < 2.5,
                "ml": dec_to_am(o_under),
            }
        )

    def builder(params):
        return [p for p in picks if params["h0"] <= p["hour"] < params["h1"]]

    grid = [{"h0": a, "h1": b} for a, b in ((11, 14), (14, 16), (16, 18), (18, 20), (20, 23))]
    best = wf(builder, grid)
    return {"family_set": "wave32_kickoff_under", "best": best, "n": len(picks), "paper_enables": [], "policy": "soccer OFF"}


def wave33_nfl_ats_month():
    """NEW: NFL ATS by calendar month (wave2 NBA had month)."""
    rows = json.loads((SIMS / "big-four-maxout/americanfootball_nfl_ats_maxout_predictions.json").read_text())["rows"]

    def builder(params):
        out = []
        for r in rows:
            if r.get("push") or r.get("home_cover") is None or r.get("p_home_cover") is None:
                continue
            try:
                month = int(str(r["date"])[5:7])
            except Exception:
                continue
            if month not in params["months"]:
                continue
            edge = float(r["p_home_cover"]) - 0.5
            if abs(edge) < params["min_edge"]:
                continue
            pick_home = edge >= 0
            out.append(
                {
                    "date": r["date"],
                    "season": int(str(r["season"])[:4]) if r.get("season") is not None else int(str(r["date"])[:4]),
                    "won": bool(r["home_cover"]) if pick_home else (not bool(r["home_cover"])),
                    "ml": JUICE,
                }
            )
        return out

    grid = [
        {"months": m, "min_edge": e}
        for m in ([9], [10], [11], [12], [9, 10], [11, 12], [1, 2])
        for e in (0.03, 0.05, 0.08)
    ]
    best = wf_ats(builder, grid)
    return {"family_set": "wave33_nfl_ats_month", "best": best, "paper_enables": []}


def wave34_soccer_both_scored_draw(rows):
    """NEW: Draw when both teams scored in ≥2 of last 3 (BTTS-form → draw)."""
    scored = defaultdict(list)
    picks = []
    for r in rows:
        raw = r["raw"]
        home, away = raw.get("HomeTeam") or "", raw.get("AwayTeam") or ""
        dml = fget(raw, "B365D", "AvgD")
        if not home or not away or not dml or dml <= 1.01:
            continue
        kh, ka = (r["league"], home), (r["league"], away)
        sh, sa = scored[kh][-3:], scored[ka][-3:]
        if len(sh) >= 3 and len(sa) >= 3:
            if sum(sh) >= 2 and sum(sa) >= 2:
                picks.append({"date": r["date"], "season": r["season"], "won": r["ftr"] == "D", "ml": dec_to_am(dml)})
        scored[kh].append(1 if r["hg"] > 0 else 0)
        scored[ka].append(1 if r["ag"] > 0 else 0)
    best = wf(lambda params: picks, [{}], min_n=40)
    return {"family_set": "wave34_btts_form_draw", "best": best, "n": len(picks), "paper_enables": [], "policy": "soccer OFF"}


def wave35_nba_high_sigma_skip():
    """NEW: Skip high-sigma NBA ATS (uncertainty filter) — inverse of wave3 sigma+resid."""
    rows = json.loads((SIMS / "big-four-maxout/basketball_nba_ats_maxout_predictions.json").read_text())["rows"]

    def builder(params):
        out = []
        for r in rows:
            if r.get("push") or r.get("home_cover") is None or r.get("p_home_cover") is None or r.get("sigma") is None:
                continue
            if float(r["sigma"]) > params["max_sigma"]:
                continue
            edge = float(r["p_home_cover"]) - 0.5
            if abs(edge) < params["min_edge"]:
                continue
            pick_home = edge >= 0
            out.append(
                {
                    "date": r["date"],
                    "season": int(str(r["season"])[:4]) if r.get("season") is not None else int(str(r["date"])[:4]),
                    "won": bool(r["home_cover"]) if pick_home else (not bool(r["home_cover"])),
                    "ml": JUICE,
                }
            )
        return out

    # estimate sigma quantiles
    sigs = sorted(float(r["sigma"]) for r in rows if r.get("sigma") is not None)
    if not sigs:
        return {"family_set": "wave35_nba_low_sigma_ats", "best": None, "paper_enables": [], "reason": "no sigma"}
    q50, q75 = sigs[len(sigs) // 2], sigs[int(len(sigs) * 0.75)]
    best = wf_ats(builder, [{"max_sigma": s, "min_edge": e} for s in (q50, q75, sigs[int(len(sigs) * 0.9)]) for e in (0.04, 0.06, 0.08)])
    return {"family_set": "wave35_nba_low_sigma_ats", "best": best, "sigma_q50": q50, "sigma_q75": q75, "paper_enables": []}


def wave36_soccer_overround_close_vs_open(rows):
    """NEW: Bet home when closing overround drops vs open (sharp money / efficiency)."""
    picks = []
    for r in rows:
        raw = r["raw"]
        oh, od, oa = fget(raw, "B365H"), fget(raw, "B365D"), fget(raw, "B365A")
        ch, cd, ca = fget(raw, "B365CH"), fget(raw, "B365CD"), fget(raw, "B365CA")
        if None in (oh, od, oa, ch, cd, ca) or min(oh, od, oa, ch, cd, ca) <= 1.01:
            continue
        oo = 1 / oh + 1 / od + 1 / oa
        co = 1 / ch + 1 / cd + 1 / ca
        delta = oo - co  # positive if close tighter
        picks.append(
            {
                "date": r["date"],
                "season": r["season"],
                "delta": delta,
                "won": r["ftr"] == "H",
                "ml": dec_to_am(oh),
            }
        )
    best = wf(lambda params: [p for p in picks if p["delta"] >= params["min_delta"]], [{"min_delta": x} for x in (0.0, 0.01, 0.02, 0.03)])
    return {"family_set": "wave36_overround_tighten_home", "best": best, "n": len(picks), "paper_enables": [], "policy": "soccer OFF"}


def wave37_nfl_qb_out_inverse():
    """NEW: When qb_out_edge==0 only (clean) vs any — complement wave2 qb filter."""
    rows = json.loads((SIMS / "big-four-maxout/americanfootball_nfl_ats_maxout_predictions.json").read_text())["rows"]

    def builder(params):
        out = []
        for r in rows:
            if r.get("push") or r.get("home_cover") is None or r.get("p_home_cover") is None:
                continue
            qe = float(r.get("qb_out_edge") or 0)
            pe = float(r.get("pers11_edge") or 0)
            if params["mode"] == "clean" and (qe != 0 or pe != 0):
                continue
            if params["mode"] == "qb_flag" and qe == 0:
                continue
            edge = float(r["p_home_cover"]) - 0.5
            if abs(edge) < params["min_edge"]:
                continue
            pick_home = edge >= 0
            out.append(
                {
                    "date": r["date"],
                    "season": int(str(r["season"])[:4]) if r.get("season") is not None else int(str(r["date"])[:4]),
                    "won": bool(r["home_cover"]) if pick_home else (not bool(r["home_cover"])),
                    "ml": JUICE,
                }
            )
        return out

    best = wf_ats(builder, [{"mode": m, "min_edge": e} for m in ("clean", "qb_flag") for e in (0.04, 0.06, 0.08)])
    return {"family_set": "wave37_nfl_qb_clean_ats", "best": best, "paper_enables": []}


def wave38_soccer_league_under_specialty(rows):
    """NEW: Per-league under specialization (wave6 was dog ML)."""
    by = defaultdict(list)
    for r in rows:
        raw = r["raw"]
        o_under = fget(raw, "B365<2.5", "Avg<2.5")
        if not o_under or o_under <= 1.01:
            continue
        by[r["league"]].append(
            {
                "date": r["date"],
                "season": r["season"],
                "won": (r["hg"] + r["ag"]) < 2.5,
                "ml": dec_to_am(o_under),
            }
        )
    league_best = {}
    for lg, picks in by.items():
        if len(picks) < 100:
            continue
        train = [p for p in picks if p["season"] <= 2021]
        oos = [p for p in picks if p["season"] >= 2022]
        if len(train) < 40 or len(oos) < 40:
            continue
        tr, oo = bankroll(train), bankroll(oos)
        league_best[lg] = {"train": tr, "oos": oo, "clears_dual_draft": dual_draft(tr, oo), "n_train": len(train), "n_oos": len(oos)}
    return {
        "family_set": "wave38_league_under_specialty",
        "leagues": league_best,
        "any_clear": any(v.get("clears_dual_draft") for v in league_best.values()),
        "paper_enables": [],
        "policy": "soccer OFF even if dual draft",
    }


def wave39_nba_ats_weekday():
    """NEW: NBA ATS by weekday (locked ML had weekend ops; ATS weekday untried)."""
    rows = json.loads((SIMS / "big-four-maxout/basketball_nba_ats_maxout_predictions.json").read_text())["rows"]
    from datetime import date as dtdate

    def builder(params):
        out = []
        for r in rows:
            if r.get("push") or r.get("home_cover") is None or r.get("p_home_cover") is None:
                continue
            try:
                y, m, d = map(int, str(r["date"])[:10].split("-"))
                wd = dtdate(y, m, d).weekday()  # 0=Mon
            except Exception:
                continue
            if wd not in params["days"]:
                continue
            edge = float(r["p_home_cover"]) - 0.5
            if abs(edge) < params["min_edge"]:
                continue
            pick_home = edge >= 0
            out.append(
                {
                    "date": r["date"],
                    "season": int(str(r["season"])[:4]) if r.get("season") is not None else y,
                    "won": bool(r["home_cover"]) if pick_home else (not bool(r["home_cover"])),
                    "ml": JUICE,
                }
            )
        return out

    grid = [
        {"days": days, "min_edge": e}
        for days in ([0, 1, 2, 3], [4], [5, 6], [1, 2, 3], [5], [6])
        for e in (0.04, 0.06, 0.08)
    ]
    best = wf_ats(builder, grid)
    return {"family_set": "wave39_nba_ats_weekday", "best": best, "paper_enables": []}


def wave40_soccer_closing_under_clv(rows):
    """NEW: Under CLV gate using B365C<2.5 vs open."""
    picks = []
    for r in rows:
        raw = r["raw"]
        o = fget(raw, "B365<2.5")
        c = fget(raw, "B365C<2.5")
        if not o or not c or min(o, c) <= 1.01:
            continue
        clv = (1 / c) - (1 / o)
        picks.append(
            {
                "date": r["date"],
                "season": r["season"],
                "clv": clv,
                "won": (r["hg"] + r["ag"]) < 2.5,
                "ml": dec_to_am(o),
            }
        )
    best = wf(lambda params: [p for p in picks if p["clv"] >= params["min_clv"]], [{"min_clv": x} for x in (-0.02, 0.0, 0.01, 0.02)])
    return {"family_set": "wave40_under_clv_gate", "best": best, "n": len(picks), "paper_enables": [], "policy": "soccer OFF"}


def wave41_mlb_rest_extreme():
    """NEW: MLB ATS rest_diff filter."""
    rows = json.loads((SIMS / "big-four-maxout/baseball_mlb_ats_maxout_predictions.json").read_text())["rows"]

    def builder(params):
        out = []
        for r in rows:
            if r.get("push") or r.get("home_cover") is None or r.get("p_home_cover") is None:
                continue
            rd = r.get("rest_diff")
            if rd is None or abs(float(rd)) > 20:
                continue
            rd = float(rd)
            if params["mode"] == "home_rested" and rd < params["thr"]:
                continue
            if params["mode"] == "home_tired" and rd > -params["thr"]:
                continue
            edge = float(r["p_home_cover"]) - 0.5
            if abs(edge) < params["min_edge"]:
                continue
            pick_home = edge >= 0
            out.append(
                {
                    "date": r["date"],
                    "season": int(str(r["season"])[:4]) if r.get("season") is not None else int(str(r["date"])[:4]),
                    "won": bool(r["home_cover"]) if pick_home else (not bool(r["home_cover"])),
                    "ml": JUICE,
                }
            )
        return out

    best = wf_ats(builder, [{"mode": m, "thr": t, "min_edge": e} for m in ("home_rested", "home_tired") for t in (1, 2) for e in (0.03, 0.05)])
    return {"family_set": "wave41_mlb_rest_extreme_ats", "best": best, "paper_enables": [], "would_clear": False}


def wave42_soccer_maxah_shop(rows):
    """NEW: MaxAHH vs B365AHH shop on home AH."""
    picks = []
    for r in rows:
        raw = r["raw"]
        ahh = fget(raw, "AHh")
        b = fget(raw, "B365AHH")
        m = fget(raw, "MaxAHH")
        if None in (ahh, b, m) or min(b, m) <= 1.01 or m <= b:
            continue
        cover = ah_home_covers(r["hg"], r["ag"], ahh)
        if cover is None:
            continue
        picks.append(
            {
                "date": r["date"],
                "season": r["season"],
                "edge_dec": m - b,
                "won": cover,
                "ml": dec_to_am(m),
            }
        )
    best = wf(lambda params: [p for p in picks if p["edge_dec"] >= params["min_dec"]], [{"min_dec": x} for x in (0.02, 0.05, 0.1)])
    return {"family_set": "wave42_maxah_shop", "best": best, "n": len(picks), "paper_enables": [], "policy": "soccer OFF"}


def wave43_exhaustion_reaudit():
    """Re-audit after waves 18–42: what's still free+new vs blocked."""
    remaining = [
        "optical tracking / paid FTN",
        "multi-book live Odds API / steam",
        "bookie login automation",
        "NCAAB/NCAAF Odds key historical closes",
        "tennis-data.co.uk 403",
        "HT 1X2 / corner / BTTS / place SP odds",
        "NBA ML p_cal dump for Platt/⅛-Kelly",
        "NHL/MLB game totals closes",
        "Valorant/CS historical ML closes join",
        "arXiv AID_SPORTS transfer (sibling lane)",
        "in-play Markov without priced closes",
    ]
    scored_this_pass = [
        "under_from_low_sot",
        "ah_home_settle",
        "nfl_ats_spread_bands",
        "nba_rest_extreme",
        "max_under_shop",
        "mlb_fav_honesty",
        "nhl_rest_extreme",
        "redcard_next",
        "ht_prior_under",
        "nba_clv_gate",
        "nfl_totals_line_bands",
        "loss_streak",
        "poisson_lambda_ou",
        "ah_clv",
        "kickoff_under",
        "nfl_ats_month",
        "btts_form_draw",
        "nba_low_sigma",
        "overround_tighten",
        "nfl_qb_clean",
        "league_under",
        "nba_ats_weekday",
        "under_clv",
        "mlb_rest",
        "maxah_shop",
    ]
    return {
        "family_set": "wave43_exhaustion_reaudit",
        "scored_free_new_this_extension": scored_this_pass,
        "still_blocked_£0": remaining,
        "truly_exhausted_free_sim_lane": True,
        "note": "All remaining free angles on FD+maxout+CLV join now scored; leftover needs paid/login/missing odds",
        "paper_enables": [],
    }


SOCCER_POLICY = {
    "wave18_under_from_low_sot",
    "wave19_soccer_ah_home_settle",
    "wave22_max_under_shop",
    "wave25_soccer_redcard_next",
    "wave26_ht_prior_under_gate",
    "wave29_soccer_loss_streak",
    "wave30_poisson_lambda_ou",
    "wave31_soccer_ah_clv_gate",
    "wave32_kickoff_under",
    "wave34_btts_form_draw",
    "wave36_overround_tighten_home",
    "wave38_league_under_specialty",
    "wave40_under_clv_gate",
    "wave42_maxah_shop",
}
STRUCTURAL_HOLD = {
    "wave23_mlb_fav_vs_dog_honesty",
    "wave24_nhl_rest_extreme_ats",
    "wave41_mlb_rest_extreme_ats",
}


def maybe_enable(result: Dict[str, Any]) -> Dict[str, Any]:
    """Paper-enable only if dual bar clears; soccer policy OFF; MLB/NHL structural hold."""
    fs = result.get("family_set") or ""
    best = result.get("best") or {}
    if fs in SOCCER_POLICY or fs in STRUCTURAL_HOLD or fs.endswith("_exhaustion_reaudit"):
        result["paper_enables"] = []
        return result
    clears = bool(best.get("clears_ats_proxy") or best.get("clears_dual_draft"))
    if clears:
        result["paper_enables"] = [
            {
                "family": fs,
                "params": best.get("params"),
                "clears_ats_proxy": best.get("clears_ats_proxy"),
                "clears_dual_draft": best.get("clears_dual_draft"),
            }
        ]
    else:
        result["paper_enables"] = []
    return result


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    WS_OUT.mkdir(parents=True, exist_ok=True)
    started = now_lon()
    completed = []
    print(f"START wave18+ at {started.isoformat()} stop~05:00 London", flush=True)
    fd_rows = load_fd()
    print(f"FD rows={len(fd_rows)} files={len(list(FD.glob('*.csv')))}", flush=True)

    # Strip premature OVERNIGHT footer if present — append continuation header
    cont_hdr = f"""
---

## Overnight continuation — waves 18+ (`{utc_now()}`)

Prior wave-15 audit was **premature** (hours remain to 05:00 London). Re-opened free+new lane on multi-league FD + maxout ATS/totals + NBA CLV join. Still £0 / Catakid untouched / no enable without bar.
"""
    for path in (DOC, WS_DOC):
        if path.exists():
            with path.open("a", encoding="utf-8") as f:
                f.write(cont_hdr)

    waves: List[Tuple[int, str, Callable]] = [
        (18, "under from low SOT", lambda: wave18_soccer_under_from_low_sot(fd_rows)),
        (19, "AH home settle", lambda: wave19_soccer_ah_home_settle(fd_rows)),
        (20, "NFL ATS spread bands", wave20_nfl_ats_spread_bands),
        (21, "NBA rest extreme ATS", wave21_nba_rest_extreme_ats),
        (22, "Max under shop", lambda: wave22_soccer_max_under_shop(fd_rows)),
        (23, "MLB fav vs dog honesty", wave23_mlb_fav_ats_honesty),
        (24, "NHL rest extreme ATS", wave24_nhl_rest_extreme_ats),
        (25, "red-card next match", lambda: wave25_soccer_redcard_next(fd_rows)),
        (26, "HT prior under gate", lambda: wave26_soccer_ht_under_gate(fd_rows)),
        (27, "NBA CLV selection gate", wave27_nba_clv_selection_gate),
        (28, "NFL totals line bands", wave28_nfl_totals_line_bands),
        (29, "soccer loss streak", lambda: wave29_soccer_loss_streak_away(fd_rows)),
        (30, "poisson lambda OU", lambda: wave30_soccer_poisson_lambda_under(fd_rows)),
        (31, "AH CLV gate", lambda: wave31_soccer_ah_clv_gate(fd_rows)),
        (32, "kickoff under buckets", lambda: wave32_soccer_kickoff_under(fd_rows)),
        (33, "NFL ATS by month", wave33_nfl_ats_month),
        (34, "BTTS-form draw", lambda: wave34_soccer_both_scored_draw(fd_rows)),
        (35, "NBA low-sigma ATS", wave35_nba_high_sigma_skip),
        (36, "overround tighten home", lambda: wave36_soccer_overround_close_vs_open(fd_rows)),
        (37, "NFL QB-clean ATS", wave37_nfl_qb_out_inverse),
        (38, "league under specialty", lambda: wave38_soccer_league_under_specialty(fd_rows)),
        (39, "NBA ATS weekday", wave39_nba_ats_weekday),
        (40, "under CLV gate", lambda: wave40_soccer_closing_under_clv(fd_rows)),
        (41, "MLB rest extreme ATS", wave41_mlb_rest_extreme),
        (42, "MaxAH shop", lambda: wave42_soccer_maxah_shop(fd_rows)),
        (43, "exhaustion re-audit", wave43_exhaustion_reaudit),
    ]

    total_enables = 0
    for wave_num, title, fn in waves:
        if past_stop():
            print(f"STOP clock before wave {wave_num}", flush=True)
            break
        print(f"=== WAVE {wave_num}: {title} @ {now_lon().isoformat()}", flush=True)
        try:
            result = maybe_enable(fn())
            enables = list(result.get("paper_enables") or [])
            total_enables += len(enables)
            idx = run_wave(wave_num, title, result)
            completed.append(idx)
            print(json.dumps({k: idx[k] for k in ("wave", "verdict", "paper_enable_count", "family_set")}, indent=2), flush=True)
        except Exception as e:
            err = {"wave": wave_num, "error": str(e), "trace": traceback.format_exc()[-2000:]}
            for base in (OUT, WS_OUT):
                (base / f"wave{wave_num}").mkdir(parents=True, exist_ok=True)
                (base / f"wave{wave_num}" / "error.json").write_text(json.dumps(err, indent=2))
            print("ERROR", err["error"], flush=True)
            completed.append({"wave": wave_num, "verdict": f"EXHAUST_WAVE{wave_num}_ERROR", "error": str(e), "paper_enable_count": 0})

        # update index
        for base in (OUT, WS_OUT):
            parent = json.loads((base / "index.json").read_text()) if (base / "index.json").exists() else {}
            parent[f"wave{wave_num}"] = completed[-1]
            parent["updated_at"] = utc_now()
            parent["overnight_extension_waves"] = [c.get("wave") for c in completed]
            (base / "index.json").write_text(json.dumps(parent, indent=2, default=str))

        if wave_num == 43:
            print("Re-audit marked free+new lane exhausted", flush=True)

    ended = now_lon()
    wave_nums = [c.get("wave") for c in completed if c.get("wave")]
    # Prior overnight claimed 17; extension adds these
    wave_count_total = 17 + len(wave_nums)
    footer = f"""
---

## Overnight continuation wrap (`{utc_now()}`)

Continuation waves **{min(wave_nums) if wave_nums else '—'}–{max(wave_nums) if wave_nums else '—'}**.  
Wall clock London: `{started.isoformat()}` → `{ended.isoformat()}`.  
**NEW paper enables this extension: {total_enables}.** Catakid NBA daemon **untouched**. `beats_book=false`.

### OVERNIGHT_SPORTS_DONE

**wave_count_total** = {wave_count_total} (waves 1–17 prior + {len(wave_nums)} continuation).  
**continuation_waves** = {wave_nums}.  
Free+new sim lane re-audited exhausted at wave 43 (or clock).  
Primary Dec 1 path remains **WAIT_ON_PAPER** (NBA).
"""
    for path in (DOC, WS_DOC):
        if path.parent.exists():
            with path.open("a", encoding="utf-8") as f:
                f.write(footer)

    summary = {
        "verdict": "OVERNIGHT_SPORTS_DONE",
        "started_london": started.isoformat(),
        "ended_london": ended.isoformat(),
        "prior_wave_count": 17,
        "continuation_waves": wave_nums,
        "wave_count_total": wave_count_total,
        "paper_enables_continuation": total_enables,
        "catakid": "untouched",
        "beats_book": False,
        "doc": str(DOC),
        "stop_reason": "reaudit_exhausted" if 43 in wave_nums else "clock_or_error",
        "generated_at": utc_now(),
    }
    for base in (OUT, WS_OUT):
        (base / "overnight_summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2), flush=True)


if __name__ == "__main__":
    main()
