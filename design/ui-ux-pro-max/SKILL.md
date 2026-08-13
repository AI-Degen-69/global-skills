---
name: ui-ux-pro-max
description: Use when designing, building, reviewing
version: "2.6.2"
author: NextLevelBuilder
license: MIT
homepage: https://uupm.cc
repository: https://github.com/nextlevelbuilder/ui-ux-pro-max-skill
keywords:
  - ui
  - ux
  - design
  - design-system
  - color-palette
  - typography
  - accessibility
  - charts
  - components
category: design
---

# UI/UX Pro Max

Professional UI/UX design intelligence for AI coding assistants. Bundled with a
searchable local database (CSV) and a stdlib-only Python BM25 search engine —
**no third-party packages, no network calls**.

Use this skill for any UI/UX task: build a landing page, dashboard, or mobile
app screen; create/refactor a component; choose a style, color scheme, or font
pairing; review existing UI for UX/a11y/visual-consistency issues; implement
dark mode, charts, navigation, or responsive behavior; or make design-system /
reusable-component decisions.

## When to use

- New project / page / screen → generate a design system first (Step 2)
- New or refactored component → domain searches for style + UX (Step 3)
- Choosing style / color / font → design system (Step 2)
- Reviewing existing UI → run UX validation pass (Step 3, `--domain ux`)
- Fixing a UI bug, adding dark mode, charts, stack best practices → domain/stack search (Step 3–4)

**Skip** for pure backend logic, API/database design, non-visual infra/DevOps,
or non-visual automation.

## Prerequisites

The bundled scripts require **Python 3** (standard library only). Verify:

```bash
python3 --version || python --version
```

On **Windows** use `python` instead of `python3`. If Python is missing, **do not
install it yourself** — stop and ask the user to install it, then continue. If
they decline, skip the CLI searches and rely on the Quick Reference rules in
`references/quick-reference.md`.

The search scripts force UTF-8 stdout/stderr, so emojis render correctly on
Windows (cp1252) terminals.

## How to use

All commands run from the skill's `scripts/` directory. Use absolute or
relative paths to `search.py` as appropriate. The canonical location is
`skills/design/ui-ux-pro-max/scripts/search.py` (relative to the Hermes
`skills/` root).

### Step 1 — Analyze the request

Extract: product type (SaaS, e-commerce, portfolio, healthcare, fintech, etc.),
target audience, style keywords (minimal, dark mode, vibrant…), and stack.

### Step 2 — Generate a design system (REQUIRED for new work)

Always start with `--design-system` for full reasoning-based recommendations:

```bash
python3 <skill>/scripts/search.py "<product_type> <industry> <keywords>" --design-system [-p "Project Name"]
```

This searches product/style/color/landing/typography in parallel, applies
reasoning rules from `data/ui-reasoning.csv`, and returns pattern + style +
colors + typography + effects + anti-patterns.

**Persist for cross-session retrieval** (Master + Overrides pattern):

```bash
python3 <skill>/scripts/search.py "<query>" --design-system --persist -p "Project Name"
python3 <skill>/scripts/search.py "<query>" --design-system --persist -p "Project Name" --page "dashboard"
```

Creates `design-system/MASTER.md` (global source of truth) and
`design-system/pages/<page>.md` (overrides). When building a page, check the
page file first; if present its rules override MASTER, else use MASTER.

**Optional design dials (1–10), only with `--design-system`:**

```bash
python3 <skill>/scripts/search.py "<query>" --design-system --variance 8 --motion 7 --density 8
```

- `--variance`: 1=centered/minimal → 10=bold/asymmetric
- `--motion`: 1=subtle → 10=complex (attaches a GSAP snippet from `data/motion.csv`)
- `--density`: 1=spacious → 10=dense/dashboard (overrides spacing-scale tokens)

Output formats: `--format ascii` (default, terminal) or `--format markdown`
(documentation).

### Step 3 — Supplement with detailed domain searches

```bash
python3 <skill>/scripts/search.py "<keyword>" --domain <domain> [-n <max_results>]
```

| Need | Domain | Example |
|------|--------|---------|
| Product-type patterns | `product` | `--domain product "entertainment social"` |
| Style options / CSS | `style` | `--domain style "glassmorphism dark"` |
| Font pairings | `typography` | `--domain typography "playful modern"` |
| Color palettes | `color` | `--domain color "entertainment vibrant"` |
| Chart types | `chart` | `--domain chart "real-time dashboard"` |
| UX best practices | `ux` | `--domain ux "animation accessibility"` |
| Landing structure | `landing` | `--domain landing "hero social-proof"` |
| React/Next perf | `react` | `--domain react "rerender memo list"` |
| App interface a11y | `web` | `--domain web "accessibilityLabel touch safe-areas"` |
| Icon suggestions | `icons` | `--domain icons "navigation arrows"` |
| Google Fonts lookup | `google-fonts` | `--domain google-fonts "variable sans serif"` |
| GSAP animation | `gsap` | `--domain gsap "scroll reveal stagger"` |

### Step 4 — Stack-specific guidelines

```bash
python3 <skill>/scripts/search.py "<keyword>" --stack <stack>
```

Available stacks: `react`, `nextjs`, `vue`, `svelte`, `astro`, `swiftui`,
`react-native`, `flutter`, `nuxtjs`, `nuxt-ui`, `html-tailwind`, `shadcn`,
`jetpack-compose`, `threejs`, `angular`, `laravel`, `javafx`, `wpf`, `winui`,
`avalonia`, `uno`, `uwp`.

**JavaFX examples:**

```bash
python3 <skill>/scripts/search.py "atlantafx primer enterprise theme" --stack javafx
python3 <skill>/scripts/search.py "enterprise tableview density permission" --stack javafx
```

### Step 5 — Implement, then validate

Synthesize design system + detailed searches and implement the UI. Before
delivery, run a final UX validation pass and review the Quick Reference CRITICAL
+ HIGH rules:

```bash
python3 <skill>/scripts/search.py "animation accessibility z-index loading" --domain ux
```

**Pre-delivery checklist (App UI):** no emoji icons (use SVG), consistent icon
family, 44×44pt+ touch targets, micro-interactions 150–300ms, disabled states
clear, focus order matches visual order, light + dark contrast both ≥4.5:1/3:1,
visible dividers + states in both themes, scrim 40–60% for modals, tested on
small/large phone + tablet (portrait + landscape), reduced-motion + dynamic type
supported, alt text + labels present, color never the only indicator.

## Reference files

- `references/quick-reference.md` — full prioritized rule catalog (10 categories,
  CRITICAL→LOW) with check/anti-pattern tables for accessibility, touch,
  performance, style, layout, typography, animation, forms, navigation, charts.
- `references/skill-content.md` — upstream skill body: detailed workflow, search
  reference, example end-to-end run, and the "Common Rules for Professional UI"
  tables (icons, interaction, light/dark contrast, layout & spacing).
- `data/` — canonical CSV databases (`styles.csv`, `colors.csv`,
  `typography.csv`, `products.csv`, `charts.csv`, `ux-guidelines.csv`,
  `ui-reasoning.csv`, `icons.csv`, `google-fonts.csv`, `motion.csv`,
  `landing.csv`, `app-interface.csv`, `react-performance.csv`, `stacks/`).
- `scripts/` — `search.py` (CLI entry), `core.py` (BM25+regex engine),
  `design_system.py` (design-system generation + persistence).

## Pitfalls

- **Don't run package managers / install Python for the user.** Ask instead.
- **Scripts are stdlib-only** — never `pip install` anything for this skill.
- **Windows:** use `python`, not `python3`, if `python3` is unavailable.
- **Paths:** `search.py` resolves `data/` relative to its own location, so run it
  from `scripts/` or pass the correct working directory — do not move the
  `data/` folder out from under `scripts/`.
- **Don't guess styles/colors** — always ` --design-system` first; the reasoning
  engine overrides intuition and avoids industry anti-patterns (e.g. "AI
  purple/pink gradients" for banking).
- **Emoji-as-icons is a hard anti-pattern** — use Phosphor/Heroicons/Lucide SVG.

## Verification

After install, confirm the engine works:

```bash
cd <skill>/scripts && python3 search.py "glassmorphism" --domain style -n 1
```

Expected: a `## UI Pro Max Search Results` block with one `Glassmorphism` row
containing CSS keywords and an implementation checklist. Any Python traceback
means the `data/` folder is misplaced or Python 3 is missing.
