---
name: product-strategy-frameworks
description: Use when applying a business/product strategy framework (JTBD, Blue Ocean, etc.).
version: 1.0.0
category: software-development
---

# Product Strategy Frameworks

Port of [Wondel.ai Skills](https://skills.wondel.ai/) — 21 business frameworks from bestselling books, packaged as agent skills for Claude Code, Cursor, Windsurf, and Hermes.

## Installation

```bash
# Clone source (MIT licensed)
git clone https://github.com/bilalmirza2001/skills ~/Developer/wondel-skills

# Install desired skills to Hermes
# Each skill is a directory with SKILL.md + reference files
cp -r ~/Developer/wondel-skills/jobs-to-be-done ~/.hermes/skills/product-strategy/
cp -r ~/Developer/wondel-skills/blue-ocean-strategy ~/.hermes/skills/product-strategy/
# ... repeat for each framework
```

Or use `skill-installer` to register them as a skill pack.

---

## Available Frameworks (21 Total)

### HIGH PRIORITY — Core Product/Strategy

| Skill | Source | Use When |
|-------|--------|----------|
| **jobs-to-be-done** | Christensen — *JTBD* | Uncovering real customer needs, positioning against "hires" |
| **blue-ocean-strategy** | Kim & Mauborgne — *Blue Ocean Strategy* | Strategy Canvas, Four Actions Framework, finding uncontested space |
| **crossing-the-chasm** | Moore — *Crossing the Chasm* | B2B SaaS GTM, beachhead segment, whole product model |
| **lean-startup** | Ries — *The Lean Startup* | Build-Measure-Learn cards, 5-day sprint plans, experiment design |
| **storybrand-messaging** | Miller — *Building a StoryBrand* | 7-part brand script: hero, problem, guide, plan, CTA, success/failure |
| **predictable-revenue** | Ross/Aaron — *Predictable Revenue* | Cold Calling 2.0, outbound process, pipeline math |

### MEDIUM PRIORITY — Growth & Operations

| Skill | Source | Use When |
|-------|--------|----------|
| **traction-eos** | Wickman — *Traction* | VTO (Vision/Traction Organizer), 10-3-1 planning, rocks |
| **design-sprint** | GV — *Sprint* | 5-day sprint: map, sketch, decide, prototype, test |
| **hooked-ux** | Eyal — *Hooked* | Retention loops, trigger-action-reward-investment cycles |
| **influence-psychology** | Cialdini — *Influence* | CRO audits, 7 principles: reciprocity, commitment, social proof, authority, liking, scarcity, unity |
| **negotiation** | Voss — *Never Split the Difference* | Tactical empathy, labels, calibrated questions, "that's right" moments |
| **drive-motivation** | Pink — *Drive* | AMP framework: Autonomy, Mastery, Purpose for team incentives |

### LOWER PRIORITY — Specialized Design/UX

| Skill | Source | Use When |
|-------|--------|----------|
| **refactoring-ui** | Wathan/Schoger — *Refactoring UI* | UI hierarchy, visual design without designer |
| **web-typography** | Santa Maria — *On Web Typography* | Readability audit, type scale, line length, hierarchy |
| **ux-heuristics** | Nielsen/Norman — 10 Heuristics | Usability audit, severity ratings 0-4 |
| **design-everyday-things** | Norman — *Design of Everyday Things* | Affordances, signifiers, feedback, mental models |
| **ios-hig-design** | Apple — Human Interface Guidelines | iOS compliance: 44pt targets, Dynamic Island, safe areas |
| **top-design** | Elite agencies (Locomotive, AREA 17, Studio Freight) | Awwwards-level: type systems, scroll reveals, micro-interactions |
| **scorecard-marketing** | Scorecard funnel methodology | Quiz funnels: 12 questions, scoring logic, 3 result tiers |
| **made-to-stick** | Heath Brothers — *Made to Stick* | SUCCESs checklist: Simple, Unexpected, Concrete, Credible, Emotional, Stories |
| **cro-methodology** | CRO frameworks | Top 5 objections, missing persuasion assets, principle gaps |

---

## Usage Pattern

```text
You: "Help me position our product. Use blue-ocean-strategy skill."
Agent: Applies Kim & Mauborgne framework — Strategy Canvas + Four Actions

You: "Uncover the real JTBD for our SaaS. Use jobs-to-be-done skill."
Agent: Runs Christensen's framework — hiring managers, competing hires

You: "Design a Cold Calling 2.0 outbound process. Use predictable-revenue skill."
Agent: Outputs ICP, 3-email sequence, qualification criteria, pipeline math
```

Each skill provides:
- Structured framework application (not generic advice)
- Copy-pasteable prompts from the Wondel site
- Reference files with book frameworks, templates, checklists

---

## Verification

After installing a skill, verify it loads:
```bash
hermes skills list | grep <skill-name>
```

Then test invocation:
```text
"Use jobs-to-be-done skill to analyze our product"
```

---

## References

- `references/wondel-skills-inventory.md` — Complete skill list with descriptions
- `references/installation-guide.md` — Bulk install and Hermes integration steps
- Source: https://github.com/bilalmirza2001/skills (MIT licensed)
- Wondel site: https://skills.wondel.ai/