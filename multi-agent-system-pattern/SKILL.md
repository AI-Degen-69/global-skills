---
name: multi-agent-system-pattern
description: Use when building a coordinated multi-agent system with orchestrator and workers.
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [architecture, multi-agent, orchestration, delegation, pattern]
    related_skills: [subagent-driven-development, writing-plans, requesting-code-review]
---

# Multi-Agent System Pattern

## Overview
A reusable pattern for building coordinated agent systems in Hermes featuring:
- Central orchestrator for task distribution and agent management
- Specialized worker agents that perform specific domain tasks
- Filesystem-based communication for loose coupling
- Standardized agent lifecycle (registration, heartbeat, task execution)
- Fault tolerance through heartbeat monitoring

## When to Use
Use this pattern when:
- Building systems requiring multiple coordinated agents with distinct responsibilities
- Need for dynamic task allocation based on agent availability and capabilities
- Wanting fault tolerance through automatic detection of agent failures
- Preferring asynchronous, decoupled communication between components
- Implementing long-running systems where agents may join/leave dynamically

**Not ideal for:**
- Simple sequential workflows (consider subagent-driven-development instead)
- Tightly coupled agents requiring frequent synchronous communication
- Systems needing real-time low-latency interactions between agents

## Core Components

### 1. Orchestrator
Central coordinator responsible for:
- Agent registration and deregistration
- Heartbeat monitoring for failure detection
- Task queuing and prioritization
- Matching tasks to available agents based on type/capability
- Collecting and storing results
- Basic fault tolerance (task requeuing on agent failure)

### 2. Agent Base Class
Abstract base class providing:
- Self-registration with orchestrator
- Periodic heartbeat mechanism
- Task polling loop from assigned directories
- Result reporting upon task completion
- Abstract `execute_task` method for domain-specific logic

### 3. Specialized Agents
Concrete implementations of AgentBase for specific work types:
- Each handles a distinct domain (e.g., assembly, quality control, logistics)
- Implements `execute_task` with domain logic
- Reports success/failure with structured results
- May handle multiple related task subtypes

### 4. Communication Mechanism
Filesystem-based loose coupling:
- **Registration**: Agents write `registrations/<agent_id>.json` on startup
- **Heartbeat**: Agents write `heartbeats/<agent_id>.json` every HEARTBEAT_INTERVAL seconds
- **Task Assignment**: Orchestrator writes `tasks/<agent_type>/<agent_id>/<task_id>.json`
- **Result Reporting**: Agents write `results/<task_id>.json` on completion

## Implementation Steps

### 1. Define Agent Types and Responsibilities
- Identify distinct work domains needing specialized agents
- For each domain, define:
  - Agent type identifier (string)
  - Capabilities list (specific skills/functions)
  - Task subtypes it handles
  - Expected input/output formats

### 2. Create Agent Base (`agent_base.py`)
Implement:
- Registration: Write agent metadata to registrations/
- Heartbeat: Periodically write liveness signal to heartbeats/
- Task Polling: Monitor `tasks/<agent_type>/<agent_id>/` for new tasks
- Execution: Call abstract `execute_task`, handle results/errors
- Result Reporting: Write outcome to results/ and clean task file
- Start/Stop: Manage agent lifecycle with clean shutdown

### 3. Implement Orchestrator (`orchestrator.py`)
Build components:
- **AgentRegistry**: Track agents by ID with type, status, last heartbeat, current task
- **TaskQueue**: Priority queue of pending work (priority, task_id, type, payload)
- **Monitors** (background threads):
  - Registrar: Watch registrations/ for new agent signups
  - Heartbeat Monitor: Check heartbeats/ for liveness and timeouts
  - Task Dispatcher: Match queued tasks to available agents
  - Result Collector: Process results/ to update agent/task status
- **Public API**:
  - `add_task(task_type, payload, priority=0)` → task_id
  - `start()` / `stop()` for system control

### 4. Create Specialized Agents
For each agent type:
- Inherit from AgentBase
- Implement `execute_task(task_type, payload)`:
  - Validate task_type matches agent's domain
  - Perform domain-specific work
  - Return result dict on success
  - Raise exception on failure (agent will report as failed)
- Add agent-specific capabilities to constructor
- Include realistic simulations/timeouts for testing

### 5. Test the System
Verification approach:
1. Start orchestrator in background thread
2. Start agents (each in own thread or process)
3. Add representative tasks via orchestrator.add_task()
4. Monitor results directory for completions
5. Test fault tolerance:
   - Stop an agent mid-task → verify task handling
   - Send malformed task → verify error reporting
6. Validate system recovers and continues operation

### 6. Document and Extend
- Create architecture diagram showing component interactions
- Document agent interfaces (task formats, result schemas)
- Provide usage guide for adding new agent types
- Note extension points for persistence, monitoring, etc.

## Key Design Decisions

### Filesystem Communication Choice
- **Pros**: Simple, debuggable, no external dependencies, works across processes
- **Cons**: Slower than in-memory, potential filesystem bottlenecks
- **Appropriate for**: Systems where agent count is moderate (<100) and latency requirements are not extreme (<100ms acceptable)

### Agent Lifecycle
- Agents self-register and self-monitor via heartbeats
- Orchestrator passively monitors rather than pushing commands
- Decouples agent startup/shutdown from orchestrator state
- Enables agents to be started in any order

### Task Handling
- Orchestrator owns task queue and assignment logic
- Agents pull tasks when idle (prevents overload)
- Clear separation: orchestrator decides *what* to do, agents decide *how*
- Failed tasks can be extended to support retry queues or dead letter queues

## Relationship to Other Skills

### vs. subagent-driven-development
- **subagent-driven-development**: Executes a single plan by breaking into discrete tasks with review gates
- **multi-agent-system-pattern**: Builds long-running systems with ongoing task distribution
- **Combination**: Use subagent-driven-development to create the initial agent implementations, then deploy them in a multi-agent system

### Agent Base and Subagents
- The AgentBase class enables true decoupled agents (can run in separate processes)
- Contrast with subagent-driven-development where subagents are temporary and controller-managed
- Both patterns can coexist in a larger system

### Pitfalls to Avoid

### ❌ Tight Coupling
- **Wrong**: Orchestrator directly calling agent methods
- **Right**: Pure filesystem communication; orchestrator never imports agent code

### ❌ Blocking Agent Loops
- **Wrong**: Agents blocking indefinitely on task polling
- **Right**: Non-blocking polling with sleeps; heartbeats in separate thread

### ❌ Inadequate Error Handling
- **Wrong**: Agents crashing on unexpected input
- **Right**: All exceptions caught and reported as failed tasks with error details

### ❌ Poor Cleanup
- **Wrong**: Leaving processed task/result files accumulating
- **Right**: Agents delete task files after processing; orchestrator cleans old result files (optional)

### ❌ Missing Timeout Handling
- **Wrong**: Orchestrator never detecting failed agents
- **Right**: Heartbeat timeout detection with task requeuing logic

### ❌ Overlooking Registration Order
- **Wrong**: Assuming agents register before tasks arrive
- **Right**: System works regardless of startup order (registrations monitored continuously)

### ❌ Import Path Issues When Running Agents Directly
- **Wrong**: Agents failing to import from parent directory when run as scripts
- **Right**: Agents should adjust sys.path when run directly: `sys.path.append(str(Path(__file__).resolve().parent.parent))` before importing from sibling directories

### ❌ Overly Aggressive Failure Simulation in Testing
- **Wrong**: Making failure rates too high during development/testing, making it hard to observe success cases
- **Right**: Start with low/no failure rates to verify basic functionality, then gradually introduce failures to test resilience

### ❌ Ignoring Agent Startup Timing in Tests
- **Wrong**: Adding tasks before agents have registered and started heartbeating
- **Right**: Always allow time for agent registration and heartbeat establishment before adding tasks to the system

## Extending the Pattern

### Adding Persistence
- Store task queue and agent state to disk/database
- Enable recovery after orchestrator restart
- Consider SQLite or simple JSON files for simplicity

### Enhancing Communication
- Replace filesystem with message queue (RabbitMQ, Redis) for scale
- Add acknowledgments and retries for message delivery
- Implement priority-based task queuing beyond simple FIFO

### Improving Fault Tolerance
- Store full task details for reliable requeuing
- Implement agent health checks beyond heartbeats
- Add graceful shutdown protocols for agents

### Monitoring and Observability
- Export metrics (task throughput, agent utilization, error rates)
- Add structured logging with correlation IDs
- Implement health check endpoints for orchestrator

## Example Usage
See the `dark_factory` implementation in `Vault/Agent Skills/dark_factory/` for a complete working example including:
- Orchestrator with registration/heartbeat/task/result handling
- Agent base class with standard lifecycle
- Four specialized agents (assembly, QC, logistics, maintenance)
- Test script demonstrating end-to-end operation

## Remember
```
Loose coupling through filesystem
Standardized agent lifecycle
Heartbeat-based failure detection
Clear separation of orchestration vs. execution
Design for extension and fault tolerance from the start
```