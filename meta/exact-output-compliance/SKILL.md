---
name: exact-output-compliance
description: Use when the user specifies an exact reply/output shape you must comply with.
---

# Exact Output Compliance

## When to use
Use this skill whenever the user specifies an exact reply shape, especially phrases like:
- `Reply with "..."`
- `Only output ...`
- connection / health / smoke tests
- active model/provider identity checks
- parser-sensitive responses where extra text would break the task

## Core rule
When the user asks for an exact output string, emit that string and nothing else unless they explicitly ask for explanation too.

## Procedure
1. Read the user's literal output requirement and treat it as the primary contract.
2. If system/runtime metadata changed during the conversation, use the **latest** active value that applies at the moment of reply.
3. Resolve placeholders like `<model-name>` from live runtime metadata, not from earlier turns or general memory.
4. Output the required string with:
   - no markdown
   - no bolding
   - no bullets
   - no status banner
   - no follow-up question
   - no extra commentary before or after
5. If the same message contains several superseded runtime changes followed by repeated tests, answer only the final active state unless the user explicitly asks for all intermediate states.

## Pitfalls
- Do **not** add helpful commentary after a successful probe. That breaks the contract.
- Do **not** answer an earlier model change when a later system message supersedes it in the same thread.
- Do **not** expand a simple connection check into product commentary.
- Do **not** decorate the literal answer with formatting such as bold, code fences, or emojis.
- When the user rejects the **answer shape itself** (for example: "stop this format", "too many bullets", "too much text wall", "remember this style"), treat that as a workflow correction, not a cosmetic note. Update the response shape immediately.

## Readability override for non-literal replies
When the user is **not** asking for an exact literal string, do not fall into either failure mode:
1. a long chain of bullets that feels mechanical and dead
2. a dense text wall with no visual anchors

Preferred response shape for this user/task class:
- short titled sections
- selective emoji as quick-skim anchors
- concise paragraphs with some voice/body
- minimal bullets only where they genuinely improve scanning
- avoid summary-framework sludge

See `references/readability-and-style-corrections.md` for the concrete trigger pattern behind this rule.

## Verification
Before sending, ask one question internally: `If the user pasted my reply into an exact-string matcher, would it pass?`
If not, strip everything except the required content.

## Notes
For terse probe-style sessions, optimize for exactness over friendliness. Correctness here is binary: exact match or failure.

## Support files
- `references/probe-cases.md` — compact examples of exact-output probe patterns and common failure modes.
