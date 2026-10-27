#!/usr/bin/env python3
"""Authoritative scorer: FULL TEXT only. Abstract-only calls are invalid for AID."""
from __future__ import annotations

from score_abstract import score_abstract


def score_fulltext(*, title: str, fulltext: str, categories: list[str] | None = None) -> dict:
    if not fulltext or not fulltext.strip():
        return {
            "labels": ["EXTRACT_FAIL"],
            "primary": "EXTRACT_FAIL",
            "aid_sports": False,
            "aid_poker": False,
            "aid_crypto": False,
            "transfer": False,
            "uncertain": False,
            "no_aid": False,
            "rationale": "no full text available — AID decision withheld",
            "phase": "fulltext",
            "score_valid": False,
        }
    # Score over title + entire extract (no truncation). Lexicon scan is streaming-safe via one string.
    # For extremely large texts, still pass full string — memory bound accepted for correctness mandate.
    result = score_abstract(title=title or "", abstract=fulltext, categories=categories or [])
    result["phase"] = "fulltext"
    result["score_valid"] = True
    result["chars_scored"] = len(fulltext)
    # UNCERTAIN from abstract-era lexicon still means uncertain on fulltext — keep
    if result.get("no_aid") and result.get("rationale", "").startswith("no desk"):
        result["rationale"] = "fulltext: " + result["rationale"]
    else:
        result["rationale"] = "fulltext: " + result.get("rationale", "")
    return result
