# Bundled Skills Opt-Out Pattern

## Problem
Hermes automatically seeds ~70 "bundled skills" from its internal manifest (`.bundled_manifest`) into `~/.hermes/skills/` on every `hermes update` (and potentially on startup). This recreates category folders like `apple/`, `smart-home/`, `media/`, `email/` even after manual deletion.

## Solution
Permanently disable bundled skill seeding for the current profile:

```bash
hermes skills opt-out --remove --yes
```

This does two things:
1. **Writes `~/.hermes/.no-bundled-skills`** — marker file telling Hermes to never seed bundled skills into this profile again
2. **`--remove` flag** — deletes all currently-present, unmodified bundled skills in one pass

## What Gets Removed
All skills listed in `.bundled_manifest` that haven't been user-modified (patches, edits). Builtin/core skills (`hermes-agent`, `obsidian`, `plan`) remain. Hub-installed skills remain.

## Verification
```bash
# Check marker exists
cat ~/.hermes/.no-bundled-skills

# Confirm bundled skills no longer appear
hermes skills list | grep -E "apple|media|smart-home|arxiv|blogwatcher|google-workspace"
# Should return empty
```

## Re-enabling
If you ever want bundled skills back:
```bash
rm ~/.hermes/.no-bundled-skills
hermes skills opt-in   # or just run `hermes update`
```

## When to Use
- User explicitly doesn't want default skills polluting their profile
- Profile is specialized (dev-only, research-only) and bundled skills add noise
- Cleaning up a profile that accumulated unwanted bundled skills over time

## Alternative: Selective Disable (Keep Bundled Seeding, Hide Only Specific Skills)
If the user wants to **keep bundled skill seeding** but hide only specific categories (e.g. Apple, Smart Home, Email, Media), use `skills.disabled` in config.yaml instead:

```yaml
# ~/.hermes/config.yaml
skills:
  disabled:
  - apple-notes
  - apple-reminders
  - findmy
  - imessage
  - macos-computer-use
  - openhue
  - himalaya
  - gif-search
  - heartmula
  - songsee
  - youtube-content
```

This keeps the `.no-bundled-skills` marker absent (so future `hermes update` still seeds new bundled skills), but prevents the listed skills from loading.

**Verification:**
```bash
hermes skills list | grep -iE "openhue|himalaya|gif-search"
# Should show 'disabled' status
```

**When to use selective disable vs opt-out:**
| Approach | Use when... |
|----------|-------------|
| `opt-out --remove` | User wants NO bundled skills ever; clean slate |
| `skills.disabled` | User wants most bundled skills, just hide specific noise |

## Pitfalls
- **Don't confuse with `hermes skills uninstall`** — that only removes hub-installed skills, not bundled ones
- **`opt-out` without `--remove`** only writes the marker; existing bundled skills stay on disk
- **The marker is profile-specific** — other profiles under `~/.hermes/profiles/<name>/` are unaffected
- **Apple skills live in `apple/` subdirectory** and don't appear in flat `hermes skills list` — adding them to `skills.disabled` is defensive but they're already hidden by scanner design
- **Protected skills**: `hermes-agent` (bundled) cannot be edited to document this; capture in non-protected umbrella instead