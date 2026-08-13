---
name: codebase-inspection
description: Use when inspecting a codebase's LOC, languages, and ratios.
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [LOC, Code Analysis, pygount, Codebase, Metrics, Repository]
    related_skills: [github-repo-management]
prerequisites:
  commands: [pygount]
---

# Codebase Inspection with pygount

Analyze repositories for lines of code, language breakdown, file counts, and code-vs-comment ratios using `pygount`.

## When to Use

- User asks for LOC (lines of code) count
- User wants a language breakdown of a repo
- User asks about codebase size or composition
- User wants code-vs-comment ratios
- General "how big is this repo" questions
- User asks to investigate/internalize a project and decide whether it needs agent-facing docs such as `CODEX.md`, `AGENTS.md`, `CLAUDE.md`, a docs index, or canonical rules

## Prerequisites

```bash
pip install --break-system-packages pygount 2>/dev/null || pip install pygount
```

## 1. Basic Summary (Most Common)

Get a full language breakdown with file counts, code lines, and comment lines:

```bash
cd /path/to/repo
pygount --format=summary \
  --folders-to-skip=".git,node_modules,venv,.venv,__pycache__,.cache,dist,build,.next,.tox,.eggs,*.egg-info" \
  .
```

**IMPORTANT:** Always use `--folders-to-skip` to exclude dependency/build directories, otherwise pygount will crawl them and take a very long time or hang.

## 2. Common Folder Exclusions

Adjust based on the project type:

```bash
# Python projects
--folders-to-skip=".git,venv,.venv,__pycache__,.cache,dist,build,.tox,.eggs,.mypy_cache"

# JavaScript/TypeScript projects
--folders-to-skip=".git,node_modules,dist,build,.next,.cache,.turbo,coverage"

# General catch-all
--folders-to-skip=".git,node_modules,venv,.venv,__pycache__,.cache,dist,build,.next,.tox,vendor,third_party"
```

## 3. Filter by Specific Language

```bash
# Only count Python files
pygount --suffix=py --format=summary .

# Only count Python and YAML
pygount --suffix=py,yaml,yml --format=summary .
```

## 4. Detailed File-by-File Output

```bash
# Default format shows per-file breakdown
pygount --folders-to-skip=".git,node_modules,venv" .

# Sort by code lines (pipe through sort)
pygount --folders-to-skip=".git,node_modules,venv" . | sort -t$'\t' -k1 -nr | head -20
```

## 5. Output Formats

```bash
# Summary table (default recommendation)
pygount --format=summary .

# JSON output for programmatic use
pygount --format=json .

# Pipe-friendly: Language, file count, code, docs, empty, string
pygount --format=summary . 2>/dev/null
```

## 6. Interpreting Results

The summary table columns:
- **Language** — detected programming language
- **Files** — number of files of that language
- **Code** — lines of actual code (executable/declarative)
- **Comment** — lines that are comments or documentation
- **%** — percentage of total

Special pseudo-languages:
- `__empty__` — empty files
- `__binary__` — binary files (images, compiled, etc.)
- `__generated__` — auto-generated files (detected heuristically)
- `__duplicate__` — files with identical content
- `__unknown__` — unrecognized file types

## 7. Documentation Internalization + Agent Docs Assessment

When the user asks to investigate a project and internalize its docs:

1. Map the docs corpus first: top-level markdown, `docs/`, agent docs (`AGENT.md`, `CODEX.md`, `AGENTS.md`, `CLAUDE.md`), README, and generated/runtime folders.
2. Read the docs in an order that exposes purpose before details: overview/README → role or agent prompt → strategy/spec docs → parameters/config → examples/logs → implementation files.
3. Identify rule drift explicitly: conflicting thresholds, role boundaries, generated-file ownership, and canonical-vs-example differences.
4. When the user corrects canon, immediately update the project docs to encode it in a single source of truth rather than leaving the correction only in chat.
5. For projects with substantial docs and agent workflows, consider recommending or creating:
   - `CODEX.md` for coding-agent/repo-operations guidance;
   - `docs/INDEX.md` for reading order;
   - `docs/canonical-rules.md` or equivalent for project rules and role boundaries.
6. After doc edits, search for stale language across markdown (`200 shares`, hard-coded caps, obsolete thresholds, role-boundary phrases, etc.) and patch all remaining contradictions.
7. Verify the project still builds or renders if docs are consumed by an app; documentation changes can break bundled markdown imports.
8. For a worked pattern, see `references/agent-docs-canonicalization.md`.

## Pitfalls

1. **Always exclude .git, node_modules, venv** — without `--folders-to-skip`, pygount will crawl everything and may take minutes or hang on large dependency trees.
2. **Markdown shows 0 code lines** — pygount classifies all Markdown content as comments, not code. This is expected behavior.
3. **JSON files show low code counts** — pygount may count JSON lines conservatively. For accurate JSON line counts, use `wc -l` directly.
4. **Large monorepos** — for very large repos, consider using `--suffix` to target specific languages rather than scanning everything.
5. **Do not treat examples as canon after the user corrects the rule.** Update the canonical project doc and then remove stale contradictory language elsewhere.
6. **Do not leave agent-role boundaries implicit.** If a project uses bots, scripts, and analysis agents, document who owns static screening, dynamic screening, execution, and post-hoc analysis.
