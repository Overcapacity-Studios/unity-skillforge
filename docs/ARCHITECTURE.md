# Architecture

Why this repo is shaped the way it is. Read this before changing its structure.

## The goal: token efficiency

Context is the scarce resource. Everything below follows from one rule: **an agent should load the
smallest amount of text that lets it do the task correctly.**

| Tier | What | When it loads | Budget |
| --- | --- | --- | --- |
| **0** | `AGENTS.md` | Automatically, every task — **on the `install.sh` path only** | ≤ 150 lines |
| **0** | the `unity-game-router` skill | On the plugin path, where `AGENTS.md` is not loaded: invoked explicitly, usually once per session | ≤ 200 lines (it is a skill) |
| **0** | `design/STATE.md` + `design/INDEX.md` | Every task, by rule — they live in the *game* repo, not the pack | STATE.md ≤ 60 lines |
| **1** | One `SKILL.md` | When the task matches its description | ≤ 200 lines |
| **2** | `references/`, `rules/`, `templates/`, the rest of `design/` | Only by exact path, named in a skill | unbounded |

The two Tier 0 rows for the pack are alternatives, not both: which one applies depends on how the
pack was installed. See "Two Tier-0 paths" below.

Skill **descriptions sit in context permanently**, for every skill installed. That is why they are
capped at 300 characters and written to say when the skill does *and does not* apply. Claude Code
drops descriptions from the listing once it exceeds about 1% of the context window, so with 33
skills the cap is load-bearing, not cosmetic.

`design/STATE.md` is capped at 60 lines for the same reason: it is read on every single task, making
it the most expensive file in a game project per token.

## Why skills are flat

The spec this repo was built from asked for `skills/core/`, `skills/2d/`, `skills/2_5d/`. That does
not work:

- Claude Code's plugin manifest defines a skills scan root as *"a directory of `<name>/SKILL.md`
  folders"* — direct children only.
- Recursion **is** documented for `agents/` and `commands/`, with explicit name-mangling rules
  (`agents/review/security.md` becomes `plugin:review:security`). No equivalent statement exists
  anywhere for `skills/`, and without a naming rule a nested skill has no addressable name.
- Codex documents `.agents/skills` being scanned in each directory from the working directory up to
  the repo root, with each skill as `<name>/SKILL.md` — again, direct children.

Note the one place nesting *is* supported, since it is easy to confuse: Claude Code loads
`<subdir>/.claude/skills/<name>/SKILL.md` for sessions started in or below `<subdir>`. That nests
the **skills root**, not the skills within it. `skills/core/unity-script/SKILL.md` is still
unaddressable.

So grouping lives in the **name prefix** — `core-`, `2d-`, `25d-`, `3d-`, `assets-`, `qa-`,
`design-` — and in the routing table. Prefixes also keep our names from colliding with Unity's
official skills, since both packs are meant to be installed together.

A plugin *can* declare grouped directories with `"skills": ["./skills/core/", ...]` in
`plugin.json`, but that only helps the plugin install path, not a manual copy into `.claude/skills/`
or `.agents/skills/`. Flat works everywhere.

## Why frontmatter is restricted

Skill frontmatter is limited to `name`, `description` and `metadata`.

Claude Code accepts many more keys. The portable set — the one the Agent Skills spec defines, and
all that is accepted outside Claude Code for claude.ai uploads and the Skills API — is `name`,
`description`, `license`, `compatibility`, `metadata` and `allowed-tools`. Anything beyond it risks
rejection there. Codex's docs say a `SKILL.md` **must include** `name` and `description`; that is a
minimum, not a maximum, which is why `metadata` is safe to add. Restricting to the portable set is
what makes one tree load in both tools, and the validator enforces it.

Two further rules are inherited from **Unity's own plugin CI**, which enforces them citing the
Claude Code plugin directory's submission scan: a description should avoid angle brackets, and the
root `README.md` should be at least 40 words. Anthropic's published docs say only that `<` and `>`
in a description are escaped for display, so treat the angle-bracket rule as defensive rather than
load-bearing — it costs nothing, and descriptions read better without them.

## Two Tier-0 paths, one table

**Claude Code does not load a plugin's `CLAUDE.md`.** Its docs are explicit: *"To include
instructions in a plugin, write them as a skill,"* and `claude plugin validate` warns about a
plugin-root `CLAUDE.md` by name. A plugin-root `AGENTS.md` is **not documented either way** — we
assume it is not loaded, because nothing says it is, and designing around the safer assumption costs
one skill. So Tier 0 depends on how the pack was installed:

| Install path | Tier 0 |
| --- | --- |
| `install.sh` into a game repo | `AGENTS.md`, loaded automatically (`CLAUDE.md` is just `@AGENTS.md`) |
| Claude Code plugin | the `unity-game-router` skill, invoked explicitly |

Both carry the same hard rules and the same routing table. `validate-skills.py` fails the build if
the two tables drift — the router's table is the full set minus itself, since a router does not
route to itself.

### An expected validator warning

`claude plugin validate . --strict` reports:

> `CLAUDE.md at the plugin root is not loaded as project context.`

That warning is **correct and expected**, and the design already answers it. `CLAUDE.md` exists for
the `install.sh` path, where the repo's rules are copied into a game repo and Claude Code loads them
as project context. On the plugin path it is inert, which is precisely why `unity-game-router`
carries the rules. Do not delete `CLAUDE.md` to silence the warning — that would break the
install.sh path, which is the one Codex users depend on.

## Why `PACK/` and `.unity-skillforge/`

Skills cite Tier 2 files as `` `PACK/references/unity-cli.md` ``. `PACK/` resolves to whichever
copy of the pack's files is present:

- `.unity-skillforge/` in a game repo, created by `install.sh`;
- the **plugin's own root directory**, when installed as a Claude Code or Codex plugin — the plugin
  ships `references/`, `rules/`, `templates/` and `scripts/` alongside `skills/`, so the same
  relative paths resolve there (`${CLAUDE_PLUGIN_ROOT}` names it on Claude Code);
- the repo root, when working on the pack itself.

Claude Code offers `${CLAUDE_SKILL_DIR}` and `${CLAUDE_PLUGIN_ROOT}` for this. **Codex documents no
equivalent.** A fixed, boring path is the only mechanism that works in both tools, so the installer
guarantees it and the validator checks every cited path exists.

## Why the Unity CLI, not MCP

Unity deprecated the in-Editor MCP server in `com.unity.ai.assistant`. Its replacement is the Unity
CLI plus the Pipeline package. Unity's migration page says direct Editor commands are *"faster and
use fewer tokens than MCP"* and should be used by any agent that can run shell commands. (That page
names them `unity command` and `unity eval`; the CLI command reference lists `unity command` but no
`unity eval`, and the attested mechanism for running C# is the Pipeline package's `script eval` /
`eval_file`. Unity's docs are inconsistent here — discover the real surface with `unity list`.)

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
each agent lists its allowed skills in prose in its body and invokes them through the `Skill` tool.
Note that every agent here sets an explicit `tools:` allowlist, and an allowlist replaces the
default set — so each one lists `Skill` explicitly. Dropping `Skill` from an agent's `tools:` would
silently stop it using any skill at all.

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
scripts/               validate-skills.py, install.sh/.ps1, uninstall.sh, sync-agents-dir.sh,
                       slice-spritesheet.py
.claude-plugin/        plugin.json + marketplace.json (repo is both)
.codex-plugin/         plugin.json
.agents/plugins/       marketplace.json (Codex)
docs/  examples/
```

The repo is simultaneously a marketplace and the single plugin it lists (`"source": "./"`), which is
supported and is what Unity's own plugin repo does. The marketplace entry deliberately omits a
`skills` key. For an entry whose `source` is the marketplace root — as ours is — listing specific
skills subdirectories there means **only those** load and the plugin's default `skills/` directory
is not scanned at all. A `skills` key in `plugin.json` behaves differently: it *adds to* the default
scan.

## Skill file contract

Every `SKILL.md` has these sections, in this order, enforced by the validator:

**When to use · Inputs needed · Steps · Unity CLI commands used · Files to read (exact paths) ·
Done checklist · Common mistakes**

All seven are checked for presence *and* order.

Plus `## Prefer the official skill` where the overlap rule applies. Steps are numbered and
imperative. Concrete code appears only where no template covers it — the rule is *copy a template,
run a script, and only then generate*.
