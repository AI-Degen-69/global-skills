---
name: gh-operations
description: Use when running the GitHub operations umbrella (auth, repo, issues, PR).
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [GitHub, git, pull-requests, issues, code-review, repositories, auth]
    related_skills: [codebase-inspection]
---

# GitHub Operations

Class-level umbrella for GitHub work. Use this instead of hunting for separate micro-skills when the job touches any part of the repo/issue/PR lifecycle.

## When to use
- GitHub authentication or `gh` setup
- Cloning, creating, forking, or configuring repos
- Creating, triaging, or closing issues
- Branching, pushing, opening PRs, watching CI, and merging
- Reviewing local diffs or open PRs

## Decision order
1. **Auth first** — determine whether `gh` is installed/authenticated or whether you need `git + curl`.
2. **Identify repo context** — extract `OWNER/REPO` from the remote before API calls.
3. **Pick the workflow lane** — repo management, issue ops, PR lifecycle, or review.
4. **Prefer `gh` when available**; fall back to `curl` with `GITHUB_TOKEN` when not.

## Subsections

### 1. Authentication
- PAT + credential helper, SSH keys, and `gh auth login`
- Use `scripts/gh-env.sh` for reusable environment bootstrapping
- Verify with `gh auth status` or a token-backed API probe

### 2. Repository management
- Clone, create, fork, sync remotes, edit settings, manage releases and Actions
- Use `references/repo-management-api-cheatsheet.md`

### 3. Issue operations
- Create, triage, label, assign, comment, close, and bulk-filter issues
- Use `templates/issue-bug-report.md` and `templates/issue-feature-request.md`

### 4. PR lifecycle
- Branch, commit, push, open PRs, monitor checks, diagnose CI, merge, and clean up
- Reuse `templates/pr-body-feature.md` and `templates/pr-body-bugfix.md`
- See `references/ci-troubleshooting.md` and `references/conventional-commits.md`

### 5. Code review
- Review local diffs before push or review an existing GitHub PR with inline comments
- Use `references/review-output-template.md` for summary structure
- For your own changes before commit, also consider broader local verification skills

## Support files in this umbrella
- `scripts/gh-env.sh`
- `references/repo-management-api-cheatsheet.md`
- `references/ci-troubleshooting.md`
- `references/conventional-commits.md`
- `references/review-output-template.md`
- `templates/issue-bug-report.md`
- `templates/issue-feature-request.md`
- `templates/pr-body-feature.md`
- `templates/pr-body-bugfix.md`

## Keep separate
- `codebase-inspection` stays separate because LOC/language-analysis is codebase metrics work, not core GitHub workflow.

## Verification
- Auth verified with `gh auth status` or API call
- Repo target confirmed from `git remote get-url origin`
- Side effects verified with returned PR/issue/release IDs or URLs

## Windows clone fallback
`git clone` from GitHub can sometimes produce an empty target directory with no working tree. If `git clone` leaves a directory without source files, treat it as a failed checkout and use the archive fallback instead of retrying clone. Preferred path:
1. Download the archive: `GITHUB_HOST=github.com curl -L "https://github.com/<owner>/<repo>/archive/refs/heads/<branch>.tar.gz" -o <repo>.tar.gz`
2. Extract: `tar -xzf <repo>.tar.gz`
3. Replace the failed clone directory with the extracted tree, then remove the archive.
4. Verify with a quick listing that the source files exist before proceeding.
