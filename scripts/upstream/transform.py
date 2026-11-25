#!/usr/bin/env python3
"""Turn an upstream pstack folder into the mechanical part of mstack.

Usage: transform.py <pstack-dir> <out-dir>

Only the renames that apply to every file live here. mstack's hand edits
(the claude.ai adapter lines, the all-Opus model tables, and so on) live
as commits on main, and git merges them with each new upstream snapshot.
"""
import os, re, shutil, sys

src, out = sys.argv[1], sys.argv[2]
if os.path.exists(out):
    shutil.rmtree(out)
shutil.copytree(src, out)
os.chdir(out)

def rm(p):
    if os.path.isdir(p): shutil.rmtree(p)
    elif os.path.exists(p): os.remove(p)

for p in [".cursor-plugin", "assets", "automations", "plugin.json",
          "docs/harness/claude-code.md", "skills/statechart/scripts/test"]:
    rm(p)
os.replace("README.md", "docs/upstream-README.md")

MOVES = {
    "skills/poteto-mode": "skills/miracle-mode",
    "skills/poteto-help": "skills/miracle-help",
    "skills/setup-pstack": "skills/setup-mstack",
    "agents/poteto-agent.md": "agents/miracle-agent.md",
    "docs/guide/02-poteto-mode.md": "docs/guide/02-miracle-mode.md",
}
for a, b in MOVES.items():
    if os.path.exists(a): os.replace(a, b)
for d in sorted(os.listdir("skills")):
    s = os.path.join("skills", d, "SKILL.md")
    if os.path.exists(s):
        os.replace(s, os.path.join("skills", d, "INSTRUCTIONS.md"))

def skill_md(m):
    t = m.group(1)
    # A path into this bundle points at INSTRUCTIONS.md. A user's or project's
    # own skill path (.cursor/..., <handle>, globs, ~) keeps SKILL.md.
    if "/" in t and not re.search(r"\.cursor|<|\*|~|\{", t):
        return t + "INSTRUCTIONS.md"
    return t + "SKILL.md"

RULES = [
    (r"poteto-mode", "miracle-mode"),
    (r"poteto-agent", "miracle-agent"),
    (r"poteto-help", "miracle-help"),
    (r"(?m)^# Poteto (mode|help|subagent)", r"# Miracle \1"),
    (r"setup-pstack", "setup-mstack"),
    (r"\bpstack\b", "mstack"),
    # upstream URLs keep their real path
    (r"(github\.com/cursor/plugins/(?:tree|blob)/main/[\w./-]*?)\bmstack\b", r"\1pstack"),
    (r"\]\((?:\.\./)+automations/", "](https://github.com/cursor/plugins/blob/main/pstack/automations/"),
    (r"([^\s`()\[\]\"']*)SKILL\.md", skill_md),
    (r"skill's `SKILL\.md`", "skill's `INSTRUCTIONS.md`"),
    (r"harness/claude-code\.md", "harness/claude-ai.md"),
    (r"\]\(\.\./\.\./README\.md\)", "](../../docs/upstream-README.md)"),
]

ADAPTER_LINE = ("In claude.ai, read [the claude.ai adapter](../../docs/harness/claude-ai.md) "
                "once per session before you follow this skill. It maps the Cursor names in "
                "mstack skills to claude.ai.")
# Skills that need no adapter pointer (they name no Cursor tools). Every other
# skill, including one upstream adds later, gets the pointer under its title.
NO_ADAPTER = {
    "benchmark-checklist",
    "blast-radius",
    "bro",
    "correct",
    "in-your-own-words",
    "ketchup",
    "ketchup-video",
    "principle-attack-the-premise",
    "principle-boundary-discipline",
    "principle-build-the-lever",
    "principle-encode-lessons-in-structure",
    "principle-exhaust-the-design-space",
    "principle-experience-first",
    "principle-explain-the-number",
    "principle-fix-root-causes",
    "principle-foundational-thinking",
    "principle-guard-the-context-window",
    "principle-laziness-protocol",
    "principle-make-operations-idempotent",
    "principle-migrate-callers-then-delete-legacy-apis",
    "principle-minimize-reader-load",
    "principle-model-the-domain",
    "principle-never-block-on-the-human",
    "principle-outcome-oriented-execution",
    "principle-redesign-from-first-principles",
    "principle-separate-before-serializing-shared-state",
    "principle-sequence-verifiable-units",
    "principle-subtract-before-you-add",
    "principle-test-behavior-not-implementation",
    "principle-type-system-discipline",
    "sharpen",
    "statechart",
    "tdd",
    "typescript-best-practices",
    "unslop",
}

TEXT = (".md", ".ts", ".json", ".yaml", ".yml", ".mmd", ".sh", ".tla", ".cfg", ".lock", ".txt", ".js")
for root, _, files in os.walk("."):
    for f in files:
        if not f.endswith(TEXT): continue
        p = os.path.join(root, f)
        try: s = open(p, encoding="utf-8").read()
        except UnicodeDecodeError: continue
        n = s
        for pat, rep in RULES: n = re.sub(pat, rep, n)
        if p == "./docs/upstream-README.md":
            # the README moved from the root into docs/
            n = re.sub(r"\]\(\./docs/", "](./", n)
            n = re.sub(r"\]\(\./(skills|agents|LICENSE)", r"](../\1", n)
            n = re.sub(r"\]\(\./automations/", "](https://github.com/cursor/plugins/blob/main/pstack/automations/", n)
        if n != s: open(p, "w", encoding="utf-8").write(n)

for d in sorted(os.listdir("skills")):
    p = os.path.join("skills", d, "INSTRUCTIONS.md")
    if d in NO_ADAPTER or not os.path.exists(p): continue
    s = open(p, encoding="utf-8").read()
    if ADAPTER_LINE in s: continue
    s = re.sub(r"(?m)^(# .+\n)\n", lambda m: m.group(1) + "\n" + ADAPTER_LINE + "\n\n", s, count=1)
    open(p, "w", encoding="utf-8").write(s)
