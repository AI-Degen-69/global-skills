---
name: context-engineering-agent-skills
description: Use when agent output quality drops, starting a new session, switching tasks, or when sources conflict and the
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [context-engineering, context-hierarchy, confusion-block, token-optimization, source-conflict]
    related_skills: [source-driven-development, doubt-driven-development, ce-brainstorm, ce-plan, systematic-debugging]
---

# Context Engineering (Agent Skills Version)

## Overview

**Context Engineering** is the discipline of feeding agents the right information at the right time — in a strict hierarchy — so they make grounded decisions instead of hallucinating. This skill implements the 5-level hierarchy from Addy Osmani's `agent-skills` repo, with the standout rule: **when sources conflict, the agent cannot silently pick one — it must stop and show a structured confusion block.**

This addresses the #1 failure mode Bitwise AI identified: "agents mostly fail from wrong context, not low intelligence."

## When to Use

- Starting a new session or major task
- Switching between tasks/projects
- Agent output quality degrades (hallucinations, wrong assumptions, missed constraints)
- Multiple sources conflict and agent would otherwise pick arbitrarily
- Token budget is tight and context must be packed efficiently
- Onboarding agents to a new codebase or domain

Don't use for:
- Trivial, single-file edits with clear scope
- Exploratory research (cast wide net instead)
- When context is already optimal and stable

## The 5-Level Context Hierarchy

Load in order — each level supersedes the previous on conflicts:

```text
LEVEL 1: RULES (highest authority)
├── AGENTS.md / CLAUDE.md / CURSOR.md / .cursorrules
├── vault-guide.md, STANDARDS.md, CONSTITUTION.md
├── Project-specific guardrails (hooks, lint configs)
└── Non-negotiable policies (security, compliance, licensing)

LEVEL 2: FILES (codebase reality)
├── Relevant source files (read, don't guess)
├── Config files (package.json, pyproject.toml, Cargo.toml)
├── Schema definitions (Types/, OpenAPI, GraphQL)
└── Test files (show expected behavior)

LEVEL 3: SPECS (intent)
├── STRATEGY.md (ce-strategy)
├── PRDs / specs from ce-brainstorm / ce-plan
├── ADRs (architecture decision records)
└── Design docs, RFCs

LEVEL 4: RELEVANT SOURCE (external truth)
├── Official documentation (version-pinned URLs)
├── Language/framework reference (not tutorials)
├── Standards specs (RFC, W3C, ECMA)
└── Verified examples from trusted repos

LEVEL 5: ERROR OUTPUT (runtime reality)
├── Test failures (full trace, not summary)
├── Build errors (exact compiler output)
├── Runtime logs (structured, not grep summaries)
└── Linter/type checker output

LEVEL 6: CONVERSATION (lowest authority)
├── Current session history
├── User preferences stated in chat
└── Prior agent outputs (treat as claims, not truth)
```

**Priority rule:** If Level 1 says X and Level 4 says Y → Level 1 wins. If Level 3 and Level 4 conflict → STOP, show confusion block.

## The Structured Confusion Block (Standout Rule)

When sources at the same or adjacent hierarchy levels conflict, the agent **must not silently pick one**. Instead:

```markdown
## ⚠️ CONTEXT CONFLICT — Agent Cannot Resolve

**Conflict:** [What contradicts what]

| Source A (Level N) | Source B (Level M) |
|--------------------|--------------------|
| Claim: [exact quote] | Claim: [exact quote] |
| Source: [file/URL]   | Source: [file/URL]   |
| Authority: [why weight] | Authority: [why weight] |

**Options:**
- **A)** [Follow Source A — rationale]
- **B)** [Follow Source B — rationale]
- **C)** [Hybrid / defer to human — rationale]

**Recommendation:** [Agent's best judgment with confidence %]

**Required:** Human must choose A, B, C, or provide D before agent proceeds.
```

This block is **rendered to the user** — the agent pauses and waits for explicit direction.

## Context Packing Strategy (Token Optimization)

When token budget is constrained, pack in hierarchy order — never drop Level 1:

| Budget | Strategy |
|--------|----------|
| Full | All 6 levels, full files |
| Medium | L1 rules (full) + L2-L3 (relevant sections) + L4 (pinned URLs) + L5 (errors only) + L6 (last 3 turns) |
| Tight | L1 rules (condensed) + L2 (changed files only) + L3 (active spec only) + L4 (1-2 key URLs) + L5 (blocking errors only) |
| Critical | L1 (non-negotiables only) + L5 (blocking error) |

**Never drop:** Security rules, compliance constraints, explicit user directives.

## Workflow

### Step 1: Assess Current Context

```python
# Quick audit
current_levels = {
    "rules": "loaded?" (AGENTS.md, vault-guide.md, etc.),
    "files": "which files read?",
    "specs": "STRATEGY.md / PRD loaded?",
    "source": "official docs URLs pinned?",
    "errors": "latest test/build failures?",
    "conversation": "turn count, key decisions"
}
```

### Step 2: Load Missing Levels (in hierarchy order)

```bash
# Example: Starting new feature task
# 1. Rules (always)
read AGENTS.md
read vault-guide.md
read STANDARDS.md

# 2. Files
read relevant module files (use search_files, not guess)
read config files
read test files for patterns

# 3. Specs
read STRATEGY.md
read relevant PRD/ADR

# 4. Source
fetch official docs for framework version in package.json
pin URLs in claim comments

# 5. Errors
run tests → capture failures
run lint/typecheck → capture output
```

### Step 3: Detect Conflicts

Before any decision, scan for:
- Rules vs. source docs
- Spec vs. existing code behavior
- Different official sources (e.g., two RFCs)
- Conversation history vs. current rules

### Step 4: On Conflict → Emit Confusion Block

Do not proceed. Render block. Wait for user.

### Step 5: Proceed with Chosen Resolution

Record decision in context log for future sessions.

## Integration with Hermes / CE Loop

| Skill | Integration |
|-------|-------------|
| `ce-brainstorm` | Load L1-L3 before interview; L4 for domain research |
| `ce-plan` | L1-L3 as planning context; L5 for verifying task breakdown |
| `ce-work` | Each subagent gets packed context per hierarchy |
| `source-driven-development` | L4 is its primary domain; L1 constrains it |
| `doubt-driven-development` | Reviewer gets fresh context = L1-L5 only (no L6 bias) |
| `ce-code-review` | Reviewers get L1-L5; confusion blocks on standard violations |

**Hermes context packing:**
```python
def pack_context(task, budget="medium"):
    context = []
    # Level 1: Always
    context += load_rules()
    # Level 2: Relevant files
    context += load_relevant_files(task)
    # Level 3: Active spec
    context += load_active_spec()
    # Level 4: Pinned sources
    context += load_pinned_sources(task)
    # Level 5: Blocking errors
    context += load_blocking_errors()
    # Level 6: Trimmed conversation
    if budget != "critical":
        context += load_recent_conversation(turns=3)
    return truncate_to_budget(context, budget)
```

## Common Pitfalls

1. **Loading everything at once** — Poisons context window; use progressive disclosure
2. **Dropping Level 1 under pressure** — Security/compliance rules are non-negotiable
3. **Treating conversation as truth** — L6 is lowest authority; prior agent claims need verification
4. **Silently resolving conflicts** — The #1 cause of subtle bugs; emit confusion block
5. **Using tutorials as Level 4** — Only official docs, standards specs, verified examples
6. **Not pinning versions** — "Latest docs" ≠ your version; fetch exact version from lockfile
7. **Ignoring L5 (errors)** — Runtime reality trumps all documentation

## Verification Checklist

- [ ] All 6 hierarchy levels assessed for current task
- [ ] Missing levels loaded in order (L1 → L6)
- [ ] Version-pinned official docs for all external dependencies
- [ ] Latest test/build errors captured (not summaries)
- [ ] Conflicts scanned before any decision
- [ ] Confusion block emitted on any conflict (no silent resolution)
- [ ] Human choice recorded for audit
- [ ] Context packed to budget without dropping L1
- [ ] Decision traceable to hierarchy level

## One-Shot Recipes

### Recipe: New Session Bootstrap
```python
# Run at session start for any non-trivial task
context = pack_context(task="new feature", budget="full")
# Verify:
assert "AGENTS.md" in context
assert "vault-guide.md" in context
assert latest_test_failures in context
assert pinned_docs_urls in context
```

### Recipe: Conflict Detection Hook
```python
# Pre-tool-use hook for write/edit on critical files
def check_conflict(file, proposed_change):
    rules = load_rules_for(file)
    source_docs = load_official_docs_for(file)
    existing_code = read_file(file)
    
    conflicts = detect_contradictions(rules, source_docs, existing_code, proposed_change)
    if conflicts:
        emit_confusion_block(conflicts)
        return "BLOCKED — human choice required"
    return "OK"
```

### Recipe: Token-Budgeted Subagent
```python
# When spawning subagent for specific task
subagent_context = pack_context(
    task="implement auth middleware",
    budget="medium"  # subagents get tighter budget
)
# L1 rules + changed files + active spec + pinned framework docs + errors
```

```
