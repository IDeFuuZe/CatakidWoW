# arXiv census — Phase0 SKIP filter

**Status:** LIVE (2026-10-27)  
**Store:** `internal/arxiv-census/`  
**Binding with:** [arxiv-census-principle.md](./arxiv-census-principle.md) · [arxiv-census-plan.md](./arxiv-census-plan.md)

## Why

Zero-miss full-PDF on ~2.5M papers at ~3.5s/PDF is multi-year (~1.5–2y). Bartosz cannot wait. We add a **Phase0 gate** that still scores **every** paper (title + abstract + category) and records a durable ledger row — without pretending abstract-only is an AID decision.

## Non-negotiables

1. **Not** “relevance search only.” Every arXiv id in lock order still enters the ledger.
2. **AID_*** / authoritative **NO_AID** still require **full PDF/HTML extract** (existing fulltext bar).
3. SKIP is a **gate outcome**, not a desk AID call. Rationale stored (`phase0_reason`).
4. Full PDF continues for `FULLTEXT_QUEUE` + `UNCERTAIN_FULLTEXT`, plus a **random ~1% audit sample** of `SKIP_HARD`.

## Phase0 outcomes

| Label | Meaning | Next action |
| --- | --- | --- |
| `SKIP_HARD` | Title+abstract+category make sports/poker/crypto-trading aid **implausible** (e.g. pure HEP collider note, no transfer lexicon) | Ledger only; ~1% audit fulltext sample |
| `FULLTEXT_QUEUE` | Positive desk / transfer / high-value-cat signal | Preferential full-PDF extract + `score_fulltext` |
| `UNCERTAIN_FULLTEXT` | Ambiguous market/game language or weak signal | Full-PDF extract + score (same queue priority band) |

## Gate inputs (only)

- `title`, `abstract` (Atom summary), `categories` / primary category  
- **No** PDF at Phase0  
- Reuses hardened sports/poker/crypto/transfer lexicons from `score_abstract.py`, plus category allow/deny lists (`score_phase0.py`)

## Category policy (summary)

**Always queue (unless cryptography-only neg):**  
`cs.GT`, `cs.AI`, `cs.LG`, `cs.MA`, `cs.CE`, `stat.ML`, all `q-fin.*`, all `econ.*`, `math.OC`, `math.PR`, `math.ST`, `stat.AP`

**Hard-skip eligible when no positive lexicon:**  
`hep-*`, `nucl-*`, `gr-qc`, `astro-ph*`, `quant-ph`, most `cond-mat.*`, most pure `math.*` (except OC/PR/ST), `nlin.*`, `physics.*` (except `physics.data-an` / `physics.soc-ph`), etc.

**Soft keep (never SKIP_HARD by category alone):**  
`physics.data-an`, `physics.soc-ph`, `cs.CY`, `cs.IR`, `cs.SI`, `stat.ME`, `stat.TH`, `stat.CO`

**Default:** if not hard-skip-eligible → `UNCERTAIN_FULLTEXT` (safe).

Positive lexicon (sports/poker/crypto-trading/transfer) **overrides** hard-skip → `FULLTEXT_QUEUE`.

## Pipeline order (LOCKED CHOICE)

**Prefer finishing the Phase0 corpus fast**, then deep-read.

1. **Phase0 pass** — lock-order category → monthly windows → Atom page (large `page_size`, meta only). Persist every id with label + reason.  
2. **Fulltext deep-read** (`run_fulltext_rerun.py --from-queue`) — drain in this order:
   - band: `FULLTEXT_QUEUE` → `UNCERTAIN_FULLTEXT` → `SKIP_HARD` audit sample  
   - **within band: high-transfer categories first** (`cs.GT`, `q-fin.*`, `econ.*`, `cs.AI`/`LG`/`MA`, `stat.ML`, `math.OC`/`PR`, …)  
   - then published / scored_at date order  
3. Lock-order fulltext cursor retained only for residual/backfill — **not** the primary path while Phase0 is incomplete.

Interleave allowed only if ops force it; default = **no PDF until Phase0 for that id is recorded**, and prefer **complete Phase0 across cats before queue drain**.

## Ledger

Table `phase0`: `arxiv_id`, `phase0_label`, `phase0_reason`, `title`, `abstract`, `categories`, `harvest_category`, `scored_at`, `audit_fulltext` (0/1).

Every id: **either** `SKIP_HARD` **or** later a fulltext authoritative score (`NO_AID` / `AID_*` / `TRANSFER` / `UNCERTAIN` / `EXTRACT_FAIL`). Already-fulltext rows stay authoritative; Phase0 still recorded for completeness when re-touched.

## Runners

```text
score_phase0.py          # gate
run_phase0_pass.py       # fast meta census → phase0 table (+ SKIP_LIVE status)
run_fulltext_rerun.py    # PDF path; --from-queue drains Phase0 queue (high-transfer first)
db_sync.py               # inflate /tmp work DB + gzip mirror to store
state/phase0_cursor.json
state/phase0-status.json # SKIP_LIVE
```

## Throughput

Phase0 ≈ one Atom page per sleep (no PDF). With `page_size=100` and ≥3s spacing, order-of-magnitude **10³–10⁴ papers/hour** (API 429s dominate). Fulltext baseline ~**10²/hour**. Live ratio in `phase0-status.json` → `phase0_vs_fulltext_speedup_est`.

## Live status

See `internal/arxiv-census/state/phase0-status.json` (`SKIP_LIVE`) for `n_skip`, `n_queue`, rate estimate, next pointer.
