# arXiv Full Census Plan

**Principle:** [arxiv-census-principle.md](./arxiv-census-principle.md)  
**SKIP filter:** [arxiv-census-skip-filter.md](./arxiv-census-skip-filter.md)  
**Ledger:** `/cursor/stores/bc-28a8dd7c-8662-49a7-9938-a5fa31b1d070/internal/arxiv-census/`  
**Budget:** £0 · free arXiv only · respect rate limits  
**Updated:** 2026-10-27 — Phase0 SKIP + fulltext queue (Bartosz cannot wait 1.5–2y for full-PDF of all)

## Honest gap (Waves 1–3 / mid-4)

Metadata+abstract passes produced **`INTERIM_ABSTRACT_ONLY`** labels. Those rows remain as catalog; they **must not** drive AID decisions. Authoritative pass = **fulltext** on Phase0 queue (+ audit).

## Two-pass harvest (2026-10-27 SKIP)

1. **Phase0 (fast, every paper)** — Atom title+abstract+category → `SKIP_HARD` | `FULLTEXT_QUEUE` | `UNCERTAIN_FULLTEXT` + reason. Runner: `run_phase0_pass.py`. Spec: [arxiv-census-skip-filter.md](./arxiv-census-skip-filter.md).
2. **Fulltext (authoritative AID)** — PDF extract for queue (+ SKIP audit sample). Prefer `--from-queue` after Phase0 completes. Within queue: **high-transfer cats first**, then date. Lock-order fulltext cursor retained for residual/backfill only.

## Harvest + extract (authoritative fulltext)

1. **Category lock (Phase0)** — `categories.json` lexicographic; within cat, `submittedDate` ascending (monthly windows if Atom deep-offset 500s).
2. **Fetch full artifact** — PDF from `https://arxiv.org/pdf/<id>` (primary). Also try HTML/`src` when useful.
3. **Extract EVERY character** — `pdftotext` (+ timed pdfminer if short); keep longer. Flag `OCR_NEEDED` / fails.
4. **Persist** — `fulltext/<id_key>.txt`; sha256 + chars in sqlite `fulltext`.
5. **Score ONLY from full extract for AID** — `score_fulltext.py`. Never promote Phase0/abstract-only to AID_*.
6. **Daily delta** — Phase0 then queue fulltext; `docs/arxiv-daily-YYYY-MM-DD.md`.

## Rate limits

≥3.0s between Phase0 Atom pages; ≥3.5s between fulltext fetches. Resume via `state/phase0_cursor.json` / `state/fulltext_cursor.json`.

## Runners

```text
internal/arxiv-census/
  categories.json
  score_phase0.py            # Phase0 SKIP gate
  score_abstract.py          # LEGACY interim + shared lexicons
  score_fulltext.py          # authoritative labeler
  fulltext_extract.py        # PDF/HTML → fulltext/<id>.txt
  run_phase0_pass.py         # fast meta census (prefer finish first)
  run_fulltext_rerun.py      # lock-order OR --from-queue
  run_daily_delta.py         # login-cadence new papers
  db_sync.py                 # /tmp work DB ↔ census.sqlite.gz
  mark_interim_abstract.py   # stamp INTERIM_ABSTRACT_ONLY
  fulltext/                  # extracts
  state/phase0_cursor.json
  state/phase0-status.json   # SKIP_LIVE
  state/fulltext_cursor.json
  state/daily_cursor.json
```

## Wave / re-run reports

- `docs/arxiv-census-wave*.md` — historical abstract waves (interim)
- `docs/arxiv-census-fulltext-rerun.md` — authoritative fulltext pass progress + extraction QA
- `docs/arxiv-census-skip-filter.md` — Phase0 SKIP design + live pointer
- `docs/arxiv-daily-YYYY-MM-DD.md` — daily deltas
