---
name: overnight-autonomous-improvement
description: Use when running overnight autonomous build-test-commit loops.
category: devops
tags: [background, overnight, autonomous, loop, notify_on_complete, hermes]
---

# Overnight Autonomous Improvement Loop

Run a background process that continuously improves a codebase overnight. Single long-running process (not cron) maintains state, accumulates logs, and delivers full output in the morning.

## When to Use

- You want a codebase to self-improve for 6-10 hours unattended
- Iteration needs continuity (shared state, accumulating data)
- Morning deliverable = complete log + git history + test results
- Free data stack preferred (no paid APIs)

## Core Pattern

```bash
# Launch (8 hours = 28800s)
# FIRST: Ensure git identity for commits (run once in repo)
git config user.email "bot@project.local"
git config user.name "Overnight Bot"

terminal(
  background=true,
  notify_on_complete=true,
  timeout=28800,
  command="cd /path/to/project && python scripts/overnight_loop.py"
)
```

## Loop Script Template

```python
#!/usr/bin/env python3
"""
Overnight improvement loop for [PROJECT].
Each iteration: collect -> build -> test -> lint -> commit.
"""
import subprocess, time, sys
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).parent.parent
LOG = ROOT / "overnight.log"
ITERATION = 0
MAX_ITERATIONS = 999

def run(cmd, cwd=None, timeout=300):
    return subprocess.run(cmd, shell=True, cwd=cwd or ROOT,
                         capture_output=True, text=True, timeout=timeout)

def log(msg):
    entry = f"[{datetime.now().isoformat()}] {msg}"
    print(entry, flush=True)
    with LOG.open("a") as f:
        f.write(entry + "\n")

def git_commit(msg):
    run("git add -A")
    result = run(f'git commit -m "{msg}"')
    if result.returncode == 0 or "nothing to commit" in result.stdout.lower():
        log(f"COMMIT: {msg}")
        return True
    log(f"COMMIT FAILED: {result.stderr}")
    return False

# ============================================================
# OPTIONAL: Multi-agent research pipeline (TradingAgents pattern)
# Analysts -> Debate -> Risk -> Trader -> Portfolio Manager
# ============================================================
def run_research_pipeline():
    """Multi-stage research: analysts -> debate -> risk -> decision"""
    log("RESEARCH: Running multi-agent pipeline...")
    
    # Stage 1: Analysts (parallel data collection)
    log("  Stage 1: Analysts collecting data...")
    # run("python -m scripts.research_engine.briefing")
    # run("python -m scripts.research_engine.collect_events")
    # run("python -m scripts.research_engine.fetch_history")
    # run("python -m scripts.research_engine.scoring")
    # run("python -m scripts.research_engine.sector_metrics")
    
    # Stage 2: Decision workflow (bull/bear debate equivalent)
    log("  Stage 2: Decision workflow (committee)...")
    # run("python -m scripts.research_engine.decision_workflow")
    
    # Stage 3: Outcomes tracking (reflection/memory)
    log("  Stage 3: Outcomes tracking...")
    # run("python -m scripts.research_engine.outcomes")

# ============================================================
# OPTIONAL: UI/UX improvements (BB-Terminal pattern)
# Workspace tabs, modular function panels, persistent layout
# ============================================================
def improve_dashboard_ui():
    """Apply BB-Terminal patterns to dashboard"""
    log("UI: Applying dashboard layout improvements...")
    # Add persistent workspace state (like BB-Terminal's workspaceStore)
    # Add modular function panels (like BB-Terminal's FunctionPanel)
    # Improve responsive grid for data display
    # Ensure terminal-style consistent theming

def iteration():
    global ITERATION
    ITERATION += 1
    log(f"=== ITERATION {ITERATION} START ===")

    # 1. DATA COLLECTION (project-specific)
    log("Running data collectors...")
    # run("python -m scripts.collector_a")
    # run("python -m scripts.collector_b")

    # 2. Multi-agent research pipeline (uncomment for projects with research engine)
    # run_research_pipeline()

    # 3. UI/UX improvements (uncomment for frontend projects)
    # improve_dashboard_ui()

    # 4. BUILD + VERIFY
    log("Building...");        run("npm run build")
    log("Typechecking...");    run("npx tsc --noEmit")
    log("Linting...");         run("npm run lint")
    log("Testing...");         run("npm test -- --run")

    # 5. COMMIT
    git_commit(f"chore: overnight iteration {ITERATION} - auto-improvement")

    log(f"=== ITERATION {ITERATION} COMPLETE ===\n")

if __name__ == "__main__":
    log("Overnight improvement loop started")
    try:
        while ITERATION < MAX_ITERATIONS:
            iteration()
            time.sleep(60)  # adjustable cadence
    except KeyboardInterrupt:
        log("Stopped by user")
    except Exception as e:
        log(f"FATAL: {e}")
        sys.exit(1)
```

## Morning Deliverable

- `overnight.log` - full timestamped trace
- Git commits - one per iteration with descriptive messages
- Test pass/fail visible in log
- Process exits cleanly -> `notify_on_complete` delivers full stdout

## Checking Progress Mid-Run

```bash
# Tail log
tail -f overnight.log

# Or via Hermes process tool
process(action="poll", session_id="proc_xxx")
```

## Pitfalls

| Pitfall | Fix |
|---------|-----|
| Cron jobs lose continuity | Use **single background process**, not cron |
| Iterator limit too low | `MAX_ITERATIONS = 999` + timeout guard |
| Silent failures | Try/except per iteration, loop continues |
| No morning notification | `notify_on_complete=true` (not `watch_patterns`) |
| Paid API dependency | Use free stack: yfinance, SEC EDGAR, Finnhub free, IBKR Flex |
| Subagent delegation in background script | Not available - use direct subprocess calls |
| **Git commits fail silently** | **Set `git config user.email/name` locally BEFORE launch (iterations 1-4 failed in session)** |
| **Research pipeline too linear** | **Use multi-agent stages: Analysts → Debate → Risk → Decision** |
| **UI improvements ad-hoc** | **Apply BB-Terminal patterns: workspace tabs, modular panels, persistent layout** |
| **Hardcoded dark bg breaks theming** | **Use semantic `bg-card` tokens, not `bg-[#0d0d14]`** |
| **Fixed max-width limits responsiveness** | **Use `max-w-full` + responsive grid (`grid-cols-1 lg:grid-cols-2 xl:grid-cols-3`)** |

| Pitfall | Fix |
|---------|-----|
| Cron jobs lose continuity | Use **single background process**, not cron |
| Iterator limit too low | `MAX_ITERATIONS = 999` + timeout guard |
| Silent failures | Try/except per iteration, loop continues |
| No morning notification | `notify_on_complete=true` (not `watch_patterns`) |
| Paid API dependency | Use free stack: yfinance, SEC EDGAR, Finnhub free, IBKR Flex |
| Subagent delegation in background script | Not available - use direct subprocess calls |
| **Git commits fail silently** | **Set `git config user.email/name` locally before launch** |
| **Research pipeline too linear** | **Use multi-agent stages: Analysts → Debate → Risk → Decision** |
| **UI improvements ad-hoc** | **Apply BB-Terminal patterns: workspace tabs, modular panels, persistent layout** |

## Northstar 2.0 Specialization

For Northstar 2.0, the collectors are:
- `scripts/seed_sp500`, `seed_qqq`, `seed_dow30`, `seed_themes`, `refresh_universes`
- `scripts.research_engine.briefing`, `collect_events`, `decision_workflow`, `fetch_history`, `scoring`, `sector_metrics`, `outcomes`

See `references/northstar2-collectors.md` for detail.

## Advanced Patterns (from session exploration)

- **Multi-agent research pipeline** (TradingAgents-inspired): Analysts → Debate → Risk → Decision → Reflection. See `references/multi-agent-research-pipeline.md`.
- **BB-Terminal UI patterns**: Workspace tabs, modular function panels, persistent layout, terminal theming. See `references/bb-terminal-ui-patterns.md`.