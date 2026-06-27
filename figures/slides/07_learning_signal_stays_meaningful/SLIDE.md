# Slide 07 — Gradient signal stays meaningful but weakens (D1, D2)

**Experiment:** Experiment 1 (baseline diagnostic)

**Key takeaway:** Within-group reward variance doesn't collapse to zero, ESS stays above 1 — the policy IS getting gradient updates. So commitment isn't because there's nothing to learn from.

## Figures

- `d1_reward_variance_mean.png` [present]
  - Mean within-group reward variance over training.
- `d2_ess_mean.png` [present]
  - Mean entropic ESS (max = group_size=16).
- `env_correctness_mean.png` [present]
  - Fraction of rollouts producing any reward signal.

## Narration

Rule out 'the policy ran out of gradient' as the cause of commitment.

**Source:** FINDINGS.md §D1, §D2
