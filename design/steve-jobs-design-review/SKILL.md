---
name: steve-jobs-design-review
description: Use when evaluating a design, UI, or product experience through Steve Jobs' lens — ruthless simplicity, binary
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [design, ux, steve-jobs, review, simplicity, focus]
    related_skills: [refactoring-ui, ux-heuristics, top-design, design-everyday-things]
---

# Steve Jobs Design Review

## Overview

Steve Jobs' design philosophy wasn't about aesthetics — it was about **saying no to the non-essential** until only the core experience remains. This skill applies Jobs' review methodology: binary verdicts (brilliant/shit), ruthless simplification, and the discipline to ship only what matters.

Based on Walter Isaacson's *Steve Jobs* and Ken Segall's *Insanely Simple*, this skill translates Jobs' famous design reviews into a repeatable agent workflow. It doesn't just critique — it forces clarity.

## When to Use

- **Design reviews** — evaluating UI mockups, product concepts, or user flows before shipping
- **Feature prioritization** — deciding what to cut to reach a coherent MVP
- **Product strategy** — defining the "one thing" a product must do exceptionally well
- **Team alignment** — creating shared vocabulary for "good enough" vs "ship-worthy"
- **Don't use for:** incremental improvements, A/B test analysis, or when you need gentle iterative feedback

## Core Methodology: The Jobs Review Loop

### 1. Binary Verdict First
Every element gets a verdict: **Brilliant** or **Shit**. No "good but," no "needs work." If it's not brilliant, it's shit — cut it or redo it.

### 2. The Simplicity Test
> "Simple can be harder than complex. You have to work hard to get your thinking clean to make it simple."

For each screen/flow/feature, ask:
- What is the **one job** this screen does?
- What can be removed without breaking that job?
- Would a first-time user understand it in 3 seconds?

### 3. The Focus Filter
Jobs famously said: "People think focus means saying yes to the thing you've got to focus on. But that's not what it means at all. It means saying no to the hundred other good ideas."

Apply:
- List every feature/screen/element in scope
- Force-rank by impact on the core user job
- Kill the bottom 80% — even if they're "good"

### 4. The "Insanely Great" Standard
The bar isn't "competitive" or "good UX." The bar is: **would this make the user feel something?** If the answer is no, it's not done.

### 5. End-to-End Ownership
Jobs reviewed the box, the unboxing, the first boot, the onboarding, the icon, the marketing page — **the total experience**. This skill demands the same scope.

## Skill Usage Patterns

### Pattern: Full Product Review
```
Use steve-jobs-design-review skill on [product/flow/screens].
Scope: [e.g., onboarding → dashboard → core action]
Deliver: binary verdict per screen, cut list, the one thing to double down on.
```

### Pattern: Feature Triage
```
Use steve-jobs-design-review skill to triage [feature list].
Constraint: ship date is [X weeks].
Output: ranked keep/cut/kill with Jobs-style rationale.
```

### Pattern: Design Concept Selection
```
Use steve-jobs-design-review skill to choose between [concept A] vs [concept B].
Criteria: simplicity, emotional resonance, focus on core job.
Output: binary pick with 3-sentence rationale.
```

## Example Invocations

> **User:** "Review our new dashboard design. Use steve-jobs-design-review skill."
> 
> **Agent applies:**
> 1. Inventory every widget, chart, tab, dropdown
> 2. For each: what's the one user job it serves?
> 3. Verdict: Brilliant / Shit
> 4. Cut list: everything rated Shit
> 5. Identify the ONE screen/flow that must be perfect
> 6. Return: verdict table, cut list, the "one thing" to perfect

> **User:** "We have 12 features for MVP. Use steve-jobs-design-review skill to decide what ships."
> 
> **Agent applies:**
> 1. Map each feature to core user job
> 2. Force-rank by indispensability
> 3. Binary: ships or doesn't
> 4. Return: ship list (max 3), kill list, the "hero feature" rationale

## Common Pitfalls

1. **Softening the verdict** — "It's good but needs polish" is not a Jobs verdict. It's Shit. Rebuild or cut.
2. **Reviewing in isolation** — Jobs reviewed the total experience (box, marketing, support). Scope must be end-to-end.
3. **Confusing simplicity with minimalism** — Simplicity is *clarity of purpose*, not few elements. A complex dashboard can be simple if every element serves the one job.
4. **Applying to early exploration** — This is a **gate skill** for shipping decisions, not a brainstorming tool.
5. **Ignoring emotional resonance** — "Usable" is the floor. "Makes the user feel understood" is the bar.
6. **Inventing metrics or assuming features** — The Simplicity Test asks "Would a first-time user understand it in 3 seconds?" — the "3 seconds" is a prompt to think, not a measured metric. Do not report invented targets (e.g., "60 seconds") as facts. Do not assume features exist (e.g., "chi-squared test") without verifying in the running code. **Label every synthesis explicitly**: "DESIGN.md says X" vs "Jobs review interprets Y." The output must distinguish spec facts from reviewer invention.

## Verification Checklist

- [ ] Every reviewed element has a binary verdict (Brilliant/Shit)
- [ ] Cut list is explicit and non-negotiable
- [ ] The "one thing" is identified and defended
- [ ] Scope covers end-to-end experience, not just UI
- [ ] Rationale references Jobs/Isaacson/Segall principles, not generic UX heuristics
- [ ] Output is actionable: ship list, kill list, the hero focus

## One-Shot Recipes

### Recipe: Pre-Launch Gate
```
Use steve-jobs-design-review skill on [product name] pre-launch.
Scope: landing page → signup → onboarding → first value moment → core loop
Deliver: pass/fail verdict, top 3 cuts, the one screen that must be perfect.
```

### Recipe: Design Partner Review
```
Use steve-jobs-design-review skill to evaluate [design partner's] concept deck.
Constraint: we can only build one.
Output: binary pick, 3-sentence rationale, what the loser teaches us.
```

### Recipe: Existing Product UX Audit
```
Use steve-jobs-design-review skill on [product name] UX audit.
Scope: all user-facing screens/flows in running product
Context: existing product refactor prioritization
Deliver: binary verdict per screen, cut list (refactor backlog), keep list, the one thing to perfect, Jobs-style rationale, SHIP/DON'T SHIP verdict.
Reference: references/ux-evaluation-existing-product.md for verdict templates and adaptation notes.
```