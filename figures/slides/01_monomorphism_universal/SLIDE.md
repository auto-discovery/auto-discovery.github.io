# Slide 01 — Lineage monomorphism is universal across tasks

**Experiment:** Experiment 1 (baseline diagnostic)

**Key takeaway:** Every baseline collapses to ~85-95% top-1 root coverage by step 10-20, regardless of task. Search is depth-first into one lineage.

## Figures

- `ancestry_top1_root_frac.png` [present]
  - HEADLINE: top-1 root share rises to ≥0.85 on every task by mid-training.
- `ancestry_n_distinct_roots.png` [present]
  - Number of distinct roots in the buffer holds steady at 4 — roots aren't lost, just out-grown.
- `ancestry_depth_mean.png` [present]
  - Mean depth of buffer states grows — confirms drilling deeper into one lineage.

## Narration

Frame the universal pattern, then transition: 'the existing PUCT knobs do not fix this' (next slide).

**Source:** FINDINGS.md §H1
