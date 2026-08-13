---
name: browser
description: Use when routing a browser task to the right browser skill.
---

# browser

Use this skill only to route to the right browser skill.

## Choose the right skill

- For real browser work — automation, scraping, testing, screenshots, clicks, `js(...)`, `new_tab(...)`, or page inspection — use `browser-harness`.
- For installation, Browser Use cloud setup, API key wiring, Hermes config, or Windows-specific verification/troubleshooting — use `browser-use-hermes-integration`.

## Rule

Do not duplicate runtime instructions here. `browser-harness` is the canonical runtime skill.

## Quick map

- runtime browser work -> `browser-harness`
- setup / integration -> `browser-use-hermes-integration`
