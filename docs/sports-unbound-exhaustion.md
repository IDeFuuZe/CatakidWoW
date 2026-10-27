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
