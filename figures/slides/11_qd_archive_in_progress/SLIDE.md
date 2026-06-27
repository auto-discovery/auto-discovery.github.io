# Slide 11 — CVT-MAP-Elites QD archive (v2) — in progress

**Experiment:** Experiment 3 (QD-archive method, v2)

**Key takeaway:** Replaces the buffer with a behavior-cell archive. CVT centroids fit once from a warmup pool of 80 valid descriptors → 64 cells, then sample_states picks parents from cells via softmax of z(quality)/tau + c_rep * z(cell_novelty). Mutually exclusive with rep-novelty v1 selection. Currently training (50 epochs, 5 GPUs/task, qos=high).

## Figures

- `best_reward_erdos.png` [present]
  - qd-archive's diamond-marker line will appear once enough steps accumulate.
- `ancestry_top1_root_frac.png` [present]
  - Same — looking for qd-archive to flatten or reduce top-1 coverage.
- `puct_share_bonus.png` [present]
  - QD doesn't use the structural bonus, so this line will sit at the floor — diagnostic that selection has switched modes.

## Narration

Placeholder slide; refresh figures after the QD runs accumulate steps. Final story: does the archive give both better reward AND broader coverage on the high-headroom tasks (AC2 especially)?

**Source:** (method spec: ttt_discover/methods/qd_archive.py; method results writeup pending)
