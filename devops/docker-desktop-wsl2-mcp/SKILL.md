---
name: docker-desktop-wsl2-mcp
description: Use when a service runs in WSL2 Docker but Python gets ConnectionReset/421, or when planning a new local Docke
---

# Docker Desktop beats WSL2-daemon for Windows-native Python clients

## When to use
- You run Docker inside WSL2 (bare `dockerd`) and a Windows-native Python client (Hermes MCP, `urllib`, `requests`) cannot reliably connect to a published port.
- Symptoms: `curl.exe localhost:PORT` works but Python `urllib` throws `ConnectionResetError [WinError 10054]` / `IncompleteRead`; or HTTP `421 Misdirected Request` from uvicorn/FastMCP.
- You are about to set up a local Docker stack on Windows and want it Python-reliable from the start.

## Root causes (verified on this machine)
1. **WSL2 localhost forwarding is flaky for raw Python sockets.** WSL2 publishes ports via a loopback proxy that `curl.exe` traverses but Python's `urllib` often hits with resets/incomplete reads (non-deterministic).
2. **FastMCP/uvicorn Host check.** Streamable-HTTP MCP servers reject `Host` headers not equal to `localhost` → `421 Misdirected Request`. Python derives `Host` from the URL (e.g. `172.30.x.x:8002`), triggering 421.
3. **`netsh interface portproxy v4tov4` is unreliable for SSE.** It forwards TCP but mangles chunked SSE streams → `10054` for Python clients. Do not rely on it.

## The fix: Docker Desktop for Windows
Docker Desktop publishes container ports directly to Windows `localhost` (reliable for Python). Procedure:

### 1. Tear down the WSL-daemon stack
```bash
wsl.exe -u root bash -lc "
cd /mnt/c/Users/Tiger/Agents/Projects/<repo>
docker compose down -v --rmi all
docker volume rm hf-cache 2>/dev/null
docker system prune -f
service docker stop
# uninstall the manually-installed engine so Docker Desktop is the sole owner
apt-get remove -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
"
```
### 2. Install Docker Desktop (needs admin/UAC)
```powershell
curl.exe -L -o $env:TEMP\docker-desktop.exe "https://desktop.docker.com/win/main/amd64/Docker%20Desktop%20Installer.exe"
Start-Process $env:TEMP\docker-desktop.exe -ArgumentList 'install','--accept-license','--backend=wsl-2' -Wait
```
Approve the UAC prompt when it appears. After install, Docker Desktop is the default context (`desktop-linux`).
### 3. Re-deploy from Windows (not WSL)
```powershell
cd C:\Users\Tiger\Agents\Projects\<repo>
docker compose up -d
```
Ports now appear on Windows `localhost` reliably.
### 4. Verify with the SAME client that will use it
```python
import urllib.request, json
url="http://localhost:8002/mcp"   # Docker Desktop publishes here natively
# initialize + tools/list ...
```
If `localhost` works in Python here, Hermes's MCP client will too.

## Pitfalls
- Do NOT configure Hermes MCP `url` with the WSL IP (`172.30.x.x`) — uvicorn 421. Use `http://localhost:PORT/mcp`.
- Do NOT add `netsh portproxy` as the "fix" — it breaks Python SSE.
- Keep the cloned repo on the Windows disk; Docker Desktop reads `docker-compose.yml`/`.env` from there.
- Brave API key lives in the repo `.env` (not Hermes `.env`). Compose interpolates it into `ENGINE_BRAVE_API_KEY`.
- Scraper image entrypoint scripts must be LF (not CRLF) or the container crashes with "no such file or directory" (CRLF shebang bug). Fix:
  `python3 -c "open(p,'wb').write(open(p,'rb').read().replace(b'\r\n',b'\n'))"`.

## Verification
- `docker compose ps` → all services `healthy`/`running`.
- `curl.exe localhost:8081/health` → `{"status":"ok"...}` with target engines `ok`.
- Python `urllib` `initialize` to `http://localhost:8002/mcp` returns a session id (not 421/10054).
