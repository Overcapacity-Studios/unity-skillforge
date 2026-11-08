---
name: 25d-billboard-sprites
description: Make sprites stand correctly in a 3D scene for a 2.5D game - billboard orientation, upright versus full facing, lighting that works on a flat quad, and shadow handling. Use when 2D art must sit in 3D space. Not for pure 2D sprites on an orthographic 2D camera.
metadata:
  version: 0.1.0
---

# Billboard sprites in 3D

Paths written as `PACK/` mean wherever this pack's own files live: `.unity-skillforge/` in a game
repo (created by `install.sh`), the plugin's root directory when installed as a plugin, or the
repo root when working on the pack itself.

## When to use

- 2D characters, props or foliage placed in a 3D scene (the classic 2.5D look).
- Sprites appear edge-on, invisible, unlit, or lie flat on the ground.
- Sprites intersect the floor or clip into geometry.

Not for pure 2D, where the camera faces the sprites by definition.

## Inputs needed

- `design/STATE.md` dimension must be **2.5D**, and the camera set up by `25d-ortho-3d-camera`.
- Whether the camera angle is truly fixed. If it is, you may not need runtime billboarding at all.
- The sprites, imported at project PPU via `2d-sprite-import`.

## Steps

1. Read `design/STATE.md` (confirm 2.5D), `design/INDEX.md`, `design/art-bible.md`, and
   `design/tech-decisions.md` for the camera projection.
2. **Ask whether you need billboarding at all.** With a genuinely fixed camera angle, the cheapest
   correct answer is to rotate sprites once at author time to match the camera and never update them
   at runtime. Choose from this table and record the choice:
   | Approach | Use when | Cost |
   | --- | --- | --- |
   | **Static authored rotation** | Camera angle never changes | Zero per frame. Prefer this |
   | **Upright billboard** (Y-axis only) | Camera orbits or the projection is perspective | One rotation per sprite per frame |
   | **Full billboard** (faces camera on all axes) | Particles, UI-ish markers, decals | Same, but characters look like they lean back |
3. For characters use **upright** billboarding, never full. A full billboard tilts a character with
   the camera pitch, so its feet lift off the ground and it reads as a floating cardboard cutout.
4. Implement billboarding in `LateUpdate`, after the camera has moved. Doing it in `Update` leaves
   sprites one frame behind, which is visible as a shimmer at the edges.
5. Cache the camera transform once in `Awake`. **Never call `Camera.main` per frame** — it performs
   a tagged search every call (`PACK/rules/performance.md`). For many sprites, drive them all from
   one manager iterating a list rather than giving each a MonoBehaviour with its own `LateUpdate`.
6. Choose the renderer for the sprite:
   - `SpriteRenderer` — simplest, but with the Universal Renderer it is unlit unless you assign a
     lit sprite material.
   - **Quad with a URP Lit material**, alpha-clipped — use this when sprites must receive scene
     lighting and cast or receive shadows. This is usually the right answer in 2.5D.
   Record the choice; mixing the two in one scene gives inconsistent lighting.
7. Set up the pivot and ground contact: the sprite's pivot should be **bottom-centre** (from
   `design/art-bible.md`) and the quad should sit with its base on the ground plane. Then offset the
   sprite slightly along the camera's view direction so it does not z-fight with the floor.
8. Enable **alpha clipping** rather than alpha blending on lit sprite materials. Blended sprites do
   not write depth, so they sort against each other unpredictably and cannot cast proper shadows —
   this is the most common 2.5D sprite bug.
9. For shadows, set Cast Shadows to **Two Sided** on a single-quad sprite, or it disappears from the
   shadow map when seen from behind.
10. Hand draw-order between sprites and 3D geometry to `25d-sorting-and-depth`.
11. Verify:
    ```bash
    unity recompile --strict --format json
    ```
    then `qa-playmode-check`: sprites stay upright, are lit consistently, make ground contact, do
    not z-fight, and sort correctly as the camera moves.

## Unity CLI commands used

```bash
unity status                              # live Editors: port, project path, version, PID
unity list                                # Editor-registered tools and their parameter schemas
unity commands --format json              # full CLI command manifest
unity recompile --strict --format json    # compile check
unity test --format json                  # PlayMode tests asserting orientation
```

Material and renderer setup is Editor work: use the tools `unity list` reports, or an Editor script
run with `eval_file`. Use fully-qualified names such as `UnityEngine.SpriteRenderer`. See
`PACK/references/unity-cli.md`.

## Files to read (exact paths)

| Need | Path |
| --- | --- |
| Project dimension | `design/STATE.md` |
| Design map | `design/INDEX.md` |
| Pivot, PPU, art angle | `design/art-bible.md` |
| Recorded camera projection | `design/tech-decisions.md` |
| Camera setup | the `25d-ortho-3d-camera` skill |
| Draw order against 3D geometry | the `25d-sorting-and-depth` skill |
| Materials, alpha, URP Lit | `PACK/references/urp-settings.md` |
| Per-frame cost rules | `PACK/rules/performance.md` |

## Done checklist

- [ ] Checked whether static authored rotation would do, before adding runtime billboarding.
- [ ] Characters use upright (Y-only) billboarding, not full.
- [ ] Orientation updates in `LateUpdate`, not `Update`.
- [ ] The camera transform is cached; `Camera.main` is not called per frame.
- [ ] Many sprites are driven by one manager, not one `LateUpdate` each.
- [ ] One renderer approach across the scene, and it is recorded.
- [ ] Alpha **clipping**, not blending, on lit sprite materials.
- [ ] Pivot is bottom-centre and the sprite makes clean ground contact with no z-fighting.
- [ ] Cast Shadows is Two Sided where sprites cast shadows.
- [ ] Verified in play mode while moving the camera.

## Common mistakes

- Full billboarding on characters, so they tilt with camera pitch and their feet leave the ground.
- Billboarding in `Update`, leaving every sprite a frame behind the camera.
- `Camera.main` inside `LateUpdate` on hundreds of sprites — a tagged search per sprite per frame.
- Alpha-blended sprite materials that write no depth, so sprites sort randomly against each other
  and cast no usable shadow.
- A `SpriteRenderer` with an unlit material in a lit 3D scene, so sprites look pasted on.
- Mixing `SpriteRenderer` and lit quads in one scene, giving two different looks for the same art.
- A centre pivot, so characters sink into or hover above the floor.
- Cast Shadows left on One Sided, so a single quad vanishes from the shadow map at some angles.
- Adding billboarding to a game whose camera never moves, paying a per-frame cost for nothing.
