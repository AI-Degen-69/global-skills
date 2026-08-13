---
name: redesign-workflow
description: Use when the user asks what should be improved visually, asks whether a plan/Kanban is needed, or wants a rede
---

# Redesign Workflow

Use this when the user wants design improvement direction for an existing product and especially when they ask some version of:
- "what should we improve?"
- "what's the best-practice approach?"
- "do we need a plan?"
- "should we use Kanban?"
- "/goal run a redesign workflow where finish is a prototype/example for me to see"

The purpose of this skill is to prevent a common failure mode: giving accurate design critique but leaving the user with no operational next step.

## Core rule

**Do not stop at critique.** A redesign conversation must progress through:
1. audit / diagnosis,
2. workflow recommendation,
3. one blocking design decision at a time,
4. written spec,
5. implementation plan,
6. visible prototype.

If the user wants momentum, do not keep handing them neutral option lists without a recommendation. Lead.

## What to say early

After the first audit or critique, explicitly answer these questions without waiting to be asked again:
1. **Do we need a plan?**
2. **Do we need Kanban?**
3. **What is the next step?**
4. **If this were my app, what would I do?**

Default guidance for a single-screen redesign prototype:
- **Yes, use a short plan.**
- **No, do not use Kanban** unless the work spans multiple screens, contributors, or a multi-week rollout.
- **Start with one flagship screen** that defines the visual system for the rest.

## Recommended workflow

### 1. Audit the live UI
Review the real screen, not just the source. Capture the visible issues in priority order.

### 2. Convert critique into direction
Do not end with "here are some ideas." Say which path you recommend and why.

Good pattern:
- state the strongest recommendation,
- state why it has the highest leverage,
- name the immediate next artifact to produce.

### 3. Pick the prototype target
Choose one screen only.

Default order:
1. main flagship screen,
2. densest high-value workflow screen,
3. supporting reference/library screens.

For calculator-style products, start with the main calculator screen because it sets the visual language and gives the fastest feedback.

### 4. Ask one blocking question at a time
Only ask questions that materially change the visual output. Preferred order:
1. Which screen is first?
2. What visual character should it lean into?
3. Any non-negotiable brand/content constraints?

Do not ask three aesthetic questions at once.

### 5. Propose 2-3 directions with one clear recommendation
Always include trade-offs, but do not be neutral.

For each direction include:
- visual character,
- palette idea,
- typography idea,
- layout approach,
- risk,
- why it may or may not fit.

Then explicitly recommend one.

### 6. Write the design spec
Create a durable design doc before implementation. It should include:
- goal,
- target screen,
- audience/job-to-be-done,
- design direction,
- color tokens,
- type system,
- layout hierarchy,
- component changes,
- motion/accessibility constraints,
- success criteria.

### 7. Write the implementation plan
Break the prototype into concrete file changes and verification steps.

### 8. Build the prototype
For redesign work, the finish line is a visible artifact the user can react to.

If the user signals urgency or says some version of:
- "go to the end"
- "I want to see a full redesigned page"
- "start, I want a finished example"

then do **not** stop at a spec, wireframe, or partial component pass. Drive to a complete, runnable flagship page in one flow.

When the user asks for safety or isolation (for example: "backup" or "work in another branch"), create a recovery handle before editing and build in an isolated branch/worktree rather than the main checkout.

### 9. Verify visually
Use screenshots after implementation. A redesign is not done when the code compiles; it is done when the screen visibly reflects the intended hierarchy and style.

Verification must include both:
- build/typecheck evidence, and
- live visual inspection of the actual redesigned page.

If the visual pass shows a layout regression, keep iterating before presenting the redesign as finished.

## Kanban decision rule

Use Kanban only when at least one is true:
- 3+ screens or workstreams are being redesigned in parallel,
- multiple people/agents are contributing,
- there is a backlog of follow-on polish items that must be tracked over days,
- the prototype is being converted into a full rollout.

Do **not** introduce Kanban for a one-screen prototype. It adds process overhead without improving design quality.

## User-facing response pattern

In redesign sessions, every substantial answer should contain:
1. the recommendation,
2. the reason,
3. the immediate next step.

Bad:
- long critique,
- several options,
- no recommendation,
- no stated next action.

Good:
- "Use a short plan, skip Kanban, redesign the main calculator first, then prototype it. Next I need the visual character locked so I can draft directions."

## Pitfalls

### Pitfall: critique without workflow
If the user responds with frustration like "what do we do next?" or "your answers leave me with questions," you failed to convert analysis into execution. Recover immediately by naming the workflow and pushing it forward.

### Pitfall: asking for management structure too early
Do not introduce Kanban, epics, lanes, or backlog structure before a single design direction exists.

### Pitfall: redesigning the whole app at once
A broad redesign without a flagship prototype produces weak, generic output and slow feedback.

### Pitfall: stopping after the plan
The prototype is part of the workflow, not an optional later phase, when the user asked to see an example.

## Handoff standard

When transitioning from direction-setting to building, explicitly state:
- target screen,
- chosen visual character,
- next artifact being produced,
- that implementation follows after the spec/plan gate.

## Success criteria

This skill was applied well if:
- the user is never left asking what happens next,
- there is always one active recommended path,
- the redesign narrows quickly to one flagship screen,
- the conversation produces a prototype instead of lingering in critique mode.
