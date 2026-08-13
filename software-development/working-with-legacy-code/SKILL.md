---
name: working-with-legacy-code
description: "Use when safely changing untested/legacy code — Michael Feathers' Working Effectively with Legacy Code: seams"
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [legacy, refactoring, testing, characterization-tests, seams, feathers, technical-debt]
    related_skills: [refactoring-patterns, clean-code, test-driven-development, dependency-vulnerability-remediation, diagnose]
---

# Working Effectively with Legacy Code — Feathers' Playbook

## Overview

Michael Feathers defines **legacy code simply: code without tests.** This skill operationalizes Feathers' core insight — *you cannot safely change what you cannot verify* — into a repeatable workflow for getting legacy code under test, making changes, and incrementally paying down technical debt without rewrites.

The methodology: **Identify seams → Write characterization tests → Break dependencies → Sprout/Wrap → Refactor under test.**

## When to Use

- **Legacy code change** — any modification to code with low/no test coverage
- **Technical debt paydown** — systematic approach to de-risking a codebase
- **Refactoring planning** — sequencing changes to maintain velocity while improving structure
- **Onboarding to a legacy codebase** — mapping seams and characterization test strategy
- **Risk assessment** — estimating effort/risk for changes in untested areas
- **Don't use for:** greenfield development, test-driven new features (use test-driven-development), or architectural rewrites (use system-design + release-it)

## Core Concepts

### The Legacy Code Change Algorithm
```
1. Identify the change point
2. Find test points (seams)
3. Break dependencies
4. Write characterization tests
5. Make the change
6. Refactor (under test)
```
**Never skip steps.** The algorithm exists because each step enables the next.

### Seams — Where You Can Alter Behavior Without Editing
A **seam** is a place where you can change behavior without changing code *at that spot*.

| Seam Type | Mechanism | Example |
|-----------|-----------|---------|
| **Preprocessor** | `#define`, `#ifdef` | Compile-time dependency selection |
| **Link** | Substitute library at link time | Swap DB driver for test double |
| **Object** | Polymorphism, dependency injection | Inject interface instead of concrete class |
| **Function** | Function pointers, delegates | Pass callback instead of direct call |

**Goal:** Create seams until you can test the change point in isolation.

### Characterization Tests — "What Does This Code Actually Do?"
Not unit tests. **Characterization tests document current behavior** — bugs and all. They say: *"This is what the code does today."* They enable safe change by detecting *any* behavioral shift.

**Process:**
1. Pick a class/function at the change point
2. Write a test that exercises it with real inputs
3. Run test → it fails (no assertion yet)
4. Use failure output to write the *actual* assertion
5. Repeat until behavior is characterized

**Key insight:** You're not testing *correctness*. You're locking *current behavior*.

### Dependency Breaking Techniques

| Technique | When | How |
|-----------|------|-----|
| **Parameterize Constructor** | Class creates collaborator internally | Add constructor arg; default to old behavior |
| **Parameterize Method** | Method creates/uses collaborator | Add method parameter; default to old |
| **Extract Interface** | Concrete class used directly | Create interface; implement on concrete; inject |
| **Subclass and Override** | Can't modify class (3rd party, frozen) | Subclass; override problematic method; use subclass |
| **Adapt Parameter** | Method signature doesn't match test need | Add adapter/wrapper that translates |
| **Encapsulate Global** | Global state/singletons | Wrap in class; inject wrapper; control in tests |
| **Expose Static Method** | Static method blocks testing | Make non-static; or wrap in instance method |

### Sprout Method / Sprout Class
**When adding new behavior to legacy code:**
- **Sprout Method:** Write new logic in a *new method* (tested), call from legacy code
- **Sprout Class:** Write new logic in a *new class* (tested), instantiate from legacy code

Both keep legacy code untouched while new code is testable.

### Wrap Method / Wrap Class
**When modifying existing behavior in legacy code:**
- **Wrap Method:** Rename legacy method → `legacyMethod`; create new `method` that calls legacy + adds behavior
- **Wrap Class:** Delegate to legacy class; override/extend only what's needed

Both let you test new behavior while preserving old.

## Skill Usage Patterns

### Pattern: Legacy Change Risk Assessment
```
Use working-with-legacy-code skill to assess risk of [change description] in [file/module].
Analyze: seams available, dependency breaking needed, characterization test scope, sprout/wrap applicability.
Output: risk level (low/med/high), seam map, test plan, estimated effort, rollback strategy.
```

### Pattern: Characterization Test Suite Generation
```
Use working-with-legacy-code skill to generate characterization tests for [class/module].
Scope: public API, critical paths, change points.
Output: test file with characterization tests, seam documentation, dependency breaking notes.
```

### Pattern: Legacy Refactoring Sequence
```
Use working-with-legacy-code skill to plan refactoring of [module] toward [target architecture].
Constraints: no rewrites, maintain deployability, incremental.
Output: phased plan (seam creation → characterization tests → dependency breaking → sprouts → refactors), risk checkpoints.
```

### Pattern: New Feature in Legacy Codebase
```
Use working-with-legacy-code skill to implement [feature] in [legacy area].
Approach: sprout method/class for new logic; characterization tests for touch points; wrap if modifying.
Output: implementation plan, test strategy, seam modifications, verification steps.
```

## Example Invocations

> **User:** "We need to add a new payment provider to the legacy billing module (2000 lines, 0 tests). Use working-with-legacy-code skill."
>
> **Agent applies:**
> 1. **Identify change point** — `PaymentProcessor.process()` and provider selection logic
> 2. **Find seams** — None. `PaymentProcessor` instantiates `StripeClient` directly; uses global `Config`
> 3. **Break dependencies** — Parameterize constructor for `PaymentClient` interface; encapsulate `Config` access
> 4. **Characterization tests** — Cover `process()` with 5 scenarios (success, decline, timeout, partial, idempotency)
> 5. **Sprout Class** — New `AdyenProvider` implements `PaymentClient` (fully tested)
> 6. **Wrap Method** — `selectProvider()` wraps legacy logic, adds new provider routing
> 7. **Returns:** seam diff, test file, new provider class, integration steps, rollback plan

> **User:** "Refactor the God class `OrderService` (3000 lines, handles pricing, inventory, shipping, notifications). Use working-with-legacy-code skill."
>
> **Agent applies:**
> 1. **Map seams** — Each responsibility = potential extraction point
> 2. **Prioritize** — Highest change frequency × lowest test coverage = pricing
> 3. **Characterize pricing** — 20 scenarios covering discounts, taxes, tiers, edge cases
> 4. **Break deps** — Parameterize `PricingEngine`, `InventoryClient`, `ShippingClient`
> 5. **Sprout Class** — Extract `PricingService` (tested); `OrderService` delegates
> 6. **Repeat** for inventory → shipping → notifications
> 7. **Returns:** 4-phase plan, characterization test suites per phase, dependency breaking diffs, verification gates

## Common Pitfalls

1. **Writing unit tests instead of characterization tests** — Unit tests assert *expected* behavior. Characterization tests assert *actual* behavior. If you write unit tests on legacy code, you'll either fail (bugs) or encode bugs as "correct."
2. **Breaking dependencies *before* characterization tests** — You'll change behavior silently. Tests first, then break deps.
3. **Trying to test everything at once** — Characterize only the **change point + its immediate dependencies**. Expand incrementally.
4. **Sprouting without tests** — The whole point of sprout/wrap is that *new code is testable*. If you sprout untested code, you've just added more legacy.
5. **Rewriting instead of sprouting** — "Let me just clean this up while I'm here" is how rewrites start. Feathers: *never rewrite; sprout and wrap.*
6. **Ignoring the "compile barrier"** — In static languages, you may need to extract interfaces *before* you can write tests. That's fine — do the minimum seam work to compile the test, then characterize.

## Verification Checklist

- [ ] Change point identified and scoped
- [ ] Seams mapped for change point + dependencies
- [ ] Characterization tests cover change point (happy + edge + error paths)
- [ ] Tests pass *before* any dependency breaking
- [ ] Dependency breaking techniques documented (which, where, why)
- [ ] New behavior added via sprout/wrap (not modification of legacy)
- [ ] New code has unit tests (not just characterization)
- [ ] Legacy code unchanged except for seam creation + delegation calls
- [ ] Rollback plan: revert seam changes + characterization tests remain
- [ ] Output includes: seam diff, test files, new classes/methods, integration steps

## One-Shot Recipes

### Recipe: Emergency Hotfix in Legacy
```
Use working-with-legacy-code skill for emergency fix in [file/function].
Constraint: deploy in 2 hours, zero test coverage.
Approach: minimal seam (parameterize method), 3 characterization tests (happy, error, fix case), sprout fix method, deploy.
Output: minimal diff, test evidence, rollback = revert parameterization.
```

### Recipe: Legacy Module Strangler Fig
```
Use working-with-legacy-code skill to plan strangler fig for [legacy module].
Target: incrementally replace with [new architecture].
Phases: 1) characterize module boundary 2) create facade seam 3) sprout new implementation behind facade 4) shift traffic 5) delete legacy.
Output: phase gates, characterization suite, facade interface, migration checklist.
```

### Recipe: Test Coverage Baseline
```
Use working-with-legacy-code skill to establish characterization baseline for [service].
Scope: all public endpoints, critical domain logic.
Output: test suite with coverage report, seam inventory, technical debt register (untestable areas), priority order for next changes.
```