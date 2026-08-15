# Converting External Skills to Hermes

Covers installing skills from other ecosystems (Codex, Claude Code, Anthropic, etc.) and making them Hermes-compatible.

---

## When to Use

- Installing skills from GitHub repos (openai/skills, anthropics/skills, etc.)
- Porting skills between agent platforms
- Making third-party skills discoverable under short names

---

## Standard Conversion Process

### 1. Fetch & Inspect

```bash
# GitHub raw content
web_extract "https://raw.githubusercontent.com/owner/repo/main/skills/skill-name/SKILL.md"

# Or clone repo
git clone https://github.com/owner/repo.git /tmp/repo
ls /tmp/repo/skills/
```

### 2. Copy to Hermes Skills Directory

```bash
# Target: ~/AppData/Local/hermes/skills/<category>/
cp -r /tmp/repo/skills/skill-name ~/AppData/Local/hermes/skills/software-development/
```

### 3. Rename Directory (Optional — for grouping)

```bash
# Add prefix for organization, e.g. superpowers-, ce-, anthropic-
mv ~/AppData/Local/hermes/skills/software-development/skill-name \
   ~/AppData/Local/hermes/skills/software-development/prefix-skill-name
```

**Directory name ≠ invocation name.** Only affects filesystem organization.

### 4. Update Frontmatter `name` Field

```bash
# Set short, invokable name (no prefix)
sed -i 's/^name: .*$/name: short-skill-name/' ~/AppData/Local/hermes/skills/software-development/prefix-skill-name/SKILL.md
```

**Critical:** The `name` field controls discovery. Users call `skill_view("short-skill-name")`. Prefixes in `name` create friction.

### 5. Rewrite Cross-References

```bash
# Replace old namespace references with new short names
# e.g., superpowers:writing-plans → writing-plans
find ~/AppData/Local/hermes/skills/software-development/prefix-skill-name -name "*.md" -exec \
  sed -i 's/old-namespace:/new-short-name-/g' {} \;

# Also fix docs/ paths if they reference old structure
sed -i 's|docs/old-path|docs/new-path|g' ~/AppData/Local/hermes/skills/software-development/prefix-skill-name/SKILL.md
```

### 6. Verify

```bash
# Check frontmatter
grep "^name:" ~/AppData/Local/hermes/skills/software-development/prefix-skill-name/SKILL.md

# Test invocation
skill_view(name="short-skill-name")
```

---

## Common Patterns by Source

### Superpowers (Claude Code)

| Original | Hermes |
|----------|--------|
| Directory: `skills/writing-plans` | `superpowers-writing-plans/` |
| `name: writing-plans` | `name: writing-plans` (already short) |
| Refs: `superpowers:subagent-driven-development` | `subagent-driven-development` |

### Anthropic Skills

| Original | Hermes |
|----------|--------|
| Single `SKILL.md` file | Create directory, add `SKILL.md` |
| No cross-refs usually | N/A |
| Rich design guidance | Keep as-is |

### Codex Skills (openai/skills)

| Original | Hermes |
|----------|--------|
| `skills/.curated/skill-name/` | Category directory |
| May have `agents/openai.yaml` | Ignore (Hermes doesn't use) |
| Scripts in `scripts/` | Keep if portable |

---

## Pitfalls to Avoid

| Pitfall | Fix |
|---------|-----|
| Prefix in `name` field | Use short name only |
| Old namespace in cross-refs | Batch rewrite with `sed` |
| Absolute paths in examples | Make relative or generic |
| Platform-specific tools (e.g., `@` links) | Replace with skill names + `REQUIRED SUB-SKILL` |
| Missing description field | Add `Use when...` triggering conditions |

---

## Verification Checklist

- [ ] `skill_view("short-name")` works
- [ ] `skills_list` shows skill in correct category
- [ ] Cross-refs resolve to existing skills
- [ ] No old namespace references remain
- [ ] Description starts with "Use when..."
- [ ] Frontmatter has only `name` and `description`

---

## Example: This Session's Conversions

### Superpowers (14 skills)
```bash
git clone https://github.com/obra/superpowers.git /tmp/sp
cp -r /tmp/sp/skills/* ~/AppData/Local/hermes/skills/software-development/
# Rename dirs to superpowers-*
# Update name fields to short form
# Rewrite superpowers: → short-name-
```

### Anthropic Frontend Design
```bash
web_extract "https://raw.githubusercontent.com/anthropics/skills/main/skills/frontend-design/SKILL.md"
# Write to ~/AppData/Local/hermes/skills/software-development/frontend-design/SKILL.md
# name: frontend-design (already short, no prefix needed)
```

---

## Iron Law Applies

**No skill without a failing test first.** After conversion:
1. Run baseline scenario WITHOUT the skill (or with broken version)
2. Verify the issue the skill addresses
3. Apply conversion
4. Run scenario WITH skill — must pass

If you skip testing the converted skill, you don't know if the conversion worked.