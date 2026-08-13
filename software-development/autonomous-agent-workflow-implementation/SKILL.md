---
name: autonomous-agent-workflow-implementation
description: Use when delegating rough ideas to an orchestrator that spawns specialist agents.
---

# Autonomous Agent Workflow Implementation

Use this when building or upgrading a persistent orchestrator that routes work to specialist agents across explicit workflow stages.

## When to use
- The user wants an orchestrator to accept rough ideas and delegate work to specialist agents.
- A current implementation is too shallow (single fanout, flat queue, demo-only flow) and needs a real staged workflow.
- Documentation still describes an old mental model after the system concept changed.
- Tests pass for the old workflow but no longer prove the deeper stage machine.

## Core principle
Do not stop at planning. Convert the rough concept into an implemented staged controller with:
1. explicit workflow states
2. dependency-gated transitions
3. durable project/work-item artifacts
4. end-to-end simulation that matches the actual workflow depth
5. documentation aligned to the verified behavior

## Default execution sequence
1. **Audit the live workspace first**
   - Read the orchestrator, base agent class, specialist agents, simulation/test harness, and README.
   - Check for durable planning files already present in the workspace and extend them instead of creating parallel drift.
   - If `AGENTS.md` exists, read it before touching code.

2. **Write/refresh a durable plan**
   - Put the plan in `.hermes/plans/` or the workspace’s existing planning file pattern.
   - Mirror stable execution items into the session todo list.

3. **Model the workflow as named stages**
   - Prefer a stage machine over vague “process idea, assign tasks” logic.
   - Recommended shape for software-delivery systems:
     - intake
     - specification / scope refinement
     - architecture
     - verification planning
     - implementation fanout
     - integration gate
     - documentation handoff
     - release readiness
     - completed / blocked

4. **Gate downstream work on upstream artifacts**
   - Implementation should depend on architecture and verification planning, not just idea intake.
   - Documentation and release should not open before an integration gate completes.
   - Store dependency IDs on work items; do not rely on implicit ordering.

5. **Persist durable artifacts on the project record**
   - Keep stage history, completed work item IDs, blocked reasons, and a per-stage artifact index.
   - The orchestrator should leave a reviewable trail, not just move files around.

6. **Align specialist agents to stage intent**
   - Intake agent should produce a brief/open-questions artifact.
   - Architecture agent should distinguish spec refinement from system design.
   - QA agent should distinguish planning gates from integration/release validation.
   - Documentation agent should distinguish intake capture from release/developer handoff.

7. **Upgrade the simulation/test harness with the workflow**
   - Increase timeouts if the workflow is now deeper.
   - Assert the real stage history, not just terminal completion.
   - Verify artifact persistence (`completed_results`, project stage artifacts, durable work items).
   - A previously correct shallow test often becomes a false failure after the controller improves.

8. **Update README last, from verified behavior**
   - Rewrite old conceptual framing if the system domain changed.
   - Document the actual stages and file artifacts that the code now uses.
   - Do not leave stale terminology from the previous system metaphor.

## Pitfalls
- **Planning-only drift**: user asked for workflow + implementation; do not stop at architecture notes or a plan file.
- **Demo-flow trap**: a flat queue with one task per agent type is not a comprehensive orchestrator.
- **Spec-less implementation fanout**: do not open build work directly from a rough idea.
- **Shallow-test false negative**: when you deepen the workflow, the old timeout/assertion shape will fail even if the controller is correct.
- **Documentation lag**: README often preserves the old system metaphor after the implementation direction changes; patch it in the same pass.
- **Artifact blindness**: if the project record does not index stage outputs, later review/debugging becomes guesswork.

## Verification standard
A successful pass requires positive evidence:
- end-to-end simulation exits successfully
- sample projects reach `completed` or intentional `blocked`
- stage history includes every expected workflow stage
- all created work items land in a terminal state
- archived results exist
- README matches the implemented workflow

## Closeout
Report:
- what stages were added or changed
- which files define the orchestrator, agents, test harness, and docs
- exact verification command and outcome
- any pitfall fixed during the pass (especially outdated tests/docs)

## Reference material
See `references/software-factory-workflow-upgrade.md` for a concrete verified example of converting a shallower agent factory into a staged software-delivery orchestrator.
