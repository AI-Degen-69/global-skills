# WSL repo + Windows Hermes workflow automation

Use this when Hermes is running from a Windows workspace but the target git repo lives in WSL.

## Safer file-authoring pattern
- For large YAML / markdown / PR-body files, prefer `write_file` to an **explicit Windows temp path** such as `C:\Users\Tiger\temp\...`.
- Then copy that file into the WSL repo with `wsl.exe` / `cp`.
- Immediately inspect the copied in-repo file before running it.

Why: nested quoting through `wsl.exe bash -lc` is fragile for multiline YAML, heredocs, and shell-heavy workflow specs.

## Relative-path pitfall
- Do not assume `write_file(path='temp/...')` lands near the WSL repo.
- In cross-workspace sessions, relative paths can resolve under an unrelated Windows workspace and silently poison later copy steps.
- Use absolute Windows paths for temp artifacts when the real target repo is in WSL.

## Workflow verification pattern
When validating an automation/workflow engine:
1. Verify the generated artifact in the repo.
2. Start the workflow and capture the run id.
3. Advance until the run reaches a **terminal** state (`completed` / `failed`), not just until one node succeeds.
4. Separately verify external side-effects: git branch, pushed commit, PR URL.

## `gh pr create` inside scripted workflow nodes
If `gh pr create` fails with `unable to find git executable in PATH` inside a workflow/script environment, export git explicitly before calling `gh`:

```bash
git_bin_dir=$(dirname "$(command -v git)")
export PATH="$git_bin_dir:$PATH"
export GIT_EXEC_PATH="$(git --exec-path)"
```

Then retry PR creation or rerun the workflow node.
