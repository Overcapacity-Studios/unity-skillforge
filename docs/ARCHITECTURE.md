# Architecture

Why this repo is shaped the way it is. Read this before changing its structure.

## The goal: token efficiency

Context is the scarce resource. Everything below follows from one rule: **an agent should load the
smallest amount of text that lets it do the task correctly.**

| Tier | What | When it loads | Budget |
| --- | --- | --- | --- |
| **0** | `AGENTS.md`, or the `unity-game-router` skill | Always | ≤ 150 lines |
| **1** | One `SKILL.md` | When the task matches its description | ≤ 200 lines |
| **2** | `references/`, `rules/`, `templates/`, the game's `design/` | Only by exact path, named in a skill | unbounded |

Skill **descriptions sit in context permanently**, for every skill installed. That is why they are
capped at 300 characters and written to say when the skill does *and does not* apply. Claude Code
drops descriptions from the listing once it exceeds about 1% of the context window, so with 33
skills the cap is load-bearing, not cosmetic.

`design/STATE.md` is capped at 60 lines for the same reason: it is read on every single task, making
it the most expensive file in a game project per token.

## Why skills are flat

The spec this repo was built from asked for `skills/core/`, `skills/2d/`, `skills/2_5d/`. That does
not work:

- Claude Code documents only `<skills-root>/<name>/SKILL.md`. Its plugin manifest defines a scan
  root as *"a directory of `<name>/SKILL.md` folders"* — direct children only.
- Recursion **is** documented for `agents/` and `commands/`, with explicit name-mangling rules. No
  such statement exists for `skills/`.
- Unity's own plugin CI requires frontmatter `name` to equal the **direct** folder name under
  `skills/`.
- Empirically, across every plugin installed on the machine this was built on, zero skills were
  nested.
- Codex documents `.agents/skills` without stating a scan depth, and its examples are flat too.

So grouping lives in the **name prefix** — `core-`, `2d-`, `25d-`, `3d-`, `assets-`, `qa-`,
`design-` — and in the routing table. Prefixes also keep our names from colliding with Unity's
official skills, since both packs are meant to be installed together.

A plugin *can* declare grouped directories with `"skills": ["./skills/core/", ...]` in
`plugin.json`, but that only helps the plugin install path, not a manual copy into `.claude/skills/`
or `.agents/skills/`. Flat works everywhere.

## Why frontmatter is restricted

Skill frontmatter is limited to `name`, `description` and `metadata`.

Claude Code accepts many more keys. But outside Claude Code — claude.ai uploads, the Skills API —
**only** `name`, `description`, `license`, `compatibility`, `metadata` and `allowed-tools` are
permitted, and *any other key is a hard error*. Codex requires exactly `name` and `description`.
Restricting to the intersection is what makes one tree load in both tools. The validator enforces it.

Two further rules come from the Claude Code plugin directory's scan: a description may not contain
angle brackets, and the root `README.md` must be at least 40 words.

## Two Tier-0 paths, one table

**Claude Code does not load a plugin's `AGENTS.md` or `CLAUDE.md`.** Its docs are explicit: *"To
include instructions in a plugin, write them as a skill."* So Tier 0 depends on how the pack was
installed:

| Install path | Tier 0 |
| --- | --- |
| `install.sh` into a game repo | `AGENTS.md`, loaded automatically (`CLAUDE.md` is just `@AGENTS.md`) |
| Claude Code plugin | the `unity-game-router` skill, invoked explicitly |

Both carry the same hard rules and the same routing table. `validate-skills.py` fails the build if
the two tables drift — the router's table is the full set minus itself, since a router does not
route to itself.

## Why `PACK/` and `.unity-skillforge/`

Skills cite Tier 2 files as `` `PACK/references/unity-cli.md` ``. `PACK/` resolves to:

- the repo root, when working on the pack itself;
- `.unity-skillforge/` in a game repo, created by `install.sh`.

Claude Code offers `${CLAUDE_SKILL_DIR}` and `${CLAUDE_PLUGIN_ROOT}` for this. **Codex documents no
equivalent.** A fixed, boring path is the only mechanism that works in both tools, so the installer
guarantees it and the validator checks every cited path exists.

## Why the Unity CLI, not MCP

Unity deprecated the in-Editor MCP server in `com.unity.ai.assistant`. Its replacement is the Unity
CLI plus the Pipeline package. Unity's own docs say `unity command` and `unity eval` are *"faster
and use fewer tokens than MCP"* and should be used by any agent that can run shell commands.

The CLI's **own** MCP mode (`unity mcp configure`) is not deprecated and remains the fallback for
agents that cannot shell out.

**Skills never hardcode an Editor tool name.** The registered tool set varies by Unity version and
by installed packages, so every Editor-touching skill starts with `unity status`, then `unity list`
and `unity commands --format json`, and uses only names it saw there. `references/unity-mcp-tools.md`
records the four names Unity's docs actually publish, explicitly labelled as the deprecated surface —
Unity never published a complete list, so claiming one would be fabrication.

## Why we duplicate some of Unity's skills

Unity's official plugin covers 13 of our topics. Rather than drop them, each overlapping skill:

1. states this project's conventions — folder layout, naming, version pins — which are genuinely
   ours;
2. carries a `## Prefer the official skill` section naming the `/unity:*` skill to defer to;
3. does **not** restate Unity's procedure.

That keeps the pack coherent standalone while avoiding a second, drifting copy of Unity's
documentation. The cost is real: those 13 need review whenever Unity updates theirs.

## Why subagents do not preload skills

Claude Code's subagent frontmatter has a `skills:` key, but it **injects full skill content**, not
just descriptions. Preloading five skills into six agents would defeat the entire tiering. Instead
each agent lists its allowed skills in its body and invokes them through the Skill tool, which is
available to subagents by default.

Agent frontmatter also has a trap: Claude Code **ignores an unrecognised agent field without
reporting an error**. A typo fails silently. The validator therefore allowlists agent keys, and
rejects `allowed-tools` — which is a *skill* key, not an agent key.

## Repository layout

```
AGENTS.md              Tier 0: hard rules + routing table (≤150 lines)
CLAUDE.md              only "@AGENTS.md"
skills/<name>/SKILL.md 33 skills, flat, prefix-grouped
agents/*.md            6 subagents (Claude Code; Codex uses docs/CODEX.md)
rules/                 Tier 2: C# style, architecture, folders, performance
references/            Tier 2: Unity CLI, versions, official skills, URP, input, Meshy, MCP
templates/csharp/      copy-ready .cs.txt
templates/game-design/ the design/ contract
scripts/               validate-skills.py, install.sh/.ps1, sync-agents-dir.sh, slice-spritesheet.py
.claude-plugin/        plugin.json + marketplace.json (repo is both)
.codex-plugin/         plugin.json
.agents/plugins/       marketplace.json (Codex)
docs/  examples/
```

The repo is simultaneously a marketplace and the single plugin it lists (`"source": "./"`), which is
supported and is what Unity's own plugin repo does. The marketplace entry deliberately omits a
`skills` key: listing one there would stop the default `skills/` directory being scanned.

## Skill file contract

Every `SKILL.md` has these sections, in this order, enforced by the validator:

**When to use · Inputs needed · Steps · Unity CLI commands used · Files to read (exact paths) ·
Done checklist · Common mistakes**

Plus `## Prefer the official skill` where the overlap rule applies. Steps are numbered and
imperative. Concrete code appears only where no template covers it — the rule is *copy a template,
run a script, and only then generate*.
