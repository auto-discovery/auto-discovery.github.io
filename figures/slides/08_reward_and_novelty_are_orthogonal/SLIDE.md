# Slide 08 — Reward and novelty rank-orderings are uncorrelated (D6)

**Experiment:** Experiment 1 (baseline diagnostic)

**Key takeaway:** Kendall τ between reward and each novelty metric stays near 0 across training. The highest-reward and highest-novelty rollouts in each group are essentially independent — which means a novelty bonus contributes independent information, not a relabelled reward.

## Figures

- `rank_disagreement_elliptic.png` [present]
  - Elliptic-bonus novelty (LinUCB-style) vs reward.
- `rank_disagreement_meancos.png` [present]
  - Mean-cosine-distance novelty vs reward.
- `rank_disagreement_knn.png` [present]
  - kNN-distance novelty vs reward.

## Narration

Justification for adding a novelty-driven exploration term to PUCT.

**Source:** FINDINGS.md §D6
