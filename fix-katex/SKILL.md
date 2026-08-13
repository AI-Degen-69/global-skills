---
name: fix-katex
description: "Use when KaTeX mathematical strings render incorrectly (e.g. tabs appearing instead of 	ext) or when you need"
---

# Fix KaTeX Formatting

When invoked, this skill automatically scans the provided target (or defaults to `web/src`) for KaTeX formatting anti-patterns and fixes them.

## The Issue

Using standard JSX string literals for LaTeX expressions leads to JavaScript evaluating escape sequences like `\t` as tabs. The double-escaping workaround (`\\text{}`) is hard to read and easily broken when copy-pasting standard LaTeX.

The required solution across this project is to use `` String.raw`...` `` template literals so that a single backslash is preserved exactly as written.

## Execution

Run the provided automated script to fix occurrences in the codebase:
```bash
node .agents/skills/fix-katex/scripts/autofix.js [target_path]
```

If no `target_path` is provided, it defaults to scanning `web/src/components`.

After running the script, ALWAYS verify with:
```bash
npm run lint:tsc
```
