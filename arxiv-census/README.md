# arXiv census ledger

Full census for Dec-1 desks with **Phase0 SKIP** (fast meta gate) + **fulltext queue** (authoritative AID).

See:

- `docs/arxiv-census-principle.md`
- `docs/arxiv-census-plan.md`
- `docs/arxiv-census-skip-filter.md`
- `docs/arxiv-census-fulltext-rerun.md`

## Layout

| Path | Role |
| --- | --- |
| `categories.json` | Locked lexicographic Phase0 harvest order |
| `score_phase0.py` | SKIP_HARD / FULLTEXT_QUEUE / UNCERTAIN_FULLTEXT gate |
| `run_phase0_pass.py` | Fast Atom meta census → `phase0` table |
| `score_fulltext.py` | Authoritative AID labeler (full extract only) |
| `run_fulltext_rerun.py` | PDF path; `--from-queue` drains Phase0 queue |
| `db_sync.py` | Inflate /tmp work DB + gzip mirror |
| `census.sqlite.gz` | Store-side authoritative ledger (gzip) |
| `state/phase0_cursor.json` + `state/phase0-status.json` | Phase0 resume + `SKIP_LIVE` |
| `state/fulltext_cursor.json` | Residual lock-order fulltext pointer |

**Work DB while running:** `/tmp/arxiv-census/census.sqlite`  
Inflate with `python3 -c 'from db_sync import ensure_work_db; ensure_work_db()'` or `gunzip -c census.sqlite.gz > /tmp/arxiv-census/census.sqlite`.

## Resume Phase0 (preferred)

```bash
cd internal/arxiv-census
python3 -u run_phase0_pass.py --page-size 100
# after Phase0 (or for a slice of queue):
python3 -u run_fulltext_rerun.py --from-queue --max-seconds 3600
```
