# Slide 02 — PUCT knobs (puct_c, topk, lineage blocking) don't break monomorphism

**Experiment:** Experiment 1 (baseline diagnostic)

**Key takeaway:** Loose-prune, c=0.3, c=3.0, and lineage-blocking-off variants land on top of baseline within 0.001 reward. No knob disrupts the basin.

## Figures

- `ancestry_top1_root_frac.png` [present]
  - Same plot as slide 1 — point to dashed/dotted ablation lines clustering on baseline.
- `best_reward_erdos.png` [present]
  - All erdos variants converge to the same plateau ~0.381-0.382.

## Narration

Set up the motivation for adding rep-novelty: the diagnostic shows we need a new signal, not a knob retune.

**Source:** FINDINGS.md §H2
