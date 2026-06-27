# Slide 03 — Q dominates the PUCT score by mid-training (mechanism)

**Experiment:** Experiment 1 (baseline diagnostic)

**Key takeaway:** The structural exploration term gets out-shouted: |Q-share| → ~1.0, |bonus-share| → 0. PUCT decays to pure exploitation.

## Figures

- `puct_share_Q.png` [present]
  - HEADLINE: Q-share rises toward 1.0.
- `puct_share_bonus.png` [present]
  - Bonus-share collapses toward 0 over training.
- `puct_selected_depth_mean.png` [present]
  - Mean depth of selected states grows → picking from deep in one lineage.

## Narration

This explains the mechanism behind H1: the structural √(1+T)/(1+n) term loses its grip; any new exploration signal has to *add* magnitude that survives standardization.

**Source:** FINDINGS.md §H3
