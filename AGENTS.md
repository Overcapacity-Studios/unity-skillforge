# unity-skillforge — agent rules

How we build Unity games. The game repo's own `design/` folder says *what* to build; this pack says
*how*. Tier 0 = this file (always loaded). Tier 1 = a `SKILL.md` (loaded on trigger). Tier 2 =
`references/`, `templates/`, `rules/`, `design/` — read by **exact path only**, never speculatively.

Paths below are written as `PACK/...`, which means `.unity-skillforge/...` in a game repo after
`install.sh`, or this repo's root when working on the pack itself.

## Hard rules

1. **Unity 6.3 LTS (`6000.3.x`) baseline**, URP, new Input System. Never use a deprecated API.
   Version and package pins: `PACK/references/unity-versions.md`.
2. **The Editor bridge is the Unity CLI**, not the in-Editor MCP server — Unity deprecated that.
   Before touching the Editor run `unity status`, then discover the real surface with
   `unity list` and `unity commands --format json`. **Never call a tool or command name you have
   not seen in that output.** Full surface: `PACK/references/unity-cli.md`.
3. **Read `design/STATE.md` and `design/INDEX.md` first — and only those.** Never read all of
   `design/`. Open a specific design doc only when `INDEX.md` points you at it.
4. **Copy a template, don't invent one.** If `PACK/templates/` has it, copy and adapt it.
5. **Defer to Unity's official skill when it is installed.** If a `/unity:*` skill covers the
   topic, run it and contribute only our conventions on top.
   Map: `PACK/references/official-unity-skills.md`.
6. **Pin everything.** Package versions, pixels-per-unit, import settings, build targets. No
   "latest", and no setting left at a default you did not state.
7. **One mechanic at a time.** After each change run `unity recompile --strict`, then the relevant
   tests. Do not start the next mechanic while the console has errors.
8. **No generated asset without `design/art-bible.md`.** The style lock is mandatory and every
   asset request must quote it.
9. **Never commit secrets or API keys.** Asset-provider keys live in environment variables.
10. **Report honestly.** Anything you could not verify in a running Unity Editor must be stated as
    unverified. Never describe an import setting or PlayMode result you did not observe.

## Routing table — for X → read Y

Load a skill by name. Each lives at `skills/<name>/SKILL.md` in the pack.

| When the task is | Use skill |
| --- | --- |
| Unclear, or starting a new game, or you need to pick a path | `unity-game-router` |
| Write or refactor a MonoBehaviour, asmdef layout | `core-unity-script` |
| Tunable data, config, item/level definitions | `core-scriptable-object-data` |
| Decoupling systems, messaging between scenes | `core-event-channels` |
| Player input, bindings, control schemes, rebinding | `core-input-setup` |
| Saving and loading progress | `core-save-system` |
| Menus, HUD, settings screens | `core-ui-toolkit` |
| Create or wire up a scene, bootstrap flow | `core-scene-setup` |
| Import sprites, PPU, pivots, filter mode, compression | `2d-sprite-import` |
| Build a tilemap level, rule tiles, palettes | `2d-tilemap-level` |
| 2D collisions, rigidbodies, triggers, platformer feel | `2d-physics-setup` |
| Sprite sheet animation, Animator for 2D | `2d-sprite-animation` |
| 2D lights, shadows, normal maps | `2d-lighting` |
| Orthographic or faked-perspective 3D camera for a 2.5D game | `25d-ortho-3d-camera` |
| Sprites standing in a 3D scene, facing the camera | `25d-billboard-sprites` |
| Things drawing in the wrong order, sorting axis, isometric depth | `25d-sorting-and-depth` |
| Player movement and control in 3D | `3d-character-controller` |
| Follow/orbit/aim cameras in 3D | `3d-cinemachine-camera` |
| Lighting a 3D scene, baked GI, probes, URP volumes | `3d-urp-lighting` |
| Enemy or NPC pathfinding and navigation | `3d-navmesh-ai` |
| Define or enforce the visual style before making art | `assets-art-style-lock` |
| Generate a 2D sprite, tileset or UI art | `assets-gen-2d-sprite` |
| Generate, retexture, rig or animate a 3D model | `assets-gen-3d-model` |
| Bring an external model or texture into the project correctly | `assets-import-pipeline` |
| Sound effects, music, mixers | `assets-audio-sfx` |
| Run the test suite | `qa-run-tests` |
| Check the game actually plays, not just compiles | `qa-playmode-check` |
| Console errors, compile failures, warnings | `qa-fix-console-errors` |
| Produce a player build | `qa-build` |
| Turn a pitch into a design doc | `design-write-gdd` |
| Specify one mechanic before coding it | `design-mechanic-spec` |
| Too much scope, cut it down | `design-scope-cut` |
| Record what changed, update project status | `design-update-state` |

## Conventions — read before writing code

| Topic | File |
| --- | --- |
| C# naming, formatting, nullability, async rules | `PACK/rules/csharp-style.md` |
| Assembly, dependency and composition rules | `PACK/rules/architecture.md` |
| Where every asset and script type lives | `PACK/rules/folder-conventions.md` |
| Allocation, draw calls, physics and update budgets | `PACK/rules/performance.md` |

## Templates

C#: `PACK/templates/csharp/` — `MonoBehaviour`, `ScriptableObject`, `StateMachine`, `EventChannel`,
`ServiceLocator`, `EditModeTest`, `PlayModeTest` (each a `.cs.txt` file).

Design docs: `PACK/templates/game-design/` — `INDEX.md`, `pitch.md`, `mechanic.md`, `art-bible.md`,
`tech-decisions.md`, `STATE.md`.

## Output discipline

- Say which skill you are following, in one line, before you act.
- Prefer running a script or copying a template over generating code from scratch.
- Keep diffs minimal: change only what the task needs, and do not reformat unrelated files.
- End a task by updating `design/STATE.md` via `design-update-state`.
