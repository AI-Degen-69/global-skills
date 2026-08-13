---
name: self-hosted-client-connectivity-triage
description: Use when a phone/native app cannot connect to a self-hosted service.
---

# Self-Hosted Client Connectivity Triage

## When to use
- A phone/native app cannot connect to a self-hosted service.
- The user recently changed bind host, port exposure, Tailscale/LAN access, or auth.
- There is ambiguity between network failure, server failure, and client/app compatibility failure.

## Core principle
Separate these three layers early:
1. **Network path** — can the target device reach the host:port at all?
2. **Server surface** — does the service return the expected HTTP page/API for unauthenticated and authenticated flows?
3. **Client compatibility** — is the native app using a different onboarding or readiness probe than the browser path?

Do not treat a native-app timeout as proof the server is unreachable.

## Default workflow
1. Verify the server is bound to the intended interface and port.
2. Probe the target URL directly from the host machine using the same scheme/host/port the client will use.
3. Check at least one **public low-risk endpoint** and one **real UI/auth entrypoint**:
   - health endpoint if available
   - login/root page actually used by humans
4. Compare the client app version against current releases or current source behavior.
5. If browser access works but native app onboarding fails, suspect a client-side readiness/protocol/version mismatch before changing server networking again.
6. Keep exploratory server patches isolated; if a diagnosis path does not yield the live fix, revert the repo before closeout.

## Strong signals and interpretations
- **`/health` works and `/login` or root login page renders** → network path and server bind are good; native-app failure is likely client logic, auth onboarding, or version mismatch.
- **Remote `/api/status` or similar readiness endpoint returns `401` while `/health` is `200` and `/login` is `200`** → the client is reaching the server, but the app is failing at the auth/protocol handshake layer rather than startup, bind, or routing.
- **Health works only on localhost but not on Tailscale/LAN** → bind/firewall/routing problem.
- **Browser on phone can open the login page but app cannot connect** → not a bind issue; investigate native-client readiness checks and app version.
- **App version lags current releases** → compare onboarding/readiness behavior before patching the server.

### Log-reading shortcut
When server access logs are available, look for the remote device IP hitting multiple surfaces:
- repeated remote `GET /health` with `200`
- remote `GET /api/status` with `401`
- remote `GET /login` with `200`

That combination is decisive evidence that the device can reach the service and that the remaining issue is auth/onboarding compatibility, not server startup.

## Verification standard
Positive evidence should include:
- exact URL tested
- HTTP status from at least one health/status endpoint
- HTTP status from the human-facing login/root page
- current client app version vs current release/source version when version skew is plausible

## Pitfalls
- Do **not** assume Tailscale bind changes are still the blocker once `/health` and `/login` are reachable remotely.
- Do **not** leave a repo dirty from speculative compatibility patches unless they are verified as the real fix.
- Do **not** claim a server fix solved a native app issue unless the native app itself was retested successfully.

## Support files
- `references/hermes-webui-android-onboarding.md` — concrete pattern from Hermes WebUI Android vs browser/Tailscale diagnosis.
