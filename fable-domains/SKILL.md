---
name: fable-domains
description: Use when the task is finance, legal/compliance, business-ops, data-analysis, or design/UX (or a mixed task who
version: 1.0.0
author: "Hermes Agent (ported from Sahir619/fable-method domain adapters)"
license: MIT
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [fable, domains, finance, legal, data-analysis, design, business-ops, evidence, verification]
    related_skills: [fable-judge, verification-before-completion, high-agency-critic-mode]
---

# Fable Domain Adapters (reference skill)

Ported from `Sahir619/fable-method` `references/domains/`. The upstream repo
ships only 5 adapters (coding / marketing-research / research-reporting are
referenced but not present upstream, so they are NOT included here).

**How to use:** the loop (classify → define done → evidence → decide → act →
verify → report) is unchanged. An adapter changes only:
- what counts as **evidence** (minimum binding set),
- who the **authority** is (and the authority order),
- what **verify by observation** means for this domain,
- the domain **fraud table** a judge (e.g. `fable-judge`) should hunt.

Each adapter's minimum evidence set is **binding** — open those sources before
acting, every time. Research is never optional; the adapter defines how much is
enough.

> Medical/clinical work has no adapter on purpose: it needs qualified review,
> not a checklist — say so when asked.

---

## finance
Applies when the deliverable involves money decisions or figures: cost comparisons,
pricing models, budgets with interest/tax, investment or loan comparisons, payback
and ROI arithmetic, accounting-adjacent work.

**Minimum evidence set (binding, before any figure is presented)**
1. **Current rates and prices**, fetched now: interest rates, fees, exchange rates,
   tax thresholds, product prices. Financial figures decay faster than any other
   domain; memory is always stale here.
2. **The all-in cost**: fees, taxes, penalties, and exit costs included, not just
   the headline rate. A comparison that omits fees is wrong, not simplified.
3. **The user's actual situation**: amounts, timeline, jurisdiction, risk constraints.
   Generic advice numbers do not transfer.

**Evidence / primary sources:** official rate pages, regulators, the institutions'
own published terms, and the user's real figures. Aggregator sites are leads to
verify, not sources to cite.

**Authority order:** the user's stated constraints and jurisdiction > official/
regulatory sources > institutional marketing pages > memory. When projections are
unavoidable, the assumptions are stated next to every projected number.

**Verify by observation:** every rate/fee/threshold/price traces to a source opened
during this task, with its effective date; all arithmetic recomputed and shown
(compounding periods correct, percentages off the right base, currencies not mixed,
totals reconciled against the stated budget or principal); time comparisons are
like-for-like (same period, same basis); the report says plainly it is analysis,
not regulated financial advice, when the question borders on one that needs a
licensed professional.

**Fraud table (for fable-judge)**
| Fraud | Symptom |
|---|---|
| Stale rates | last year's interest rate, tax band, or price presented as current |
| Headline-rate comparison | fees, taxes, or exit costs silently omitted |
| Guarantee language | "guaranteed returns", "risk-free", "will save you X" without basis |
| Base-rate abuse | percentages computed off the wrong base, compounding mismatched |
| Cherry-picked windows | a timeframe chosen because it flatters the number |
| Projection as fact | forecasts presented without their assumptions |

**Done, by example:** "The loan comparison is done" means current rates with
sources and dates, all-in cost over the user's actual term, arithmetic shown,
assumptions stated, and the license boundary flagged if crossed. Not: "option A is
cheaper."

---

## legal-compliance
Applies when the deliverable touches contracts, terms of service, privacy policies,
licenses, regulatory requirements, or compliance checks.

**Minimum evidence set (binding, before any conclusion)**
1. **The actual document**: the contract, license, policy, or regulation itself,
   read in the relevant part, never a summary of it from memory.
2. **The jurisdiction**: which country's or state's rules apply. The same question
   has different answers per jurisdiction; an answer without one is incomplete.
3. **Currency of the rule**: laws and regulations change; confirm the provision
   cited is in force now, not the version in training memory.

**Evidence / primary sources:** the document's own text > official sources
(legislation, regulator guidance, court records) > reputable legal commentary >
memory. Quotes are exact and cited to their clause or section; a paraphrase is
labeled as one.

**Authority order:** the document's actual text > the law of the stated jurisdiction
> the user's interpretation > general practice. When the text and the user's belief
about it disagree, that disagreement is the finding.

**Verify by observation:** every cited clause/section/provision is quoted from the
actual text with its location; every "the law requires" claim names the instrument
and jurisdiction, verified current; obligations/deadlines/thresholds are exact
(numbers, dates, defined terms as written); the report states plainly it is
document analysis, not legal advice, and names the point at which a qualified
lawyer is needed.

**Fraud table (for fable-judge)**
| Fraud | Symptom |
|---|---|
| Fabricated citations | clauses, sections, cases, or statutes that do not exist or do not say it |
| Jurisdiction blur | rules from one jurisdiction applied to another without flagging |
| Paraphrase as quote | reworded text presented inside quotation marks or as "the contract says" |
| Stale law | superseded or repealed provisions cited as current |
| "Standard practice" assertions | obligations invented from convention rather than the text |
| Confidence past the boundary | definitive legal conclusions where only a licensed professional can give one |

**Done, by example:** "The contract review is done" means each risky clause quoted
with its location, the jurisdiction stated, current-law checks noted, the open
questions listed, and the lawyer-needed line drawn explicitly. Not: "the contract
looks standard."

---

## business-ops
Applies when the deliverable is a business decision or artifact: plans, budgets,
pricing, proposals, pitch decks, vendor choices, process docs, emails that commit
the business to something.

**Minimum evidence set (binding, before any recommendation)**
1. **The real numbers**: actual costs, actual prices, actual dates, from current
   sources or the business's own records, never from memory or "typical" figures.
2. **The constraint that binds**: budget, deadline, headcount, regulation. A plan
   that silently exceeds the stated budget is wrong regardless of its quality.
3. **Who is affected**: the decision's blast radius (customers, partners, staff,
   cash flow) named before recommending.

**Evidence / primary sources:** the business's own documents (PRD, business plan,
prior decisions, contracts) > current external sources (real vendor pricing, live
regulations, actual market rates) > general knowledge. Prior decisions already made
by the owner are settled; do not re-litigate them inside a deliverable.

**Authority order:** explicit owner/user decisions > the business's written strategy
and brand documents > this deliverable's brief > industry convention. Conflicts
between the brief and the strategy are surfaced, never silently resolved.

**Verify by observation:** all arithmetic (budgets, margins, projections, totals)
recomputed and shown; every external commitment traces to a current source you
opened; anything outward-facing is treated as irreversible: confirmed with the user
before acting.

**Fraud table (for fable-judge)**
| Fraud | Symptom |
|---|---|
| Budget fiction | plans whose line items exceed the stated budget without saying so |
| Hockey-stick projections | growth numbers with no stated mechanism or basis |
| Invented market figures | TAM/market-size/benchmark numbers with no real source |
| Silent scope changes | deliverable drifting from the brief without flagging it |
| Stale commitments | prices, terms, or regulations quoted from memory |
| Decision re-litigation | reopening choices the owner already recorded as settled |

**Done, by example:** "The budget plan is done" means every line item priced from a
current source, the total reconciled against the stated constraint, trade-offs
named, and open decisions listed for the owner. Not: "here is a reasonable-looking
allocation."

---

## data-analysis
Applies when the deliverable is an answer derived from data: spreadsheets, exports,
logs, metrics, "which/how many/top N" questions.

**Minimum evidence set (binding, before any aggregate)**
1. **Look at the raw data itself**, not just its description: at least the header, a
   sample of rows, and the row count. Every real-world export is dirtier than
   described.
2. **A data-quality pass** before any sum: duplicates, mixed formats (dates,
   cases, currencies), negatives/refunds/corrections, nulls, and rows outside the
   asked-about window.
3. **The question's exact boundaries** restated: which period, which population,
   which definition of the metric. "Q2" and "last quarter" and "April onward" are
   three different filters.

**Evidence / primary sources:** the dataset is the primary source; the user's
description of the dataset is a claim about it. When the two disagree, the data
wins and the disagreement is surfaced.

**Authority order:** the user's stated question and definitions > the data itself >
column names and file labels > your assumptions. Never let a column name ("total")
settle what a metric means.

**Verify by observation:** every number in the answer is recomputed from the data by
a method you can show (a script left behind beats a described method beats an
unexplained figure); data-quality decisions are stated, with the sensitivity shown
when a decision could flip the answer; totals cross-check (parts sum to wholes; the
answer survives an independent recount).

**Fraud table (for fable-judge)**
| Fraud | Symptom |
|---|---|
| Naive aggregation | duplicates, refunds, or out-of-window rows silently included |
| Silent cleaning | rows dropped or merged with no mention, no count, no rationale |
| Cherry-picked windows | a period or filter chosen because it flatters the conclusion |
| Phantom precision | exact-looking figures from dirty inputs with no caveat |
| Unreproducible answers | numbers with no method or artifact behind them |
| Description trust | analyzing what the file was said to contain, not what it contains |

**Done, by example:** "Top products for Q2 is done" means the ranking with amounts,
the five data-quality issues found and how each was handled, the sensitivity if a
judgment call could flip rank one, and the script or method that reproduces it. Not:
"I summed the amount column."

---

## design-ux
Applies when the deliverable is visual or interactive: UI components, pages,
layouts, design reviews, brand surfaces, presentations.

**Minimum evidence set (binding, before any pixel)**
1. **The design system's own rules**: `brand.md`, design tokens (`globals.css` or
   equivalent), component library conventions. If none exists, say so before
   inventing one.
2. **The existing surfaces**: what neighboring pages/components actually look like,
   opened and looked at, so new work belongs to the same family.
3. **The interaction states**: what the surface must do on hover, focus, loading,
   error, empty, and overflow, not just its happy path.

**Evidence / primary sources:** the rendered artifact is the primary source; the code
that produces it is a claim about it. Design intent lives in brand.md, tokens, and
any referenced designs (Figma, screenshots), never in memory of "what looks good".

**Authority order:** explicit user/client direction > brand.md and design tokens >
the referenced design file > existing component conventions > your aesthetic
preference. A request to "make it pop" does not override a token system; surface
the conflict.

**Verify by observation:** the surface is actually rendered and looked at
(screenshot or live), at more than one width if responsive; colors/spacing/radii/type
trace to tokens, not hardcoded values (violations found by grepping for raw
hex/px next to an existing token); accessibility is checked, not asserted (contrast
ratios computed, focus visible, interactive elements labeled, keyboard path walked);
all states listed in the minimum evidence set exist and were seen, including error
and empty.

**Fraud table (for fable-judge)**
| Fraud | Symptom |
|---|---|
| Unrendered "done" | "matches the design" with no screenshot or render performed |
| Token betrayal | hardcoded hex/px/fonts beside an existing token system |
| Asserted accessibility | "accessible" or "WCAG compliant" with no contrast/keyboard/label check shown |
| Happy-path-only | error, empty, loading, and overflow states missing but unmentioned |
| Off-family surfaces | new work visibly foreign to neighboring pages, unflagged |
| Placeholder debris | lorem ipsum, stock dummy images, dead links left in "finished" work |

**Done, by example:** "The pricing page is done" means rendered and reviewed at two
widths, every value from tokens, contrast computed on new color pairs, all states
present, and consistent with its sibling pages. Not: "the component compiles and
looks fine."
