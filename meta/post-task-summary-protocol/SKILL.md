---
name: post-task-summary-protocol
description: Use when closing a task with a structured delta-log summary.
argument-hint: "Use after every completed task, session, or milestone."
---

# Post-Task Summary Protocol

**Mandatory — applies to ALL development sessions and projects.**

## 1. Executive Walkthrough
- Plain, non-technical description of what changed and why.
- Max **5 lines**.
- No technical minutiae.

## 2. Delta Log
- Report every completed task with an **ordered delta log** using bracketed action tags.
- Use the tag set that matches the actual work. Common options include, but are not limited to: `[ADDED]`, `[CHANGED]`, `[REMOVED]`, `[CREATED]`, `[UPDATED]`, `[DELETED]`, `[REFACTORED]`, `[MIGRATED]`, `[FIXED]`, `[OPTIMIZED]`.
- Add or substitute tags freely when the action verb fits better than the common examples.
- Each entry uses one bracketed tag and includes:
  1. One-sentence plain-language description of the change.
  2. Expected result.
  3. Manual verification step.
- Keep strict tag ordering that reflects execution sequence; do not force unrelated changes into a fixed tag list.
- Use only entries that apply; omit tags with no changes.

## 3. Report Path
- Always state which path was used: inline handling or delegation.

## 4. Next Steps
- Add follow-ups only when there is a real blocker, risk, decision, or high-leverage continuation path.
- Do **not** force a `1/2/3` menu after a completed deliverable just because more work is possible.
- When options are truly needed, keep them short, concrete, and immediately executable.
- If model switching is relevant, name the model/profile explicitly.

## 5. External Blockers and Permission Walls
- When work is blocked by branch protection, missing repo rights, API permissions, policy gates, or similar external controls, include the **exact command attempted** and the **exact server/tool refusal text** in verification evidence.
- Do not summarize permission failures generically when the underlying CLI/API returned a concrete message; quote the real blocker so the user can distinguish policy failure from merge conflict or tool misuse.
- If you attempted multiple unblock paths (for example direct merge and auto-merge), record each path separately with its own result.

## User-Specific Constraints
- Do not use vague planning language like "continue work" or "iterate".
- Per-step model recommendation only; omit if same model is clearly correct.
- Include a protocol status line when the governing project/persona contract asks for it; otherwise omit it.
- For SOUL/profile/persona maintenance, verify exact file readback and any symlink/path claims before closing.
- Prefer Linux tool paths first in WSL contexts; mention Windows full paths only as human-facing context when useful.
- Prefer dense technical style, English only, AS-IS agreed closeout format.
- Browser-based verification is required when a web UI exists **and the task changed that UI or depends on it**. Open the URL, navigate to the changed page/section, capture a screenshot or DOM snapshot, and tell the user exactly what to look for (specific headings, badges, data values, UI state). If no browser is possible, provide explicit manual verification steps with exact commands/URLs and expected outputs. The era of "trust me it works" is over — visual or command-line evidence is required.

**Feedback trigger:** If user replies "Protocol 4", immediately re-check this skill and regenerate the closeout in this exact format.