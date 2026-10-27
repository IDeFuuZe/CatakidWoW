#!/usr/bin/env python3
"""Build locked lexicographic arXiv category list from OAI ListSets (no topic filter)."""
from __future__ import annotations

import json
import re
import urllib.request
from pathlib import Path

OAI = "https://oaipmh.arxiv.org/oai?verb=ListSets"
OUT = Path(__file__).resolve().parent / "categories.json"


def setspec_to_cat(spec: str) -> str | None:
    """Map OAI setSpec → Atom cat: code. Drop archive-only umbrella sets."""
    # Examples:
    #   cs:cs:AI → cs.AI
    #   physics:astro-ph:CO → astro-ph.CO
    #   physics:hep-th → hep-th
    #   q-fin:q-fin:TR → q-fin.TR
    #   cs / physics / math (top-level) → skip (not a leaf harvest unit)
    parts = spec.split(":")
    if len(parts) == 1:
        return None  # archive umbrella
    if len(parts) == 2:
        archive, leaf = parts
        if leaf == archive or leaf.startswith(archive):
            # econ:econ, cs:cs, physics:physics → umbrella under archive
            if leaf in {archive, "astro-ph", "cond-mat", "nlin", "physics"} and "." not in leaf:
                # physics:astro-ph is still an umbrella if subtypes exist; keep legacy singles
                if leaf in {"hep-ex", "hep-lat", "hep-ph", "hep-th", "gr-qc", "math-ph",
                            "nucl-ex", "nucl-th", "quant-ph"}:
                    return leaf
                if archive == "physics" and leaf == "astro-ph":
                    return None  # has subtypes
                if archive == "physics" and leaf == "cond-mat":
                    return None
                if archive == "physics" and leaf == "nlin":
                    return None
                if archive == "physics" and leaf == "physics":
                    return None
                if leaf == archive:
                    return None
            return leaf
        return f"{archive}.{leaf}" if False else leaf
    if len(parts) == 3:
        archive, mid, sub = parts
        if archive == "physics":
            if mid == "physics":
                return f"physics.{sub}"
            return f"{mid}.{sub}"
        # cs:cs:AI → cs.AI ; q-fin:q-fin:TR → q-fin.TR
        return f"{mid}.{sub}"
    return None


def main() -> None:
    req = urllib.request.Request(OAI, headers={"User-Agent": "arxiv-census/1.0 (Dec1 prove-out; free metadata)"})
    with urllib.request.urlopen(req, timeout=120) as resp:
        xml = resp.read().decode("utf-8", errors="replace")
    specs = re.findall(r"<setSpec>([^<]+)</setSpec>", xml)
    cats: list[str] = []
    seen: set[str] = set()
    for spec in specs:
        cat = setspec_to_cat(spec)
        if not cat or cat in seen:
            continue
        seen.add(cat)
        cats.append(cat)
    # Ensure important legacy single-level cats present
    for legacy in [
        "hep-th", "hep-ph", "hep-ex", "hep-lat", "gr-qc", "quant-ph",
        "nucl-th", "nucl-ex", "math-ph",
    ]:
        if legacy not in seen:
            cats.append(legacy)
            seen.add(legacy)
    cats = sorted(cats)
    payload = {
        "source": OAI,
        "order": "lexicographic",
        "n_categories": len(cats),
        "categories": cats,
        "note": "Strict harvest order: index 0..n-1, submittedDate ascending within each cat. Zero keyword pre-filter.",
    }
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {OUT} n={len(cats)}")
    print("first10=", cats[:10])
    print("last10=", cats[-10:])


if __name__ == "__main__":
    main()
