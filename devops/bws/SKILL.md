---
name: bws
description: Use when using the bws CLI for Bitwarden Secrets Manager secrets.
---

# Bitwarden Secrets Manager CLI (`bws`)

Native CLI for Bitwarden Secrets Manager. Authenticated from `BWS_ACCESS_TOKEN` (already present in this environment). Use this instead of the `bitwarden-sdk` Python package — the SDK import path is brittle under MSYS and the CLI is already installed.

## 📌 Fixed facts (this machine)
- **CLI binary**: `C:\Users\Tiger\.local\bin\bws.exe` (on PATH). Version `2.1.0`.
- **PROJECT_ID** (where secrets live): `e0dd5874-53e4-4b06-bfc1-b49000e19239`
- **ORG_ID**: `ab1196ea-4214-4fec-9880-b49000e0837e`
- **Token env var**: `BWS_ACCESS_TOKEN` (94 chars). CLI resolves the org automatically — no org ID needed for `list`/`get`.
- **Auth is via env var only** — there is no `bw login` session. `bws` reads `BWS_ACCESS_TOKEN` from the environment at startup.

## 🛠️ Commands
```powershell
bws secret list                      # all secrets; VALUES MASKED on screen (sk-or-...5ac9)
bws secret list --output json        # parseable; values still masked
bws secret list --output table       # readable table

bws secret get <ID>                  # FULL UNMASKED value, returned as JSON
                                     #   extract: bws secret get <ID> | python -c "import sys,json;print(json.load(sys.stdin)['value'])"

bws secret create <KEY> <VALUE> <PROJECT_ID>   # ADD  (positional! no flags)
bws secret edit   <ID> <KEY> <VALUE> <PROJECT_ID>
bws secret delete <ID> [<ID>...]    # accepts multiple IDs

bws project list                     # see project IDs
```
- `list` **masks** values on console. `get <id>` returns the **real** value in JSON — use it when you need the unmasked secret.

## 🐚 Shell command family (migrated from Infisical)
**IMPORTANT: these are PowerShell functions, NOT bash scripts.** On this host the
terminal is **PowerShell 7**; `keys`/`kadd`/`kremove`/`kfind`/`kget`/`ktest`/`kdash`
are functions defined in `C:\Program Files\PowerShell\7\profile.ps1` that call `.ps1`
scripts in `C:\Program Files\PowerShell\7\scripts\Infisical\` (filenames kept as
`Infisical-*.ps1` for profile stability). There are NO bash equivalents in
`~/.local/bin` — do not create or edit those, they will never run in pwsh.

The `.ps1` scripts call `bws` (absolute path `C:\Users\Tiger\.local\bin\bws.exe`,
with `Get-Command bws` fallback) and require `BWS_ACCESS_TOKEN`. They resolve
key-name → UUID where bws needs an ID.

| Function | Calls | Notes |
|---|---|---|
| `keys` | `Bws-Get.ps1` → `bws secret list` | lists key names, masked |
| `kfind <PAT>` | `Bws-Find.ps1` | case-insensitive regex; prompts index to copy unmasked value |
| `kadd -Name X -Value Y` | `Bws-Add.ps1` → `bws secret create` | profile forwards `@Args` |
| `kremove -Name X` | `Bws-Remove.ps1` | deletes ALL matches by name (bws dup keys) |
| `ktest [-All]` | `Bws-Test.ps1` | probes every key vs Ollama/OpenRouter; `Get-VaultSecrets` rewritten onto `bws` |
| `kdash` | `Bws-Dashboard.ps1` | opens `https://vault.bitwarden.com/#/sm` |

- All require `BWS_ACCESS_TOKEN` (reopen terminal if "Missing access token").
- `kremove` deletes every match by name — handles bws duplicate-key names safely.
- PROJECT_ID read from `$BW_PROJ` (default `e0dd5874-...`) inside each script.
- To change behavior, edit the `.ps1` scripts directly; the profile just dispatches.

## ⚠️ Pitfalls (all verified on this host)
1. **"Missing access token" in an already-open terminal** — the token is persisted in the **Windows User** env store, but a terminal tab opened *before* that write never sees it (Windows injects env only at process start). **Fix: close + reopen the tab**, then re-run. NOT a broken setup.
   - If a fresh pwsh still fails, re-persist once:
     ```powershell
     pwsh.exe -NoProfile -Command '[Environment]::SetEnvironmentVariable("BWS_ACCESS_TOKEN",$env:BWS_ACCESS_TOKEN,"User")'
     ```
     (only works if the current Hermes session still has the token in its own process env).
2. **`bws run` (inject-into-command) CRASHES** on this Windows/MSYS spawn path (`crates\bws\src\command\run.rs` panic). Do NOT use `bws run`. To read a value, use `bws secret get <ID>` and parse JSON.
3. **`[WinError 5] Access is denied` on `auth.json` rename** — a concurrent multi-session write race when 2+ Hermes sessions refresh auth simultaneously. Transient; `auth.json` stays intact (the losing writer just logs the error). Nothing to fix from the shell.
4. **Use Windows-style paths in `pwsh.exe`**, not MSYS `/c/Users/...` — the MSYS layer rewrites them to `C:\c\...` and breaks Python/credential calls.
5. **Python SDK import is brittle** here: `hermes-agent\venv` has `bitwarden-sdk` 2.1.0 installed, but `import bitwarden` fails when invoked through MSYS-mangled paths. Prefer the `bws` CLI; avoid the SDK unless specifically needed.

## 🔎 Local cache check (do this BEFORE claiming a secret is missing)
Hermes mirrors live secrets to `C:\Users\Tiger\AppData\Local\hermes\cache\bws_cache.json` with this structure:
```
{ "key": ..., "secrets": { "SECRET_NAME": "value", ... }, "fetched_at": <unix_ts> }
```
Check a key's presence/length (never print the value) before reporting "missing/empty":
```bash
python3 -c "import json;d=json.load(open('C:/Users/Tiger/AppData/Local/hermes/cache/bws_cache.json'));s=d['secrets'];print('len=',len(s.get('KEY_NAME','')))"
```
- `len=0` → key truly absent (or cached value empty).
- `len>0` → secret exists; fetch live with `bws secret get <ID>` if you need it.
- Cache can lag live by a day (refresh is not automatic) — treat cache as a hint, `bws` as source of truth.

## ✅ Verification
After setup, confirm in a **fresh** `pwsh.exe`:
```powershell
bws secret list --output table | Select-Object -First 5
```
Expect ~38 secrets listed with masked values. If it errors with "Missing access token", the tab is stale — reopen it.
