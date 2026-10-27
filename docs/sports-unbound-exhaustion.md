# Sports unbound method exhaustion — beyond prior DONE map

Updated: `2026-10-27T00:26:52Z` · Cloud · **£0** · **no synthetic** · **no bookie login automation** · **beats_book=false** · **Catakid untouched** · model estimate · not tips

Parent: [dec1-profit-proveout](./dec1-profit-proveout.md) · Prior map: [betting-methods-exhaustion](./betting-methods-exhaustion.md) · Big-four: [big-four-gold-standard](./big-four-gold-standard.md) · [big-four-data-maxout](./big-four-data-maxout.md) · Soccer hold: [soccer-paper-disable](./soccer-paper-disable.md) · [soccer-1x2-lift](./soccer-1x2-lift.md) · Paper: [paper-bet-autonomy-status](./paper-bet-autonomy-status.md)

Raw: [`../internal/sims/sports-unbound-exhaustion/`](../internal/sims/sports-unbound-exhaustion/) · Runner: `run_unbound.py`

Preference unlock: **no method ceiling** (basic → most advanced / undiscovered) under £0 only — this pass invents **past** the Dec 1 DONE / WAIT map without re-opening tipster edges or paid feeds.

---

## Verdict (blunt)

**EXHAUST_DONE.** New method families beyond [betting-methods-exhaustion](./betting-methods-exhaustion.md) were mapped and honestly simmed (train-frozen WF; no OOS peek). **Zero NEW paper enables.** Catakid stays `nba_dog_conf_edge_8pct_isotonic` + ¼-Kelly + ≤2/night. Soccer / ATS / totals / CLV gates / injury filters / ensembles / other-sports desks **do not** clear dual bars.

**Ops notes only** (frozen NBA selection — not new method_ids): DD-scaled 1% stake cuts maxDD £151→£22; weekend-only and max-1/night lift flat end on the locked set. These reinforce the existing prove-path caveats (weekday weak; density caps help) — they do **not** justify re-opening τ search or attaching NFL/soccer.

`beats_book` stays **false**. Primary Dec 1 path remains **wait on NBA paper settles**.

| Label | This pass |
| --- | --- |
| **NEW_SCORED** | staking variants · market structure · CLV gates · temperature (ATS) · shrink ensemble · injury bankroll filters · NFL totals · soccer FD CLV · other-sports census |
| **TRIED_FAIL** | CLV band/rolling gates (shut off −CLV) · NFL totals dual-clear · NFL ATS dual-clear · NBA ATS ensemble · soccer fade · weekday-only |
| **OPS_NOTE** | DD-scaled stake · weekend-only · density max1 (frozen selection) |
| **BLOCKED_£0** | ⅛-Kelly / Platt / temp on locked **ML** (no per-bet `p_cal` dump in store — refuse synthetic p) · multi-book arb · NCAAB/NCAAF Odds key |
| **PAPER_ENABLE** | **none** |
| **NEVER** | lookahead CLV selection · tipster · bookie login automation |

---

## Scope vs prior DONE map

Prior map closed inventing at IDF-104/105/106 then WAIT. Unbound re-opens only families marked **PARTIAL / OUT_OF_SCOPE / not tried**, plus undiscovered staking/structure levers — still £0, still no synthetic closes, still no Catakid flip without bar.

| Family | Prior status | This pass |
| --- | --- | --- |
| Fractional Kelly ¼/½/Walters/flat/% | **DONE** | Not re-litigated; baseline cite only |
| ⅛-Kelly / temp / Platt on NBA ML | OUT_OF_SCOPE / PARTIAL | **BLOCKED** — need `p_cal` rows (absent); ATS temp scored instead |
| CLV as selection gate | OUT_OF_SCOPE | **SCORED** → shutoff / fail |
| Ensemble / injuries as levers | PARTIAL | **SCORED** → dual-clear fail |
| Totals / ATS paper | PARTIAL / TRIED_FAIL | **SCORED** WF → dual-clear fail |
| Soccer FD open/close | OUT_OF_SCOPE | **SCORED** process + fade → fail; paper stays off |
| Other sports / college | BLOCKED / research | Census restated — no new priced desk |

---

## 1. Staking variants (NEW beyond ¼/½/Walters)

Locked selection: `nba_dog_conf_edge_8pct_isotonic` OOS lean n=**369** (same freeze as Kelly/CLV docs). Stake-only / density / stop-loss — **no τ re-search**.

| Variant | n | End £ | Max DD | Bust | Clears draft? | Notes |
| --- | ---: | ---: | ---: | :---: | :---: | --- |
| flat £5 (cite) | 369 | 139.00 | 150.75 | N | Y | Already known path; high DD |
| 1% bank | 369 | 86.48 | 29.13 | N | Y | Conservative twin |
| 1.5% bank | 369 | 87.42 | 47.18 | N | Y | |
| **DD-scaled 1%** (NEW) | 343 | 84.07 | **21.74** | N | Y | Best DD cut; ops note |
| vol-target flat (NEW) | 369 | 104.57 | 149.17 | N | Y | No DD help |
| stop-loss BR&lt;40 (NEW) | 369 | 139.00 | 150.75 | N | Y | Never tripped on this path |
| density max1 (NEW) | 315 | **199.75** | 111.25 | N | Y | Ops note vs locked max2 |
| density max2 | 365 | 159.00 | 140.75 | N | Y | |

**Paper:** no new method_id. Live stake mode remains **¼-Kelly** ([nba-kelly-staking](./nba-kelly-staking.md)). DD-scaled / max1 are optional ops experiments on paper ledger only if Bartosz wants — not auto-applied.

**⅛-Kelly / ML temperature / NBA Platt:** **BLOCKED_£0** this cloud pass — store has no locked per-bet `p_cal` dump; inventing Kelly from win% alone is **NEVER** (prior map).

---

## 2. Market structure (NEW)

| Lever | Result | Verdict |
| --- | --- | --- |
| **Weekend-only** (Fri–Sun hard filter) | n=179 · end £192.25 · DD £96.75 · clears draft | **OPS_NOTE** — confirms prove-path weekend carry; weekday-only **busts** (end £2.50) |
| Mild dogs +100..+200 | n=339 · end £85.50 · DD £126.50 | Weak vs all-dog flat; not enable |
| Long dogs &gt;+200 | n=30 · end £133.50 · thin | Artifact risk — **HOLD** |
| Multi-book / steam / arb | — | Still **BLOCKED_£0** / **NEVER** (no Odds API / no passwords) |

---

## 3. CLV gates (NEW — was OUT_OF_SCOPE)

Standard sign: `CLV = fair_close − fair_open` (+ = beat close). Quality join n=**195** (cite [nba-clv-probe](./nba-clv-probe.md)).

| Check | Value |
| --- | ---: |
| Mean std-CLV | **−5.78** fair-prob points |
| % +CLV | **12.8%** |
| Train band means (all) | **negative** (−4.4 to −10.1 pp) |
| Band gate keep_bands | **∅ → 0 bets** (honest shutoff) |
| Rolling prior-20 +CLV gate | **0 kept** (never armed) |
| Lookahead +CLV-only | Scored as **NEVER** (same-game close) |

**beats_book:** still **false**. CLV cannot be a Dec 1 selection lever on free NBA opens.

---

## 4. Calibration (NEW temperature — was OUT_OF_SCOPE)

Applied **temperature scaling on NBA ATS `p_home_cover`** (free prediction dump). Train≤2018 chooses T; OOS≥2019 scored once.

| Item | Result |
| --- | --- |
| Chosen T (train Brier) | **1.5** |
| OOS edge≥5% after temper | does **not** clear ATS dual proxy |
| ML isotonic locked path | unchanged — no re-fit |

---

## 5. Ensemble (NEW shrink-to-market)

NBA ATS: `ens = w·pred_margin + (1−w)·(−spread)`; edge + side from tempered cover prob. **Train-frozen** w,τ → OOS once.

| Best train pick | OOS cover | Dual-clear? |
| --- | ---: | :---: |
| w_model=0.3 · τ=0.08 | ~49.7% | **no** |

Prior ATS ~coin conclusion stands — **no paper**.

---

## 6. Injuries free (NEW as bankroll filter)

NFL ATS maxout rows with `injury_filter` / train≤2018 freeze τ → OOS≥2019.

| Slice | Train-frozen τ | Train cover / end | OOS cover / end | Dual-clear? |
| --- | ---: | --- | --- | :---: |
| all | 0.08 | 50.4% / £3.64 | 54.7% / £222.73 | **no** (train fails) |
| injury_flag only | 0.08 | 44.9% / £3.18 | 50.0% / £58.64 | **no** |
| exclude injury flag | 0.08 | 50.4% / £3.64 | 55.5% / £244.09 | **no** (train fails) |

Matches maxout: injury ridge **KILL** as edge; live filter only — **not** a paper ATS method.

---

## 7. Totals / spreads (NEW totals bankroll WF)

NFL totals (`nflverse total_line`, n=7290). Train≤2018 freezes side+τ; OOS≥2019 once.

| Best train | OOS cover | OOS end | Dual-clear? |
| --- | ---: | ---: | :---: |
| side=`both` · τ=0.02 | ~50.3% | £3.64 | **no** |

NBA/NFL ATS paper bar still **not** cleared (see §5–6). Spreads stay research-only per preferences.

---

## 8. Soccer FD CLV (NEW process — paper stays OFF)

Free Football-Data EPL CSVs (B365 open + B365C close), seasons 19/20–24/25, n=**2280**.

| Metric | Value |
| --- | ---: |
| Mean home fair CLV (open−close playbook sign) | ~0 |
| % home +CLV | ~49% |
| Causal “fade home-shortening → away dog at open” | n=671 candidates · path end £3.25 · **fail** |
| Dual-clear / flood | **no** |

Soccer Match Odds remain **disabled** ([soccer-paper-disable](./soccer-paper-disable.md)); lift dual-clear still **0**.

---

## 9. Other sports (census — no new priced enable)

Re-read [other-sports-data-maxout](./other-sports-data-maxout.md) / `college_hard_stops.json`:

| Desk | Status |
| --- | --- |
| WNBA / cricket / esports / boxing closes | research / **BLOCKED_£0** priced paper often |
| NCAAB / NCAAF | **HARD_STOP** — no Odds key; ESPN sched alone insufficient |
| Extra FD soccer comps | gaps closed or Δ negligible — not Dec 1 |
| MMA / NHL | already OOS-disabled on Catakid |

No new other-sport method cleared a paper bar this pass.

---

## Paper decision

| Action | Detail |
| --- | --- |
| **NEW enables** | **none** |
| **Catakid** | **untouched** — still NBA-only ¼-Kelly ≤2/night ([paper-bet-autonomy-status](./paper-bet-autonomy-status.md)) |
| **Ops notes** | DD-scaled 1% · weekend-only · density max1 — optional ledger experiments; not method_ids |
| **Do not re-enable** | NFL rescue · soccer · racing · NHL · MMA · ATS · totals |
| **Dec 1** | Keep waiting on NBA paper settles / weekday evidence ([nba-only-prove-path](./nba-only-prove-path.md)) |

---

## Honesty labels

| Label | Value |
| --- | --- |
| synthetic | **false** |
| beats_book | **false** |
| cost | **£0** |
| OOS peek for hyperparams | **false** (train-frozen) |
| bookie login automation | **false** |
| real_stakes | **none** |
| catakid | **untouched** |
| tipster | **none** |
| estimate | model estimate · not tips |

_model estimate — IDeFuuZe Lab research output. Not tipster advice; no auto-wager._

---

## EXHAUST_DONE

Unbound sports inventing past the prior DONE map is **complete** for this cloud pass: families listed above are scored or hard-stopped under £0. Nothing new clears the paper bar. Return to **WAIT_ON_PAPER** (NBA).
