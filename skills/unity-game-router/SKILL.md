---
name: unity-game-router
description: Entry point for Unity game work. Classifies the task and the project dimension (2D, 2.5D or 3D) from the design folder, then names the minimum set of skills to load. Use when a Unity request is broad or unclear, when starting a project, or when unsure which skill applies.
metadata:
  version: 0.1.0
---

# Unity game router

Paths written as `PACK/` mean wherever this pack's shared files live: `.unity-skillforge/` in a
game repo (`install.sh`), the sibling `unity-skillforge-pack` folder (`npx skills add`), the
plugin's root directory (plugin install), or `skills/unity-skillforge-pack/` in this repo.

This skill is the **Tier 0 entry point when this pack is installed as a plugin**, because Claude Code
does not load a plugin's `AGENTS.md` or `CLAUDE.md`. If the pack was installed into a game repo with
`install.sh`, `AGENTS.md` carries the same rules and table and is loaded automatically — in that
case use this skill only when the right path is genuinely unclear.

## When to use

- A Unity request is broad ("make a platformer", "add enemies", "the game is broken").
- Starting a new project, or you do not know the project's dimension.
- You are unsure which of the pack's skills applies.

Skip it when the request already maps to one obvious skill — load that skill directly rather than
paying for a routing step.

## Hard rules (these apply to every task)

1. **Unity 6.3 LTS (`6000.3.x`) baseline**, URP, new Input System. No deprecated APIs.
2. **The Editor bridge is the Unity CLI**, not the deprecated in-Editor MCP server. Run
   `unity status`, then discover the real surface with `unity list` and
   `unity commands --format json`. **Never call a name you have not seen in that output.**
3. **Read `design/STATE.md` and `design/INDEX.md` first — and only those.** Open a specific design
   doc only when `INDEX.md` points at it.
4. **Copy a template, don't invent one** (`PACK/templates/`).
5. **Defer to Unity's official skill when installed** — see
   `PACK/references/official-unity-skills.md`.
6. **Pin everything.** No "latest", no silent defaults.
7. **One mechanic at a time.** `unity recompile --strict` and tests must be clean before the next.
8. **No generated asset without a locked `design/art-bible.md`.**
9. **Report honestly.** Anything not verified in a running Editor is stated as unverified.

## Inputs needed

- The user's request.
- `design/STATE.md` — above all its **Dimension** field, which decides the whole path.

## Steps

1. Read `design/STATE.md` and `design/INDEX.md`. Nothing else yet.
2. **If `design/` does not exist**, stop routing and run `design-write-gdd`. Nothing else in this
   pack works without it.
3. Read the **Dimension** field. If it is missing or ambiguous, ask the user — do not guess, because
   it decides camera, renderer, physics and art cost:
   | Dimension | Means |
   | --- | --- |
   | **2D** | Flat art, camera faces the plane, 2D Renderer |
   | **2.5D** | 3D geometry and lighting, 2D presentation, fixed camera angle, Universal Renderer |
   | **3D** | Free camera, depth matters to gameplay, Universal Renderer |
4. Check **Blocked / broken** in `STATE.md`. If something is broken, route there first —
   `qa-fix-console-errors` — regardless of what was asked.
5. Classify the request and route with the table below. **Name the skills you are loading and why,
   in one line**, then load only those.
6. Prefer the narrowest set. Two skills is normal; six means the request should be split into
   separate tasks.
7. If the topic belongs to Unity's official plugin, say so and route to the `/unity:*` skill rather
   than loading ours — check `PACK/references/official-unity-skills.md`.
8. End every task by handing off to `design-update-state`.

## Routing table — for X → load Y

| When the task is | Load |
| --- | --- |
| No design folder, or a new game from a pitch | `design-write-gdd` |
| About to build a mechanic that has no spec | `design-mechanic-spec` |
| Too much scope, stalled progress, a deadline moved | `design-scope-cut` |
| Finishing any task | `design-update-state` |
| Write or refactor a MonoBehaviour, asmdef layout | `core-unity-script` |
| Tunable data, config, item or level definitions | `core-scriptable-object-data` |
| Decoupling systems, messaging between scenes | `core-event-channels` |
| Player input, bindings, control schemes, rebinding | `core-input-setup` |
| Saving and loading progress or settings | `core-save-system` |
| Menus, HUD, settings screens | `core-ui-toolkit` |
| Create or wire a scene, bootstrap flow | `core-scene-setup` |
| Import sprites, PPU, pivots, filter mode, compression | `2d-sprite-import` |
| Build a tilemap level, rule tiles, palettes | `2d-tilemap-level` |
| 2D collisions, rigidbodies, triggers, platformer feel | `2d-physics-setup` |
| Sprite sheet animation, Animator for 2D | `2d-sprite-animation` |
| 2D lights, shadows, normal maps | `2d-lighting` |
| Orthographic or faked-perspective camera for 2.5D | `25d-ortho-3d-camera` |
| Sprites standing in a 3D scene, facing the camera | `25d-billboard-sprites` |
| Wrong draw order, sorting axis, isometric depth | `25d-sorting-and-depth` |
| Player movement and control in 3D | `3d-character-controller` |
| Follow, orbit or aim cameras | `3d-cinemachine-camera` |
| Lighting a 3D scene, baked GI, probes, URP volumes | `3d-urp-lighting` |
| Enemy or NPC pathfinding and navigation | `3d-navmesh-ai` |
| Define or enforce the visual style before making art | `assets-art-style-lock` |
| Generate a 2D sprite, tileset or UI art | `assets-gen-2d-sprite` |
| Generate, retexture, rig or animate a 3D model | `assets-gen-3d-model` |
| Bring an external model or texture into the project | `assets-import-pipeline` |
| Sound effects, music, mixers | `assets-audio-sfx` |
| Run the test suite | `qa-run-tests` |
| Check the game actually plays, not just compiles | `qa-playmode-check` |
| Console errors, compile failures, warnings | `qa-fix-console-errors` |
| Produce a player build | `qa-build` |

## Common routes

| Request | Route |
| --- | --- |
| "Make a 2D platformer from this pitch" | `design-write-gdd` → `assets-art-style-lock` → `core-scene-setup` → `core-input-setup` → `design-mechanic-spec` → `2d-physics-setup` → `qa-playmode-check` |
| "Add a dash to the player" | `design-mechanic-spec` → `core-scriptable-object-data` → `core-unity-script` → `qa-playmode-check` |
| "Make an isometric tactics game" | `design-write-gdd` → `25d-ortho-3d-camera` → `25d-sorting-and-depth` → `2d-tilemap-level` |
| "Sprites are drawing in front of walls" | `25d-sorting-and-depth` |
| "Generate enemy sprites" | `assets-art-style-lock` → `assets-gen-2d-sprite` → `2d-sprite-import` |
| "The game won't compile" | `qa-fix-console-errors` |
| "Ship a build" | `qa-run-tests` → `qa-build` |

## Unity CLI commands used

```bash
unity status                     # is an Editor reachable at all
unity list                       # Editor-registered tools and their parameter schemas
unity commands --format json     # full CLI command manifest
```

Routing itself touches nothing. See `PACK/references/unity-cli.md`.

## Files to read (exact paths)

| Need | Path |
| --- | --- |
| Project status and dimension | `design/STATE.md` |
| Design map | `design/INDEX.md` |
| What Unity's official plugin already covers | `PACK/references/official-unity-skills.md` |
| Editor bridge surface | `PACK/references/unity-cli.md` |

## Done checklist

- [ ] `design/STATE.md` and `design/INDEX.md` were read, and nothing else.
- [ ] A missing `design/` folder routed to `design-write-gdd`.
- [ ] The dimension is known, or the user was asked rather than guessed.
- [ ] A broken console routed to `qa-fix-console-errors` first.
- [ ] The chosen skills were named with a one-line reason.
- [ ] The set is minimal; a sprawling request was split into tasks.
- [ ] Topics owned by Unity's official plugin were routed to `/unity:*`.

## Common mistakes

- Guessing the dimension. It decides camera, renderer, physics and art cost, so a wrong guess is
  rework, not a detail.
- Reading the whole `design/` folder. Two files, then only what `INDEX.md` points at.
- Routing to implementation while `STATE.md` says something is broken.
- Loading eight skills for one request, spending the context the tiering exists to save.
- Routing a mechanic straight to code with no spec, leaving `qa-playmode-check` nothing to verify.
- Rewriting a topic Unity's official plugin already owns instead of routing to it.
- Routing an obvious single-skill request through here instead of loading that skill directly.
