---
name: unity-skillforge-pack
description: Shared data for the unity-skillforge pack - the Unity rules, references and code templates every other unity-skillforge skill reads by path. Install it alongside them; it holds no procedure of its own and you never invoke it directly.
metadata:
  version: 0.1.0
---

# unity-skillforge shared data

**This is a data package, not a procedure.** It carries the files the other 36 unity-skillforge
skills refer to as `PACK/...`. You do not run it. If you are reading this because it matched a
request, the skill you actually want is **`unity-game-router`**, which will route you correctly.

## Why it exists

The rules, references and templates are shared: `references/unity-cli.md` alone is cited by 32 of
the skills. Keeping one copy here, rather than duplicating it into every skill, is what keeps the
pack at 70 KB instead of 700 KB and means a correction is made once.

It is shaped as a skill so that `npx skills add` carries it. That tool copies each skill's own
folder, so a shared tree at the repo root would never arrive — the other skills would install with
every `PACK/` path dangling.

## What `PACK/` resolves to

Whichever copy of these files is present, in this order:

| Install method | `PACK/` is |
| --- | --- |
| `scripts/install.sh` | `.unity-skillforge/` in the game repo |
| `npx skills add` | the sibling folder `unity-skillforge-pack/`, next to the other skills |
| Claude Code / Codex plugin | the plugin's own root |
| Working on the pack itself | `skills/unity-skillforge-pack/` |

So `PACK/rules/csharp-style.md` means `unity-skillforge-pack/rules/csharp-style.md` when the pack
was installed with `npx skills`, and `.unity-skillforge/rules/csharp-style.md` when it was installed
with `install.sh`. Look in whichever of those exists.

## What is in here

| Folder | Holds |
| --- | --- |
| `references/` | Unity CLI surface, version and package pins, the official-skill overlap map, URP settings, Input System conventions, Meshy MCP tool names, the deprecated Unity MCP surface |
| `rules/` | C# style, architecture and layering, folder conventions, performance budgets |
| `templates/csharp/` | MonoBehaviour, ScriptableObject, StateMachine, EventChannel, ServiceLocator, EditMode and PlayMode tests |
| `templates/game-design/` | The `design/` contract: STATE, INDEX, concept, pitch, decisions, mechanic, prototype, art bible, tech decisions |

Read a file only when a skill names it by exact path. These are Tier 2: never read speculatively,
and never read a whole folder.
