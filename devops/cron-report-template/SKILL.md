---
name: cron-report-template
description: Use when authoring or auditing a Hermes cron job's Discord run-report output. Enforces ONE uniform header hier
---

# Cron Run-Report Template (fleet-wide uniform)

## ⚠️ The load-bearing gotcha
**Discord does NOT render markdown `#`/`##` headers.** They arrive in chat as
literal text — `# 🟢` shows up as the string "# 🟢", with NO header hierarchy,
no bold, no separation. So a job that prints `print("# 🟢 Foo — Run Report")`
looks broken and flat next to a job using bold. **Never use `#`/`##` in any
cron delivery meant for Discord.**

Also: a job's **title must lead with a status badge** (🟢/🟡/🔴), never a topic
emoji (e.g. 🛡️). Topic emojis belong inside sections, not as the title lead.

## ✅ Canonical regime (the ONLY accepted shape)
```
[status] **Name — Run Report**          # status badge 🟢/🟡/🔴 + **bold** title
📅 YYYY-MM-DD                           # date line

🔍 What ran                             # plain emoji-led section (NO #, NO **)
<one-line description>

📋 Changes applied
  - <bullets of fixes, or "- None (read-only audit)">

📊 Findings
  - <bullets, or "- none">

🚦 Outcome
[status] GREEN|YELLOW|RED — one-line verdict

⏸️ Left (manual / approval-gated):
  - <items, or "- none">
```

Rules:
- Title = `[status] **Name — Run Report**` (badge first, then bold).
- Sections = plain `[emoji] Label` — emoji-led, **no `#`, no `**`**.
- No literal `#`/`##` anywhere in the emitted text.
- Status badge leads the title; never a topic emoji (🛡️📡 etc.).

## When to use this skill
- Writing a new `no_agent` cron script (scripts/*.py) that prints a report.
- Writing an `agent` cron `prompt` that tells the LLM how to format its delivery.
- Auditing existing jobs for header drift (the symptom: some deliveries show
  `# 🟢` literally, or lead with a topic emoji).

## Patterns

### A. `no_agent` script — emit directly (preferred for script-only jobs)
Print the exact shape above. Status badge + bold title, plain emoji sections.

```python
def report(title, objective, status, findings, fixed, left):
    badge = {"ok": "🟢", "partial": "🟡", "fail": "🔴"}[status]
    word  = {"ok": "GREEN", "partial": "YELLOW", "fail": "RED"}[status]
    lines = [
        f"{badge} **{title} — Run Report**",
        f"📅 {datetime.now():%Y-%m-%d}",
        "",
        "🔍 What ran",
        objective or "(no description)",
        "",
        "📋 Changes applied",
        ("  - " + "\n  - ".join(fixed)) if fixed else "  - None (read-only audit)",
        "",
        "📊 Findings",
        ("  - " + "\n  - ".join(findings)) if findings else "  - none",
        "",
        "🚦 Outcome",
        f"{badge} {word} — <verdict>",
    ]
    if left:
        lines += ["", "⏸️ Left (manual / approval-gated):", "  - " + "\n  - ".join(left)]
    print("\n".join(lines))
```

### B. Vault / gbrain jobs — use the shared renderer (DON'T hand-roll)
`scripts/vault_report.py` is the single source of truth. Import and call it;
the output already matches the canonical regime, and editing it cascades to
all 7 vault/gbrain jobs at once.

```python
from vault_report import render_report   # alias: render()

text = render_report(
    title="gbrain vault cleanup (autopilot)",   # shown after the badge
    objective="protect vault-tiger from stale locks / drift",
    status="ok",                                  # "ok"|"partial"|"fail"
    findings=["cleared stale lock"],              # list[str]; [] -> "- none"
    fixed=[],                                     # list[str]; [] -> "- None (read-only audit)"
    left=["cycle other sources"],                 # optional; omitted if empty
)
print(text)
```
Output:
```
🟢 **gbrain vault cleanup (autopilot) — Run Report**
📅 2026-07-20

🔍 What ran
protect vault-tiger from stale locks / drift

📋 Changes applied
  - None (read-only audit)

📊 Findings
  - cleared stale lock

🚦 Outcome
🟢 GREEN — no action needed.

⏸️ Left (manual / approval-gated):
  - cycle other sources
```

### C. `agent` job — bake the shape into the prompt
The LLM won't inherit a renderer; tell it explicitly. In the job's `prompt`:
- Give the exact template block (from ✅ above).
- Forbid `#`/`##` and forbid a topic-emoji title lead.
- Example (the fixed STACK.md Watchdog prompt):
  `🟢 **STACK.md Watchdog — Run Report**` (status badge, NOT `🛡️ **...**`),
  then `🔍 What ran` / `📋 Changes applied` / `📊 Outcome` / `🚦 File state after run`
  as plain emoji-led sections.

## Audit / fix checklist (how to standardize a drifting fleet)
1. `search_files` the scripts dir for literal markdown headers:
   pattern `"## 🔍|"## 📋|"## 📊|"## 🚦|"# 🟢|"# 🟡|"# 🔴` (target=content).
   Every hit is a Discord-render bug → convert to plain emoji-led section.
2. For `no_agent` scripts: replace `print("# 🟢 X — Run Report")` →
   `print("🟢 **X — Run Report**")`; replace `print("## 🔍 What ran")` →
   `print("🔍 What ran")`. Same for `lines.append(...)` list-built reports.
3. For `agent` jobs: read `cron/jobs.json`, find the job's `prompt` string
   (it's one escaped JSON string — emoji are `\ud83d\udfe2` etc., newlines `\n`).
   Patch the title to lead with `\ud83d\udfe2` (🟢) and strip any `**` from
   section labels so they match the plain-emoji regime.
4. `vault_report.py` is shared by gbrain + vault jobs — fix it ONCE, not per job.
5. Verify: `search_files` returns 0 hits; `python3 -c "import ast,json; [ast.parse(open(f)) for f in FILES]; json.load(open('cron/jobs.json'))"` passes;
   render one job's output and eyeball the shape (no leading `#`).

## Pitfalls
- **Topic emoji in title** (🛡️/📡) — looks like a status badge but isn't.
  Always 🟢/🟡/🔴 first.
- **Bold sections** (`**🔍 What ran**`) — deviates from the accepted plain-emoji
  regime used by the vault jobs; keep sections unbolded for uniformity.
- **Editing `jobs.json` prompt with real newlines/emoji** — the file stores the
  prompt as ONE escaped string; use the `\ud83d\udfe2` / `\n` forms in `patch`,
  not literal newlines, or the match fails.
- **Docstrings claiming `#` is safe** — `vault_report.py` and `hermes-backup.py`
  once said this; it's wrong. Discord flat-renders `#`.
- **Stale template file** — `scripts/VAULT_MAINTENANCE_REPORT_TEMPLATE.md` must
  mirror this regime; keep it updated when the shape changes.

## Verification
- 0 literal `#`/`##` headers in any cron script (`search_files` clean).
- 0 topic-emoji title leads in `cron/jobs.json` prompts.
- All edited `.py` + `jobs.json` parse (AST / JSON).
- Live render of one job prints the exact `[status] **Name — Run Report**` +
  plain `🔍/📋/📊/🚦` sections, no leading `#`.
