# mstack in Claude Code

mstack is a fork of pstack, which was written for Cursor. Its skills still use Cursor names. In Claude Code, read this file once per session, then map each Cursor name with the tables below. If a Cursor field has no row, drop it and say so. Never pass a field or value the tool schema rejects.

`<mstack>` means the folder that holds this skill's top-level `SKILL.md`, `skills/` and `docs/`, normally `~/.claude/skills/mstack`. The Skill tool prints it as the skill's base directory when `mstack` loads. Use that absolute path in every brief.

Each bundled skill keeps its instructions in `<mstack>/skills/<name>/INSTRUCTIONS.md`, not `SKILL.md`, so that the same folder also installs in claude.ai, which allows one `SKILL.md` per skill. Where any text says a bundled skill's `SKILL.md`, read its `INSTRUCTIONS.md`. A `SKILL.md` you write for the user's own project is still named `SKILL.md`.

## Install and update

```bash
git clone https://github.com/lkyxuan/mstack ~/.claude/skills/mstack
git -C ~/.claude/skills/mstack pull   # update
```

The user starts it with `/mstack`. It is opt-in. Never load it on your own.

## Tools

| Cursor | Claude Code |
| --- | --- |
| `Task` | `Agent` |
| `AskQuestion` | `AskUserQuestion`. In `-p` mode it is absent, so ask in plain text. |
| Open a todolist | `TodoWrite`, or `TaskCreate` and `TaskUpdate`, whichever the session offers. Otherwise keep the list in your reply and update it at each phase. |
| Run another mstack skill (`/name` or "the **name** skill") | `Read` `<mstack>/skills/<name>/INSTRUCTIONS.md` and follow it. Only `mstack` is installed as a skill, so the `Skill` tool cannot find the others. When you tell the user how to call one, write "`/mstack <name>`". Where a skill tells the user to type `/miracle-mode`, write `/mstack`. |
| `Grep`, `Glob` | The same tools. In a session without them, `Bash` with `rg`. |

## Subagent fields

| Cursor | Claude Code |
| --- | --- |
| `subagent_type: generalPurpose` | `subagent_type: "general-purpose"` |
| `miracle-agent`, `comment-sicko` | Not registered as agent types, because mstack installs as a skill, not a plugin. Use `subagent_type: "general-purpose"` and open the brief with "Read `<mstack>/agents/<name>.md` in full and act as that agent." For `miracle-agent`, also give the absolute path of `<mstack>/skills/miracle-mode/INSTRUCTIONS.md`. |
| `readonly: true` | `subagent_type: "Explore"`. It keeps `Bash`, so the brief also says "do not edit files", and you check `git status` afterward. |
| `readonly: false` | `general-purpose`. It keeps the session's MCP servers. |
| `environment: "cloud"` | `isolation: "worktree"`. Name the branch or commit the worker checks out. |
| `environment: "local"` | Omit. |
| `cloud_base_branch: <b>` | Tell the worker to check out `<b>` first. |
| `run_in_background: true` | Omit. Subagents run in the background by default and notify you when they finish. |
| `resume` | Spawn a new agent and paste the earlier result into its brief. Use `SendMessage` only in the strict cases miracle-mode's Subagents section allows. |
| `file_attachments` | List the absolute paths in the brief. |

## Models

mstack runs every role on Opus. Pass `model: "opus"` on every `Agent` call, and `effort: "xhigh"` when the schema offers an effort field.

The table below is the role table. Wherever a skill reads a line from the `mstack-models.mdc` rule, `~/.cursor/rules/mstack-models.mdc`, or `~/.claude/rules/mstack-models.md`, use the matching line here instead. A role missing from the table also runs on `opus xhigh`.

```
# mstack model configuration for Claude Code. Every role on Opus.
feature, refactoring: opus xhigh
bug-fix: opus xhigh
perf-issue: opus xhigh
hillclimb: opus xhigh
judgment and prose: opus xhigh
hardest tasks: opus max
how explorer: opus high
how explainer: opus xhigh
why investigators: opus high
why synthesizer: opus xhigh
reflect tooling: opus high
reflect judgment, divergent, synthesizer: opus xhigh
arena runners: opus xhigh, opus xhigh
arena cross-judge pool: opus xhigh
swarm workers: opus high
architect runners: opus xhigh, opus xhigh
interrogate reviewers: opus xhigh, opus xhigh
```

| Cursor | Claude Code |
| --- | --- |
| Any model slug, Claude or not (`claude-opus-*`, `grok-*`, `gpt-*`, `composer-*`) | `model: "opus"` with the role's effort from the table. |
| `auto` or `inherit-parent` | `model: "opus"` |
| Raise or lower the reasoning effort | Move the `effort` value one step on the ladder `max` > `xhigh` > `high` > `medium` > `low`. Drop `-fast`. If the schema has no effort field, keep `opus` and say nothing. |
| A panel of different models (`arena`, `architect`, `interrogate`) | One `opus` agent per seat, each with a fresh brief and no view of the others. Agreement between them is weaker evidence than agreement across model families, so say "same-model panel" when you report it. |
| A judge or reviewer that must come from a family other than the parent's | Use a fresh `opus` agent that never saw the candidates being made, and say the judge shares the parent's model. |
| Codex or another outside model | Not used by mstack. Verify with `opus`. The user may run Codex on the result themselves. |

## setup-mstack

The role table above replaces the rule file. Follow `setup-mstack` with these changes:

- Detect. Skip it. Every role runs on `opus`.
- Budget. A budget changes only the effort values in the table. Show the user the resulting table.
- Write. Do not write `~/.claude/rules/mstack-models.md`. The table lives in this file in the user's repo. To change it for good, edit this file, commit, and push.
- Steps 7 and 8 work as written.

## Paths

| Cursor | Claude Code |
| --- | --- |
| `.cursor/skills/`, `~/.cursor/skills/` | `.claude/skills/`, `~/.claude/skills/` |
| `~/.cursor/plugins/`, `.cursor-plugin/plugin.json` | `<mstack>`. There is no plugin manifest. |
| `.cursor/rules/*.mdc`, always-applied rules | `CLAUDE.md`, or `AGENTS.md` when no `CLAUDE.md` exists. Claude Code never reads `.mdc` files. The model rule is the exception. See Models. |
| `https://github.com/cursor/plugins/blob/main/pstack/<path>` | `<mstack>/<path>` when that file exists. Read the local copy and never fetch it. Give the user the URL when they need a link to the upstream original. |
| Transcripts in `~/.cursor/projects/<slug>/agent-transcripts/` | `~/.claude/projects/<slug>/<session>.jsonl`. The slug is the workspace path with each `/` and `.` changed to `-`, so `/Users/you/proj` is `-Users-you-proj`. The newest `.jsonl` directly in that folder is the current session. Its `<session>/subagents/` folder holds subagent transcripts. Read only this workspace's folder. |
| MCP discovery through a Cursor `mcps/` folder | The MCP tools this session lists, including deferred ones found with `ToolSearch`. |

## Cursor-only features

Claude Code has no Cursor Automations, Bugbot, Cursor cloud agents, custom modes, `cursor-team-kit` (`deslop`, `control-cli`, `control-ui`), or built-in PR tool. When a step needs one, put one line in your reply, `Skipped in Claude Code: <step>. <reason>.`, then go on to the next step. Do not stop, ask, or retry. When a later step needs what the skipped step made, such as a URL or a key, leave a placeholder and name it in the line.

| Cursor | Claude Code |
| --- | --- |
| Cursor Automations: routines, `update_state` calls, `api2.cursor.sh/automations` webhooks, `SendToUser` secret requests | Skip with the line. |
| `/loop` or a routine wake | Claude Code's own `/loop`, or a scheduled task, when the session offers one. Otherwise skip with the line. |
| Bugbot | Bugbot comments on a GitHub PR are ordinary review threads, so triage them with the forge command that the step gives. Skip a step that starts, waits for, or configures Bugbot when the PR has no Bugbot check or comment. |
| Cursor cloud agents | `environment: "cloud"` maps to a worktree, as in Subagent fields. Skip a step that needs the cloud agent itself. |
| `/deslop` | Run the **unslop** and **no-comments** skills over the diff yourself. That is not a skip, so write no line. |
| `control-ui` | Claude in Chrome or another browser tool the session offers. Otherwise skip with the line. |
| `control-cli` | Drive the CLI with `Bash`. That is not a skip. |
| A built-in PR tool | Use the forge command that the step gives, such as `gh pr create`. That is not a skip, so write no line. |
| Custom mode, keep miracle-mode on across turns | The user calls `/mstack` again, or says "stay in miracle mode". Keep following it until they say stop. |

## Gaps the Cursor text leaves open

| Cursor assumption | Claude Code |
| --- | --- |
| The repo has a remote and a PR can open | With no remote, write `Skipped in Claude Code: Opening a PR. No remote.` and report the branch and commits instead. |
| The default branch is `main` | Use the repo's own default branch, from `git symbolic-ref refs/remotes/origin/HEAD`, or the current branch when there is no remote. |
| One investigator per evidence source (`why`, `how`) | Spawn one only for a source that can hold evidence about this symptom. A defect already located in a few lines of code needs no fan-out. Say which sources you left out and why. |
| Reproduce through `control-ui` or `control-cli` | For a library, a function, or a script, reproduce with a failing test or a `Bash` command. That is not a skip. |
| The **create-skill** skill (Cursor's built-in) | The **skill-creator** skill when the session offers it. Otherwise follow the Authoring a skill playbook on its own. |
