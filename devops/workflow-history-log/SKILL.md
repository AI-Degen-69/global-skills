---
name: workflow-history-log
description: Use when appending each cron run to the workflow history store.
---

# Workflow History Logger (cron wiring)

Every time this cron run finishes — success OR failure — you MUST append one
history entry to the shared store. This is a hard requirement, not optional.

Run this command via the terminal (the `terminal` tool is available in this cron):

```bash
python "C:/Users/Tiger/AppData/Local/hermes/scripts/workflow_history.py" log_run \
  --workflow "<this cron's job name, e.g. daily-ibkr-report>" \
  --did "<one line: what this run actually did>" \
  --fixed "<one line: what it fixed this run, or empty>" \
  --recurring "<one line: any problem that keeps coming back, or empty>" \
  --improve "<one line: where this workflow could be improved, or empty>" \
  --status ok
```

Rules:
- Use `--status error` if the run failed or partially failed. Put the failure
  cause in `--recurring` and a concrete fix idea in `--improve`.
- Keep each field a single concise line (no newlines). The weekly scanner
  clusters on shared content words, so REUSE the exact same wording for the
  same recurring issue across runs (e.g. always write "flaky git push on VPN
  drop", never a fresh paraphrase each time — otherwise it won't cluster).
- Never let logging failure break your delivery. The logger is fail-safe (it
  never raises), but if the command itself errors, ignore it and still deliver
  your normal report.
- This runs IN ADDITION to, not instead of, your normal cron output.

Do this as the LAST action before you finish.
