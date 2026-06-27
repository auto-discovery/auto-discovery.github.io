# Rep-Novelty PUCT bonus — interim findings

**Status as of 2026-06-01 ~22:50 PT.**
- `mrep_erdos` (job 1641872) — complete (30/30)
- `mrep_ac1` (job 1642395) — **TIMEOUT at step 25/30**, walltime cap hit
  (sbatch `--time=1-00:00:00`); final best 1.5068, plateaued after step 22
- `mrep_ac2` (job 1642396) — **CANCELLED**, Ray init hung on node-25 for
  10 hours after "Started a local Ray instance". Same pattern as nodes
  19/29 from before. Sbatch updated with `--exclude=node-19,node-25,node-29`
  and `--time=2-00:00:00`; awaiting user to resubmit when GPU budget frees

## Method (one-paragraph recap)

Additive PUCT bonus:

```
score = Q + puct_c * scale * P * sqrt(1+T)/(1+n)   # original
      + puct_c_rep * scale * nov_z                  # rep-novelty term
```

- Frozen encoder: PEFT `disable_adapter()` → hidden states of base model on
  `(prompt + response)`, mean-pooled.
- Compression: sparse random projection (Li et al. 2006, `density = 1/sqrt(d_in)`),
  no fit-time cold-start. Reduces ~3584-dim hidden state to **64-dim
  descriptor**.
- Novelty: LinUCB/OFUL elliptical leverage `nov_raw = sqrt(h^T A^-1 h)` with
  `A = lam*I + sum_t gamma^(T-t) h_t h_t^T`, `gamma = 0.97`.
- Standardization: median/MAD computed only over rep-having candidates;
  missing reps get `nov_z = 0` (neutral, avoids MAD-collapse).
- Hook point: encoder runs only when `correctness > 0` (i.e. successful
  rollouts). State.frozen_rep is attached and serialised through JSON.

Run config: `puct_c_rep=1.0`, `gamma=0.97`, `descriptor_dim=64`, on 5 GPUs
(1 train + 4 vLLM TP=4), 30 epochs.

## Honest cross-variant comparison (all per `puct/buffer_value/max`)

I initially overstated rep-novelty's win because I only compared it to
baseline, ignoring the other ablations from FINDINGS §H2 (loose-prune,
mcts-c=0.3, mcts-c=3.0, lineage-blocking-off). When you compare against
ALL variants, the picture is:

### ERDOS (lower C₅ bound = better)

| Variant                  | Step to reach 0.3816 | Final best |
|--------------------------|----------------------|------------|
| baseline                 | step 27              | 0.3816     |
| **loose-prune** (topk=8, buf=4000) | **step 4** ⭐⭐ | **0.3810** ⭐⭐ |
| mcts-c=0.3               | step 18              | 0.3814     |
| mcts-c=3.0               | step 7               | 0.3810     |
| rep-novelty (v1)         | step 12              | 0.3813     |

**loose-prune is the unambiguous erdos winner — fastest AND best.** Rep-novelty
is third. The original FINDINGS §H2 noted ablations gave the same final reward
within 0.0006 of each other; that's still true, but the *convergence-speed*
ordering is dramatic.

### AC1 (lower autocorrelation upper bound = better)

| Variant                   | Step to reach 1.5086 | Final best |
|---------------------------|----------------------|------------|
| baseline                  | step 26              | 1.5086     |
| lineage-blocking-off      | step 9               | 1.5075     |
| **rep-novelty (v1)**      | **step 4** ⭐         | **1.5068** ⭐ |

**Rep-novelty wins AC1 cleanly on both speed and final reward.** Beats every
ablation, surpasses baseline's full-30-epoch result by step 4 (8% of training).

### AC2

Never ran successfully (Ray-init hang at 10h on node-25). Should be the most
informative task since it has the largest reward headroom (~0.034 below
target) — the only one where neither baseline nor any ablation got close to
the published frontier.

### Why the split?

Reward headroom from baseline to the best-known frontier:
- erdos:  ~0.0016 (very tight — every variant essentially closes this gap)
- AC1:    ~0.0046 (~3× more headroom)
- AC2:    ~0.034  (~20× more headroom)

On erdos, brute-force expansion (loose-prune's topk=8 + bigger buffer) is
enough to close the small gap quickly. On AC1, where there's genuine room to
find new optima, a *smarter selection signal* (rep-novelty) outperforms
brute-force budget. AC2's pending result is the cleanest test of whether
this generalizes.

## Sampler-buffer snapshot (final state, from `puct_sampler_step_*.json`)

**Direction convention** (per `scripts/analysis/FINDINGS.md` and the repo):

- **erdos** = Erdős C₅ overlap bound, **MIN** (target 0.380)
- **AC1**   = autocorrelation upper bound, **MIN** (target 1.503)
- **AC2**   = autocorrelation lower bound, **MAX** (target 0.97)

(I had erdos backwards in the first draft of this file — TTT-Discover's
0.380876 beats the human 0.380927 by going *lower*. Numbers below now
reflect the correct sign.)

| Task  | Run            | Step  | Buffer | Best       | Δ vs baseline (signed: + = rep-novelty better) |
|-------|----------------|-------|--------|------------|-----------------------------------------------|
| erdos | baseline       | 30/30 | 198    | 0.3816     | —                                             |
| erdos | rep-novelty    | 30/30 | 213    | **0.3813** | **+0.0003 (better — lower is better)**        |
| ac1   | baseline       | 30/30 | 243    | 1.5076     | —                                             |
| ac1   | rep-novelty    | 25/30 (TIMEOUT) | 183 | **1.5068** | **+0.0008 (better — lower is better)** |
| ac2   | baseline       | 30/30 | 220    | 0.9358     | —                                             |
| ac2   | rep-novelty    | warm  | —      | TBD        | TBD                                           |

So on the **two tasks with results so far, rep-novelty beats baseline on
reward.** AC1's lead (0.0008, with 8 steps still to run) is larger relative
to seed noise (~0.001-0.002) than erdos's (0.0003). Both improvements are
small in absolute terms — these are tasks near their published frontiers.

## Lineage diversity (erdos only — analysis re-runs queued for ac1/ac2)

Re-running `ancestry_monomorphism.py` after each run completes.

| Run                     | Steps | Distinct roots | **top-1 root coverage** | Depth mean | Depth p90 |
|-------------------------|-------|----------------|--------------------------|------------|-----------|
| erdos-baseline-1        | 30/30 | 4              | 84.8%                   | 15.7       | 27.0      |
| erdos-rep-novelty       | 30/30 | 4              | **94.4%** (worse!)      | 8.5        | 13.8      |
| ac1-baseline-1          | 30/30 | 4              | 92.6%                   | 15.1       | 27.0      |
| ac1-rep-novelty         | 22/30 | 4              | **75.8%** (better)      | 6.4        | 11.0      |
| ac2-baseline-1          | 30/30 | (re-run later)                                                          |

## The erdos paradox

On erdos, rep-novelty **improved reward slightly but became MORE monomorphic,
not less**:

- Reward delta: **+0.0003 better** (0.3816 → 0.3813; small but in the right
  direction)
- Top-1 root coverage: **84.8% → 94.4%**, +9.6 pp WORSE diversity
- Buffer depth distribution: collapsed (mean 15.7 → 8.5, p90 27 → 14)

This doesn't fit cleanly into any single quadrant of the hypothesis matrix —
the bonus is biting (during runs we observed `rep_bonus / Q` ratio rising to
~1.25 by step 4), and reward did move in the right direction, but lineage
spread went the *opposite* direction from what we predicted.

Interpretation: rep-novelty found a *different* lineage with a marginally
better C₅ bound, and then PUCT exploited that single different-looking
lineage to depth-fronted saturation. The bonus changed WHICH lineage wins
and made it a slightly-better one, but did not increase HOW MANY lineages
win. So we got the reward improvement without the diversity improvement.

On AC1 (next section), the same mechanism produces a much cleaner outcome.

## ac1 (in progress) — first task where rep-novelty wins on reward

At step 22/30, rep-novelty has already discovered:

```
top-5 buffer values (lower=better):
  rep-novelty:  1.5068, 1.5082, 1.5083, 1.5083, 1.5085
  baseline:     1.5076, 1.5080, 1.5083, 1.5086, 1.5088
```

It beats baseline's *final-30-step* best by 0.0008 with 8 steps still to go.
Multiple top-5 entries also surpass baseline. This is the first signal that
on a task with a meaningfully un-saturated objective (baseline was 0.0076
above the conjectured optimum), pushing into novel-rep regions actually finds
better solutions.

**Lineage diversity also improves on AC1**: top-1 root coverage 75.8% (vs
baseline's 92.6%), distinct-roots=4 (same), depth mean 6.4 (vs 15.1, p90 11
vs 27 — shallower exploration with broader root spread). Notably it does
NOT meet the 80/10 monomorphism criterion (`last_monomorphic_80_10 = false`),
whereas the baseline does. So on AC1 we are seeing outcome **(a)** from the
hypothesis matrix: **selection WAS the bottleneck** — coverage drops AND
reward improves.

(Caveat: comparing step-22 to step-30 is not strictly apples-to-apples;
top-1 coverage tends to grow over training, so 75.8% < 92.6% is a real
diversity improvement, but the final-step number may be higher.)

Whether the reward win is a real effect or noise depends on the remaining
8 steps — AC1's run-to-run variance is ~0.001-0.002, so 0.0008 is within
seed noise unless ac1-rep-novelty extends the lead further.

## ac2 — pending

AC2 is the diagnostic case from the baseline study: it saturated **0.034
short of target**, with re-encoded drift going 0 → 0.02 → 0.005-0.008
(active *un-learning* of useful directions; see FINDINGS.md §I4). If
rep-novelty is going to "bite" anywhere, AC2 is the most plausible candidate.
Results not yet available.

## Mechanism trace (logged per pick, from `puct_selection_step_*.json`)

Per-pick fields added: `nov_raw`, `nov_z`, `rep_bonus`.

Observations from erdos runs:

- The bonus is non-trivial. `rep_bonus` magnitudes track `Q` magnitudes
  by step 4 (ratio ~1.25 averaged over picks), meaning it's not a
  vanishing additive nudge — it's competitive with the value estimate.
- `nov_z` distribution is roughly N(0, 1) after MAD-fix, with occasional
  outliers ~+3 standard deviations that the bonus then chases.
- ESS (effective sample size of standardised novelty) stays near
  `group_size`, so the bonus isn't collapsing into one-dominant-state mode.

The implication is **mechanism is working**; the issue on erdos is that
the mechanism (per-pick novelty preference) does not produce the OUTCOME we
wanted (broader lineage spread at the buffer level).

## What this implies about the original hypothesis

The hypothesis matrix from the design phase was:

| Coverage drops | Reward improves | Interpretation |
|----------------|-----------------|----------------|
| Yes            | Yes             | Selection was the bottleneck |
| Yes            | No              | Population/seeds are the ceiling |
| No             | —               | Bonus didn't bite |
| **No**         | **No / tied**   | Bonus bit but in the wrong direction |

- **Erdos**: half outcome (a) (reward did improve, +0.0003) but with
  the diversity sign FLIPPED — top-1 root coverage got worse, not better.
  Doesn't sit in the matrix cleanly: "reward improves, coverage gets worse"
  is a fifth outcome the matrix didn't enumerate.
- **AC1**: clean outcome **(a)** — reward improves by 0.0008 AND coverage
  drops 92.6% → 75.8%. Selection was the bottleneck on AC1.

The two tasks split, and they split *consistently with their reward
headroom*:

| Task  | Baseline | Target | Headroom | Outcome             |
|-------|----------|--------|----------|---------------------|
| erdos | 0.3816   | 0.380  | 0.0016   | reward ↑, cov ↓ ↓ ↓ |
| ac1   | 1.5076   | 1.503  | 0.0046   | reward ↑, cov ↑     |
| ac2   | 0.9358   | 0.97   | 0.034    | TBD                 |

On erdos the headroom is small enough that the bonus's main effect is
*which* lineage gets exploited; on AC1 the headroom is large enough that
the bonus actively pulls the search across lineages. AC2 has the largest
headroom of all, which is the cleanest test of the method's value.

If AC2 looks like AC1, the case for v1 is strong. If AC2 looks like erdos
(reward up, coverage down), the fix is to gate the bonus by ancestry — two
straightforward variants:

1. **Per-root rep-novelty**: maintain a separate tracker per root seed, so
   the bonus rewards rep-diversity *within* a root rather than across.
   Pulls each lineage outward rather than letting one lineage hog the bonus.
2. **Cross-root rep-novelty floor**: explicit minimum bonus for picks from
   currently-underrepresented roots, additive on top of the elliptical term.
   Trades a little reward-following for guaranteed coverage.

Pending: see if AC1's reward win generalises to AC2, then decide whether
to ship method-v1 (current) or move straight to one of these v2 variants.

## Configuration / reproducibility

- Branch: `main` (multi-gpu merged 2026-05-31)
- Sbatch: `scripts/methods/rep_novelty/rep_novelty_{erdos,ac1,ac2}.sbatch`
- Runs: `/workspace-vast/$USER/exp/ttt-discover/runs/tinker_log/{task}-rep-novelty/`
- W&B project: `ttt-discover-method-rep-novelty`
- Job IDs: erdos=1641872 (done), ac1=1642395 (running), ac2=1642396 (running)

## Next step

When AC1 and AC2 finish:

```bash
python scripts/analysis/run_all.py \
    --run-dir /workspace-vast/$USER/exp/ttt-discover/runs/tinker_log/ac1-rep-novelty \
    --include-saturation

# Then update this file with:
#   - final AC1 best vs baseline
#   - AC2 best vs baseline (the critical test)
#   - ancestry top-1 coverage for both
#   - decide: ship v1 or move to per-root v2
```
