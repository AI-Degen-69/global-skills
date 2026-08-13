---
name: todoist-cli-operations
description: Use when the user wants task reads/writes, Todoist setup, or Todoist as the system of record
---

# Todoist CLI operations

## When to use
- User says Todoist is their task manager
- User wants tasks read, added, closed, modified, filtered, or projects inspected
- User wants the Todoist CLI connected or reconnected

## Core rules
1. Treat Todoist as the task system of record for task-management requests.
2. Before trusting IDs or task state, run `todoist sync` when reading live state or after auth/config changes.
3. Prefer filtered reads over dumping the full list. Use Todoist filter syntax to narrow scope.
4. Before overwriting auth config, create a recovery handle by backing up the current config file.
5. Verification is not "config written". Verification requires successful live CLI reads such as `todoist projects` and `todoist list`.

## Standard workflow
1. Confirm the CLI exists and responds to `--help` if setup state is unknown.
2. Locate the config file and back it up before editing.
3. Write or update the API token only in the Todoist CLI config.
4. Run `todoist sync`.
5. Verify with:
   - `todoist projects`
   - `todoist list --filter '(overdue | today)'`
   - fallback: `todoist list` if the filtered result is empty
6. Report the recovery handle and the verified projects/tasks found.

## Read patterns
- Due focus: `todoist list --filter '(overdue | today)'`
- Project focus: `todoist list --filter '#ProjectName'`
- Label focus: `todoist list --filter '@LabelName'`
- Priority focus: `todoist list --filter '(overdue | today) & p1'`

## Write patterns
- Add task: `todoist add "Task name" -p p1 -d "tomorrow 10:00"`
- Quick add: `todoist quick "Task name #Project @Label tomorrow"`
- Modify task: `todoist modify <task-id> ...`
- Complete task: `todoist close <task-id>`
- Delete task permanently only with explicit user intent: `todoist delete <task-id>`

## Edge cases
- IDs are alphanumeric in current Todoist CLI/API flow.
- An empty filtered list is not a failure; retry with a broader list before concluding auth is broken.
- Avoid ANSI/color flags when scraping output for agent use.

## References
- `references/windows-auth-and-verification.md` — Windows-specific config path, backup pattern, and verification sequence validated in-session.
