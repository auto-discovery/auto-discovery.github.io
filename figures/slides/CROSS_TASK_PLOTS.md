# Cross-task overlay plots — analysis notes

**Path to figures:** `/workspace-vast/edwardosunny/exp/ttt-discover/runs/_summary/cross_task/`
**Generator script:** `scripts/analysis/cross_run_overlay.py`
**Regenerate with:** `/workspace-vast/$USER/venvs/ttt-discover/bin/python scripts/analysis/cross_run_overlay.py`

These cover the entire analysis surface from `FINDINGS.md` (H1-H4, D1-D7,
H4 supplements) as cross-run overlays. 34 figures total.

## Plot legend convention

- **Color = task family**:
  - `erdos` (blue), `ac1` (green), `ac2` (orange)
- **Line style = variant**:
  - `baseline-1` — solid + circle markers (the canonical run)
  - `loose-prune` — long-dash
  - `mcts-puct_c_0.3` — dotted
  - `mcts-puct_c_3.0` — dash-dot
  - `lineage-blocking-off` — dash-dot-dot
  - `rep-novelty` — solid + square markers (heavier)
  - `qd-archive` — solid + diamond markers (heavier)
- Each curve shows one run; one figure per analysis dimension.

Runs included (auto-discovered, smoke runs excluded):
`erdos-baseline-1`, `erdos-loose-prune`, `erdos-mcts-puct_c_0.3`,
`erdos-mcts-puct_c_3.0`, `erdos-rep-novelty`, `erdos-qd-archive` (partial),
`ac1-baseline-1`, `ac1-lineage-blocking-off`, `ac1-rep-novelty` (steps 0-24),
`ac2-baseline-1`.

---

## Headline / method comparison

These are the plots that show **whether the methods worked**.

### Best reward over time (per-task, units differ)
- `best_reward_erdos.png` — best `state.value` so far, all erdos variants
- `best_reward_ac1.png` — same for ac1
- `best_reward_ac2.png` — same for ac2

`state.value` is normalized "higher = better" at env layer
(erdos `value = -c5_bound`, ac1 `value = -lower_bound_autocorr`,
ac2 `value = lower_bound_autocorr`). **Higher curve = better discovery.**

**Rep-novelty headline result (look at these plots):**
- erdos: rep-novelty's curve sits slightly above baseline through training,
  ending at value ≈ -0.3813 vs baseline -0.3816 (better by 0.0003).
- ac1: rep-novelty (truncated at step 25 by 24h timeout) reaches
  value ≈ -1.5068 by step ~22, vs baseline ≈ -1.5076 at step 30
  (better by 0.0008; *also* reached a comparable level several steps
  earlier, supporting the "faster convergence" reading).

### Ancestry / monomorphism (does it break the lineage commitment?)
- `ancestry_top1_root_frac.png` — fraction of buffer states descended from
  the single most-common root. Rises = lineage commitment. **H1 finding:**
  baselines all saturate ≥ 0.85 by step ~10-20 on every task.
  **Rep-novelty result on ac1: 75.8% at step 22 vs baseline 92.6% at step
  30** — visibly less monomorphic.
- `ancestry_depth_mean.png` — mean depth-from-root of buffer states.
  Higher = more in-lineage expansion vs broader seed sampling.
- `ancestry_n_distinct_roots.png` — number of distinct root seeds in
  buffer. Steady at 4 = every seed root survives.

### PUCT factor share (mechanism diagnostic — H3)
- `puct_share_Q.png` — fraction of |score| from Q (value estimate).
  Rises toward 1.0 → Q dominates by mid-training.
- `puct_share_bonus.png` — fraction from structural √(1+T)/(1+n).
  Falls toward 0 → exploration term out-shouted. **H3 finding.**
- `puct_Q_mean.png` — raw mean Q of picked candidates.
- `puct_bonus_mean.png` — raw mean structural bonus value.

For rep-novelty runs: their `puct_share_bonus.png` line should sit higher
than baseline (the additive `puct_c_rep * scale * nov_z` term keeps the
bonus competitive with Q even in late training).

---

## H4: Local vs global exploration

### Per-step geometry from post-hoc PCA (`tsne_evolution`)
- `tsne_centroid_drift.png` — distance of each step's centroid from
  step-0 centroid (shared PCA space). **H4d: plateaus by step ~10
  on baselines, "policy stops moving globally."**
- `tsne_spread.png` — within-step mean distance to centroid. Stays roughly
  constant. **H4a: within-step rollout diversity is preserved.**
- `tsne_diameter.png` — within-step max pairwise distance (variant of
  spread, more outlier-sensitive).

### Per-step RepExp drift (re-encoded with current model)
- `d3_drift_from_step0.png` — current centroid vs step-0 centroid (re-encoded
  with the live policy each step). Same shape as H4d centroid_drift.
- `d3_drift_from_prev.png` — step-to-step drift (not from step 0).
  **H4b: this drops 10× over training on baselines — "no new directions."**
- `d3_drift_rel_spread.png` — drift normalized by within-step spread.
- `h4c_cross_step_over_within_step.png` — the H4c ratio. **Drops from
  ~10× to ~1× by step 29 on baselines.** This is THE plot for "local-only
  exploration": when the ratio approaches 1, cross-step novelty is no
  longer larger than within-step noise.

### Nearest-neighbour overlap with past
- `d4_cov_frac_in_step0.png` — fraction of new rollouts within 1σ of
  step-0 cloud (after re-encoding). Rises = policy is regressing toward
  the initial region.
- `d4_cov_frac_in_prev.png` — same vs previous step.
- `d4_nn_dist_ratio_step0.png` — nearest-neighbour distance to step-0
  cloud divided by within-step spread.
- `d4_nn_dist_ratio_prev.png` — same vs previous step.

---

## D1-D2 from FINDINGS

### D1: gradient signal strength
- `d1_reward_variance_mean.png` — mean within-group reward variance
  across the 4 groups per step. Higher = stronger learning signal.
- `d1_reward_variance_max.png` — max-over-groups version.

### D2: effective sample size (entropic ESS)
- `d2_ess_mean.png` — within-step mean ESS (entropic-adaptive). Drops
  toward 1 = a single rollout dominates the gradient.
- `d2_beta_mean.png` — the adaptive entropic β over training.

### Other useful per-step env stats
- `env_correctness_mean.png` — fraction of rollouts with reward signal.
- `env_frac_all_bad.png` — fraction of groups where every rollout failed.
- `repexp_repr_spread.png` — within-step representational spread (mean of
  pairwise distances in 64-dim sparse-projected space).

---

## Rank disagreement (D6)

- `rank_disagreement_elliptic.png` — Kendall τ between reward and
  elliptic-bonus novelty, averaged across the 4 groups per step.
  Near 0 = reward and novelty are orthogonal (so a novelty bonus isn't
  just reproducing reward).
- `rank_disagreement_meancos.png` — Kendall with mean-cosine-distance novelty.
- `rank_disagreement_knn.png` — Kendall with kNN-distance novelty.

---

## PUCT internals from metrics

- `puct_selected_depth_mean.png` — mean depth of picked states across
  training. Rises = the sampler keeps picking from one deep lineage.
- `puct_selected_bonus_mean.png` — mean structural bonus of picked states.
- `puct_buffer_size.png` — PUCT buffer growth over time.

---

## Skipped (per-run only, not cross-task)

- 2-D t-SNE *embeddings* (`overlay.png` per run) — each has its own
  coordinate system; can't overlay meaningfully. Per-run files at
  `tinker_log/<run>/analysis/tsne_evolution/overlay.png` are the right
  place to look.
- Saturation breakthrough chains (`per_breakthrough.json`) — these are
  per-discovery records, not per-step time series. Per-run summary at
  `tinker_log/<run>/analysis/saturation/summary.json`.

---

## Mapping FINDINGS.md sections → cross_task plots

| FINDINGS.md | Cross-task plot(s) |
|---|---|
| H1 buffer monomorphism (universal) | `ancestry_top1_root_frac.png`, `ancestry_n_distinct_roots.png` |
| H2 exploration knobs don't fix it | Compare baseline vs loose-prune / mcts in `ancestry_top1_root_frac.png` |
| H3 Q dominates PUCT factor share | `puct_share_Q.png`, `puct_share_bonus.png` |
| H4a within-step rollout diversity is high | `tsne_spread.png`, `tsne_diameter.png`, `repexp_repr_spread.png` |
| H4b cross-step novelty collapses 10x→1x | `d3_drift_from_prev.png`, `d4_nn_dist_ratio_prev.png` |
| H4c cross-step / within-step ratio drops | `h4c_cross_step_over_within_step.png` (the specific metric) |
| H4d centroid drift plateaus | `tsne_centroid_drift.png`, `d3_drift_from_step0.png` |
| D1 reward variance | `d1_reward_variance_{mean,max}.png` |
| D2 entropic ESS | `d2_ess_mean.png`, `d2_beta_mean.png` |
| D3 RepExp global drift | `d3_drift_from_step0.png`, `d3_drift_from_prev.png`, `d3_drift_rel_spread.png` |
| D4 pairwise cosine sim | Closest proxies: `d4_cov_frac_in_*.png`, `d4_nn_dist_ratio_*.png` |
| D5 bonus Gini | Not plotted (would need per-pick distribution; check `puct_selection_step_*.json`) |
| D6 rank disagreement | `rank_disagreement_{elliptic,meancos,knn}.png` |
| D7 greedy saturation | Per-run only: `tinker_log/<run>/analysis/saturation/summary.json` |

---

## What to look for in each plot

1. **Baseline vs methods on the same task** (compare line styles within
   one color group):
   - rep-novelty's solid+square line in `best_reward_<task>.png`,
     `ancestry_top1_root_frac.png`, and `puct_share_bonus.png` —
     this is the rep-novelty-v1 story.
   - qd-archive's solid+diamond line will appear in the same plots once
     the in-progress runs accumulate enough steps (currently only
     `erdos-qd-archive` has data, and only batch 0-1).
2. **Baseline cross-task differences** (compare colors with solid lines):
   - erdos saturates monomorphism fastest; ac2 has the largest reward
     headroom (saturates 0.034 short of target).
3. **Whether ablations changed anything** (loose-prune, mcts, lineage-off):
   - In `ancestry_top1_root_frac.png` and `best_reward_erdos.png`, the
     ablation curves sit on top of baseline within ~0.001 — that's the
     H2 finding.

---

## Limitations / caveats

- `erdos-qd-archive` is currently early in training (sign-bug fix just
  re-launched it); curves cover only first 1-2 steps right now.
- `ac1-rep-novelty` was killed at step 25/30 (24h timeout). Curves cover
  steps 0-24 only.
- `ac1-qd-archive` and `ac2-qd-archive` not yet started training; will
  appear after queue gives them GPUs.
- `ac2-rep-novelty` never produced data (Ray-init hang at 10h on node-25).
- Re-run `cross_run_overlay.py` after the QD runs finish to include their
  curves.
- D5 bonus Gini is not in the auto-overlay (the per-step.json schema for
  it doesn't expose a single scalar; need to compute from
  `puct_selection_step_*.json` files directly).
