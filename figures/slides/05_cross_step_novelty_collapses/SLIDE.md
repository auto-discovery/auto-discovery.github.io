# Slide 05 — Cross-step novelty collapses — local exploration only

**Experiment:** Experiment 1 (baseline diagnostic)

**Key takeaway:** Step-to-step centroid drift drops 10× by mid-training. The cross-step / within-step novelty ratio falls from ~10× to ~1× (within noise). The policy explores around a committed center, not across the rep space.

## Figures

- `h4c_cross_step_over_within_step.png` [present]
  - HEADLINE: ratio drops from ~10× to ~1× by step 29 → cross-step exploration becomes noise-level.
- `d3_drift_from_prev.png` [present]
  - Raw step-to-step drift: 10× decay over training.
- `tsne_centroid_drift.png` [present]
  - Centroid drift from step 0 plateaus by step ~10 — global motion stops.

## Narration

This IS the core diagnostic: the policy keeps generating local noise around a frozen center, never exploring genuinely new directions in rep space. That's what the new methods need to break.

**Source:** FINDINGS.md §H4b, H4c, H4d
