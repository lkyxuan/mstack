# mstack

Miracle's stack, by 0xmiracle.

mstack is built on [pstack](https://github.com/cursor/plugins/tree/main/pstack) by Lauren Tan ([@poteto](https://github.com/poteto)), from pstack 0.15.36 (cursor/plugins commit `6b03002`, 2026-11-06). Both are MIT licensed. See `LICENSE`.

## When to use it

mstack is opt-in. It loads only when you type `/mstack`, never on its own, the same as pstack's `poteto-mode`. It is rigorous and suited to large work: features that cross modules, migrations, hard bugs, long unattended runs. On a small task it burns tokens and runs slowly, so skip it for quick fixes and questions.

## Install

- claude.ai: save `mstack.skill` from a chat, or zip this folder and upload it as a skill.
- Claude Code: `git clone https://github.com/lkyxuan/mstack ~/.claude/skills/mstack`. Update with `git -C ~/.claude/skills/mstack pull`.

## Use

- `/mstack <task>` for anything that needs rigor. It picks a playbook and runs the other skills as needed.
- `/mstack <skill> ...` to run one bundled skill directly, such as `/mstack how does the sync engine work`.
- `/mstack help` when unsure which skill fits.

## How it is laid out

- `SKILL.md` is the one installed skill. It routes to the bundled skills.
- `skills/miracle-mode/` is the main mode: playbooks, principles index, and the rules every run follows.
- `skills/` holds the other 56 skills. Each keeps its instructions in `INSTRUCTIONS.md`, because claude.ai allows one `SKILL.md` per skill.
- `agents/` holds the subagent roles, `miracle-agent` and `comment-sicko`.
- `docs/harness/claude-ai.md` and `docs/harness/claude-code.md` map the Cursor names in the skills to claude.ai and to Claude Code, and set every role to Opus.
- `docs/upstream-README.md` is the upstream pstack README, kept for reference.

## Changes from pstack

- Packaged as one claude.ai skill, `mstack`.
- `poteto-mode` is `miracle-mode`, `poteto-agent` is `miracle-agent`, `poteto-help` is `miracle-help`, and `setup-pstack` is `setup-mstack`.
- Every role runs on Opus. pstack's multi-model panels run as same-model panels.
- A claude.ai adapter replaces the Cursor and Claude Code harness.
- The `statechart` skill's developer test corpus is removed.
