---
name: coding-model-evaluation
description: Use when comparing models for coding agent selection, validating provider claims, or building model routing lo
category: software-development
tags: [benchmarking, evaluation, coding-agents, model-selection, empirical-testing]
---

# Coding Model Evaluation Skill

## Purpose
Systematic, evidence-based evaluation of LLM coding capabilities. Moves beyond marketing benchmarks (HumanEval, MMLU) to **agentic coding tasks** that reflect real workflow: multi-file edits, test generation, debugging loops, dependency awareness.

## Core Methodology: 3-Tier Task Design

| Tier | Task Profile | What It Tests |
|------|--------------|---------------|
| **Simple** | Single function, clear spec, type hints + docstring | Basic syntax, instruction following, boilerplate |
| **Medium** | Class/module with state, concurrency, edge cases | Architecture, thread-safety, error handling, testing |
| **Hard** | Production-ready component: dynamic config, metrics, comprehensive tests, async primitives | Agentic completeness: test-driven, self-verifying, maintainable |

### Task Templates (Reusable)

**Simple**: "Write a Python function that takes a list of integers and returns the sum of all even numbers. Include type hints and a docstring."

**Medium**: "Implement a thread-safe LRU cache in Python with get/put operations, max size, and TTL expiration. Include tests."

**Hard**: "Design a Python async rate limiter using token bucket algorithm that works across multiple asyncio tasks. Support dynamic rate changes, burst allowance, and provide metrics (requests allowed, rejected, current tokens). Write clean, production-ready code with comprehensive tests."

## Execution Protocol

1. **Parallel execution** — Use `ThreadPoolExecutor` (max 3-5 workers) to query all models concurrently
2. **Identical prompts** — Same prompt, same parameters (temp=0.1, max_tokens=4096) for every model
3. **Timeout handling** — 120-180s per request; treat timeout as failure
4. **Response validation** — Parse JSON, extract `message.content`, verify non-empty
5. **Failure categorization** — Track: success, subscription_error, server_error, timeout, empty_response

## Verification Standards

**Positive verification only** — "No errors" ≠ success. Require:
- Executable code (syntax check via `python -m py_compile`)
- Tests pass (if model included tests)
- Key patterns present (type hints, docstrings, async/await for async tasks)

## Ranking Framework

| Rank Signal | Weight | Notes |
|-------------|--------|-------|
| Tasks completed (3/3) | 40% | Hard requirement for Tier 1 |
| Code quality indicators | 30% | `__slots__`, frozen dataclasses, `time.monotonic()`, comprehensive tests |
| Output completeness | 20% | Non-trivial length, no truncation |
| Architecture soundness | 10% | Separation of concerns, extensibility |

## Pitfalls to Avoid

- ❌ Trusting provider benchmarks (HumanEval, MMLU) — they don't measure agentic behavior
- ❌ Single-turn evaluation — real coding is iterative
- ❌ Ignoring subscription/access errors — filter them from capability assessment
- ❌ Comparing different prompt styles — must be identical
- ❌ Treating "knows syntax" as "can code agentically" — different capabilities

## When to Re-Benchmark

- New model added to provider
- Provider API changes (quantization, context window, temperature defaults)
- New coding task category needed (e.g., Rust, Kubernetes, frontend)
- Quarterly for drift detection

## Reference Files

- `references/ollama-benchmark-2026-06-29.md` — Session results: 35 models tested, 20 responsive, updated with Tier 2 model evaluations (nemotron-3-nano:30b passed all tiers, devstral-2:123b and qwen3-coder-next passed simple/medium but failed hard, glm-4.7 and gemma3:27b timed out on medium/hard)
- `references/task-templates.md` — Copy-paste ready prompts for each tier
- `scripts/benchmark-runner.py` — Reusable execution script (TODO: create)

## Key Insights from Benchmarking

- **nemotron-3-nano:30b** demonstrated exceptional efficiency, passing all three tiers despite its smaller size
- **Async token bucket task** (Hard tier) proved most discriminating, revealing differences in async Python proficiency
- **Specialized coding models** (devstral-2:123b, qwen3-coder-next) showed strength in structured tasks but had gaps in advanced async patterns
- **Generalist models** (glm-4.7, gemma3:27b) demonstrated conceptual understanding but sometimes timed out on complex implementations
- **Subscription models** showed high failure rates (14/15 non-responsive) and should be filtered from capability assessments