# Slide 04 — Within-step rollout diversity stays HIGH throughout training (H4a)

**Experiment:** Experiment 1 (baseline diagnostic)

**Key takeaway:** The policy keeps producing diverse rollouts within each step — it's not entropy collapse of the policy itself.

## Figures

- `tsne_spread.png` [present]
  - HEADLINE: within-step mean dist to centroid is roughly flat.
- `tsne_diameter.png` [present]
  - Same shape with the max-pairwise variant.
- `repexp_repr_spread.png` [present]
  - Same with the RepExp mean pairwise dist metric.

## Narration

Critical setup for slide 5: rollouts ARE diverse, just always around the same point.

**Source:** FINDINGS.md §H4a
