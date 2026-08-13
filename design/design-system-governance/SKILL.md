---
name: design-system-governance
description: Use when a project has DESIGN.md/tokens but unverified implementation. Runs audit, establishes verification ga
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [design-system, audit, verification, three-layer-method, governance]
    related_skills: [frontend-design, steve-jobs-design-review, verification-before-completion, ce-strategy, ce-plan]
---

# Design System Governance — Three-Layer Method

## When to Use

- Project has DESIGN.md, tokens.json, tailwind.theme.json but **no verification artifacts**
- Taking ownership of a codebase with a design system — need to know actual compliance
- Before major refactor/feature work — verify Environment consumes Spec correctly
- Three-Layer Method gap detected: Spec ✅ | Verifier ❌ | Environment ❓
- Team says "looks right" but no audit exists — "looks right" is not verification

**Do NOT use for:** Greenfield design (use `frontend-design`), incremental tweaks, or when Verifier layer already current.

---

## Core Concept: Three-Layer Method for Design Systems

| Layer | Artifacts | Gate | Owner |
|-------|-----------|------|-------|
| **Spec** | DESIGN.md (source), tokens.json (DTCG), tailwind.theme.json (Tailwind v3), index.css (@theme + :root) | Machine-readable, exports validated, single source of truth | Design lead |
| **Verifier** | design-system-audit.md, ux-evaluation.md, visual regression tests | **P0 violations = 0** before Environment work | Auditor |
| **Environment** | ui/ primitives, calculator components, pages | Compose from primitives, zero hardcoded tokens | Engineers |

**Invariant:** Spec investment is wasted if Environment doesn't consume it. Verifier layer **blocks** Environment feature work until P0 clear.

---

## Audit Workflow (The Verifier Layer)

### Phase 1: Spec Completeness Check
**Input:** DESIGN.md  
**Check:** All sections present (Colors, Typography, Spacing, Rounded, Components, Motion, Signature Elements, Accessibility, Export commands)  
**Output:** Completeness score + gap list

### Phase 2: Token Fidelity
**Input:** tokens.json, tailwind.theme.json, src/index.css vs DESIGN.md  
**Check:** Every token in DESIGN.md exists in all three with identical values  
**Output:** Fidelity % per category (Colors, Spacing, Typography, Rounded, Motion)

### Phase 3: Component Inventory
**Input:** DESIGN.md §Component Usage Map vs `src/components/ui/`  
**Check:** Every semantic component exists with correct variants  
**Output:** Missing / Partial / Complete table

### Phase 4: Implementation Scan (Anti-Pattern Detection)
**Input:** All component files (`src/**/*.tsx`)  
**Greppable anti-patterns:**

```bash
# P0: Hardcoded magic numbers
grep -rn "text-\[[0-9]px\]" src/
grep -rn "p-\[[0-9]" src/
grep -rn "rounded-\[[0-9]" src/

# P0: Generic Tailwind colors
grep -rn "slate-\|zinc-\|gray-\|neutral-\|stone-" src/

# P0: Raw hex in components
grep -rn "#[0-9a-fA-F]\{6\}" src/ --include="*.tsx"

# P1: Missing semantic composition
grep -rn "className.*bg-.*border-.*rounded-" src/ | grep -v "var(--color"
```

**Output:** Violation catalog with file:line, priority, remediation

### Phase 5: Signature Element Verification
**Input:** DESIGN.md §Signature Elements vs src/index.css  
**Check:** Each named element (`.accent-bar`, `.curve-glow`, `.stagger-in`, `.pulse-brass`, etc.) implemented  
**Output:** Present / Missing list

### Phase 6: RTL / Theme / Accessibility
**Check:** Dark/light mode renders correctly, RTL Hebrew + Math LTR isolation, WCAG AA contrast in both themes  
**Output:** Pass/fail per component per criterion

---

## Audit Outputs

### 1. design-system-audit.md (Machine-readable + Human)
Structured report with:
- Spec completeness score
- Token fidelity table
- Component inventory table
- Violation catalog (P0/P1/P2)
- Signature element status
- RTL/Theme/A11y matrix
- Remediation priority list

### 2. ux-evaluation.md (Experience verdict)
Via `steve-jobs-design-review`:
- Binary verdict per screen/flow (BRILLIANT/SHIT)
- The One Thing to perfect
- Cut list vs Keep list
- SHIP / DON'T SHIP verdict

---

## Remediation Protocol

### P0 — Blocks All Feature Work (Must be zero before Environment features)
| Violation | Fix |
|-----------|-----|
| `text-[Npx]`, `p-[N]`, `rounded-[N]` hardcoded | Replace with semantic tokens |
| `slate-`/`zinc-`/`gray-`/`neutral-`/`stone-` utilities | Replace with `var(--color-*)` |
| Raw `#hex` in components | Replace with `var(--color-*)` |
| Missing signature elements (`.accent-bar`, etc.) | Implement in CSS with motion tokens |
| Missing `prefers-reduced-motion` handling | Add for all animations |
### P1 — Design System Completeness (After P0, Before Complex Features)

| Violation | Fix |
|-----------|-----|
| Missing primitive components (Button, Input, Badge, Table, Tooltip, Accordion, FormulaBlock, Modal, Heading) | Build per DESIGN.md §Component Usage Map |
| Components don't compose from primitives | Refactor to compose from ui/ primitives |
| Motion tokens not in CSS/@theme | Add `--motion-duration-*`, `--motion-easing-*` |

### P1 Primitive Build Order (Highest Reuse First)

Per DESIGN.md §Component Usage Map, build primitives in this priority order:

| Priority | Primitive | DESIGN.md Spec | Reuse Rationale |
|----------|-----------|----------------|-----------------|
| **P1-1** | `Button` + `SegmentedButton` | 5 variants (primary, secondary, ghost, danger, success) | Highest reuse — every calculator, modal, form |
| **P1-2** | `Badge` + `StatusBadge` + `BadgeGroup` | 5 semantic (brass, teal, crimson, cobalt, neutral) | Status displays: Power, α, Z-scores, P-values |
| **P1-3** | `Heading` + `SectionHeader` | 4 scales (page, section, subsection, label) | Every page/section/subsection |
| **P1-4** | `Input` / `Select` / `Label` + `InputGroup` | 6 form variants | All parameter inputs, dropdowns |
| **P1-5** | `Accordion` + `SimpleAccordion` | FormulaSheet chapters, power calc | Progressive disclosure, chapter navigation |
| **P1-6** | `Table` + `DecisionMatrixCell` + `PowerTable` | Decision matrices, power tables | Type I/II error tables, power analysis |
| **P1-7** | `Tooltip` + `ChartTooltip` + `InputHelpTooltip` | Input help, chart hover | Contextual help, chart data points |
| **P1-8** | `FormulaBlock` | 2 variants (formula-block, calc-block) | Formulas, substituted calculations |
| **P1-9** | `Modal` | StatisticalHelperModal, confirmations | Help modal, destructive confirmations |

**Build Rule:** Each primitive must:
1. Consume DESIGN.md tokens via `var(--color-*)`, `var(--spacing-*)`, `var(--rounded-*)`
2. Export from `src/components/ui/index.ts` barrel
3. Include RTL support (`dir="rtl"` on containers, `dir="ltr"` on math/numeric content)
4. Pass all 7 verification checks before commit
5. Include TypeScript types for all props

### P1 Non-Compositional Components (P1-NC)

After primitives exist, refactor existing components to compose from them:

```bash
# Find components building inline className soup
grep -rn "className.*bg-.*border-.*rounded-" src/components/ | \\
  grep -v "var(--color" | \\
  grep -v "ui/" | \\
  grep -v "node_modules"

# Target refactor: replace inline styles with primitive imports
# e.g. <button className="bg-cobalt text-white px-4 py-2 rounded"> → <Button variant="primary">
```

### P2 — Polish (Can parallel with features)
| Violation | Fix |
|-----------|-----|
| Light mode not visually verified | Test all components in both themes |
| Visual regression tests missing | Add Chromatic/Percy or screenshot diff |
| Component API documentation missing | Storybook or similar |

---

## Verification Gates (CI-Ready)

```bash
# Gate 1: Token discipline (runs in CI)
npm run lint:tokens   # grep for hardcoded sizes, generic colors, raw hex

# Gate 2: Component composition
npm run lint:components  # verify components import from ui/ primitives

# Gate 3: Signature elements
npm run test:signatures  # verify .accent-bar, .curve-glow, etc. exist in CSS

# Gate 4: Accessibility
npm run test:a11y  # axe-core or similar
```

### Session Verification Checklist (Run After Each Primitive Build)

```bash
# 1. Build passes without TypeScript/Vite errors
npm run build

# 2. Token discipline: no hardcoded sizes, no generic colors, no raw hex
npm run lint:colors

# 3. Git clean: no untracked review artifacts (add to .gitignore)
git status --porcelain | grep -v "^??" || true

# 4. Hardcoded sizes scan (P0-HS)
grep -rn "text-\\[[0-9]px\\]" src/ --include="*.tsx" | grep -v "node_modules" || echo "CLEAN"

# 5. Generic Tailwind colors scan (P0-GC)
grep -rn "slate-\\|zinc-\\|gray-\\|neutral-\\|stone-" src/ --include="*.tsx" | grep -v "var(--color" || echo "CLEAN"

# 6. Signature elements present
for elem in ".accent-bar" ".curve-glow" ".stagger-in" ".pulse-brass"; do
  grep -q "$elem" src/index.css && echo "✅ $elem" || echo "❌ $elem MISSING"
done

# 7. prefers-reduced-motion handling
grep -q "prefers-reduced-motion" src/index.css && echo "✅ reduced-motion" || echo "❌ reduced-motion MISSING"
```

**All 7 checks must pass before committing primitives.**

---

## Integration with Context Engineering (CE) Workflow

| CE Step | Design System Governance Role |
|---------|-------------------------------|
| `ce-strategy` | STRATEGY.md includes design system maturity as KPI |
| `ce-brainstorm` | Requirements include design system compliance criteria |
| `ce-plan` | P0 remediation as gate before feature tasks; P1 as parallel track |
| `ce-work` | Worktrees for primitive components; feature branches blocked on P0 |
| `ce-code-review` | 12-persona includes Design System Auditor persona |
| `ce-compound` | Extract audit patterns, violation taxonomies, remediation scripts |
| `ce-product-pulse` | Track design debt: P0 count, component coverage %, signature element status |

---

## Common Pitfalls

| Pitfall | Prevention |
|---------|------------|
| "Design system exists" = "compliant" | Audit is mandatory; Spec ≠ Environment |
| Fixing P1 before P0 | P0 blocks all feature work; sequence is invariant |
| Auditing once | Verifier layer must be re-run on every DESIGN.md change |
| Skipping UX evaluation | Token compliance ≠ good experience; pair with `steve-jobs-design-review` |
| No CI gates | Violations recur; automate the greppable checks |
| Treating audit as "done" | Verifier layer is a living artifact; update on every Spec change |

---

## Quick Start (One-Liner)

```bash
# In project root with DESIGN.md
# 1. Run audit (frontend-design skill)
# 2. Run UX review (steve-jobs-design-review skill)
# 3. If P0 > 0: STOP features, remediate P0
# 4. If P0 == 0: Plan P1 primitives, then features
```

---

## References

- `references/violation-taxonomy.md` — Complete violation catalog with regex patterns
- `references/primitive-building-patterns.md` — Token consumption, component structure, RTL, export patterns for P1 primitives
- `references/remediation-scripts.md` — Re-runnable scripts for bulk replacement
- `templates/design-system-audit.md` — Audit report template
- `templates/ux-evaluation.md` — UX evaluation template