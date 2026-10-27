# EXP-S1 / EXP-S2 results — paper CLV gates + injury skip

Updated: `2026-10-27T10:58Z` · Cloud paper-eval · **£0** · **no bookie login** · **Catakid NBA ¼-Kelly daemon untouched** · model estimate · not tips

Parent: [how-people-profit](./how-people-profit.md) §7 · [gain-edge-playbook](./gain-edge-playbook.md) · [paper-bet-autonomy-status](./paper-bet-autonomy-status.md) · [paper-ledger-scoreboard](./paper-ledger-scoreboard.md)

Raw: [`../internal/sims/exp-s1-s2/`](../internal/sims/exp-s1-s2/)

**Token:** `EXP_S1_S2_DONE`

---

## Verdict

| ID | Result | Why |
| --- | --- | --- |
| **EXP-S1** | **PASS** | Scoreboard emits `%+CLV`, `mean_CLV_pp`, `n_with_clv`, `rlm_proxy`, `note_lag_h` on settled NBA rows even when `n_with_clv=0`. **No** CLV selection gate. |
| **EXP-S2** | **PASS** | Dry-run on saved `official.nba.com` injury index HTML + 06:45 ET PDF; star→Out after note logs `injury_out_after_note` void/shrink. **No** ATS edge claim. |

Catakid daemon **not** restarted / not reconfigured. Paper-side filters only (Bartosz YES for S1/S2 ops pack).

---

## EXP-S1 — paper CLV scoreboard (+ S3 RLM + S4 note lag)

### Spec (§7)

Touch: Catakid `…/paper-bets/ledger.jsonl` + scoreboard. Settled **NBA** only; CLV vs free close when available; print `%+CLV`, `mean_CLV_pp`, `n_with_clv`; embed **S3** `rlm_proxy` + **S4** `note_lag_h`.  
**Pass:** fields show even if `n_with_clv=0`. **Fail:** CLV selection gate.

### Run

| Item | Value |
| --- | --- |
| Runner | `internal/sims/exp-s1-s2/run_exp_s1_scoreboard.py` |
| Ledger fixture | store/Catakid mirror `ledger.jsonl` (35 lines; NFL places/settles; **0 NBA settles**) |
| Output | `exp_s1_scoreboard.json` |
| `clv_selection_gate` | **false** |

### Scoreboard (live ledger mirror)

| Field | Value |
| --- | --- |
| `n_settled_nba` | **0** |
| `n_with_clv` | **0** |
| `%+CLV` (`pct_plus_clv`) | **null** (honest empty) |
| `mean_CLV_pp` | **null** (honest empty) |
| `rlm_proxy_counts` | `{}` |
| `note_lag_h_mean` | **null** |
| selection gate | **off** |

Matches §7 expectation: NBA method still 0 settles — scoreboard must tolerate empty CLV.

### Synth close check (math only — not claimed live edge)

Two synthetic NBA settle rows with one free open+close pair prove field wiring when closes exist:

| bet | open dec | close dec | CLV pp | rlm_proxy | note_lag_h |
| --- | ---: | ---: | ---: | --- | ---: |
| `pb_syn_nba_1` | 2.20 | 1.90 | **+6.35** | `shorten_into_pick` | 5.5 |
| `pb_syn_nba_2` | 2.10 | — | null | null | 4.0 |

`n_with_clv=1` · `%+CLV=100` · `mean_CLV_pp≈6.35` · gate still **false**. Artifact: `exp_s1_scoreboard_synth.json`.

### Explicit non-goals

- Does **not** revive CLV band/rolling keep gates (unbound **TRIED_FAIL**).
- Does **not** flip `beats_book` (historical free NBA probe still mean **−5.8 pp**).
- Does **not** change ¼-Kelly / ≤2/night place set.

---

## EXP-S2 — official injury skip

### Spec (§7)

At note + tip−90m: if listed star → **Out** after note → void/shrink with `injury_out_after_note`.  
**Pass:** dry-run on one saved HTML **or** live skip logged. **Fail:** ATS edge claim.

### Run

| Item | Value |
| --- | --- |
| Runner | `internal/sims/exp-s1-s2/run_exp_s2_injury_skip.py` |
| HTML fixture | `official-nba-injury-index-2026-10-27.html` (`official.nba.com` · 28 PDF links) |
| PDF fixture | `Injury-Report_2026-10-27_06_45AM.pdf` (ak-static free) |
| Output | `exp_s2_injury_skip.json` |
| `ats_edge_claim` | **false** |

### Dry-run skips logged

Parsed **28** injury rows · **6** listed stars **Out** on the PDF. Example paper actions (note assumed Questionable → tip PDF Out):

| Player | Matchup | Action |
| --- | --- | --- |
| Jalen Duren | DET@NYK | `injury_out_after_note` → void/shrink |
| Jose Alvarado | DET@NYK | `injury_out_after_note` → void/shrink |
| Keegan Murray | SAC@SAS | `injury_out_after_note` → void/shrink |
| Ben Simmons | SAC@SAS | `injury_out_after_note` → void/shrink |
| Tobias Harris | SAC@SAS | `injury_out_after_note` → void/shrink |

Controls: star still Questionable/Available at tip → `no_skip` / keep. Non-star Out → `no_skip` (star list only).

### Explicit non-goals

- **Not** an ATS / injury-alpha method_id (unbound injury bankroll filters failed dual-clear).
- **Not** steam race / beat-reporter latency.
- **Not** applied live on Catakid this turn (paper dry-run + drop-in filter module only).

---

## Catakid impact

| Check | Status |
| --- | --- |
| NBA place method | unchanged `nba_dog_conf_edge_8pct_isotonic` |
| Stake | unchanged `kelly_quarter` · ≤2/night |
| Daemon restart | **none** (no self-hosted worker this run) |
| Bookie login automation | **none** |
| £ spent | **£0** |

When Catakid is next online: merge scoreboard fields into `paper-ledger-scoreboard.ps1` / eval JSON; wire injury poll at note + tip−90m as optional paper void reason — still filter-only.

---

## Re-run

```bash
cd internal/sims/exp-s1-s2
python3 run_exp_s1_scoreboard.py --ledger fixtures/ledger.jsonl
python3 run_exp_s2_injury_skip.py \
  --html fixtures/official-nba-injury-index-2026-10-27.html \
  --pdf fixtures/Injury-Report_2026-10-27_06_45AM.pdf
```

---

## Bottom line

**EXP-S1 PASS** · **EXP-S2 PASS** · honest empty CLV on current ledger · injury skip dry-run logged · daemon untouched · `EXP_S1_S2_DONE`.
