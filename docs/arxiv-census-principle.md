# arXiv Full Census Principle

**Status:** BINDING (updated 2026-10-27 — **Phase0 SKIP + FULL TEXT for queue**)  
**Scope:** £80 Dec-1 prove-out desks — sports betting, poker, memecoin/crypto trading  
**Constraint stack:** £0 data · free arXiv only · honest AID vs NO_AID · no bookie/wallet login automation · paper/sim before live

## Principle

Treat **https://arxiv.org/** as a **FULL CENSUS**, not a relevance-prefiltered literature search.

1. **Every paper is in scope** until Phase0-labeled. ~2.5M+ papers; **ZERO** keyword/topic/author pre-filter that drops ids from the ledger.
2. **FULL TEXT is mandatory for AID / authoritative NO_AID.** Download the free PDF (and/or HTML/LaTeX source; Word/.docx if a free mirror exists). Extract **every character** of readable text (`pdftotext` / pdfminer — completeness verified). Save the raw extract under `internal/arxiv-census/fulltext/<id>.txt` (plus PDF path if stored). **AID scores ONLY from that extract** (title may join; abstract alone is never enough for AID).
3. **Phase0 SKIP gate (speed):** Every paper still gets a Phase0 title+abstract+category label (`SKIP_HARD` / `FULLTEXT_QUEUE` / `UNCERTAIN_FULLTEXT`) + reason in the ledger — **not** an AID call. Full PDF zero-miss only for QUEUE + UNCERTAIN + random SKIP audit. See [arxiv-census-skip-filter.md](./arxiv-census-skip-filter.md). Prefer finish Phase0 corpus, then deep-read queue (high-transfer cats first within queue).
4. **`ABSTRACT_ONLY` = INVALID for AID decisions.** Prior Waves 1–3 (and mid Wave 4 abstract harvest) are labeled **`INTERIM_ABSTRACT_ONLY`** in the ledger — catalog/metadata only, **not** authoritative AID/NO_AID.
5. **Extraction QA:** Record char count, extractor, sha256. Flag `OCR_NEEDED` / `EXTRACT_FAIL` if empty, near-empty, or garbled; do not invent AID from a failed extract.
6. **No cherry-picking.** Strict locked category → submitted-date order for Phase0; fulltext prefers the Phase0 queue after the Phase0 pass. Dedup by arXiv id.
7. **Daily delta (Catakid login):** weekdays **16:00**, weekends **09:00** Europe/London — all new submissions since last daily cursor, Phase0 then full-PDF for queue, append ledger, write `docs/arxiv-daily-YYYY-MM-DD.md`.
8. **Honest labels.** Prefer `NO_AID` / `UNCERTAIN` over forced AID. `TRANSFER` for transferable methods that are not domain AID.

## Score vocabulary (FULL TEXT only)

| Label | Meaning |
| --- | --- |
| `AID_SPORTS` | Full text directly aids sports betting / sports-market edge |
| `AID_POKER` | Full text directly aids poker |
| `AID_CRYPTO` | Full text directly aids memecoin / crypto **trading** |
| `TRANSFER` | Transferable methods; not domain AID |
| `NO_AID` | No credible desk aid in full text |
| `UNCERTAIN` | Full text still ambiguous → human/deep queue |
| `INTERIM_ABSTRACT_ONLY` | Legacy abstract pass — **not** an AID decision |
| `EXTRACT_FAIL` / `OCR_NEEDED` | Could not obtain usable full text yet |

## Non-goals

- Abstract-only AID calls.
- Paid APIs, bookie/wallet automation, live auto-wager.

## Ledger

`internal/arxiv-census/` — sqlite + jsonl + `fulltext/<id>.txt`. Wave / rerun reports under `docs/`.

## Related

- Plan: [arxiv-census-plan.md](./arxiv-census-plan.md)
- SKIP filter: [arxiv-census-skip-filter.md](./arxiv-census-skip-filter.md)
- Fulltext re-run: [arxiv-census-fulltext-rerun.md](./arxiv-census-fulltext-rerun.md)
- Preference: `preferences.md` → **arXiv full census** / **arXiv daily delta**
