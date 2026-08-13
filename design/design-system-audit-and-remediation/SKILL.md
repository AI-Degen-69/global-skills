---
name: design-system-audit-and-remediation
description: Use when a project defines a design system (DESIGN.md/tokens) and you must verify implementation.
category: software-development
---

## When to use
When working on a project that defines a design system via DESIGN.md and token files (index.css, tailwind.theme.json, tokens.json) and you need to ensure implementation compliance before proceeding with feature work.

## Why
Design system drift leads to inconsistent UI, broken semantics, and increased technical debt. Auditing and remediating early unlocks component composition and prevents rework.

## Steps

### 1. Audit for common violations
- Search for hardcoded pixel font sizes: `text-\\[0-9\\]+px` (e.g., text-\\[10px\\], text-\\[11px\\], text-\\[13px\\], text-\\[15px\\]).
- Search for raw `slate-800` or `bg-slate-800` etc.
- Verify signature elements (`.accent-bar`, `.curve-glow`, `.stagger-in`, `.pulse-brass`) exist in `src/index.css`.
- Verify motion tokens (`--motion-duration-*`, `--motion-easing-*`, `--motion-stagger-delay`) are defined in `:root`.

### 2. Remediate hardcoded pixel font sizes
Replace each occurrence with the appropriate semantic token from DESIGN.md:
- `text-\\[10px\\]` → `text-xs` (or `caption` depending on context)
- `text-\\[11px\\]` → `text-xs` or `caption`
- `text-\\[13px\\]` → `text-sm` or `body-xs`
- `text-\\[15px\\]` → `text-base` or `body-sm`
Use the `patch` tool with surrounding context to ensure uniqueness.

### 3. Remediate raw slate-800
Replace `slate-800` with `var(--color-border)` or the appropriate semantic accent (`--color-accent-brass`, etc.) based on usage (border vs background vs text).

### 4. Add missing signature elements
Append to `src/index.css` under the "Signature Elements" section:
```css
/* .accent-bar — 48×4px brass→teal gradient bar. Marks hero sections, primary actions, page titles. */
.accent-bar {
  width: 48px;
  height: 4px;
  background: linear-gradient(90deg, var(--color-accent-brass), var(--color-accent-teal));
  border-radius: var(--rounded-full);
  flex-shrink: 0;
}

/* .curve-glow — Brass+teal blur glow. Appears on active calculation panels, live results. */
.curve-glow {
  box-shadow:
    0 0 24px rgba(250, 204, 21, 0.35),
    0 0 48px rgba(46, 196, 182, 0.25);
  transition: box-shadow 300ms ease-out;
}

/* .stagger-in — Choreographed entrance (50ms stagger). Page load, mode switches. */
.stagger-in > * {
  opacity: 0;
  transform: translateY(8px);
  animation: stagger-in 500ms ease-out forwards;
}
.stagger-in > *:nth-child(1)  { animation-delay: 0ms; }
.stagger-in > *:nth-child(2)  { animation-delay: 50ms; }
.stagger-in > *:nth-child(3)  { animation-delay: 100ms; }
.stagger-in > *:nth-child(4)  { animation-delay: 150ms; }
.stagger-in > *:nth-child(5)  { animation-delay: 200ms; }
.stagger-in > *:nth-child(6)  { animation-delay: 250ms; }
.stagger-in > *:nth-child(7)  { animation-delay: 300ms; }
.stagger-in > *:nth-child(8)  { animation-delay: 350ms; }

@keyframes stagger-in {
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* .pulse-brass — Live calculation indicator. Breathing brass glow on active results. */
.pulse-brass {
  animation: pulse-brass 2s ease-in-out infinite;
}

@keyframes pulse-brass {
  0%, 100% {
    box-shadow: 0 0 0 rgba(250, 204, 21, 0);
  }
  50% {
    box-shadow: 0 0 16px rgba(250, 204, 21, 0.6), 0 0 32px rgba(250, 204, 21, 0.3);
  }
}
```
(Include also `.pulse-success` and `.pulse-error` if needed.)

### 5. Add motion tokens
In `:root` of `src/index.css`, add:
```css
--motion-duration-fast: 150ms;
--motion-duration-normal: 280ms;
--motion-duration-slow: 500ms;
--motion-duration-choreographed: 1000ms;
--motion-easing-standard: cubic-bezier(0.4, 0, 0.2, 1);
--motion-easing-entrance: cubic-bezier(0.16, 1, 0.3, 1);
--motion-easing-exit: cubic-bezier(0.4, 0, 1, 1);
--motion-stagger-delay: 50ms;
```

### 6. Verify
Run the following commands and ensure they pass:
```bash
npm run lint:tsc   # TypeScript strict check
npm run lint:colors # Color token lint (no raw slate/gray/zinc, no magic pixel sizes)
npm run build       # Full production build
```
If any fail, iterate on the fixes.

## Pitfalls
- Forgetting to regenerate `tailwind.theme.json` and `tokens.json` after editing `index.css`. Run the DESIGN.md export commands if needed.
- Overlooking `prefers-reduced-motion` media query; ensure animations are disabled when user prefers reduced motion.
- Accidentally breaking KaTeX RTL isolation (`.katex { direction: ltr !important; }`). Do not modify these rules.
- Using utility classes like `bg-slate-900` instead of semantic tokens; always map meaning → component variant.

## References
- DESIGN.md – authoritative spec
- CONTEXT.md – current architecture and known issues
- STRATEGY.md – product anchor and verification metrics

## Output
A codebase where all visual tokens consume DESIGN.md semantics, signature elements are present, motion tokens are defined, and lint checks pass.

---
*Updated: 2026-06-20*
*Author: Hermes (based on session with Robert)*