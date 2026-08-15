---
name: yt-dlp-caption-capture
description: Use when capturing clean YouTube captions via yt-dlp.
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows]
metadata:
  hermes:
    tags: [youtube, transcript, captions, ingestion, vault]
---

# yt-dlp Caption Capture (clean re-capture)

## Overview
When a YouTube-video ingest lands with a rough, garbled, or low-context transcript (e.g. a mixed Hebrew/English web-clip capture), re-pull the clean captions with `yt-dlp` and rebuild the raw. This produces a far higher-fidelity source artifact than a browser-clipper capture.

## Hard Rules (from Robert)
- **When:** re-capture whenever you suspect the existing capture is missing context or is a messy auto-clip. Do not ship an extract off a low-quality raw.
- **Language:** detect the original-language caption track. **Default to `en` (English)**. Use **Hebrew (`he`) only when Hebrew is the original audio** track. Almost never another language.
- yt-dlp is invoked from the **bash terminal**, never via the Windows Python `subprocess` (the MSYS binary at `~/.local/bin/yt-dlp` is not resolvable from the Windows python shim).

## Procedure

### 1. Detect the original-language track
```bash
yt-dlp --list-subs --no-warnings "<URL>"
```
Find the line like `en-orig  English (Original)` → the prefix before `-orig` is the original language.

### 2. Pick the language
- Original audio = English (or unknown) → `--sub-langs "en"`.
- Original audio = Hebrew (track `he-orig`) → `--sub-langs "he"`.
- Prefer the `-orig` track when present; otherwise the base code.

### 3. Download captions only (no video)
```bash
mkdir -p ./ytcap_tmp
yt-dlp --write-auto-subs --sub-langs "<LANG>" --skip-download --sub-format vtt \
      -o "./ytcap_tmp/%(id)s.%(ext)s" "<URL>"
```
Output: `./ytcap_tmp/<VID>.<LANG>.vtt`.

### 4. De-noise the VTT → paragraph transcript
YouTube emits **each phrase twice**: once with word-level `<c>` timing tags (garbage), once as a clean plain line. Keep ONLY the clean cues.
```python
import re
VID="<VID>"; VTT=f"./ytcap_tmp/{VID}.<LANG>.vtt"
txt=open(VTT,encoding='utf-8').read()
cues,cur=[],None
for ln in txt.splitlines():
    s=ln.strip()
    if s=='' : cur=None; continue
    if s.startswith(('WEBVTT','NOTE','STYLE','Kind:')): cur=None; continue
    if '-->' in ln: cur=[]; cues.append(cur); continue
    if cur is not None and s: cur.append(s)
clean=[]
for c in cues:
    if not c: continue
    j=' '.join(c)
    if '<' in j: continue   # drop <c> timing-tag / echoed cues
    if j.strip(): clean.append(j.strip())
flow=' '.join(clean)
sents=re.split(r'(?<=[.?!])\s+', flow)
paras,buf=[],''
for s in sents:
    s=s.strip()
    if not s: continue
    buf=(buf+' '+s).strip() if buf else s
    if len(buf.split('. '))>=3 and s.rstrip().endswith(('.','!','?')):
        paras.append(buf); buf=''
if buf: paras.append(buf)
paras=[p for p in paras if len(p.split())>2]
transcript="\n\n".join(paras)
```
Key: **any cue containing `<` is dropped** — that single filter removes both the `<c>`-tagged version and the echoed duplicate, leaving only the readable plain line.

### 5. Rebuild the raw
Keep the existing frontmatter; replace the body:
```
# :FabYoutube: [<Title>](<URL>)

*Clean <LANG> auto-captions retrieved via yt-dlp, de-noised (word-level timing tags and echoed duplicates dropped), merged into paragraph transcript.*

<transcript>
```
Recompute `origin-hash` = sha256 of `---\n<frontmatter WITHOUT prior origin-hash>\n---\n\n<body>`. Write the raw, then update the matching extract's `origin-hash` to the same value.

### 6. Verify + build the index (mandatory closeout)
Open the raw: confirm **no `<c>` tags remain** and the text reads as clean, flowing English (or Hebrew). Then:
1. `python3 scripts/build_index.py --check` — confirm which domains are stale.
2. For each stale domain (back up first; the builder flattens custom date-grouped ordering): `python3 scripts/build_index.py "<Domain>"`.
3. Re-run `--check` → all domains `OK`.
4. Only then run `python3 scripts/check_vault.py`.

Hand-editing `wiki/index.md` is NOT an acceptable substitute for the rebuild.

## Pitfalls
- `en-orig` and `en` both contain the dual-cue noise; the parser handles both — do not assume `en-orig` is cleaner.
- Windows Python `subprocess.run(["yt-dlp", ...])` raises `FileNotFoundError`; always run yt-dlp from the bash terminal tool.
- Do NOT commit the `ytcap_tmp/` scratch dir to the vault.
- If a video has **no** captions at all, yt-dlp yields nothing — fall back to Whisper on the downloaded audio (out of scope here).

## Related
- `vault-ingestion` — canonical ingest flow this skill feeds.
- `vault-audit-fix` — run after rebuilding the raw.
