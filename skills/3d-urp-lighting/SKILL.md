---
name: 3d-urp-lighting
description: Light a 3D or 2.5D scene in URP - directional and real-time lights, baked GI and lightmaps, Adaptive Probe Volumes, and the global Volume. Use when lighting a scene or fixing flat, black or over-bright results. Defer to Unity's skills for post-processing and Built-in pipeline migration.
metadata:
  version: 0.1.0
---

# URP lighting

Paths written as `PACK/` mean `.unity-skillforge/` in a game repo, or this pack's root.

## When to use

- Lighting a 3D or 2.5D scene.
- The scene is flat, black, blown out, or looks different in the build than the Editor.
- Setting up baked lighting or probe-based indirect light.

## Prefer the official skill

If Unity's official plugin is installed:

- `/unity:urp-postprocessing` — Volume overrides, bloom, tonemapping, colour grading.
- `/unity:migrate-birp-to-urp` — a project still on the Built-in pipeline.
- `/unity:validate-urp-render-graph-renderer-feature` — custom renderer features.
- `/unity:craft-game-floors` — its `references/scene-lighting.md` covers scene lighting recipes.

What stays ours: **baked GI, lightmap and Adaptive Probe Volume settings**, which are thin
officially, plus the per-tier verification rule. See `PACK/references/official-unity-skills.md`.

## Inputs needed

- Mood, time of day and light direction from `design/art-bible.md`.
- The project dimension. 2.5D uses this skill, not `2d-lighting` — the 2D Renderer cannot light 3D
  meshes.
- Whether the scene is static enough to bake. If everything moves, baking buys nothing.

## Steps

1. Read `design/STATE.md`, `design/INDEX.md`, `design/art-bible.md`, and `design/tech-decisions.md`.
2. Confirm the fundamentals before touching a light — each of these is unrecoverable later without
   redoing work (`PACK/references/urp-settings.md`):
   - **Colour space is Linear.** Gamma breaks lighting maths.
   - Every quality tier has a URP Asset assigned. A tier set to `None` silently falls back to
     Built-in and renders wrong on that tier only.
   - The renderer is the **Universal Renderer** (Forward, Forward+ or Deferred), recorded in
     `design/tech-decisions.md`. Changing it later invalidates bakes.
3. Set up the key light: one **Directional** light as the sun, angled per the art bible. Set its
   intensity and colour temperature deliberately rather than leaving defaults.
4. Decide real-time versus baked per object, and mark it:
   - Static geometry → **Static** flag set, Light mode **Baked** or **Mixed**.
   - Moving objects → real-time light plus probes for indirect.
   A real-time light with shadows is one extra full render of everything it touches
   (`PACK/rules/performance.md`).
5. For baked GI, in Lighting settings:
   - Lightmapper: **Progressive GPU** where available, CPU as fallback.
   - **Lightmap Resolution** is the main cost and quality dial. Start low (10–20 texels/unit) and
     raise it only where seams or blotches are visible. Starting high means every bake is slow for
     no gain.
   - Enable **Compress Lightmaps** for shipping; disable while judging quality, since compression
     artefacts can be mistaken for bake errors.
   - Set Lightmap Size to 1024 or 2048. Larger atlases reduce count but waste memory on small scenes.
6. For indirect light on moving objects, prefer **Adaptive Probe Volumes (APV)** over hand-placed
   Light Probe Groups. Add one APV covering the playable space, set the density higher only where
   lighting changes sharply, and bake it with the lightmaps. Hand-placing probe groups in a modern
   URP project is work the APV does better.
7. Add exactly **one global Volume** per scene, using the shared profile at
   `Assets/Settings/Rendering/Volumes/Global.asset`. Set tonemapping there once; it is an
   art-bible decision, not a per-scene one. Local volumes use a trigger collider and a blend
   distance — never set a local volume to Global.
8. Set shadow cascades per `PACK/references/urp-settings.md`: 1 for 2.5D and small scenes, 2–4 only
   for open scenes. Each cascade is a full extra shadow render.
9. Bake, then **look at it in a build on the target device**, not only the Editor. Then verify on a
   second quality tier.
   ```bash
   unity recompile --strict --format json
   ```
   then `qa-playmode-check`, then `qa-build`.
10. If you change renderer, colour space or light modes after baking, **re-bake**. Stale lightmaps
    render convincingly and are wrong.

## Unity CLI commands used

```bash
unity status                              # live Editors: port, project path, version, PID
unity list                                # Editor-registered tools and their parameter schemas
unity commands --format json              # full CLI command manifest
unity recompile --strict --format json    # compile check
unity build --format json                 # verify the lit result in a real build
```

Baking is long-running Editor work: start it through the tools `unity list` reports and consider
`unity job` for detached jobs rather than blocking. Use fully-qualified names such as
`UnityEngine.LightmapSettings`. See `PACK/references/unity-cli.md`.

## Files to read (exact paths)

| Need | Path |
| --- | --- |
| Project dimension | `design/STATE.md` |
| Design map | `design/INDEX.md` |
| Mood, light direction, tonemapping choice | `design/art-bible.md` |
| Recorded renderer decision | `design/tech-decisions.md` |
| Colour space, tiers, cascades, volumes | `PACK/references/urp-settings.md` |
| Official post-processing and migration skills | `PACK/references/official-unity-skills.md` |
| Shadow and static-flag budgets | `PACK/rules/performance.md` |
| 2D lighting instead (pure 2D only) | `PACK/skills/2d-lighting/SKILL.md` |

## Done checklist

- [ ] Colour space is Linear.
- [ ] Every quality tier has a URP Asset using the Universal Renderer.
- [ ] The renderer choice is recorded in `design/tech-decisions.md`.
- [ ] One directional key light, angled and tuned per the art bible.
- [ ] Static geometry is marked Static with Baked or Mixed light mode.
- [ ] Lightmap resolution started low and was raised only where needed.
- [ ] Adaptive Probe Volumes cover the playable space; no hand-placed probe groups.
- [ ] Exactly one global Volume per scene, with tonemapping set once.
- [ ] Shadow cascade count matches the scene scale.
- [ ] Verified in a build on the target device, and on a second quality tier.
- [ ] Re-baked after any renderer, colour space or light-mode change.

## Common mistakes

- Using the 2D Renderer in a 2.5D project, then finding 3D meshes cannot be lit at all.
- Lighting in Gamma colour space, so every value has to be re-tuned after switching to Linear.
- One quality tier without a URP Asset, so the scene is black on that tier only — and usually in the
  build rather than the Editor.
- Starting at a high lightmap resolution, making every iteration a long bake for no visible gain.
- Judging bake quality with lightmap compression on, and chasing artefacts that are compression.
- Hand-placing light probe groups when an Adaptive Probe Volume would cover it correctly.
- Several global Volumes in one scene, giving unpredictable post-processing.
- Many real-time shadowed lights, each a full extra render, then blaming mesh complexity.
- Changing the renderer after baking and shipping stale lightmaps that look plausible and are wrong.
- Signing off lighting from the Editor viewport only.
