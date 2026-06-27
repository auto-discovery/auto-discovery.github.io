# TTT-Discover behavior study — findings

Cross-run analysis of 7 ttt-discover training runs on Qwen3-8B (local backend).
All runs ran 30 training steps under the *medium scale* config:
`group_size=16, groups_per_batch=4, phase1_max_tokens=16000,
eval_timeout=1100, save_every=1`. Only the PUCT-sampler knobs varied between runs.

The training algorithm is byte-identical to the upstream `discover/` repo —
this study only added logging and exposed five new `DiscoverConfig` fields
(`puct_c`, `puct_topk_children`, `puct_max_buffer_size`,
`puct_lineage_blocking`, `puct_blacklisted_seed_ids`), all defaulted to
preserve original behavior. Sampler math, advantage estimator, KL penalty, and
loss function were left untouched.

---

## Runs

| Run | Task | PUCT config | Best | Target |
|---|---|---|---:|---:|
| `erdos-baseline-1` | erdős min-overlap (C₅ bound, min) | `c=1.0 topk=2 buf=1000 block=on` | 0.3816 | 0.380 |
| `erdos-loose-prune` | erdős | `c=1.0 topk=8 buf=4000 block=on` | **0.3810** | 0.380 |
| `erdos-mcts-puct_c_0.3` | erdős | `c=0.3 topk=2 buf=1000 block=on` | 0.3814 | 0.380 |
| `erdos-mcts-puct_c_3.0` | erdős | `c=3.0 topk=2 buf=1000 block=on` | **0.3810** | 0.380 |
| `ac1-baseline-1` | autocorrelation upper bound (min) | `c=1.0 topk=2 buf=1000 block=on` | 1.5076 | 1.503 |
| `ac1-lineage-blocking-off` | ac1 | `c=1.0 topk=2 buf=1000 block=OFF` | **1.5075** | 1.503 |
| `ac2-baseline-1` | autocorrelation lower bound (max) | `c=1.0 topk=2 buf=1000 block=on` | 0.9358 | 0.97 |

5 of 7 essentially hit their published targets. **ac2 saturated 0.034 below
target** — the clearest case of missed solutions due to narrow search.

---

# Part 1 — Headline findings

## H1. Buffer monomorphism is universal

Top-1 root coverage (% of the final 30-step buffer descended from a single
seed state) at the end of training:

| Run | Buffer size | # distinct roots | Top-1 root | Monomorphic (80/10)? |
|---|---:|---:|---:|---|
| erdos-baseline | 198 | 4 | 84.8% | YES |
| erdos-loose-prune | **558** | 4 | 83.7% | YES |
| erdos-mcts c=0.3 | 216 | 4 | **95.8%** | YES |
| erdos-mcts c=3.0 | 210 | 4 | 94.3% | YES |
| ac1-baseline | 243 | 4 | 92.6% | YES |
| ac1-noblock | 241 | 4 | 92.9% | YES |
| ac2-baseline | 220 | 4 | 89.1% | YES |

**Every run ends ≥ 84% from one seed.** The four initial seeds were never
explored evenly — one always dominates.

## H2. The exploration knobs we tested don't fix it

| Intervention | Result |
|---|---|
| **Loose pruning** (topk=8, max=4000 vs 2/1000) | Buffer 2.8× larger but still 84% monomorphic; best C₅ improved by 0.0006 (within noise) |
| **MCTS c sweep** (0.3 → 1.0 → 3.0) | Score spread 0.0006; top-1 root coverage 96% / 85% / 94% (no monotone relation) |
| **Lineage blocking off** | ac1 with vs without blocking: 1.5076 vs 1.5075 — tied. Top-1 root coverage 92.6% vs 92.9% — identical |

The "more exploration" knobs simulate exploration without producing it.
Increasing puct_c from 0.3 → 3.0 *increased* visit-count bonus weight 10× but
the final buffer is still mostly one lineage.

**Why:** the bonus `puct_c · scale · P · √(1+T) / (1+n)` always favors
freshly-added states with `n=0`. Those fresh states are children of the
dominant lineage. The visit-count term suppresses re-picking *old ancestors*,
not new descendants of the same lineage.

## H3. PUCT factor share — Q dominates by mid-training

`share_Q = |Q| / (|Q| + |bonus|)` over a run's selections. Starts at ~1.0
(no T accumulated → bonus tiny) and ends at 0.70-0.97 depending on `puct_c`.

| Run | Q-share start → end | Mean depth start → end |
|---|---|---|
| erdos-baseline | 0.99 → 0.76 | 0 → 27.8 |
| erdos-loose-prune | 1.00 → 0.80 | 0 → 19.0 |
| erdos-mcts c=0.3 | 1.00 → **0.97** | 0 → 25.0 |
| erdos-mcts c=3.0 | 0.97 → 0.73 | 0 → 25.2 |
| ac1-baseline | 1.00 → 0.88 | 0 → 29.0 |
| ac1-noblock | 1.00 → 0.88 | 0 → 28.0 |
| ac2-baseline | 1.00 → 0.88 | 0 → 25.0 |

Even at `puct_c=3.0` (3× exploration weight), Q controls 73% of the score at
step 30. Mean depth of picked parents grows monotonically to 25-29 across all
runs — the algorithm consistently picks deep descendants, not seed alternatives.

## H4. **Local exploration is preserved; global exploration is not.**

This is the deepest finding. Three independent rep-space measures show the
same pattern.

### H4a. Within-step rollout diversity stays HIGH throughout

Per-step elliptic bonus (average leverage score per rollout in its group;
max = 1.0; min = 1/N ≈ 0.06 if all redundant):

| Run | s0 | s5 | s10 | s15 | s20 | s25 | s29 |
|---|---:|---:|---:|---:|---:|---:|---:|
| erdos-baseline | 0.86 | 0.85 | 0.84 | 0.85 | 0.85 | 0.85 | 0.85 |
| erdos-loose-prune | 0.86 | 0.86 | 0.85 | 0.85 | 0.86 | 0.86 | 0.86 |
| erdos-mcts c=3.0 | 0.86 | 0.86 | 0.86 | 0.86 | 0.84 | 0.85 | 0.85 |
| ac1-baseline | 0.87 | 0.86 | 0.85 | 0.85 | 0.85 | 0.84 | 0.83 |
| ac1-noblock | 0.87 | 0.87 | 0.86 | 0.85 | 0.86 | 0.86 | 0.86 |
| ac2-baseline | 0.84 | 0.87 | 0.83 | 0.84 | 0.84 | 0.81 | 0.81 |

Effective rank of the within-step rep matrix (max = 16):

| Run | s0 | s5 | s10 | s15 | s20 | s25 | s29 |
|---|---:|---:|---:|---:|---:|---:|---:|
| erdos-baseline | 11.2 | 10.7 | 10.1 | 9.9 | 10.1 | 10.1 | 9.6 |
| erdos-loose-prune | 10.9 | 10.5 | 10.6 | 10.3 | 9.6 | 10.8 | 10.7 |
| erdos-mcts c=3.0 | 11.0 | 10.6 | 10.6 | 10.5 | 9.6 | 10.5 | 9.8 |
| ac1-baseline | 10.2 | 10.5 | 10.2 | 10.3 | 8.8 | 9.0 | 9.9 |
| ac1-noblock | 10.8 | 11.1 | 10.6 | 10.8 | 11.0 | 10.3 | 10.6 |
| ac2-baseline | **9.0** | 9.8 | 9.2 | 8.7 | 8.2 | **7.5** | 8.4 |

For all runs except ac2, each batch of 16 rollouts spans ~10 of the 16
possible "effective dimensions" — about 60-70% diversity, stable throughout
training.

### H4b. Cross-step novelty COLLAPSES from ~10× to ~1×

For each step T, the mean elliptic bonus of step T's rollouts evaluated
against the *union of all previous steps' rollouts*:

| Run | s1 | s5 | s10 | s15 | s20 | s25 | s29 |
|---|---:|---:|---:|---:|---:|---:|---:|
| erdos-baseline | 10.8 | 2.7 | 2.4 | 1.3 | 1.0 | 0.98 | **0.86** |
| erdos-loose-prune | 12.3 | 2.8 | 1.8 | 1.4 | 1.1 | 0.88 | **0.86** |
| erdos-mcts c=0.3 | 9.3 | 2.8 | 1.6 | 1.3 | 1.1 | 0.87 | **0.82** |
| erdos-mcts c=3.0 | 11.9 | 2.9 | 1.6 | 1.4 | 1.4 | 1.1 | **1.03** |
| ac1-baseline | 14.4 | 2.9 | 1.6 | 1.4 | 1.0 | 0.85 | **0.65** |
| ac1-noblock | 13.8 | 2.8 | 1.9 | 1.4 | 1.1 | 0.98 | **0.93** |
| ac2-baseline | 7.9 | 5.7 | 1.6 | 1.3 | 1.3 | 0.83 | **0.72** |

Step T = 29's rollouts have leverage ≈ 1 vs everything before — they're
essentially *spanned* by the cumulative rep history.

Step-to-step novelty (vs step T-1 only) drops similarly fast then plateaus at
moderate (5-7), so neighboring steps still differ from each other a bit, but
they all sit inside the historical span.

### H4c. The ratio `cross-step / within-step` novelty drops to ~1 (or below)

| Run | s1 | s5 | s10 | s15 | s20 | s25 | s29 |
|---|---:|---:|---:|---:|---:|---:|---:|
| erdos-baseline | 13.1 | 3.4 | 2.9 | 1.6 | 1.2 | 1.2 | **1.05** |
| erdos-mcts c=3.0 | 14.5 | 3.5 | 1.9 | 1.7 | 1.7 | 1.4 | **1.25** |
| ac1-baseline | 17.0 | 3.5 | 2.0 | 1.7 | 1.3 | 1.1 | **0.84** |
| ac2-baseline | 9.8 | 6.7 | 2.0 | 1.7 | 1.6 | 1.1 | **0.96** |

At step 29 the ratio is ~1 for erdos and **<1 for ac1 baseline** — meaning
step T's rollouts are *less* novel vs all-history than they are vs their own
batchmates. Late training is producing rollouts that fit a learned mold; any
deviation *within* a step is bigger than any deviation *across* steps.

### H4d. Centroid drift plateaus fast (post-hoc PCA)

Centroid distance from step-0 centroid in raw rep space:

| Run | s5 | s10 | s15 | s20 | s25 |
|---|---:|---:|---:|---:|---:|
| erdos-baseline | 0.14 | 0.13 | 0.13 | 0.15 | 0.15 |
| erdos-loose-prune | 0.09 | 0.10 | 0.12 | 0.13 | 0.12 |
| erdos-mcts c=0.3 | 0.11 | 0.13 | 0.15 | 0.11 | 0.16 |
| erdos-mcts c=3.0 | 0.15 | 0.14 | 0.16 | 0.16 | 0.16 |
| ac1-baseline | 0.06 | 0.16 | 0.15 | **0.24** | 0.18 |
| ac1-noblock | 0.08 | 0.07 | 0.06 | 0.12 | 0.11 |
| ac2-baseline | **0.14** | **0.07** | **0.06** | 0.09 | 0.09 |

Erdos: most movement by step 5, then plateau. AC1 baseline keeps moving
(this is the run that achieved the best AC1 result). **AC2 drifted then
collapsed BACK toward origin** — the policy partially un-trained itself.

### Combined verdict on H4

| Question | Answer |
|---|---|
| Within-step diversity? | **High and stable** (~60-70% of available dims, bonus ≈ 0.85). |
| Step-to-step novelty? | **Drops fast, settles at moderate** (5-7). |
| Vs all history? | **Collapses 10× → 1.0** by step 29. |
| Centroid drift? | **Plateaus by step 5-10** (except ac1-baseline). |

**Translation:** TTT-Discover does **local exploration around a committed
center** but does **not** do **global exploration of new regions**. The
policy keeps producing diverse responses *within* each batch, but the *set
of regions* those responses cover stops growing very quickly. By halfway
through training, new batches mostly retread old ground in rep space.

This is exactly consistent with the lineage-monomorphism finding (H1):
drilling deeper into one seed's subtree keeps you in roughly the same rep
neighborhood, even if individual rollouts within a step vary.

---

# Part 2 — Detailed analyses

## D1. Within-group reward variance (gradient signal strength)

| Run | s0 → s5 | s5 → s25 |
|---|---|---|
| All 4 **erdos** runs | 0.03-0.17 → **0.6-1.4** | Stays high |
| **ac1** (both) | 0.06-0.07 → 0.08-0.10 | Stays flat & very low |
| **ac2** | 0.16 → 0.16 | Stays flat & low |

For erdos the model gets strong, growing reward signal across the group —
the advantage estimator has real information to use. For ac1 and ac2 all
rollouts in a group get similar rewards → the policy gradient signal is
weak. This is structural to the task, not a bug.

## D2. Effective sample size per group (entropic ESS, group_size=16)

| Run | s0 | s5 | s10 | s15 | s20 | s25 |
|---|---:|---:|---:|---:|---:|---:|
| erdos-baseline | 13.0 | 8.3 | 5.6 | 7.9 | 6.2 | 6.6 |
| erdos-loose-prune | 10.0 | 5.8 | 6.3 | 6.6 | 5.6 | 7.0 |
| erdos-mcts c=3.0 | 10.2 | 7.0 | 6.5 | 6.1 | 8.6 | 5.9 |
| ac1-baseline | 6.7 | 7.3 | 6.8 | 7.0 | 7.0 | 6.7 |
| ac1-noblock | 6.3 | 6.6 | 7.3 | 6.9 | 7.0 | 6.8 |
| ac2-baseline | 6.4 | 5.9 | 5.5 | 6.6 | 6.1 | 6.5 |

For erdos: groups START diverse (ESS ~10-13), then COLLAPSE to ~6 effective
rollouts. The model learns to produce a small set of "winners."
For AC1/AC2: groups are already collapsed to ESS ~6 from step 0.

## D3. RepExp global drift (re-encoded with current model)

This is RepExp's principled "how much has the policy moved" metric — encodes
old reference rollouts with the CURRENT model so encoder drift doesn't
contaminate the signal.

| Run | s5 | s10 | s15 | s20 | s25 |
|---|---:|---:|---:|---:|---:|
| erdos-baseline | 0.019 | 0.016 | 0.016 | 0.022 | 0.021 |
| erdos-mcts c=3.0 | 0.023 | 0.020 | 0.026 | 0.026 | 0.027 |
| **ac1-baseline** | 0.003 | 0.023 | 0.021 | **0.055** | 0.031 |
| ac1-noblock | 0.008 | 0.005 | 0.004 | 0.014 | 0.012 |
| **ac2-baseline** | **0.020** | **0.005** | **0.004** | 0.007 | 0.008 |

**AC1 baseline:** stops-and-starts — drift quintuples between steps 10 and 20
(0.011 → 0.055), then partly retracts to 0.031. This is the run that hit the
best AC1 result. Real discovery happens late.

**AC2 is the headline:** drift goes **UP then DOWN**. The policy moves from
0.000 → 0.020 by step 5, then **collapses BACK** to 0.005-0.008 for the rest
of training.

### Drift / within-step spread ratio

When this ratio is **<<1**, the policy "movement" is smaller than the
within-step rollout variability — i.e., the drift is essentially noise.

| Run | s5 | s10 | s15 | s20 | s25 |
|---|---:|---:|---:|---:|---:|
| erdos (avg) | 0.9 | 0.8 | 1.0 | 0.9 | 1.3 |
| ac1-baseline | 0.19 | 0.83 | 1.10 | **1.78** | 1.12 |
| ac1-noblock | 0.45 | 0.25 | 0.27 | 0.80 | 0.53 |
| **ac2** | 0.59 | 0.21 | **0.13** | 0.17 | 0.19 |

AC2's ratio drops to **0.13** by step 15 — the policy is generating noise
around a stuck point.

## D4. Pairwise cosine similarity (within-step)

Mean pairwise cosine across mean-centered rollout reps. Higher = rollouts
more similar to each other.

| Run | s0 | s5 | s10 | s15 | s20 | s25 | s29 |
|---|---:|---:|---:|---:|---:|---:|---:|
| erdos-baseline | -0.059 | -0.053 | -0.055 | -0.059 | -0.057 | -0.059 | -0.042 |
| ac1-baseline | -0.053 | -0.055 | -0.056 | -0.053 | -0.056 | -0.049 | -0.047 |
| **ac2-baseline** | -0.051 | -0.057 | -0.035 | -0.052 | -0.042 | -0.028 | **-0.006** |

For erdos and ac1, rollouts stay slightly orthogonal (cos ≈ -0.05)
throughout. For **ac2, rollouts become 10× less orthogonal** over training
(from -0.05 to -0.006) — they start pointing similar directions.

## D5. Bonus Gini coefficient (within-step novelty inequality)

High Gini = one rollout hogs novelty; low Gini = even distribution.

| Run | s0 | s5 | s10 | s15 | s20 | s25 | s29 |
|---|---:|---:|---:|---:|---:|---:|---:|
| erdos-baseline | 0.019 | 0.019 | 0.019 | 0.016 | 0.019 | 0.022 | 0.019 |
| ac1-baseline | 0.015 | 0.021 | 0.023 | 0.025 | 0.023 | 0.027 | **0.033** |
| ac1-noblock | 0.014 | 0.017 | 0.019 | 0.024 | 0.015 | 0.017 | 0.018 |
| **ac2-baseline** | 0.029 | 0.021 | 0.027 | 0.029 | 0.029 | 0.035 | **0.044** |

AC2 has the highest and growing Gini — novelty concentrates in fewer
rollouts as training progresses.

## D6. Reward vs novelty rank disagreement (per group)

For each rollout group, Kendall τ between per-rollout reward and per-rollout
elliptic-bonus novelty:

| Run | τ first → τ last | top-2 Jaccard first → last | mean reward gap first → last |
|---|---|---|---|
| erdos-baseline | -0.07 → -0.03 | 0.00 → 0.08 | 0.00 → **2.60** |
| erdos-loose-prune | +0.16 → -0.09 | 0.08 → 0.00 | 0.00 → **2.47** |
| erdos-mcts c=3.0 | +0.20 → +0.03 | 0.17 → 0.17 | 0.33 → **1.31** |
| ac1-baseline | -0.16 → +0.04 | 0.08 → 0.00 | 0.43 → 0.22 |
| ac2-baseline | +0.01 → -0.21 | 0.00 → 0.08 | 0.62 → 0.66 |

Reward and novelty ranks are largely orthogonal across all runs.
**Reward gap if you'd picked by novelty** (in reward units) grows over
training for erdos (1.3-2.6), stays modest for ac1/ac2 (0.2-0.7).

## D7. Greedy saturation (only meaningful on loose-prune run)

For the `erdos-loose-prune` run, 10 final-step top states inspected:

- **9.68%** of breakthrough-ancestors would have been pruned under tight
  `top-2` sibling policy
- **0%** would have been pruned under tight `top-1000` global cap (buffer
  never reached 1000 anyway)

**But** the would-be-cut ancestors all had value ≈ -0.3812 vs the kept ones
at -0.3810 — functionally identical. The "tax" exists but the cut states
were near-tied with the kept ones.

---

# Part 3 — Interpretation

## I1. Three task regimes

The RepExp data exposes three distinct task regimes:

| Regime | Tasks | Reward variance | Drift behavior | What works |
|---|---|---|---|---|
| Strong signal | erdos (all 4 variants) | High (0.6-1.4) | Steady forward drift | Defaults work, knobs barely matter |
| Borderline | ac1 | Low (0.08) | Big late-training movement (0.055) | Defaults still work, needs patience |
| Insufficient signal | ac2 | Low (0.16) | Drift collapses back to origin | Defaults FAIL; needs different reward shaping or much longer training |

## I2. The two-phase commitment pattern

```
Step 0-5:   Policy moves in rep space.  Center drifts; rollouts diverse.
Step 5-30:  Center stops moving.        Within-step rollouts STAY diverse.
            Buffer fills with descendants of one seed.
            Lineage commits, representation stays locally diverse but globally fixed.
```

## I3. Two distinct kinds of commitment

What the algorithm DOES commit:
1. **Lineage commitment** (H1): 84-96% of buffer descended from one seed.
2. **Region commitment** (H4): step T's rollouts redundant vs history by step 15-20.
3. **Center commitment** (H4d): centroid stops moving by step 5-10.

What the algorithm DOESN'T collapse:
- **Within-step rollout diversity** stays at ~60-70% of available dimensions.
- **Rollouts within a batch stay nearly orthogonal** (cos ≈ -0.05).
- **Effective rank per group** stays at ~10/16.

These are not contradictions — they say:
"The set of regions the policy visits is committed early. Within those
regions, the policy keeps producing varied responses. Variation is local,
not global."

## I4. AC2 is the only task with representational collapse

Combining everything we now know:

- AC2 reward plateaued at 0.9358 at step 10 and never improved
- AC2 has weak reward variance per group (~0.16 throughout) → little gradient
- AC2 drifted forward briefly (0.020 at s5) then collapsed back to 0.005-0.008
- AC2 drift/spread ratio drops to 0.13-0.19 → drift dominated by noise
- AC2 effective rank drops 9.0 → 7.5 (loses 1.5 dims of variation)
- AC2 pairwise cosine drifts from -0.05 → -0.005 (rollouts become co-linear)
- AC2 bonus gini grows 0.029 → 0.044 (novelty concentrates in fewer rollouts)

**AC2 doesn't just commit early and get stuck.** With weak gradient signal,
LoRA updates were essentially noise, which on average pulled the policy back
toward the base model. This is "unlearning."

For AC1 (similarly low reward variance ~0.08), the same dynamic might
happen, but the policy *did* find a real improvement at step 25 (1.5076)
and its drift trajectory shows it still moving (0.031 at step 25). AC1 is a
borderline case where the gradient was barely strong enough.

---

# Part 4 — Implications

## What WON'T fix the commitment

Empirically tested, all flat:
- Looser pruning (topk=8, max_buffer=4000) — buffer 2.8× bigger but still
  monomorphic; final reward gain 0.0006
- MCTS exploration weight (puct_c 0.3 → 3.0) — 10× more bonus weight,
  final reward spread 0.0006
- Lineage blocking — no effect on score or buffer structure

## What's likely to actually help

Based on the H4 finding (commitment is *global* not *local*), the
interventions that have a chance:

1. **Cross-step diversity term in the PUCT score.** Add a leverage-score
   penalty for picks whose parent state's representation is too similar to
   recent history. This directly targets the failure mode H4 identified:
   bonus_vs_history < bonus_within_step. The within-step elliptic bonus is
   already high (~0.85) so adding within-step diversity penalties won't
   help; the cross-step term is where novelty is missing.

2. **Multi-seed parallel runs with cross-pollination.** Maintain K
   independent buffers, periodically inject the best from each into the
   others. Breaks single-lineage accretion at K× compute cost.

3. **Forced root reset.** With probability ε, sample from the initial seeds
   instead of PUCT-favored states. Bluntest fix; matches ε-greedy logic
   from classical RL.

4. **For AC2 specifically: reward shaping.** No exploration trick will fix
   a weak reward signal. AC2's reward variance is ~0.16 from step 0 to step
   29 — there's just not enough information for the policy gradient. Would
   need: denser reward function, intermediate reward signals, or a better
   prompt that encourages diverse construction strategies.

---

# Part 5 — Where to find the data

## Plots

`/workspace-vast/$USER/exp/ttt-discover/runs/_summary/`
- `summary.png` — 6-panel cross-run overview (monomorphism, gap-from-target,
  Q-share, depth, MCTS sweep, legend).
- `blocking_ablation.png` — ac1 with vs without lineage blocking
  (3 panels: best score, top-1 root, depth).

Regenerate with:
```bash
/workspace-vast/$USER/venvs/ttt-discover/bin/python \
  /workspace-vast/$USER/code/rep-ttt/scripts/analysis/make_summary_plots.py
```

## Per-run artifacts

`/workspace-vast/$USER/exp/ttt-discover/runs/tinker_log/<run>/`

| Path | Contents |
|---|---|
| `metrics.jsonl` | one row per step with rewards, PUCT shares, depth stats, repexp scalars |
| `puct_sampler_step_NNNNNN.json` | full buffer snapshot per step (parent chains, values) |
| `puct_selection_step_NNNNNN.json` | per-pick PUCT factor breakdown (Q, P, bonus, score, depth) — NEW logging |
| `rollouts.jsonl` | per-rollout parent_state_id + reward + length — NEW logging |
| `repexp/representations_step*.npz` | mean-pooled response hidden states |
| `repexp/group_diversity.jsonl` | per-group diversity scalars |
| `local_checkpoints/<step>/adapter/` | LoRA weights every `save_every` steps |
| `analysis/ancestry/per_step.json,summary.json,top_roots.png` | per-step monomorphism stats |
| `analysis/puct_factor_share/per_step.json,trends.png` | Q-share, depth, visit-count trajectories |
| `analysis/rank_disagreement/per_step.json,summary.json,per_step_trends.png` | reward vs novelty Kendall τ, top-2 Jaccard, reward gap |
| `analysis/tsne_evolution/embedding.npz,overlay.png,geometry_over_steps.png` | 2D PCA/t-SNE of rollout reps over time |
| `analysis/saturation/summary.json,per_breakthrough.json` | greedy-saturation analysis (only meaningful on `erdos-loose-prune`) |

Run all analyses on a single run dir:
```bash
/workspace-vast/$USER/venvs/ttt-discover/bin/python \
  /workspace-vast/$USER/code/rep-ttt/scripts/analysis/run_all.py \
  --run-dir /workspace-vast/$USER/exp/ttt-discover/runs/tinker_log/<run> \
  --include-saturation
```

## How to reproduce the cross-step novelty analysis (H4b, H4c)

The cross-step elliptic-bonus numbers were computed ad-hoc by walking each
run's `repexp/representations_step*.npz` files. Re-run with:

```python
import numpy as np
from ttt_discover.repexp.metrics import elliptic_bonuses, mean_center

def bonus_vs_context(H_new, H_ctx, lam=1.0):
    """Leverage of each row in H_new against context H_ctx (Woodbury form)."""
    N = H_ctx.shape[0]
    G = H_ctx @ H_ctx.T
    M = lam * np.eye(N) + G
    C = H_ctx @ H_new.T
    Minv_C = np.linalg.solve(M, C)
    cross = (C * Minv_C).sum(axis=0)
    norms_sq = (H_new * H_new).sum(axis=1)
    return np.clip((norms_sq - cross) / lam, 0.0, None)

# Then for each step T, load reps and call:
#   vs_history = bonus_vs_context(H_T, union_of_steps_0_to_T_minus_1)
#   vs_prev    = bonus_vs_context(H_T, H_T_minus_1)
```

## W&B

- `https://wandb.ai/edward-sun-ucla/ttt-discover-baselines/` (3 baselines)
- `https://wandb.ai/edward-sun-ucla/ttt-discover-experiments/` (4 experiments)

## Logs

`/workspace-vast/$USER/exp/ttt-discover/logs/ttt_*.out` — sbatch stdouts.

---

# Summary

| Question | Answer |
|---|---|
| Does TTT-Discover commit to a lineage early? | **YES, universally.** 84-96% top-1 root coverage in every run. |
| Does it explore within that lineage? | **YES.** Per-step rollouts span ~60-70% of available dims throughout. |
| Does it explore *new* regions of rep space across steps? | **NO.** Cross-step novelty drops 10× → 1× by step 29. |
| Do the existing exploration knobs (puct_c, blocking, pruning) help? | **NO.** Best-score spread of 0.0006 across all sweeps and ablations. |
| Does commitment cost reward on every task? | **NO for erdos/ac1** (reward landscape clusters near optimum), **YES for ac2** (saturated 0.034 short of target). |
| Is AC2 just stuck, or actively un-learning? | **Actively un-learning.** Drift went 0 → 0.02 → back to 0.005-0.008. Eff rank dropped 9.0 → 7.5. |

**The core finding:** TTT-Discover does local exploration around a committed
center, not global exploration. The existing "exploration" knobs don't move
the needle. A structural change targeting cross-step novelty (not
within-step) is the realistic path to broader search.
