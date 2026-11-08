---
name: 25d-sorting-and-depth
description: Fix and control draw order in 2.5D and isometric scenes - sorting layers, transparency sort axis, isometric Z-as-Y, depth writing and sprite-versus-mesh ordering. Use when things draw in front of or behind what they should, or flicker as the camera moves.
metadata:
  version: 0.1.0
---

# Sorting and depth in 2.5D

Paths written as `PACK/` mean wherever this pack's shared files live: `.unity-skillforge/` in a
game repo (`install.sh`), the sibling `unity-skillforge-pack` folder (`npx skills add`), the
plugin's root directory (plugin install), or `skills/unity-skillforge-pack/` in this repo.

## When to use

- Something draws in front of or behind something it should not.
- Draw order flickers or swaps as the camera or a character moves.
- A character walks "through" a wall it should pass behind, or vice versa.
- Isometric tiles stack in the wrong order.

This is the most common source of visual bugs in 2.5D, and it is a different problem from framing
(`25d-ortho-3d-camera`) or orientation (`25d-billboard-sprites`).

## First: identify which ordering system applies

Unity has several, and they do not cooperate. Using the wrong one is why a fix "does nothing".

| Object kind | Ordered by | Notes |
| --- | --- | --- |
| Opaque mesh (depth-writing) | **Depth buffer** | Per-pixel and automatic. Sorting layers are ignored |
| Transparent mesh | Distance from camera, then render queue | No depth write, so it sorts per object |
| `SpriteRenderer` | Sorting layer → order in layer → **transparency sort axis** | Sorting layer always wins over order in layer |
| Alpha-clipped sprite on a lit quad | **Depth buffer**, like an opaque mesh | This is why clipping beats blending in 2.5D |
| UI (Canvas / UI Toolkit) | Its own hierarchy order | Independent of everything above |

**The key decision:** if sprites and 3D meshes must interleave correctly, make the sprites
depth-writing (alpha-clipped lit quads, per `25d-billboard-sprites`). Sorting layers cannot order a
sprite against an opaque mesh — the depth buffer decides, and a blended sprite is not in it.

## Inputs needed

- `design/STATE.md` dimension must be **2.5D** (or an isometric 2D project).
- The camera angle and projection from `design/tech-decisions.md`.
- Whether the grid is rectangular or isometric.

## Steps

1. Read `design/STATE.md`, `design/INDEX.md` and `design/tech-decisions.md`.
2. Classify the misordered objects using the table above. Fix the **system**, not the symptom — do
   not nudge positions to work around a sorting rule.
3. Set the **Transparency Sort Mode** and **Transparency Sort Axis** in Project Settings → Graphics
   (or per camera). For an angled 2.5D view, sprites must sort by depth along the view, not by
   distance to the camera:
   - Sort Mode: **Custom Axis**.
   - Sort Axis: `(0, 1, -1)` is the usual starting point for a camera angled down the +Z axis — it
     makes something further "up" the screen sort behind. Tune the Y and Z weights to match the
     actual camera angle.
   This single setting fixes most "characters behind the wrong wall" bugs, and nothing else does.
4. For isometric tilemaps, set the Tilemap's **Mode** to `Individual` and use **Z as Y**: increasing
   the tile's Z moves it up and sorts it correspondingly. Without Z-as-Y, stacked isometric tiles
   cannot order correctly no matter what layers you assign.
5. Define sorting layers once, project-wide, back to front — `Background`, `Ground`, `Entities`,
   `Foreground`, `UI` — and use them consistently. Remember **order in layer only breaks ties
   within the same sorting layer**; across layers, the layer always wins.
6. Never drive sorting by nudging Y or Z position by hand. If a character needs to sort by its feet,
   set the `SpriteRenderer`'s sorting order from its pivot position in one small system, or rely on
   the sort axis — not on scattered magic offsets.
7. Tighten near and far clip planes (`25d-ortho-3d-camera`). Flicker between two objects at nearly
   the same depth is depth-buffer precision, and a 1000-unit far plane on an orthographic camera is
   usually the cause.
8. Keep transparent objects to a minimum. Each one sorts per object, and two overlapping transparent
   objects at similar depth will swap order as the camera moves — there is no setting that fixes
   that, only making them depth-writing.
9. Verify:
   ```bash
   unity recompile --strict --format json
   ```
   then `qa-playmode-check`: walk a character all the way around and behind every tall object,
   moving the camera through its full range. Sorting bugs only appear at specific angles.

## Unity CLI commands used

```bash
unity status                              # live Editors: port, project path, version, PID
unity list                                # Editor-registered tools and their parameter schemas
unity commands --format json              # full CLI command manifest
unity recompile --strict --format json    # compile check
```

Graphics settings and sorting layers are project settings: change them through the tools `unity
list` reports, or an Editor script run with `eval_file`. Use fully-qualified names such as
`UnityEngine.Rendering.TransparencySortMode`. See `PACK/references/unity-cli.md`.

## Files to read (exact paths)

| Need | Path |
| --- | --- |
| Project dimension | `design/STATE.md` |
| Design map | `design/INDEX.md` |
| Camera angle and projection | `design/tech-decisions.md` |
| Camera and clip planes | the `25d-ortho-3d-camera` skill |
| Making sprites depth-writing | the `25d-billboard-sprites` skill |
| Tilemap layer stack | the `2d-tilemap-level` skill |
| Render queues, materials, alpha | `PACK/references/urp-settings.md` |
| Overdraw and transparency cost | `PACK/rules/performance.md` |

## Done checklist

- [ ] The ordering system in play was identified before anything was changed.
- [ ] Transparency Sort Mode is Custom Axis with an axis matched to the camera angle.
- [ ] Sprites that must interleave with meshes are depth-writing (alpha-clipped), not blended.
- [ ] Isometric tilemaps use Individual mode with Z as Y.
- [ ] Sorting layers are defined once project-wide and used consistently.
- [ ] No magic per-object Y or Z offsets are being used to force order.
- [ ] Near and far clip planes are tight; no depth flicker.
- [ ] Transparent object count is deliberate and minimal.
- [ ] Verified by circling a character around tall objects through the camera's full range.

## Common mistakes

- Setting sorting layers on a sprite and expecting it to order against an opaque mesh. The depth
  buffer decides that, and the sprite is not in it.
- Leaving Transparency Sort Mode on Default in an angled view, so sprites sort by camera distance
  and characters appear in front of walls they are behind.
- Isometric tiles without Z as Y, which cannot be ordered correctly by any layer assignment.
- Expecting order in layer to beat a sorting layer. It never does.
- Nudging positions by small amounts to fix order, which then breaks when the camera angle changes.
- Alpha-blended sprites that write no depth, swapping order as the camera moves — unfixable by
  settings alone.
- A 1000-unit far clip plane causing precision flicker, then blaming the sort axis.
- Testing sorting from one camera angle. Sorting bugs are angle-specific by nature.
