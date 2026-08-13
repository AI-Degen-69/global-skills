---
name: external-coding-agents
description: Use when coordinating external coding-agent CLIs (Claude Code, Codex, OpenCode).
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [coding-agent, autonomous, orchestration, claude-code, codex, opencode]
    related_skills: [hermes-agent]
---

# External Coding Agents

Umbrella skill for orchestrating third-party coding-agent CLIs from Hermes. Use this when the user wants an external agent rather than Hermes-native delegation.

## When to use
- User explicitly asks for Claude Code, Codex, or OpenCode
- Long-running coding/refactor/review work should happen in a separate agent process
- You need CLI-specific orchestration, PTY handling, or process monitoring

## Shared rules
1. Verify the binary and auth state before dispatching work.
2. Prefer one-shot non-interactive mode when the CLI supports it cleanly.
3. Use background sessions only for long-running or truly interactive work.
4. Keep each agent scoped to one repo/workdir or one isolated worktree.
5. Report concrete outcomes: changed files, tests run, review verdicts, remaining risks.

## Decision table

### Claude Code
Use when:
- Anthropic's agent is explicitly requested
- You need rich one-shot print mode (`claude -p`) or tmux-backed interactive sessions

Key pattern:
- Prefer `claude -p 'task'` for automation
- Use tmux for multi-turn interactive sessions
- Be ready for trust/permission dialogs in interactive mode

### Codex
Use when:
- OpenAI Codex CLI is explicitly requested
- The task fits `codex exec` and the repo requirement is satisfied

Key pattern:
- Always use `pty=true`
- Must run inside a git repo (or a scratch repo you initialize)
- Use background mode for long autonomous runs and monitor with `process`

### OpenCode
Use when:
- OpenCode is explicitly requested
- You want provider-agnostic agent execution with `opencode run` or interactive TUI

Key pattern:
- Prefer `opencode run 'task'` for bounded work
- Interactive mode needs `pty=true`
- Exit interactive sessions with Ctrl+C / process kill, not `/exit`

## Verification checklist
- Binary/version checked
- Auth checked
- Workdir/repo confirmed
- Command actually executed
- Result verified from logs/output, not assumed
