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
> The agent develops the idea with you first — what the player actually does, what the loop is, what
> it would cost solo — and challenges the parts that do not hold, instead of handing you a design
> document full of decisions you never made. Once you agree, it writes `design/pitch.md`, asks the
> two things it cannot guess (2D, 2.5D or 3D, and what the art should look like), builds the
> bootstrap scene, wires the Input System, writes the movement spec with real numbers, implements it
> from the templates here, runs `unity recompile --strict` and the tests, enters Play Mode to check
> the player actually jumps the height the spec says, and records where things stand.

It also knows when **not** to do that: a bug fix is a bug fix, and gets routed straight to the QA
skill with no design process attached.

Both walkthroughs trace this in full:
[2D platformer](examples/2d-platformer-walkthrough.md) ·
[3D third-person](examples/3d-third-person-walkthrough.md). **If you read one thing after this
page, read a walkthrough** — it shows the real shape of the work.

What it will not do: it never invents a Unity command (it asks your Editor what exists first), never
claims a Play Mode result it did not observe, never invents a playtest result no human gave it, and
never generates production art before you have agreed a style.

## The workflow, end to end

```
Idea → Discovery → Director review → Game design → Prototype plan
     → Prototype → Playtest → Production → QA → Release
```

| Stage | What runs | What you get |
| --- | --- | --- |
| **Idea** | you, in one sentence | — |
| **Discovery** | `design-idea-discovery` | `design/concept.md`: fantasy, verbs, loop hypothesis, pillars, risks. Needs no Unity project |
| **Director review** | the `game-director` agent | Options with tradeoffs, conflicts with what you already approved, a recommendation |
| **Game design** | `design-write-gdd`, `design-decision-log` | `pitch.md`, `STATE.md`, `INDEX.md`, `decisions.md` |
| **Prototype plan** | `design-prototype-plan` | The smallest playable test of your riskiest assumption, with agreed success and reject criteria |
| **Prototype** | `core-*` and the dimension skills, on `PH_` placeholders | Something playable. No art style needed yet |
| **Playtest** | you, playing it | Observations written into `design/prototype-*.md`. **Agents never fill this in** |
| **Production** | `design-mechanic-spec` → `core-*` / `2d-*` / `25d-*` / `3d-*` → `assets-*` | The real mechanic, with real art against a locked art bible |
| **QA** | `qa-run-tests`, `qa-playmode-check`, `qa-fix-console-errors` | Observed results against the spec's acceptance checks |
| **Release** | `qa-build` | A build that was launched, not just compiled |

You do not have to start at the top. An existing project resumes from the `Stage` field in
`design/STATE.md`, and nothing already decided gets re-opened.

## Who does what

Seven roles, in `agents/`. You rarely need more than one or two for a task.

| Role | Owns | Call it when |
| --- | --- | --- |
| **game-director** | The vision, the pillars, cross-system coherence, scope | Before committing to a significant mechanic, or when you want an idea challenged |
| **designer** | `design/` — concept, pitch, mechanic specs, prototype plans | Anything needs specifying before it is built |
| **architect** | Layers, assemblies, packages, `tech-decisions.md` | A feature spans systems, or a package choice is in play |
| **gameplay-coder** | C#, data assets, scene wiring | A spec exists and needs implementing |
| **asset-producer** | Art and audio, generation and import | Assets are needed, and the style is locked |
| **qa** | Compile, tests, play-mode verification | After any implementation, before any build |
| **reviewer** | Accepting or rejecting a change | Before you commit |

The director and the designer are different jobs: the designer writes what a mechanic does, the
director judges whether the game should have it. **You are the final creative authority** — the
director recommends, and records nothing as approved that you did not approve.

### Two examples

**A brand-new game, from a rough idea.**

> "I have a rough idea — a game about repairing lighthouses. Help me develop it."

Discovery asks what you actually *do* second to second, offers two or three concrete loop options
with their tradeoffs, challenges the parts that contradict each other, and writes
`design/concept.md` with every line marked confirmed or assumed. Nothing is built, no Unity project
is needed. When you agree, `design-write-gdd` turns it into the pitch, and
`design-prototype-plan` plans the smallest thing that tests whether repairing is fun — on capsules
and cubes, before any art decision.

**An existing game, new mechanic.**

> "I want to add a grappling hook."

The `game-director` reads your pillars, your core loop and `design/decisions.md`, says what the
grapple would do to the mechanics you already have, flags that it contradicts the "no vertical
traversal" decision you approved in week two, and gives you options with costs. You decide.
`design-mechanic-spec` then writes the numbers, the implementing skills build it, and
`qa-playmode-check` verifies it against the acceptance checks.

## Quickstart

**Step 1 — connect Unity.** Needed for every path, and free: no Unity AI subscription, no Unity
Cloud link.

You need an existing Unity project — this pack works on one, it does not create one. If you have
none, make a **Universal 3D** or **Universal 2D** project on Unity 6.3 LTS in Unity Hub first; that
gives you URP. ([details](docs/INSTALL.md#0-if-you-do-not-have-a-unity-project-yet))

```bash
curl -fsSL https://unity.com/install.sh | bash   # macOS/Linux. Windows: winget install Unity.CLI
unity --version && unity auth login
unity pipeline install     # with your project open in Unity 6.3 LTS or later
unity status               # should list your Editor. If it does, you are connected
```

The Unity CLI is currently **beta** (`1.0.0-beta.x`) and Unity labels it experimental;
`unity --help` is authoritative for your installed version.

**Step 2 — install the pack.** Three routes. Pick by what you want:

| | `npx skills` | Installer | Claude Code plugin |
| --- | --- | --- | --- |
| Agents supported | Claude Code, Codex, ~70 more | Claude Code, Codex | Claude Code |
| Take just one skill | **yes** | no | no |
| Always-on rules (`AGENTS.md`) | no | **yes** | no |
| The 7 subagents | no | **yes** | yes |
| Creates `design/STATE.md` | no | **yes** | no |
| Update later | `npx skills update` | re-run it | `/plugin marketplace update` |

### `npx skills` — quickest, and the only way to cherry-pick

```bash
# Everything, into this project
npx skills add Overcapacity-Studios/unity-skillforge --all

# See what is in it before installing anything
npx skills add Overcapacity-Studios/unity-skillforge -l

# A few skills, for one agent
npx skills add Overcapacity-Studios/unity-skillforge \
  -s unity-skillforge-pack -s unity-game-router -s 25d-sorting-and-depth \
  -a claude-code

# Globally (user-level) instead of per-project
npx skills add Overcapacity-Studios/unity-skillforge --all -g -a claude-code
```

> **Always include `unity-skillforge-pack`, or use `--all`.**
> The CLI copies each skill's own folder and nothing else, and that package is how the shared
> rules, references and templates travel. Leave it out and every `PACK/...` path in the other
> skills points at nothing — the skills load, but the files they tell the agent to read are
> missing.

Notes that save a retry:

- **Repeat `-s` and `-a`.** `-a claude-code,codex` is rejected; `-a claude-code -a codex` works.
- Installs to `.claude/skills/` and `.agents/skills/`, and writes `skills-lock.json`.
- `--copy` copies instead of symlinking. `-y` skips prompts. `--json` for scripting.
- Later: `npx skills list`, `npx skills update`, `npx skills remove`.

Afterwards, open each session with *"Use the unity-game-router skill"* — it carries the hard rules
that this route does not install, and it creates `design/` on its first run.

### Installer — the full pack, rules included

```bash
# macOS / Linux. Skip the clone if you already have this folder.
git clone https://github.com/Overcapacity-Studios/unity-skillforge.git
cd unity-skillforge
./scripts/install.sh /path/to/your/game        # --dry-run to preview first
```

```powershell
# Windows PowerShell, from the same folder. Switch syntax: -DryRun, not --dry-run.
.\scripts\install.ps1 C:\dev\MyGame
```

This is the only route that also writes `AGENTS.md` (loaded automatically every task), the seven
subagents, and the `design/` contract. It never overwrites an existing `AGENTS.md`, `CLAUDE.md`,
`design/` file or anything in `Assets/`, and re-running it is safe.

### Claude Code plugin

```
/plugin install unity-skillforge --marketplace Overcapacity-Studios/unity-skillforge
```

<details>
<summary>On Claude Code older than 2.1.275</summary>

```
/plugin marketplace add Overcapacity-Studios/unity-skillforge
/plugin install unity-skillforge@unity-skillforge
```
</details>

Ships the skills and subagents but not the always-on rules, since Claude Code does not load a
plugin's `AGENTS.md`. Open each session with *"Use the unity-game-router skill"*.

Running more than one route is fine — use the plugin or `npx` for the skills and the installer for
the rules, if you want both.

**Step 3 — your first prompt.** Pick the one that matches where you are:

> **"Use the unity-game-router skill. I have a rough idea: \<one sentence\>. Help me develop it."**
> — starts a design conversation, writes `design/concept.md`, builds nothing yet.

> **"Use the unity-game-router skill. I want to build \<describe your game in one sentence\>."**
> — for a concept you have already settled. It asks whether the game is 2D, 2.5D or 3D and creates
> the `design/` folder it works from.

Uninstalling: `./scripts/uninstall.sh /path/to/your/game`. It removes only this pack's files and
never touches your `design/` folder or `Assets/`.

Full details, including an existing project and what to commit:
[docs/INSTALL.md](docs/INSTALL.md).

## Words this project uses

| Term | Means |
| --- | --- |
| **Skill** | One procedure in a `SKILL.md` file. Your agent loads it only when the task matches, so 36 skills cost almost nothing until used |
| **Subagent** | A role (designer, coder, QA...) with its own fresh context and a narrow remit |
| **Router** | The one skill to start with when you are unsure. It reads your project state and picks the others |
| **Dimension** | Whether your game is **2D, 2.5D or 3D**. Recorded once in `design/STATE.md`; it decides camera, renderer, physics and art cost |
| **`design/`** | A folder in *your game repo* holding what you are building — status, concept, pitch, approved decisions, art style, one file per mechanic and prototype. The pack reads it; you own it |
| **Stage** | Where the project is: `concept`, `prototype`, `production`, `polish`, `shipped`. Recorded in `design/STATE.md` so an existing project resumes instead of restarting |
| **Tier 0 / 1 / 2** | How the pack rations your context. Tier 0 (`AGENTS.md`) is always loaded; Tier 1 is a skill, loaded only when the task matches; Tier 2 (`references/`, `templates/`) is read only when a skill names the exact file |
| **`PACK/`** | How a skill refers to the pack's own files. In your game repo it means the `.unity-skillforge/` folder the installer creates |
| **Unity CLI** | The `unity` command. How the agent drives your Editor — compile, test, build |
| **MCP** | A protocol some agents use to reach tools. **You almost certainly do not need it**: Claude Code and Codex run `unity` directly |

## What you get

**36 skills**, flat under `skills/`, grouped by prefix:

| Group | Skills | Covers |
| --- | --- | --- |
| `unity-game-router` | 1 | Classifies the task and project dimension, loads the minimum skill set |
| `design-*` | 7 | Idea discovery, pitch to design docs, mechanic specs, prototype plans, decision log, scope cuts, state updates |
| `core-*` | 7 | Scripts, ScriptableObject data, event channels, input, save, UI Toolkit, scenes |
| `2d-*` | 5 | Sprite import, tilemaps, 2D physics, sprite animation, 2D lighting |
| `25d-*` | 3 | Fixed-angle camera, billboard sprites, sorting and depth |
| `3d-*` | 4 | Character controller, Cinemachine, URP lighting, NavMesh AI |
| `assets-*` | 5 | Art style lock, 2D and 3D generation, import pipeline, audio |
| `qa-*` | 4 | Tests, play-mode verification, console errors, builds |

**7 subagents** in `agents/` — game-director, designer, architect, gameplay-coder, asset-producer,
qa, reviewer — each with a model hint, an exact read list and a fixed handoff format.

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
| **OpenAI Codex** | `.agents/skills/` + root `AGENTS.md` | No subagent directory; `docs/CODEX.md` ships the seven roles as prompts |

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
[references/official-unity-skills.md](skills/unity-skillforge-pack/references/official-unity-skills.md), which also lists other
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
| [examples/idea-to-prototype-walkthrough.md](examples/idea-to-prototype-walkthrough.md) | A rough idea to a played prototype, and a new mechanic on an existing game |
| [examples/](examples/) | Full 2D platformer and 3D third-person walkthroughs |

## Project status

Version 0.2.0. Every skill, rule and reference here was written against Unity's current published
documentation. `scripts/validate-skills.py` enforces the structural rules and runs in CI
(`.github/workflows/validate.yml`) alongside shellcheck, manifest checks and an end-to-end
install/uninstall test.

**Nothing in this repo has been executed against a running Unity Editor**, so every `unity` command,
import setting and Play Mode check is documented from Unity's own docs, not observed. The workflow
tests in `scripts/test-workflows.py` are static checks on the pack's own routing contracts — they
prove the pack says the right thing, not that an Editor behaved a certain way. The Unity CLI
is beta, so `unity --help` is authoritative for your version. See
[docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) if a command behaves differently on your install.

MIT licensed. Unity's own skills are under the Unity Companion License and are linked, never
vendored.
