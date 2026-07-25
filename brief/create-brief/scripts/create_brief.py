#!/usr/bin/env python3
"""Create Brief — machine-parseable + human-readable session brief.

GENERALIZED: detects the active project from git (cwd's repo root) and
produces a valid brief for ANY repo, not a hardcoded one. Verification
commands are DERIVED from the project's manifest (npm build/test/lint,
python pytest/build, etc.); design-system-specific checks are opt-in via
--design-system so they never run on unrelated repos.

Writes to the canonical briefs dir. Integrates with load-brief.
"""
import argparse
import json
import subprocess
from datetime import datetime
from pathlib import Path

# Canonical briefs dir is Hermes-wide, NOT project-specific.
BRIEFS_DIR = Path(r"C:/Users/Tiger/AppData/Local/hermes/briefs")


def run_cmd(cmd, cwd=None):
    """Run a shell command; return (success, stdout, stderr).

NOTE: under MSYS/git-bash, subprocess.run(shell=True) mangles
single-quoted args (e.g. git --format='%h %s') when cwd is a
Windows backslash path. Posix-ify cwd so the shell sees /c/Users/...
and the quotes survive.
"""
    posix_cwd = str(Path(cwd)).replace("\\", "/") if cwd else None
    try:
        r = subprocess.run(cmd, shell=True, cwd=posix_cwd,
                           capture_output=True, text=True, timeout=120)
        return r.returncode == 0, r.stdout.strip(), r.stderr.strip()
    except subprocess.TimeoutExpired:
        return False, "", "timeout"
    except Exception as e:  # pragma: no cover
        return False, "", str(e)


def detect_root(explicit=None):
    """Repo root: explicit arg > git toplevel of cwd > cwd."""
    if explicit:
        return Path(explicit).resolve()
    ok, out, _ = run_cmd("git rev-parse --show-toplevel")
    if ok and out:
        return Path(out).resolve()
    return Path.cwd().resolve()


def detect_project_name(root):
    pkg = root / "package.json"
    if pkg.exists():
        try:
            return json.loads(pkg.read_text(encoding="utf-8")).get("name", root.name)
        except Exception:
            pass
    tom = root / "pyproject.toml"
    if tom.exists():
        for line in tom.read_text(encoding="utf-8").splitlines():
            s = line.strip()
            if s.startswith("name") and "=" in s:
                return s.split("=", 1)[1].strip().strip('"')
    return root.name


def detect_ecosystem(root):
    """Map of available verify commands, derived from manifests (not hardcoded)."""
    cmds = {}
    pkg = root / "package.json"
    if pkg.exists():
        try:
            scripts = json.loads(pkg.read_text(encoding="utf-8")).get("scripts", {})
            if "build" in scripts:
                cmds["build"] = "npm run build"
            if "test" in scripts:
                cmds["test"] = "npm test"
            if "lint" in scripts:
                cmds["lint"] = "npm run lint"
        except Exception:
            pass
    tom = root / "pyproject.toml"
    if tom.exists():
        text = tom.read_text(encoding="utf-8")
        if "pytest" in text:
            cmds["test"] = "pytest -q"
        if "[build-system]" in text or "build" in text:
            cmds.setdefault("build", "python -m build")
    return cmds


def get_git_info(root):
    info = {}
    ok, out, _ = run_cmd("git branch --show-current", cwd=root)
    info["branch"] = out if ok and out else "detached"
    ok, h, _ = run_cmd("git rev-parse --short HEAD", cwd=root)
    ok2, subj, _ = run_cmd("git log -1 --format=%s", cwd=root)
    info["last_commit"] = (f"{h} {subj}".strip() if (ok and ok2 and h and subj) else "unknown")
    ok, out, _ = run_cmd("git status --porcelain", cwd=root)
    info["dirty"] = bool(out.strip())
    info["status_short"] = out.strip()[:500]
    ok, out, _ = run_cmd("git rev-parse HEAD", cwd=root)
    info["head"] = out[:8] if ok else "unknown"
    ok, out, _ = run_cmd("git log --oneline -10", cwd=root)
    info["recent_commits"] = out.strip() if ok else ""
    return info


def verify_critical(root, eco, design_system=False):
    checks = {}
    ok, out, _ = run_cmd("git status --porcelain", cwd=root)
    checks["git_clean"] = {"passed": not out.strip(),
                            "output": out[:200] if out else "clean"}
    for name, cmd in eco.items():
        ok, out, err = run_cmd(cmd, cwd=root)
        checks[name] = {"passed": ok, "output": (out or err)[-200:]}
    if design_system:
        # Opt-in: statistics-style design-system guards only.
        ok, out, _ = run_cmd(
            r"grep -rE 'slate-|zinc-|gray-' src/ --include='*.tsx' 2>/dev/null "
            r"| grep -v 'var(--' | head -5",
            cwd=root)
        checks["no_raw_tailwind_colors"] = {"passed": not out.strip(),
                                           "output": out[:200] if out else "none found"}
        css = (root / "src/index.css").read_text(encoding="utf-8") \
            if (root / "src/index.css").exists() else ""
        sig = all(x in css for x in
                  [".accent-bar", ".curve-low", ".stagger-in", ".pulse-brass"])
        checks["signature_elements"] = {"passed": sig,
                                       "output": "all present" if sig else "missing"}
    all_passed = all(c["passed"] for c in checks.values())
    return all_passed, checks


def detect_key_files(root):
    cands = ["README.md", "AGENTS.md", "CLAUDE.md", "CONTEXT.md",
              "STRATEGY.md", "DESIGN.md", "pyproject.toml", "package.json",
              "requirements.txt", "Makefile", "Dockerfile"]
    return [c for c in cands if (root / c).exists()]


def generate_brief(phase_from, phase_to, session_id, profile, root,
                   design_system, notes):
    git_info = get_git_info(root)
    eco = detect_ecosystem(root)
    all_passed, checks = verify_critical(root, eco, design_system)
    name = detect_project_name(root)
    key_files = detect_key_files(root)

    frontmatter = {
        "session_id": session_id,
        "created": datetime.now().isoformat(),
        "phase_from": phase_from,
        "phase_to": phase_to,
        "profile": profile,
        "project": name,
        "project_root": str(root),
        "branch": git_info["branch"],
        "base_commit": git_info["head"],
        "last_commit": git_info["last_commit"],
        "git_dirty": git_info["dirty"],
        "verification_passed": all_passed,
        "schema_version": "1.0",
    }

    s = []
    s.append("## Project Context")
    s.append(f"**Repository:** `{root}`")
    s.append(f"**Branch:** `{git_info['branch']}`")
    s.append(f"**Base Commit:** `{git_info['head']}` — {git_info['last_commit']}")
    s.append(f"**Project type:** {', '.join(eco) if eco else 'manual/unknown'}")
    if key_files:
        s.append("")
        s.append("**Detected key files:** " +
                 ", ".join(f"`{f}`" for f in key_files))
    s.append("")

    s.append("## What Was Done")
    s.append("")
    if git_info["recent_commits"]:
        s.append("### Recent commits on branch")
        for line in git_info["recent_commits"].splitlines():
            s.append(f"- `{line}`")
    else:
        s.append("- (no commit history available)")
    if git_info["dirty"]:
        s.append("")
        s.append("### Uncommitted changes (`git status --porcelain`)")
        for line in git_info["status_short"].splitlines():
            s.append(f"- `{line}`")
    s.append("")

    s.append("## Verification Results")
    for n, c in checks.items():
        st = "✅" if c["passed"] else "❌"
        s.append(f"- {st} **{n}**: {c['output'][:120]}")
    s.append("")

    s.append("## Current State")
    s.append("")
    s.append(f"- Working directory / repo root: `{root}`")
    s.append(f"- Objective / next phase: *describe* (phase_to = `{phase_to}`)")
    s.append("- Missing pieces: *fill in*")
    s.append("- Existing assets: *fill in*")
    if notes:
        s.append("")
        s.append("### Session notes")
        for nline in notes:
            s.append(f"- {nline}")
    s.append("")

    s.append("## Blocking Decisions")
    s.append("")
    s.append("| Decision | Context | Blocking |")
    s.append("|----------|---------|----------|")
    s.append("| *add row* | *context* | *yes/no* |")
    s.append("")

    s.append("## Risks")
    s.append("")
    s.append("| Risk | Impact | Likelihood | Mitigation |")
    s.append("|------|--------|------------|------------|")
    s.append("| *add row* | *impact* | *likelihood* | *mitigation* |")
    s.append("")

    s.append("## Verification Checklist (Next Agent MUST Run)")
    s.append("")
    for n, c in checks.items():
        st = "✅" if c["passed"] else "❌"
        s.append(f"- [ ] {st} **{n}** — {c['output'][:80]}")
    s.append("")

    s.append("## Quick Start for Next Agent")
    s.append("")
    s.append("```bash")
    s.append(f"cd {root}")
    s.append(f"git checkout {git_info['branch']}")
    for cmd in eco.values():
        s.append(f"# {cmd}")
        s.append(cmd)
    s.append("# Load this brief:")
    s.append("python C:/Users/Tiger/AppData/Local/hermes/skills/brief/load-brief/scripts/load_brief.py")
    s.append("```")
    s.append("")

    s.append("## Context Engineering Files Status")
    s.append("")
    s.append("| File | Status |")
    s.append("|------|--------|")
    for f in ["AGENTS.md", "CLAUDE.md", "CONTEXT.md", "STRATEGY.md", "DESIGN.md"]:
        p = root / f
        st = "✅ Present" if p.exists() else "⚠️ Not found"
        s.append(f"| `{f}` | {st} |")
    s.append("")

    s.append("## Reference Artifacts (Do Not Duplicate)")
    s.append("")
    s.append("| Artifact | Path |")
    s.append("|----------|------|")
    for f in key_files:
        s.append(f"| `{f}` | `{root / f}` |")
    s.append("")

    yaml_lines = []
    for k, v in frontmatter.items():
        if isinstance(v, (dict, list, bool)):
            yaml_lines.append(f"{k}: {json.dumps(v)}")
        else:
            yaml_lines.append(f"{k}: {v}")
    doc = "---\n" + "\n".join(yaml_lines) + "\n---\n\n" + \
          f"# Brief: {phase_from} → {phase_to}\n\n" + "\n".join(s)
    return doc, frontmatter, checks


def main():
    p = argparse.ArgumentParser(description="Create brief (generic, any project).")
    p.add_argument("--phase-from", required=True)
    p.add_argument("--phase-to", required=True)
    p.add_argument("--session-id", required=True)
    p.add_argument("--profile", default="default")
    p.add_argument("--project-root", default=None,
                   help="Repo root. Default: git toplevel of cwd, else cwd.")
    p.add_argument("--design-system", action="store_true",
                   help="Add design-system checks (slate/zinc/signature). Opt-in.")
    p.add_argument("--note", action="append", default=[],
                   help="Session note line (repeatable).")
    a = p.parse_args()

    root = detect_root(a.project_root)
    BRIEFS_DIR.mkdir(parents=True, exist_ok=True)

    doc, fm, checks = generate_brief(
        a.phase_from, a.phase_to, a.session_id, a.profile,
        root, a.design_system, a.note)

    all_passed = all(c["passed"] for c in checks.values())
    ts = datetime.now().strftime("%Y%m%d-%H%M")
    filename = (f"brief-{a.profile}-{fm['project']}-"
               f"{a.phase_from}-to-{a.phase_to}-{ts}.md")
    filepath = BRIEFS_DIR / filename
    filepath.write_text(doc, encoding="utf-8")

    print(f"✅ Brief created: {filepath}")
    print(f"📋 Session: {a.session_id} | Phase: {a.phase_from} → {a.phase_to}")
    print(f"🔍 Verification: {'ALL PASSED' if all_passed else 'SOME FAILED'}")
    for n, c in checks.items():
        st = "✅" if c["passed"] else "❌"
        print(f"   {st} {n}")
    print(f"🎯 Recommended follow-up: review phase_to objective; fill Blocking/Risks")
    print("📂 Load: python C:/Users/Tiger/AppData/Local/hermes/skills/brief/load-brief/scripts/load_brief.py")


if __name__ == "__main__":
    main()
