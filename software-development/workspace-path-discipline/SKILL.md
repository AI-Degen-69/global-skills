---
name: workspace-path-discipline
description: Use when the user any coding session that mixes terminal commands with file tools (read_file, search_files, pa
---

# Workspace Path Discipline

## When to use
Use for any coding session that mixes terminal commands with file tools (`read_file`, `search_files`, `patch`, `write_file`) and especially when you `cd` into a repo subdirectory such as `web/`, `backend/`, `packages/*`, or a worktree.

## Why this exists
A common self-inflicted failure mode is path drift:
- the terminal has moved into a subdirectory,
- the agent keeps using repo-root-relative paths from earlier context,
- file edits then target `subdir/subdir/...` or fail with "file not found".

This is avoidable and should be treated as execution sloppiness, not bad luck.

## Core rule
Before any file-tool call after changing directories in terminal, explicitly re-anchor the path mentally:
1. What directory is the current session effectively operating from?
2. Is this file-tool path repo-root-relative or current-subdir-relative?
3. Would prepending the subdirectory duplicate part of the path?

If there is any doubt, inspect first and then edit.

## Operating procedure
1. **Start from the project anchor**
   - Read `AGENTS.md`, then required context files.
   - Identify whether the repo convention assumes root-relative paths in discussion.
2. **Notice every directory change**
   - Treat `cd web`, `cd backend`, entering a worktree, or switching project roots as a context change that can invalidate later path assumptions.
3. **Before the first file edit after a directory change**
   - Re-state the target path in the form the tool will actually resolve.
   - Prefer a quick read/search on that exact path before patching if the path has changed since the last successful edit.
4. **If a file-tool path fails once**
   - Stop repeating the same call.
   - Infer whether the failure implies duplicated path segments (`web/web/src/...`) or missing root segments.
   - Retry with the corrected anchor, not the same stale path.
5. **If terminal commands are being run from a subdirectory**
   - Keep terminal verification there when appropriate, but do not blindly copy those paths into file-tool calls without checking resolution.
6. **Close the loop with verification**
   - After path corrections, run the relevant verification command from the intended directory and confirm the edited file is part of the changed set.

## Pitfalls
- **Duplicated subdirectory prefix**: editing `web/src/...` after the effective workspace is already `web/` produces `web/web/src/...`.
- **Half-switched context**: terminal is in a package directory while `read_file`/`patch` calls still assume repo root.
- **Looping on stale paths**: retrying the same failed patch call twice instead of re-anchoring.
- **False blame**: treating a path-resolution mistake as a tool bug.

## Recovery pattern
When a path call fails:
1. Read the failure path literally.
2. Compare it to the intended repo location.
3. Remove the duplicated segment or add the missing anchor.
4. Re-read or patch using the corrected path.
5. Verify via changed-file list or build/test output.

## Verification checklist
- The file-tool path resolves on the first retry after correction.
- The edited file appears in the intended changed-file set.
- Build/test output reflects the expected file location.

## Support files
- `references/path-drift-example.md` — concrete example of the duplicated-subdirectory failure mode and the correction pattern.