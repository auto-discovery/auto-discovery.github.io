# Slide 10 — Rep-novelty: less monomorphic on AC1 (outcome a)

**Experiment:** Experiment 2 (rep-novelty method, v1)

**Key takeaway:** AC1 baseline ends at 92.6% top-1 root coverage; AC1 rep-novelty sits at 75.8% at step 22 (not monomorphic under the 80/10 criterion). Bonus magnitude stays competitive with Q throughout training — mechanism is biting.

## Figures

- `ancestry_top1_root_frac.png` [present]
  - Compare ac1 baseline (solid green) vs ac1 rep-novelty (square green) — visibly lower.
- `puct_share_bonus.png` [present]
  - Rep-novelty bonus share stays elevated where baseline collapses to 0.

## Narration

On erdos the same mechanism didn't reduce monomorphism (outcome 'reward up, coverage worse') — tied to reward headroom. AC1 has 3× more headroom than erdos, AC2 has 10× more — explaining the split. Suggests the QD method (next experiment) is the right next step.

**Source:** METHODS_FINDINGS.md §AC1 (outcome a)
