---
name: web-discovery-fallback
description: Use when web_search / web_extract (Firecrawl) are unavailable, dead, quota-exhausted, or returning errors — provides verified browser + curl/Python discovery paths so "find X on the web" still works.
---

# Web Discovery Fallback (when Firecrawl is down)

Hermes's native `web_search` / `web_extract` route through Firecrawl. When that
backend is uninstalled, key-less, over quota, or erroring, the agent must NOT
claim "I searched the web" falsely. Use the paths below instead. All were
verified live on this install (Windows + git-bash venv).

## When to use
- `web_search` returns `Feature 'search.firecrawl' unavailable` (SDK missing / lazy installs off).
- Firecrawl returns 401 (bad/expired key) or 429 (free-tier 1k credits/mo exhausted).
- Any non-2xx / empty-result anomaly from the native web tools.

## Path A — Browser (JS-rendered search engines) [PRIMARY but CAPTCHA-PRONE]
The `browser` tool (browser-use) works independently of Firecrawl and can drive a
search engine. BUT live testing on this install showed **DuckDuckGo serves a CAPTCHA**
("Select all squares containing a duck") to the browser-use session, and Bing/Google
often serve degraded bot-mode results. Use the browser path when you need JS rendering
of a *specific known URL*, not as a reliable open-web discovery engine.

1. `browser_navigate("https://html.duckduckgo.com/html/?q=YOUR+QUERY")` (HTML endpoint is
   less likely to CAPTCHA than the JS homepage — still not guaranteed).
2. `browser_snapshot()` → parse result links from the accessibility tree.
3. For a chosen result: `browser_navigate(url)` then `browser_snapshot()` or
   `browser_get_images()` to extract content.
4. Use `browser_click` / `browser_scroll` for paginated or "more results" flows.

⚠️ If you hit a CAPTCHA or empty results via the browser search engine, **do not claim
"no results"** — fall back to Path B or state the engine blocked the request.

## Path B — curl + Python (raw HTML / APIs) [FAST, NO JS — but engines degrade]
For endpoints that serve HTML/JSON (news sites, docs, Wikipedia, APIs, RSS). Search
*engines* via curl are unreliable here: live test showed DuckDuckGo Lite returned 0
parseable result links and Bing returned degraded/off-topic results to a non-browser
User-Agent (even with HTTP 200). Use curl for **known URLs / APIs**, not for open search.

```bash
# Known-URL extraction (reliable):
curl -sL --max-time 20 "https://en.wikipedia.org/wiki/OpenAI" | python3 -c "
import sys, re, html
from html.parser import HTMLParser
class T(HTMLParser):
    def __init__(s): super().__init__(); s.out=[]; s.skip=0
    def handle_starttag(s,t,a):
        if t in ('script','style'): s.skip+=1
    def handle_endtag(s,t):
        if t in ('script','style') and s.skip: s.skip-=1
    def handle_data(s,d):
        if not s.skip: s.out.append(d)
p=T(); p.feed(sys.stdin.read())
print(' '.join(p.out).strip()[:4000])
"
```
- Verify egress first: `curl -sI --max-time 12 https://example.com` → expect `HTTP/1.1 200 OK`.
- No `bs4` in the Hermes venv — use stdlib `html.parser` (above). Do NOT `pip install`
  unless the user explicitly relaxes `security.allow_lazy_installs`.
- `html.parser` passes attrs as a **list of (name,value) tuples**, NOT a dict —
  `dict(attrs)` before `.get()`. (Common crash: `'list' object has no attribute 'get'`.)
- For JSON APIs, pipe curl into `python3 -m json.tool` or `python3 -c "import sys,json;..."`.

## Path C — Local second brain (NOT live web)
Vault / gbrain / session_search are context, not the live web. Use them when the
answer can come from Robert's prior research; label it clearly as "from vault, not live web."

## Repair (restore native search) — only if user wants it
1. `uv pip install firecrawl-py==4.17.0` into the Hermes venv
   (`C:/Users/Tiger/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe -m pip install ...`).
2. Put key in `C:/Users/Tiger/AppData/Local/hermes/.env` as `FIRECRAWL_API_KEY=...`.
3. **Restart the Hermes runtime** — secrets load at process start.
4. Verify: `web_search("test")` should return live results.

## API-shape note (firecrawl-py 4.17.0)
The v4 SDK split into `v1`/`v2`. `v2.FirecrawlClient(api_key=...).search(q, limit=N)`
returns a `SearchData` with `.web` / `.news` / `.images` — NOT `.data`. Reading
`.data` yields an empty list (a common false "0 results"). The agent's own
`web_search` reads `.web` correctly.

## Measured behavior (live test, 2026-07-15, query "best lightweight markdown note app 2026")
| Path | Result | Time | Cost |
|---|---|---|---|
| Native `web_search` / `v2.search(limit=N)` | ✅ 5 real results, clean | 0.6–2.1s | **2 credits per 10 results** (limit=5 → ~10 credits; limit=10 → ~20) |
| Browser → DDG homepage | ⚠️ CAPTCHA wall ("select all ducks") | n/a | 0 (blocked) |
| curl → DDG Lite | ❌ 0 parseable result links | 0.5s | 0 (useless) |
| curl → Bing (encoded query) | ⚠️ 200 OK but degraded/off-topic results | 1.6s + 0.2s parse | 0 (unreliable) |

**Takeaway:** When Firecrawl is live, it is the only path that reliably *discovers*
open-web content here. The fallback paths are for (a) fetching a *known URL* via curl,
or (b) rendering a *specific page* via browser. They are NOT a substitute for search
engine discovery. If Firecrawl is dead/over-quota, the honest move is to tell the user
discovery is degraded and offer to re-enable it — not to fake a "search."

**Free-tier math:** 1,000 credits/mo ÷ ~10 credits/search ≈ **~100 searches/month** before
the free tier is exhausted (then 429 = hard stop until reset or paid plan).
- [ ] Browser path returned ≥1 real result URL for the query.
- [ ] OR curl path returned non-empty extracted text / valid JSON.
- [ ] Output states which fallback path was used (never implies native search).
- [ ] If claiming "no results found," confirm via ≥2 independent paths before stating it.
