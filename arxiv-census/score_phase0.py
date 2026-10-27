#!/usr/bin/env python3
"""
Phase0 gate: title + abstract + categories → SKIP_HARD | FULLTEXT_QUEUE | UNCERTAIN_FULLTEXT.
Not an AID decision. Reuses hardened lexicons from score_abstract.
"""
from __future__ import annotations

import re
from typing import Any

from score_abstract import (
    CRYPTO_MED,
    CRYPTO_STRONG,
    CRYPTOGRAPHY_NEG,
    POKER_MED,
    POKER_STRONG,
    SPORTS_BETTING_FRAME,
    SPORTS_MED,
    SPORTS_STRONG,
    ASTRO_SPORTS_FP,
    TRANSFER,
    UNCERTAIN_HINT,
)

# Categories that always deserve fulltext (desk / transfer adjacency)
ALWAYS_QUEUE_PREFIXES = (
    "cs.GT",
    "cs.AI",
    "cs.LG",
    "cs.MA",
    "cs.CE",
    "stat.ML",
    "stat.AP",
    "q-fin.",
    "econ.",
    "math.OC",
    "math.PR",
    "math.ST",
)

# Deep-read preference AFTER Phase0 completes (lower = sooner).
# Documented choice: finish Phase0 lock-order first; then drain queue with this rank
# within FULLTEXT_QUEUE, then UNCERTAIN, then SKIP audit — date order within band+rank.
HIGH_TRANSFER_QUEUE_PREFIXES = (
    "cs.GT",
    "q-fin.",
    "econ.",
    "cs.AI",
    "cs.LG",
    "cs.MA",
    "stat.ML",
    "math.OC",
    "math.PR",
    "stat.AP",
    "cs.CE",
    "math.ST",
    "physics.data-an",
    "physics.soc-ph",
    "cs.CY",
    "cs.IR",
    "cs.SI",
    "stat.ME",
)

# Hard-skip eligible ONLY when no positive lexicon hits
HARD_SKIP_PREFIXES = (
    "hep-",
    "nucl-",
    "gr-qc",
    "astro-ph",
    "quant-ph",
    "cond-mat.",
    "cond-mat",
    "nlin.",
    "math.AG",
    "math.AT",
    "math.AP",
    "math.CA",
    "math.CO",  # careful: combinatorics can touch games — lexicon overrides
    "math.CT",
    "math.CV",
    "math.DG",
    "math.DS",
    "math.FA",
    "math.GM",
    "math.GN",
    "math.GR",
    "math.GT",  # geometric topology, not game theory (cs.GT)
    "math.HO",
    "math.KT",
    "math.LO",
    "math.MG",
    "math.MP",
    "math.NA",
    "math.NT",
    "math.OA",
    "math.QA",
    "math.RA",
    "math.RT",
    "math.SG",
    "math.SP",
    "physics.acc-ph",
    "physics.ao-ph",
    "physics.atm-clus",
    "physics.atom-ph",
    "physics.bio-ph",
    "physics.chem-ph",
    "physics.class-ph",
    "physics.comp-ph",
    "physics.ed-ph",
    "physics.flu-dyn",
    "physics.gen-ph",
    "physics.geo-ph",
    "physics.hist-ph",
    "physics.ins-det",
    "physics.med-ph",
    "physics.optics",
    "physics.plasm-ph",
    "physics.pop-ph",
    "physics.space-ph",
)

# Soft keep (never SKIP_HARD by category alone)
KEEP_CATS = {
    "physics.data-an",
    "physics.soc-ph",
    "cs.CY",
    "cs.IR",
    "cs.SI",
    "stat.ME",
    "stat.TH",
    "stat.CO",
}


def _cat_match(cat: str, prefixes: tuple[str, ...]) -> bool:
    return any(cat == p or cat.startswith(p) for p in prefixes)


def high_transfer_rank(primary: str | None, categories: list[str] | None = None) -> int:
    """Lower = drain sooner in --from-queue. Unknown cats rank last within band."""
    cats = list(categories or [])
    if primary and primary not in cats:
        cats = [primary] + cats
    best = 10_000
    for i, pref in enumerate(HIGH_TRANSFER_QUEUE_PREFIXES):
        if any(_cat_match(c, (pref,)) for c in cats):
            best = min(best, i)
    return best


def _has_positive_desk_signal(text: str) -> tuple[bool, str]:
    """True → must FULLTEXT_QUEUE. Returns (hit, reason)."""
    if SPORTS_STRONG.search(text) or (
        SPORTS_MED.search(text) and re.search(r"\b(bet|odds|wager|market|forecast|predict)\b", text, re.I)
    ):
        if ASTRO_SPORTS_FP.search(text) and not SPORTS_BETTING_FRAME.search(text):
            pass  # suppressed FP
        else:
            return True, "sports/betting lexicon"
    if POKER_STRONG.search(text) or (
        POKER_MED.search(text) and re.search(r"\bpoker\b", text, re.I)
    ):
        return True, "poker lexicon"
    crypto_hit = CRYPTO_STRONG.search(text) or (
        CRYPTO_MED.search(text)
        and re.search(r"\b(trad|price|market|forecast|liquidity|token)\b", text, re.I)
    )
    if crypto_hit:
        if CRYPTOGRAPHY_NEG.search(text) and not CRYPTO_STRONG.search(text) and not re.search(
            r"\b(bitcoin|ethereum|memecoin|defi|uniswap|token\s+price)\b", text, re.I
        ):
            pass
        else:
            return True, "crypto-trading lexicon"
    if TRANSFER.search(text):
        return True, "transferable method lexicon"
    return False, ""


def score_phase0(
    *,
    title: str,
    abstract: str,
    categories: list[str] | None = None,
    primary_category: str | None = None,
) -> dict[str, Any]:
    cats = list(categories or [])
    if primary_category and primary_category not in cats:
        cats = [primary_category] + cats
    text = f"{title or ''}\n{abstract or ''}"
    cat_str = " ".join(cats)

    desk, desk_why = _has_positive_desk_signal(text)
    always = any(_cat_match(c, ALWAYS_QUEUE_PREFIXES) for c in cats) or _cat_match(
        primary_category or "", ALWAYS_QUEUE_PREFIXES
    )
    keep = any(c in KEEP_CATS for c in cats) or (primary_category in KEEP_CATS if primary_category else False)
    hard_eligible = (
        any(_cat_match(c, HARD_SKIP_PREFIXES) for c in cats)
        or _cat_match(primary_category or "", HARD_SKIP_PREFIXES)
    ) and not always and not keep

    if desk or always:
        reason = desk_why if desk else f"always-queue category ({cat_str or primary_category})"
        return {
            "phase0_label": "FULLTEXT_QUEUE",
            "phase0_reason": reason,
            "score_valid_for_aid": False,
            "phase": "phase0",
        }

    if UNCERTAIN_HINT.search(text) and not hard_eligible:
        return {
            "phase0_label": "UNCERTAIN_FULLTEXT",
            "phase0_reason": "ambiguous market/game language",
            "score_valid_for_aid": False,
            "phase": "phase0",
        }

    if hard_eligible and not desk:
        return {
            "phase0_label": "SKIP_HARD",
            "phase0_reason": f"hard-skip category without desk/transfer lexicon ({primary_category or cats[:1]})",
            "score_valid_for_aid": False,
            "phase": "phase0",
        }

    # Default safe: queue for fulltext
    if UNCERTAIN_HINT.search(text):
        label, reason = "UNCERTAIN_FULLTEXT", "ambiguous lexicon outside hard-skip"
    elif keep:
        label, reason = "FULLTEXT_QUEUE", f"keep-category ({cat_str})"
    else:
        label, reason = "UNCERTAIN_FULLTEXT", "default uncertain — not hard-skip eligible"

    return {
        "phase0_label": label,
        "phase0_reason": reason,
        "score_valid_for_aid": False,
        "phase": "phase0",
    }


if __name__ == "__main__":
    demos = [
        ("Higgs mass bounds", "Loop corrections in the MSSM.", ["hep-ph"], "hep-ph"),
        ("Kelly for NFL moneylines", "Fractional Kelly on sportsbook closing lines.", ["stat.ML"], "stat.ML"),
        ("Solving poker with CFR+", "We solve HUNL with CFR.", ["cs.GT"], "cs.GT"),
        ("Galaxy cluster lensing", "We measure weak lensing shear.", ["astro-ph"], "astro-ph"),
        ("Limit order book dynamics", "Optimal execution in LOBs.", ["q-fin.TR"], "q-fin.TR"),
    ]
    for t, a, cats, prim in demos:
        print(prim, "=>", score_phase0(title=t, abstract=a, categories=cats, primary_category=prim))
