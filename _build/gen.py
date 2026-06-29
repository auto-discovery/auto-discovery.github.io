"""Generate per-experiment pages from content blocks.

Run from /home/edwardosunny/auto-discovery-site/_build/:
    python3 gen.py
"""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------------------
# Page registries (slug, title, badge, content_html)
# ---------------------------------------------------------------------------

ANALYSIS_PAGES = [
    ("index", "Analysis — overview", "8 experiments", "OVERVIEW"),
    ("h1-monomorphism", "H1 — Buffer monomorphism is universal", "H1", "EXPERIMENT"),
    ("h2-knobs", "H2 — PUCT knobs don't fix it", "H2", "EXPERIMENT"),
    ("h3-q-dominates", "H3 — Q dominates the PUCT score", "H3", "EXPERIMENT"),
    ("h4-local-vs-global", "H4 — Local vs global exploration", "H4", "EXPERIMENT"),
    ("d1-d2-learning-signal", "D1 + D2 — Learning signal stays meaningful", "D1·D2", "EXPERIMENT"),
    ("d3-d4-drift-coverage", "D3 + D4 — Drift &amp; coverage", "D3·D4", "EXPERIMENT"),
    ("d6-rank-disagreement", "D6 — Reward and novelty are uncorrelated", "D6", "EXPERIMENT"),
    ("ac2-unlearning", "AC2 — Active un-learning pathology", "AC2", "EXPERIMENT"),
]

METHOD_PAGES = [
    ("index", "Methods — overview", "11 experiments", "OVERVIEW"),
    ("rep-novelty", "Rep-novelty PUCT bonus", "Method 1", "EXPERIMENT"),
    ("qd-archive", "CVT-MAP-Elites QD archive", "Method 2", "EXPERIMENT"),
    ("hybrid-puctc3", "Hybrid 1 — QD + high warmup PUCT_C", "Hybrid 1", "EXPERIMENT"),
    ("hybrid-visit", "Hybrid 2 — QD + visit-count cell bonus", "Hybrid 2", "EXPERIMENT"),
    ("dual-diversity", "Dual-diversity ladder — overview", "Method 3", "OVERVIEW"),
    ("e0-batch-gate", "E0 — Batch-confound gate", "E0", "EXPERIMENT"),
    ("e1-parent-sensitivity", "E1 — Parent-sensitivity probe", "E1", "EXPERIMENT"),
    ("e2-descriptor-validity", "E2 — Descriptor validity", "E2", "EXPERIMENT"),
    ("e3-2x2", "E3 — Selection × update 2×2", "E3", "EXPERIMENT"),
    ("e4-shared-vs-sep", "E4 — Shared vs separate A", "E4", "EXPERIMENT"),
    ("e5-alpha-sweep", "E5 — α-schedule stress test", "E5", "EXPERIMENT"),
    ("leaderboards", "Cross-task leaderboards", "Summary", "OVERVIEW"),
]


# ---------------------------------------------------------------------------
# Sidebar builder
# ---------------------------------------------------------------------------

def render_sidebar(section: str, active_slug: str) -> str:
    pages = ANALYSIS_PAGES if section == "analysis" else METHOD_PAGES
    items = []
    items.append(f'<h4>{section.title()}</h4><ul>')
    for slug, title, badge, _ in pages:
        href = "index.html" if slug == "index" else f"{slug}.html"
        cls = "active" if slug == active_slug else ""
        # Short title for sidebar — use description part after the badge prefix
        if slug == "index":
            short = "Overview"
        elif " — " in title:
            short = title.split(" — ", 1)[1]
        else:
            short = title
        items.append(
            f'<li><a class="{cls}" href="{href}">'
            f'<span class="sidebar-tag">{badge}</span>{short}</a></li>'
        )
    items.append('</ul>')
    return "\n".join(items)


def render_page(section: str, slug: str, title_full: str, badge: str, kind: str,
                body_html: str, prev_link=None, next_link=None) -> str:
    sidebar = render_sidebar(section, slug)
    top_active = section
    # exp_nav (prev/next)
    nav_html = '<div class="exp-nav">'
    if prev_link:
        slug_p, ttl_p = prev_link
        nav_html += (f'<a href="{slug_p}.html">'
                     f'<div class="dir">← Previous</div>'
                     f'<div class="ttl">{ttl_p}</div></a>')
    else:
        nav_html += '<span></span>'
    if next_link:
        slug_n, ttl_n = next_link
        nav_html += (f'<a class="next" href="{slug_n}.html">'
                     f'<div class="dir">Next →</div>'
                     f'<div class="ttl">{ttl_n}</div></a>')
    nav_html += '</div>'

    # exp header (with badge)
    if slug == "index":
        header = f'<h1>{title_full}</h1>'
    else:
        title_main = title_full
        header = (
            f'<div class="exp-header">'
            f'  <span class="exp-id">{badge}</span>'
            f'  <span style="color: var(--text-dim); font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.05em;">{kind}</span>'
            f'</div>'
            f'<h1>{title_main}</h1>'
        )

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title_full.replace('&amp;', '&')} · Auto-Discovery</title>
<link rel="stylesheet" href="../style.css">
</head>
<body>
<nav class="top">
  <div class="brand">auto-discovery<span class="dot">/</span><span class="mono">.</span></div>
  <a class="tab" href="../index.html">Overview</a>
  <a class="tab {'active' if top_active == 'analysis' else ''}" href="../analysis/">Analysis</a>
  <a class="tab {'active' if top_active == 'methods' else ''}" href="../methods/">Methods</a>
</nav>

<div class="layout">
  <aside class="sidebar">{sidebar}</aside>
  <main>
    {header}
    {body_html}
    {nav_html}
  </main>
</div>

<footer>
  Repo: <a href="https://github.com/EdwardoSunny/rep-ttt">github.com/EdwardoSunny/rep-ttt</a> on <code>method-rep-novelty</code>.
</footer>
</body>
</html>
"""


# ---------------------------------------------------------------------------
# Content blocks
# ---------------------------------------------------------------------------

# Helper: figure
def fig(src, caption):
    return f'<figure><img src="../figures/cross_task/{src}" alt=""><figcaption>{caption}</figcaption></figure>'

# Helper: 2-column figure grid
def figgrid(items):
    inner = "\n".join(
        f'<figure><img src="../figures/cross_task/{s}" alt=""><figcaption>{c}</figcaption></figure>'
        for s, c in items
    )
    return f'<div class="figure-grid">{inner}</div>'


CONTENT = {}

# ============================== ANALYSIS ==============================

CONTENT[("analysis", "index")] = """
<div class="subtitle">
  Diagnostic study on 7 baseline runs across erdos, AC1, AC2 — 8 experiments grouped into headline weaknesses (H1-H4) and detailed mechanisms (D1-D7).
</div>

<h2>Setup</h2>
<div class="card">
  <p><strong>Tasks</strong></p>
  <ul>
    <li><span class="tag accent">erdos</span> minimize Erdős C₅ overlap bound (frontier <code>0.380876</code>)</li>
    <li><span class="tag accent">AC1</span> minimize sup‖autocorrelation‖ (frontier <code>1.503</code>)</li>
    <li><span class="tag accent">AC2</span> maximize lower-bound autocorrelation (frontier <code>0.97</code>)</li>
  </ul>
  <p><strong>Config:</strong> Qwen3-8B + LoRA · <code>group_size=16</code>, <code>groups_per_batch=4</code> → <strong>64 rollouts/step</strong> · 30 epochs · PUCT sampler · vLLM + PEFT</p>
  <p><strong>Runs (7):</strong> 4 erdos variants (baseline, loose-prune, mcts c=0.3, c=3.0) · 2 ac1 variants (baseline, lineage-blocking-off) · 1 ac2 baseline</p>
</div>

<h2>Experiments</h2>
<ul class="findings">
  <li><span class="h-label">H1</span><a href="h1-monomorphism.html">Buffer monomorphism is universal</a> — every run collapses to 84-96% top-1 root.</li>
  <li><span class="h-label">H2</span><a href="h2-knobs.html">PUCT knobs don't fix it</a> — 0.0006 spread across all variants.</li>
  <li><span class="h-label">H3</span><a href="h3-q-dominates.html">Q dominates the PUCT score</a> — exploration term self-disables.</li>
  <li><span class="h-label">H4</span><a href="h4-local-vs-global.html">Local exploration is preserved; global is not</a> — THE key finding.</li>
  <li><span class="h-label">D1·D2</span><a href="d1-d2-learning-signal.html">Learning signal stays meaningful</a> — gradient isn't dead.</li>
  <li><span class="h-label">D3·D4</span><a href="d3-d4-drift-coverage.html">Global drift &amp; coverage of past regions</a> — confirms H4 from independent metrics.</li>
  <li><span class="h-label">D6</span><a href="d6-rank-disagreement.html">Reward ⊥ novelty</a> — Kendall τ ≈ 0; novelty bonus carries independent information.</li>
  <li><span class="h-label">AC2</span><a href="ac2-unlearning.html">Active un-learning pathology</a> — policy drifts backward, eff rank shrinks.</li>
</ul>

<h2>Distilled weaknesses</h2>
<ul class="findings">
  <li><span class="h-label">W1</span><strong>Single-lineage commitment.</strong> PUCT picks one root early and depth-fronts it.</li>
  <li><span class="h-label">W2</span><strong>PUCT exploration self-disables.</strong> <code>√(1+T)/(1+n)</code> shrinks faster than Q grows.</li>
  <li><span class="h-label">W3</span><strong>Local-only exploration.</strong> Per-step diversity high, cross-step novelty collapses 10×.</li>
  <li><span class="h-label">W4</span><strong>Active unlearning (AC2).</strong> Policy drift goes <code>0 → 0.02 → 0.005</code>; eff rank <code>9.0 → 7.5</code>.</li>
</ul>

<div class="callout warn">
  <strong>Caveat that emerged after publishing.</strong> The diagnostic was at 64 rollouts/step. Phase A (currently running) tests the same baseline at paper-spec 512 rollouts and is already matching the prior method-best on erdos. H1-H4 mechanisms are real per-step phenomena; their <em>practical cost</em> may shrink at proper batch.
</div>
"""

CONTENT[("analysis", "h1-monomorphism")] = f"""
<div class="subtitle">Every TTT-Discover baseline collapses to one dominant root lineage within ~10-20 steps, regardless of task or knob setting. The other seeds survive in the buffer but stop being expanded.</div>

<h2>Key numbers</h2>
<table>
  <thead><tr><th>Run</th><th>Top-1 root coverage</th><th>Distinct roots</th><th>Monomorphic (80/10)</th></tr></thead>
  <tbody>
    <tr><td>erdos-baseline</td><td class="num">84.8%</td><td class="num">4</td><td>YES</td></tr>
    <tr><td>erdos-loose-prune</td><td class="num">83.7%</td><td class="num">4</td><td>YES</td></tr>
    <tr><td>erdos-mcts c=0.3</td><td class="num"><strong>95.8%</strong></td><td class="num">4</td><td>YES</td></tr>
    <tr><td>erdos-mcts c=3.0</td><td class="num">94.3%</td><td class="num">4</td><td>YES</td></tr>
    <tr><td>ac1-baseline</td><td class="num">92.6%</td><td class="num">4</td><td>YES</td></tr>
    <tr><td>ac1-noblock</td><td class="num">92.9%</td><td class="num">4</td><td>YES</td></tr>
    <tr><td>ac2-baseline</td><td class="num">89.1%</td><td class="num">4</td><td>YES</td></tr>
  </tbody>
</table>

<h2>Evidence</h2>
{fig("ancestry_top1_root_frac.png", "Top-1 root coverage over training (color = task, linestyle = variant). All runs saturate at 0.85+.")}
{figgrid([
  ("ancestry_n_distinct_roots.png", "Number of distinct roots holds at 4 (= num seeds). Roots aren't lost, they're out-grown."),
  ("ancestry_depth_mean.png", "Mean depth of buffer states grows — confirms drilling deeper into one lineage rather than broader."),
])}

<h2>What it means</h2>
<div class="callout">
  <strong>TTT-Discover always picks one seed and exploits it.</strong> The "search" is effectively a single-lineage search after the first 10-20 epochs. Whatever broad exploration the original 4 seeds were supposed to provide is structurally undone by selection pressure.
</div>
"""

CONTENT[("analysis", "h2-knobs")] = f"""
<div class="subtitle">PUCT exposes several knobs (<code>puct_c</code>, <code>topk_children</code>, <code>max_buffer_size</code>, <code>lineage_blocking</code>). Sweeping them doesn't move any of the H1 numbers — and barely moves reward either.</div>

<h2>Variants tested</h2>
<table>
  <thead><tr><th>Variant</th><th>puct_c</th><th>topk</th><th>buf</th><th>Best reward</th></tr></thead>
  <tbody>
    <tr><td>baseline</td><td>1.0</td><td>2</td><td>1000</td><td class="num">0.381584</td></tr>
    <tr><td>loose-prune</td><td>1.0</td><td>8</td><td>4000</td><td class="num"><strong>0.381044</strong></td></tr>
    <tr><td>mcts-puct_c=0.3</td><td>0.3</td><td>2</td><td>1000</td><td class="num">0.381355</td></tr>
    <tr><td>mcts-puct_c=3.0</td><td>3.0</td><td>2</td><td>1000</td><td class="num">0.380983</td></tr>
  </tbody>
</table>
<p>Reward spread across all 4: <strong>0.0006</strong> (0.3810–0.3816). All four still monomorphic at 83-96% top-1 root.</p>

<h2>Evidence</h2>
{fig("best_reward_erdos.png", "All 4 erdos variants converge to within 0.0006 of each other. Different paths, same plateau.")}
{fig("ancestry_top1_root_frac.png", "Same monomorphism on all variants — knob-tuning doesn't disrupt the commitment.")}

<h2>What it means</h2>
<div class="callout">
  <strong>The commitment isn't a hyperparameter problem; it's structural.</strong> No setting of the existing knobs breaks the single-lineage convergence. To get different behavior you have to change the <em>mechanism</em>, not its parameters — which motivates the rep-novelty additive term (Method 1) and the QD-archive replacement (Method 2).
</div>
"""

CONTENT[("analysis", "h3-q-dominates")] = f"""
<div class="subtitle">The PUCT score is <code>Q + puct_c · scale · P · √(1+T)/(1+n)</code>. The structural exploration term shrinks with <code>√T/n</code> while Q grows — by mid-training, Q dominates and PUCT becomes greedy.</div>

<h2>The decay</h2>
<table>
  <thead><tr><th>Step</th><th>|Q|-share</th><th>|bonus|-share</th></tr></thead>
  <tbody>
    <tr><td>0</td><td class="num">0.99</td><td class="num">0.01</td></tr>
    <tr><td>10</td><td class="num">0.85</td><td class="num">0.15</td></tr>
    <tr><td>30</td><td class="num">0.76–0.97 (variant-dependent)</td><td class="num">0.03–0.24</td></tr>
  </tbody>
</table>

<h2>Evidence</h2>
{figgrid([
  ("puct_share_Q.png", "|Q|-share rises across training. By step 30 most variants are >0.90."),
  ("puct_share_bonus.png", "|bonus|-share collapses correspondingly. The exploration term self-disables."),
])}
{figgrid([
  ("puct_Q_mean.png", "Raw mean Q of picked candidates grows."),
  ("puct_bonus_mean.png", "Raw mean bonus shrinks toward zero."),
])}

<h2>What it means</h2>
<div class="callout">
  <strong>Implication for new methods.</strong> Any added exploration signal must be on a scale that <em>survives standardization against Q</em> — bigger than the structural <code>√T/n</code> term that PUCT lets decay. Rep-novelty's bonus is scaled by the candidate value range (<code>scale</code>) for exactly this reason.
</div>
"""

CONTENT[("analysis", "h4-local-vs-global")] = f"""
<div class="subtitle">THE key finding. The policy keeps producing diverse rollouts <em>per step</em>, but stops moving the <em>center</em> of those rollouts in representation space. Four sub-findings (H4a–d) all point the same way.</div>

<h2>H4a — Within-step rollout diversity stays HIGH</h2>
<p>Mean pairwise cosine similarity of rollouts within a single step ≈ 0.85 over all 30 steps. Per-step the policy generates spread-out rollouts on every task.</p>
{figgrid([
  ("tsne_spread.png", "Within-step mean distance to centroid stays roughly flat through training."),
  ("repexp_repr_spread.png", "Same finding from the RepExp pairwise-distance metric."),
])}

<h2>H4b — Cross-step novelty COLLAPSES</h2>
<p>Step-to-step centroid drift starts at ~0.04 and falls to ~0.004 by step 29 — <strong>10× drop</strong>.</p>
{fig("d3_drift_from_prev.png", "Cross-step drift collapses 10× over training.")}

<h2>H4c — Cross-step / within-step ratio drops to ~1</h2>
<p>Early training: cross-step movement is ~10× the within-step rollout spread. Late training: cross-step movement = within-step noise. <strong>The centroid effectively stops moving relative to per-step noise.</strong></p>
{fig("h4c_cross_step_over_within_step.png", "Cross-step / within-step ratio crashes from ~10× to ~1× by step 29.")}

<h2>H4d — Global centroid drift plateaus by step ~10</h2>
{fig("tsne_centroid_drift.png", "Centroid drift from step-0 saturates by step ~10 and stays flat.")}

<h2>What it means</h2>
<div class="callout">
  <strong>The policy explores <em>locally</em> around a committed center, not <em>globally</em> across rep space.</strong> It keeps making diverse rollouts in the same neighborhood forever. This is the diagnosis that motivates every method we built — both rep-novelty (push toward globally-novel reps) and QD-archive (force coverage across behavior cells).
</div>
"""

CONTENT[("analysis", "d1-d2-learning-signal")] = f"""
<div class="subtitle">Two checks that the commitment problem isn't because the gradient died — it's not.</div>

<h2>D1 — Within-group reward variance</h2>
<p>Stays meaningful throughout training on every task. Even after monomorphism, the within-group rollouts have a range of rewards → the policy gradient is non-trivial.</p>
{figgrid([
  ("d1_reward_variance_mean.png", "Mean within-group reward variance over training."),
  ("d1_reward_variance_max.png", "Max-over-groups version — even more clearly maintained."),
])}

<h2>D2 — Entropic ESS</h2>
<p>The entropic-adaptive-β advantage estimator computes an effective sample size per group. It stays above 1 throughout training → not a single-rollout-dominates collapse.</p>
{figgrid([
  ("d2_ess_mean.png", "Within-step mean ESS (max = group_size=16). Stays well above 1."),
  ("d2_beta_mean.png", "The adaptive entropic β over training."),
])}

<h2>Bonus: env-level signal</h2>
{figgrid([
  ("env_correctness_mean.png", "Fraction of rollouts producing any reward signal (correctness > 0)."),
  ("env_frac_all_bad.png", "Fraction of groups where every rollout failed."),
])}

<h2>What it means</h2>
<div class="callout">
  <strong>Rules out "the policy ran out of gradient" as a cause of H1 commitment.</strong> Gradient signal stays meaningful; ESS stays > 1; correctness stays above floor. The selection bias that drives monomorphism is independent of "is there anything to learn from?".
</div>
"""

CONTENT[("analysis", "d3-d4-drift-coverage")] = f"""
<div class="subtitle">Two metrics that confirm H4 from independent angles: rep-encoded global drift, and how often new rollouts land in previously-seen regions.</div>

<h2>D3 — RepExp global drift</h2>
<p>Re-encode all buffered states with the <em>current</em> policy each step, compute centroid drift. Same shape as H4d — plateaus by step ~10.</p>
{figgrid([
  ("d3_drift_from_step0.png", "Centroid drift from step 0 (re-encoded with current model). Plateaus."),
  ("d3_drift_from_prev.png", "Step-to-step drift. Falls 10×."),
])}
{fig("d3_drift_rel_spread.png", "Drift normalized by within-step spread.")}

<h2>D4 — Coverage of past regions</h2>
<p>How often do new rollouts land in or near the cloud of previously-seen rollouts?</p>
{figgrid([
  ("d4_cov_frac_in_step0.png", "Fraction of new rollouts within 1σ of step-0 cloud — rises over training."),
  ("d4_cov_frac_in_prev.png", "Same vs previous step."),
])}
{figgrid([
  ("d4_nn_dist_ratio_step0.png", "NN-distance to step-0 reps / within-step spread — shrinks."),
  ("d4_nn_dist_ratio_prev.png", "Same vs previous step."),
])}

<h2>What it means</h2>
<div class="callout">
  <strong>Three independent metrics (H4d centroid drift, D3 RepExp drift, D4 NN-overlap) all agree.</strong> The policy spends increasing fractions of its rollouts re-visiting the early-training neighborhood. This isn't a measurement artifact of one metric; it's a real property of the policy trajectory.
</div>
"""

CONTENT[("analysis", "d6-rank-disagreement")] = f"""
<div class="subtitle">Within each 16-rollout group, rank the rollouts two ways: by reward, and by representational novelty. Compute Kendall τ between the two rankings. The answer: ~0 throughout training.</div>

<h2>Three novelty measures</h2>
<p>We tried three definitions of "novelty" to make sure the finding isn't metric-specific:</p>
<ul>
  <li><strong>Elliptic bonus</strong>: LinUCB / OFUL confidence width <code>√(hᵀ A⁻¹ h)</code> against an online covariance.</li>
  <li><strong>Mean-cosine-distance</strong>: mean cosine distance to other group members.</li>
  <li><strong>kNN-distance</strong>: distance to nearest neighbor among other group members.</li>
</ul>

<h2>Evidence</h2>
{figgrid([
  ("rank_disagreement_elliptic.png", "Kendall τ between reward and elliptic-bonus novelty, averaged across groups per step."),
  ("rank_disagreement_meancos.png", "Same for mean-cosine-distance novelty."),
])}
{fig("rank_disagreement_knn.png", "Same for kNN-distance novelty. All three measures give τ ≈ 0 throughout training.")}

<h2>What it means</h2>
<div class="callout good">
  <strong>This is the structural justification for adding a novelty bonus.</strong> If reward and novelty were correlated (τ near ±1), a novelty bonus would just be a relabeled reward bonus. Since τ ≈ 0, novelty carries <em>independent</em> information about which states to explore. The bonus we add isn't a different way to chase reward; it's a different signal entirely.
</div>
"""

CONTENT[("analysis", "ac2-unlearning")] = """
<div class="subtitle">AC2 is the worst-case TTT-Discover failure mode. The baseline saturated <strong>0.034 below the frontier</strong> (0.9358 vs 0.97) — the largest gap of any task. And it's not just stuck — it's <em>regressing</em>.</div>

<h2>The drift trajectory</h2>
<p>Re-encoded global drift over training on AC2:</p>
<table>
  <thead><tr><th>Phase</th><th>Drift from step 0</th></tr></thead>
  <tbody>
    <tr><td>Step 0–5</td><td class="num">0 → 0.02</td></tr>
    <tr><td>Step 5–15</td><td class="num">0.02 (peak)</td></tr>
    <tr><td>Step 15–30</td><td class="num">0.02 → <strong>0.005–0.008</strong> (regressing!)</td></tr>
  </tbody>
</table>
<p>The centroid moves <em>away</em> from step 0 in early training (good), then moves <em>back toward</em> step 0 in late training (bad). It's losing the representational ground it gained.</p>

<h2>The rank collapse</h2>
<p>Effective rank of the rep covariance:</p>
<ul>
  <li>Early training: <strong>9.0</strong> (out of 64 max — already low)</li>
  <li>Late training: <strong>7.5</strong> — rank drops 1.5 over training</li>
</ul>
<p>The policy actively shrinks the dimensionality of its representation. Useful directions are being un-learned.</p>

<div class="callout bad">
  <strong>AC2's failure isn't "couldn't find better" — it's actively un-learning structure it had earlier.</strong> This is qualitatively different from H1-H4 (greedy commitment). Both methods we built (rep-novelty, QD-archive) are selection-side interventions — they don't address active unlearning, which is an <em>objective</em>-side problem (KL pressure, β schedule, advantage estimator).
</div>

<h2>Implications for method work</h2>
<p>AC2 is the one task where neither rep-novelty nor QD-archive helped. The diagnostic predicts this:</p>
<ul>
  <li><strong>Selection-side methods</strong> (both ours) push the policy toward different parents to expand. But if the policy itself is actively shedding useful directions, picking different parents won't recover them.</li>
  <li><strong>Objective-side fixes</strong> would target <em>why</em> the policy is shrinking — likely a too-large KL/β allowing convergence to a low-rank attractor.</li>
</ul>
<p>Future work on AC2 should focus on KL coefficient sweeps, β schedules, and possibly LoRA-island ensembles rather than further selection-side experiments.</p>
"""

# ============================== METHODS ==============================

CONTENT[("methods", "index")] = """
<div class="subtitle">Two original selection methods plus two hybrids, then a new dual-diversity ladder (E0–E5) that uses one rep-novelty signal in both selection AND update. Each method was built from the analysis findings and tested head-to-head against PUCT-knob ablations.</div>

<h2>What's here</h2>
<ul class="findings">
  <li><span class="h-label">M1</span><a href="rep-novelty.html">Rep-novelty PUCT bonus</a> — additive elliptical-leverage novelty term. <strong>Wins AC1 at 64 rollouts.</strong></li>
  <li><span class="h-label">M2</span><a href="qd-archive.html">CVT-MAP-Elites QD archive</a> — replaces lineage buffer with behavior-cell archive. <strong>Wins erdos by 10⁻⁶ at 64 rollouts.</strong></li>
  <li><span class="h-label">H1</span><a href="hybrid-puctc3.html">Hybrid 1 — QD + high warmup PUCT_C</a> — built, pending compute.</li>
  <li><span class="h-label">H2</span><a href="hybrid-visit.html">Hybrid 2 — QD + visit-count cell bonus</a> — built, pending compute.</li>
  <li><span class="h-label">M3</span><a href="dual-diversity.html">Dual-diversity ladder (E0–E5)</a> — shared signal in selection + update. <strong>30 jobs queued, code-complete.</strong></li>
  <li><span class="h-label">★</span><a href="leaderboards.html">Cross-task leaderboards</a> — full 6-digit results on all 3 tasks.</li>
</ul>

<h2>How they relate to the diagnosis</h2>
<table>
  <thead><tr><th>Weakness</th><th>Addressed by</th></tr></thead>
  <tbody>
    <tr><td>W1 — single-lineage commitment</td><td>QD-archive (replaces lineage with cells); rep-novelty (pushes toward novel reps)</td></tr>
    <tr><td>W2 — PUCT exploration self-disables</td><td>rep-novelty (scale-survives Q standardization)</td></tr>
    <tr><td>W3 — local-only exploration</td><td>Both methods explicitly reward global-rep movement</td></tr>
    <tr><td>W4 — AC2 active unlearning</td><td><strong>Neither</strong> (selection-side fixes don't address objective-side regression)</td></tr>
  </tbody>
</table>

<div class="callout warn">
  <strong>Important caveat.</strong> All methods above ran at 64 rollouts/step. The Phase A baseline at 512 rollouts/step already matches the prior method-best on erdos (0.380965) with no method enabled. The methods may have been beating a weak baseline, not introducing genuine signal. Phase A is the proper noise floor.
</div>
"""

CONTENT[("methods", "rep-novelty")] = f"""
<div class="subtitle">Add an elliptical-leverage novelty term to PUCT's selection score. Frozen encoder + sparse projection + LinUCB confidence width.</div>

<h2>Mechanism</h2>
<div class="card">
<pre>score(i) = Q(i) + puct_c · scale · P(i) · √(1+T)/(1+n[i])      # existing PUCT
                + puct_c_rep · scale · z(novelty(i))            # ← new additive term</pre>
<p><code>novelty(i)</code>:</p>
<ol>
  <li><strong>Frozen encoder</strong>: rollout response → Qwen3-8B with LoRA <em>disabled</em> → mean-pool last hidden → 3584-d</li>
  <li><strong>Compress to 64-d</strong> via sparse random projection (Li et al. 2006, density <code>1/√d_in</code>, no fitting)</li>
  <li><strong>Online elliptical covariance</strong>: <code>A = λI + Σ γ^(T-t) hₜhₜᵀ</code> with γ=0.97 decay</li>
  <li><strong>Score</strong>: <code>novelty(i) = √(hᵀ A⁻¹ h)</code> — LinUCB / OFUL confidence width</li>
  <li><strong>Robust-standardize</strong> across candidates (median/MAD) → <code>nov_z</code></li>
</ol>
<p>The tracker observes every picked state, so subsequent selections compute novelty against past picks. Code: <code>ttt_discover/methods/rep_novelty.py</code>.</p>
</div>

<h2>Why it addresses the diagnosis</h2>
<ul>
  <li><strong>D6</strong>: reward ⊥ novelty (τ ≈ 0) — bonus injects independent gradient signal</li>
  <li><strong>H3</strong>: scaled by <code>scale</code> so it survives standardization against Q</li>
  <li><strong>H4b/d</strong>: novelty rewards picks in directions A⁻¹ poorly covers — pushes the centroid into new regions</li>
</ul>

<h2>Results (30 epochs, <code>puct_c_rep=1.0, γ=0.97, d=64</code>)</h2>
<table>
  <thead><tr><th>Task</th><th>Best</th><th>vs baseline</th><th>Notes</th></tr></thead>
  <tbody>
    <tr><td><span class="tag accent">erdos</span></td><td class="num">0.381272</td><td class="num">+0.000312 better</td><td>3rd place; loose-prune (0.381044) and mcts-c=3.0 (0.380983) both beat it</td></tr>
    <tr class="winner"><td><span class="tag accent">AC1</span></td><td class="num">1.506845</td><td class="num">+0.001783 better</td><td><strong>Best AC1 result of any variant.</strong> Also less monomorphic (75.8% top-1 root vs baseline 92.6%)</td></tr>
    <tr><td><span class="tag accent">AC2</span></td><td>—</td><td>—</td><td>Cluster Ray-init hang at 10h, no data</td></tr>
  </tbody>
</table>

<h2>Evidence the mechanism is biting</h2>
{fig("puct_share_bonus.png", "Rep-novelty (heavy square marker) keeps the |bonus|-share elevated where baseline collapses to 0 — the additive novelty term substitutes for the vanishing structural PUCT bonus.")}
{fig("ancestry_top1_root_frac.png", "AC1 rep-novelty (green square) sits at 75.8% top-1 root coverage vs ac1-baseline (green circle) at 92.6% — visibly less monomorphic.")}
{fig("best_reward_ac1.png", "Best reward over training, all AC1 variants. Rep-novelty hits 1.5068 at step ~22 and sustains it — best of any variant.")}

<h2>Interpretation</h2>
<div class="callout">
  <strong>The split is correlated with reward headroom.</strong> erdos has only 0.0016 headroom to the frontier — brute-force expansion (loose-prune) closes the gap by itself. AC1 has 0.0046 headroom — enough room for a smarter selection signal to find new optima. AC2's active unlearning isn't a selection problem, so rep-novelty doesn't help.
</div>
"""

CONTENT[("methods", "qd-archive")] = f"""
<div class="subtitle">Throw out the lineage-based PUCT buffer entirely. Replace it with a CVT-MAP-Elites archive that partitions rep space into behavior cells and picks parents by softmax over cell quality + cell novelty.</div>

<h2>Mechanism</h2>
<div class="card">
<ol>
  <li><strong>Warmup</strong>: run PUCT for ~5-7 batches until 80 valid (<code>correctness&gt;0</code>) rollouts have frozen-rep descriptors.</li>
  <li><strong>Fit CVT once</strong>: k-means on the 80 descriptors → 64 centroids. <em>Centroids frozen.</em></li>
  <li><strong>Each cell keeps one elite</strong>: the highest-reward state whose descriptor falls in that cell.</li>
  <li><strong>Selection</strong>: pick a cell via softmax of <code>z(quality)/tau + c_rep · z(cell_novelty)</code>. Cell-novelty reuses the same LinUCB tracker but observes cell centroids of picked parents.</li>
  <li>The cell's elite becomes the next parent for rollouts.</li>
</ol>
<p>Config used: <code>n_cells=64, tau=0.5, c_rep=1.0</code>. Code: <code>ttt_discover/methods/qd_archive.py</code>.</p>
</div>

<h2>Why it addresses the diagnosis</h2>
<ul>
  <li><strong>W1 (commitment)</strong>: by construction — selection is per-cell, not per-lineage. The system can't depth-front one root.</li>
  <li><strong>W3 (local-only)</strong>: cell-novelty rewards picks in cells the tracker hasn't observed recently → explicit cross-region pressure.</li>
  <li><strong>H3 (Q dominates)</strong>: <code>tau</code> and <code>c_rep</code> let us tune the trade-off explicitly; no structural decay.</li>
</ul>

<h2>Results (50 epochs)</h2>
<table>
  <thead><tr><th>Task</th><th>Best</th><th>vs every prior variant</th></tr></thead>
  <tbody>
    <tr class="winner"><td><span class="tag accent">erdos</span></td><td class="num">0.380966</td><td><strong>Beat prior leader</strong> mcts-c=3.0 (0.380983) by 0.000017; gap +0.000090 to 0.380876 frontier</td></tr>
    <tr><td><span class="tag accent">AC1</span></td><td class="num">1.510981</td><td>Worse than baseline (1.5086) and rep-novelty (1.5068)</td></tr>
    <tr><td><span class="tag accent">AC2</span></td><td class="num">0.930612</td><td>Worse than baseline (0.9358)</td></tr>
  </tbody>
</table>

<h2>Evidence</h2>
{fig("best_reward_erdos.png", "QD-archive (diamond marker, blue) sits at the top of the erdos leaderboard by 1×10⁻⁶ over mcts-c=3.0.")}
{fig("best_reward_ac1.png", "QD-archive (diamond marker, green) lands BELOW the baseline on AC1. The cell-based selection didn't generalize.")}
{fig("best_reward_ac2.png", "QD-archive (diamond marker, orange) underperforms baseline on AC2 too.")}

<h2>Interpretation</h2>
<div class="callout">
  <strong>QD wins erdos because erdos is the closest to its frontier already</strong> — and QD's behavior-cell coverage forces the search to <em>find</em> a slightly-different lineage rather than refine the same one. On erdos that lands on a marginally better solution. AC1's win comes from rep-novelty's smarter signal in a higher-headroom regime; QD's per-cell elite doesn't add anything beyond that. AC2 has the unlearning pathology — neither method helps.
</div>
"""

CONTENT[("methods", "hybrid-puctc3")] = """
<div class="subtitle">QD-archive but with <code>PUCT_C=3.0</code> during the warmup phase, so the seed pool is more diverse before the CVT fit. <strong>Built; pending compute.</strong></div>

<h2>Hypothesis</h2>
<p>QD-archive's quality depends on the CVT centroids, which depend on the 80 warmup descriptors. If warmup is just PUCT with default <code>c=1.0</code>, the seeds cluster around whatever PUCT happens to find first — possibly missing rep-space modes. Cranking <code>c=3.0</code> during warmup biases PUCT toward more diverse exploration, which propagates into more diverse centroids → broader cell coverage → better global search.</p>

<h2>Implementation</h2>
<div class="card">
  <p>No code change required — just an env var:</p>
  <pre>export PUCT_C=3.0
export QD_ENABLE=1   # everything else as in qd_erdos.sbatch</pre>
  <p>Sbatch: <code>scripts/methods/qd_archive/qd_erdos_puctc3.sbatch</code>. Standalone job <code>1653761</code>.</p>
</div>

<h2>Status</h2>
<div class="callout warn">
  <strong>Pending compute.</strong> Submitted multiple times; cluster failed each attempt before reaching first batch. No data yet. Will rerun once Phase A finishes.
</div>

<h2>What we'd measure</h2>
<ul>
  <li>Does the CVT cover broader rep-space at fit time? Compare initial-cell-coverage between QD baseline and QD-puctc3.</li>
  <li>Does the broader CVT translate to better discovery? Best C₅ on erdos.</li>
  <li>Does it help AC1 / AC2 by giving the cell archive a better seed pool?</li>
</ul>
"""

CONTENT[("methods", "hybrid-visit")] = """
<div class="subtitle">QD-archive's cell selection currently uses <code>z(quality)/tau + c_rep · z(cell_novelty)</code>. Add a PUCT-style visit-count term so cells with fewer expansions get a boost — combines QD's behavior-cell exploitation with MCTS's visit-count exploration.</div>

<h2>Mechanism</h2>
<div class="card">
<pre>logit(c) = z(quality(c)) / tau
         + c_rep   · z(cell_novelty(c))
         + c_visit · z( √(1+T) / (1+n_select[c]) )    # ← new term</pre>
<p>The archive already tracks <code>n_select[cell]</code> (number of times each cell has been chosen as a parent). The visit term boosts under-visited cells: <strong>3×</strong> for never-visited cells vs once-visited cells (verified by smoke test).</p>
<p>Code: <code>qd_archive.py::_visit_term</code>. Threaded through sampler/config/run_baseline via <code>QD_C_VISIT</code> env var. Default 0.0 preserves prior QD behavior.</p>
</div>

<h2>Implementation diff</h2>
<div class="card">
<pre>def _visit_term(self, cells: list[int]) -> np.ndarray:
    \"\"\"PUCT-style visit bonus over cells:
       sqrt(1 + sum_visits) / (1 + n_select[cell])\"\"\"
    total = sum(self.n_select.values())
    sqrtT = np.sqrt(1.0 + total)
    n_arr = np.array([self.n_select.get(c, 0) for c in cells], dtype=np.float64)
    return sqrtT / (1.0 + n_arr)

# inside sample_parent():
logits = _robust_z(q) / tau + self.c_rep * _robust_z(nov)
if self.c_visit != 0.0:
    logits += self.c_visit * _robust_z(self._visit_term(cells))</pre>
</div>

<h2>Status</h2>
<div class="callout warn">
  <strong>Pending compute.</strong> Submitted as job <code>1654430</code>. Cluster failed each launch attempt. No data yet.
</div>

<h2>What we'd measure</h2>
<ul>
  <li>How does cell-visit distribution differ between QD baseline (visit term off) and visit-hybrid?</li>
  <li>Does pushing into under-visited cells find new modes? Best C₅ on erdos, autocorr on AC1/AC2.</li>
  <li>Sweep <code>c_visit ∈ {0.5, 1.0, 2.0}</code> to find the balance against quality and rep-novelty.</li>
</ul>
"""

CONTENT[("methods", "dual-diversity")] = """
<div class="subtitle">Shared-signal dual diversity — one rep-novelty signal computed once, consumed in BOTH selection (existing PUCT bonus) AND update (new α·z(nov) advantage adjustment, outside the entropic tilt). Six experiments arranged as a gated ladder; cheap probes go first so a failure can kill the project before the expensive 20-job 2×2 burns compute.</div>

<h2>The method</h2>
<div class="card">
<p>Two consumers of the same novelty signal:</p>
<pre>SELECTION (existing rep-novelty PUCT bonus, unchanged):
  score(i) = Q(i) + puct_c·scale·P(i)·√(1+T)/(1+n[i])
           + puct_c_rep · scale · z(novelty(i))

UPDATE (new — outside the entropic tilt):
  A_final = A_entropic(R)  +  α(t) · z(novelty)</pre>
<p><strong>Why outside the exp.</strong> Adding novelty as <code>R+α·nov</code> inside the entropic estimator would be damped by the adaptive-β KL budget exactly where novelty creates spread. Adding to the <em>final</em> advantage lets the entropic estimator do its thing on reward, then nudges the gradient toward novel states on top.</p>
<p><strong>Reward-gated.</strong> Invalid rollouts (<code>correctness ≤ 0</code>) get 0 novelty advantage. All-bad groups skip the term entirely (no novelty credit when there's no valid signal to compare against).</p>
<p><strong>α annealed.</strong> Linear from <code>α_init</code> at step 0 to <code>α_final</code> at <code>anneal_to_step</code> (clamped after). "Explore early, commit late" — un-annealed novelty risks degenerating into rep-novel-but-invalid rollouts (RepExp's high-temperature failure mode).</p>
<p>Code: <code>ttt_discover/methods/update_novelty.py</code>. Plumbed via <code>UPDATE_NOVELTY_{ALPHA, FINAL, ANNEAL_TO, SHARED_A}</code>.</p>
</div>

<h2>Ladder structure (gates)</h2>
<pre>E0 (batch gate, AC1, drift)  ──fail──→  stop / pivot to E2
  │ pass
E1 (parent-sensitivity)      ──insensitive──→  update-side is load-bearing
  │                          └──sensitive────→  fix reuse first; dual may be overkill
E2 (descriptor validity)     ──disagree──────→  new descriptor becomes headline
  │ both pass
E3 (2×2 interaction test)    ──no interaction→  simplify
  │ interaction present
E4 (shared vs separate A)
  │
E5 (α-anneal / validity stress)</pre>

<h2>Held-fixed design choices</h2>
<ul>
  <li><strong>Drift, not reward, as the primary DV at 512 rollouts</strong> — reward is low-power at full batch (Phase A's seed 0 already hit 0.380965 with no method).</li>
  <li><strong>AC1, not erdos, as the testbed</strong> — erdos can't discriminate methods once the batch closes its headroom.</li>
  <li><strong>AC2 excluded</strong> — it's an objective-side regression (W4 in the analysis), not a selection/update problem.</li>
</ul>

<h2>The 6 experiments</h2>
<ul class="findings">
  <li><span class="h-label">E0</span><a href="e0-batch-gate.html">Batch-confound gate</a> — does selection-only rep-novelty still help at 512 rollouts/step?</li>
  <li><span class="h-label">E1</span><a href="e1-parent-sensitivity.html">Parent-sensitivity probe</a> — are rollouts actually sensitive to parent choice? (no training)</li>
  <li><span class="h-label">E2</span><a href="e2-descriptor-validity.html">Descriptor validity</a> — does our 64-d rep distinguish structurally different objects? (no training)</li>
  <li><span class="h-label">E3</span><a href="e3-2x2.html">Selection × update 2×2</a> — the headline test: is "both" > "either alone"?</li>
  <li><span class="h-label">E4</span><a href="e4-shared-vs-sep.html">Shared vs separate A</a> — does sharing the LinUCB tracker between selection + update matter?</li>
  <li><span class="h-label">E5</span><a href="e5-alpha-sweep.html">α-schedule stress test</a> — constant-high vs anneal-early vs anneal-long.</li>
</ul>

<h2>Status</h2>
<div class="callout warn">
  <strong>30 jobs queued on qos=high.</strong> All pending behind the user's <code>ztl</code> Llama training (16-GPU cap). Each is 3 GPUs × 3 days. Will dispatch as <code>ztl</code> array tasks throttle through. E0 first (cheapest gate), E3 once code-path is validated, E4/E5 if E3 vindicates the bet.
</div>
"""

CONTENT[("methods", "e0-batch-gate")] = """
<div class="subtitle">The gate experiment. The original rep-novelty result (Method 1) was measured at 64 rollouts/step, where the bare baseline was weak. Phase A is showing that at 512 rollouts/step the baseline already matches the prior method-best. E0 asks: does selection-only rep-novelty still beat the baseline at 512 rollouts, or did "method" just measure "weak baseline"?</div>

<h2>Design</h2>
<table>
  <thead><tr><th>Arm</th><th>Selection-side</th><th>Update-side</th><th>Source</th></tr></thead>
  <tbody>
    <tr><td>baseline</td><td>off</td><td>off</td><td>Reuse Phase A <code>ac1-phaseA-baseline-seed{0..4}</code></td></tr>
    <tr><td>repnov-sel</td><td><strong>on</strong> (<code>puct_c_rep=1.0</code>)</td><td>off</td><td>E0 array, 5 seeds</td></tr>
  </tbody>
</table>
<p><strong>Task:</strong> AC1 · <strong>Batch:</strong> 512 rollouts/step (group_size=16 × groups_per_batch=32) · <strong>Epochs:</strong> 50 · <strong>Seeds:</strong> 0–4</p>

<h2>Primary DV</h2>
<p><strong>Global representation drift</strong>, not best reward. At 512 rollouts/step reward is low-power (the baseline already at ceiling), so we measure whether selection-side novelty actually moves the rep centroid more than baseline. Compare the slope of "centroid drift from step 0" across the two arms; difference at step 50 with 5-seed CI.</p>

<h2>Predictions</h2>
<ul>
  <li><strong>E0 PASSES</strong> if drift slope in repnov-sel exceeds baseline by &gt; the seed-to-seed spread — selection-side signal still has work to do at 512 rollouts.</li>
  <li><strong>E0 FAILS</strong> if no significant difference — the original "rep-novelty wins AC1" was a batch-size confound. Ladder stops; pivot to E2 (descriptor validity) and reconsider the framing.</li>
</ul>

<h2>Status</h2>
<div class="callout warn">
  <strong>Queued.</strong> Slurm array <code>1762424_[0-4]</code>, qos=high, 3 GPUs each. Pending behind <code>ztl</code> Llama training.
</div>

<h2>Why this is the cheapest gate</h2>
<p>Five jobs. Reuses the existing rep-novelty code path with no modifications. Compared against five jobs already running (Phase A baseline). If it fails, we've spent ~3 GPU-days to kill 30+ GPU-days of E3/E4/E5 that would have been wasted.</p>
"""

CONTENT[("methods", "e1-parent-sensitivity")] = """
<div class="subtitle">No-training probe. Are rollouts actually sensitive to which parent they're started from, or do they collapse to similar outputs regardless of parent? If parent insensitive, the update-side novelty signal is load-bearing; if sensitive, selection-side already does the work and dual diversity may be overkill.</div>

<h2>Method</h2>
<div class="card">
<p>For each training step, group rollouts by <code>parent_id</code> and compute the variance decomposition of frozen-rep descriptors:</p>
<pre>σ²_within  = within-parent variance of descriptors
σ²_across  = between-parent variance of descriptors
ratio      = σ²_across / σ²_within</pre>
<ul>
  <li><strong>ratio ≫ 1</strong> → parent strongly predicts rollout content (SENSITIVE)</li>
  <li><strong>ratio ≈ 1</strong> → parent doesn't matter much (INSENSITIVE — update-side needed)</li>
  <li><strong>ratio &lt; 1</strong> → noise dominates parent (INSENSITIVE, more so)</li>
</ul>
<p>Script: <code>scripts/analysis/e1_parent_sensitivity.py</code>. Runs on any completed rollouts.jsonl with embedded <code>parent_id</code> + <code>frozen_rep</code>. Output: per-step ratio + an aggregate verdict.</p>
</div>

<h2>Usage</h2>
<pre>python scripts/analysis/e1_parent_sensitivity.py \\
    /workspace-vast/$USER/exp/ttt-discover/runs/tinker_log/ac1-phaseA-baseline-seed0 \\
    --out e1_phaseA_seed0.json</pre>

<h2>Verdict thresholds (preregistered)</h2>
<table>
  <thead><tr><th>median ratio</th><th>verdict</th><th>implication</th></tr></thead>
  <tbody>
    <tr><td class="num">&gt; 2.0</td><td>SENSITIVE</td><td>Selection-side novelty is the leverage; dual diversity is overkill</td></tr>
    <tr><td class="num">0.5–2.0</td><td>AMBIGUOUS</td><td>Worth running E3 to test; both consumers may each contribute</td></tr>
    <tr><td class="num">&lt; 0.5</td><td>INSENSITIVE</td><td>Update-side advantage adjustment is load-bearing; dual diversity justified</td></tr>
  </tbody>
</table>

<h2>Status</h2>
<div class="callout">
  <strong>No GPU jobs.</strong> Code ready; runs on any completed run dir. Will be executed against Phase A AC1 baselines once those produce enough <code>rollouts.jsonl</code> with descriptors attached.
</div>
"""

CONTENT[("methods", "e2-descriptor-validity")] = """
<div class="subtitle">No-training probe. Does our 64-d descriptor (Qwen3-8B base → mean-pool → sparse random projection) actually distinguish structurally different output objects, or are two very different combinatorial constructions mapped to nearby points? If invalid, both selection and update novelty are chasing text-pattern noise and the dual-diversity bet is misplaced.</div>

<h2>Method</h2>
<div class="card">
<p>For each pair of rollouts in the same step:</p>
<ol>
  <li><code>rep_distance(A, B)</code> = ‖rep_A − rep_B‖ in the 64-d projected space</li>
  <li><code>obj_distance(A, B)</code> = task-specific structural distance between the parsed output objects:
    <ul>
      <li><strong>AC1/AC2:</strong> mean |a − b| over the parsed (a, b) sequence</li>
      <li><strong>erdos:</strong> Jaccard distance on edge sets</li>
    </ul>
  </li>
  <li>Spearman ρ between the two distance arrays, across all pairs in all steps</li>
</ol>
<p>Script: <code>scripts/analysis/e2_descriptor_validity.py</code>.</p>
</div>

<h2>Usage</h2>
<pre>python scripts/analysis/e2_descriptor_validity.py \\
    /workspace-vast/$USER/exp/ttt-discover/runs/tinker_log/ac1-phaseA-baseline-seed0 \\
    --task ac1 --out e2_phaseA_seed0.json</pre>

<h2>Verdict thresholds (preregistered)</h2>
<table>
  <thead><tr><th>Spearman ρ</th><th>verdict</th><th>implication</th></tr></thead>
  <tbody>
    <tr><td class="num">&gt; 0.4</td><td>DESCRIPTOR VALID</td><td>Tracks object structure. Dual-diversity bet rests on real signal.</td></tr>
    <tr><td class="num">0.15–0.4</td><td>DESCRIPTOR WEAK</td><td>Worth comparing to a content-aware descriptor (parsed-object hashing).</td></tr>
    <tr><td class="num">&lt; 0.15</td><td>DESCRIPTOR INVALID</td><td>Chasing text-pattern noise. Need a different descriptor before E3/E4/E5.</td></tr>
  </tbody>
</table>

<h2>Why this matters even if E0 passes</h2>
<p>E0 only tells us "selection-side novelty correlates with drift". It doesn't tell us "the descriptor measures the right thing." A descriptor that captures formatting/length patterns can drive drift in rep space without driving any change in the actual combinatorial object the task cares about. E2 grounds the rep-novelty signal in object-level meaning.</p>

<h2>Status</h2>
<div class="callout">
  <strong>No GPU jobs.</strong> Code ready; runs on any completed run dir. Independent of E0/E1.
</div>
"""

CONTENT[("methods", "e3-2x2")] = """
<div class="subtitle">The headline test. Selection-novelty × update-novelty 2×2 on AC1, 5 seeds per cell. Two new cells (the other two are reused from Phase A and E0). Tests whether the two consumers of the rep-novelty signal interact — if "both" is better than the sum of "either alone", dual diversity is real.</div>

<h2>Design</h2>
<table>
  <thead><tr><th>Cell</th><th>Selection-side<br/><span class="mono">PUCT_C_REP</span></th><th>Update-side<br/><span class="mono">UPDATE_NOVELTY_ALPHA</span></th><th>n seeds</th><th>Source</th></tr></thead>
  <tbody>
    <tr><td>baseline</td><td class="num">0</td><td class="num">0</td><td class="num">5</td><td>Reuse Phase A baselines</td></tr>
    <tr><td>selection-only</td><td class="num">1.0</td><td class="num">0</td><td class="num">5</td><td>Reuse E0</td></tr>
    <tr><td>update-only</td><td class="num">0</td><td class="num">0.3→0.05@30</td><td class="num">5</td><td><strong>E3 cells 0–4, NEW</strong></td></tr>
    <tr><td>both (shared A)</td><td class="num">1.0</td><td class="num">0.3→0.05@30</td><td class="num">5</td><td><strong>E3 cells 5–9, NEW</strong></td></tr>
  </tbody>
</table>
<p><strong>Task:</strong> AC1 · <strong>Batch:</strong> 512 rollouts/step · <strong>Epochs:</strong> 50 · <strong>α schedule:</strong> linear anneal from 0.3 at step 0 to 0.05 at step 30, constant after</p>

<h2>Why we don't run all 4 cells from scratch</h2>
<p>Cells 0 and 1 are already covered:</p>
<ul>
  <li>Cell 0 (baseline) = Phase A's <code>ac1-phaseA-baseline-seed{0..4}</code></li>
  <li>Cell 1 (selection-only) = E0's <code>ac1-E0-repnov-seed{0..4}</code></li>
</ul>
<p>Running them again would duplicate 10 GPU-days. The E3 sbatch only runs cells 2 and 3 (the new ones, 10 jobs total).</p>

<h2>Primary DV: interaction term</h2>
<p>Two complementary readouts:</p>
<ol>
  <li><strong>Drift slope at step 50</strong> (5-seed mean ± SE). Compute the interaction:<br/>
    <code>Δ_interact = (both − baseline) − (selonly − baseline) − (updonly − baseline)</code><br/>
    If <code>Δ_interact &gt; 0</code> with CI excluding zero → the two signals reinforce each other.</li>
  <li><strong>Best-reward at step 50.</strong> Same interaction test, but on the (lower-power) reward metric for sanity-check.</li>
</ol>

<h2>Predictions</h2>
<ul>
  <li><strong>Strong interaction</strong> (both ≫ selonly + updonly) → ship dual diversity.</li>
  <li><strong>Additive only</strong> (both ≈ selonly + updonly) → dual works but redundant; pick one based on cost.</li>
  <li><strong>Antagonistic</strong> (both &lt; max(selonly, updonly)) → the signals conflict; need to investigate sharing mechanism (E4) before publishing anything.</li>
</ul>

<h2>Status</h2>
<div class="callout warn">
  <strong>Queued.</strong> Slurm array <code>1762454_[0-9]</code>, qos=high, 3 GPUs each. Pending behind <code>ztl</code>. This is the expensive arm of the ladder — 10 jobs × ~3 days each = ~30 GPU-days.
</div>
"""

CONTENT[("methods", "e4-shared-vs-sep")] = """
<div class="subtitle">Refinement on E3's "both" cell. Does it matter whether selection and update use the SAME elliptical covariance <code>A</code> matrix (one tracker, two consumers) or maintain SEPARATE accumulators? The shared-signal framing predicts shared is better; the separate framing predicts they should be free to optimize independently.</div>

<h2>Design</h2>
<table>
  <thead><tr><th>Arm</th><th>Tracker</th><th>n seeds</th></tr></thead>
  <tbody>
    <tr><td>shared A</td><td>Update-side reuses the sampler's <code>RepNoveltyTracker.A</code>. One observation stream.</td><td class="num">3</td></tr>
    <tr><td>separate A</td><td>Update-side maintains its own <code>UpdateNoveltyTracker</code>. Two independent observation streams.</td><td class="num">3</td></tr>
  </tbody>
</table>
<p><strong>Both arms:</strong> AC1 · 512 rollouts/step · 50 epochs · <code>PUCT_C_REP=1.0, UPDATE_NOVELTY_ALPHA=0.3→0.05@30</code>. Flag: <code>UPDATE_NOVELTY_SHARED_A ∈ {0, 1}</code>.</p>

<h2>Hypothesis</h2>
<p><strong>Shared should win</strong> if the signal is genuinely "this region of rep space is under-explored" — both selection (which parent to expand) and update (which rollout to credit) should be looking at the same evidence about regions. Two trackers means each one independently observes a subset of the rollouts, halving the effective sample size for any given direction.</p>

<p><strong>Separate should win</strong> if there's a non-stationary mismatch — e.g. if selection naturally drifts faster than update should respond to, separate buffers can decouple. Unlikely a priori but worth ruling out.</p>

<h2>Primary DV</h2>
<p>Same drift-slope + interaction-test as E3. Plus a diagnostic: track the <strong>cosine similarity between the two A-matrices' top eigenvectors</strong> over training. If they're nearly identical even in the "separate" arm, the experiment is degenerate — the two trackers are observing the same distribution, just with smaller sample size. That itself would be a finding.</p>

<h2>Status</h2>
<div class="callout warn">
  <strong>Queued.</strong> Slurm array <code>1762455_[0-5]</code>, qos=high, 3 GPUs each. Pending behind <code>ztl</code>. Only ~18 GPU-days; cheaper than E3 because we only need a small-N test of an architectural choice (the effect either exists or it doesn't).
</div>

<h2>Dependency on E3</h2>
<p>If E3 says "both no better than either alone", E4 is moot. Will check E3 status before reading E4 results.</p>
"""

CONTENT[("methods", "e5-alpha-sweep")] = """
<div class="subtitle">Stress test on the α annealing schedule for the update-side novelty term. Tests whether α persistence triggers the RepExp degenerate "novel-but-invalid" failure mode (chase novelty so hard the policy stops being correct).</div>

<h2>Design</h2>
<table>
  <thead><tr><th>Schedule</th><th>α at step 0</th><th>α at step T</th><th>Anneal-to-step</th><th>n seeds</th></tr></thead>
  <tbody>
    <tr><td>constant high</td><td class="num">0.3</td><td class="num">0.3</td><td class="num">0 (no anneal)</td><td class="num">3</td></tr>
    <tr><td>anneal early</td><td class="num">0.3</td><td class="num">0.0</td><td class="num">20</td><td class="num">3</td></tr>
    <tr><td>anneal long</td><td class="num">0.5</td><td class="num">0.05</td><td class="num">40</td><td class="num">3</td></tr>
  </tbody>
</table>
<p>All arms: AC1 · 512 rollouts/step · 50 epochs · <code>PUCT_C_REP=1.0, UPDATE_NOVELTY_SHARED_A=1</code>.</p>

<h2>Hypotheses</h2>
<ul>
  <li><strong>Constant high</strong> should show late-training degeneracy: the policy keeps being pushed toward novel directions long after the reward signal stops finding anything useful. Look for <code>frac_valid</code> (rollouts with correctness &gt; 0) decreasing late in training as the policy invents novel-but-broken outputs.</li>
  <li><strong>Anneal early</strong> is the safe bet — give the policy a sharp exploration kick early, then let it commit. Should match selection-only by step 30 since α=0 by then.</li>
  <li><strong>Anneal long</strong> is the ambitious bet — bigger early kick (α=0.5) but gradually taper. Tests whether more aggressive exploration upfront pays off if you anneal back down.</li>
</ul>

<h2>Primary DV</h2>
<ol>
  <li><strong>frac_valid trajectory</strong> — does any arm see correctness collapse? (signature of degenerate novelty chasing)</li>
  <li><strong>Final best reward</strong> — does any arm meaningfully beat selection-only?</li>
  <li><strong>Drift trajectory</strong> — do the three schedules produce qualitatively different drift curves, or do they converge?</li>
</ol>

<h2>Status</h2>
<div class="callout warn">
  <strong>Queued.</strong> Slurm array <code>1762456_[0-8]</code>, qos=high, 3 GPUs each. Pending behind <code>ztl</code>. ~27 GPU-days.
</div>

<h2>What we'd learn</h2>
<p>If <strong>constant-high crashes</strong> but anneal-early matches selection-only → the schedule is the load-bearing detail, not α magnitude. Publish anneal-early as the recipe.</p>
<p>If <strong>anneal-long beats anneal-early</strong> → upfront exploration pays off; recommend a stronger initial α.</p>
<p>If <strong>all three give the same result</strong> → α magnitude doesn't matter much in this regime; the term is either subtractively-small or saturating somewhere.</p>
"""

CONTENT[("methods", "leaderboards")] = f"""
<div class="subtitle">Full 6-digit results on all 3 tasks, across every variant tested.</div>

<h2>ERDOS — minimize C₅ overlap (frontier 0.380876)</h2>
<table>
  <thead><tr><th>Variant</th><th>Epochs · rollouts/step</th><th class="mono">C₅ bound</th><th class="mono">Gap</th></tr></thead>
  <tbody>
    <tr class="winner"><td>phaseA baseline seed=0 (preliminary)</td><td>50 ep · 512</td><td class="num">0.380965</td><td class="num">+0.000089</td></tr>
    <tr><td>qd-archive</td><td>50 ep · 64</td><td class="num">0.380966</td><td class="num">+0.000090</td></tr>
    <tr><td>mcts-puct_c=3.0</td><td>30 ep · 64</td><td class="num">0.380983</td><td class="num">+0.000107</td></tr>
    <tr><td>loose-prune</td><td>30 ep · 64</td><td class="num">0.381044</td><td class="num">+0.000168</td></tr>
    <tr><td>rep-novelty</td><td>30 ep · 64</td><td class="num">0.381272</td><td class="num">+0.000396</td></tr>
    <tr><td>mcts-puct_c=0.3</td><td>30 ep · 64</td><td class="num">0.381355</td><td class="num">+0.000479</td></tr>
    <tr><td>baseline</td><td>30 ep · 64</td><td class="num">0.381584</td><td class="num">+0.000708</td></tr>
  </tbody>
</table>
{fig("best_reward_erdos.png", "Per-step best C₅ across all erdos variants. Lower is better.")}

<h2>AC1 — minimize sup‖autocorrelation‖ (frontier 1.503)</h2>
<table>
  <thead><tr><th>Variant</th><th>Epochs · rollouts/step</th><th class="mono">Best</th></tr></thead>
  <tbody>
    <tr class="winner"><td>rep-novelty</td><td>24/30 (timeout) · 64</td><td class="num">1.506845</td></tr>
    <tr><td>ac1-loose-prune-50</td><td>50 · 64</td><td class="num">1.507113</td></tr>
    <tr><td>ac1-baseline-50 (partial)</td><td>step 22/50 · 64</td><td class="num">1.507085</td></tr>
    <tr><td>lineage-blocking-off</td><td>30 · 64</td><td class="num">1.507528</td></tr>
    <tr><td>baseline-1</td><td>30 · 64</td><td class="num">1.508628</td></tr>
    <tr><td>qd-archive</td><td>50 · 64</td><td class="num">1.510981</td></tr>
    <tr><td>ac1-mcts-c=3.0-50</td><td>50 · 64</td><td class="num">1.515995</td></tr>
  </tbody>
</table>
{fig("best_reward_ac1.png", "Per-step best autocorr bound across all AC1 variants. Lower is better.")}

<h2>AC2 — maximize lower bound (frontier 0.97)</h2>
<table>
  <thead><tr><th>Variant</th><th>Epochs · rollouts/step</th><th class="mono">Best</th></tr></thead>
  <tbody>
    <tr class="winner"><td>baseline-1</td><td>30 · 64</td><td class="num">0.935814</td></tr>
    <tr><td>qd-archive</td><td>50 · 64</td><td class="num">0.930612</td></tr>
  </tbody>
</table>
{fig("best_reward_ac2.png", "AC2 — neither method helped. Baseline still saturated 0.034 below frontier.")}

<h2>Headline take</h2>
<div class="callout">
  <strong>No method broke the published 0.380876 frontier on erdos.</strong> Closest was qd-archive at 0.380966 (+0.000090). The Phase A baseline at full batch is at 0.380965 — essentially the same, with no method enabled.
</div>
<div class="callout warn">
  <strong>The interpretation hinges on the noise floor.</strong> Until Phase A's 5 erdos seeds finish and we have a std on the seed-to-seed variance, "qd beat mcts by 0.000017" or "phaseA baseline beat qd by 0.000001" are both inside the plausible noise.
</div>
"""

# ---------------------------------------------------------------------------
# Generate
# ---------------------------------------------------------------------------

def main():
    for section, pages in [("analysis", ANALYSIS_PAGES), ("methods", METHOD_PAGES)]:
        for i, (slug, title, badge, kind) in enumerate(pages):
            content = CONTENT.get((section, slug))
            if content is None:
                print(f"  SKIP {section}/{slug} — no content")
                continue
            prev_link = None
            next_link = None
            if i > 0:
                ps, pt, _, _ = pages[i - 1]
                if ps == "index":
                    p_short = f"{section.title()} overview"
                elif " — " in pt:
                    p_short = pt
                else:
                    p_short = pt
                prev_link = (ps, p_short)
            if i < len(pages) - 1:
                ns, nt, _, _ = pages[i + 1]
                if ns == "index":
                    n_short = f"{section.title()} overview"
                elif " — " in nt:
                    n_short = nt
                else:
                    n_short = nt
                next_link = (ns, n_short)
            html = render_page(section, slug, title, badge, kind, content,
                               prev_link=prev_link, next_link=next_link)
            out = ROOT / section / f"{slug}.html"
            out.write_text(html)
            print(f"  wrote {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
