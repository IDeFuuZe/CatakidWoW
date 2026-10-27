# arXiv census — FULL TEXT re-run

**Status:** FULLTEXT_QUEUE_MODE (Phase0 SKIP live — prefer finish Phase0, then `--from-queue`)  
**Mandate:** Abstract-only = **INVALID** for AID. Score only from complete PDF/HTML extract.  
**Principle / plan / SKIP:** [arxiv-census-principle.md](./arxiv-census-principle.md) · [arxiv-census-plan.md](./arxiv-census-plan.md) · [arxiv-census-skip-filter.md](./arxiv-census-skip-filter.md)  
**When:** 2026-10-26 overnight cloud; **2026-10-27** Phase0 gate — full-PDF only for QUEUE+UNCERTAIN+SKIP audit

## Hard stop on abstract-only

| Item | Value |
| --- | --- |
| Prior abstract rows stamped | **119363** → `INTERIM_ABSTRACT_ONLY` (`score_valid=0`) |
| Stamp file | `internal/arxiv-census/state/interim_abstract_stamp.json` |
| Wave 4 abstract continue | **Aborted** |

## Extraction stack

1. Download `https://arxiv.org/pdf/<id>`
2. `pdftotext -raw` **and** `-layout` — keep **longer** full extract (no page/char truncate for scoring)
3. Fallback: pdfminer entire doc; then `arxiv.org/html` / ar5iv / abs full text on PDF 404
4. Persist `fulltext/<id_key>.txt` (+ `.pdf` when store allows) with sha256 + flags
5. Score via `score_fulltext.py` over **entire** extract

## Cloud overnight

- Runner: `run_fulltext_rerun.py` — **cloud PID in `state/fulltext-status.json`** (no Catakid)
- Cursor: `state/fulltext_cursor.json`
- Ledger work DB: `/tmp/arxiv-census/census.sqlite` (+ `census.sqlite.gz` mirror in store)
- Fulltext score snapshot: `internal/arxiv-census/fulltext-scores.json.gz`
- Extracts: `/tmp/arxiv-census/fulltext/`
- Daily delta: `run_daily_delta.py` + timers
  - weekday **16:00** Europe/London → `arxiv-census-daily-delta-weekday-1600-london`
  - weekend **09:00** Europe/London → `arxiv-census-daily-delta-weekend-0900-london`
  - keepalive every 3h → `arxiv-census-fulltext-keepalive-3h`

## Live progress

Authoritative pointer: `state/fulltext_cursor.json` / `state/fulltext-status.json`.

HTML fallback live (legacy PDF 404s → ar5iv/html/abs). Zero-miss: `n_extract_fail=0` after retry of early 404s.

## False positive + lexicon fix (2026-10-27)

| Item | Detail |
| --- | --- |
| Paper | `astro-ph/9307026` — *NGC 6397: A case study in the resolution of post-collapse globular cluster cores* |
| Was | `AID_SPORTS` — rationale `sports-betting/odds lexicon (strong)` |
| Deep-read | Full extract is HST **point spread** / surface-brightness / globular-cluster cores. **No** sports-betting content. |
| Match | Bare `point spread` (optics/PSF) hit old strong pattern that only excluded `point spread function` immediately after. |
| Action | Demoted → **NO_AID** in `fulltext` + `papers`. All prior AID_* rows rescored with hardened lexicon (now **0** AID). |
| Lexicon harden | `score_abstract.py`: `point spread` requires betting frame; `odds forecasting` requires sports/bet prefix; added `ASTRO_SPORTS_FP` + `SPORTS_BETTING_FRAME` suppress for astro/optics collisions (PSF, globular cluster, core-collapse, etc.). |

### FP #2 — AID_CRYPTO (2026-10-27T05:xxZ)

| Item | Detail |
| --- | --- |
| Paper | `astro-ph/9405036` — *Massive Tau Neutrino and SN 1987a* |
| Was | `AID_CRYPTO` — `crypto/memecoin trading lexicon` |
| Match | Physics **"5 MeV both"** hit `mev\s+bots?` (`bots?` matched prefix of *both*) |
| Action | Demoted → **NO_AID**. Lexicon: require word-bounded `bots?`/`auctions?`/… and forbid preceding mass digit before `mev`. |

## Turn-end status (2026-10-27T01:18:46Z)

| Metric | Value |
| --- | ---: |
| n_fulltext_scored_cum | **619** |
| NO_AID | 619 |
| AID_SPORTS / POKER / CRYPTO | 0 / 0 / 0 |
| EXTRACT_FAIL | 0 |
| HTML fallback recoveries | 48 |

**Next pointer:** `astro-ph` / `199311` / start `40` (cat 0/158)

PID 13583. FP `astro-ph/9307026` demoted; lexicon hardened.
