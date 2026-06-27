# Slide 09 — Rep-novelty PUCT bonus: clean win on AC1, third-place on erdos

**Experiment:** Experiment 2 (rep-novelty method, v1)

**Key takeaway:** Added an additive `puct_c_rep * scale * standardized_novelty` term to PUCT scoring. Honest result: on AC1 rep-novelty BEATS every other variant in BOTH speed and final reward (step 4 to 1.5068 vs baseline step-30 1.5086). On erdos it's middle-of-pack — loose-prune (topk=8, buf=4000, brute-force exploration) reaches baseline's final 0.3816 at step 4 and ends at 0.3810, beating rep-novelty's step-12 / 0.3813.

## Figures

- `best_reward_erdos.png` [present]
  - ERDOS — fastest-to-0.3816: loose-prune (step 4) > mcts-c=3.0 (step 7) > rep-novelty (step 12) > mcts-c=0.3 (step 18) > baseline (step 27). Final: loose-prune & mcts-c=3.0 tie at 0.3810; rep-novelty 0.3813; mcts-c=0.3 0.3814; baseline 0.3816. Rep-novelty is third.
- `best_reward_ac1.png` [present]
  - AC1 — rep-novelty (square, green) hits 1.5068 at step 4 and SUSTAINS it through step 24/30 (job timed out). lineage-blocking-off reaches 1.5086 at step 9, plateaus at 1.5075. Baseline only reaches 1.5086 at step 26 and never improves. Rep-novelty is the unambiguous winner.

## Narration

Honest framing: rep-novelty's value is task-conditional. On AC1 it's the best method by all measures. On erdos brute-force loose-prune (more children per parent + bigger buffer) wins by both metrics, suggesting that low-headroom tasks just need more expansion budget rather than a smarter signal. The split is consistent with the reward-headroom argument in METHODS_FINDINGS.md: erdos has ~0.0016 headroom from baseline to best-known frontier; AC1 has ~0.0046; so AC1 is where the better SELECTION mechanism actually has room to find new optima.

**Source:** METHODS_FINDINGS.md headline + AC1 section; FINDINGS.md §H2 (knobs comparison)
