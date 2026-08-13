---
name: autoresearch-loop
description: Use when running autoresearch autonomous LLM training experiments.
version: 0.1.0
author: Hermes
platforms: [windows]
metadata:
  hermes:
    tags: [Autoresearch, LLM-Training, Autonomous-Agent, Windows]
---

# Autoresearch Loop

Autoresearch (the Windows/RTX fork of karpathy/autoresearch) turns a single consumer NVIDIA GPU into an autonomous LLM-pretraining researcher: an agent edits `train.py`, trains for a fixed 5-minute budget, reads the `val_bpb` metric, and keeps or discards the change. This skill captures how to set the repo up and run the experiment loop through Hermes. It does NOT cover distributed training, the upstream Linux/H100 path, or modifying `prepare.py` (read-only). Dependency stance: the repo is self-contained — `uv` plus the pinned `pyproject.toml` are all that is needed; no new packages are allowed inside the loop.

## When to Use
- "How do I run autoresearch on my RTX GPU / on this repo?"
- "Kick off a new autoresearch experiment" / "let the agent train overnight"
- Setting up the `autoresearch/<tag>` branch and `results.tsv` for a fresh run
- Pointing an agent at `program.md` to start autonomous research
- "Run the autoresearch training loop and log val_bpb"

## Prerequisites
- Windows + a single **desktop** NVIDIA GPU meeting the VRAM floor:
  - Turing: `>=8 GB` (e.g. RTX 2080 Ti)
  - Ampere / Ada / Blackwell: `>=10 GB` (e.g. RTX 3080 / 4090 / 5090)
  - Laptop GPUs are NOT supported. `RTX 2060 6GB` is out of matrix.
- [uv](https://docs.astral.sh/uv/) installed (`uv --version`).
- The repo cloned locally — this skill assumes `C:\Users\Tiger\Agents\Projects\autoresearch`; set `REPO` to wherever it lives.
- NVIDIA driver with CUDA 12.8 capability (PyTorch cu128 wheels, pinned `torch==2.9.1`).
- One-time data prep needs network access to download TinyStories (`karpathy/tinystories_gpt4_clean`).
- Optional autotune env: `AUTORESEARCH_DISABLE_AUTOTUNE=1` skips probing; `AUTORESEARCH_AUTOTUNE_REFRESH=1` refreshes the cached batch-size decision.

## How to Run
Invoke every shell command through the `terminal` tool from inside the repo directory. Canonical setup plus a single experiment:

```bash
cd "C:/Users/Tiger/Agents/Projects/autoresearch"
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"   # if uv missing
uv sync
uv run prepare.py                 # one-time: data shards + BPE tokenizer -> ~/.cache/autoresearch/
uv run train.py --smoke-test     # quick validation (~seconds)
uv run train.py > run.log 2>&1   # one 5-minute experiment, output to log only
```

The autonomous loop itself is defined in `program.md`; point the agent at that file. To launch it, spin up the agent in this repo with permissions disabled and prompt it to follow `program.md` (e.g. "have a look at program.md and let's kick off a new experiment — do the setup first").

## Quick Reference
```
uv sync                           # install deps from pyproject.toml (torch==2.9.1 cu128)
uv run prepare.py                 # one-time data + tokenizer prep
uv run train.py                   # single ~5-min experiment
uv run train.py --smoke-test     # fast validation run
uv run train.py > run.log 2>&1   # redirect ALL output to run.log (do NOT tee)
grep "^val_bpb:\|^peak_vram_mb:" run.log   # extract metrics (raw terminal form)
tail -n 50 run.log               # read crash trace (raw terminal form)
git checkout -b autoresearch/<tag>   # fresh run branch (date tag, e.g. mar5)
results.tsv                      # commit  val_bpb  memory_gb  status  description
AUTORESEARCH_DISABLE_AUTOTUNE=1            # skip autotune probe
AUTORESEARCH_AUTOTUNE_REFRESH=1            # refresh cached autotune decision
```
Files: `prepare.py` (read-only — eval/harness/constants), `train.py` (agent edits this), `program.md` (human edits this), `pyproject.toml` (pinned deps, `python>=3.10`).

## Procedure
1. **Pick a run tag.** Propose a date-based tag (e.g. `mar5`). Confirm the branch does not already exist: `git branch --list "autoresearch/<tag>"` (via `terminal`).
2. **Create the branch.** `cd "<REPO>" && git checkout -b autoresearch/<tag>` from current master.
3. **Read in-scope files** with `read_file` for full context: `README.md`, `prepare.py`, `train.py`. Do NOT modify `prepare.py`.
4. **Verify data.** Confirm `~/.cache/autoresearch/` holds data shards + tokenizer. If missing, tell the user to run `uv run prepare.py` (one-time network download).
5. **Init `results.tsv`** with the header row only (tab-separated, NOT comma):
   `commit\tval_bpb\tmemory_gb\tstatus\tdescription`. Baseline is recorded after the first run.
6. **Establish baseline.** First run is always the unmodified script: `uv run train.py > run.log 2>&1`.
7. **Read metrics** with `search_files` (`pattern="^val_bpb:\|^peak_vram_mb:"`, `path="run.log"`, `output_mode="content"`). If empty → crashed; read the trace with `read_file` (`path="run.log"`, `offset` near end, `limit=50`) and either fix a dumb bug or mark `crash`.
8. **Log the result.** Append one tab-separated row to `results.tsv` via `terminal`:
   `printf '%s\t%s\t%s\t%s\t%s\n' <7char-hash> <val_bpb> <mem_gb> <status> <desc> >> results.tsv`
   - `val_bpb`: the number from the log, or `0.000000` on crash.
   - `memory_gb`: `peak_vram_mb` / 1024 rounded to .1f (e.g. `44.0`), or `0.0` on crash.
   - `status`: `keep` / `discard` / `crash`.
   - `description`: short text of what the experiment tried.
9. **Advance or revert.** If `val_bpb` improved (lower) → keep the commit (advance the branch). If equal/worse → `git reset` back to start. VRAM is a soft constraint; all else equal, simpler code wins ties.
10. **Loop forever.** Repeat steps 6–9 autonomously. Never pause to ask the human. Kill any run exceeding ~10 min and treat it as failure/discard. Run until the human interrupts.

## Pitfalls
- **`--smoke-test` is the only fast path.** A normal `train.py` run is ~5 min by design — don't re-run it casually just to "check" something.
- **Output flooding.** Always redirect to `run.log` (`> run.log 2>&1`); never `tee` or let output into your context.
- **`prepare.py` is sacred.** Editing it breaks the eval harness / `evaluate_bpb` ground-truth metric. The only editable file is `train.py`.
- **No new deps.** Inside the loop you may only use packages already in `pyproject.toml`. Do not `pip install` / `uv add`.
- **VRAM floors.** RTX 2060 6GB unsupported; laptop GPUs unsupported; Turing needs >=8 GB, others >=10 GB. OOM crashes log as `crash`.
- **Not cross-platform comparable.** Results are tuned to your GPU's 5-min budget; don't compare to other hardware.
- **Upstream Linux/H100 path removed** in this fork — need it? Use `karpathy/autoresearch`.
- **Autotune caching:** a cached batch-size decision persists across GPU/runtime changes; set `AUTORESEARCH_AUTOTUNE_REFRESH=1` if you swap GPUs.

## Verification
A working setup is proven by a successful smoke test plus a real baseline:
```bash
uv run train.py --smoke-test && uv run train.py > run.log 2>&1
```
Then confirm the metric with `search_files` (`pattern="^val_bpb:"`, `path="run.log"`). Positive evidence: `val_bpb:` prints a finite number (e.g. `0.997900`) and `results.tsv` has a baseline `keep` row carrying that value.
