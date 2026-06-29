# auto-discovery.github.io — agent guide

This repo is the public dashboard for the TTT-Discover analysis + methods study.
Live at <https://auto-discovery.github.io>. Source repo for the experiments is
`github.com/EdwardoSunny/rep-ttt` on branch `method-rep-novelty`.

**TL;DR for agents:** Don't hand-edit `.html` files. Edit `_build/gen.py`,
run it, commit, push. One Python registry drives every page.

---

## Layout

```
.
├── index.html              ← landing page (hand-written, edit cautiously)
├── style.css               ← global styling (dark/light themed)
├── analysis/               ← per-experiment pages, GENERATED
│   ├── index.html
│   ├── h1-monomorphism.html
│   └── ...
├── methods/                ← per-experiment pages, GENERATED
│   ├── index.html
│   ├── rep-novelty.html
│   ├── dual-diversity.html
│   ├── e0-batch-gate.html
│   └── ...
├── figures/                ← images referenced by content blocks
│   ├── cross_task/         ← cross-task overlay PNGs (the bulk)
│   └── ...
└── _build/
    └── gen.py              ← the generator. THIS IS WHERE YOU EDIT.
```

All pages under `analysis/` and `methods/` (except `style.css`, `figures/`,
`index.html`) are **regenerated from `_build/gen.py` every build**. Editing
them by hand will be wiped the next time `gen.py` runs.

---

## How `gen.py` is structured

Three pieces:

1. **Page registries** (`ANALYSIS_PAGES`, `METHOD_PAGES`) — ordered lists of
   `(slug, title, badge, kind)` tuples. Drive the sidebar order and the
   prev/next links between pages.

2. **`CONTENT` dict** — `CONTENT[(section, slug)] = "<body html>"`. One
   entry per page. The HTML goes between the page's `<h1>` (auto-rendered
   from `title`) and the prev/next nav bar (auto-rendered from the
   registry's neighbors).

3. **`render_page(...)`** — wraps your content with the global chrome:
   nav bar, sidebar, footer. You don't call this; `main()` does.

To add a new page, you touch the registry AND add a `CONTENT[(...)] = """..."""`
block. Forget either one and the build either skips the page (no content
entry) or omits it from the sidebar (no registry entry).

---

## Adding a new experiment page

Example: adding a Method 4 page `methods/m4-something.html`.

1. **Edit `_build/gen.py`**:

   ```python
   # 1) Add to METHOD_PAGES, in the order it should appear in the sidebar.
   #    The badge is the short tag shown next to the sidebar link
   #    (max ~6 chars or it wraps ugly).
   METHOD_PAGES = [
       ("index", "Methods — overview", "11 experiments", "OVERVIEW"),
       ...existing pages...
       ("m4-something", "Method 4 — something descriptive", "M4", "EXPERIMENT"),
       ("leaderboards", "Cross-task leaderboards", "Summary", "OVERVIEW"),
   ]

   # 2) Add a CONTENT block. Add it ABOVE the existing methods/leaderboards
   #    block so the file stays in registry order.
   CONTENT[("methods", "m4-something")] = """
   <div class="subtitle">One-sentence summary of what this method does and what we measured.</div>

   <h2>Mechanism</h2>
   <div class="card">
   <p>How it works, briefly.</p>
   <pre>config_var=value
   another_var=value</pre>
   </div>

   <h2>Results</h2>
   <table>
     <thead><tr><th>Task</th><th>Best</th><th>vs baseline</th></tr></thead>
     <tbody>
       <tr class="winner"><td>AC1</td><td class="num">1.506</td><td class="num">+0.002</td></tr>
     </tbody>
   </table>

   <h2>Status</h2>
   <div class="callout warn">
     <strong>Pending.</strong> Job <code>NNNNNNN</code> queued.
   </div>
   """
   ```

2. **Update `methods/index.html`'s "What's here" list** — same `CONTENT[("methods", "index")]`
   block — add a `<li>` so users can find the new page from the methods overview.

3. **Update the front-page `index.html`** *only if* this is a major new addition
   that deserves to be advertised on the landing page. Otherwise leave it alone.

4. **Rebuild + push:**

   ```bash
   cd /home/edwardosunny/auto-discovery-site/_build && python3 gen.py
   cd ..
   git add -A
   git commit -m "Add M4 — something descriptive"
   git push origin main
   ```

GitHub Pages picks up the push and rebuilds in ~30 seconds.

---

## Content patterns to reuse

The `gen.py` file has helper functions:

- `fig("filename.png", "caption")` — single figure (from `figures/cross_task/`)
- `figgrid([("a.png", "cap a"), ("b.png", "cap b")])` — two-column grid

CSS classes you'll use a lot (defined in `style.css`, don't redefine):

| Element | Purpose |
|---|---|
| `<div class="subtitle">` | One-line summary right under the H1 (gray) |
| `<div class="card">` | Block of related content with a border |
| `<div class="callout">` | Highlighted accent box |
| `<div class="callout warn">` / `bad` / `good` | Colored variants (yellow/red/green) |
| `<table>` with `<tr class="winner">` | Star-marked winning row |
| `<td class="num">` | Right-aligned monospace number cell |
| `<span class="tag accent">` / `good` / `warn` / `bad` | Inline pill labels |
| `<ul class="findings">` with `<li><span class="h-label">H1</span>...</li>` | Findings list with badge prefixes |
| `<pre><code>` | Code block (auto-styled) |

**Stylistic conventions** to match existing pages:

- **H2 sections only** — `<h2>` for major sections, `<h3>` rarely. The sidebar
  jumps between pages, not within a page.
- **One-sentence subtitle** under the H1, in `<div class="subtitle">`.
- **Numbers in `<td class="num">`** — keep 6 significant digits where it matters
  (e.g. erdos bounds), fewer otherwise.
- **Callouts at the end** — every page ends with a callout summarizing the
  takeaway. Use the right color: `good` for wins, `warn` for caveats/pending,
  `bad` for known failures, default (accent) for neutral findings.

---

## When experiment results land

Most pages start out marked "pending compute" or "queued". When the results
actually come in:

1. **Pull the numbers** from the run dirs at
   `/workspace-vast/$USER/exp/ttt-discover/runs/tinker_log/<experiment_name>/`.
   Per-step best reward usually goes in `best_seq*.json` or similar; ask the
   user where the canonical metric lives if unsure.
2. **Drop new plots into `figures/cross_task/`** — same naming convention as
   existing files. Update `_build/gen.py` to reference them via `fig(...)`.
3. **Replace the "Status" pending block** with a "Results" block (table +
   evidence figures + a closing callout with the verdict).
4. **Update the leaderboards page** (`CONTENT[("methods", "leaderboards")]`)
   if the new result changes the ranking.
5. **Update the front-page tagline** (`index.html`) only if a new method beat
   the current headline number on a task.

---

## Things NOT to do

- **Don't hand-edit `analysis/*.html` or `methods/*.html`.** They're regenerated.
  Your edits will be wiped.
- **Don't add JavaScript.** This is a static site; the value is that it renders
  fast and works offline. Keep it that way.
- **Don't add a CSS framework.** `style.css` is hand-written and
  ~400 lines. Match the existing palette (CSS variables at the top of `style.css`).
- **Don't break the registry order vs the prev/next nav.** The prev/next links
  on each page are computed from the registry order. If you append a page out
  of place, the navigation will jump around weirdly.
- **Don't claim results that don't exist yet.** If a job is queued/running/failed,
  say so explicitly with a `callout warn`. The dashboard's credibility comes
  from clearly distinguishing measured from speculated.
- **Don't delete experiment pages, even for failed/abandoned methods.** Mark
  them as such with `callout bad` and keep the page — the negative result is
  part of the story.

---

## Quick sanity check before pushing

```bash
cd /home/edwardosunny/auto-discovery-site/_build && python3 gen.py
# Should print "wrote ..." for every registry entry. If any line says
# "SKIP <name> — no content", you added it to the registry but forgot
# the CONTENT block.

cd ..
git status  # look at the diff — only generated HTML + your gen.py edit
git diff _build/gen.py  # double-check your edit before committing
```

To preview locally before pushing:

```bash
cd /home/edwardosunny/auto-discovery-site
python3 -m http.server 8000
# open http://localhost:8000
```

---

## Remote

```
git remote -v
# origin  git@github.com:auto-discovery/auto-discovery.github.io.git (fetch)
# origin  git@github.com:auto-discovery/auto-discovery.github.io.git (push)
```

Live URL: `https://auto-discovery.github.io/`. Push to `main` → live in ~30s.
