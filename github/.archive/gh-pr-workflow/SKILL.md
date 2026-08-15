---
name: gh-pr-workflow
description: Use when complete guide for managing the PR lifecycle. Each section shows the gh way first, then the git + cur
version: 1.1.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [GitHub, Pull-Requests, CI/CD, Git, Automation, Merge]
    related_skills: [github-auth, github-code-review]
---

# GitHub Pull Request Workflow

Complete guide for managing the PR lifecycle. Each section shows the `gh` way first, then the `git` + `curl` fallback for machines without `gh`.

## Prerequisites

- Authenticated with GitHub (see `github-auth` skill)
- Inside a git repository with a GitHub remote

### Quick Auth Detection

```bash
# Determine which method to use throughout this workflow
if command -v gh &>/dev/null && gh auth status &>/dev/null; then
  AUTH="gh"
else
  AUTH="git"
  # Ensure we have a token for API calls
  if [ -z "$GITHUB_TOKEN" ]; then
    if _hermes_env="${HERMES_HOME:-$HOME/.hermes}/.env"; [ -f "$_hermes_env" ] && grep -q "^GITHUB_TOKEN=" "$_hermes_env"; then
      GITHUB_TOKEN=$(grep "^GITHUB_TOKEN=" "$_hermes_env" | head -1 | cut -d= -f2 | tr -d '\n\r')
    elif grep -q "github.com" ~/.git-credentials 2>/dev/null; then
      GITHUB_TOKEN=$(grep "github.com" ~/.git-credentials 2>/dev/null | head -1 | sed 's|https://[^:]*:\([^@]*\)@.*|\1|')
    fi
  fi
fi
echo "Using: $AUTH"
```

### Extracting Owner/Repo from the Git Remote

Many `curl` commands need `owner/repo`. Extract it from the git remote:

```bash
# Works for both HTTPS and SSH remote URLs
REMOTE_URL=$(git remote get-url origin)
OWNER_REPO=$(echo "$REMOTE_URL" | sed -E 's|.*github\.com[:/]||; s|\.git$||')
OWNER=$(echo "$OWNER_REPO" | cut -d/ -f1)
REPO=$(echo "$OWNER_REPO" | cut -d/ -f2)
echo "Owner: $OWNER, Repo: $REPO"
```

---

## 1. Branch Creation

This part is pure `git` — identical either way:

```bash
# Make sure you're up to date
git fetch origin
git checkout main && git pull origin main

# Create and switch to a new branch
git checkout -b feat/add-user-authentication
```

Branch naming conventions:
- `feat/description` — new features
- `fix/description` — bug fixes
- `refactor/description` — code restructuring
- `docs/description` — documentation
- `ci/description` — CI/CD changes

## 2. Making Commits

Use the agent's file tools (`write_file`, `patch`) to make changes, then commit:

```bash
# Stage specific files
git add src/auth.py src/models/user.py tests/test_auth.py

# Commit with a conventional commit message
git commit -m "feat: add JWT-based user authentication

- Add login/register endpoints
- Add User model with password hashing
- Add auth middleware for protected routes
- Add unit tests for auth flow"
```

Commit message format (Conventional Commits):
```
type(scope): short description

Longer explanation if needed. Wrap at 72 characters.
```

Types: `feat`, `fix`, `refactor`, `docs`, `test`, `ci`, `chore`, `perf`

### Artifact hygiene before push

Before you push or open the PR, check for generated junk that should not land in git — especially on tiny bootstrap branches where one stray file pollutes the whole review.

**WSL/Windows pitfall:** if the repo lives in WSL but the current Hermes workspace is on the Windows side, do not use `write_file` with Linux absolute paths like `/home/...` for repo edits. They can resolve under `C:\\home\\...` instead of the WSL repo. For WSL repos, write from inside WSL (for example via `terminal` + a quoted heredoc/Python writer) or operate from a workspace path the file tool can actually see.

**Safer cross-WSL authoring pattern:** for large YAML / markdown / PR-body files, write to an **explicit Windows temp path** (for example `C:\\Users\\<user>\\temp\\...`), copy that file into the WSL repo, and inspect the copied in-repo file before running it. Avoid relative `write_file` temp paths in cross-workspace sessions — they can land in the wrong Windows workspace and silently corrupt later copy steps. See `references/wsl-workflow-automation.md`.

```bash
# Review exactly what will be committed
git status --short

# Common Python junk to catch early
find . -type d \( -name '__pycache__' -o -name '.pytest_cache' \) -prune -print
find . -type f \( -name '*.pyc' -o -name '*.pyo' \) -print
```

If any of those appear, add a minimal `.gitignore`, remove the tracked artifacts, rerun the verification command, and amend or follow up with a cleanup commit before asking for review.

```bash
printf "__pycache__/\n*.py[cod]\n.pytest_cache/\n" > .gitignore
rm -rf **/__pycache__ .pytest_cache 2>/dev/null || true
git rm -r --cached . 2>/dev/null || true
git add .gitignore
```

Rule: a bootstrap PR should contain source, docs, and deliberate config only — never interpreter cache files.

## 3. Pushing and Creating a PR

### Windows shell routing and false-blocker guard

On this Hermes Windows host, `terminal()` runs through bash/MSYS by default. If the user explicitly asks to run the GitHub flow **in PowerShell**, keep the repo work in the same directory but wrap the Git/GitHub commands with `powershell.exe -NoProfile -Command "..."` rather than arguing with the shell choice.

Example pattern:

```bash
cd /c/Users/<user>/path/to/repo && powershell.exe -NoProfile -Command "
git status --short
git push -u origin HEAD
gh pr create --base main --head $(git branch --show-current)
"
```

Do **not** infer a repo-level blocker from `git rev-parse --abbrev-ref --symbolic-full-name @{u}` failing on the current branch. That only means the branch has no upstream yet. Before claiming "no remote", "no target branch", or "cannot open PR", separately verify all three:

```bash
git remote -v
git branch -a
gh auth status
```

Interpretation rule:
- missing branch upstream != missing `origin`
- missing current-branch upstream != missing `main`
- a push-created upstream branch is the normal precursor to `gh pr create`

### Push the Branch (same either way)

Before pushing, explicitly confirm WHICH repo you are in and which remote you are targeting when the session touched more than one git repo (for example, an app repo plus a plugin/tooling repo). State the repo path and branch in the closeout so you do not accidentally report a branch from repo A as if it belonged to repo B.

```bash
git status --short --branch
git remote -v
```

Then push:

```bash
git push -u origin HEAD
```

### Read-only upstream via `gh`: fork and continue, do not stall

If `gh auth status` is valid but the upstream repo only grants `READ` / no push permission, do **not** stop at `git push` failure. Continue with the normal contributor flow:

```bash
# verify what repo gh sees and your permission level
gh repo view --json nameWithOwner,viewerPermission,url

# create or reuse your fork
# if the fork already exists, this is harmless to check first via gh repo view <your-user>/<repo>
gh repo fork --remote --remote-name my-fork --clone=false

# if gh created the fork on GitHub but did not wire a git remote locally, add it yourself
git remote get-url my-fork >/dev/null 2>&1 || \
  git remote add my-fork https://github.com/<your-user>/<repo>.git

# push your branch to the fork
git push -u my-fork HEAD

# open the PR back to upstream
gh pr create --repo <upstream-owner>/<repo> --head <your-user>:<branch> --base main
```

Rule: successful `gh` login is not the same thing as upstream write access. When upstream is read-only, the winning path is **fork → push to fork → PR to upstream**.

### Create the PR

**With gh:**

```bash
gh pr create \
  --title "feat: add JWT-based user authentication" \
  --body "## Summary
- Adds login and register API endpoints
- JWT token generation and validation

## Test Plan
- [ ] Unit tests pass

Closes #42"
```

Options: `--draft`, `--reviewer user1,user2`, `--label "enhancement"`, `--base develop`

**With git + curl:**

```bash
BRANCH=$(git branch --show-current)

curl -s -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/repos/$OWNER/$REPO/pulls \
  -d "{
    \"title\": \"feat: add JWT-based user authentication\",
    \"body\": \"## Summary\nAdds login and register API endpoints.\n\nCloses #42\",
    \"head\": \"$BRANCH\",
    \"base\": \"main\"
  }"
```

The response JSON includes the PR `number` — save it for later commands.

To create as a draft, add `"draft": true` to the JSON body.

## 4. Monitoring CI Status

### Check CI Status

**With gh:**

```bash
# One-shot check
gh pr checks

# Watch until all checks finish (polls every 10s)
gh pr checks --watch
```

**With git + curl:**

```bash
# Get the latest commit SHA on the current branch
SHA=$(git rev-parse HEAD)

# Query the combined status
curl -s \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/commits/$SHA/status \
  | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(f\"Overall: {data['state']}\")
for s in data.get('statuses', []):
    print(f\"  {s['context']}: {s['state']} - {s.get('description', '')}\")"

# Also check GitHub Actions check runs (separate endpoint)
curl -s \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/commits/$SHA/check-runs \
  | python3 -c "
import sys, json
data = json.load(sys.stdin)
for cr in data.get('check_runs', []):
    print(f\"  {cr['name']}: {cr['status']} / {cr['conclusion'] or 'pending'}\")"
```

### Poll Until Complete (git + curl)

```bash
# Simple polling loop — check every 30 seconds, up to 10 minutes
SHA=$(git rev-parse HEAD)
for i in $(seq 1 20); do
  STATUS=$(curl -s \
    -H "Authorization: token $GITHUB_TOKEN" \
    https://api.github.com/repos/$OWNER/$REPO/commits/$SHA/status \
    | python3 -c "import sys,json; print(json.load(sys.stdin)['state'])")
  echo "Check $i: $STATUS"
  if [ "$STATUS" = "success" ] || [ "$STATUS" = "failure" ] || [ "$STATUS" = "error" ]; then
    break
  fi
  sleep 30
done
```

## 5. Auto-Fixing CI Failures

When CI fails, diagnose and fix. This loop works with either auth method.

### Step 1: Get Failure Details

**With gh:**

```bash
# List recent workflow runs on this branch
gh run list --branch $(git branch --show-current) --limit 5

# View failed logs
gh run view <RUN_ID> --log-failed
```

**With git + curl:**

```bash
BRANCH=$(git branch --show-current)

# List workflow runs on this branch
curl -s \
  -H "Authorization: token $GITHUB_TOKEN" \
  "https://api.github.com/repos/$OWNER/$REPO/actions/runs?branch=$BRANCH&per_page=5" \
  | python3 -c "
import sys, json
runs = json.load(sys.stdin)['workflow_runs']
for r in runs:
    print(f\"Run {r['id']}: {r['name']} - {r['conclusion'] or r['status']}\")"

# Get failed job logs (download as zip, extract, read)
RUN_ID=<run_id>
curl -s -L \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/actions/runs/$RUN_ID/logs \
  -o /tmp/ci-logs.zip
cd /tmp && unzip -o ci-logs.zip -d ci-logs && cat ci-logs/*.txt
```

### Step 2: Fix and Push

After identifying the issue, use file tools (`patch`, `write_file`) to fix it:

```bash
git add <fixed_files>
git commit -m "fix: resolve CI failure in <check_name>"
git push
```

### Step 3: Verify

Re-check CI status using the commands from Section 4 above.

### Auto-Fix Loop Pattern

When asked to auto-fix CI, follow this loop:

1. Check CI status → identify failures
2. Read failure logs → understand the error
3. Use `read_file` + `patch`/`write_file` → fix the code
4. `git add . && git commit -m "fix: ..." && git push`
5. Wait for CI → re-check status
6. Repeat if still failing (up to 3 attempts, then ask the user)

### Workflow / automation verification addendum

When the PR lifecycle is being exercised through a workflow engine or scripted node runner, do not treat partial node success as proof that the PR flow is complete.

Required verification:
1. Capture the workflow run id.
2. Advance/poll until the run reaches a **terminal** state (`completed` or `failed`).

## Continuation and cleanup

- Treat repository work as incomplete at `PR opened` stage when the active goal is to finish the branch flow and merge is safe. If the PR is open, checks are green, GitHub reports a clean merge state, and there is no user instruction to hold, continue through `merge -> sync main -> cleanup` autonomously.
- After merge, verify the final state explicitly: confirm the PR is `MERGED`, confirm the current branch is `main`, and confirm `git status --short` is empty.
- Cleanup includes removing throwaway artifacts created during the branch flow: temporary PR-body markdown files, one-off plan files whose work is complete, and scratch temp folders used only for handoff or automation.
- Branch cleanup can be partially pre-done by GitHub or earlier commands. If local branch deletion reports `branch not found` after a successful merge/sync, treat that as a non-blocking cleanup confirmation, not a workflow failure.
3. Verify the external side-effects directly: current branch, pushed commit/remote branch, and PR URL via `gh pr view` / `gh pr list`.
4. If `gh pr create` fails inside the workflow environment with `unable to find git executable in PATH`, export `PATH` + `GIT_EXEC_PATH` from the discovered git binary before retrying. See `references/wsl-workflow-automation.md`.

## 6. Merging

**With gh:**

```bash
# Squash merge + delete branch (cleanest for feature branches)
gh pr merge --squash --delete-branch

# Enable auto-merge (merges when all checks pass)
gh pr merge --auto --squash --delete-branch
```

**With git + curl:**

```bash
PR_NUMBER=<number>

# Merge the PR via API (squash)
curl -s -X PUT \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/pulls/$PR_NUMBER/merge \
  -d "{
    \"merge_method\": \"squash\",
    \"commit_title\": \"feat: add user authentication (#$PR_NUMBER)\"
  }"

# Delete the remote branch after merge
BRANCH=$(git branch --show-current)
git push origin --delete $BRANCH

# Switch back to main locally
git checkout main && git pull origin main
git branch -d $BRANCH
```

Merge methods: `"merge"` (merge commit), `"squash"`, `"rebase"`

### Enable Auto-Merge (curl)

```bash
# Auto-merge requires the repo to have it enabled in settings.
# This uses the GraphQL API since REST doesn't support auto-merge.
PR_NODE_ID=$(curl -s \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/pulls/$PR_NUMBER \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['node_id'])")

curl -s -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/graphql \
  -d "{\"query\": \"mutation { enablePullRequestAutoMerge(input: {pullRequestId: \\\"$PR_NODE_ID\\\", mergeMethod: SQUASH}) { clientMutationId } }\"}"
```

## 7. Complete Workflow Example

```bash
# 1. Start from clean main
git checkout main && git pull origin main

# 2. Branch
git checkout -b fix/login-redirect-bug

# 3. (Agent makes code changes with file tools)

# 4. Commit
git add src/auth/login.py tests/test_login.py
git commit -m "fix: correct redirect URL after login

Preserves the ?next= parameter instead of always redirecting to /dashboard."

# 5. Push
git push -u origin HEAD

# 6. Create PR (picks gh or curl based on what's available)
# ... (see Section 3)

# 7. Monitor CI (see Section 4)

# 8. Merge when green (see Section 6)
```

## Useful PR Commands Reference

| Action | gh | git + curl |
|--------|-----|-----------|
| List my PRs | `gh pr list --author @me` | `curl -s -H "Authorization: token $GITHUB_TOKEN" "https://api.github.com/repos/$OWNER/$REPO/pulls?state=open"` |
| View PR diff | `gh pr diff` | `git diff main...HEAD` (local) or `curl -H "Accept: application/vnd.github.diff" ...` |
| Add comment | `gh pr comment N --body "..."` | `curl -X POST .../issues/N/comments -d '{"body":"..."}'` |
| Request review | `gh pr edit N --add-reviewer user` | `curl -X POST .../pulls/N/requested_reviewers -d '{"reviewers":["user"]}'` |
| Close PR | `gh pr close N` | `curl -X PATCH .../pulls/N -d '{"state":"closed"}'` |
| Check out someone's PR | `gh pr checkout N` | `git fetch origin pull/N/head:pr-N && git checkout pr-N` |
