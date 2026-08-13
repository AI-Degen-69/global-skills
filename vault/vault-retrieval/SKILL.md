---
name: vault-retrieval
description: Use when Robert asks about existing vault knowledge. Retrieve answers from the current vault cheaply before re
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows]
metadata:
  hermes:
    tags: [obsidian, vault, retrieval, search, provenance]
    related_skills: [vault-umbrella, vault-compounding-loop, vault-ingestion]
---

# Vault Retrieval

## Overview

This skill answers from existing vault material without ingesting new sources. Follow a cheap-to-expensive retrieval path, distinguish sourced vault facts from agent inference, and only touch raw captures when provenance or missing detail requires it.

## When to Use

- Robert asks what the vault already knows about a topic.
- You need existing notes, outputs, or indexes before proposing new ingestion.
- You need to verify whether a synthesis already exists.

Do not use this skill when the task is actually ingestion or structural maintenance.

## Retrieval Order

1. `vault-index.md`
2. target domain `wiki/index.md`
3. domain `outputs/` for prior source-backed synthesis
4. frontmatter, title, and index search
5. focused full-note reads for top candidates
6. raw only when provenance or missing detail requires it

## Answering Discipline

- Distinguish direct vault facts from your synthesis.
- If retrieval reveals stale indexing or missing ingestion, report it clearly.
- Do not create new vault files from the answer unless a separate provenance-backed compounding decision justifies it.

## Common Pitfalls

1. Jumping straight to raw captures without checking curated notes and outputs.
2. Mixing vault facts and inference without labeling the difference.
3. Turning a retrieval question into unasked ingestion work.
4. Saving ordinary chat answers back into the vault.
5. **Checking implementation status in Hermes or other systems before consulting the vault** — For questions about what the vault already knows, always follow the cheap-to-expensive retrieval path first. Vault presence does not confirm implementation status (see AGENTS.md "Vault ≠ Implementation Boundary"), but the vault is the correct source for existing vault knowledge.

## Verification Checklist

- [ ] Followed the cheap-to-expensive retrieval order.
- [ ] Used raw only when necessary.
- [ ] Distinguished sourced vault facts from inference.
- [ ] Did not perform unasked ingestion.
- [ ] Did not create unsupported output files.
