# Getting started — a new game, idea to tested build

For a teammate who has this pack and wants to start a new game with it. Work top to bottom once;
after that you only ever re-enter at the phase you are in.

**The split that explains everything else:** this pack is *how* we build. Your game repo's `design/`
folder is *what* you are building. The pack is reusable across games; `design/` is per-game.

Deeper references, when you need them: [INSTALL.md](INSTALL.md) for setup detail,
[USAGE.md](USAGE.md) for the prompt-per-workflow list, [ARCHITECTURE.md](ARCHITECTURE.md) for why it
is tiered this way.

---

## Phase 0 — one-time setup

Order matters. Unity first, then the CLI bridge, then the pack.

### 1. A Unity project

The pack works on an existing project; **it does not create one.**

Unity Hub → New project → **Universal 2D** or **Universal 3D** template on **Unity 6.3 LTS
(`6000.3.x`)** or later. That template gives you URP already configured.

Then Project Settings → Player → **Active Input Handling** → **Input System Package (New)**. It asks
to restart; let it.

> Already have a project? That is the expected case. Two strict rules: **URP only** (Built-in RP is
> unsupported — Unity's own `/unity:migrate-birp-to-urp` owns that migration) and **new Input System
> only** (`Input.GetKey` / `Input.GetAxis` are banned by `rules/csharp-style.md`). Both govern *new*
> code the agent writes; it will not refactor your existing scripts unless you ask.

### 2. The Unity CLI

The Editor bridge is the **Unity CLI**, not the in-Editor MCP server — Unity deprecated that.

```bash
curl -fsSL https://unity.com/install.sh | bash     # macOS / Linux
brew install --cask unity-cli                      # macOS alternative
winget install Unity.CLI                           # Windows

unity --version
unity auth login          # opens a browser; the session is stored
unity auth status
```

No Unity AI subscription is needed. The CLI is beta, so `unity <command> --help` is more
authoritative than any document, including this one.

### 3. Let the CLI drive your Editor

**Open the Unity project first**, then:

```bash
unity pipeline install     # installs com.unity.pipeline; wait for the Editor to recompile
unity pipeline list        # expect "Pipeline: Installed"
unity status               # must list your Editor: port, project path, version, PID
```

`unity status` listing your Editor is the real test. If it does not,
[TROUBLESHOOTING.md](TROUBLESHOOTING.md). The Pipeline package exposes a **localhost-only** HTTP
API; nothing is exposed to the network.

### 4. Install the pack into the game repo

```bash
git clone https://github.com/Overcapacity-Studios/unity-skillforge.git   # or use your existing clone
cd unity-skillforge
./scripts/install.sh /path/to/your/game --dry-run   # preview, changes nothing
./scripts/install.sh /path/to/your/game
```

Windows: `.\scripts\install.ps1 C:\dev\MyGame` (PowerShell switches: `-DryRun`, `-Symlink`).
Add `--symlink` if you want the game repo to track edits you make to your pack clone.

This writes:

```
your-game/
  .claude/skills/   .claude/agents/     # Claude Code
  .agents/skills/                       # Codex
  .unity-skillforge/                    # rules, templates, references, scripts, the 7 role files
  AGENTS.md                             # Tier 0 rules — appended to, never overwritten
  CLAUDE.md                             # contains only @AGENTS.md
  design/STATE.md  design/INDEX.md      # created only if absent; yours are never overwritten
```

Re-running it is safe and idempotent. This installer path is the recommended one: it is the only
route that **auto-loads the rules** via `AGENTS.md` and creates the `design/` contract. If you
instead install as a plugin or via `npx skills`, the rules do not load automatically — open every
session with **"Use the unity-game-router skill"**, which carries the same rules and routing table.

---

## Phase 1 — idea → design

Work in the game repo. One prompt starts the chain:

> "I have a rough idea — *\<your one sentence\>*. Help me develop it. Use the unity-game-router
> skill."

| Step | Skill / agent | Output |
| --- | --- | --- |
| Develop the idea | `design-idea-discovery` | `design/concept.md`, every line marked **confirmed** or **assumed** |
| Get it challenged | the `game-director` agent | Options with tradeoffs, conflicts, risks, a recommendation |
| Write it down | `design-write-gdd` → `design-decision-log` | `pitch.md`, `decisions.md`, and the **Stage** + **Dimension** fields pinned |

Discovery is a conversation, not a document generator: it plays the idea back, asks at most three
high-impact questions at a time, challenges what contradicts itself, and refuses to write a GDD from
one sentence. It needs **no Unity project and no Unity CLI**, so this phase can happen before Phase 0.

If the concept is already settled, skip discovery — say *"I want to build \<concept\>"* and the
router goes straight to `design-write-gdd`. Forcing discovery on a decided idea just costs time.

### The two answers nothing else can be derived from

- **Dimension** — `2D`, `2.5D` or `3D`. It decides camera, renderer, physics, art cost and which
  skills load, so a wrong guess is rework, not a detail. The router asks rather than guessing.
- **Art style** — give `assets-art-style-lock` a **reference image**. A style cannot be locked with
  adjectives, and every later asset depends on this lock.

---

## Phase 2 — layout and structure

You do not design this. It is pinned in `rules/folder-conventions.md`, and the skills create these
folders rather than inventing new top-level ones:

```
Assets/_Project/                  # all first-party content, so imported packages stay separate
  Art/{Sprites,Models,Materials,Textures,Animations,VFX}
  Audio/{Music,SFX,Mixers}
  Code/{Core,Systems,Features,Game}/     # one asmdef each
  Code/Tests/{EditMode,PlayMode}/
  Data/{Items,Levels,Tuning,EventChannels}   # ScriptableObject instances
  Prefabs/{Player,Enemies,Props,UI,Systems}
  Prototype/                      # PH_ placeholders only. Deleted, not shipped
  Scenes/{Bootstrap.unity,Gameplay,UI}
  UI/                             # UI Toolkit .uxml / .uss
Settings/{Rendering,Input,Build}
design/                           # the game's own design docs
```

Bootstrap it with `core-scene-setup` (bootstrap scene and flow) and `core-input-setup` (Input
System). The `architect` role owns assembly, package and layering calls and records them in
`design/tech-decisions.md`.

Two rules that bite if ignored: folder names are PascalCase with **no spaces** (spaces break CLI and
CI paths), and an asset's `.meta` file is part of the asset — move assets through the Editor or
`unity command`, never a bare `mv`, or every reference pointing at it breaks.

### What lives in `design/`

```
design/
  STATE.md            # where we are now, incl. Stage. Read on EVERY task. Under 60 lines
  INDEX.md            # a map of every other design doc. A doc with no row here is invisible
  concept.md          # the early hypothesis: verbs, loop, risks
  pitch.md            # fantasy, pillars, core loop, dimension, scope
  decisions.md        # DESIGN decisions — what the game is. Read its Index table, not the file
  art-bible.md        # the style lock. No production asset is made without it
  tech-decisions.md   # TECHNICAL decisions — how it is built. Append-only
  mechanic-<name>.md  # rules, tuning, feel, acceptance checks
  prototype-<name>.md # one hypothesis, its criteria, and the playtest log
```

Every skill starts by reading `STATE.md` and `INDEX.md` — and **nothing else** until one of them
points further. That is what keeps context cost flat as the project grows. `Stage` (`concept`,
`prototype`, `production`, `polish`, `shipped`) is how an existing project resumes instead of
restarting.

---

## Phase 3 — prototype before committing

> "I want to test whether \<riskiest assumption\> works before building it properly."

```
design-prototype-plan → core-* / dimension skills on PH_ placeholders
                      → qa-playmode-check → you play it → design-decision-log
```

- **Placeholders need no art bible.** Unity primitives, flat materials, blockout geometry, debug
  visuals and unstyled UI are explicitly exempt. They live in `Assets/_Project/Prototype/` with a
  `PH_` prefix and are listed in the prototype doc. Generated *production* art is still gated.
- **Two kinds of validation, kept apart.** Technical criteria (does it work, is it fast enough, do
  the controls behave) are measurable and run by `qa-playmode-check`. Gameplay questions (was it
  understood, did it feel right, were you frustrated) are answered only by a human who played it.
- **Agents never fill in the playtest log.** Until you report a session it says "not played yet" and
  the verdict stays "not concluded". Tell the agent what happened and it transcribes it.

---

## Phase 4 — assets

```
assets-art-style-lock (hard gate) → assets-gen-2d-sprite → 2d-sprite-import → 2d-sprite-animation
                                  → assets-gen-3d-model  → assets-import-pipeline
```

- If `art-bible.md` is not locked, the generation skills **stop.** Deliberate: an unlocked style
  means every asset is a fresh guess and the set has to be redone.
- A raw download is never the finished asset. `assets-import-pipeline` owns scale, axis, LODs, URP
  material conversion and Avatar retargeting.
- 3D generation reports credit cost **before** spending, and is asynchronous — it polls before
  downloading.
- Audio is `assets-audio-sfx`. Every asset gets a licensing row — see [ASSETS.md](ASSETS.md).
- Source art (layered, full-resolution) stays in `art-source/` at the repo root, **outside**
  `Assets/`, so Unity does not import it.

---

## Phase 5 — coding, one mechanic at a time

```
design-mechanic-spec → core-scriptable-object-data → core-unity-script → qa-playmode-check
```

**The spec comes first on purpose.** It produces the *acceptance checks*, which are what make "done"
decidable instead of a matter of opinion. Skip it and `qa-playmode-check` has nothing to measure —
the `gameplay-coder` role will refuse to start. Numbers you do not supply are proposed and flagged as
proposals; correct them **in the spec, not in the code**.

Process is proportional. A **significant** mechanic (a new system, a core-loop change, a scope
increase, anything contradicting `decisions.md`) gets a `game-director` review first. A **trivial**
change (a tuning value, a rename, a bug) gets no review and no spec: edit the number and re-verify.
Routing small work through design is a failure too.

Then the skills for your dimension:

| Area | Skills |
| --- | --- |
| Cross-cutting | `core-unity-script`, `core-scriptable-object-data`, `core-event-channels`, `core-save-system`, `core-ui-toolkit`, `core-scene-setup`, `core-input-setup` |
| 2D | `2d-sprite-import`, `2d-tilemap-level`, `2d-physics-setup`, `2d-sprite-animation`, `2d-lighting` |
| 2.5D | `25d-ortho-3d-camera`, `25d-billboard-sprites`, `25d-sorting-and-depth` |
| 3D | `3d-character-controller`, `3d-cinemachine-camera`, `3d-urp-lighting`, `3d-navmesh-ai` |

After **every** change: `unity recompile --strict`, then the relevant tests. Do not start the next
mechanic while the console has errors.

---

## Phase 6 — tests, QA and release

| Need | Skill |
| --- | --- |
| Run the suite | `qa-run-tests` — templates `EditModeTest.cs.txt`, `PlayModeTest.cs.txt` |
| Does it actually *play*, not just compile | `qa-playmode-check` — against the spec's acceptance checks |
| Console errors, compile failures, warnings | `qa-fix-console-errors` — **stop-the-line**: no feature work while it is red; `--strict` treats a warning as a failure |
| A player build | `qa-run-tests` → `qa-build` — gates on a clean strict recompile and a green suite, discovers real targets with `unity build --list-targets`, then **launches** the build |
| Before you commit | the `reviewer` agent — reads the diff and the spec, re-runs the checks rather than trusting the report, ranks findings blocking / should-fix / nit |

Every task ends with `design-update-state`, so the next session resumes from `STATE.md` instead of
redoing finished work.

---

## The seven roles

You rarely need more than one or two per task. Prompt them by name: *"Use the designer agent to spec
the grapple hook."*

| Role | Owns | Call it when |
| --- | --- | --- |
| `game-director` | Vision, pillars, cross-system coherence, scope | Before committing to a significant mechanic, or to have an idea challenged |
| `designer` | `design/` — concept, pitch, mechanic specs, prototype plans | Anything needs specifying before it is built |
| `architect` | Layers, assemblies, packages, `tech-decisions.md` | A feature spans systems, or a package choice is in play |
| `gameplay-coder` | C#, data assets, scene wiring | A spec exists and needs implementing |
| `asset-producer` | Art and audio, generation and import | Assets are needed and the style is locked |
| `qa` | Compile, tests, play-mode verification | After any implementation, before any build |
| `reviewer` | Accepting or rejecting a change | Before you commit |

The director and the designer are different jobs: the designer writes what a mechanic does, the
director judges whether the game should have it. **You are the final creative authority.** Anything
in `decisions.md` marked `PROPOSED` is waiting on you; nothing becomes `APPROVED` because an agent
liked its own idea.

Codex has no subagent directory — the role files are copied to `.unity-skillforge/agents/` and
[CODEX.md](CODEX.md) gives a one-line prompt for each.

---

## Your first three prompts in a new repo

1. "I have a rough idea — *\<sentence\>*. Help me develop it. Use the unity-game-router skill."
2. "Lock the art style — here is a reference image." *(attach it)*
3. "Set up the bootstrap scene and input, then spec the first mechanic."

Then read a walkthrough — it shows the real shape of the work better than any reference page:
[idea to prototype](../examples/idea-to-prototype-walkthrough.md), and
[2D platformer](../examples/2d-platformer-walkthrough.md) or
[3D third-person](../examples/3d-third-person-walkthrough.md) for your dimension.

---

## Habits that keep it working

- **Describe the symptom, not the fix.** "Sprites draw in front of walls" routes correctly; "change
  the sorting layer" sends the agent to the wrong system.
- **One mechanic at a time.** A clean strict compile and green tests before the next one.
- **Answer the dimension and art-style questions properly.** Everything else derives from them.
- **Treat "not verified" as a real answer.** If no Editor was reachable, the skills say so rather
  than inferring a pass. That is the behaviour you want.
- **Let it update `STATE.md`.** The next session starts there, and a stale one causes finished work
  to be redone.
- **Say when a proposed number is wrong.** Correcting the spec is cheaper than correcting the code.
- **Report playtests in your own words.** "I got lost after the second room" is worth more than any
  metric here, and it is the only input that can answer a gameplay question.
- **Never commit secrets.** Asset-provider keys live in environment variables.

If Unity's own plugin is installed (`/plugin marketplace add Unity-Technologies/unity-agent-plugin`),
these skills defer to the matching `/unity:*` skill where the topics overlap instead of duplicating
it.
