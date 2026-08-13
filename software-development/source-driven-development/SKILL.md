---
name: source-driven-development
description: "Use when implementing any framework, library, or API feature. Ground every decision in official documentation:"
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [source-driven, official-docs, version-pinning, citation, verification, anti-hallucination]
    related_skills: [context-engineering-agent-skills, doubt-driven-development, test-driven-development, systematic-debugging, ce-work]
---

# Source-Driven Development

## Overview

**Source-Driven Development** eliminates hallucinated APIs, deprecated patterns, and version skew by mandating: **every framework decision must be grounded in official, version-pinned documentation with a cited URL in the code comment.**

This skill implements the third standout skill from Addy Osmani's `agent-skills` repo. The banned primary sources list is explicit: **Stack Overflow, blog posts, model training data.** The mantra: *"Confidence is not evidence."*

## When to Use

- Implementing any feature using a framework/library (React, FastAPI, PyTorch, Kubernetes, etc.)
- Adding new dependencies or upgrading existing ones
- Writing integrations with external APIs (GitHub, Stripe, AWS, etc.)
- Using language features with version-specific behavior (Python 3.11+, JS ES2024, etc.)
- Any code where "I think this works" is not acceptable

Don't use for:
- Pure algorithm/logic code with no external dependencies
- One-off scripts with no maintenance burden
- Exploratory spikes (but convert to SDD before merging)

## The Banned Primary Sources List

| Source | Why Banned | Acceptable Use |
|--------|------------|----------------|
| Stack Overflow | Unverified, often outdated, no version context | Secondary only: "see also" links after official source |
| Blog posts / tutorials | Author's opinion, often outdated, no review | Secondary only: complementary explanation |
| Model training data | Hallucinates APIs, confident but wrong | Never as primary; treat as "unverified" |
| GitHub issues (open) | Unresolved, may be wrong | Only if linked from official docs as known issue |
| Reddit / Hacker News / Discord | Anecdotal, no authority | Never |
| AI-generated code (other agents) | Compounds hallucination | Never as source |

## The SDD Workflow

```text
┌─────────────────────────────────────────────────────────────┐
│  1. DETECT VERSION                                          │
│     Read lockfile (package-lock.json, Cargo.lock,           │
│     poetry.lock, go.sum, requirements.txt, Pipfile.lock)    │
│     Extract EXACT version of every relevant dependency      │
└──────────────────────┬──────────────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  2. FETCH OFFICIAL DOCS                                     │
│     Construct version-pinned URL:                           │
│     - https://docs.framework.dev/v{X.Y.Z}/...               │
│     - https://pkg.go.dev/github.com/...@v{X.Y.Z}            │
│     - https://pypi.org/project/{name}/{version}/            │
│     Save URL + relevant section anchors                     │
└──────────────────────┬──────────────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  3. IMPLEMENT                                               │
│     Write code using ONLY the official docs as reference    │
│     For each non-trivial call: add inline comment with URL  │
└──────────────────────┬──────────────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  4. VERIFY                                                  │
│     Run tests against actual dependency version             │
│     Type-check / compile                                    │
│     If unverifiable → emit explicit UNVERIFIED block        │
└─────────────────────────────────────────────────────────────┘
```

## Version Detection (Step 1)

**Automated extraction from lockfiles:**

```python
# package-lock.json (npm/yarn/pnpm)
import json
data = json.load(open("package-lock.json"))
version = data["packages"]["node_modules/react"]["version"]

# Cargo.lock (Rust)
# Use: cargo metadata --format-version=1 | jq '.packages[] | select(.name=="serde") | .version'

# poetry.lock / pyproject.toml (Python)
# poetry show --lock | grep package-name

# go.sum (Go)
# go list -m github.com/pkg/errors

# pip freeze / requirements.txt
# grep package-name requirements.txt
```

**Always pin the exact version in your implementation comments:**

```python
# Source: https://docs.pydantic.dev/v2.9.2/concepts/models/#model-config
# Version: pydantic==2.9.2 (from poetry.lock)
model_config = ConfigDict(extra="forbid", frozen=True)
```

## Official Docs URL Patterns (Step 2)

| Ecosystem | Version-Pinned URL Pattern |
|-----------|----------------------------|
| **Python (PyPI)** | `https://pypi.org/project/{name}/{version}/` → links to project page, then `https://{name}.readthedocs.io/en/{version}/` |
| **Node (npm)** | `https://www.npmjs.com/package/{name}/v/{version}` → README often has versioned docs link |
| **Rust (crates.io)** | `https://docs.rs/{name}/{version}/{name}/` |
| **Go (pkg.go.dev)** | `https://pkg.go.dev/github.com/{org}/{repo}@v{version}` |
| **Java (Maven)** | `https://central.sonatype.com/artifact/{group}/{artifact}/{version}` |
| **.NET (NuGet)** | `https://www.nuget.org/packages/{name}/{version}` |
| **Kubernetes** | `https://kubernetes.io/docs/reference/kubernetes-api/workload-resources/pod-v1/` (version in URL path) |
| **AWS SDK** | `https://docs.aws.amazon.com/sdk-for-{lang}/v{version}/api/` |
| **React** | `https://react.dev/learn/` (versioned via `package.json` react version) |
| **FastAPI** | `https://fastapi.tiangolo.com/{version}/` (e.g., `0.110.0`) |

**Rule:** If no version-pinned URL exists, use the latest stable URL but **add a comment warning**: `// WARNING: URL not version-pinned; verify against {version}`

## Implementation with Citations (Step 3)

**Every non-trivial external call gets a citation comment:**

```python
# GOOD: Version-pinned, section-anchored, explains WHY
# Source: https://docs.pydantic.dev/v2.9.2/concepts/validation/#field-validators
# Version: pydantic==2.9.2
# Why: Need pre-validation transformation before type coercion
@field_validator("email", mode="before")
@classmethod
def normalize_email(cls, v: str) -> str:
    return v.strip().lower()

# GOOD: Config from official docs
# Source: https://fastapi.tiangolo.com/0.110.0/tutorial/security/oauth2-jwt/#oauth2-with-password-and-bearer
# Version: fastapi==0.110.0
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# BAD: No source, no version, no why
@field_validator("email")
def validate_email(v): return v

# BAD: Stack Overflow copy-paste
# https://stackoverflow.com/questions/12345/how-to-validate-email
```

**Citation format (inline, minimal):**
```python
# Source: {version_pinned_URL}#section-anchor
# Version: {package}=={version}
# Why: {one-line rationale}
```

## Unverifiable Claims → Explicit UNVERIFIED Blocks (Step 4)

When official docs don't cover a use case, or behavior is undocumented:

```python
# UNVERIFIED: No official doc covers async context manager for this client
# Version: httpx==0.27.0
# Assumption: __aenter__/__aexit__ properly close connection pool
# Risk: Connection leak if exception during __aenter__
# Verification: Integration test required (see test_httpx_lifecycle.py)
async with httpx.AsyncClient() as client:
    ...
```

**UNVERIFIED block format:**
```markdown
# UNVERIFIED BLOCK
## Claim
[What you're assuming]
## Source Gap
[What official docs don't say]
## Version
[Dependency version]
## Risk
[What breaks if wrong]
## Verification Required
[Test / manual check / monitoring]
```

These blocks **must be addressed before merge** — they're tracked as technical debt.

## Integration with Context Engineering (L4)

Source-Driven Development **is** Level 4 of Context Engineering. The workflow:

1. **Context Engineering** loads L1-L3 (rules, files, specs)
2. **SDD** executes L4: detects version → fetches official docs → implements with citations
3. **Doubt-Driven Development** reviews the implementation with fresh context
4. **Test-Driven Development** verifies against actual runtime (L5)

## Integration with Hermes / CE Loop

| Skill | Integration |
|-------|-------------|
| `context-engineering-agent-skills` | SDD = L4 implementation; CE packs L1-L3 context |
| `doubt-driven-development` | Reviewer verifies citations resolve to official docs |
| `ce-work` | Each subagent runs SDD for its task; citations in PR |
| `ce-code-review` | Check: every external call has citation; UNVERIFIED blocks tracked |
| `test-driven-development` | Tests use same pinned versions; test docs against official examples |

**Hermes hook idea:** Pre-commit hook that scans for external calls without citations.

## Common Pitfalls

1. **Using `latest` docs instead of version-pinned** — Version skew causes subtle bugs
2. **Citing the wrong version** — Lockfile says 2.9.2 but you cite v2.10 docs
3. **Citing tutorial instead of reference** — Tutorials show "happy path"; reference shows constraints
4. **No "Why" in citation** — Future maintainer can't evaluate if still valid
5. **Skipping UNVERIFIED blocks** — Untracked assumptions become production incidents
6. **Trusting framework defaults without verification** — Defaults change across versions
7. **Copy-pasting from GitHub issues** — Issues are not docs; they're bug reports/feature requests

## Verification Checklist

- [ ] Exact version detected from lockfile for every external dependency used
- [ ] Version-pinned official docs URL constructed and accessible
- [ ] Every non-trivial external call has inline citation comment
- [ ] Citation includes: URL, version, one-line rationale
- [ ] No Stack Overflow, blog posts, or training data as primary sources
- [ ] UNVERIFIED blocks created for any assumption without official doc
- [ ] UNVERIFIED blocks have: claim, source gap, version, risk, verification plan
- [ ] Tests run against the exact pinned versions
- [ ] Type-check / compile passes
- [ ] CI verifies lockfile hasn't drifted

## One-Shot Recipes

### Recipe: New Dependency Adoption
```bash
# 1. Add to lockfile
poetry add httpx==0.27.0

# 2. Detect version
poetry show httpx --lock  # → 0.27.0

# 3. Fetch official docs
# https://www.python-httpx.org/ (versioned via release tags)
# Pin: https://github.com/encode/httpx/tree/0.27.0

# 4. Implement with citations
# Source: https://www.python-httpx.org/api/#asyncclient
# Version: httpx==0.27.0
# Why: Need async client with connection pooling
async with httpx.AsyncClient(limits=httpx.Limits(max_connections=10)) as client:
    ...

# 5. Write UNVERIFIED block if needed
# UNVERIFIED: Connection pool sizing for our load profile
# Verification: Load test with locust (see test_load_httpx.py)
```

### Recipe: Upgrade Dependency
```bash
# 1. Upgrade in lockfile
poetry add pydantic@latest  # → 2.9.2

# 2. Diff official docs between versions
# Old: https://docs.pydantic.dev/v2.8.2/
# New: https://docs.pydantic.dev/v2.9.2/

# 3. Check migration guide
# https://docs.pydantic.dev/v2.9.2/migration/

# 4. Update all citations in codebase
# Search: "Version: pydantic=="
# Update to 2.9.2, verify URLs still resolve

# 5. Run full test suite
# Any break = citation was wrong or API changed
```

### Recipe: Pre-Commit Citation Check (Hook)
```bash
#!/bin/bash
# .git/hooks/pre-commit
# Scan for common external patterns without citations
patterns=(
    "httpx\.AsyncClient"
    "pydantic\.BaseModel"
    "fastapi\.APIRouter"
    "react\.useState"
    "axios\."
    "boto3\."
)
for pattern in "${patterns[@]}"; do
    if git diff --cached | grep -q "$pattern"; then
        # Check for citation in same file within 5 lines
        if ! git diff --cached | grep -B5 -A5 "$pattern" | grep -q "Source:"; then
            echo "ERROR: $pattern usage missing Source: citation"
            exit 1
        fi
    fi
done
```

---

## Quick Reference: SDD vs. Traditional

| Traditional | Source-Driven Development |
|-------------|---------------------------|
| "I know this API" | "Let me fetch the v2.9.2 docs" |
| Copy from Stack Overflow | Cite official reference |
| `import x; x.foo()` | `# Source: url#section\n# Version: x==1.2.3\nx.foo()` |
| "Works on my machine" | "Tested against pinned version in CI" |
| Assumptions implicit | UNVERIFIED blocks explicit |
| Upgrade → pray tests pass | Upgrade → diff docs → update citations → test |
```
