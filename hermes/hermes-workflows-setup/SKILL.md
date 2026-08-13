---
name: hermes-workflows-setup
description: Use when configuring Hermes Workflows for the dashboard pipeline.
category: hermes
---

# Hermes Workflows Setup Skill

## Purpose
Configure and troubleshoot the Hermes Workflows plugin so that the dashboard's Workflows page loads and displays available workflows.

## When to Use
- After installing or enabling the `hermes-workflows` plugin.
- When the dashboard shows "Failed to load workflows".
- To set up a new workflow directory or verify an existing one.

## Prerequisites
- Hermes Agent is running.
- You have access to the terminal/command line.
- The `hermes-workflows` plugin is available (bundled or from Git).

## Steps

### 1. Verify Plugin Status
```bash
hermes plugins list | grep workflow
```
Ensure the line shows `enabled`. If not, enable it:
```bash
hermes plugins enable hermes-workflows
hermes gateway restart   # required for the plugin to take effect
```

### 2. Set (or Verify) the Global Workflows Path
The dashboard loads workflows from the folder defined by `plugins.workflows.global_workflows_path`. Check current value:
```bash
hermes config show | grep -A1 -B1 workflows
```
You should see a block like:
```
workflows:
    core_cli: '["c:/Users/Tiger/AppData/Roaming/npm/bun.cmd", "run", "c:/Users/Tiger/AppData/Local/hermes/plugins/hermes-workflows/packages/core/src/cli.ts"]'
```
If the `global_workflows_path` subkey is missing or incorrect, set it:
```bash
hermes config set plugins.workflows.global_workflows_path "C:\Users\Tiger\AppData\Local\hermes\workflows\global"
```
Create the folder if it does not exist:
```bash
mkdir -p "C:\Users\Tiger\AppData\Local\hermes\workflows\global"
```

### 3. Ensure at Least One Workflow File Exists
Copy a known-good workflow (e.g., the test workflow or the example) into the global folder:
```bash
cp "/c/Users/Tiger/AppData/Local/hermes/workflows/test.workflow.yaml" "/c/Users/Tiger/AppData/Local/hermes/workflows/global/"
```
You can also use the `feature-development.workflow.yaml` example.

### 4. Rebuild the Dashboard Bundle
After any plugin change or configuration update, rebuild the dashboard assets:
```bash
cd "/c/Users/Tiger/AppData/Local/hermes/plugins/hermes-workflows"
bun run dashboard:rebuild
```
This runs `dashboard:bump` then `dashboard:build`. If you get errors about missing `vite`, run `bun install` inside the dashboard folder first:
```bash
cd apps/dashboard
bun install
cd ../..
bun run dashboard:rebuild
```

### 5. Restart the Gateway (Optional but Recommended)
```bash
hermes gateway restart
```

### 6. Verify the Dashboard Can See the Workflow
Test the internal CLI that the dashboard uses:
```bash
bun run packages/core/src/cli.ts list-specs --roots "C:\Users/Tiger/AppData/Local/hermes/workflows\global"
```
Expected output (JSON array with at least one workflow):
```json
[
  {
    "id": "test",
    "name": "Test Workflow",
    "scope": { "type": "global" },
    "trigger": "manual",
    "path": "C:\\Users\\Tiger\\AppData\\Local\\hermes\\workflows\\global\\test.workflow.yaml"
  }
]
```
If you see an empty array `[]` or an error, double-check the path and file name.

### 7. Load the Dashboard
Open (or hard‑refresh) the Hermes dashboard in your browser:
```
http://127.0.0.1:9119/
```
Navigate to **Workflows** in the left sidebar. You should now see a list of workflow(s) (e.g., "Test Workflow", "Feature Development").

If you still see "Failed to load workflows":
- Perform a hard refresh (`Ctrl + F5`) or open an incognito/private window.
- Check the Hermes logs for errors: `hermes logs | grep -i workflow`.
- Ensure no other process is bound to port 9119 (or change the dashboard port via `hermes config set dashboard.api_port 9120` and restart).

## Troubleshooting Notes
- **Port Conflicts**: If the dashboard fails to start because the port is in use, kill the existing process or change the port:
  ```bash
  hermes config set dashboard.api_port 9120
  hermes gateway restart
  ```
- **Dashboard Not Updating**: After rebuilding, always clear browser cache or hard‑refresh; the dashboard serves cached assets.
- **Workflow Validation**: You can validate a workflow file with:
  ```bash
  bun run packages/core/src/cli.ts validate /path/to/your.workflow.yaml
  ```
- **Logs**: Use `hermes logs` to see runtime errors from the workflows plugin.

## References
- Official Hermes Workflows documentation: https://hermes-agent.nousresearch.com/docs/user-guide/features/workflows
- Example workflows are located in `packages/hermes-workflows/examples/` after plugin installation.

## Notes
- This skill assumes a Windows environment; adjust paths accordingly for Linux/WSL (use `/mnt/c/...` style paths).
- The `global_workflows_path` can also point to a folder inside your project (`<project>/.hermes/workflows`) for project‑specific workflows.