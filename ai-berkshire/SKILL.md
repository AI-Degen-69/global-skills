---
name: ai-berkshire
version: "1.0.0"
description: Use when researching equities, auditing a portfolio, tracking investment theses, screening for quality, or run
argument-hint: "ai-berkshire portfolio-review <holdings> | ai-berkshire quality-screen AAPL,MSFT | ai-berkshire thesis-tracker <name> | ai-berkshire news-pulse <ticker>"
allowed-tools: Read, Write, Bash, WebSearch, AskUserQuestion
metadata:
  openclaw:
    emoji: "📈"
    requires:
      env: []
      bins: [python3]
    tags: [investing, research, portfolio, valuation, equities]
---

# AI Berkshire — value-investing research methodology (Hermes adapter)

Source repo cloned locally (canonical, do not fork):
`C:/Users/Tiger/Agents/Projects/portfolio-os/vendor/ai-berkshire`
Upstream: https://github.com/xbtlin/ai-berkshire

The repo's `skills/*.md` files are the canonical workflow prompts (19 of them).
This skill tells Hermes HOW to use them correctly in THIS environment, which
differs from the repo's native Claude Code / Codex assumptions.

## ⚠️ Environment adaptation (MANDATORY — read before invoking any workflow)
The repo assumes Claude Code/Codex with `WebSearch` + `Task` multi-agent.
This environment DOES NOT have WebSearch enabled and Hermes has no `Task` tool.
Adapt every workflow as follows:

| Repo assumes | Use instead in Hermes |
|--------------|----------------------|
| `WebSearch` for prices/filings/news | **P1.2 market-data connector** (yfinance / IBKR) + `last30days` skill for narrative/sentiment. If connector not built yet, state data gap explicitly — do NOT fabricate. |
| `Task` parallel agents | `delegate_task` (background subagents) for parallel per-holding research. |
| Inline financial math | `python3 tools/financial_rigor.py ...` (runs on stdlib, no deps) |
| Publishable-report check | `python3 tools/report_audit.py ...` |

Always state the data-cutoff date (run `date`) in any output, per repo rules.

## Inventory → objective mapping (the 19 workflows)
Objectives: 2 signals · 3 audit · 4 opportunities · 5 health · 6 PM loop

| Workflow (skills/<file>.md) | Covers | Use for |
|------------------------------|--------|---------|
| `portfolio-review.md` | 3,5,6 | Audit a live/paper portfolio; concentration, correlation, rebalancing |
| `thesis-tracker.md` | 5,6 | Post-buy discipline: track if each thesis is still valid |
| `thesis-drift.md` | 3,5 | Compare two theses/reports; fact vs valuation vs wording drift |
| `quality-screen.md` | 4 | 7 hard metrics to exclude non-first-class companies (batch) |
| `investment-checklist.md` | 4 | 6-gate Buffett pre-buy filter (~10 min) |
| `news-pulse.md` | 2,3 | 10-min attribution when a holding spikes/drops |
| `financial-data.md` | 3 | Cross-verify key data from 2 independent sources (>1% gap = alert) |
| `earnings-review.md` | 3,5 | Read raw filings like Buffett; no secondary research notes |
| `investment-research.md` | 4 | Full deep-dive on one listed company |
| `investment-team.md` | 4 | 4-agent parallel research, fastest+broadest |
| `industry-research.md` / `industry-funnel.md` | 4 | Whole-sector scan → ≤10 → 3 deep |
| `bottleneck-hunter.md` | 4 | Supply-chain bottleneck / arbitrage from super-trends |
| `management-deep-dive.md` | 4 | "Buy the person" — deep management check |
| `private-company-research.md` | 4 | Ant, SpaceX, etc. (sparse-info) |
| `deep-company-series.md` | 4 | 8-long-form series on one company |
| `dyp-ask.md` | — | Reason about anything Duan-Yongping style |
| `wechat-article.md` | — | Publishable article (3-agent) |
| `earnings-team.md` | 3,4 | Earnings read team + publish |

## How to invoke (pattern)
1. Read the relevant `skills/<file>.md` — that IS the prompt.
2. Substitute data gathering per the table above (no WebSearch).
3. Run rigor tools where the workflow calls them:
   - `python3 <repo>/tools/financial_rigor.py verify-valuation --price P --eps E --bvps B`
   - `python3 <repo>/tools/financial_rigor.py verify-market-cap --price P --shares S --reported M --currency USD`
   - `python3 <repo>/tools/financial_rigor.py three-scenario ...`
   - `python3 <repo>/tools/report_audit.py extract <report.md>` → `verdict`
4. Output to `reports/` under portfolio-os (or user-specified). Mirror durable
   theses/decisions into Vault `Finance/` (vault-ingestion).

## Verification
Any "research complete / report publishable" claim MUST be gated by
`report_audit.py verdict` AND (for subagent work) `fable-judge`. Absence of
errors is not proof.

## Notes
- Repo is for learning/research, not investment advice (per its LICENSE/AGENTS).
- The Python rigor tools run on stdlib only (verified Python 3.14). `stock_screener.py`
  and data-dependent tools need P1.2 market-data connector to fetch live prices.
