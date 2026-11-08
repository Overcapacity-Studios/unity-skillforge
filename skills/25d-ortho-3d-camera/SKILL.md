---
name: 25d-ortho-3d-camera
description: Set up the camera for a 2.5D game - orthographic or narrow-perspective projection over a 3D scene, with a fixed angle, pixel-exact framing and the matching URP renderer. Use for isometric, top-down-angled or 2D-in-3D games. Not for pure 2D or free-look 3D.
metadata:
  version: 0.1.0
---

# 2.5D camera

Paths written as `PACK/` mean `.unity-skillforge/` in a game repo, or this pack's root.

## What 2.5D means here

Geometry and physics are **3D**; presentation reads as **2D**. The camera is locked to a fixed angle
and the player never controls it freely. That combination is what makes 2.5D its own problem: you
get 3D lighting and depth, plus 2D sorting and framing concerns at the same time.

## When to use

- Isometric or three-quarter-view games (tactics, ARPG, city builder).
- Top-down-angled games where art is authored for one fixed angle.
- Sprites or flat art composed inside a 3D scene.

Not for: pure 2D with an orthographic camera and the 2D Renderer (`core-scene-setup` plus
`2d-lighting`), or free-look 3D (`3d-cinemachine-camera`).

## Inputs needed

- `design/STATE.md` dimension must be **2.5D**. If it says 2D or 3D, stop and confirm with the user.
- The intended camera angle and whether the art is authored for exactly that angle.
- Target resolution, and whether pixel-exactness is required.

## Steps

1. Read `design/STATE.md` (confirm 2.5D), `design/INDEX.md`, `design/art-bible.md` and
   `design/tech-decisions.md`.
2. Use the **Universal Renderer**, not the 2D Renderer. The 2D Renderer cannot light 3D meshes, and
   2.5D scenes contain them. Confirm every quality tier per `PACK/references/urp-settings.md`.
3. Choose the projection and record it in `design/tech-decisions.md` — this is expensive to change
   once art exists:
   | Projection | Gives | Costs |
   | --- | --- | --- |
   | **Orthographic** | No perspective distortion; art authored once works everywhere on screen; clean isometric | No depth cue from perspective; shadows and VFX can read flat |
   | **Narrow perspective** (FOV 15–30, camera pulled far back) | Subtle depth, better-looking shadows and particles | Art distorts toward screen edges; sprites must face the camera |
4. Set the angle once and never let it drift. Common choices: `30°` X for a classic isometric look,
   `45°` X and `45°` Y for true isometric, `60°` X for a tactics view. Put the angle on the camera
   rig's parent transform, not on the camera, so the camera can move without re-deriving rotation.
5. Size the view:
   - Orthographic: `orthographicSize` is **half the visible height in world units**. To show N world
     units of height, set it to `N / 2`.
   - For pixel-exact art: `orthographicSize = screenHeightInPixels / (2 * PPU)`, using the PPU from
     `design/art-bible.md`. A non-integer result is what makes 2.5D pixel art shimmer.
6. Set near and far clip planes tightly around the scene depth. An orthographic camera with a huge
   far plane wastes depth precision and causes sorting flicker between near-coplanar objects.
7. Build the rig as parent (angle, never animated) → child (position, follows the target). Follow in
   `LateUpdate` after the target has moved, or the camera lags one frame behind.
8. For camera motion use Cinemachine 3.x with the fixed rotation locked. `3d-cinemachine-camera`
   covers the rig; keep the angle constraint from this skill.
9. Hand the depth and draw-order consequences to `25d-sorting-and-depth` — an angled camera makes
   sorting the main source of visual bugs in 2.5D, and it is a separate problem from framing.
10. Verify:
    ```bash
    unity recompile --strict --format json
    ```
    then `qa-playmode-check` at the target resolution **and** one other aspect ratio. Confirm no
    shimmer when the camera moves, and nothing pops in front of anything it should be behind.

## Unity CLI commands used

```bash
unity status                              # live Editors: port, project path, version, PID
unity list                                # Editor-registered tools and their parameter schemas
unity commands --format json              # full CLI command manifest
unity recompile --strict --format json    # compile check
unity test --format json                  # PlayMode tests for follow behaviour
```

Camera and rig setup is Editor work: use the tools `unity list` reports, or an Editor script run
with `eval_file`. `script eval` compiles a statement block — fully-qualified names such as
`UnityEngine.Camera`, no `using` directives. See `PACK/references/unity-cli.md`.

## Files to read (exact paths)

| Need | Path |
| --- | --- |
| Project dimension | `design/STATE.md` |
| Design map | `design/INDEX.md` |
| PPU, art angle, resolution | `design/art-bible.md` |
| Recorded projection and renderer decision | `design/tech-decisions.md` |
| Renderer, tiers, clip and volume settings | `PACK/references/urp-settings.md` |
| Sorting consequences | the `25d-sorting-and-depth` skill |
| Camera rig motion | the `3d-cinemachine-camera` skill |
| Frame budget | `PACK/rules/performance.md` |

## Done checklist

- [ ] `design/STATE.md` says 2.5D.
- [ ] Universal Renderer on every quality tier; not the 2D Renderer.
- [ ] Projection chosen and recorded in `design/tech-decisions.md`.
- [ ] The camera angle is fixed, set on the rig parent, and does not drift.
- [ ] `orthographicSize` derived from the intended world height, or pixel-exact from PPU.
- [ ] Near and far clip planes are tight around actual scene depth.
- [ ] Follow logic runs in `LateUpdate`.
- [ ] Sorting and depth handled via `25d-sorting-and-depth`.
- [ ] Verified at the target resolution and one other aspect ratio, with no shimmer.

## Common mistakes

- Using the 2D Renderer because the game "looks 2D", then being unable to light any 3D mesh.
- Treating `orthographicSize` as the full visible height. It is **half** the height.
- A non-integer pixels-per-unit relationship, which makes pixel art shimmer whenever the camera
  moves — and no amount of filtering fixes it.
- Animating rotation on the camera itself, so the fixed angle slowly drifts and authored art stops
  matching the view.
- A far clip plane of 1000 on an orthographic camera, wasting depth precision and causing flicker
  between objects at similar depth.
- Following the target in `Update`, leaving the camera one frame behind and visibly juddering.
- Using perspective with a wide FOV, which distorts art at the screen edges that was authored for
  one angle.
- Fixing a sorting bug by nudging the camera. Sorting is a separate problem — use
  `25d-sorting-and-depth`.
