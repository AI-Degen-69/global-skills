---
name: web-browsing-log
description: Use after every web_search / web_extract (Firecrawl) OR groktocrawl_search / groktocrawl_answer (GroktoCrawl MCP) OR web_search_exa / web_fetch_exa (Exa MCP) run — logs results to the Vault/Web Browsing research history as per-run markdown files with frontmatter, and rebuilds the root index.md. Keeps a searchable, smart web-research trail.
---

# Web Browsing Log (auto-log web research to Vault)

Convention: after ANY `web_search` or `web_extract` (Firecrawl backend) OR
`groktocrawl_search` / `groktocrawl_answer` (GroktoCrawl MCP) OR
`web_search_exa` / `web_fetch_exa` (Exa MCP) call, persist
the result to Robert's Obsidian vault as a searchable research history.
Enforced via a memory nudge + this skill (no code hook exists; the agent
follows the procedure).

Triggers:
- `web_search` / `web_extract` → `Firecrawl/` layer
- `groktocrawl_search` (MCP) → `GroktoCrawl/Search/`
- `groktocrawl_answer` (MCP) → `GroktoCrawl/Answer/`
- `web_search_exa` (MCP) → `Exa/Search/`
- `web_fetch_exa` (MCP) → `Exa/Web Fetch/`

## Where things live
```markdown
Vault/Web Browsing/                         (new top-level domain, Title Case)
├── index.md                                ROOT INDEX — auto-rebuilt, indexes all child folders
├── Firecrawl/                              provider layer
│   ├── Web Search/                         one md file per web_search run, named <exact search term>.md
│   │   └── Harry Potter.md
│   └── Web Extract/                        one md file per web_extract run, named <page title>.md
│       └── Best Markdown Note Taking Apps for 2026 | Productivity Tools.md
├── GroktoCrawl/                           provider layer (local, privacy-first)
│   ├── Search/                             one md file per groktocrawl_search run, named <exact query>.md
│   └── Answer/                             one md file per groktocrawl_answer run, named <exact query>.md
└── Exa/                                   provider layer (Exa neural web search API)
    ├── Search/                             one md file per web_search_exa run, named <exact query>.md
    └── Web Fetch/                          one md file per web_fetch_exa run, named <page title>.md
```
**Why this shape** (vs the redundant `Web Searches/Fire Crawl/Web Search/Fire Crawl/Web Extract`):
provider is a *layer*, not repeated; `Web Search` / `Web Extract` / `Search` / `Answer`
are sibling categories under the provider. Matches the vault's `domain/provider/category/`
layering and its Title Case convention. Extensible: add `Browser-Use/`, `curl/`
later without restructuring.

## Procedure (run after each search/extract)
1. **Filename = exact search term / query (NO date prefix).** Sanitize: remove `\/:*?"<>|`, trim, cap ~80 chars. `Harry Potter` → `Harry Potter.md`. Re-running same term overwrites (updates `updated` + results).
2. **Firecrawl search** (`web_search`): write `Firecrawl/Web Search/<slug>.md` from the SEARCH template. Dedup: overwrite existing `<query>.md`.
3. **Firecrawl extract** (`web_extract`): write `Firecrawl/Web Extract/<slug>.md` from the EXTRACT template. Set `parent_search` wikilink to the originating search file when applicable.
4. **GroktoCrawl search** (`groktocrawl_search` MCP): write `GroktoCrawl/Search/<slug>.md` from the GroktoCrawl SEARCH template (credits 0 — local).
5. **GroktoCrawl answer** (`groktocrawl_answer` MCP): write `GroktoCrawl/Answer/<slug>.md` from the GroktoCrawl ANSWER template.
6. **Exa search** (`web_search_exa` MCP): write `Exa/Search/<slug>.md` from the Exa SEARCH template (credits = 1 API call).
7. **Exa fetch** (`web_fetch_exa` MCP): write `Exa/Web Fetch/<slug>.md` from the Exa WEB FETCH template. Set `parent_search` wikilink when applicable.
8. Rebuild index: `python "<skill>/scripts/rebuild_index.py"` (or `--base <path>`). Regenerates `Vault/Web Browsing/index.md` — idempotent, safe to re-run.

## Templates

### SEARCH (`Firecrawl/Web Search/<exact-search-term>.md`)
```markdown
---
title: "<query>"
type: "[[Web Search]]"
provider: "[[Firecrawl]]"
domain: "[[Web Browsing]]"
query: "<query>"
run_at: <ISO8601 +03:00>
results_count: <N>
credits_used: <limit*2, i.e. 2 per 10 results>
tags: [web-search, firecrawl]
created: <DD-MM-YYYY>
updated: <DD-MM-YYYY>
---
# <query>

**Provider:** Firecrawl (`web_search`)
**Run at:** <ISO8601>
**Results:** <N> · **Credits:** ~<M>

## Results
1. [<title>](<url>) — <snippet>
   - ⭐ <why best/authoritative — or omit>
2. [<title>](<url>) — <snippet>
   ...

## Agent Verdict
<one line: which result is best and why>
```

### EXTRACT (`Firecrawl/Web Extract/<page-title>.md`)
```markdown
---
title: "<page title>"
type: "[[Web Extract]]"
provider: "[[Firecrawl]]"
domain: "[[Web Browsing]]"
source_url: "<url>"
source_title: "<page title>"
extracted_at: <ISO8601 +03:00>
parent_search: "[[DD-MM-YYYY-<search-slug>]]"
credits_used: 1
tags: [web-extract, firecrawl]
created: <DD-MM-YYYY>
updated: <DD-MM-YYYY>
---
# <page title>

**Source:** [<url>](<url>)
**Extracted:** <ISO8601>

## Content
<markdown body returned by web_extract>

## Agent Summary
<2-3 line condensation of what matters>
```

## GroktoCrawl templates

### SEARCH (`GroktoCrawl/Search/<exact-query>.md`)
Same shape as Firecrawl Web Search, but `provider: "[[GroktoCrawl]]"` and
credits are local (0 — no SaaS cost). Sources come from the local
SearXNG backend (Brave + DuckDuckGo + Google).
```markdown
---
title: "<query>"
type: "[[Web Search]]"
provider: "[[GroktoCrawl]]"
domain: "[[Web Browsing]]"
query: "<query>"
run_at: <ISO8601 +03:00>
results_count: <N>
credits_used: 0
tags: [web-search, groktocrawl, local]
created: <DD-MM-YYYY>
updated: <DD-MM-YYYY>
---
# <query>

**Provider:** GroktoCrawl (`groktocrawl_search`, local SearXNG)
**Run at:** <ISO8601>
**Results:** <N> · **Credits:** 0 (local)

## Results
1. [<title>](<url>) — <snippet>
2. [<title>](<url>) — <snippet>
   ...

## Agent Verdict
<one line: which result is best and why>
```

### ANSWER (`GroktoCrawl/Answer/<exact-query>.md`)
Synthesis run — `groktocrawl_answer` returns a cited answer + source list.
Log the synthesized answer (truncated if long) + cited source URLs.
```markdown
---
title: "<query>"
type: "[[Web Answer]]"
provider: "[[GroktoCrawl]]"
domain: "[[Web Browsing]]"
query: "<query>"
answered_at: <ISO8601 +03:00>
model: "qwen3:latest (local Ollama)"
citations_count: <N>
tags: [web-answer, groktocrawl, local, synthesis]
created: <DD-MM-YYYY>
updated: <DD-MM-YYYY>
---
# <query>

**Provider:** GroktoCrawl (`groktocrawl_answer`, qwen3:latest local)
**Answered at:** <ISO8601>

## Answer
<synthesized answer text, cited [N] markers preserved>

## Cited Sources
1. [<title>](<url>)
2. [<title>](<url>)
   ...

## Agent Verdict
<one line: was the synthesis accurate / biased? compare to native web_search>
```

## Exa templates

### SEARCH (`Exa/Search/<exact-query>.md`)
Same shape as Firecrawl Web Search, but `provider: "[[Exa]]"` and credits = 1 API call
(Exa meters per search request). Results come from Exa's neural/keyword web index.
```markdown
---
title: "<query>"
type: "[[Web Search]]"
provider: "[[Exa]]"
domain: "[[Web Browsing]]"
query: "<query>"
run_at: <ISO8601 +03:00>
results_count: <N>
credits_used: 1
tags: [web-search, exa, api]
created: <DD-MM-YYYY>
updated: <DD-MM-YYYY>
---
# <query>

**Provider:** Exa (`web_search_exa`, neural web search API)
**Run at:** <ISO8601>
**Results:** <N> · **Credits:** 1 (API call)

## Results
1. [<title>](<url>) — <snippet>
2. [<title>](<url>) — <snippet>
   ...

## Agent Verdict
<one line: which result is best and why — compare to Firecrawl/GroktoCrawl if useful>
```

### WEB FETCH (`Exa/Web Fetch/<page-title>.md`)
Full-content fetch from a known URL via `web_fetch_exa`. Same shape as Firecrawl
Web Extract but `provider: "[[Exa]]"` and credits = 1 API call.
```markdown
---
title: "<page title>"
type: "[[Web Extract]]"
provider: "[[Exa]]"
domain: "[[Web Browsing]]"
source_url: "<url>"
source_title: "<page title>"
extracted_at: <ISO8601 +03:00>
parent_search: "[[DD-MM-YYYY-<search-slug>]]"
credits_used: 1
tags: [web-extract, exa, api]
created: <DD-MM-YYYY>
updated: <DD-MM-YYYY>
---
# <page title>

**Source:** [<url>](<url>)
**Extracted:** <ISO8601>

## Content
<clean markdown body returned by web_fetch_exa>

## Agent Summary
<2-3 line condensation of what matters>
```

## Index format (`Vault/Web Browsing/index.md`)
Frontmatter: `title: Web Browsing — Index`, `type: "[[Index]]"`, `domain: "[[Web Browsing]]"`,
`created`, `updated`, `icon: TiWorld`, `iconColor: Silver`. Body:
- Structure (wikilinks to the two folders)
- Recent Searches (last 15, wikilinked, with result count + credits)
- Recent Extracts (last 15)
- By Provider (Firecrawl → file counts)
- All Entries (chronological, full list)
Generated by `rebuild_index.py` — do NOT hand-edit (it is overwritten).

## Notes / limitations
- Vault is a git backup repo; files are NOT committed unless Robert asks (gbrain
  won't see uncommitted files until then). Logging still works locally.
- "Automatic" = convention enforced by memory nudge + this skill. For truly
  unattended logging, a cron scanning session transcripts would be needed.
- Never invent results — only log what the tool actually returned.
