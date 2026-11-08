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

## 60-second quickstart

**Claude Code** — install as a plugin:

```
/plugin install unity-skillforge --marketplace Overcapacity-Studios/unity-skillforge
```

<details>
<summary>On Claude Code older than 2.1.275, or to pin a version</summary>

```
/plugin marketplace add Overcapacity-Studios/unity-skillforge
/plugin install unity-skillforge@unity-skillforge
```
</details>

**Codex, or a shared tree for both tools** — clone and run the installer against your game repo:

```bash
git clone https://github.com/Overcapacity-Studios/unity-skillforge.git
cd unity-skillforge
./scripts/install.sh /path/to/your/game        # --dry-run to preview, --symlink to link
```

**Connect Unity** (needed either way, and free — no Unity AI subscription):

```bash
curl -fsSL https://unity.com/install.sh | bash   # macOS/Linux; or: winget install Unity.CLI
unity --version && unity auth login
unity pipeline install     # with your project open in Unity 6.3 LTS or later
unity status               # should list your Editor
```

Then ask your agent: **"Use the unity-game-router skill"**, or just describe what you want to build.

Full details in [docs/INSTALL.md](docs/INSTALL.md).

---

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

## Documentation

| Doc | Read it for |
| --- | --- |
| [docs/INSTALL.md](docs/INSTALL.md) | Prerequisites, both install paths, connecting Unity, verifying it works |
| [docs/USAGE.md](docs/USAGE.md) | Example prompts per workflow, and the `design/` contract |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | The token tiers, why skills are flat, how routing works |
| [docs/CODEX.md](docs/CODEX.md) | Codex setup, Sol vs Terra, AGENTS.md behaviour |
| [docs/ASSETS.md](docs/ASSETS.md) | Asset providers, licensing and commercial-use caveats |
| [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) | Unity not connecting, skills not triggering, version mismatches |
| [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md) | Adding a skill, and the checks it must pass |
| [examples/](examples/) | Full 2D platformer and 3D third-person walkthroughs |

## Project status

Version 0.1.0. Every skill, rule and reference here was written against Unity's current published
documentation, and `scripts/validate-skills.py` enforces the structural rules on every change.
**Nothing in this repo has been executed against a running Unity Editor**, so the Editor-driving
steps are documented, not verified. See [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) if a
command behaves differently on your install, and `unity --help` is authoritative for your version.

MIT licensed. Unity's own skills are under the Unity Companion License and are linked, never
vendored.
