# Slide deck index — TTT-Discover diagnostic study + methods

All figures: `/workspace-vast/edwardosunny/exp/ttt-discover/runs/_summary/cross_task/`
This index: `/workspace-vast/edwardosunny/exp/ttt-discover/runs/_summary/slides/INDEX.md`

Companion writeups (also copied alongside):
  - `FINDINGS.md`  — full diagnostic writeup (H1-H4, D1-D7)
  - `METHODS_FINDINGS.md` — rep-novelty v1 results
  - `CROSS_TASK_PLOTS.md` — figure legend + analysis notes


## Experiment 1 (baseline diagnostic)

- **`01_monomorphism_universal/`** — Lineage monomorphism is universal across tasks
- **`02_knobs_dont_fix_it/`** — PUCT knobs (puct_c, topk, lineage blocking) don't break monomorphism
- **`03_Q_dominates_PUCT_score/`** — Q dominates the PUCT score by mid-training (mechanism)
- **`04_within_step_diversity_high/`** — Within-step rollout diversity stays HIGH throughout training (H4a)
- **`05_cross_step_novelty_collapses/`** — Cross-step novelty collapses — local exploration only
- **`06_rollouts_regress_to_past/`** — New rollouts increasingly land near previously-seen regions (D4)
- **`07_learning_signal_stays_meaningful/`** — Gradient signal stays meaningful but weakens (D1, D2)
- **`08_reward_and_novelty_are_orthogonal/`** — Reward and novelty rank-orderings are uncorrelated (D6)

## Experiment 2 (rep-novelty method, v1)

- **`09_repnovelty_wins_reward/`** — Rep-novelty PUCT bonus: clean win on AC1, third-place on erdos
- **`10_repnovelty_wins_diversity_on_ac1/`** — Rep-novelty: less monomorphic on AC1 (outcome a)

## Experiment 3 (QD-archive method, v2)

- **`11_qd_archive_in_progress/`** — CVT-MAP-Elites QD archive (v2) — in progress