---
name: good-strategy-bad-strategy
description: Use when evaluating, crafting, or stress-testing strategy — Richard Rumelt's kernel (diagnosis, guiding policy
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [strategy, rumelt, diagnosis, guiding-policy, coherent-action, bad-strategy]
    related_skills: [product-strategy-frameworks, crossing-the-chasm, blue-ocean-strategy, traction-eos, ce-strategy]
---

# Good Strategy / Bad Strategy — Rumelt's Kernel

## Overview

Richard Rumelt's *Good Strategy Bad Strategy* cuts through the fluff: **strategy is not goals, vision, or ambition — it's a coherent response to a challenge.** This skill operationalizes Rumelt's **Kernel** (Diagnosis → Guiding Policy → Coherent Action) and his **hallmarks of bad strategy** into a repeatable agent workflow for strategy creation, review, and stress-testing.

## When to Use

- **Strategy authoring** — turning a vague direction into a Rumelt-compliant kernel
- **Strategy review** — stress-testing an existing strategy against the kernel + bad-strategy hallmarks
- **Decision framing** — structuring a high-stakes choice as a strategic problem
- **Org alignment** — translating top-level strategy into coherent actions per team
- **Postmortem** — diagnosing why a strategy failed (usually: missing kernel or bad-strategy traits)
- **Don't use for:** tactical planning, OKR setting, or when you need execution frameworks (use traction-eos or ce-plan instead)

## The Kernel (Three Elements, All Required)

### 1. Diagnosis — "What's Going On?"
A diagnosis **simplifies complexity** by identifying the critical aspects of the situation. It replaces an overwhelming reality with a actionable story.

- **Not a list of problems** — a *pattern explanation* that points to leverage
- **Uses a metaphor/frame** — "This is a *commodity trap*" or "This is a *coordination failure*"
- **Test:** Does the diagnosis suggest *where to focus* and *what to ignore*?

### 2. Guiding Policy — "How Do We Deal With It?"
A guiding policy **constrains action** without specifying every move. It's the *approach* for overcoming the obstacles identified in the diagnosis.

- **Not a goal** — "Be #1" is a goal. "Win on integration depth while competitors chase breadth" is a guiding policy.
- **Creates advantage** — by concentrating resources on a *pivot point* where relative strength matters
- **Test:** Does it rule out a wide swath of plausible actions?

### 3. Coherent Action — "What Do We Do?"
Coordinated actions that **build on each other**, not a "to-do list." Each action reinforces the others.

- **Not "initiatives"** — Initiatives are independent. Coherent actions are *interdependent*.
- **Resource allocation is the acid test** — Budget, headcount, calendar must reflect the policy
- **Test:** If you dropped the bottom 50% of actions, would the rest still work?

## Bad Strategy Hallmarks (Detection Checklist)

| Hallmark | Signal | Antidote |
|----------|--------|----------|
| **Fluff** | Gibberish masquerading as expertise; "cloud-first blockchain-enabled AI leverage" | Restate in plain English. If it evaporates, it was fluff. |
| **Failure to Face the Problem** | Strategy ignores the *real* challenge (competition, tech shift, org debt) | Rewrite diagnosis until it names the brutal fact. |
| **Mistaking Goals for Strategy** | "20% growth," "market leadership," "digital transformation" | Ask: "What's the kernel?" No kernel = no strategy. |
| **Bad Strategic Objectives** | Laundry lists, "push" objectives (do more), vague "improve X" | Objectives must be *proximate* — solvable with current resources. |
| **Blue Sky / Wishful Thinking** | "We'll disrupt by being better" without *how* | Demand guiding policy + coherent actions. |
| **Template-Style Strategy** | Fill-in-the-blanks: Vision/Mission/Values/Goals | Strategy is bespoke to the challenge. Templates produce fluff. |

## Skill Usage Patterns

### Pattern: Strategy Kernel Extraction
```
Use good-strategy-bad-strategy skill to extract kernel from [strategy doc / deck / narrative].
Output: Diagnosis (1 paragraph), Guiding Policy (1 sentence), Coherent Actions (3-5 interdependent moves).
Flag: any bad-strategy hallmarks detected.
```

### Pattern: Strategy Stress Test
```
Use good-strategy-bad-strategy skill to stress-test [proposed strategy].
Checks: kernel complete? diagnosis actionable? policy constraining? actions coherent? bad-strategy hallmarks?
Output: PASS/FAIL per check, specific fixes, rewritten kernel if needed.
```

### Pattern: Strategy from Scratch
```
Use good-strategy-bad-strategy skill to craft strategy for [situation: e.g., "B2B SaaS plateauing at $5M ARR, churn rising, two well-funded competitors"].
Process: 1) diagnose → 2) guiding policy → 3) coherent actions.
Output: full kernel + 90-day action map with resource allocation.
```

### Pattern: Bad Strategy Cleanup
```
Use good-strategy-bad-strategy skill to de-fluff [strategy doc].
Identify: fluff passages, goal-masquerading-as-strategy, missing diagnosis, incoherent actions.
Output: cleaned kernel, deleted fluff, specific rewrites.
```

## Example Invocations

> **User:** "Our strategy: 'Become the AI-first CRM for SMBs. Goals: 3x ARR, launch AI features, hire 50 people.' Use good-strategy-bad-strategy skill."
>
> **Agent applies:**
> 1. **Diagnosis missing** — *Why* is this the right challenge? What's the leverage point?
> 2. **Goals masquerading as strategy** — 3x ARR is a goal, not a kernel.
> 3. **No guiding policy** — How do we win? "AI-first" is a label, not a policy.
> 4. **Incoherent actions** — Hiring 50 ≠ coordinated with AI launch ≠ SMB focus.
> 5. **Returns:** Rewritten kernel + bad-strategy flags + 90-day coherent action map.

> **User:** "Review this strategy: 'Diagnosis: Competitors have better distribution. Policy: Build viral product-led growth. Actions: Add invite flow, referral rewards, free tier, SEO content, partnerships.' Use good-strategy-bad-strategy skill."
>
> **Agent applies:**
> 1. Diagnosis: OK but thin — *why* does distribution beat product? What's our counter-advantage?
> 2. Policy: "Viral PLG" is a tactic, not a policy. Policy would be: "Win on time-to-value for solo founders; competitors serve teams."
> 3. Actions: Incoherent — SEO content doesn't build viral loops. Partnerships ≠ PLG.
> 4. **Returns:** tightened diagnosis, reframed policy, pruned action set (keep: invite flow, referral, free tier; cut: SEO, partnerships).

## Common Pitfalls

1. **Writing a diagnosis that's just a problem list** — "Competitors, churn, tech debt" is not a diagnosis. "We're trapped in a feature-parity race where our architecture prevents rapid iteration" is.
2. **Confusing guiding policy with vision/mission** — "Empower every developer" is vision. "Win on local-first architecture while competitors require cloud" is policy.
3. **Listing initiatives as coherent actions** — "Launch mobile, add SSO, rewrite billing" are independent projects. Coherent actions: "Ship local-first sync → enables mobile offline → reduces churn → funds billing rewrite."
4. **Skipping resource allocation** — If the budget doesn't match the policy, the strategy is theater.
5. **Applying to operational problems** — "Reduce bug count" is an operational target. Strategy addresses *competitive/structural* challenges.

## Verification Checklist

- [ ] Diagnosis: single paragraph, names the challenge, implies focus, uses a framing metaphor
- [ ] Guiding Policy: one sentence, constrains action, creates advantage at a pivot point
- [ ] Coherent Actions: 3-5 moves, interdependent (each amplifies the others), resource-allocated
- [ ] No bad-strategy hallmarks: fluff, goal-masquerade, problem-avoidance, template language
- [ ] Kernel fits on one page — if it doesn't, it's not a kernel
- [ ] Output includes: rewritten kernel, bad-strategy flags, 90-day action map with owners

## One-Shot Recipes

### Recipe: Quarterly Strategy Review
```
Use good-strategy-bad-strategy skill to review Q[X] strategy.
Inputs: current strategy doc, last quarter results, competitive shifts.
Output: kernel validity check, bad-strategy drift report, adjusted actions for next quarter.
```

### Recipe: Competitive Response Framing
```
Use good-strategy-bad-strategy skill to frame response to [competitor move: e.g., pricing drop, feature launch, funding round].
Process: diagnose the strategic threat → guiding policy for response → 3 coherent counter-moves.
Output: kernel + 30/60/90-day plan.
```

### Recipe: Strategy-to-OKR Translation
```
Use good-strategy-bad-strategy skill to translate [validated kernel] into OKRs.
Constraint: every OKR must trace to a coherent action; no orphan objectives.
Output: Objective → Key Results → Coherent Action mapping, resource allocation %.
```