#!/usr/bin/env python3
"""Rebuild the bundled-skill list and skill counts in SKILL.md and README.md.

Run from the repository root after an upstream merge adds or removes a skill.
"""
import os, re

def description(path):
    text = open(path, encoding="utf-8").read()
    m = re.match(r"---\n(.*?)\n---", text, re.S)
    if not m: return ""
    lines = m.group(1).split("\n")
    for i, line in enumerate(lines):
        if line.startswith("description:"):
            v = line[len("description:"):].strip()
            if v in (">-", ">", "|", "|-"):
                v = " ".join(l.strip() for l in lines[i + 1:] if l.startswith((" ", "\t")))
            v = v.strip()
            if v[:1] == '"' and v[-1:] == '"': v = v[1:-1].replace('\\"', '"')
            return v.strip("'")
    return ""

def short(d, n=150):
    if len(d) <= n: return d
    cut = d[:n].rsplit(" ", 1)[0] if " " in d[:n] else d[:n]
    return cut.rstrip(" ,.;:") + "…"

skills = sorted(d for d in os.listdir("skills")
                if os.path.exists(f"skills/{d}/INSTRUCTIONS.md"))
items = "\n".join(f"- `{s}`: {short(description(f'skills/{s}/INSTRUCTIONS.md'))}" for s in skills)

p = "SKILL.md"
s = open(p, encoding="utf-8").read()
s = re.sub(r"(## Bundled skills\n\n)(?:- `.*\n?)+", lambda m: m.group(1) + items + "\n", s)
s = re.sub(r"Its \d+ skills are bundled", f"Its {len(skills)} skills are bundled", s)
playbooks = len([f for f in os.listdir("skills/miracle-mode/playbooks") if f.endswith(".md")])
s = re.sub(r"with \d+ playbooks", f"with {playbooks} playbooks", s)
open(p, "w", encoding="utf-8").write(s)

p = "README.md"
s = open(p, encoding="utf-8").read()
s = re.sub(r"holds the other \d+ skills", f"holds the other {len(skills) - 1} skills", s)
open(p, "w", encoding="utf-8").write(s)
print(f"{len(skills)} skills indexed")
