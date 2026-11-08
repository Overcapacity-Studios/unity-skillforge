---
name: core-scene-setup
description: Create or wire a Unity scene following this project's bootstrap and additive-loading contract - one persistent bootstrap scene, gameplay scenes loaded additively, no cross-scene references. Use when adding a scene or fixing scene load order and persistent services.
metadata:
  version: 0.1.0
---

# Scene setup

Paths written as `PACK/` mean wherever this pack's shared files live: `.unity-skillforge/` in a
game repo (`install.sh`), the sibling `unity-skillforge-pack` folder (`npx skills add`), the
plugin's root directory (plugin install), or `skills/unity-skillforge-pack/` in this repo.

## When to use

- Adding a gameplay, menu or level scene.
- Setting up the bootstrap scene on a new project.
- Fixing "service is null" on scene load, or a scene that only works when opened directly.

## Prefer the official skill

If Unity's official plugin is installed:

- `/unity:new-unity-project` — project creation, packages and initial setup. Run it before this
  skill on a brand-new project.
- `/unity:craft-game-floors` — building out the contents of a 3D scene (layout, lighting, camera
  rigs). Its `references/scene-lighting.md` and `references/camera-rigs.md` are authoritative.

What stays ours: the **bootstrap and additive-loading contract** below, scene naming, and the
service lifetime rules. Do not restate Unity's scene-authoring procedure — link it. See
`PACK/references/official-unity-skills.md`.

## Inputs needed

- Scene role: bootstrap, menu, gameplay level, or additive overlay.
- Which persistent services it needs (they live in bootstrap, not here).
- The project dimension (2D / 2.5D / 3D) from `design/STATE.md` — it decides camera and renderer.

## Steps

1. Read `design/STATE.md` and `design/INDEX.md`. Note the dimension; it drives everything below.
2. Ensure the bootstrap scene exists at `Assets/_Project/Scenes/Bootstrap.unity`. If not, create it:
   - One `Bootstrap` GameObject with the composition root script.
   - It registers services via `PACK/templates/csharp/ServiceLocator.cs.txt` in `Awake` and calls
     `ServiceLocator.Clear()` in `OnDestroy`.
   - It is **first in the Build Settings scene list** and is never unloaded.
3. Create the new scene at `Assets/_Project/Scenes/{Gameplay|UI}/<SceneName>.unity`. Scene names are
   PascalCase and unique project-wide — `unity` CLI commands address scenes by name.
4. Set up the camera for the dimension:
   - 2D → orthographic camera, 2D Renderer. See `2d-lighting`.
   - 2.5D → run `25d-ortho-3d-camera`; do not hand-roll it.
   - 3D → perspective camera, Universal Renderer; run `3d-cinemachine-camera` for the rig.
5. Confirm the scene's quality tier has a URP Asset assigned, per `PACK/references/urp-settings.md`.
   A tier pointing at `None` silently falls back to Built-in and renders wrong.
6. Add exactly one **global Volume** with the profile at
   `Assets/Settings/Rendering/Volumes/Global.asset`.
7. Register the scene in Build Settings, after `Bootstrap`.
8. Enforce the contract:
   - Gameplay scenes load **additively**; bootstrap owns persistent services.
   - A scene must not assume another scene is already loaded — it asks the scene loader service.
   - **No cross-scene references in the Inspector.** They do not survive a build.
   - Resolve services in `Start`, not `Awake` — registration order matters.
9. Mark non-moving geometry as Static so occlusion and light baking can work
   (`PACK/rules/performance.md`).
10. Verify the scene works from a cold start, not just when opened directly:
    ```bash
    unity recompile --strict --format json
    ```
    then run `qa-playmode-check` starting from `Bootstrap`.

## Unity CLI commands used

```bash
unity status                              # live Editors: port, project path, version, PID
unity list                                # Editor-registered tools and their parameter schemas
unity commands --format json              # full CLI command manifest
unity recompile --strict --format json    # compile check
unity test --format json                  # PlayMode tests for load order
```

Scene creation and object wiring go through the Editor tools discovered by `unity list`, or an
Editor script run with `eval_file`. Unity's docs show `Unity.ManageScene` and
`Unity.ManageGameObject` only as examples of the deprecated MCP surface — **use the names `unity
list` actually reports**, not those. See `PACK/references/unity-cli.md`.

## Files to read (exact paths)

| Need | Path |
| --- | --- |
| Project status and dimension | `design/STATE.md` |
| Design map | `design/INDEX.md` |
| Official skill map | `PACK/references/official-unity-skills.md` |
| URP assets, renderer, volumes | `PACK/references/urp-settings.md` |
| Version and package pins | `PACK/references/unity-versions.md` |
| Scene and folder naming | `PACK/rules/folder-conventions.md` |
| Composition root rules | `PACK/rules/architecture.md` |
| Static flags, batching | `PACK/rules/performance.md` |
| Service locator template | `PACK/templates/csharp/ServiceLocator.cs.txt` |

## Done checklist

- [ ] `Bootstrap.unity` exists, is first in Build Settings, and is never unloaded.
- [ ] Services are registered in bootstrap and cleared on destroy.
- [ ] The new scene is in `Assets/_Project/Scenes/`, PascalCase and uniquely named.
- [ ] Camera and renderer match the dimension in `design/STATE.md`.
- [ ] Every quality tier has a URP Asset assigned.
- [ ] Exactly one global Volume, using the shared profile.
- [ ] The scene is registered in Build Settings after `Bootstrap`.
- [ ] No cross-scene Inspector references.
- [ ] Services are resolved in `Start`, not `Awake`.
- [ ] Non-moving geometry is marked Static.
- [ ] Verified by starting from `Bootstrap`, not by opening the scene directly.

## Common mistakes

- Testing a scene by opening it directly, so missing bootstrap services are never noticed until the
  build.
- Resolving a service in `Awake` and getting null because bootstrap had not registered it yet.
- Cross-scene Inspector references, which look fine in the Editor and are empty in a build.
- Loading a gameplay scene in Single mode, unloading bootstrap and taking every service with it.
- Leaving one quality tier without a URP Asset, so the scene is black on that tier only.
- Several global Volumes in one scene, giving unpredictable post-processing.
- Duplicating a scene name, so a CLI command addresses the wrong scene.
- Putting persistent services in the gameplay scene, so they are destroyed and recreated on reload.
