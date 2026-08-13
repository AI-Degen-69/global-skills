---
name: summarize-update
description: Use when the user asks "what's new upstream / what would I get if I update / summarize before I update"
---

# summarize-update

Turn the gap between **what you have now (HEAD)** and **what upstream published
(origin/main)** into a **before → after comparison table** the user can skim in
30 seconds. Plain language, real-world examples, zero commit IDs, zero line
counts. Lead with what's heavy or risky; bury the noise.

## When to use
- User asks "what's new upstream / what would I get if I update / summarize before I update".
- User wants a "day summary" of what changed upstream since their version.
- User mentions summarizing the diff between their version and upstream in non-technical terms.

## Inputs — CURRENT vs UPSTREAM (not a historical range)
The comparison is **your current checkout (`HEAD`) against what upstream has
published** — i.e. `HEAD..origin/main` (or `HEAD..<upstream>/<branch>`).
This answers "what would an update bring me?" before/after pulling.

- **Base = your current `HEAD`** (what you have installed/running).
- **Target = upstream tip** — `origin/main` by default. If on a fork or
  non-main branch, use the tracked upstream branch.
- **Always `git fetch` first** so `origin/main` is fresh. Then:
  - If `git rev-list --count HEAD..origin/main` == 0 → you're up to date; say so
    in 1 sentence and stop (no table).
  - If > 0 → that's the range to summarize: `HEAD..origin/main`.

This replaces any "find the pre-update base commit" logic. The whole point is
current-vs-upstream, so the table reads as **what you HAVE now → what you'd GET
after updating**.

## Target repository (which repo to compare)
The Hermes runtime root (`C:\Users\Tiger\AppData\Local\hermes`) is **NOT** a git
repo (per AGENTS.md §6), so this skill must compare a *code* repo, not the
runtime folder.

- **Default target = the `hermes-agent` repo:**
  `C:\Users\Tiger\AppData\Local\hermes\hermes-agent`
  (origin `https://github.com/NousResearch/hermes-agent.git`, branch `main`).
  This is the canonical "Hermes itself" source and is what the user means by
  "the hermes-agent repo" / "hermes/hermes-agent".
- **Only compare a different repo (e.g. gstack, a plugin, another project) if
  the user explicitly names it.** Never substitute gstack or any other repo
  just because the runtime root isn't a git repo — that is the wrong target and
  must not be inferred. (If the user later says "compare gstack", then target
  `C:\Users\Tiger\Agents\Global-Skills\gstack`.)
- Run every Gather-phase command from the chosen repo's root (`cd` there
  first). If that repo's working tree has local uncommitted edits, surface them
  in the summary — they survive `git pull` unless upstream touched the same
  paths.

## Gather phase (run these, then THINK — do not dump raw output at the user)
Run in the repo root after `git fetch`. Replace `UP` with `origin/main`.

1. **Heaviest files (structural signal):**
   ```
   git diff --stat HEAD..UP | sort -t'|' -k2 -rn | head -20
   ```
   (Approximate by line volume; enough to spot rewrites/deletions.)

2. **Risk-class commits (behavior / data / security):**
   ```
   git log HEAD..UP --format="%s" | grep -iE "breaking|security|credential|oauth|migrat|reset --hard|data loss|backward|incompat|auth|token"
   ```

3. **Core-touching files (affect every session):** search the stat output for
   `gateway/run.py`, `hermes_cli/web_server.py`, `tui_gateway/server.py`,
   `hermes_cli/config.py`, `hermes_cli/main.py`. These outrank single-skill
   tweaks.

4. **Feature/fix areas:** group subjects by conventional prefix/area:
   ```
   git log HEAD..UP --format="%s" | grep -iE '^feat' | grep -oiE '\((desktop|gateway|agent|browser|codex|kanban|cron|cli|dashboard|memory|skills|mcp|plugin|config|provider|model|honcho|portal|tui|pricing|analytics)[^)]*\)' | sort | uniq -c | sort -rn
   ```

## Weighting / bucketing (order the final table by this)
1. **Structural** — files with the biggest churn, or deleted/renamed core
   modules. These usually explain why a rebuild happened.
2. **Risk / behavior-changing** — anything from step 2 (OAuth, credentials,
   reset/recovery, migration). Flag these for the user to verify.
3. **Features** — visible wins (new UI, new providers, new commands).
4. **Fixes by area** — collapsed to one line per area, no enumeration.
5. **Noise** — lockfile churn, test files. Mention in one sentence, don't table.

## Output format (EXACT — this is the deliverable)

Group changes by **verdict**, and lead each group with a verdict **header**.
Structure per group:

```
## ⚠️ Significant
<one-line plain summary of what's in this group>
| What | Before | Now | Everyday example |
|---|---|---|---|
| ... | ... | ... | ... |

## 🟡 Can Wait
<one-line plain summary>
| What | Before | Now | Everyday example |
|---|---|---|---|
| ... | ... | ... | ... |

## 🟢 Skip / Not Applicable
<one-line plain summary>
| What | Before | Now | Everyday example |
|---|---|---|---|
| ... | ... | ... | ... |
```

- **Verdict headers** (use exactly these, in this order):
  - `## ⚠️ Significant` — fixes real daily-use gaps or behavior/security risks.
    Update now if any of these touch what you use.
  - `## 🟡 Can Wait` — annoyances or edge cases you may never hit. Safe to
    delay.
  - `## 🟢 Skip / Not Applicable` — dev-only, docs/CI, or features you don't
    use (e.g. a memory backend you don't have, a platform you don't run).
- **One-line summary** under each header: what the group covers, in open
  language.
- **Table columns** (same for every group):
  - **What**: the area/feature in 2–4 words.
  - **Before / Now**: the user-visible behavior, NOT the code.
  - **Everyday example**: a concrete "you can now…" scenario a non-dev gets.

Rules:
- NO commit hashes, NO PR numbers, NO `+N/-N` counts anywhere.
- NO file paths, NO function names, NO jargon (say "login tokens", not "OAuth
  bearer tokens").
- **Repo header (mandatory, first block of the output):** emit the target repo
  identity before anything else, using exactly this shape — `Local Commit #`
  is the short SHA of `HEAD`, `Repo Commit #` is the short SHA of `origin/main`,
  and `Commits behind` is `git rev-list --count HEAD..origin/main`:
  ```
  ## Repo: hermes-agent (NousResearch/hermes-agent)
  - **Local Commit #**: <HEAD short SHA>
  - **Repo Commit #**: <origin/main short SHA>
  - **Commits behind**: <count>
  ```
  If the user pointed the skill at a non-default repo, put that repo's name in
  the `## Repo:` line instead (e.g. `## Repo: gstack (garrytan/gstack)`).
- Then lead with the one-line header "📋 What you'd get if you update now
  (your version → available update)".
- End with an **Overall Summary** section: one paragraph recap, then a final
  verdict rendered as a **header with a colored emoji**:
  - `## 🟢 Update now` — when any Significant row touches the user's verified
    stack (per STACK.md). Green = update now.
  - `## 🟡 Can wait` — when every Significant row is for something the user
    doesn't run (all landed in 🟢 Skip). Yellow = can wait.
  Use exactly one of those two headers as the closing line. If STACK.md was
  flagged stale in step 4, add a one-line note under the verdict: "⚠️ STACK.md
  may be outdated — verify before relying on the Skip calls."
- Keep it day-to-day, open, explanatory. Examples are mandatory, not optional.

### STACK.md is the source of truth (do NOT hedge, do NOT guess)
The user maintains a `STACK.md` that declares exactly what they run. It is the
authoritative input for bucketing — **never infer the stack from commit
subjects or decide "this looks big, so it's Significant."**

1. **Locate it.** Check, in order:
   - `<hermes-runtime-root>/STACK.md` (e.g. `C:\Users\Tiger\AppData\Local\hermes\STACK.md`)
   - repo-adjacent `STACK.md` if the skill is run from a project dir.
   If no `STACK.md` exists, fall back to live-config reverse-engineering (step 5).

2. **Read it first, then follow its `Implication` lines.** STACK.md already
   encodes verdict logic per area, e.g. "Windows-specific fixes → Significant",
   "mem0 change → 🟢 Skip", "Multiple providers → model-switch fixes
   Significant". Use those lines directly — they override general sizing.

3. **A change is Significant/Can-Wait ONLY if it touches something STACK.md
   lists.** This is the anti-"huge-but-irrelevant" rule: a 2000-line WhatsApp
   integration, a brand-new Slack feature you don't use, or a mem0 rewrite all
   land in **🟢 Skip** — never Significant — when STACK.md does not list that
   platform/backend as active. **Size of the change does not earn it a
   Significant row; relevance to the verified stack does.**

4. **Verify STACK.md is current (don't trust a stale card).** Cross-check it
   against reality before using it to bucket:
   - Its `Last verified` date should be recent relative to the release you're
     summarizing. If a major upstream release has shipped since that date, flag
     STACK.md as *possibly stale* and re-confirm the key facts.
   - Spot-check 2–3 claims against live `config.yaml` (memory backend, platform
     list, primary provider). If they disagree, trust live config for that row
     and note STACK.md needs an update.
   - After bucketing, confirm every Significant row maps to a STACK.md entry. If
     you had to decide a Significant row from live config because STACK.md was
     silent on it, that's a STACK.md gap → recommend updating it.

5. **Fallback (no STACK.md):** read `config.yaml` (+ profile config) for memory
   backend, model providers, platforms (Discord/Slack — Telegram is
   decommissioned, treat as 🟢 Skip automatically), and plugin toggles. Same
   rule applies: not-enabled → 🟢 Skip with a confirmed reason, never a hedged
   "can wait unless you use".

## Worked example — SAMPLE SHAPE ONLY, NEVER HARDCODE
This is a **template of the output format**, NOT a cached result. Every time
the skill runs it MUST regenerate from the **live** `HEAD..origin/main` range
after a fresh `git fetch` — never reuse this table. The rows below are
illustrative; the real run will differ (commit counts grow, themes shift).
If STACK.md was updated, re-read it first — the verdicts follow STACK.md, not
this sample.

## Repo: hermes-agent (NousResearch/hermes-agent)
- **Local Commit #**: a1b2c3d
- **Repo Commit #**: e4f5g6h
- **Commits behind**: 81

📋 What you'd get if you update now (your version → available update)

## ⚠️ Significant
Fixes that close real daily-use gaps for YOUR verified stack (per STACK.md) —
update now if you hit any of these.
| What | Before | Now | Everyday example |
|---|---|---|---|
| Discord stability | Stalled connection left bot frozen until manual restart | Gateway auto-detects stall, recovers websocket + event loop | Your Discord bot recovers on its own after a blip |
| Gateway resilience | Stuck worker / crash-loop could hang or peg CPU | Thread watchdog + heartbeat + circuit breaker | Gateway survives a crash without babysitting |
| Windows desktop startup | Electron crashed at launch (GPU sandbox) | Fallback recovers the startup crash | App opens on Windows instead of dying on boot |
| Global model switch | Stale API mode / wrong base URL after switch | Base URL + mode sync on switch | Flip providers and the endpoint actually sticks |

## 🟡 Can Wait
Annoyances or edge cases — safe to delay.
| What | Before | Now | Everyday example |
|---|---|---|---|
| Stop button | Could hit wrong session | Interrupt targets right session | Stop A, B stays calm |
| Update progress | Log buffered, late | Live streaming output | Watch the update progress |
| Kanban unblock | Status mismatch vs DB | Synced with DB | Unblock reflects on board |
| Cron on Windows | Launcher popups | No popups | Jobs run silently |

## 🟢 Skip / Not Applicable
Dev-only, docs/CI, or things STACK.md does NOT list you run.
| What | Before | Now | Everyday example |
|---|---|---|---|
| mem0 memory | Legacy URL aliases broken | Migrated to current URLs | — (STACK.md: default memory, not mem0) |
| Windows remote gateway | Untrusted system CAs | Trusts Windows system CAs | — (STACK.md silent on remote gateway → Skip) |
| In-app Nous plan | Left app for website | /subscription + /topup in-app | — (STACK.md: nous provider, no paid-plan use stated → Skip) |
| Docs / CI / tests | Internal upkeep | Fixes + coverage | Nothing user-visible |

## Overall Summary
The available update's Significant rows are those STACK.md confirms you hit
(Windows + Discord + multiple providers). Anything STACK.md doesn't list as
active — remote gateway, Nous paid plan, mem0, other platforms — lands in 🟢
Skip regardless of change size. Regenerate this section live; do not copy the
sample verdicts.

## 🟢 Update now  (or ## 🟡 Can wait — pick per live run)
Render exactly one closing verdict header based on the live run: green if any
Significant row touches your verified stack, yellow if all Significant rows
fell to 🟢 Skip.

## Pitfalls
- Do NOT paste `git log --oneline` of hundreds of lines. That is the failure
  mode this skill exists to replace.
- Do NOT lead with lockfile/test churn — that's the noise bucket (usually lands
  in 🟢 Skip).
- If the range is small (1–3 commits), skip the grouped tables — reply in 1–3
  plain sentences with a verdict instead, still no hashes.
- Keep examples grounded in what the user actually uses; if they only use
  Discord + Windows, drop rows for areas they don't touch (put them in 🟢 Skip
  with the reason).
- NEVER write "unless you use X" — verify the stack from STACK.md (or config as
  fallback) and place the row in 🟢 Skip with a confirmed reason.
- **STACK.md is law.** A change's size never makes it Significant — relevance to
  the verified stack does. A huge feature for a platform STACK.md doesn't list
  (e.g. WhatsApp, Telegram, a memory backend you don't run) goes to 🟢 Skip, not
  Significant. Always read STACK.md before bucketing; never guess the stack from
  commit subjects.
- **Flag stale STACK.md, don't blind-trust it.** If its `Last verified` date
  predates a major release or it contradicts live config, say so and re-confirm
  the key facts — but still prefer its explicit Implication lines when present.
- **NEVER hardcode the worked example.** The sample above is format-only. The
  real output MUST come from the live `HEAD..origin/main` range; commit counts
  and themes shift every fetch. If you find yourself copying the sample rows
  verbatim, stop and run the Gather phase instead.
