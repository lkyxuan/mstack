# mstack in claude.ai

mstack is a fork of pstack, which was written for Cursor. Its skills still use Cursor names. In claude.ai, read this file once per session, then map each Cursor name with the tables below. If a Cursor field has no row, drop it and say so. Never pass a field or value the tool schema rejects.

`<mstack>` means the folder that holds this skill's top-level `SKILL.md`, `skills/` and `docs/`. The Skill tool prints it as the skill's base directory when `mstack` loads. Use that absolute path in every brief.

claude.ai accepts only one `SKILL.md` per skill, so each bundled skill keeps its instructions in `<mstack>/skills/<name>/INSTRUCTIONS.md`. Where any text says a bundled skill's `SKILL.md`, read its `INSTRUCTIONS.md`. A `SKILL.md` you write for the user's own project is still named `SKILL.md`.

## Tools

| Cursor | claude.ai |
| --- | --- |
| `Task` | `Agent`. If this chat has no `Agent` tool, do the subagent's job yourself, one role at a time, and say so once. A panel run this way is not independent, so label its agreement as weaker evidence. |
| `AskQuestion` | `AskUserQuestion`. If it is absent, ask in plain text. |
| Open a todolist | `TaskCreate` and `TaskUpdate` when the chat offers them. Otherwise keep the list in your reply and update it at each phase. |
| Run another mstack skill (`/name` or "the **name** skill") | `Read` `<mstack>/skills/<name>/INSTRUCTIONS.md` and follow it. Only `mstack` is installed as a claude.ai skill, so the `Skill` tool cannot find the others. When you tell the user how to call one, write "`/mstack <name>`", such as "`/mstack how does the auth flow work`". Where a skill tells the user to type `/miracle-mode`, write `/mstack`. |
| `Grep`, `Glob` | The same tools when present. Otherwise `Bash` with `rg`. |
| Cursor's built-in `babysit` skill | Not present. The Babysit playbook is the only one. |

## Subagent fields

| Cursor | claude.ai |
| --- | --- |
| `subagent_type: generalPurpose` | `subagent_type: "general-purpose"` |
| `miracle-agent`, `comment-sicko` | No custom agent types are registered in claude.ai. Use `subagent_type: "general-purpose"` and open the brief with "Read `<mstack>/agents/<name>.md` in full and act as that agent." For `miracle-agent`, also give the absolute path of `<mstack>/skills/miracle-mode/INSTRUCTIONS.md`. |
| `readonly: true` | `subagent_type: "Explore"`. It keeps `Bash`, so the brief also says "do not edit files", and you check `git status` afterward. |
| `readonly: false` | `general-purpose`. It keeps the chat's MCP servers. |
| `environment: "cloud"` | `isolation: "worktree"` when the work is in a git repo. Name the branch or commit the worker checks out. Outside a repo, omit it. |
| `environment: "local"` | Omit. |
| `cloud_base_branch: <b>` | Tell the worker to check out `<b>` first. |
| `run_in_background: true` | Omit. Subagents run in the background by default and notify you when they finish. |
| `resume` | Spawn a new agent and paste the earlier result into its brief. Use `SendMessage` only in the strict cases miracle-mode's Subagents section allows. |
| `file_attachments` | List the absolute paths in the brief. |

## Models

mstack runs every role on Opus. Pass `model: "opus"` on every `Agent` call. The `Agent` tool takes no effort setting.

The table below is the role table. Wherever a skill reads a line from the `mstack-models.mdc` rule, `~/.cursor/rules/mstack-models.mdc`, or `~/.claude/rules/mstack-models.md`, use the matching line here instead. A role missing from the table also runs on `opus`.

```
# mstack model configuration for claude.ai. Every role on Opus.
feature, refactoring: opus
bug-fix: opus
perf-issue: opus
hillclimb: opus
judgment and prose: opus
hardest tasks: opus
how explorer: opus
how explainer: opus
why investigators: opus
why synthesizer: opus
reflect tooling: opus
reflect judgment, divergent, synthesizer: opus
arena runners: opus, opus
arena cross-judge pool: opus
swarm workers: opus
architect runners: opus, opus
interrogate reviewers: opus, opus
```

| Cursor | claude.ai |
| --- | --- |
| Any model slug, Claude or not (`claude-opus-*`, `grok-*`, `gpt-*`, `composer-*`) | `model: "opus"` |
| `auto` or `inherit-parent` | `model: "opus"` |
| Raise or lower the reasoning effort, or switch to fast mode | Not available. Keep `opus` and say nothing. |
| A panel of different models (`arena`, `architect`, `interrogate`) | One `opus` agent per seat, each with a fresh brief and no view of the others. Agreement between them is weaker evidence than agreement across model families, so say "same-model panel" when you report it. |
| A judge or reviewer that must come from a family other than the parent's | Use a fresh `opus` agent that never saw the candidates being made, and say the judge shares the parent's model. |
| Codex or another outside model for verification | Not reachable from claude.ai. Verify with `opus`. The user may run Codex on the result themselves. |

## setup-mstack

claude.ai has no always-applied rules folder, so `setup-mstack` cannot write a rule file. Follow its steps with these changes:

- Detect. Skip it. Every role runs on `opus`.
- Budget. Skip it. There is no effort field to set.
- Write. Show the final role table to the user. It applies to the rest of this conversation. To make it permanent, the table in `<mstack>/docs/harness/claude-ai.md` has to change and the skill has to be saved again. Offer to produce the updated `.skill` file.
- Steps 7 and 8 work as written.

## Paths

| Cursor | claude.ai |
| --- | --- |
| `.cursor/skills/`, `~/.cursor/skills/` | `.claude/skills/` inside the repo you are working in. claude.ai's own skills are installed by the user, not written to disk. |
| `~/.cursor/plugins/`, `.cursor-plugin/plugin.json` | `<mstack>`. There is no plugin manifest. |
| `.cursor/rules/*.mdc`, always-applied rules | The repo's `CLAUDE.md`, or `AGENTS.md` when no `CLAUDE.md` exists. The model rule is the exception. See Models. |
| `https://github.com/cursor/plugins/blob/main/pstack/<path>` | `<mstack>/<path>` when that file exists. Read the local copy and never fetch it. Give the user the URL when they need a link to the upstream original. |
| Transcripts in `~/.cursor/projects/<slug>/agent-transcripts/` | Not on disk. Search past chats with `conversation_search` or `recent_chats` when the chat offers them. Otherwise ask the user for the branch, PR, or a pasted summary. |

## The workspace

The work happens in a cloud Linux sandbox, not on the user's machine. Bring a repo in with the `add_repo` tool when the chat offers it, or with `gh repo clone`. Its network goes through an allowlist. If a fetch is refused, say so and ask the user to attach the file. Do not retry with another command.

When the chat is linked to the user's computer, its files are reached with the `mcp__remote-devices__*` tools. Bring files into the sandbox for any step that needs processing.

## Cursor-only features

claude.ai has no Cursor Automations, Bugbot, Cursor cloud agents, `/loop`, custom modes, `cursor-team-kit` (`deslop`, `control-cli`, `control-ui`), or built-in PR tool. When a step needs one, put one line in your reply, `Skipped in claude.ai: <step>. <reason>.`, then go on to the next step. Do not stop, ask, or retry. When a later step needs what the skipped step made, such as a URL or a key, leave a placeholder and name it in the line.

| Cursor | claude.ai |
| --- | --- |
| Cursor Automations: routines, `update_state` calls, `api2.cursor.sh/automations` webhooks, `SendToUser` secret requests | Skip with the line. |
| A routine wake, or `/loop` to keep working later | A scheduled task (`send_later` to come back to this chat, `create_trigger` for a recurring run) when the chat offers one. Otherwise skip with the line. |
| Bugbot | Bugbot comments on a GitHub PR are ordinary review threads, so triage them with the forge command that the step gives. Skip a step that starts, waits for, or configures Bugbot when the PR has no Bugbot check or comment. |
| Cursor cloud agents | `environment: "cloud"` maps to a worktree, as in Subagent fields. Skip a step that needs the cloud agent itself. |
| `/deslop` | Run the **unslop** and **no-comments** skills over the diff yourself. That is not a skip, so write no line. |
| `control-ui` | The built-in browser or Claude in Chrome when the chat offers one, loaded by its own skill. Otherwise skip with the line. |
| `control-cli` | Drive the CLI with `Bash` in the sandbox. That is not a skip. |
| A built-in PR tool | Use the forge command that the step gives, such as `gh pr create`. That is not a skip, so write no line. |
| Custom mode, keep miracle-mode on across turns | The user calls `/mstack` again, or says "stay in miracle mode". Keep following it until they say stop. |

## Gaps the Cursor text leaves open

| Cursor assumption | claude.ai |
| --- | --- |
| The repo has a remote and a PR can open | With no remote, write `Skipped in claude.ai: Opening a PR. No remote.` and report the branch and commits instead. |
| The default branch is `main` | Use the repo's own default branch, from `git symbolic-ref refs/remotes/origin/HEAD`, or the current branch when there is no remote. |
| MCP discovery through a Cursor `mcps/` folder | The MCP tools this chat lists, including deferred ones found with `ToolSearch`. |
| One investigator per evidence source (`why`, `how`) | Spawn one only for a source that can hold evidence about this symptom. A defect already located in a few lines of code needs no fan-out. Say which sources you left out and why. |
| Reproduce through `control-ui` or `control-cli` | For a library, a function, or a script, reproduce with a failing test or a `Bash` command. That is not a skip. |
| The **create-skill** skill (Cursor's built-in) | The **skill-creator** skill when the chat offers it. Otherwise follow the Authoring a skill playbook on its own. |
| A fresh reviewer such as `comment-sicko` | With no `Agent` tool, review your own diff against that agent's file and say the review was not independent. |
| The playbook's todolist copied verbatim | With `TaskCreate`, copy it verbatim. Without it, keep the list in your working notes and put only the final state in the reply. |
