# Output Rules

Cross-cutting output quality standards for all brain-writing skills.

## Deterministic Links

All links in brain pages MUST be deterministic (built from actual data, not composed
by the LLM). Never guess a URL or path. Build it from the slug, the commit hash, or
the API response.

- Brain page links: `[page title](type/slug.md)`
- Commit links: `[abc1234](https://github.com/{owner}/{repo}/commit/abc1234)`
- External links: use the actual URL from the source, never reconstruct it

## No Slop

Brain pages are not chat output. They are durable knowledge artifacts.

- No filler phrases ("It's worth noting that...", "Interestingly...")
- No hedging when facts are cited ("According to the source, X is true" not "X might be true")
- No LLM preamble ("I've created...", "Here's the updated...", "Certainly!")
- No placeholder dates ("YYYY-MM-DD", "recently", "in the near future")
- Short paragraphs. Concrete facts. Inline citations.

## Exact Phrasing Preservation

When capturing someone's original thinking, use their exact words. Don't paraphrase.
Don't clean up grammar. The language IS the insight.

- Direct quotes: preserve verbatim in quote blocks
- Ideas and frameworks: use the person's own terminology for slugs and titles
- Observations: capture the phrasing, not a sanitized version

## Title Quality

Page titles should be:
- Descriptive enough to identify the page from a search result
- Short enough to scan in a list (under 60 characters)
- NOT sentences ("Meeting with Pedro" not "Meeting with Pedro about the new deal structure")
- NOT generic ("Pedro Franceschi" not "Person Page")

## Global Response Formatting
- **No Time Estimates**: Never include minute counts or time duration estimates in responses.
- **Suggested Follow-ups Ending**: Always end responses with a `### Suggested Follow-ups` section containing exactly 3 options framed as actions the AI assistant will execute using "I'll..." phrasing (without "Option 1:", "Option 2:", etc.):
  1. **(Recommended) I'll [action verb]**: Primary recommended next action I will execute with a short plain English description.
  2. **I'll [action verb]**: Alternative direction I will execute with a short plain English description.
  3. **I'll [action verb]**: Another variation I will execute with a short plain English description.
- **Numbered Selection Execution**: When the user replies with a number (e.g. "1", "2", "3", "I choose 1"), immediately execute that numbered follow-up action.




