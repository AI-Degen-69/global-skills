---
name: hermes-plugins-setup
description: Use when installing and configuring Hermes plugins for automation.
author: Hermes Agent
version: 1
---

# Hermes Plugins Setup

This skill covers installing and configuring essential Hermes plugins for automation workflows, specifically the Open Second Brain memory plugin and the Hermes Workflows orchestration plugin.

## When to Use

Use this skill when setting up a new Hermes Agent environment for advanced automation, persistent memory, or workflow orchestration (e.g., for a "Dark Factory" setup).

## Steps

### 1. Install Open Second Brain (Memory Plugin)

```bash
hermes plugins install itechmeat/open-second-brain --enable
hermes gateway restart
```

### 2. Publish CLI Commands

After installation, publish the `o2b` and `vault-log` CLI tools to your PATH:

```bash
~/.hermes/plugins/open-second-brain/scripts/o2b install-cli
```

> **Note**: On Windows with Git-Bash/MSYS, the `o2b install-cli` command may fail due to symlink permission issues. If you encounter `EPERM: operation not permitted, symlink`, run the Hermes terminal as Administrator or adjust Windows Developer Settings to allow symlink creation without elevation.

### 3. Configure Open Second Brain Locally

Choose or create an Obsidian-compatible vault folder, then persist the minimal local config Hermes actually needs. On Windows/Git-Bash this is the most reliable path because it avoids stale CLI assumptions and backslash-path pitfalls.

Write `~/.config/open-second-brain/config.yaml` (Windows: `C:/Users/<user>/.config/open-second-brain/config.yaml`) with:

```yaml
vault: "C:/path/to/vault"
agent_name: "hermes"
timezone: "Asia/Jerusalem"
```

Rules:
- Use **forward slashes** in the vault path on Windows.
- `agent_name` is the identity that appears in Brain log entries.
- `timezone` must be an IANA timezone.

### 4. Verify the Local Open Second Brain Config

Prefer the plugin wrapper directly, even if `o2b` is not yet on PATH:

```bash
~/.hermes/plugins/open-second-brain/scripts/o2b status
~/.hermes/plugins/open-second-brain/scripts/o2b doctor --vault "/path/to/your/vault"
```

You want positive evidence:
- `config_exists: true`
- `[OK] vault_writeable`
- `[OK] config_writeable`

If the bare `o2b` command is unavailable, that is a PATH/symlink problem, **not** proof that Open Second Brain itself is broken.

### 5. Set Open Second Brain as Memory Provider and Verify Hermes

```bash
hermes memory setup   # choose open-second-brain when prompted
hermes gateway restart
hermes memory status
```

Success criteria:
- `Provider: open-second-brain`
- `Status: available`

If `hermes memory status` already reports `open-second-brain` + `available`, Hermes memory is working even when no MCP server is registered.
### 6. Install Hermes Workflows (Orchestration Plugin)

```bash
hermes plugins install itechmeat/hermes-workflows --enable
hermes gateway restart
```

### 7. Verify Workflows CLI

The plugin provides a CLI wrapper at `~/.hermes/plugins/hermes-workflows/bin/hermes-workflows`. Ensure it is callable:

```bash
hermes-workflows --help
```

> **Note**: The `hermes-workflows` command relies on `bun` and TypeScript (`tsc`) for validation. If you see errors like `bun: command not found: tsc`, install the Bun runtime and ensure TypeScript is available:
> - Install Bun: https://bun.sh/
> - The plugin’s `validate` script runs `tsc --noEmit`; having TypeScript installed globally or via the project’s dev dependencies is required for full validation, though runtime execution may still work.

### 8. Create a Workspace for Workflows (Optional)

To keep your workflow files organized, create a directory under your Hermes home:

```bash
mkdir -p ~/.hermes/workflows
```

You can then place workflow YAML files there and reference them with `--project` or by setting the workflow roots.

### 9. Test a Simple Workflow

Create a minimal workflow file (e.g., `test.workflow.yaml`):

```yaml
id: test
name: Test Workflow
version: 1
scope:
  type: global
trigger:
  type: manual
nodes:
  - id: hello
    type: agent_task
    title: Say Hello
    profile: default
    prompt: |
      Say hello in a friendly way.
  - id: done
    type: finish
    title: Done
    outcome: success
edges:
  - from: hello
    to: done
```

Validate and run it:

```bash
hermes-workflows validate test
hermes-workflows run test
```

### 10. Troubleshooting

- **Symlink errors on Windows**: Run your terminal as Administrator or enable Developer Mode in Windows Settings > For Developers > Allow symbolic links.
- **`bun` not found**: Install Bun from https://bun.sh/ and ensure `~/.bun/bin` is in your PATH.
- **TypeScript errors during validation**: Install Node.js and TypeScript (`npm install -g typescript`) or rely on the runtime only (validation is optional for execution).
- **MCP server connection fails**: separate the layers before changing anything.
  1. Verify the plugin itself through the wrapper path first:
     ```bash
     ~/.hermes/plugins/open-second-brain/scripts/o2b status
     ~/.hermes/plugins/open-second-brain/scripts/o2b doctor --vault "/path/to/vault"
     ```
  2. Verify Hermes memory independently:
     ```bash
     hermes memory status
     ```
     If this shows `Provider: open-second-brain` and `Status: available`, the memory-provider path is healthy even if MCP is unregistered.
  3. Only register MCP if you specifically need O2B tools exposed as an MCP server. Prefer the wrapper command (`o2b mcp ...`) or the plugin's documented install flow; do **not** rely on stale `bun run .../src/cli/main.ts mcp` recipes.
## References

- `references/open-second-brain-windows-live-setup.md` — Windows/Git-Bash recovery path for Open Second Brain when Hermes memory is configured but availability is unclear; includes minimal config contract, wrapper-path verification, and Honcho cleanup boundary.
- Open Second Brain plugin: https://github.com/itechmeat/open-second-brain
- Hermes Workflows plugin: https://github.com/itechmeat/hermes-workflows
- Hermes Agent documentation: https://hermes-agent.nousresearch.com/docs

## Troubleshooting

### Symlink Permission Errors on Windows

When running `o2b install-cli`, you may encounter:
```
EPERM: operation not permitted, symlink
```

**Solution**: Run your terminal as Administrator, or enable Developer Mode in Windows Settings:
1. Go to Settings > Update & Security > For Developers
2. Select "Developer Mode" to allow symlink creation without elevation.

### Vault Initialization Fails with "disallowed character (\\\"\\\\\\\\\\\")"

If you see:
```
error: failed to persist plugin config: config value for \"vault\" contains a disallowed character (\"\\\\\"); reject rather than silently corrupting on read-back
```

**Solution**: This is due to a validation in the Open Second Brain plugin that rejects backslashes in paths. As of the session, a temporary fix is to modify the plugin's source code:

1. Navigate to the plugin directory:
   ```
   ~/.hermes/plugins/open-second-brain/src/core/config.ts
   ```
2. Change line 30 from:
   ```ts
   const CONFIG_VALUE_REJECTED_CHARS = ['\"', \"\\\\\", \"\\n\", \"\\r\"] as const;
   ```
   to:
   ```ts
   const CONFIG_VALUE_REJECTED_CHARS = ['\"', \"\\n\", \"\\r\"] as const;
   ```
   (Remove the backslash from the array.)

> **Note**: This is a workaround. Ideally, the plugin should be updated to handle Windows paths properly. Keep an eye on upstream fixes.

### Hermes Workflows Validation Fails Due to Missing tsc

When running `hermes-workflows validate`, you may see:
```
bun: command not found: tsc
```

**Solution**: Install TypeScript globally or ensure it's available in your PATH:
```bash
npm install -g typescript
```
Alternatively, if you only need to run workflows (not validate), you can skip the validation step.

### MCP Server Connection Issues

If the MCP server for Open Second Brain fails to connect, ensure you are setting the required environment variables:
- `VALET_DIR`: Absolute path to your vault (use forward slashes or WSL path)
- `VALET_AGENT_NAME`: Your agent name (e.g., "hermes-main")
- `VALET_TIMEZONE`: Your IANA timezone (e.g., "Asia/Jerusalem")

Test the MCP server manually:
```bash
VALET_DIR="/path/to/vault" VALET_AGENT_NAME="hermes-main" VALET_TIMEZONE="Asia/Jerusalem" bun run ~/.hermes/plugins/open-second-brain/src/cli/main.ts mcp
```
You should see:
```
[mcp] open-second-brain listening on stdio (vault=/path/to/vault)
```

### Hermes Workflows Command Not Found or Python Module Errors

If running `hermes-workflows` results in an error like:
```
Error while finding module specification for 'hermes_workflows.cli' (ModuleNotFoundError: No module named 'hermes_workflows')
```
or simply `hermes-workflows: command not found`, this indicates the Python wrapper cannot find the Hermes Workflows module.

**Solution 1**: Set the `HERMES_AGENT_HOME` environment variable to point to your Hermes installation directory before running the command:
```bash
set HERMES_AGENT_HOME=C:/Users/Tiger/AppData/Local/hermes/hermes-agent
hermes-workflows run test
```

**Solution 2**: Bypass the wrapper and use the Bun CLI directly for validation and workflow operations:
- Validate a workout:
  ```bash
  bun run ~/.hermes/plugins/hermes-workflows/packages/core/src/cli.ts validate /path/to/workflow.yaml
  ```
- Create a run:
  ```bash
  bun run ~/.hermes/plugins/hermes-workflows/packages/core/src/cli.ts run-create --db /tmp/test.db --id test-run-1 /path/to/workflow.yaml
  ```
- Advance the run:
  ```bash
  bun run ~/.hermes/plugins/hermes-workflows/packages/core/src/cli.ts advance /path/to/workflow.yaml --db /tmp/test.db --run-file /tmp/run0.json
  ```
  (See the skill's references for full examples of creating and advancing runs.)

Note: During this session, we found that directly using the Bun CLI was reliable when the Python wrapper encountered path or module issues.