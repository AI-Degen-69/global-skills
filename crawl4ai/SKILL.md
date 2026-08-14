---
name: crawl4ai
version: 1.0.0
description: Use when Robert wants to crawl one or more web pages into clean, LLM-ready
triggers:
  - "crawl this page to markdown"
  - "use crawl4ai to scrape"
  - "pull web content as markdown for RAG"
  - "crawl a site into the vault"
tools:
  - terminal
  - write_file
mutating: true
---

# Crawl4AI — Web to LLM-Ready Markdown

## Contract

This skill guarantees:
- Pages are crawled with the installed `crawl4ai` library (venv `C:\Users\Tiger\venv\crawl4ai`).
- Output is clean Markdown (optionally "fit" markdown) suitable for LLM/RAG ingestion.
- Every crawl reports `success` + char count; failures surface the real error, never a fake result.
- The dedicated venv is used explicitly — never the hermes-agent venv.

## Critical environment note (DO NOT SKIP)

The shell carries a persistent `PYTHONPATH` pointing at the hermes-agent venv,
which makes `crawl4ai` import the WRONG `pydantic` and crash with
`ModuleNotFoundError: No module named 'pydantic_core._pydantic_core'`.

**Always prefix crawl commands with `PYTHONPATH=`** to clear it:

```bash
cd /c/Users/Tiger && PYTHONPATH= uv run --python venv/crawl4ai python your_script.py
```

## Phases

1. **Resolve target.** Single URL, list of URLs, or a deep-crawl (BFS/DFS) seed.
2. **Write a crawl script.** Use `AsyncWebCrawler` with `BrowserConfig(headless=True)`
   and `CrawlerRunConfig`. For RAG, prefer `result.markdown` (clean) or
   `result.fit_markdown` (noise-filtered). The library is async.
3. **Run it** with the `PYTHONPATH=` prefix above. (Browser binary is pre-installed
   via `crawl4ai-setup`; if `Executable doesn't exist` appears, re-run
   `PYTHONPATH= uv run --python venv/crawl4ai crawl4ai-setup`.)
4. **Write output** to a `.md` file under the target location (e.g.
   `AI Sphere/raw/` for vault ingestion, or a temp path for one-off use).
5. **Verify** — print `result.success` and `len(markdown)`. Only claim success
   after a positive signal. Never fabricate crawled content.

## Minimal single-URL example

```python
import asyncio
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig

async def main():
    bc = BrowserConfig(headless=True, verbose=False)
    rc = CrawlerRunConfig(cache_mode="BYPASS")
    async with AsyncWebCrawler(config=bc) as crawler:
        r = await crawler.arun(url="https://example.com", config=rc)
        md = r.markdown or ""
        print("ok=%s chars=%d" % (r.success, len(md)))
        print(md[:800])

asyncio.run(main())
```

## Batch / deep crawl (BFS, max 10 pages)

```python
import asyncio
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, DeepCrawlStrategy

async def main():
    rc = CrawlerRunConfig(cache_mode="BYPASS", deep_crawl=DeepCrawlStrategy(max_pages=10, score_threshold=0.3))
    async with AsyncWebCrawler(config=BrowserConfig(headless=True)) as crawler:
        results = await crawler.arun("https://example.com", config=rc)
        for r in results:
            if r.success:
                print(r.url, len(r.markdown or ""))

asyncio.run(main())
```

## Output Format

A `.md` file (or stdout preview) containing the clean Markdown, plus a one-line
status: `ok=<bool> chars=<n>`. For vault ingestion, save to `AI Sphere/raw/`
and reference from a durable note.

## Vault-ingest wrapper (file crawl -> AI Sphere/raw/)

`scripts/crawl_to_vault.py` crawls a URL and files the clean Markdown into the
vault as a raw capture, fully matching the manual ingest convention:

- Writes `AI Sphere/raw/<DD-MM-YYYY>-<slug>.md` with `type`/`domain`/`platform`/
  `url`/`author`/`published`/`created`/`updated`/`Ingested: true`/`linked_extracts`/
  `origin-hash` (sha256 of the markdown).
- `domain` is always `[[AI Sphere]]`; `type` defaults to `Article` (broad bucket
  for written web content); `author` defaults to `[[unknown|Unknown]]`.
- `platform` resolves from the URL host: the script auto-loads the vault's
  `Platforms/*.md` pages (matching each `website:` host) plus a small alias map
  (youtu.be→YouTube, twitter.com→X, medium.com→Substack, etc.). Unknown hosts
  fall back to `[[unknown|Unknown]]` (a valid existing page, keeps CK08/CK11 green).
- Prepends a dated entry to `AI Sphere/wiki/log.md` and bumps the raw-capture
  count in the `wiki/index.md` footer.
- Refuses to clobber: appends `-N` if the target slug already exists.

Run it:

```bash
cd /c/Users/Tiger && PYTHONPATH= uv run --python venv/crawl4ai python \
  "$HOME/AppData/Local/hermes/skills/crawl4ai/scripts/crawl_to_vault.py" \
  "https://example.com/article" --title "Human Title" --type Article
```

It prints `OK path=... chars=... hash=...` on success, or `CRAWL_FAILED ...`
on a failed crawl (non-zero exit). Promote to a durable Extract only on demand.

## Anti-Patterns

- Running without `PYTHONPATH=` (imports wrong pydantic → crash).
- Using the hermes-agent venv to install/run crawl4ai.
- Claiming a crawl succeeded without printing `result.success` / char count.
- Inventing Markdown content when the browser binary is missing — run setup instead.
- Crawling authenticated/paywalled pages without stored browser profiles.
- Writing a `platform:` wikilink to a page that doesn't exist (breaks CK08).

## Tools Used

- `terminal` — run the venv python with the `PYTHONPATH=` guard.
- `write_file` — persist Markdown output, the crawl script, and the wrapper.
