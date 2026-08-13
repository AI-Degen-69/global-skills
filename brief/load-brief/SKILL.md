---
name: load-brief
description: Use when starting a new session to load the most recent brief file from the canonical briefs directory, intern
---
# Load Brief Skill

## Overview
Loads the most recent brief file from `C:/Users/Tiger/AppData/Local/hermes/briefs/`, injects its content into the current session context, deletes the file after successful load, and outputs a verification message with the file path and creation timestamp.

## When to Use
- Starting a new session after a phase transition, subagent completion, or cron job
- Need to resume work from a structured brief document
- Want to ensure brief files are consumed exactly once (no stale context)

## Core Pattern

```bash
# 1. Find most recent brief file by mtime
# 2. Read and parse frontmatter + content
# 3. Inject into session context (display to user)
# 4. Delete file
# 5. Output verification: "Loaded brief: <path> (created <timestamp>) — deleted, internalized."
```

## Implementation

**Script:** `load_brief.py` (in skill directory)

```python
#!/usr/bin/env python3
"""
Load Brief — consume most recent brief file from canonical directory.
"""
import os
import sys
import glob
from pathlib import Path
from datetime import datetime

BRIEFS_DIR = Path(r"C:/Users/Tiger/AppData/Local/hermes/briefs")

def find_latest_brief():
    """Return Path to most recent .md file in briefs dir, or None."""
    files = list(BRIEFS_DIR.glob("brief-*.md"))
    if not files:
        return None
    return max(files, key=lambda p: p.stat().st_mtime)

def parse_brief(filepath):
    """Extract frontmatter and body. Returns (frontmatter_dict, body_str)."""
    content = filepath.read_text(encoding="utf-8")
    if not content.startswith("---"):
        return {}, content
    parts = content.split("---", 2)
    if len(parts) < 3:
        return {}, content
    import yaml
    frontmatter = yaml.safe_load(parts[1]) or {}
    body = parts[2].strip()
    return frontmatter, body

def main():
    latest = find_latest_brief()
    if not latest:
        print("No brief files found in canonical directory.")
        sys.exit(0)

    # Get creation time from filename timestamp or file mtime
    mtime = datetime.fromtimestamp(latest.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
    
    frontmatter, body = parse_brief(latest)
    
    # Display to user (injected into session)
    print(f"## Brief Loaded: {latest.name}")
    print(f"**File:** `{latest}`")
    print(f"**Created:** {mtime}")
    if frontmatter.get("session_id"):
        print(f"**Session ID:** {frontmatter['session_id']}")
    if frontmatter.get("trigger"):
        print(f"**Trigger:** {frontmatter['trigger']}")
    if frontmatter.get("phase_from") and frontmatter.get("phase_to"):
        print(f"**Phase:** {frontmatter['phase_from']} → {frontmatter['phase_to']}")
    print()
    print("---")
    print(body)
    print("---")
    
    # Delete after successful display
    latest.unlink()
    
    # Verification message
    print(f"✅ **Loaded and deleted:** `{latest}` (created {mtime}) — internalized, no longer on disk.")

if __name__ == "__main__":
    main()
```

## Usage
```bash
# From slash command or terminal
python C:/Users/Tiger/AppData/Local/hermes/skills/devops/load-brief/scripts/load_brief.py
```

## Verification Output Format
```
✅ Loaded and deleted: C:/Users/Tiger/AppData/Local/hermes/briefs/brief-default-statistics-p0-remediation-to-p1-primitives-20260617-1846.md (created 2026-06-17 18:09:35) — internalized, no longer on disk.
```
*Note: The verification message explicitly confirms the file has been deleted after being loaded and read, ensuring no stale context remains.*

## Common Mistakes
| Mistake | Fix |
|---------|-----|
| Running twice in same session | File deleted after first run — second run shows "No brief files found" |
| Brief dir empty | Expected — no brief to load |
| Parsing YAML frontmatter fails | Script handles gracefully, treats as plain markdown |

## Post-Load Continuation Pattern

After loading and deleting a brief, do not stop at the verification message when the body contains explicit continuation work:

1. **Run any mandatory checklist in the brief body** before claiming the brief is fully consumed. Treat checklist commands as part of the load contract, not optional follow-up.
2. **Resolve repo boundaries before installing hooks or guards.** A brief may reference files under `AppData/Local/hermes` that are not inside a git repo; locate the actual repo with `git rev-parse --show-toplevel` before writing `.git/hooks/*`.
3. **Verify preserved archives recursively.** Cleanup archives often preserve original subdirectories; check with recursive glob patterns (for example `archive.rglob("request_dump_*.json")`) rather than only the archive root.
4. **Clean idempotent-script scaffolding.** Re-running migration scripts may recreate empty temp backup directories even when they skip all work. Remove empty scaffolds after verification, but retain audit archives with manifests and payload files.
5. **Report coverage precisely.** If a hook is installed in a related repo, state what it protects and what it does not protect (for example, commits in that repo vs. direct manual edits in an external config tree).

## Red Flags
- File not deleted after load → check permissions
- No verification message → script didn't run to completion

## Disambiguation Pattern: "What are we working on now?"

When a brief resumes work in a repo that also has broader review or roadmap artifacts, do not assume the user knows which "step list" is active.

After loading the brief, if the user asks for current status before execution:

1. Identify the **active execution artifact** named by the brief (for example, the current implementation plan).
2. Identify any **broader roadmap/review artifacts** the user references (for example, architecture-review HTML, design audit, RFC, review doc).
3. State explicitly which one governs **current execution** vs which one is **background strategy / refactor roadmap**.
4. Translate both into a simple status report:
   - **what we are working on now**
   - **the goal**
   - **what is already done**
   - **what is not wired / verified yet**
5. If the same word like "step" could refer to two different artifacts, call that out directly (for example, "architecture review candidates" vs "implementation plan tasks").

This prevents immediate confusion after brief-driven context restore and gives the user a stable mental model before you run checklists or reviews.

## Cross-Reference: Create Brief (Replaces unified-handoff, 2026-06-18)

The standalone `unified-handoff` skill was renamed to `create-brief` on 2026-06-23. This skill (`load-brief`) continues to be the canonical reader for any brief file in the canonical directory, regardless of which generator wrote it.

If a brief file appears here, it was produced by `create-brief` (current) or by `unified-handoff` prior to 2026-06-23 (still consumable — same frontmatter, same body schema, same filename pattern). No special handling is required.