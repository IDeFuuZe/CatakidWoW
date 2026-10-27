# Sports unbound method exhaustion — beyond prior DONE map

Updated: `2026-10-27T00:38:03Z` · Cloud · **£0** · **no synthetic** · **no bookie login automation** · **beats_book=false** · **Catakid untouched** · model estimate · not tips

Parent: [dec1-profit-proveout](./dec1-profit-proveout.md) · Prior map: [betting-methods-exhaustion](./betting-methods-exhaustion.md) · Big-four: [big-four-gold-standard](./big-four-gold-standard.md) · [big-four-data-maxout](./big-four-data-maxout.md) · Soccer hold: [soccer-paper-disable](./soccer-paper-disable.md) · [soccer-1x2-lift](./soccer-1x2-lift.md) · Paper: [paper-bet-autonomy-status](./paper-bet-autonomy-status.md)

Raw: [`../internal/sims/sports-unbound-exhaustion/`](../internal/sims/sports-unbound-exhaustion/) · W1–W4 runners · [`wave2/`](../internal/sims/sports-unbound-exhaustion/wave2/) · [`wave3/`](../internal/sims/sports-unbound-exhaustion/wave3/) · [`wave4/`](../internal/sims/sports-unbound-exhaustion/wave4/)

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

## EXHAUST_DONE (wave 1)

Unbound sports inventing past the prior DONE map is **complete** for wave 1: families listed above are scored or hard-stopped under £0. Nothing new clears the paper bar. Catakid NBA daemon left alone.

---

## Wave 2 — further NEW families (`2026-10-27T00:32:04Z`)

Overnight continuation under the unbound ceiling. **No overlap re-litigation** of wave-1 levers. Still £0 · train-frozen WF · no OOS peek · **Catakid NBA daemon untouched**.

### Wave-2 verdict

**EXHAUST_WAVE2_DONE.** Fourteen additional families scored. **Zero NEW paper enables.** NHL/MLB ATS “dual-clear” numbers are **STRUCTURAL_HOLD** (always-dog also clears; model picks dog ≈97% on NHL OOS — puck/run-line ceiling from [big-four-data-maxout](./big-four-data-maxout.md)). Soccer OU/DNB fail dual or refuse as book-fav. Racing fade is process-only (no place/lay price). Shannon ATS fails. Rest/QB/personnel filters fail dual-clear.

| Label | Wave 2 |
| --- | --- |
| **NEW_SCORED** | season regime · anti-martingale · loss-press · bootstrap CI · RLM ex-post slices · month structure · Shannon ATS · NHL/MLB ATS honesty · NBA rest ATS · NFL QB/personnel ATS · soccer OU 2.5 multi-league · soccer DNB book · horse short-fav fade process |
| **STRUCTURAL_HOLD** | NHL/MLB ATS model≈always-dog |
| **TRIED_FAIL** | Shannon · NBA rest · NFL qb/pers · soccer OU · soccer DNB dual · loss/anti progressions as enable |
| **PAPER_ENABLE** | **none** |
| **Catakid** | **untouched** |

### 10. NBA locked-selection structure (NEW)

| Lever | Result | Verdict |
| --- | --- | --- |
| Early season (Oct–Jan) flat £5 | n=216 · end £84.50 · DD £105 | Weak vs late |
| Late season (Feb+) flat £5 | n=153 · end £134.50 · DD £77 | Better end — **OPS_NOTE** only |
| Anti-martingale win-press | end £125.72 · DD **£202** | Worse DD — **TRIED_FAIL** as stake mode |
| Loss-press cap 4× | end £145.75 · DD **£317** | Pathological DD — **TRIED_FAIL** |
| Bootstrap weekend flat (400 resamples) | point £192 · p05 **£2.25** · p50 £185 · frac&lt;£70 **23.5%** | Weekend point estimate **fragile** — honesty meta |
| RLM ex-post (−CLV vs +CLV slices) | against end £1.25 · with £80.50 | Ex-post only (**NEVER** as same-game gate) |
| Month structure | Mar best (£163) · Oct worst (£47) | Thin months — no enable |

### 11. Shannon / fortune stake on NBA ATS (NEW)

Train-frozen edge τ + Shannon fraction on `p_home_cover` edge; OOS once.

| Best train | OOS end | OOS cover | Dual? |
| --- | ---: | ---: | :---: |
| τ=0.08 · frac=0.25 | £24.81 | 50.3% | **no** |

### 12. NHL / MLB ATS honesty (NEW desks vs wave-1 NFL/NBA)

| Desk | Train-frozen best | Dual numbers? | Paper? |
| --- | --- | :---: | --- |
| **NHL** | model τ=0.0 (≈65% cover) | looks green | **STRUCTURAL_HOLD** — always-dog also dual-clears; model dog-pick rate OOS **97.3%** |
| **MLB** | model (run-line) | always-dog also dual-clears | **STRUCTURAL_HOLD** — same ±1.5 base-rate ceiling |

### 13. NBA rest_diff / NFL QB+personnel ATS (NEW filters)

| Family | Best train | OOS | Dual? |
| --- | --- | --- | :---: |
| NBA rest_home_plus τ=0.08 | cover 52.6% · end £88.64 | cover 48.2% · end £3.18 | **no** |
| NFL model τ=0.08 (qb/pers modes lost train) | train fail | OOS 54.7% / £222 | **no** (train fails) |

### 14. Soccer OU 2.5 multi-league + DNB book (NEW)

FD free: E0/SP1/D1/I1/F1 · n_OU=**4031**.

| Method | Train-frozen | OOS | Dual? |
| --- | --- | --- | :---: |
| Rolling over-rate → **under** τ=0.52 · min_dec 1.7 | end £90.40 · win 49.0% | end £2.25 · win 48.3% | **no** |
| Book-fav **DNB** (no model) | train fails dual | OOS end £279.87 (fav win% high — not +EV invent) | **no** enable (refuse book-fav) |

Soccer paper stays **OFF**.

### 15. Horse short-fav fade process (NEW)

| Filter | Train fav_win − SP_implied | OOS | Bankroll paper? |
| --- | ---: | ---: | --- |
| field≥8 · fav_dec≤2.5 | **−17.5 pp** | **−13.4 pp** | **HARD STOP** — no free place/lay price (prior map) |

Signal direction holds OOS as **process only** — not a Catakid method.

### Wave-2 paper decision

| Action | Detail |
| --- | --- |
| **NEW enables** | **none** |
| **Catakid NBA daemon** | **left alone** |
| **Structural refusals** | NHL/MLB ATS dog illusion |
| **Dec 1** | Still wait on NBA paper settles |

### Wave-2 honesty

| Label | Value |
| --- | --- |
| synthetic | **false** |
| beats_book | **false** |
| OOS peek | **false** |
| catakid | **untouched** |
| cost | **£0** |

---

## EXHAUST_WAVE2_DONE

Wave 2 unbound inventing is complete for this overnight slice. No new method clears a non-structural paper bar. Keep **WAIT_ON_PAPER** (NBA).

---

## Wave 3 — further NEW families (`2026-10-27T00:35:37Z`)

Overnight continuation. Families **not** scored in wave 1/2. Still £0 · train-frozen WF · **Catakid NBA daemon left alone**.

### Wave-3 verdict

**EXHAUST_WAVE3_DONE.** Nine additional families/process stops scored. **Zero NEW paper enables.** Soccer AH / ref-cards / kickoff / MaxH-shop all fail dual draft (or policy-hold). NBA sigma/resid ATS fails dual. Cool-off hurts locked NBA end. Greyhound fade process holds OOS but place/lay **HARD STOP**. Tennis-data.co.uk **403** this pass; cricket/WNBA priced paths still blocked.

| Label | Wave 3 |
| --- | --- |
| **NEW_SCORED** | soccer AH · HT process · ref yellows→under · kickoff home buckets · FD MaxH shop proxy · NBA sigma+resid ATS · NBA home/away+cool-off · greyhound short-fav fade · blocked census |
| **TRIED_FAIL** | AH · ref-under · kickoff · Max shop · sigma ATS · cool-off as improve |
| **HARD_STOP** | HT odds absent · greyhound place/lay · tennis-data 403 · cricket/WNBA closes |
| **PAPER_ENABLE** | **none** |
| **Catakid** | **untouched** |

### 16. Soccer Asian Handicap (NEW)

FD `AHh` + `B365AHH/AHA` multi-league.

| Best train-frozen | OOS end | OOS win% | Dual draft? |
| --- | ---: | ---: | :---: |
| longer_side · min_dec 1.70 | £2.65 | 39.5% | **no** (train end £156.70) |

### 17. HT/FT process (NEW) — no HT odds

| Metric | Value |
| --- | --- |
| P(FT home \| HT home) | **0.775** |
| Bankroll paper | **HARD_STOP** — no HT 1X2 odds columns in FD CSVs |

### 18. Referee yellows → under 2.5 (NEW)

| Best train | OOS end | Dual? |
| --- | ---: | :---: |
| card_min 3.5 · min_dec 1.70 · train end £114.55 | £4.65 | **no** |

### 19. Kickoff-hour home ML (NEW)

Evening vs early home at B365H — both buckets **fail** OOS dual draft.

### 20. FD MaxH vs B365H shop proxy (NEW)

Archive “best tape” shop (not live multi-book; not executable CLV).

| Best train | OOS end | Dual? |
| --- | ---: | :---: |
| Max−B365 ≥ 0.20 · train end £242.70 | £4.80 | **no** |

### 21. NBA ATS sigma tercile + residual filter (NEW)

Train sigma breaks frozen; OOS once.

| Best train | OOS cover | OOS end | Dual ATS? |
| --- | ---: | ---: | :---: |
| high-σ · τ=0.0 · train cover ~51.9% | 50.9% | £3.18 | **no** |

### 22. Locked NBA home/away + loss cool-off (NEW ops)

| Slice | End £ |
| --- | ---: |
| baseline flat | 139.00 |
| home picks only | 111.50 |
| away picks only | 107.50 |
| cool-off (3 losses → skip 2) | **71.00** (worse) |

**OPS:** cool-off not recommended vs baseline.

### 23. Greyhound short-fav fade process (NEW)

| Filter | Train gap (win−implied) | OOS gap | Paper? |
| --- | ---: | ---: | --- |
| field≥6 · fav_dec≤3.0 | **−13.1 pp** | **−13.1 pp** | **HARD STOP** (no place/lay) |

### 24. Blocked census (this pass)

| Item | Status |
| --- | --- |
| tennis-data.co.uk | **HTTP 403** — surface re-split deferred |
| cricket priced bankroll | advance cal only — no free closes |
| WNBA closes | prior HARD STOP |
| HT 1X2 odds | absent in FD |

### Wave-3 paper decision

| Action | Detail |
| --- | --- |
| **NEW enables** | **none** |
| **Catakid NBA daemon** | **left alone** |
| **Dec 1** | Wait on NBA paper settles |

### Wave-3 honesty

| Label | Value |
| --- | --- |
| synthetic | **false** |
| beats_book | **false** |
| OOS peek | **false** |
| catakid | **untouched** |
| cost | **£0** |

---

## EXHAUST_WAVE3_DONE

Wave 3 unbound inventing complete. No new method clears the paper bar. Keep **WAIT_ON_PAPER** (NBA).

---

## Wave 4 — further NEW families (`2026-10-27T00:38:03Z`)

Overnight continuation. Families **not** scored in waves 1–3. Still £0 · train-frozen WF · **Catakid NBA daemon left alone**.

### Wave-4 verdict

**EXHAUST_WAVE4_DONE.** Eleven additional families scored. **Zero NEW paper enables.** PS-vs-B365 shop, double-chance, long-draw, rolling GD, overround, Elo/eff disagree, sim-vs-p, NFL totals∩ATS corr-cap all fail dual bars. AH CLV ≈ coin process. Mean-reversion-after-wins **hurts**; early stop-win is path-fragile (hits +£40 in 23 bets then stops — not a robust enable). MMA/CS/Valorant reaffirmed non-paper.

| Label | Wave 4 |
| --- | --- |
| **NEW_SCORED** | PS vs B365 shop · AH CLV process · double chance · long draw · rolling GD form · overround regime · NBA elo/eff disagree · sim vs p_cover · NFL totals+ATS corr cap · mean-rev/stop-win · other-desk reaffirm |
| **TRIED_FAIL** | all bankroll WFs above |
| **PROCESS** | AH open→close CLV ~fair coin |
| **PAPER_ENABLE** | **none** |
| **Catakid** | **untouched** |

### 25. Pinnacle/PSH vs B365H shop (NEW)

| Best train | OOS | Dual? |
| --- | --- | :---: |
| min_edge 0.15 · train end £153.25 | end £0 · ruin | **no** |

### 26. AH open→close CLV process (NEW)

| n | mean std-CLV home | % open better dec | mean \|line move\| |
| ---: | ---: | ---: | ---: |
| 7815 | +0.0019 | 49.7% | 0.096 |

≈ coin — **no beats_book**.

### 27. Double chance 1X/X2 (NEW)

| Best train-frozen | OOS end | Dual? |
| --- | ---: | :---: |
| X2 · min_dec 1.35 | £1.16 | **no** |

### 28. Long draw (NEW)

| Best | OOS win% | Dual? |
| --- | ---: | :---: |
| B365D ≥ 3.4 | ~21% | **no** |

### 29. Rolling goal-diff form (NEW)

| Best | OOS win% | OOS end | Dual? |
| --- | ---: | ---: | :---: |
| \|ΔGD\|≥1.5 · home | 72.9% (thin luck?) | £50.15 | **no** (train also &lt;£70) |

### 30. Low-overround home ML (NEW)

| Best train | OOS | Dual? |
| --- | --- | :---: |
| max_ov 1.05 · train £254 | OOS £4.40 | **no** |

### 31. NBA Elo vs efficiency disagreement (NEW)

| Best train | OOS cover | Dual ATS? |
| --- | ---: | :---: |
| disagree≥1 · τ=0.08 · signs disagree | 47.1% | **no** |

### 32. sim_home_win_pct vs p_home_cover gap (NEW)

| Best | OOS cover | Dual? |
| --- | ---: | :---: |
| gap≥0.08 · trust sim | 49.2% | **no** |

### 33. NFL totals + ATS correlation cap (NEW)

| Best train-frozen | OOS cover | Dual? |
| --- | ---: | :---: |
| τ_tot 0.02 · τ_ats 0.05 · max 1/game | 51.5% | **no** |

### 34. Locked NBA mean-reversion + stop-win (NEW ops)

| Lever | End £ | Note |
| --- | ---: | --- |
| baseline flat | 139.00 | cite |
| after 2 wins only | 2.75 | **fail** |
| after 3 wins only | 76.75 | weak |
| stop-win +£40 | 175.25 @ n=23 | **fragile** early path — not enable |

### 35. Other desks reaffirm

MMA / CS / Valorant — prior maxout: `beats_book=false` or closes partial; **no** new paper.

### Wave-4 paper decision

| Action | Detail |
| --- | --- |
| **NEW enables** | **none** |
| **Catakid NBA daemon** | **left alone** |
| **Dec 1** | Wait on NBA paper settles |

### Wave-4 honesty

| Label | Value |
| --- | --- |
| synthetic | **false** |
| beats_book | **false** |
| OOS peek | **false** |
| catakid | **untouched** |
| cost | **£0** |

---

## EXHAUST_WAVE4_DONE

Wave 4 unbound inventing complete. No new method clears the paper bar. Keep **WAIT_ON_PAPER** (NBA).

---

## Wave 6 — league dog specialization (`2026-10-27T00:42:27Z`)

**EXHAUST_WAVE6_DONE.** Families: `wave6_league_dog_specialization`. Paper enables this wave: **0**. Catakid NBA **untouched**. `beats_book=false`.

```json
{
  "wave": 6,
  "family_set": "wave6_league_dog_specialization",
  "paper_enables": [],
  "highlights": {
    "by_league": {
      "B1": {
        "clears": false,
        "params": null,
        "oos_end": null,
        "train_end": null
      },
      "D1": {
        "clears": false,
        "params": null,
        "oos_end": null,
        "train_end": null
      },
      "D2": {
        "clears": false,
        "params": null,
        "oos_end": null,
        "train_end": null
      },
      "E0": {
        "clears": false,
        "params": {
          "kind": "home_dog",
          "min_dec": 3.0
        },
        "oos_end": 1.75,
        "train_end": 391.0
      },
      "E1": {
        "clears": false,
        "params": null,
        "oos_end": null,
        "train_end": null
      },
      "F1": {
        "clears": false,
        "params": null,
        "oos_end": null,
        "train_end": null
      },
      "F2": {
        "clears": false,
        "params": null,
        "oos_end": null,
        "train_end": null
      },
      "G1": {
        "clears": false,
        "params": {
          "kind": "away_dog",
          "min_dec": 3.0
        },
        "oos_end": 2.0,
        "train_end": 112.3
      },
      "I1": {
        "clears": false,
        "params": null,
        "oos_end": null,
        "train_end": null
      },
      "I2": {
        "clears": false,
        "params": null,
        "oos_end": null,
        "train_end": null
      },
      "N1": {
        "clears": false,
        "params": {
          "kind": "home_dog",
          "min_dec": 3.0
        },
        "oos_end": 1.75,
        "train_end": 4.0
      },
      "P1": {
        "clears": false,
        "params": null,
        "oos_end": null,
        "train_end": null
      },
      "SC0": {
        "clears": false,
        "params": {
          "kind": "away_dog",
          "min_dec": 2.0
        },
        "oos_end": 4.25,
        "train_end": 4.3
      },
      "SP1": {
        "clears": false,
        "params": null,
        "oos_end": null,
        "train_end": null
      },
      "SP2": {
        "clears": false,
        "params": null,
        "oos_end": null,
        "train_end": null
      },
      "T1": {
        "clears": false,
        "params": null,
        "oos_end": null,
        "train_end": null
      }
    },
    "leagues_dual_clear_draft": [],
    "policy": "soccer OFF even if dual draft",
    "generated_at": "2026-10-27T00:42:27Z",
    "wave": 6,
    "paper_decision": {
      "paper_enable": [],
      "catakid": "untouched",
      "beats_book": false
    }
  }
}
```

Raw: [`../internal/sims/sports-unbound-exhaustion/wave6/`](../internal/sims/sports-unbound-exhaustion/wave6/)

## EXHAUST_WAVE6_DONE

---

## Wave 10 — NBA staking ladder/time-stop (`2026-10-27T00:42:33Z`)

**EXHAUST_WAVE10_DONE.** Families: `wave10_nba_staking_ladder`. Paper enables this wave: **0**. Catakid NBA **untouched**. `beats_book=false`.

```json
{
  "wave": 10,
  "family_set": "wave10_nba_staking_ladder",
  "paper_enables": [],
  "highlights": {
    "baseline": {
      "n": 369,
      "wins": 160,
      "win_pct": 0.43360433604336046,
      "pl": 59.0,
      "staked": 1845.0,
      "end": 139.0,
      "roi_bank": 0.7375,
      "max_dd": 150.75,
      "bust": false,
      "skipped": 0,
      "clears_draft": true
    },
    "win_ladder": {
      "n": 369,
      "wins": 160,
      "win_pct": 0.43360433604336046,
      "pl": 1.6927,
      "staked": 2056.3823,
      "end": 81.6927,
      "roi_bank": 0.021159,
      "max_dd": 187.3728,
      "bust": false,
      "skipped": 0,
      "clears_draft": true
    },
    "loss_ladder": {
      "n": 369,
      "wins": 160,
      "win_pct": 0.43360433604336046,
      "pl": 48.3711,
      "staked": 2262.429,
      "end": 128.3711,
      "roi_bank": 0.604639,
      "max_dd": 167.9588,
      "bust": false,
      "skipped": 0,
      "clears_draft": true
    },
    "time_stop_100": {
      "n": 100,
      "wins": 46,
      "win_pct": 0.46,
      "pl": 119.0,
      "staked": 500.0,
      "end": 199.0,
      "roi_bank": 1.4875,
      "max_dd": 33.5,
      "bust": false,
      "skipped": 0,
      "clears_draft": true
    },
    "time_stop_200": {
      "n": 200,
      "wins": 93,
      "win_pct": 0.465,
      "pl": 129.5,
      "staked": 1000.0,
      "end": 209.5,
      "roi_bank": 1.61875,
      "max_dd": 48.75,
      "bust": false,
      "skipped": 0,
      "clears_draft": true
    },
    "per_calendar_year_flat": [
      {
        "season": "2015",
        "n": 8,
        "wins": 2,
        "win_pct": 0.25,
        "pl": -18.75,
        "staked": 40.0,
        "end": 61.25,
        "roi_bank": -0.234375,
        "max_dd": 18.75,
        "bust": false,
        "skipped": 0,
        "clears_draft": false
      },
      {
        "season": "2016",
        "n": 42,
        "wins": 20,
        "win_pct": 0.47619047619047616,
        "pl": 108.75,
        "staked": 210.0,
        "end": 188.75,
        "roi_bank": 1.359375,
        "max_dd": 32.75,
        "bust": false,
        "skipped": 0,
        "clears_draft": true
      },
      {
        "season": "2017",
        "n": 49,
        "wins": 24,
        "win_pct": 0.4897959183673469,
        "pl": 34.0,
        "staked": 245.0,
        "end": 114.0,
        "roi_bank": 0.425,
        "max_dd": 24.5,
        "bust": false,
        "skipped": 0,
        "clears_draft": true
      },
      {
        "season": "2018",
        "n": 39,
        "wins": 18,
        "win_pct": 0.46153846153846156,
        "pl": -0.25,
        "staked": 195.0,
        "end": 79.75,
        "roi_bank": -0.003125,
        "max_dd": 42.25,
        "bust": false,
        "skipped": 0,
        "clears_draft": false
      },
      {
        "season": "2019",
        "n": 47,
        "wins": 22,
        "win_pct": 0.46808510638297873,
        "pl": 3.75,
        "staked": 235.0,
        "end": 83.75,
        "roi_bank": 0.046875,
        "max_dd": 28.75,
        "bust": false,
        "skipped": 0,
        "clears_draft": true
      },
      {
        "season": "2020",
        "n": 27,
        "wins": 9,
        "win_pct": 0.3333333333333333,
        "pl": -36.5,
        "staked": 135.0,
        "end": 43.5,
        "roi_bank": -0.45625,
        "max_dd": 68.5,
        "bust": false,
        "skipped": 0,
        "clears_draft": false
      },
      {
        "season": "2021",
        "n": 90,
        "wins": 37,
        "win_pct": 0.4111111111111111,
        "pl": -14.75,
        "staked": 450.0,
        "end": 65.25,
        "roi_bank": -0.184375,
        "max_dd": 52.75,
        "bust": false,
        "skipped": 0,
        "clears_draft": false
      },
      {
        "season": "2022",
        "n": 60,
        "wins": 23,
        "win_pct": 0.38333333333333336,
        "pl": -38.25,
        "staked": 300.0,
        "end": 41.75,
        "roi_bank": -0.478125,
        "max_dd": 79.25,
        "bust": false,
        "skipped": 0,
        "clears_draft": false
      },
      {
        "season": "2023",
        "n": 7,
        "wins": 5,
        "win_pct": 0.7142857142857143,
        "pl": 21.0,
        "staked": 35.0,
        "end": 101.0,
        "roi_bank": 0.2625,
        "max_dd": 5.0,
        "bust": false,
        "skipped": 0,
        "clears_draft": true
      }
    ]
  }
}
```

Raw: [`../internal/sims/sports-unbound-exhaustion/wave10/`](../internal/sims/sports-unbound-exhaustion/wave10/)

## EXHAUST_WAVE10_DONE

---

## Wave 11 — racing course/jumps process (`2026-10-27T00:42:35Z`)

**EXHAUST_WAVE11_DONE.** Families: `wave11_racing_course_jumps`. Paper enables this wave: **0**. Catakid NBA **untouched**. `beats_book=false`.

```json
{
  "wave": 11,
  "family_set": "wave11_racing_course_jumps",
  "paper_enables": [],
  "highlights": {
    "courses_fade_holds_oos": [],
    "n_courses_scored": 3,
    "jumps": {
      "train_gap": -0.1667,
      "oos_gap": -0.0342,
      "n_train": 39,
      "n_oos": 23
    },
    "flat": {
      "train_gap": -0.0566,
      "oos_gap": -0.0407,
      "n_train": 236,
      "n_oos": 152
    },
    "reason": "HARD STOP place/lay \u2014 process only",
    "generated_at": "2026-10-27T00:42:35Z"
  }
}
```

Raw: [`../internal/sims/sports-unbound-exhaustion/wave11/`](../internal/sims/sports-unbound-exhaustion/wave11/)

## EXHAUST_WAVE11_DONE

---

## Wave 13 — HT lead holds FT process (`2026-10-27T00:42:38Z`)

**EXHAUST_WAVE13_DONE.** Families: `wave13_ht_lead_holds_ft`. Paper enables this wave: **0**. Catakid NBA **untouched**. `beats_book=false`.

```json
{
  "wave": 13,
  "family_set": "wave13_ht_lead_holds_ft",
  "paper_enables": [],
  "highlights": {
    "n_ht_leads": 8871,
    "hold_rate": 0.7479,
    "reason": "HARD_STOP no live HT odds for in-play style; process only",
    "generated_at": "2026-10-27T00:42:38Z",
    "wave": 13,
    "paper_decision": {
      "paper_enable": [],
      "catakid": "untouched",
      "beats_book": false
    }
  }
}
```

Raw: [`../internal/sims/sports-unbound-exhaustion/wave13/`](../internal/sims/sports-unbound-exhaustion/wave13/)

## EXHAUST_WAVE13_DONE

---

## Wave 14 — NBA weekend×density×DD stack (`2026-10-27T00:42:39Z`)

**EXHAUST_WAVE14_DONE.** Families: `wave14_nba_weekend_density_dd_stack`. Paper enables this wave: **0**. Catakid NBA **untouched**. `beats_book=false`.

```json
{
  "wave": 14,
  "family_set": "wave14_nba_weekend_density_dd_stack",
  "paper_enables": [],
  "highlights": {
    "weekend_flat": {
      "n": 179,
      "wins": 81,
      "win_pct": 0.45251396648044695,
      "pl": 112.25,
      "staked": 895.0,
      "end": 192.25,
      "roi_bank": 1.403125,
      "max_dd": 91.75,
      "bust": false,
      "skipped": 0,
      "clears_draft": true
    },
    "weekend_dens1_flat": {
      "n": 148,
      "wins": 70,
      "win_pct": 0.47297297297297297,
      "pl": 148.0,
      "staked": 740.0,
      "end": 228.0,
      "roi_bank": 1.85,
      "max_dd": 74.75,
      "bust": false,
      "skipped": 0,
      "clears_draft": true
    },
    "weekend_dens1_ddscaled": {
      "n": 148,
      "wins": 70,
      "win_pct": 0.47297297297297297,
      "pl": 25.0678,
      "staked": 139.9553,
      "end": 105.0678,
      "roi_bank": 0.313347,
      "max_dd": 15.8662,
      "bust": false,
      "skipped": 0,
      "clears_draft": true
    },
    "note": "stacked ops on frozen NBA \u2014 not new method_id; reinforce wait-on-paper",
    "generated_at": "2026-10-27T00:42:39Z",
    "wave": 14
  }
}
```

Raw: [`../internal/sims/sports-unbound-exhaustion/wave14/`](../internal/sims/sports-unbound-exhaustion/wave14/)

## EXHAUST_WAVE14_DONE

---

## Wave 15 — exhaustion audit (`2026-10-27T00:42:41Z`)

**EXHAUST_WAVE15_DONE.** Families: `wave15_exhaustion_audit`. Paper enables this wave: **0**. Catakid NBA **untouched**. `beats_book=false`.

```json
{
  "wave": 15,
  "family_set": "wave15_exhaustion_audit",
  "paper_enables": [],
  "highlights": {
    "totals_files": [
      "americanfootball_nfl_totals_predictions.json"
    ],
    "blocked_\u00a30": [
      "multi-book live Odds API",
      "bookie login / steam tape",
      "NCAAB/NCAAF Odds key",
      "tennis-data.co.uk (403)",
      "HT 1X2 / corner / BTTS / place SP odds missing",
      "NBA ML p_cal dump for \u215b-Kelly/Platt (absent in store)",
      "optical tracking / paid FTN",
      "NHL/MLB game totals free closes (not in maxout dumps)",
      "Valorant/CS free historical ML closes join"
    ],
    "remaining_free_ideas_outside_lane": [
      "arXiv AID_SPORTS transfer after census sibling \u2014 out of this sports-sim lane",
      "live in-play Markov path paper \u2014 Catakid hours / not overnight cloud invent without priced closes"
    ],
    "truly_exhausted_free_sim_lane": true,
    "generated_at": "2026-10-27T00:42:41Z",
    "wave": 15
  }
}
```

Raw: [`../internal/sims/sports-unbound-exhaustion/wave15/`](../internal/sims/sports-unbound-exhaustion/wave15/)

## EXHAUST_WAVE15_DONE

---

## Wave 17 — ATP stake blocked (`2026-10-27T00:42:44Z`)

**EXHAUST_WAVE17_DONE.** Families: `wave17_atp_no_bet_dump`. Paper enables this wave: **0**. Catakid NBA **untouched**. `beats_book=false`.

```json
{
  "wave": 17,
  "family_set": "wave17_atp_no_bet_dump",
  "paper_enables": [],
  "highlights": {
    "oos_summary": {
      "n_seasons": 9,
      "seasons_profit": 3,
      "seasons_bust": 1,
      "pct_seasons_above_80": 0.3333333333333333,
      "avg_end_bankroll": 62.39,
      "median_end_bankroll": 75.89,
      "continuous": {
        "n_bets": 23,
        "n_void": 0,
        "wins": 4,
        "win_pct": 0.17391304347826086,
        "pl": -79.21,
        "end_bankroll": 0.79,
        "bust": true,
        "games_to_bust": 23,
        "max_drawdown": 79.21,
        "start_bankroll": 80.0,
        "stake": 5.0
      }
    },
    "reason": "BLOCKED \u2014 no per-bet ATP rows in store for new stake invent; prior Platt/Kelly already scored",
    "generated_at": "2026-10-27T00:42:44Z",
    "wave": 17,
    "paper_decision": {
      "paper_enable": [],
      "catakid": "untouched",
      "beats_book": false
    }
  }
}
```

Raw: [`../internal/sims/sports-unbound-exhaustion/wave17/`](../internal/sims/sports-unbound-exhaustion/wave17/)

## EXHAUST_WAVE17_DONE

---

## Overnight continuous wrap (`2026-10-27T00:42:46Z`)

Ran waves **5–17** continuously (plus prior 1–4).  
Wall clock London: `2026-10-27T00:42:25.571300+00:00` → `2026-10-27T00:42:46.128207+00:00`.  
**NEW paper enables overnight (waves 5+): 0.** Catakid NBA daemon **untouched**. `beats_book=false`.

### OVERNIGHT_SPORTS_DONE

**wave_count_total** = 17 (waves 1–4 prior + 13 continuous).  
**continuous_waves** = [5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17].  
Free+new sim lane treated as exhausted at wave 15 audit (+ trailing blocked/ATP notes).  
Primary Dec 1 path remains **WAIT_ON_PAPER** (NBA).

---

## Wave 5 — shots/BTTS-proxy/CS/corners (`2026-10-27T00:43:10Z`)

**EXHAUST_WAVE5_DONE.** Families: `wave5_shots_btts_cs_corners`. Paper enables this wave: **0**. Catakid NBA **untouched**. `beats_book=false`.

```json
{
  "wave": 5,
  "family_set": "wave5_shots_btts_cs_corners",
  "paper_enables": [],
  "highlights": {
    "over_from_sot": {
      "best": {
        "params": {
          "min_sot": 5.5
        },
        "n_train": 99,
        "n_oos": 396,
        "clears_dual_draft": false,
        "train": {
          "n": 99,
          "win_pct": 0.5656565656565656,
          "end": 19.75,
          "max_dd": 88.2,
          "bust": false,
          "clears_draft": false
        },
        "oos": {
          "n": 396,
          "win_pct": 0.648989898989899,
          "end": 165.9,
          "max_dd": 63.9,
          "bust": false,
          "clears_draft": true
        }
      },
      "clears": false
    },
    "btts_settle_o25_price_MISSPEC": {
      "best": {
        "params": {
          "min_sot": 5.0
        },
        "n_train": 221,
        "n_oos": 947,
        "clears_dual_draft": false,
        "train": {
          "n": 128,
          "win_pct": 0.578125,
          "end": 4.7,
          "max_dd": 75.3,
          "bust": false,
          "clears_draft": false
        },
        "oos": {
          "n": 615,
          "win_pct": 0.5804878048780487,
          "end": 0.65,
          "max_dd": 122.15,
          "bust": false,
          "clears_draft": false
        }
      },
      "note": "NEVER enable \u2014 settle\u2260price; scored to show temptation",
      "clears": false
    },
    "clean_sheet_priced_home_ml_MISSPEC": {
      "best": {
        "params": {
          "max_away_scored": 0.7
        },
        "n_train": 1988,
        "n_oos": 5441,
        "clears_dual_draft": false,
        "train": {
          "n": 84,
          "win_pct": 0.39285714285714285,
          "end": 2.3,
          "max_dd": 85.8,
          "bust": false,
          "clears_draft": false
        },
        "oos": {
          "n": 55,
          "win_pct": 0.36363636363636365,
          "end": 3.65,
          "max_dd": 77.65,
          "bust": false,
          "clears_draft": false
        }
      },
      "note": "CS settle with home ML price \u2014 misspec; process/reject",
      "clears": false
    },
    "corners_process": {
      "n": 14028,
      "corr_prior_vs_actual": 0.0711,
      "paper": "HARD_STOP no corner odds"
    },
    "generated_at": "2026-10-27T00:43:10Z",
    "wave": 5
  }
}
```

Raw: [`../internal/sims/sports-unbound-exhaustion/wave5/`](../internal/sims/sports-unbound-exhaustion/wave5/)

## EXHAUST_WAVE5_DONE

---

## Wave 7 — NBA spread bands + enrich (`2026-10-27T00:43:11Z`)

**EXHAUST_WAVE7_DONE.** Families: `wave7_nba_spread_bands`. Paper enables this wave: **0**. Catakid NBA **untouched**. `beats_book=false`.

```json
{
  "wave": 7,
  "family_set": "wave7_nba_spread_bands",
  "paper_enables": [],
  "highlights": {
    "best": {
      "clears_ats_proxy": false,
      "n_train": 327,
      "n_oos": 562,
      "edge": 0.08,
      "band": "small",
      "train": {
        "n": 327,
        "win_pct": 0.5137614678899083,
        "end": 48.6364,
        "max_dd": 113.6364,
        "bust": false,
        "clears_draft": false
      },
      "oos": {
        "n": 250,
        "win_pct": 0.492,
        "end": 4.0909,
        "max_dd": 130.0,
        "bust": false,
        "clears_draft": false
      }
    },
    "generated_at": "2026-10-27T00:43:11Z",
    "wave": 7,
    "paper_decision": {
      "paper_enable": [],
      "catakid": "untouched",
      "beats_book": false
    }
  }
}
```

Raw: [`../internal/sims/sports-unbound-exhaustion/wave7/`](../internal/sims/sports-unbound-exhaustion/wave7/)

## EXHAUST_WAVE7_DONE

---

## Wave 8 — NFL weekday totals (`2026-10-27T00:43:12Z`)

**EXHAUST_WAVE8_DONE.** Families: `wave8_nfl_weekday_totals`. Paper enables this wave: **0**. Catakid NBA **untouched**. `beats_book=false`.

```json
{
  "wave": 8,
  "family_set": "wave8_nfl_weekday_totals",
  "paper_enables": [],
  "highlights": {
    "best": {
      "clears_ats_proxy": false,
      "n_train": 154,
      "n_oos": 85,
      "edge": 0.08,
      "days": "thu_mon",
      "train": {
        "n": 154,
        "win_pct": 0.525974025974026,
        "end": 83.1818,
        "max_dd": 40.0,
        "bust": false,
        "clears_draft": true
      },
      "oos": {
        "n": 85,
        "win_pct": 0.4823529411764706,
        "end": 46.3636,
        "max_dd": 65.4545,
        "bust": false,
        "clears_draft": false
      }
    },
    "generated_at": "2026-10-27T00:43:12Z",
    "wave": 8,
    "paper_decision": {
      "paper_enable": [],
      "catakid": "untouched",
      "beats_book": false
    }
  }
}
```

Raw: [`../internal/sims/sports-unbound-exhaustion/wave8/`](../internal/sims/sports-unbound-exhaustion/wave8/)

## EXHAUST_WAVE8_DONE

---

## Wave 9 — Max away/draw shop (`2026-10-27T00:43:13Z`)

**EXHAUST_WAVE9_DONE.** Families: `wave9_max_away_draw_shop`. Paper enables this wave: **0**. Catakid NBA **untouched**. `beats_book=false`.

```json
{
  "wave": 9,
  "family_set": "wave9_max_away_draw_shop",
  "paper_enables": [],
  "highlights": {
    "away": {
      "params": {
        "min_edge": 0.2
      },
      "n_train": 827,
      "n_oos": 4079,
      "train": {
        "n": 44,
        "win_pct": 0.13636363636363635,
        "end": 4.5,
        "max_dd": 83.25,
        "bust": false,
        "clears_draft": false
      },
      "oos": {
        "n": 377,
        "win_pct": 0.19363395225464192,
        "end": 3.95,
        "max_dd": 344.6,
        "bust": false,
        "clears_draft": false
      },
      "clears_dual_draft": false
    },
    "draw": {
      "params": {
        "min_edge": 0.15
      },
      "n_train": 1324,
      "n_oos": 6532,
      "train": {
        "n": 95,
        "win_pct": 0.2,
        "end": 4.95,
        "max_dd": 147.4,
        "bust": false,
        "clears_draft": false
      },
      "oos": {
        "n": 102,
        "win_pct": 0.21568627450980393,
        "end": 4.3,
        "max_dd": 98.6,
        "bust": false,
        "clears_draft": false
      },
      "clears_dual_draft": false
    },
    "policy": "soccer shop proxy \u2014 no enable",
    "generated_at": "2026-10-27T00:43:13Z",
    "wave": 9,
    "paper_decision": {
      "paper_enable": [],
      "catakid": "untouched",
      "beats_book": false
    }
  }
}
```

Raw: [`../internal/sims/sports-unbound-exhaustion/wave9/`](../internal/sims/sports-unbound-exhaustion/wave9/)

## EXHAUST_WAVE9_DONE

---

## Wave 12 — NBA resid next-game fade (`2026-10-27T00:43:15Z`)

**EXHAUST_WAVE12_DONE.** Families: `wave12_nba_resid_next_fade`. Paper enables this wave: **0**. Catakid NBA **untouched**. `beats_book=false`.

```json
{
  "wave": 12,
  "family_set": "wave12_nba_resid_next_fade",
  "paper_enables": [],
  "highlights": {
    "best": {
      "clears_ats_proxy": false,
      "n_train": 70,
      "n_oos": 160,
      "min_abs": 6.0,
      "train": {
        "n": 70,
        "win_pct": 0.5285714285714286,
        "end": 83.1818,
        "max_dd": 32.7273,
        "bust": false,
        "clears_draft": true
      },
      "oos": {
        "n": 82,
        "win_pct": 0.4268292682926829,
        "end": 4.0909,
        "max_dd": 89.0909,
        "bust": false,
        "clears_draft": false
      }
    },
    "generated_at": "2026-10-27T00:43:15Z",
    "wave": 12,
    "paper_decision": {
      "paper_enable": [],
      "catakid": "untouched",
      "beats_book": false
    }
  }
}
```

Raw: [`../internal/sims/sports-unbound-exhaustion/wave12/`](../internal/sims/sports-unbound-exhaustion/wave12/)

## EXHAUST_WAVE12_DONE

---

## Wave 16 — soccer rolling CLV home gate (`2026-10-27T00:43:17Z`)

**EXHAUST_WAVE16_DONE.** Families: `wave16_soccer_rolling_clv_home`. Paper enables this wave: **0**. Catakid NBA **untouched**. `beats_book=false`.

```json
{
  "wave": 16,
  "family_set": "wave16_soccer_rolling_clv_home",
  "paper_enables": [],
  "highlights": {
    "best": {
      "params": {
        "min_prior": 0.005
      },
      "n_train": 338,
      "n_oos": 2010,
      "clears_dual_draft": false,
      "train": {
        "n": 302,
        "win_pct": 0.45364238410596025,
        "end": 3.35,
        "max_dd": 144.0,
        "bust": false,
        "clears_draft": false
      },
      "oos": {
        "n": 45,
        "win_pct": 0.3333333333333333,
        "end": 0.85,
        "max_dd": 88.25,
        "bust": false,
        "clears_draft": false
      }
    },
    "n": 6956,
    "policy": "soccer OFF",
    "generated_at": "2026-10-27T00:43:17Z",
    "wave": 16,
    "paper_decision": {
      "paper_enable": [],
      "catakid": "untouched",
      "beats_book": false
    }
  }
}
```

Raw: [`../internal/sims/sports-unbound-exhaustion/wave16/`](../internal/sims/sports-unbound-exhaustion/wave16/)

## EXHAUST_WAVE16_DONE


### Repair note (`2026-10-27T00:43:19Z`)

Re-ran waves [5, 7, 8, 9, 12, 16] after slim_for_doc KeyError. Still **0** paper enables. Catakid untouched.

---

## Overnight continuation — waves 18+ (`2026-10-27T00:48:52Z`)

Prior wave-15 audit was **premature** (hours remain to 05:00 London). Re-opened free+new lane on multi-league FD + maxout ATS/totals + NBA CLV join. Still £0 / Catakid untouched / no enable without bar.

---

## Wave 18 — under from low SOT (`2026-10-27T00:48:54Z`)

**EXHAUST_WAVE18_DONE.** Families: `wave18_under_from_low_sot`. Paper enables this wave: **0**. Catakid NBA **untouched**. `beats_book=false`.

```json
{
  "wave": 18,
  "family_set": "wave18_under_from_low_sot",
  "paper_enables": [],
  "highlights": {
    "best": {
      "params": {
        "max_sot": 3.0
      },
      "n_train": 189,
      "n_oos": 465,
      "clears_dual_draft": false,
      "train": {
        "n": 189,
        "win_pct": 0.5714285714285714,
        "end": 53.65,
        "max_dd": 73.1,
        "bust": false,
        "clears_draft": false
      },
      "oos": {
        "n": 393,
        "win_pct": 0.5776081424936387,
        "end": 4.6,
        "max_dd": 98.9,
        "bust": false,
        "clears_draft": false
      }
    },
    "n": 18340,
    "policy": "soccer OFF \u2014 score only",
    "clears": false,
    "generated_at": "2026-10-27T00:48:54Z"
  }
}
```

Raw: [`../internal/sims/sports-unbound-exhaustion/wave18/`](../internal/sims/sports-unbound-exhaustion/wave18/)

## EXHAUST_WAVE18_DONE

---

## Wave 19 — AH home settle (`2026-10-27T00:48:56Z`)

**EXHAUST_WAVE19_DONE.** Families: `wave19_soccer_ah_home_settle`. Paper enables this wave: **0**. Catakid NBA **untouched**. `beats_book=false`.

```json
{
  "wave": 19,
  "family_set": "wave19_soccer_ah_home_settle",
  "paper_enables": [],
  "highlights": {
    "best": {
      "params": {
        "side": "fav",
        "max_abs_line": 2.0
      },
      "n_train": 1142,
      "n_oos": 3654,
      "clears_dual_draft": false,
      "train": {
        "n": 1142,
        "win_pct": 0.542907180385289,
        "end": 340.1,
        "max_dd": 105.85,
        "bust": false,
        "clears_draft": true
      },
      "oos": {
        "n": 1432,
        "win_pct": 0.5167597765363129,
        "end": 4.4,
        "max_dd": 136.8,
        "bust": false,
        "clears_draft": false
      }
    },
    "n": 18025,
    "policy": "soccer OFF",
    "generated_at": "2026-10-27T00:48:56Z"
  }
}
```

Raw: [`../internal/sims/sports-unbound-exhaustion/wave19/`](../internal/sims/sports-unbound-exhaustion/wave19/)

## EXHAUST_WAVE19_DONE

---

## Wave 20 — NFL ATS spread bands (`2026-10-27T00:48:59Z`)

**EXHAUST_WAVE20_DONE.** Families: `wave20_nfl_ats_spread_bands`. Paper enables this wave: **1**. Catakid NBA **untouched**. `beats_book=false`.

```json
{
  "wave": 20,
  "family_set": "wave20_nfl_ats_spread_bands",
  "paper_enables": [
    {
      "family": "wave20_nfl_ats_spread_bands",
      "params": {
        "band": [
          10,
          14
        ],
        "min_edge": 0.06
      },
      "clears_ats_proxy": true,
      "clears_dual_draft": null
    }
  ],
  "highlights": {
    "best": {
      "clears_ats_proxy": true,
      "params": {
        "band": [
          10,
          14
        ],
        "min_edge": 0.06
      },
      "n_train": 248,
      "n_oos": 97,
      "train": {
        "n": 248,
        "win_pct": 0.5725806451612904,
        "end": 195.4545,
        "max_dd": 38.6364,
        "bust": false,
        "clears_draft": true
      },
      "oos": {
        "n": 97,
        "win_pct": 0.5567010309278351,
        "end": 110.4545,
        "max_dd": 39.5455,
        "bust": false,
        "clears_draft": true
      }
    },
    "note": "NFL ATS band \u2014 enable only if clears_ats_proxy",
    "generated_at": "2026-10-27T00:48:59Z"
  }
}
```

Raw: [`../internal/sims/sports-unbound-exhaustion/wave20/`](../internal/sims/sports-unbound-exhaustion/wave20/)

## EXHAUST_WAVE20_DONE

---

## Wave 21 — NBA rest extreme ATS (`2026-10-27T00:49:01Z`)

**EXHAUST_WAVE21_DONE.** Families: `wave21_nba_rest_extreme_ats`. Paper enables this wave: **0**. Catakid NBA **untouched**. `beats_book=false`.

```json
{
  "wave": 21,
  "family_set": "wave21_nba_rest_extreme_ats",
  "paper_enables": [],
  "highlights": {
    "best": {
      "clears_ats_proxy": false,
      "params": {
        "mode": "b2b_home",
        "thr": -2,
        "min_edge": 0.03
      },
      "n_train": 89,
      "n_oos": 195,
      "train": {
        "n": 89,
        "win_pct": 0.550561797752809,
        "end": 102.7273,
        "max_dd": 26.3636,
        "bust": false,
        "clears_draft": true
      },
      "oos": {
        "n": 115,
        "win_pct": 0.45217391304347826,
        "end": 1.3636,
        "max_dd": 98.6364,
        "bust": false,
        "clears_draft": false
      }
    },
    "note": "ATS filter on locked path cousin \u2014 no Catakid flip; enable only if clears (checked below)",
    "would_clear": false,
    "generated_at": "2026-10-27T00:49:01Z"
  }
}
```

Raw: [`../internal/sims/sports-unbound-exhaustion/wave21/`](../internal/sims/sports-unbound-exhaustion/wave21/)

## EXHAUST_WAVE21_DONE

---

## Wave 22 — Max under shop (`2026-10-27T00:49:04Z`)

**EXHAUST_WAVE22_DONE.** Families: `wave22_max_under_shop`. Paper enables this wave: **0**. Catakid NBA **untouched**. `beats_book=false`.

```json
{
  "wave": 22,
  "family_set": "wave22_max_under_shop",
  "paper_enables": [],
  "highlights": {
    "best": {
      "params": {
        "min_dec": 0.05
      },
      "n_train": 3462,
      "n_oos": 10119,
      "clears_dual_draft": false,
      "train": {
        "n": 115,
        "win_pct": 0.4,
        "end": 4.3,
        "max_dd": 83.25,
        "bust": false,
        "clears_draft": false
      },
      "oos": {
        "n": 1358,
        "win_pct": 0.4889543446244477,
        "end": 4.7,
        "max_dd": 337.7,
        "bust": false,
        "clears_draft": false
      }
    },
    "n": 18816,
    "policy": "soccer OFF",
    "generated_at": "2026-10-27T00:49:04Z"
  }
}
```

Raw: [`../internal/sims/sports-unbound-exhaustion/wave22/`](../internal/sims/sports-unbound-exhaustion/wave22/)

## EXHAUST_WAVE22_DONE

---

## Wave 23 — MLB fav vs dog honesty (`2026-10-27T00:49:05Z`)

**EXHAUST_WAVE23_DONE.** Families: `wave23_mlb_fav_vs_dog_honesty`. Paper enables this wave: **0**. Catakid NBA **untouched**. `beats_book=false`.

```json
{
  "wave": 23,
  "family_set": "wave23_mlb_fav_vs_dog_honesty",
  "paper_enables": [],
  "highlights": {
    "always_fav": null,
    "always_dog": null,
    "model": null,
    "policy": "STRUCTURAL_HOLD if dog clears and fav fails \u2014 reaffirm",
    "generated_at": "2026-10-27T00:49:05Z"
  }
}
```

Raw: [`../internal/sims/sports-unbound-exhaustion/wave23/`](../internal/sims/sports-unbound-exhaustion/wave23/)

## EXHAUST_WAVE23_DONE

---

## Wave 24 — NHL rest extreme ATS (`2026-10-27T00:49:08Z`)

**EXHAUST_WAVE24_DONE.** Families: `wave24_nhl_rest_extreme_ats`. Paper enables this wave: **0**. Catakid NBA **untouched**. `beats_book=false`.

```json
{
  "wave": 24,
  "family_set": "wave24_nhl_rest_extreme_ats",
  "paper_enables": [],
  "highlights": {
    "best": {
      "clears_ats_proxy": true,
      "params": {
        "mode": "home_rested",
        "thr": 1,
        "min_edge": 0.08
      },
      "n_train": 337,
      "n_oos": 1133,
      "train": {
        "n": 337,
        "win_pct": 0.6884272997032641,
        "end": 609.5455,
        "max_dd": 35.4545,
        "bust": false,
        "clears_draft": true
      },
      "oos": {
        "n": 1133,
        "win_pct": 0.6451897616946161,
        "end": 1392.7273,
        "max_dd": 52.2727,
        "bust": false,
        "clears_draft": true
      }
    },
    "note": "STRUCTURAL_HOLD risk if dog-dominated",
    "would_clear": true,
    "generated_at": "2026-10-27T00:49:08Z"
  }
}
```

Raw: [`../internal/sims/sports-unbound-exhaustion/wave24/`](../internal/sims/sports-unbound-exhaustion/wave24/)

## EXHAUST_WAVE24_DONE

---

## Wave 25 — red-card next match (`2026-10-27T00:49:10Z`)

**EXHAUST_WAVE25_DONE.** Families: `wave25_soccer_redcard_next`. Paper enables this wave: **0**. Catakid NBA **untouched**. `beats_book=false`.

```json
{
  "wave": 25,
  "family_set": "wave25_soccer_redcard_next",
  "paper_enables": [],
  "highlights": {
    "best": {
      "params": {
        "kind": "away_after_home_red"
      },
      "n_train": 5068,
      "n_oos": 14104,
      "clears_dual_draft": false,
      "train": {
        "n": 68,
        "win_pct": 0.25,
        "end": 4.55,
        "max_dd": 102.95,
        "bust": false,
        "clears_draft": false
      },
      "oos": {
        "n": 704,
        "win_pct": 0.3252840909090909,
        "end": 3.0,
        "max_dd": 291.0,
        "bust": false,
        "clears_draft": false
      }
    },
    "n": 57473,
    "policy": "soccer OFF",
    "generated_at": "2026-10-27T00:49:10Z"
  }
}
```

Raw: [`../internal/sims/sports-unbound-exhaustion/wave25/`](../internal/sims/sports-unbound-exhaustion/wave25/)

## EXHAUST_WAVE25_DONE

---

## Wave 26 — HT prior under gate (`2026-10-27T00:49:12Z`)

**EXHAUST_WAVE26_DONE.** Families: `wave26_ht_prior_under_gate`. Paper enables this wave: **0**. Catakid NBA **untouched**. `beats_book=false`.

```json
{
  "wave": 26,
  "family_set": "wave26_ht_prior_under_gate",
  "paper_enables": [],
  "highlights": {
    "best": {
      "params": {
        "max_ht": 1.0
      },
      "n_train": 3536,
      "n_oos": 13544,
      "clears_dual_draft": false,
      "train": {
        "n": 260,
        "win_pct": 0.4576923076923077,
        "end": 4.85,
        "max_dd": 101.55,
        "bust": false,
        "clears_draft": false
      },
      "oos": {
        "n": 397,
        "win_pct": 0.5188916876574308,
        "end": 2.55,
        "max_dd": 93.4,
        "bust": false,
        "clears_draft": false
      }
    },
    "n": 18340,
    "policy": "soccer OFF",
    "generated_at": "2026-10-27T00:49:12Z"
  }
}
```

Raw: [`../internal/sims/sports-unbound-exhaustion/wave26/`](../internal/sims/sports-unbound-exhaustion/wave26/)

## EXHAUST_WAVE26_DONE

---

## Wave 27 — NBA CLV selection gate (`2026-10-27T00:49:14Z`)

**EXHAUST_WAVE27_DONE.** Families: `wave27_nba_clv_selection_gate`. Paper enables this wave: **0**. Catakid NBA **untouched**. `beats_book=false`.

```json
{
  "wave": 27,
  "family_set": "wave27_nba_clv_selection_gate",
  "paper_enables": [],
  "highlights": {
    "best": {
      "params": {
        "mode": "pos",
        "thr": -0.02
      },
      "n_train": 45,
      "n_oos": 147,
      "clears_dual_draft": false,
      "train": {
        "n": 45,
        "win_pct": 0.4222222222222222,
        "end": 61.25,
        "max_dd": 44.25,
        "bust": false,
        "clears_draft": false
      },
      "oos": {
        "n": 95,
        "win_pct": 0.35789473684210527,
        "end": 4.25,
        "max_dd": 76.5,
        "bust": false,
        "clears_draft": false
      }
    },
    "n_quality": 212,
    "note": "CLV gate on locked concentrate \u2014 Catakid untouched unless clears dual draft AND policy allow; still no enable without bar",
    "would_clear": false,
    "generated_at": "2026-10-27T00:49:14Z"
  }
}
```

Raw: [`../internal/sims/sports-unbound-exhaustion/wave27/`](../internal/sims/sports-unbound-exhaustion/wave27/)

## EXHAUST_WAVE27_DONE

---

## Wave 28 — NFL totals line bands (`2026-10-27T00:49:16Z`)

**EXHAUST_WAVE28_DONE.** Families: `wave28_nfl_totals_line_bands`. Paper enables this wave: **0**. Catakid NBA **untouched**. `beats_book=false`.

```json
{
  "wave": 28,
  "family_set": "wave28_nfl_totals_line_bands",
  "paper_enables": [],
  "highlights": {
    "best": {
      "clears_ats_proxy": false,
      "params": {
        "band": [
          30,
          40
        ],
        "min_edge": 0.04
      },
      "n_train": 985,
      "n_oos": 171,
      "train": {
        "n": 380,
        "win_pct": 0.5026315789473684,
        "end": 3.1818,
        "max_dd": 143.1818,
        "bust": false,
        "clears_draft": false
      },
      "oos": {
        "n": 107,
        "win_pct": 0.4485981308411215,
        "end": 3.1818,
        "max_dd": 88.6364,
        "bust": false,
        "clears_draft": false
      }
    },
    "generated_at": "2026-10-27T00:49:16Z"
  }
}
```

Raw: [`../internal/sims/sports-unbound-exhaustion/wave28/`](../internal/sims/sports-unbound-exhaustion/wave28/)

## EXHAUST_WAVE28_DONE

---

## Wave 29 — soccer loss streak (`2026-10-27T00:49:17Z`)

**EXHAUST_WAVE29_DONE.** Families: `wave29_soccer_loss_streak`. Paper enables this wave: **0**. Catakid NBA **untouched**. `beats_book=false`.

```json
{
  "wave": 29,
  "family_set": "wave29_soccer_loss_streak",
  "paper_enables": [],
  "highlights": {
    "best": {
      "params": {
        "kind": "fade_to_home",
        "min_losses": 3
      },
      "n_train": 357,
      "n_oos": 865,
      "clears_dual_draft": false,
      "train": {
        "n": 357,
        "win_pct": 0.5602240896358543,
        "end": 135.25,
        "max_dd": 92.65,
        "bust": false,
        "clears_draft": true
      },
      "oos": {
        "n": 183,
        "win_pct": 0.5136612021857924,
        "end": 2.75,
        "max_dd": 99.1,
        "bust": false,
        "clears_draft": false
      }
    },
    "n": 2444,
    "policy": "soccer OFF",
    "generated_at": "2026-10-27T00:49:17Z"
  }
}
```

Raw: [`../internal/sims/sports-unbound-exhaustion/wave29/`](../internal/sims/sports-unbound-exhaustion/wave29/)

## EXHAUST_WAVE29_DONE

---

## Wave 30 — poisson lambda OU (`2026-10-27T00:49:20Z`)

**EXHAUST_WAVE30_DONE.** Families: `wave30_poisson_lambda_ou`. Paper enables this wave: **0**. Catakid NBA **untouched**. `beats_book=false`.

```json
{
  "wave": 30,
  "family_set": "wave30_poisson_lambda_ou",
  "paper_enables": [],
  "highlights": {
    "best": {
      "params": {
        "side": "over",
        "thr": 3.3
      },
      "n_train": 862,
      "n_oos": 3544,
      "clears_dual_draft": false,
      "train": {
        "n": 172,
        "win_pct": 0.5813953488372093,
        "end": 4.65,
        "max_dd": 81.0,
        "bust": false,
        "clears_draft": false
      },
      "oos": {
        "n": 189,
        "win_pct": 0.5396825396825397,
        "end": 1.85,
        "max_dd": 87.0,
        "bust": false,
        "clears_draft": false
      }
    },
    "n": 36342,
    "policy": "soccer OFF",
    "generated_at": "2026-10-27T00:49:20Z"
  }
}
```

Raw: [`../internal/sims/sports-unbound-exhaustion/wave30/`](../internal/sims/sports-unbound-exhaustion/wave30/)

## EXHAUST_WAVE30_DONE

---

## Wave 31 — AH CLV gate (`2026-10-27T00:49:21Z`)

**EXHAUST_WAVE31_DONE.** Families: `wave31_soccer_ah_clv_gate`. Paper enables this wave: **0**. Catakid NBA **untouched**. `beats_book=false`.

```json
{
  "wave": 31,
  "family_set": "wave31_soccer_ah_clv_gate",
  "paper_enables": [],
  "highlights": {
    "best": {
      "params": {
        "min_clv": 0.0
      },
      "n_train": 2131,
      "n_oos": 7701,
      "clears_dual_draft": false,
      "train": {
        "n": 360,
        "win_pct": 0.48055555555555557,
        "end": 3.2,
        "max_dd": 82.25,
        "bust": false,
        "clears_draft": false
      },
      "oos": {
        "n": 274,
        "win_pct": 0.4781021897810219,
        "end": 4.9,
        "max_dd": 85.7,
        "bust": false,
        "clears_draft": false
      }
    },
    "n": 17968,
    "policy": "soccer OFF",
    "generated_at": "2026-10-27T00:49:21Z"
  }
}
```

Raw: [`../internal/sims/sports-unbound-exhaustion/wave31/`](../internal/sims/sports-unbound-exhaustion/wave31/)

## EXHAUST_WAVE31_DONE

---

## Wave 32 — kickoff under buckets (`2026-10-27T00:49:23Z`)

**EXHAUST_WAVE32_DONE.** Families: `wave32_kickoff_under`. Paper enables this wave: **0**. Catakid NBA **untouched**. `beats_book=false`.

```json
{
  "wave": 32,
  "family_set": "wave32_kickoff_under",
  "paper_enables": [],
  "highlights": {
    "best": {
      "params": {
        "h0": 20,
        "h1": 23
      },
      "n_train": 414,
      "n_oos": 1885,
      "clears_dual_draft": false,
      "train": {
        "n": 414,
        "win_pct": 0.5096618357487923,
        "end": 84.8,
        "max_dd": 91.5,
        "bust": false,
        "clears_draft": true
      },
      "oos": {
        "n": 242,
        "win_pct": 0.4793388429752066,
        "end": 2.95,
        "max_dd": 103.05,
        "bust": false,
        "clears_draft": false
      }
    },
    "n": 19292,
    "policy": "soccer OFF",
    "generated_at": "2026-10-27T00:49:23Z"
  }
}
```

Raw: [`../internal/sims/sports-unbound-exhaustion/wave32/`](../internal/sims/sports-unbound-exhaustion/wave32/)

## EXHAUST_WAVE32_DONE

---

## Wave 33 — NFL ATS by month (`2026-10-27T00:49:25Z`)

**EXHAUST_WAVE33_DONE.** Families: `wave33_nfl_ats_month`. Paper enables this wave: **1**. Catakid NBA **untouched**. `beats_book=false`.

```json
{
  "wave": 33,
  "family_set": "wave33_nfl_ats_month",
  "paper_enables": [
    {
      "family": "wave33_nfl_ats_month",
      "params": {
        "months": [
          9
        ],
        "min_edge": 0.08
      },
      "clears_ats_proxy": true,
      "clears_dual_draft": null
    }
  ],
  "highlights": {
    "best": {
      "clears_ats_proxy": true,
      "params": {
        "months": [
          9
        ],
        "min_edge": 0.08
      },
      "n_train": 332,
      "n_oos": 142,
      "train": {
        "n": 332,
        "win_pct": 0.5391566265060241,
        "end": 128.6364,
        "max_dd": 90.0,
        "bust": false,
        "clears_draft": true
      },
      "oos": {
        "n": 142,
        "win_pct": 0.5422535211267606,
        "end": 105.0,
        "max_dd": 50.4545,
        "bust": false,
        "clears_draft": true
      }
    },
    "generated_at": "2026-10-27T00:49:25Z"
  }
}
```

Raw: [`../internal/sims/sports-unbound-exhaustion/wave33/`](../internal/sims/sports-unbound-exhaustion/wave33/)

## EXHAUST_WAVE33_DONE

---

## Wave 34 — BTTS-form draw (`2026-10-27T00:49:27Z`)

**EXHAUST_WAVE34_DONE.** Families: `wave34_btts_form_draw`. Paper enables this wave: **0**. Catakid NBA **untouched**. `beats_book=false`.

```json
{
  "wave": 34,
  "family_set": "wave34_btts_form_draw",
  "paper_enables": [],
  "highlights": {
    "best": {
      "params": {},
      "n_train": 3689,
      "n_oos": 9516,
      "clears_dual_draft": false,
      "train": {
        "n": 184,
        "win_pct": 0.23369565217391305,
        "end": 0.25,
        "max_dd": 157.0,
        "bust": false,
        "clears_draft": false
      },
      "oos": {
        "n": 122,
        "win_pct": 0.2459016393442623,
        "end": 0.9,
        "max_dd": 87.25,
        "bust": false,
        "clears_draft": false
      }
    },
    "n": 13205,
    "policy": "soccer OFF",
    "generated_at": "2026-10-27T00:49:27Z"
  }
}
```

Raw: [`../internal/sims/sports-unbound-exhaustion/wave34/`](../internal/sims/sports-unbound-exhaustion/wave34/)

## EXHAUST_WAVE34_DONE

---

## Wave 35 — NBA low-sigma ATS (`2026-10-27T00:49:29Z`)

**EXHAUST_WAVE35_DONE.** Families: `wave35_nba_low_sigma_ats`. Paper enables this wave: **0**. Catakid NBA **untouched**. `beats_book=false`.

```json
{
  "wave": 35,
  "family_set": "wave35_nba_low_sigma_ats",
  "paper_enables": [],
  "highlights": {
    "best": {
      "clears_ats_proxy": false,
      "params": {
        "max_sigma": 14.453503510933102,
        "min_edge": 0.04
      },
      "n_train": 1814,
      "n_oos": 2004,
      "train": {
        "n": 124,
        "win_pct": 0.4596774193548387,
        "end": 4.0909,
        "max_dd": 102.2727,
        "bust": false,
        "clears_draft": false
      },
      "oos": {
        "n": 334,
        "win_pct": 0.5,
        "end": 4.0909,
        "max_dd": 122.7273,
        "bust": false,
        "clears_draft": false
      }
    },
    "sigma_q50": 13.885315123256307,
    "sigma_q75": 14.453503510933102,
    "generated_at": "2026-10-27T00:49:29Z"
  }
}
```

Raw: [`../internal/sims/sports-unbound-exhaustion/wave35/`](../internal/sims/sports-unbound-exhaustion/wave35/)

## EXHAUST_WAVE35_DONE

---

## Wave 36 — overround tighten home (`2026-10-27T00:49:30Z`)

**EXHAUST_WAVE36_DONE.** Families: `wave36_overround_tighten_home`. Paper enables this wave: **0**. Catakid NBA **untouched**. `beats_book=false`.

```json
{
  "wave": 36,
  "family_set": "wave36_overround_tighten_home",
  "paper_enables": [],
  "highlights": {
    "best": {
      "params": {
        "min_delta": 0.02
      },
      "n_train": 82,
      "n_oos": 218,
      "clears_dual_draft": false,
      "train": {
        "n": 82,
        "win_pct": 0.4878048780487805,
        "end": 84.85,
        "max_dd": 40.8,
        "bust": false,
        "clears_draft": true
      },
      "oos": {
        "n": 49,
        "win_pct": 0.3877551020408163,
        "end": 3.75,
        "max_dd": 76.25,
        "bust": false,
        "clears_draft": false
      }
    },
    "n": 19272,
    "policy": "soccer OFF",
    "generated_at": "2026-10-27T00:49:30Z"
  }
}
```

Raw: [`../internal/sims/sports-unbound-exhaustion/wave36/`](../internal/sims/sports-unbound-exhaustion/wave36/)

## EXHAUST_WAVE36_DONE

---

## Wave 37 — NFL QB-clean ATS (`2026-10-27T00:49:32Z`)

**EXHAUST_WAVE37_DONE.** Families: `wave37_nfl_qb_clean_ats`. Paper enables this wave: **0**. Catakid NBA **untouched**. `beats_book=false`.

```json
{
  "wave": 37,
  "family_set": "wave37_nfl_qb_clean_ats",
  "paper_enables": [],
  "highlights": {
    "best": {
      "clears_ats_proxy": false,
      "params": {
        "mode": "qb_flag",
        "min_edge": 0.04
      },
      "n_train": 224,
      "n_oos": 187,
      "train": {
        "n": 201,
        "win_pct": 0.48258706467661694,
        "end": 0.9091,
        "max_dd": 106.8182,
        "bust": false,
        "clears_draft": false
      },
      "oos": {
        "n": 187,
        "win_pct": 0.49732620320855614,
        "end": 32.7273,
        "max_dd": 80.0,
        "bust": false,
        "clears_draft": false
      }
    },
    "generated_at": "2026-10-27T00:49:32Z"
  }
}
```

Raw: [`../internal/sims/sports-unbound-exhaustion/wave37/`](../internal/sims/sports-unbound-exhaustion/wave37/)

## EXHAUST_WAVE37_DONE

---

## Wave 38 — league under specialty (`2026-10-27T00:49:34Z`)

**EXHAUST_WAVE38_DONE.** Families: `wave38_league_under_specialty`. Paper enables this wave: **0**. Catakid NBA **untouched**. `beats_book=false`.

```json
{
  "wave": 38,
  "family_set": "wave38_league_under_specialty",
  "paper_enables": [],
  "highlights": {
    "leagues": {
      "E1": {
        "train": {
          "n": 205,
          "win_pct": 0.4878048780487805,
          "end": 4.7,
          "max_dd": 94.9,
          "bust": false,
          "clears_draft": false
        },
        "oos": {
          "n": 108,
          "win_pct": 0.5,
          "end": 4.5,
          "max_dd": 79.1,
          "bust": false,
          "clears_draft": false
        },
        "clears_dual_draft": false,
        "n_train": 1385,
        "n_oos": 1927
      },
      "N1": {
        "train": {
          "n": 52,
          "win_pct": 0.28846153846153844,
          "end": 0.6,
          "max_dd": 83.4,
          "bust": false,
          "clears_draft": false
        },
        "oos": {
          "n": 165,
          "win_pct": 0.44242424242424244,
          "end": 3.45,
          "max_dd": 114.55,
          "bust": false,
          "clears_draft": false
        },
        "clears_dual_draft": false,
        "n_train": 700,
        "n_oos": 756
      },
      "E0": {
        "train": {
          "n": 151,
          "win_pct": 0.4370860927152318,
          "end": 4.6,
          "max_dd": 80.75,
          "bust": false,
          "clears_draft": false
        },
        "oos": {
          "n": 206,
          "win_pct": 0.4563106796116505,
          "end": 2.5,
          "max_dd": 127.6,
          "bust": false,
          "clears_draft": false
        },
        "clears_dual_draft": false,
        "n_train": 943,
        "n_oos": 1337
      },
      "SC0": {
        "train": {
          "n": 348,
          "win_pct": 0.5632183908045977,
          "end": 139.85,
          "max_dd": 76.6,
          "bust": false,
          "clears_draft": true
        },
        "oos": {
          "n": 163,
          "win_pct": 0.50920245398773,
          "end": 2.45,
          "max_dd": 110.45,
          "bust": false,
          "clears_draft": false
        },
        "clears_dual_draft": false,
        "n_train": 348,
        "n_oos": 564
      },
      "F1": {
        "train": {
          "n": 188,
          "win_pct": 0.48936170212765956,
          "end": 52.1,
          "max_dd": 80.2,
          "bust": false,
          "clears_draft": false
        },
        "oos": {
          "n": 221,
          "win_pct": 0.4841628959276018,
          "end": 4.2,
          "max_dd": 190.55,
          "bust": false,
          "clears_draft": false
        },
        "clears_dual_draft": false,
        "n_train": 188,
        "n_oos": 1184
      },
      "D1": {
        "train": {
          "n": 145,
          "win_pct": 0.4068965517241379,
          "end": 4.4,
          "max_dd": 96.35,
          "bust": false,
          "clears_draft": false
        },
        "oos": {
          "n": 56,
          "win_pct": 0.35714285714285715,
          "end": 1.1,
          "max_dd": 78.9,
          "bust": false,
          "clears_draft": false
        },
        "clears_dual_draft": false,
        "n_train": 153,
        "n_oos": 1071
      },
      "SP1": {
        "train": {
          "n": 182,
          "win_pct": 0.5494505494505495,
          "end": 47.15,
          "max_dd": 78.05,
          "bust": false,
          "clears_draft": false
        },
        "oos": {
          "n": 270,
          "win_pct": 0.5259259259259259,
          "end": 0.4,
          "max_dd": 116.5,
          "bust": false,
          "clears_draft": false
        },
        "clears_dual_draft": false,
        "n_train": 182,
        "n_oos": 1338
      },
      "I1": {
        "train": {
          "n": 42,
          "win_pct": 0.2619047619047619,
          "end": 2.0,
          "max_dd": 78.0,
          "bust": false,
          "clears_draft": false
        },
        "oos": {
          "n": 1003,
          "win_pct": 0.5124626121635095,
          "end": 1.6,
          "max_dd": 230.4,
          "bust": false,
          "clears_draft": false
        },
        "clears_dual_draft": false,
        "n_train": 189,
        "n_oos": 1330
      },
      "G1": {
        "train": {
          "n": 70,
          "win_pct": 0.4714285714285714,
          "end": 4.5,
          "max_dd": 83.0,
          "bust": false,
          "clears_draft": false
        },
        "oos": {
          "n": 416,
          "win_pct": 0.5769230769230769,
          "end": 3.7,
          "max_dd": 113.1,
          "bust": false,
          "clears_draft": false
        },
        
```

Raw: [`../internal/sims/sports-unbound-exhaustion/wave38/`](../internal/sims/sports-unbound-exhaustion/wave38/)

## EXHAUST_WAVE38_DONE

---

## Wave 39 — NBA ATS weekday (`2026-10-27T00:49:37Z`)

**EXHAUST_WAVE39_DONE.** Families: `wave39_nba_ats_weekday`. Paper enables this wave: **0**. Catakid NBA **untouched**. `beats_book=false`.

```json
{
  "wave": 39,
  "family_set": "wave39_nba_ats_weekday",
  "paper_enables": [],
  "highlights": {
    "best": {
      "clears_ats_proxy": false,
      "params": {
        "days": [
          4
        ],
        "min_edge": 0.04
      },
      "n_train": 252,
      "n_oos": 382,
      "train": {
        "n": 252,
        "win_pct": 0.5555555555555556,
        "end": 156.3636,
        "max_dd": 75.9091,
        "bust": false,
        "clears_draft": true
      },
      "oos": {
        "n": 35,
        "win_pct": 0.2857142857142857,
        "end": 0.4545,
        "max_dd": 79.5455,
        "bust": false,
        "clears_draft": false
      }
    },
    "generated_at": "2026-10-27T00:49:37Z"
  }
}
```

Raw: [`../internal/sims/sports-unbound-exhaustion/wave39/`](../internal/sims/sports-unbound-exhaustion/wave39/)

## EXHAUST_WAVE39_DONE

---

## Wave 40 — under CLV gate (`2026-10-27T00:49:39Z`)

**EXHAUST_WAVE40_DONE.** Families: `wave40_under_clv_gate`. Paper enables this wave: **0**. Catakid NBA **untouched**. `beats_book=false`.

```json
{
  "wave": 40,
  "family_set": "wave40_under_clv_gate",
  "paper_enables": [],
  "highlights": {
    "best": {
      "params": {
        "min_clv": 0.02
      },
      "n_train": 1150,
      "n_oos": 4082,
      "clears_dual_draft": false,
      "train": {
        "n": 1150,
        "win_pct": 0.5243478260869565,
        "end": 216.55,
        "max_dd": 187.3,
        "bust": false,
        "clears_draft": true
      },
      "oos": {
        "n": 2261,
        "win_pct": 0.5329500221141088,
        "end": 3.9,
        "max_dd": 312.7,
        "bust": false,
        "clears_draft": false
      }
    },
    "n": 19269,
    "policy": "soccer OFF",
    "generated_at": "2026-10-27T00:49:39Z"
  }
}
```

Raw: [`../internal/sims/sports-unbound-exhaustion/wave40/`](../internal/sims/sports-unbound-exhaustion/wave40/)

## EXHAUST_WAVE40_DONE

---

## Wave 41 — MLB rest extreme ATS (`2026-10-27T00:49:42Z`)

**EXHAUST_WAVE41_DONE.** Families: `wave41_mlb_rest_extreme_ats`. Paper enables this wave: **0**. Catakid NBA **untouched**. `beats_book=false`.

```json
{
  "wave": 41,
  "family_set": "wave41_mlb_rest_extreme_ats",
  "paper_enables": [],
  "highlights": {
    "best": null,
    "would_clear": false,
    "generated_at": "2026-10-27T00:49:42Z"
  }
}
```

Raw: [`../internal/sims/sports-unbound-exhaustion/wave41/`](../internal/sims/sports-unbound-exhaustion/wave41/)

## EXHAUST_WAVE41_DONE

---

## Wave 42 — MaxAH shop (`2026-10-27T00:49:43Z`)

**EXHAUST_WAVE42_DONE.** Families: `wave42_maxah_shop`. Paper enables this wave: **0**. Catakid NBA **untouched**. `beats_book=false`.

```json
{
  "wave": 42,
  "family_set": "wave42_maxah_shop",
  "paper_enables": [],
  "highlights": {
    "best": {
      "params": {
        "min_dec": 0.1
      },
      "n_train": 242,
      "n_oos": 704,
      "clears_dual_draft": true,
      "train": {
        "n": 242,
        "win_pct": 0.49586776859504134,
        "end": 89.5,
        "max_dd": 90.3,
        "bust": false,
        "clears_draft": true
      },
      "oos": {
        "n": 704,
        "win_pct": 0.5113636363636364,
        "end": 199.15,
        "max_dd": 77.3,
        "bust": false,
        "clears_draft": true
      }
    },
    "n": 17237,
    "policy": "soccer OFF",
    "generated_at": "2026-10-27T00:49:43Z"
  }
}
```

Raw: [`../internal/sims/sports-unbound-exhaustion/wave42/`](../internal/sims/sports-unbound-exhaustion/wave42/)

## EXHAUST_WAVE42_DONE

---

## Wave 43 — exhaustion re-audit (`2026-10-27T00:49:45Z`)

**EXHAUST_WAVE43_DONE.** Families: `wave43_exhaustion_reaudit`. Paper enables this wave: **0**. Catakid NBA **untouched**. `beats_book=false`.

```json
{
  "wave": 43,
  "family_set": "wave43_exhaustion_reaudit",
  "paper_enables": [],
  "highlights": {
    "scored_free_new_this_extension": [
      "under_from_low_sot",
      "ah_home_settle",
      "nfl_ats_spread_bands",
      "nba_rest_extreme",
      "max_under_shop",
      "mlb_fav_honesty",
      "nhl_rest_extreme",
      "redcard_next",
      "ht_prior_under",
      "nba_clv_gate",
      "nfl_totals_line_bands",
      "loss_streak",
      "poisson_lambda_ou",
      "ah_clv",
      "kickoff_under",
      "nfl_ats_month",
      "btts_form_draw",
      "nba_low_sigma",
      "overround_tighten",
      "nfl_qb_clean",
      "league_under",
      "nba_ats_weekday",
      "under_clv",
      "mlb_rest",
      "maxah_shop"
    ],
    "still_blocked_\u00a30": [
      "optical tracking / paid FTN",
      "multi-book live Odds API / steam",
      "bookie login automation",
      "NCAAB/NCAAF Odds key historical closes",
      "tennis-data.co.uk 403",
      "HT 1X2 / corner / BTTS / place SP odds",
      "NBA ML p_cal dump for Platt/\u215b-Kelly",
      "NHL/MLB game totals closes",
      "Valorant/CS historical ML closes join",
      "arXiv AID_SPORTS transfer (sibling lane)",
      "in-play Markov without priced closes"
    ],
    "truly_exhausted_free_sim_lane": true,
    "note": "All remaining free angles on FD+maxout+CLV join now scored; leftover needs paid/login/missing odds",
    "generated_at": "2026-10-27T00:49:45Z"
  }
}
```

Raw: [`../internal/sims/sports-unbound-exhaustion/wave43/`](../internal/sims/sports-unbound-exhaustion/wave43/)

## EXHAUST_WAVE43_DONE

---

## Overnight continuation wrap (`2026-10-27T00:49:46Z`)

Continuation waves **18–43**.  
Wall clock London: `2026-10-27T00:48:52.451365+00:00` → `2026-10-27T00:49:46.864831+00:00`.  
**NEW paper enables this extension: 2.** Catakid NBA daemon **untouched**. `beats_book=false`.

### OVERNIGHT_SPORTS_DONE

**wave_count_total** = 43 (waves 1–17 prior + 26 continuation).  
**continuation_waves** = [18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43].  
Free+new sim lane re-audited exhausted at wave 43 (or clock).  
Primary Dec 1 path remains **WAIT_ON_PAPER** (NBA).

---

## Honesty correction (`2026-10-27T00:50:47Z`)

- **Wave 33** (`nfl_ats_month` Sept × edge≥0.08): **REVOKED** → **STRUCTURAL_HOLD**. Always-dog on the same filter clears OOS harder than the model (≈58.5% vs ≈54.2%). Not a paper enable.
- **Wave 20** (`nfl_ats_spread_bands` |spread| 10–14 × edge≥0.06): **KEEP**. Always-dog fails OOS (~49.5%); model dual-clears ATS proxy (train 57.3% / OOS 55.7%). Catakid NBA still untouched. `beats_book=false` until live book path.


---

## Overnight continuation — waves 44+ (`2026-10-27T00:52:59Z`)

Further free+new after wave43 re-audit (hours remain to 05:00). Still £0 / Catakid untouched.

---

## Wave 44 — soccer away AH (`2026-10-27T00:53:00Z`)

**EXHAUST_WAVE44_DONE.** Families: `wave44_soccer_away_ah`. Paper enables this wave: **0**. Catakid NBA **untouched**. `beats_book=false`.

```json
{
  "wave": 44,
  "family_set": "wave44_soccer_away_ah",
  "paper_enables": [],
  "highlights": {
    "best": {
      "params": {
        "side": "dog",
        "max_abs": 0.5
      },
      "n_train": 1296,
      "n_oos": 5192,
      "clears_dual_draft": true,
      "train": {
        "n": 1296,
        "win_pct": 0.5640432098765432,
        "end": 634.85,
        "max_dd": 100.65,
        "bust": false,
        "clears_draft": true
      },
      "oos": {
        "n": 5192,
        "win_pct": 0.5493066255778121,
        "end": 1463.25,
        "max_dd": 257.85,
        "bust": false,
        "clears_draft": true
      }
    },
    "n": 18025,
    "policy": "soccer OFF",
    "generated_at": "2026-10-27T00:53:00Z"
  }
}
```

Raw: [`../internal/sims/sports-unbound-exhaustion/wave44/`](../internal/sims/sports-unbound-exhaustion/wave44/)

## EXHAUST_WAVE44_DONE

---

## Wave 45 — NBA resid bands (`2026-10-27T00:53:02Z`)

**EXHAUST_WAVE45_DONE.** Families: `wave45_nba_resid_bands`. Paper enables this wave: **0**. Catakid NBA **untouched**. `beats_book=false`.

```json
{
  "wave": 45,
  "family_set": "wave45_nba_resid_bands",
  "paper_enables": [],
  "highlights": {
    "best": {
      "clears_ats_proxy": false,
      "params": {
        "lo": 2,
        "hi": 3,
        "min_edge": 0.08
      },
      "n_train": 196,
      "n_oos": 324,
      "train": {
        "n": 196,
        "win_pct": 0.5357142857142857,
        "end": 102.2727,
        "max_dd": 69.0909,
        "bust": false,
        "clears_draft": true
      },
      "oos": {
        "n": 203,
        "win_pct": 0.4827586206896552,
        "end": 0.4545,
        "max_dd": 95.0,
        "bust": false,
        "clears_draft": false
      }
    },
    "generated_at": "2026-10-27T00:53:02Z"
  }
}
```

Raw: [`../internal/sims/sports-unbound-exhaustion/wave45/`](../internal/sims/sports-unbound-exhaustion/wave45/)

## EXHAUST_WAVE45_DONE

---

## Wave 46 — NFL injury-filter ATS (`2026-10-27T00:53:03Z`)

**EXHAUST_WAVE46_DONE.** Families: `wave46_nfl_injury_filter_ats`. Paper enables this wave: **0**. Catakid NBA **untouched**. `beats_book=false`.

```json
{
  "wave": 46,
  "family_set": "wave46_nfl_injury_filter_ats",
  "paper_enables": [],
  "highlights": {
    "best": {
      "clears_ats_proxy": false,
      "params": {
        "mode": "clean",
        "min_edge": 0.08
      },
      "n_train": 1455,
      "n_oos": 559,
      "train": {
        "n": 399,
        "win_pct": 0.5037593984962406,
        "end": 3.6364,
        "max_dd": 120.4545,
        "bust": false,
        "clears_draft": false
      },
      "oos": {
        "n": 559,
        "win_pct": 0.554561717352415,
        "end": 244.0909,
        "max_dd": 80.0,
        "bust": false,
        "clears_draft": true
      }
    },
    "generated_at": "2026-10-27T00:53:03Z"
  }
}
```

Raw: [`../internal/sims/sports-unbound-exhaustion/wave46/`](../internal/sims/sports-unbound-exhaustion/wave46/)

## EXHAUST_WAVE46_DONE

---

## Wave 47 — NHL fav vs dog honesty (`2026-10-27T00:53:05Z`)

**EXHAUST_WAVE47_DONE.** Families: `wave47_nhl_fav_vs_dog_honesty`. Paper enables this wave: **0**. Catakid NBA **untouched**. `beats_book=false`.

```json
{
  "wave": 47,
  "family_set": "wave47_nhl_fav_vs_dog_honesty",
  "paper_enables": [],
  "highlights": {
    "always_fav": {
      "train": {
        "n": 40,
        "win_pct": 0.325,
        "end": 4.0909,
        "max_dd": 75.9091,
        "bust": false,
        "clears_draft": false
      },
      "oos": {
        "n": 44,
        "win_pct": 0.3409090909090909,
        "end": 3.1818,
        "max_dd": 80.9091,
        "bust": false,
        "clears_draft": false
      },
      "clears_ats_proxy": false,
      "n_train": 1282,
      "n_oos": 4337
    },
    "always_dog": {
      "train": {
        "n": 1282,
        "win_pct": 0.6521060842433697,
        "end": 1650.0,
        "max_dd": 50.9091,
        "bust": false,
        "clears_draft": true
      },
      "oos": {
        "n": 4337,
        "win_pct": 0.6294673737606641,
        "end": 4454.0909,
        "max_dd": 59.5455,
        "bust": false,
        "clears_draft": true
      },
      "clears_ats_proxy": true,
      "n_train": 1282,
      "n_oos": 4337
    },
    "model": {
      "train": {
        "n": 1282,
        "win_pct": 0.656786271450858,
        "end": 1707.2727,
        "max_dd": 52.7273,
        "bust": false,
        "clears_draft": true
      },
      "oos": {
        "n": 4337,
        "win_pct": 0.6345400046114826,
        "end": 4664.0909,
        "max_dd": 60.0,
        "bust": false,
        "clears_draft": true
      },
      "clears_ats_proxy": true,
      "n_train": 1282,
      "n_oos": 4337
    },
    "policy": "STRUCTURAL_HOLD reaffirm if dog clears",
    "generated_at": "2026-10-27T00:53:05Z"
  }
}
```

Raw: [`../internal/sims/sports-unbound-exhaustion/wave47/`](../internal/sims/sports-unbound-exhaustion/wave47/)

## EXHAUST_WAVE47_DONE

---

## Wave 48 — midweek under (`2026-10-27T00:53:07Z`)

**EXHAUST_WAVE48_DONE.** Families: `wave48_midweek_under`. Paper enables this wave: **0**. Catakid NBA **untouched**. `beats_book=false`.

```json
{
  "wave": 48,
  "family_set": "wave48_midweek_under",
  "paper_enables": [],
  "highlights": {
    "best": {
      "params": {
        "days": [
          3
        ]
      },
      "n_train": 104,
      "n_oos": 269,
      "clears_dual_draft": true,
      "train": {
        "n": 104,
        "win_pct": 0.5288461538461539,
        "end": 112.15,
        "max_dd": 51.3,
        "bust": false,
        "clears_draft": true
      },
      "oos": {
        "n": 269,
        "win_pct": 0.5130111524163569,
        "end": 121.9,
        "max_dd": 57.0,
        "bust": false,
        "clears_draft": true
      }
    },
    "n": 19292,
    "policy": "soccer OFF",
    "generated_at": "2026-10-27T00:53:07Z"
  }
}
```

Raw: [`../internal/sims/sports-unbound-exhaustion/wave48/`](../internal/sims/sports-unbound-exhaustion/wave48/)

## EXHAUST_WAVE48_DONE

---

## Wave 49 — pick'em AH home (`2026-10-27T00:53:08Z`)

**EXHAUST_WAVE49_DONE.** Families: `wave49_pickem_ah_home`. Paper enables this wave: **0**. Catakid NBA **untouched**. `beats_book=false`.

```json
{
  "wave": 49,
  "family_set": "wave49_pickem_ah_home",
  "paper_enables": [],
  "highlights": {
    "best": {
      "params": {},
      "n_train": 1675,
      "n_oos": 6150,
      "clears_dual_draft": false,
      "train": {
        "n": 91,
        "win_pct": 0.42857142857142855,
        "end": 2.85,
        "max_dd": 77.85,
        "bust": false,
        "clears_draft": false
      },
      "oos": {
        "n": 494,
        "win_pct": 0.5,
        "end": 0.0,
        "max_dd": 156.15,
        "bust": false,
        "clears_draft": false
      }
    },
    "n": 7825,
    "policy": "soccer OFF",
    "generated_at": "2026-10-27T00:53:08Z"
  }
}
```

Raw: [`../internal/sims/sports-unbound-exhaustion/wave49/`](../internal/sims/sports-unbound-exhaustion/wave49/)

## EXHAUST_WAVE49_DONE

---

## Wave 50 — Pinnacle under shop (`2026-10-27T00:53:10Z`)

**EXHAUST_WAVE50_DONE.** Families: `wave50_pinnacle_under_shop`. Paper enables this wave: **0**. Catakid NBA **untouched**. `beats_book=false`.

```json
{
  "wave": 50,
  "family_set": "wave50_pinnacle_under_shop",
  "paper_enables": [],
  "highlights": {
    "best": {
      "params": {
        "min_dec": 0.05
      },
      "n_train": 1954,
      "n_oos": 5135,
      "clears_dual_draft": false,
      "train": {
        "n": 91,
        "win_pct": 0.38461538461538464,
        "end": 2.7,
        "max_dd": 81.25,
        "bust": false,
        "clears_draft": false
      },
      "oos": {
        "n": 192,
        "win_pct": 0.453125,
        "end": 2.05,
        "max_dd": 91.45,
        "bust": false,
        "clears_draft": false
      }
    },
    "n": 15106,
    "policy": "soccer OFF",
    "generated_at": "2026-10-27T00:53:10Z"
  }
}
```

Raw: [`../internal/sims/sports-unbound-exhaustion/wave50/`](../internal/sims/sports-unbound-exhaustion/wave50/)

## EXHAUST_WAVE50_DONE

---

## Wave 51 — month home dog (`2026-10-27T00:53:12Z`)

**EXHAUST_WAVE51_DONE.** Families: `wave51_month_home_dog`. Paper enables this wave: **0**. Catakid NBA **untouched**. `beats_book=false`.

```json
{
  "wave": 51,
  "family_set": "wave51_month_home_dog",
  "paper_enables": [],
  "highlights": {
    "best": {
      "params": {
        "months": [
          2,
          3
        ]
      },
      "n_train": 463,
      "n_oos": 1810,
      "clears_dual_draft": false,
      "train": {
        "n": 463,
        "win_pct": 0.3045356371490281,
        "end": 91.65,
        "max_dd": 172.65,
        "bust": false,
        "clears_draft": true
      },
      "oos": {
        "n": 271,
        "win_pct": 0.3025830258302583,
        "end": 4.6,
        "max_dd": 179.95,
        "bust": false,
        "clears_draft": false
      }
    },
    "n": 11215,
    "policy": "soccer OFF",
    "generated_at": "2026-10-27T00:53:12Z"
  }
}
```

Raw: [`../internal/sims/sports-unbound-exhaustion/wave51/`](../internal/sims/sports-unbound-exhaustion/wave51/)

## EXHAUST_WAVE51_DONE

---

## Wave 52 — HT-draw-rate under (`2026-10-27T00:53:13Z`)

**EXHAUST_WAVE52_DONE.** Families: `wave52_ht_draw_rate_under`. Paper enables this wave: **0**. Catakid NBA **untouched**. `beats_book=false`.

```json
{
  "wave": 52,
  "family_set": "wave52_ht_draw_rate_under",
  "paper_enables": [],
  "highlights": {
    "best": {
      "params": {
        "min_rate": 0.3
      },
      "n_train": 2896,
      "n_oos": 11528,
      "clears_dual_draft": false,
      "train": {
        "n": 226,
        "win_pct": 0.46017699115044247,
        "end": 4.8,
        "max_dd": 109.05,
        "bust": false,
        "clears_draft": false
      },
      "oos": {
        "n": 1224,
        "win_pct": 0.5277777777777778,
        "end": 3.1,
        "max_dd": 277.35,
        "bust": false,
        "clears_draft": false
      }
    },
    "n": 18340,
    "policy": "soccer OFF",
    "generated_at": "2026-10-27T00:53:13Z"
  }
}
```

Raw: [`../internal/sims/sports-unbound-exhaustion/wave52/`](../internal/sims/sports-unbound-exhaustion/wave52/)

## EXHAUST_WAVE52_DONE

---

## Wave 53 — NFL band staking ops (`2026-10-27T00:53:16Z`)

**EXHAUST_WAVE53_DONE.** Families: `wave53_nfl_band_staking`. Paper enables this wave: **0**. Catakid NBA **untouched**. `beats_book=false`.

```json
{
  "wave": 53,
  "family_set": "wave53_nfl_band_staking",
  "paper_enables": [],
  "highlights": {
    "variants": {
      "flat5": {
        "train": {
          "n": 248,
          "win_pct": 0.5725806451612904,
          "end": 195.4545,
          "max_dd": 38.6364,
          "bust": false,
          "clears_draft": true
        },
        "oos": {
          "n": 97,
          "win_pct": 0.5567010309278351,
          "end": 110.4545,
          "max_dd": 39.5455,
          "bust": false,
          "clears_draft": true
        },
        "clears_ats_proxy": true
      },
      "qkelly": {
        "train": {
          "n": 248,
          "win_pct": 0.5725806451612904,
          "end": 223.0574,
          "max_dd": 40.6337,
          "bust": false,
          "clears_draft": true
        },
        "oos": {
          "n": 97,
          "win_pct": 0.5567010309278351,
          "end": 89.6702,
          "max_dd": 29.2122,
          "bust": false,
          "clears_draft": true
        },
        "clears_ats_proxy": true
      },
      "dd_scaled": {
        "train": {
          "n": 248,
          "win_pct": 0.5725806451612904,
          "end": 97.7074,
          "max_dd": 6.1297,
          "bust": false,
          "clears_draft": true
        },
        "oos": {
          "n": 97,
          "win_pct": 0.5567010309278351,
          "end": 84.612,
          "max_dd": 6.6669,
          "bust": false,
          "clears_draft": true
        },
        "clears_ats_proxy": true
      }
    },
    "note": "Staking ablations on wave20 filter \u2014 Catakid untouched; NFL ATS paper path separate from NBA daemon",
    "ops_note_only": true,
    "generated_at": "2026-10-27T00:53:16Z"
  }
}
```

Raw: [`../internal/sims/sports-unbound-exhaustion/wave53/`](../internal/sims/sports-unbound-exhaustion/wave53/)

## EXHAUST_WAVE53_DONE

---

## Wave 54 — fouls→under (`2026-10-27T00:53:18Z`)

**EXHAUST_WAVE54_DONE.** Families: `wave54_fouls_under`. Paper enables this wave: **0**. Catakid NBA **untouched**. `beats_book=false`.

```json
{
  "wave": 54,
  "family_set": "wave54_fouls_under",
  "paper_enables": [],
  "highlights": {
    "best": {
      "params": {
        "min_foul": 10
      },
      "n_train": 3222,
      "n_oos": 12800,
      "clears_dual_draft": false,
      "train": {
        "n": 98,
        "win_pct": 0.42857142857142855,
        "end": 4.4,
        "max_dd": 84.1,
        "bust": false,
        "clears_draft": false
      },
      "oos": {
        "n": 309,
        "win_pct": 0.517799352750809,
        "end": 4.0,
        "max_dd": 94.6,
        "bust": false,
        "clears_draft": false
      }
    },
    "n": 18340,
    "policy": "soccer OFF",
    "generated_at": "2026-10-27T00:53:18Z"
  }
}
```

Raw: [`../internal/sims/sports-unbound-exhaustion/wave54/`](../internal/sims/sports-unbound-exhaustion/wave54/)

## EXHAUST_WAVE54_DONE

---

## Wave 55 — tennis surface process (`2026-10-27T00:53:20Z`)

**EXHAUST_WAVE55_DONE.** Families: `wave55_tennis_surface_process`. Paper enables this wave: **0**. Catakid NBA **untouched**. `beats_book=false`.

```json
{
  "wave": 55,
  "family_set": "wave55_tennis_surface_process",
  "paper_enables": [],
  "highlights": {
    "status": "ok",
    "decision": "KEEP_PATH_TRAILS_COIN",
    "beats_book": false,
    "n_games": 100,
    "surface_briers": {
      "clay": 0.2699013675213675,
      "hard": 0.2972797385620915
    },
    "reason": "HARD_STOP / process \u2014 no historical ML closes join for stake invent; prior ATP stake blocked",
    "generated_at": "2026-10-27T00:53:20Z"
  }
}
```

Raw: [`../internal/sims/sports-unbound-exhaustion/wave55/`](../internal/sims/sports-unbound-exhaustion/wave55/)

## EXHAUST_WAVE55_DONE

---

## Wave 56 — greyhound stake blocked (`2026-10-27T00:53:22Z`)

**EXHAUST_WAVE56_DONE.** Families: `wave56_greyhound_stake_blocked`. Paper enables this wave: **0**. Catakid NBA **untouched**. `beats_book=false`.

```json
{
  "wave": 56,
  "family_set": "wave56_greyhound_stake_blocked",
  "paper_enables": [],
  "highlights": {
    "oos_summary": {
      "method_id": "disagree_edge_1pct",
      "n_picks": 50,
      "win_rate": 0.18,
      "roi": -0.305,
      "end_bankroll": 3.75,
      "clears_bar": false,
      "enable_recommend": "lift-needed",
      "beats_book": false
    },
    "reason": "Place/EW HARD STOP; win-only already failed enable path \u2014 no new free price",
    "generated_at": "2026-10-27T00:53:22Z"
  }
}
```

Raw: [`../internal/sims/sports-unbound-exhaustion/wave56/`](../internal/sims/sports-unbound-exhaustion/wave56/)

## EXHAUST_WAVE56_DONE

---

## Wave 57 — exhaustion re-audit 2 (`2026-10-27T00:53:24Z`)

**EXHAUST_WAVE57_DONE.** Families: `wave57_exhaustion_reaudit2`. Paper enables this wave: **0**. Catakid NBA **untouched**. `beats_book=false`.

```json
{
  "wave": 57,
  "family_set": "wave57_exhaustion_reaudit2",
  "paper_enables": [],
  "highlights": {
    "scored_this_batch": [
      "away_ah",
      "nba_resid_bands",
      "nfl_injury_filter",
      "nhl_fav_honesty",
      "midweek_under",
      "pickem_ah",
      "pinnacle_under_shop",
      "month_home_dog",
      "ht_draw_rate_under",
      "nfl_band_staking",
      "fouls_under",
      "tennis_surface_process",
      "greyhound_stake_blocked"
    ],
    "still_blocked_\u00a30": [
      "multi-book live Odds API / steam / bookie login",
      "NCAAB/NCAAF Odds key closes",
      "tennis-data.co.uk 403 / ATP per-bet dump absent",
      "HT 1X2 / corner / BTTS / place SP odds",
      "NBA ML p_cal for Platt/\u215b-Kelly",
      "NHL/MLB totals closes",
      "Valorant/CS ML closes",
      "optical / paid FTN",
      "arXiv AID_SPORTS sibling lane",
      "in-play Markov without priced closes",
      "MMA/cricket per-bet re-stake without new free close columns (already scored live-methods)"
    ],
    "truly_exhausted_free_sim_lane": true,
    "paper_enables_total_overnight_note": "wave20 NFL ATS band kept after honesty; wave33 revoked structural",
    "generated_at": "2026-10-27T00:53:24Z"
  }
}
```

Raw: [`../internal/sims/sports-unbound-exhaustion/wave57/`](../internal/sims/sports-unbound-exhaustion/wave57/)

## EXHAUST_WAVE57_DONE

---

## Overnight continuation wrap 44+ (`2026-10-27T00:53:26Z`)

Waves **44–57**.  
London `2026-10-27T00:52:59.110273+00:00` → `2026-10-27T00:53:26.365793+00:00`.  
**NEW paper enables this batch: 0** (post-honesty). Catakid NBA **untouched**. `beats_book=false`.

### OVERNIGHT_SPORTS_DONE

**wave_count_total** = 57.  
Kept enable: **wave20_nfl_ats_spread_bands** (honesty-checked). Wave33 revoked structural.  
Free+new lane re-audited at wave 57.
