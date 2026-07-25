---
name: frontend-design
description: Build web interfaces with genuine design quality, not AI slop. Use for any frontend work - landing pages, web apps, dashboards, admin panels, components, interactive experiences. Activates for both greenfield builds and modifications to existing applications. Detects existing design systems and respects them. Covers composition, typography, color, motion, and copy. Verifies results via screenshots before declaring done.
---

# Frontend Design Skill — Comprehensive Summary

> **Source:** `https://raw.githubusercontent.com/anthropics/skills/main/skills/frontend-design/SKILL.md`
> **License:** Complete terms in LICENSE.txt

---

## Core Philosophy

> **Approach this as the design lead at a small studio known for giving every client a visual identity that could not be mistaken for anyone else's.** This client has already rejected proposals that felt templated, and is paying for a distinctive point of view: **make deliberate, opinionated choices about palette, typography, and layout that are specific to this brief, and take one real aesthetic risk you can justify.**

---

## 1. Ground It in the Subject

| Step | Action |
|------|--------|
| **Define** | If the brief doesn't pin down the product/subject, **pin it yourself**: name one concrete subject, its audience, and the page's single job |
| **Use context** | Leverage any memory of human preferences, project context, or prior designs as hints |
| **Source from the subject** | The subject's own world — its materials, instruments, artifacts, and vernacular — is where distinctive choices come from |
| **Build with real content** | Use the brief's actual content and subject matter throughout |

---

## 2. Design Principles

### Hero = Thesis

> **Open with the most characteristic thing in the subject's world**, in whatever form makes sense: a headline, an image, an animation, a live demo, an interactive moment.

- Be deliberate — **a big number + small label + supporting stats + gradient accent is the template answer**; only use if truly the best option

### Typography Carries Personality

- **Pair display and body faces deliberately** — not the same families you'd reach for on any other project
- Set a **clear type scale** with intentional weights, widths, and spacing
- Make the **type treatment itself a memorable part of the design**, not a neutral delivery vehicle

### Structure Is Information

> **Structural devices (numbering, eyebrows, dividers, labels) should encode something true about the content, not decorate it.**

- Numbered markers (01/02/03) only appropriate if content **actually is a sequence** (real process, typed timeline where order carries needed information)
- **Question** if choices like numbered markers actually make sense before incorporating

### Leverage Motion Deliberately

| Motion Type | When to Use |
|-------------|-------------|
| Page-load sequence | Sets tone, orients user |
| Scroll-triggered reveal | Progressive disclosure |
| Hover micro-interactions | Feedback, affordance |
| Ambient atmosphere | Brand immersion |

- **An orchestrated moment usually lands harder than scattered effects** — choose what the direction calls for
- **Sometimes less is more** — extra animation can contribute to feeling AI-generated

### Match Complexity to Vision

- **Maximalist** → elaborate execution
- **Minimal** → precision in spacing, type, and detail
- **Elegance = executing the chosen vision well**

### Consider Written Content Carefully

> **Copy can make a design feel as templated as the design itself.** See [Writing in Design](#7-more-on-writing-in-design) for guidance.

---

## 3. Process: Brainstorm → Explore → Plan → Critique → Build → Critique Again

### The Three AI Default Clusters (Avoid Unless Brief Demands)

1. **Warm cream** (~#F4F1EA) + high-contrast serif display + terracotta accent
2. **Near-black** + single bright acid-green or vermilion accent
3. **Broadsheet-style** + hairline rules + zero border-radius + dense newspaper columns

> **All three are legitimate for some briefs, but they are defaults rather than choices, and they appear regardless of subject.** Where the brief pins down a visual direction, follow it exactly. Where it leaves an axis free, **don't spend that freedom on one of these defaults.**

### Two-Pass Workflow

#### Pass 1: Design Plan (Compact Token System)

| Token | Specification |
|-------|---------------|
| **Color** | 4–6 named hex values |
| **Type** | 2+ roles: characterful display face (used with restraint), complementary body face, utility face for captions/data if needed |
| **Layout** | One-sentence prose descriptions + ASCII wireframes to ideate/compare |
| **Signature** | **The single unique element this page will be remembered by** that embodies the brief appropriately |

#### Pass 2: Review & Revise

> **If any part reads like the generic default you would produce for any similar page — revise that part, say what you changed and why.**

- Work through a similar prompt to see if you arrive somewhere similar
- Only after confirming relative uniqueness → start writing code
- Follow revised plan exactly; derive every color/type decision from it

### CSS Specificity Warning

> **Be careful of structuring CSS selector specificities.** It's easy to generate classes that cancel each other out (especially with type-based like `.section` and element-based like `.cta`). This often happens with paddings/margins between sections.

---

## 4. Color

### Palette Discipline

- **4–6 named colors max** — background, surface, foreground, muted, primary, accent(s)
- Name them semantically: `--bg`, `--fg`, `--muted`, `--primary`, `--accent`, `--card`
- **No raw hex in components** — only var() references
- One **signature accent** used with restraint; it should feel intentional, not decorative

### Avoid Default Palettes

Don't reach for:
- Tailwind's slate/stone/zinc/slate/etc. as-is
- Generic "semantic" color mappings without subject grounding
- "Safe" combinations that appear across unrelated projects

### Dark Mode by Default

Design for dark first; derive light as inversion with intention. Test both.

---

## 5. Typography

### Font Selection

- **Display face**: Chosen for character; used sparingly (headlines, hero, key moments)
- **Body face**: Readable at length; complementary — not same family as display unless deliberate
- **Utility face** (optional): Monospace or condensed for data, code, captions
- **Total: 2–3 families max** — every additional family needs justification

### Type Scale

- Define a **modular scale** (e.g., 1.25 ratio) with named steps: `--text-xs`, `--text-sm`, `--text-base`, `--text-lg`, `--text-xl`, `--text-2xl`, `--text-3xl`, `--text-4xl`
- **Weights**: Use the full range (100–900) intentionally — don't default to 400/600/700
- **Letter-spacing**: Tighten at display sizes; normal at body sizes
- **Line-height**: Tighter for headlines (1.1–1.2); relaxed for body (1.5–1.7)

### Variable Fonts

Prefer variable fonts when available — single file, continuous weight/width/optical-size control.

---

## 6. Layout & Composition

### Spacing System

- **Base unit**: 4px or 8px — all spacing derives from it
- Named tokens: `--space-1` … `--space-12` (or similar)
- **No magic numbers** in component styles

### Grid & Container

- **Max-width container** for content; full-bleed for hero/atmosphere
- **Asymmetric layouts** welcome when they serve the content
- **Whitespace as active element** — not empty space, but breathing room that directs attention

### Responsive Behavior

- Define breakpoints as named tokens: `--bp-sm`, `--bp-md`, `--bp-lg`, `--bp-xl`
- **Mobile-first** by default; enhance up
- Content reflow should feel intentional, not like "stacking"

---

## 7. More on Writing in Design

### Copy Is Part of the Design

- **Headlines**: Specific, not clever. The hero headline should be the thesis statement
- **Body**: Conversational density — not marketing fluff, not technical manual
- **Microcopy**: Button labels, form hints, empty states — all carry voice
- **Consistent voice** across every string in the interface

### Avoid AI Writing Tells

- "Elevate your X" / "Unlock the power of Y" / "Seamless experience"
- Lists of 3 benefit bullets with parallel structure
- "In today's world..." / "In the fast-paced landscape..."
- **If it could be on any SaaS landing page, rewrite it.**

---

## 8. Motion & Interaction

### Principles

- **Motion serves content** — never motion for motion's sake
- **Respect `prefers-reduced-motion`** — always provide no-motion fallback
- **Duration**: 150–300ms for UI feedback; 500–1000ms for choreographed sequences
- **Easing**: Custom cubic-bezier, not `ease` / `ease-in-out` defaults

### Choreography

- **Staggered entrance** for lists/grids (50–100ms delay per item)
- **Shared element transitions** for navigation
- **One hero animation** per page — the "signature motion"

---

## 9. Verification Checklist

Before declaring done, **screenshot and verify**:

- [ ] Design has a **distinctive point of view** — not a default cluster
- [ ] Color palette is **4–6 semantic tokens**, derived from subject
- [ ] Typography uses **2–3 deliberate font choices** with a defined scale
- [ ] Layout has **intentional asymmetry or structure** — not generic grid
- [ ] Copy is **specific to this subject** — no AI tells
- [ ] Motion is **purposeful and restrained** — respects reduced-motion
- [ ] Dark and light modes both **look designed** (not inverted defaults)
- [ ] **Signature element** exists — the one thing you'd remember

### 9.1 Mandatory `hallmark audit` gate (post-UI)

If the `hallmark` skill is installed (it is, in this profile), the design is NOT done until a `hallmark audit` pass has run over the emitted artifact and returned a clean (or fixed) slop-test result. This is the enforcement layer for the anti-patterns in §10 — Hallmark codifies them as 58 discrete gates, so we run them rather than eyeball them.

**Procedure (run AFTER the screenshot verify above, before closeout):**

1. Load `hallmark` (`skill_view(name='hallmark')`).
2. Run the `audit` verb over the emitted page/CSS: score it against `references/slop-test.md` (58 gates) + `references/anti-patterns.md`.
3. If any gate fails → fix the emitted CSS/markup, re-run the audit. Do **not** declare done with open slop gates.
4. Report the slop-test outcome in closeout (pass class + any fixed gates), exactly like the §9 screenshot verify.

**Why this is non-optional:** §10 already lists Inter+slate, gradient-text, 3-col grids, etc. as failures — but a self-check is easy to skip under time pressure. `hallmark audit` turns that into a verifiable gate with a fixed checklist, consistent across every UI this profile emits. The `hallmark` skill is a faithful port of `Nutlope/hallmark` (MIT) living at `~/AppData/Local/hermes/skills/hallmark/`; invoke by intent (build / audit / redesign / study), there is no CLI binary in Hermes.

---

## 10. Anti-Patterns (What to Actively Avoid)

| Pattern | Why It Fails |
|---------|--------------|
| Generic "hero + 3 columns + footer" | Could be any SaaS |
| Tailwind defaults without customization | Reads as "unconfigured" |
| Gradient text on dark bg | Default AI decorator |
| 3-column benefit grids | Template tell |
| "Elevate/Unlock/Transform" copy | Marketing sludge |
| Animation on everything | Feels synthetic |
| Same Inter/Roboto + slate palette | Zero personality |

---

## 11. When Brief Provides Constraints

- **Design system exists** → Extend it, don't replace. Document what you're adding.
- **Brand guidelines exist** → Follow exactly. Your job is execution within constraints.
- **Component library exists** → Compose from it. Don't rebuild primitives.
- **Accessibility requirements** → Non-negotiable. WCAG AA minimum.

---

## 12. Handoff to Implementation

If you're designing for another agent to build:
1. **Produce the design plan** (tokens, wireframes, signature element)
2. **Annotate** component hierarchy and states
3. **Specify** exact CSS custom properties
4. **Flag** any non-standard browser APIs needed
5. **Verify** the built result against screenshots
6. **Run the `hallmark audit` gate** (§9.1) over the built result before sign-off — the 58-gate slop test is the pass/fail bar, not the screenshot alone.