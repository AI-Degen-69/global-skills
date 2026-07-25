# ECC Skills Index

Imported from `affaan-m/ECC` into `skills/ecc/` — 24 skills.
Binary for `security-scan`: `agentshield` (not `ecc-agentshield`).
Windows note: AgentShield misreads NTFS ACLs as `0o666` (false HIGHs); scan a WSL/Linux path for truthful grades.

| Skill Dir | Name | Description |
|---|---|---|
| `agentic-engineering` | agentic-engineering | Operate as an agentic engineer using eval-first execution, decomposition, and cost-aware model routing. |
| `api-design` | api-design | REST API design patterns including resource naming, status codes, pagination, filtering, error responses, versioning, and rate limiting for production APIs. |
| `autonomous-loops` | autonomous-loops | Patterns and architectures for autonomous Claude Code loops — from simple sequential pipelines to RFC-driven multi-agent DAG systems. |
| `backend-patterns` | backend-patterns | Backend architecture patterns, API design, database optimization, and server-side best practices for Node.js, Express, and Next.js API routes. |
| `blueprint` | blueprint | Turn a one-line objective into a step-by-step construction plan for multi-session, multi-agent engineering projects. Each step has a self-contained context brief so a fresh agent can execute it cold. Includes adversarial review gate, dependency graph, parallel step detection, anti-pattern catalog, and plan mutation protocol. TRIGGER when: user requests a plan, blueprint, or roadmap for a complex multi-PR task, or describes work that needs multiple sessions. DO NOT TRIGGER when: task is completable in a single PR or fewer than 3 tool calls, or user says "just do it". |
| `clickhouse-io` | clickhouse-io | ClickHouse database patterns, query optimization, analytics, and data engineering best practices for high-performance analytical workloads. |
| `coding-standards` | coding-standards | Baseline cross-project coding conventions for naming, readability, immutability, and code-quality review. Use detailed frontend or backend skills for framework-specific patterns. |
| `configure-ecc` | configure-ecc | Interactive installer for Everything Claude Code — guides users through selecting and installing skills and rules to user-level or project-level directories, verifies paths, and optionally optimizes installed files. |
| `content-hash-cache-pattern` | content-hash-cache-pattern | Cache expensive file processing results using SHA-256 content hashes — path-independent, auto-invalidating, with service layer separation. |
| `continuous-agent-loop` | continuous-agent-loop | Patterns for continuous autonomous agent loops with quality gates, evals, and recovery controls. |
| `continuous-learning-v2` | continuous-learning-v2 | Instinct-based learning system that observes sessions via hooks, creates atomic instincts with confidence scoring, and evolves them into skills/commands/agents. v2.1 adds project-scoped instincts to prevent cross-project contamination. |
| `deep-research` | deep-research | Multi-source deep research using firecrawl and exa MCPs. Searches the web, synthesizes findings, and delivers cited reports with source attribution. Use when the user wants thorough research on any topic with evidence and citations. |
| `eval-harness` | eval-harness | Formal evaluation framework for Claude Code sessions implementing eval-driven development (EDD) principles |
| `exa-search` | exa-search | Neural search via Exa MCP for web, code, and company research. Use when the user needs web search, code examples, company intel, people lookup, or AI-powered deep research with Exa's neural search engine. |
| `frontend-patterns` | frontend-patterns | Frontend development patterns for React, Next.js, state management, performance optimization, and UI best practices. |
| `market-research` | market-research | Conduct market research, competitive analysis, investor due diligence, and industry intelligence with source attribution and decision-oriented summaries. Use when the user wants market sizing, competitor comparisons, fund research, technology scans, or research that informs business decisions. |
| `postgres-patterns` | postgres-patterns | PostgreSQL database patterns for query optimization, schema design, indexing, and security. Based on Supabase best practices. |
| `prompt-optimizer` | prompt-optimizer | Analyze raw prompts, identify intent and gaps, match ECC components (skills/commands/agents/hooks), and output a ready-to-paste optimized prompt. Advisory role only — never executes the task itself. TRIGGER when: user says "optimize prompt", "improve my prompt", "how to write a prompt for", "help me prompt", "rewrite this prompt", or explicitly asks to enhance prompt quality. Also triggers on Chinese equivalents: "优化prompt", "改进prompt", "怎么写prompt", "帮我优化这个指令". DO NOT TRIGGER when: user wants the task executed directly, or says "just do it" / "直接做". DO NOT TRIGGER when user says "优化代码", "优化性能", "optimize performance", "optimize this code" — those are refactoring/performance tasks, not prompt optimization. |
| `python-patterns` | python-patterns | Pythonic idioms, PEP 8 standards, type hints, and best practices for building robust, efficient, and maintainable Python applications. |
| `python-testing` | python-testing | Python testing strategies using pytest, TDD methodology, fixtures, mocking, parametrization, and coverage requirements. |
| `search-first` | search-first | Research-before-coding workflow. Search for existing tools, libraries, and patterns before writing custom code. Invokes the researcher agent. |
| `security-scan` | security-scan | Scan your Claude Code configuration (.claude/ directory) for security vulnerabilities, misconfigurations, and injection risks using AgentShield. Checks CLAUDE.md, settings.json, MCP servers, hooks, and agent definitions. |
| `strategic-compact` | strategic-compact | Suggests manual context compaction at logical intervals to preserve context through task phases rather than arbitrary auto-compaction. |
| `swiftui-patterns` | swiftui-patterns | SwiftUI architecture patterns, state management with @Observable, view composition, navigation, performance optimization, and modern iOS/macOS UI best practices. |
