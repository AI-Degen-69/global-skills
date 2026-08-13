---
name: hermes-plugin-compatibility-maintenance
description: Use when a Hermes plugin that patches a core tool breaks after a core update.
---

# Hermes Plugin Compatibility Maintenance

## When to use
- A Hermes plugin monkey-patches a core tool and the tool starts failing after a core update.
- You see errors like `unexpected keyword argument ...`, schema drift, or runtime handler mismatch on a patched tool.
- A local plugin re-registers a tool, wraps a core function, or intercepts runtime tool dispatch.
- Delegation, cron, terminal, or other tool behavior differs from what current Hermes docs/runtime suggest.

## Core idea
Local compatibility plugins often fail not because the core feature is broken, but because the plugin copied an old function signature or forwarding path and stopped passing through newly added parameters.

The durable check is:
1. Identify the enabled plugin.
2. Locate its wrapper/forwarder/registry code.
3. Compare the wrapper signature against the current core tool signature.
4. Check every forwarding path, not just the top-level wrapper.
5. Patch pass-through arguments everywhere the plugin intercepts the tool.
6. Restart Hermes and verify both old and new call shapes.

## Investigation workflow

### 1) Confirm the plugin is enabled
Check the active/global Hermes config for plugin enablement before blaming the core runtime.

Typical evidence to collect:
- config entry under `plugins.enabled`
- plugin directory and `plugin.yaml`
- whether the issue reproduces only in the patched environment

### 2) Inspect the plugin for three common interception points
Search the plugin for:
- runtime wrapper around the tool function
- invoke-tool interception / runtime dispatch patch
- tool re-registration handler / custom schema override

Do not stop after finding only one wrapper. Many plugins patch all three.

### 3) Compare against current Hermes core
Read the current core tool signature and current schema/handler behavior. Focus on newly added parameters such as:
- `background`
- `profile`
- `role`
- `tasks`
- `context_from`
- other new booleans/enums added after the plugin was written

### 4) Patch pass-through, not behavior
Prefer the smallest safe fix:
- add the missing parameter to the plugin wrapper signature
- forward it into the original core function
- forward it through runtime interception
- forward it through the tool registry handler

Avoid redesigning the plugin unless the user asked.

### 5) Verify old and new shapes
After patching and restarting Hermes, verify:
- baseline call without the new parameter still works
- call with the new parameter works
- any plugin-specific extra parameter (for example `profile`) still works
- combined call shape also works

## Frequent pitfall
### Wrapper fixed, handler still broken
A common failure mode is patching only the direct wrapper while forgetting the plugin also:
- intercepts tool invocation, and/or
- re-registers the tool with a lambda handler

If either forwarding path omits the new parameter, the runtime still fails.

### Invoke-tool shims freeze core arity
Plugins that monkey-patch `agent_runtime_helpers.invoke_tool` can break unrelated tools after core adds dispatch parameters. When repairing an invoke-tool interceptor:
- compare against the current `invoke_tool(...)` signature, not just the target tool signature
- forward newer dispatch arguments such as `skip_tool_request_middleware` and `tool_request_middleware_trace`
- include `*extra_args: Any, **extra_kwargs: Any` when wrapping runtime dispatch so future core additions pass through instead of crashing the whole tool layer
- verify a non-target tool call still reaches the original `invoke_tool` path

### Live process still has old monkey patch
Patching the plugin file does not replace functions already loaded into the running Hermes/WebUI process. Verify the patched file in a fresh Python process, then restart Hermes/WebUI before expecting live tools or delegation to use the new shim.

### Discovery fixed, later lifecycle still broken
Another common failure mode is fixing only initial discovery (for example, teaching a CLI wrapper to search the current repo) while leaving later lifecycle operations (`status`, `advance`, `advance-all`, retry paths) dependent on global roots or cwd-sensitive lookup.

When the plugin starts a run from a repo-local artifact, check whether the runtime persists only a logical id or also the resolved absolute spec path. If later operations re-resolve by id only, the fix is incomplete and will break as soon as the operator changes directories or the tick runs elsewhere.

Repair pattern:
- add repo-local discovery for the operator entrypoint,
- persist the resolved artifact path/identity into run state at create time,
- make later lifecycle commands prefer the stored path before falling back to root-based lookup,
- verify from a different cwd than the one used to start the run.

### Windows workspace vs WSL repo path trap
If Hermes is running from a Windows workspace but the target plugin repo lives in WSL, file-edit tools can resolve Linux-looking absolute paths into `C:\\home\\...` and silently miss the real checkout. For WSL-hosted plugin repos:
- verify the actual repo path first,
- prefer editing from inside WSL for the final patch path,
- if a helper script is easier, write it on the Windows side and execute it from WSL via `/mnt/c/...`,
- delete temporary helper files after verification.

## Review standard
When reporting the issue, name:
- the enabled plugin
- the exact file containing the stale wrapper
- the exact upstream/core signature that now differs
- each forwarding path that drops the argument
- the minimal patch scope needed

## Supporting references
- `references/delegate-background-regression-20260619.md` — concrete example: `delegate-profile-contract` dropped the newer `background` parameter from all delegate forwarding paths.
- `references/delegate-background-smoke-test.md` — controlled live-module smoke pattern that stubs async dispatch and verifies `background=true` returns a delegation handle through both invoke-tool and registry-handler paths.
- `references/delegate-sync-profile-role-smoke-test.md` — controlled sync smoke pattern for profile-aware delegation that proves `profile`, `role`, and `parent_agent` survive wrapper, invoke-tool, and registry forwarding and still return a normal JSON result string.
- `references/repo-local-discovery-and-persisted-paths.md` — repo-local workflow/plugin fix pattern: discovery root plus persisted absolute path, with cross-cwd verification.

## Verification addendum for delegate compatibility patches
When the target behavior is "background delegation should return a handle instead of crashing", do not stop at source inspection or a direct wrapper call.

Run a controlled live-module smoke that:
1. imports the installed plugin and live Hermes modules,
2. stubs `_build_child_agent` and `dispatch_async_delegation` to avoid spawning a real child,
3. calls `plugin.register(None)`,
4. exercises `agent.agent_runtime_helpers.invoke_tool(..., "delegate_task", ...)`, and
5. exercises the registered `delegate_task` handler from `tools.registry`.

Success criteria:
- no `TypeError` on `background=true`,
- returned JSON contains `status="dispatched"`, `delegation_id`, and `mode="background"`,
- the schema still exposes both `profile` and `background`.

This catches the common case where one forwarding path was patched but another still drops the newer argument.

### Sync contract variant for profile-aware delegation
When the target behavior is "sync delegation should still accept profile-aware fields and return a normal result string", use the same live-module pattern but stub `_run_single_child` instead of async dispatch.

Success criteria:
- no `TypeError` for `profile`, `role`, or `parent_agent`,
- direct wrapper, invoke-tool interception, and registry handler each return a **string** result,
- `json.loads(result)["results"][0]["status"] == "completed"`, and
- the summary or another sentinel proves explicit `role` survived forwarding.

See `references/delegate-sync-profile-role-smoke-test.md` for the concise recipe.
