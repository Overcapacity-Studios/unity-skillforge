# unity-skillforge

Agent skills, subagents, rules and templates that help AI coding agents build **Unity games in 2D,
2.5D and 3D** — code, scenes and generated assets. One source of truth that loads natively in both
**Claude Code** and **OpenAI Codex**.

Targets **Unity 6.3 LTS (`6000.3.x`)**, URP and the new Input System. The Editor bridge is the
**Unity CLI** plus the Unity Pipeline package, because Unity has deprecated the in-Editor MCP server
in `com.unity.ai.assistant`.

> **This repo is *how* we build. Your game repo keeps a `design/` folder describing *what* you are
> building.** That split is the whole architecture: the pack is reusable, the design is per-game.

---

## What it actually does

You describe what you want in plain language. The agent picks the matching skill, follows its
procedure, writes C# and assets into your Unity project, drives the Editor through the Unity CLI to
compile and test, and reports what it observed.

A worked example, start to finish:

> **You:** "I want a 2D platformer where a courier delivers parcels across rooftops in a storm."
>
> The agent writes `design/pitch.md` and asks you two things it cannot guess — is this 2D, 2.5D or
> 3D, and what should the art look like. It then builds the bootstrap scene, wires the Input System,
> writes the movement spec with real numbers, implements it from the templates here, runs
> `unity recompile --strict` and the tests, enters Play Mode to check the player actually jumps the
> height the spec says, and records where things stand.

Both walkthroughs trace this in full:
[2D platformer](examples/2d-platformer-walkthrough.md) ·
[3D third-person](examples/3d-third-person-walkthrough.md). **If you read one thing after this
page, read a walkthrough** — it shows the real shape of the work.

What it will not do: it never invents a Unity command (it asks your Editor what exists first), never
claims a Play Mode result it did not observe, and never generates art before you have agreed a style.

## Quickstart

> **Note:** the `/plugin` commands below need this repo published and public on GitHub. Until then,
> use the local clone path — it is the fully supported route and the one Codex uses anyway.

**Step 1 — connect Unity.** Needed for every path, and free: no Unity AI subscription, no Unity
Cloud link.

```bash
curl -fsSL https://unity.com/install.sh | bash   # macOS/Linux. Windows: winget install Unity.CLI
unity --version && unity auth login
unity pipeline install     # with your project open in Unity 6.3 LTS or later
unity status               # should list your Editor. If it does, you are connected
```

The Unity CLI is currently **beta** (`1.0.0-beta.x`) and Unity labels it experimental;
`unity --help` is authoritative for your installed version.

**Step 2 — install the pack.** Choose by which agent you use:

```bash
# Works for Claude Code AND Codex, and loads the rules automatically. Recommended.
git clone https://github.com/Overcapacity-Studios/unity-skillforge.git
cd unity-skillforge
./scripts/install.sh /path/to/your/game        # --dry-run to preview first
```

<details>
<summary>Claude Code plugin instead (once the repo is published)</summary>

```
/plugin install unity-skillforge --marketplace Overcapacity-Studios/unity-skillforge
```

On Claude Code older than 2.1.275:
`/plugin marketplace add Overcapacity-Studios/unity-skillforge` then
`/plugin install unity-skillforge@unity-skillforge`.

The plugin ships the skills but **not** the always-on rules file, because Claude Code does not load
a plugin's `AGENTS.md`. Open each session with *"Use the unity-game-router skill"*, or run
`./scripts/install.sh` as well to get both.
</details>

**Step 3 — your first prompt.** Literally type this:

> **"Use the unity-game-router skill. I want to build \<describe your game in one sentence\>."**

It will ask whether the game is 2D, 2.5D or 3D, and create the `design/` folder it works from.

Uninstalling: `./scripts/uninstall.sh /path/to/your/game`. It removes only this pack's files and
never touches your `design/` folder or `Assets/`.

Full details, including an existing project and what to commit:
[docs/INSTALL.md](docs/INSTALL.md).

## Words this project uses

| Term | Means |
| --- | --- |
| **Skill** | One procedure in a `SKILL.md` file. Your agent loads it only when the task matches, so 33 skills cost almost nothing until used |
| **Subagent** | A role (designer, coder, QA...) with its own fresh context and a narrow remit |
| **Router** | The one skill to start with when you are unsure. It reads your project state and picks the others |
| **Dimension** | Whether your game is **2D, 2.5D or 3D**. Recorded once in `design/STATE.md`; it decides camera, renderer, physics and art cost |
| **`design/`** | A folder in *your game repo* holding what you are building — status, pitch, art style, one file per mechanic. The pack reads it; you own it |
| **Tier 0 / Tier 2** | Tier 0 is always loaded (the rules). Tier 2 is read only when a skill names the exact file. This is how the pack stays cheap in context |
| **`PACK/`** | How skills refer to their own files, wherever they are installed |
| **Unity CLI** | The `unity` command. How the agent drives your Editor — compile, test, build |
| **MCP** | A protocol some agents use to reach tools. **You almost certainly do not need it**: Claude Code and Codex run `unity` directly |

## What you get

**33 skills**, flat under `skills/`, grouped by prefix:

| Group | Skills | Covers |
| --- | --- | --- |
| `unity-game-router` | 1 | Classifies the task and project dimension, loads the minimum skill set |
| `design-*` | 4 | Pitch to design docs, mechanic specs, scope cuts, state updates |
| `core-*` | 7 | Scripts, ScriptableObject data, event channels, input, save, UI Toolkit, scenes |
| `2d-*` | 5 | Sprite import, tilemaps, 2D physics, sprite animation, 2D lighting |
| `25d-*` | 3 | Fixed-angle camera, billboard sprites, sorting and depth |
| `3d-*` | 4 | Character controller, Cinemachine, URP lighting, NavMesh AI |
| `assets-*` | 5 | Art style lock, 2D and 3D generation, import pipeline, audio |
| `qa-*` | 4 | Tests, play-mode verification, console errors, builds |

**6 subagents** in `agents/` — designer, architect, gameplay-coder, asset-producer, qa, reviewer —
each with a model hint, an exact read list and a fixed handoff format.

**Costs:** the pack itself is free, and so is the Unity CLI. The only paid dependency is optional —
`assets-gen-3d-model` uses Meshy, which needs a **paid Meshy Pro or higher** plan and spends credits
per generation. Everything else, including all 2D and QA work, costs nothing beyond your agent.
See [docs/ASSETS.md](docs/ASSETS.md).

**Rules and templates** read by path only: `rules/` (C# style, architecture, folders, performance),
`templates/csharp/` (MonoBehaviour, ScriptableObject, StateMachine, EventChannel, ServiceLocator,
Edit/PlayMode tests), `templates/game-design/` (the `design/` folder contract).

## Feature matrix

| | 2D | 2.5D | 3D |
| --- | :---: | :---: | :---: |
| Camera | orthographic, 2D Renderer | **fixed-angle ortho / narrow perspective** | Cinemachine 3.x |
| Renderer | 2D Renderer | Universal | Universal |
| Lighting | `Light2D`, normal maps, shadow casters | URP, baked GI, probes | URP, baked GI, Adaptive Probe Volumes |
| Physics | both Unity 6 2D systems, detected not guessed | 3D | 3D |
| Draw order | sorting layers | **transparency sort axis, isometric Z-as-Y** | depth buffer |
| Characters | sprite animation | **upright billboards, depth-writing** | character controller |
| Levels | tilemaps | tilemaps + 3D geometry | NavMesh |

Bold entries are the ones no other Unity agent pack covers.

## Supported agents

| Agent | How it loads | Notes |
| --- | --- | --- |
| **Claude Code** | Plugin, or `.claude/skills/` + `.claude/agents/` | Subagents supported |
| **OpenAI Codex** | `.agents/skills/` + root `AGENTS.md` | No subagent directory; `docs/CODEX.md` ships the six roles as prompts |

Skill frontmatter is restricted to `name`, `description` and `metadata`, so a skill stays valid
outside Claude Code too, where any other key is a hard error.

## Use it with Unity's official plugin

Unity ships [`Unity-Technologies/unity-agent-plugin`](https://github.com/Unity-Technologies/unity-agent-plugin)
(36 skills). **Install both** — this pack is built to complement it, not replace it:

```
/plugin marketplace add Unity-Technologies/unity-agent-plugin
/plugin install unity@unity-agent-plugin
```

Where topics overlap, our skill contributes this project's conventions and defers to the `/unity:*`
skill by name rather than restating its procedure. The full map is in
[references/official-unity-skills.md](references/official-unity-skills.md), which also lists other
complementary packs worth installing.

## Already have a Unity project?

That is the expected case. The installer never overwrites your `AGENTS.md`, `CLAUDE.md`, `design/`
folder or anything under `Assets/`.

Two rules here are strict, and worth knowing before you start: this pack targets **URP** and the
**new Input System**, and treats Built-in RP and legacy `UnityEngine.Input` as unsupported. That
applies to *new* code the agent writes — it will not go and refactor your existing project unless
you ask it to. If your project is Built-in RP today, Unity's own `/unity:migrate-birp-to-urp` skill
owns that migration. See [docs/INSTALL.md](docs/INSTALL.md#already-have-a-unity-project).

## Documentation

| Doc | Read it for |
| --- | --- |
| [docs/INSTALL.md](docs/INSTALL.md) | Prerequisites, both install paths, connecting Unity, verifying it works |
| [docs/USAGE.md](docs/USAGE.md) | Example prompts per workflow, and the `design/` contract |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | The token tiers, why skills are flat, how routing works |
| [docs/CODEX.md](docs/CODEX.md) | Codex setup, which GPT model to use for which role, AGENTS.md behaviour |
| [docs/ASSETS.md](docs/ASSETS.md) | Asset providers, licensing and commercial-use caveats |
| [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) | Unity not connecting, skills not triggering, version mismatches |
| [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md) | Adding a skill, and the checks it must pass |
| [examples/](examples/) | Full 2D platformer and 3D third-person walkthroughs |

## Project status

Version 0.1.0. Every skill, rule and reference here was written against Unity's current published
documentation. `scripts/validate-skills.py` enforces the structural rules and runs in CI
(`.github/workflows/validate.yml`) alongside shellcheck, manifest checks and an end-to-end
install/uninstall test.

**Nothing in this repo has been executed against a running Unity Editor**, so every `unity` command,
import setting and Play Mode check is documented from Unity's own docs, not observed. The Unity CLI
is beta and `unity --help` is authoritative for your version. See [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) if a
command behaves differently on your install, and `unity --help` is authoritative for your version.

MIT licensed. Unity's own skills are under the Unity Companion License and are linked, never
vendored.
