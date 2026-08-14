#!/usr/bin/env python3
"""
crawl_to_vault.py — Crawl a URL with crawl4ai and file the clean Markdown into
the Vault as a raw capture under AI Sphere/raw/, with proper frontmatter, a
sha256 origin-hash, a log.md entry, and an index footer raw-count bump.

Run from the crawl4ai venv (PYTHONPATH cleared to avoid hermes-agent pydantic clash):
    PYTHONPATH= uv run --python venv/crawl4ai python \
        <skill>/scripts/crawl_to_vault.py <URL> [--title ".."] [--slug ".."] [--type Article]

The crawl + vault write are both done here so the agent just invokes and verifies.
"""
import argparse
import asyncio
import hashlib
import re
import sys
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig

VAULT = Path(r"C:\Users\Tiger\Vault")
DOMAIN = "AI Sphere"
RAW_DIR = VAULT / DOMAIN / "raw"
LOG = VAULT / DOMAIN / "wiki" / "log.md"
INDEX = VAULT / DOMAIN / "wiki" / "index.md"

# Extra host aliases not derivable from the Platform pages' website: fields.
# Key = registered host (or exact host); value = platform page name (matches the
# Platform page's `name:` field, which is what CK11 expects in the wikilink).
PLATFORM_ALIASES = {
    "youtu.be": "YouTube",
    "twitter.com": "X",
    "medium.com": "Substack",        # Medium-hosted blogs resolve via Substack-style blog bucket
    "news.ycombinator.com": "HackerNews",
    "finance.yahoo.com": "Yahoo Finance",
    "gemini.google.com": "Gemini",
    "notebooklm.google.com": "NotebookLM",
    "obsidian.md": "ObsidianPlatform",
    "skills.wondel.ai": "Wondel AI Skills",
    "wondelai.com": "WondelAi",
    "wondelai-org": "WondelAi",
    "algotrading101.com": "AlgoTrading101",
    "beehiiv.com": "beehiiv",
    "betterstack.com": "Better Stack",
    "every.to": "Every",
    "signals.forwardfuture.ai": "Forward Future",
    "honcho.dev": "Honcho",
    "impeccable.style": "Impeccable",
    "schema.org": "Schema.org",
    "stockstory.org": "StockStory",
    "todoist.com": "Todoist",
    "wikipedia.org": "Wikipedia",
    "en.wikipedia.org": "Wikipedia",
}

# Loaded at runtime from the vault's Platform pages (name: + website:).
_PLATFORM_HOSTS = None  # list of (host, name)


def _load_platform_hosts() -> list:
    global _PLATFORM_HOSTS
    if _PLATFORM_HOSTS is not None:
        return _PLATFORM_HOSTS
    hosts = []
    plat_dir = VAULT / "Platforms"
    if plat_dir.is_dir():
        for p in plat_dir.glob("*.md"):
            txt = p.read_text(encoding="utf-8", errors="replace")
            nm = re.search(r'^name:\s*"?([^"\n]+?)"?\s*$', txt, re.M)
            wb = re.search(r'^website:\s*"?([^"\n]+?)"?\s*$', txt, re.M)
            if not (nm and wb):
                continue
            name = nm.group(1).strip().strip('"')
            web = wb.group(1).strip().strip('"')
            if web.startswith("http"):
                try:
                    host = urlparse(web).netloc.lower()
                except Exception:
                    host = ""
                if host:
                    hosts.append((host, name))
    _PLATFORM_HOSTS = hosts
    return hosts


def resolve_platform(url: str) -> str:
    """Resolve a URL host to an existing Platform page wikilink, else [[unknown|Unknown]]."""
    host = urlparse(url).netloc.lower()
    host = host[4:] if host.startswith("www.") else host
    reg = host  # best-effort registered domain (keeps subdomain, e.g. news.ycombinator.com)
    # 1) Exact/alias match.
    if host in PLATFORM_ALIASES:
        return f"[[{PLATFORM_ALIASES[host]}]]"
    if reg in PLATFORM_ALIASES:
        return f"[[{PLATFORM_ALIASES[reg]}]]"
    # 2) Match against vault platform pages by host (handles subdomains + registered domain).
    for phost, name in _load_platform_hosts():
        ph = phost[4:] if phost.startswith("www.") else phost
        if host == ph or host.endswith("." + ph) or reg == ph or reg.endswith("." + ph):
            return f"[[{name}]]"
    return "[[unknown|Unknown]]"


TODAY = date.today().strftime("%d-%m-%Y")  # DD-MM-YYYY (vault convention)


def slugify(text: str, limit: int = 60) -> str:
    text = text.lower().strip()
    text = re.sub(r"^https?://", "", text)
    text = re.sub(r"^www\.", "", text)
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    text = text.strip("-")
    return text[:limit].strip("-") or "untitled"


def bump_raw_count(index_text: str) -> str:
    # Footer line looks like: *82 wiki pages · 28 raw captures · regenerated 05-08-2026*
    m = re.search(r"(\*\s*\d+\s*wiki pages\s*·\s*)(\d+)(\s*raw captures\s*·\s*regenerated\s*)(\d{2}-\d{2}-\d{4})(\s*\*)", index_text)
    if not m:
        return index_text
    new_count = int(m.group(2)) + 1
    return (
        index_text[: m.start()]
        + m.group(1) + str(new_count) + m.group(3) + TODAY + m.group(5)
        + index_text[m.end():]
    )


def prepend_log(log_text: str, block: str) -> str:
    # Insert after the "Append-only chronological record..." preamble line.
    marker = "Append-only chronological record of all wiki operations."
    idx = log_text.find(marker)
    if idx == -1:
        return block + "\n---\n" + log_text
    # Find end of that line + following blank line.
    nl = log_text.find("\n", idx)
    rest = log_text[nl + 1:]
    # Skip one blank line if present.
    if rest.startswith("\n"):
        insert_at = nl + 1 + 1
    else:
        insert_at = nl + 1
    return log_text[:insert_at] + block + "\n---\n" + log_text[insert_at:]


async def crawl(url: str) -> tuple[bool, str, str]:
    bc = BrowserConfig(headless=True, verbose=False)
    rc = CrawlerRunConfig(cache_mode="BYPASS")
    async with AsyncWebCrawler(config=bc) as crawler:
        r = await crawler.arun(url=url, config=rc)
        md = r.markdown or ""
        title = ""
        try:
            title = (r.metadata or {}).get("title", "") or ""
        except Exception:
            pass
        return bool(r.success), md, title


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("url")
    ap.add_argument("--title", default="")
    ap.add_argument("--slug", default="")
    ap.add_argument("--type", default="Article")
    args = ap.parse_args()

    ok, markdown, crawled_title = asyncio.run(crawl(args.url))
    if not ok or not markdown:
        print("CRAWL_FAILED ok=%s chars=%d" % (ok, len(markdown)), file=sys.stderr)
        return 1

    slug = args.slug or slugify(args.title or crawled_title or args.url)
    title = args.title or crawled_title or slug
    platform = resolve_platform(args.url)
    raw_path = RAW_DIR / f"{TODAY}-{slug}.md"

    # Avoid clobbering an existing capture.
    if raw_path.exists():
        i = 1
        while raw_path.exists():
            raw_path = RAW_DIR / f"{TODAY}-{slug}-{i}.md"
            i += 1

    origin_hash = "sha256-" + hashlib.sha256(markdown.encode("utf-8")).hexdigest()

    frontmatter = (
        "---\n"
        f'title: "{title}"\n'
        f'type: "[[{args.type}]]"\n'
        f'domain: "[[{DOMAIN}]]"\n'
        f"platform: {platform}\n"
        f'url: "{args.url}"\n'
        'author:\n  - "[[unknown|Unknown]]"\n'
        f'published: "{TODAY}"\n'
        f'created: "{TODAY}"\n'
        f'updated: "{TODAY}"\n'
        "Ingested: true\n"
        "linked_extracts:\n"
        f'origin-hash: "{origin_hash}"\n'
        "---\n\n"
    )
    # Vault convention is LF line endings (use newline="\n" to override Windows CRLF default).
    raw_path.write_text(frontmatter + markdown + "\n", encoding="utf-8", newline="\n")

    # Log entry.
    log_block = (
        f"## [{TODAY}] ingest (crawl) | {slug}\n\n"
        f"**Source:** Web crawl of `{args.url}` via crawl4ai (v0.9.2) → "
        f"`{DOMAIN}/raw/{raw_path.name}` — {title}. Clean Markdown capture "
        f"({len(markdown)} chars), platform {platform}. Filed as raw provenance "
        f"for RAG / radar ingestion.\n\n"
        f"**Origin-hash:** `{origin_hash}`\n\n"
        f"**Status:** ✅ Raw capture written; no durable extract created (promote on demand).\n"
    )
    log_text = LOG.read_text(encoding="utf-8")
    LOG.write_text(prepend_log(log_text, log_block), encoding="utf-8", newline="\n")

    # Bump index footer raw count.
    idx_text = INDEX.read_text(encoding="utf-8")
    INDEX.write_text(bump_raw_count(idx_text), encoding="utf-8", newline="\n")

    print(f"OK path={raw_path} chars={len(markdown)} hash={origin_hash}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
