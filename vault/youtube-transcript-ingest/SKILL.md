---
name: youtube-transcript-ingest
description: Use when re-capturing a clean YouTube transcript into the vault.
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows, linux, macos]
---

# YouTube Transcript Ingest (re-capture)

## When to use
- A `_Inbox/` YouTube capture is a rough web-clip (thin summary, mixed-language transcript, or missing the actual spoken content) and you need the real transcript.
- You are ingesting a video and want the verbatim transcript in the `raw/` file rather than a link-only stub.
- Robert says to "re-capture" or "get the transcript" for a video already ingested.

## Do NOT use raw yt-dlp for transcripts
yt-dlp's `--write-auto-subs` downloads VTT that carries **word-level `<c>` timing tags and echoes every phrase twice** (a timed version + a clean version). It is noisy and requires non-trivial de-noising. Prefer the `youtube-content` skill, which returns clean `timedtext` (no duplicate/garbage lines).

## Procedure
1. **Load the helper skill** `youtube-content` (path `media/youtube-content/SKILL.md` — the bare `youtube-content/SKILL.md` is a stray copy with no `scripts/`). Its helper is `media/youtube-content/scripts/fetch_transcript.py`, run via `uv run python3`.
2. **Pick language by ORIGINAL audio, not by convenience:**
   - Default → `--language en`.
   - If the video's **original audio is Hebrew** → request the Hebrew track (`--language he`) when available.
   - If the requested language returns empty → retry with no `--language` to get any available transcript, and note the actual language to Robert.
3. **Fetch** (bash terminal — MSYS resolves `uv`/`python3`; the Windows python shim does not):
   ```bash
   uv run python3 "C:/Users/Tiger/AppData/Local/hermes/skills/media/youtube-content/scripts/fetch_transcript.py" "URL" --text-only --language en > /tmp/yt.txt 2>/tmp/yte.txt
   ```
   - Validate non-empty output and correct language. Empty + no `--language` retry still empty → transcripts disabled; tell Robert.
   - Dependency missing → `uv pip install youtube-transcript-api`.
4. **Write into the raw file:** keep existing frontmatter, replace the body with the fetched transcript, and **recompute `origin-hash`** (sha256 of the full frontmatter+body) so the extract's `origin-hash` still matches.
5. **Update the extract's `origin-hash`** to the new value if the re-capture changed the raw.
6. Re-run `python3 scripts/check_vault.py` — only your touched files should be clean.

## Pitfalls
- The `youtube-content` SKILL.md references `scripts/fetch_transcript.py`, but the **bare** `youtube-content/` dir has no scripts — use `media/youtube-content/scripts/`.
- `subprocess` from the Windows `python3` shim cannot resolve `yt-dlp`/`uv` from MSYS PATH. Always run yt-dlp/uv from the **bash terminal** tool, never via `python:execute_code`/`subprocess`.
- Never leave the raw with a stale `origin-hash` after re-capturing — the audit and gbrain dedup both key off it.
- Keep the original-language rule strict: English is the default, Hebrew only when the source audio is genuinely Hebrew.

## Index build is a mandatory closeout step (not optional)
After writing raw + extract, the domain `wiki/index.md` MUST be regenerated — hand-editing the index is the weaker path and drifts counts/sections.
1. `python3 scripts/build_index.py --check` — confirm which domains are stale.
2. For each stale domain (back up first; the builder flattens custom date-grouped ordering): `python3 scripts/build_index.py "<Domain>"`.
3. Re-run `--check` → all domains `OK`.
4. Only then run `check_vault.py`.

## Verification
- Transcript file non-empty and in the expected language.
- `origin-hash` in raw and extract match.
- `build_index.py --check` → all domains OK (index regenerated after the ingest).
- `check_vault.py` relevant checks (CK01/03/04/07/11/12/13) PASS.
