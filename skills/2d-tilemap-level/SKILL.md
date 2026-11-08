---
name: 2d-tilemap-level
description: Build a 2D tilemap level with this project's grid, layer and chunk conventions - tilemap layers, collision, sorting and level folder layout. Use when creating or editing a tile-based level. Defer to Unity's create-tile-palette-or-rule-tiles skill for palettes and rule tiles.
metadata:
  version: 0.1.0
---

# Tilemap level

Paths written as `PACK/` mean wherever this pack's shared files live: `.unity-skillforge/` in a
game repo (`install.sh`), the sibling `unity-skillforge-pack` folder (`npx skills add`), the
plugin's root directory (plugin install), or `skills/unity-skillforge-pack/` in this repo.

## When to use

- Creating a new tile-based level or editing an existing one.
- Setting up the tilemap layer stack on a project for the first time.
- Fixing tile collision, or tiles drawing in front of or behind the player incorrectly.

## Prefer the official skill

If Unity's official plugin is installed:

- `/unity:create-tile-palette-or-rule-tiles` — creating Tile Palettes, Rule Tiles and tile assets.
  This is the authoritative procedure; run it for anything palette- or rule-tile-shaped.

What stays ours: the **layer stack, grid convention, collision setup and level folder layout**
below. Do not restate Unity's palette procedure — link it. See
`PACK/references/official-unity-skills.md`.

## Inputs needed

- The level's design: from `design/levels.md` if `design/INDEX.md` lists it, otherwise the mechanic
  spec driving it.
- Tile art, already imported with the project PPU via `2d-sprite-import`.
- Grid type: rectangular, isometric or hexagonal. Isometric changes sorting — see
  `25d-sorting-and-depth`.

## Steps

1. Read `design/STATE.md`, `design/INDEX.md`, then the level or mechanic doc it names.
2. Confirm tile art is imported at the project PPU. A tile whose PPU differs from the grid size
   leaves seams that no amount of tilemap tweaking fixes — fix the import first.
3. Create the Grid with cell size `1, 1, 0` for rectangular. The grid cell is **one world unit**;
   the PPU makes the art fit it. Never compensate with a scaled Grid transform.
4. Build the standard layer stack, each a child Tilemap of the Grid, ordered back to front:
   | Tilemap | Sorting layer | Collider |
   | --- | --- | --- |
   | `Background` | `Background` | none |
   | `Ground` | `Ground` | `TilemapCollider2D`, used by physics |
   | `Decoration` | `Ground` (higher order) | none |
   | `Foreground` | `Foreground` | none |
   Sorting layers are project-wide; define them once and reuse. Never rely on `Order in Layer` alone
   across different layers.
5. Add collision to `Ground` only: `TilemapCollider2D` plus a `CompositeCollider2D` on the same
   object with the Tilemap collider set to **Used By Composite**. Without the composite, every tile
   is a separate collider and a character catches on the seams between them.
6. Match the physics system actually in use. **Unity 6 has two incompatible 2D physics systems** —
   check which before adding any collider, per `2d-physics-setup` and
   `PACK/references/unity-versions.md`.
7. Save the level as a prefab or scene per `PACK/rules/folder-conventions.md`:
   `Assets/_Project/Scenes/Gameplay/<LevelName>.unity`, with tile assets under
   `Assets/_Project/Art/Sprites/Tiles/`.
8. Keep levels chunked. One enormous tilemap is slow to edit and to cull; split large levels into
   additively loaded scenes per `core-scene-setup`.
9. Verify in play mode — the character walks on the ground, does not catch on seams, and nothing
   draws in the wrong order:
   ```bash
   unity recompile --strict --format json
   ```
   then `qa-playmode-check`.

## Unity CLI commands used

```bash
unity status                              # live Editors: port, project path, version, PID
unity list                                # Editor-registered tools and their parameter schemas
unity commands --format json              # full CLI command manifest
unity recompile --strict --format json    # verify nothing broke
unity test --format json                  # PlayMode tests for traversal
```

Tilemap authoring is Editor work: use the tools `unity list` reports, or an Editor script run with
`eval_file`. `script eval` compiles a statement block — no `using` directives, fully-qualified types
such as `UnityEngine.Tilemaps.Tilemap`. See `PACK/references/unity-cli.md`.

## Files to read (exact paths)

| Need | Path |
| --- | --- |
| Project status and dimension | `design/STATE.md` |
| Design map | `design/INDEX.md` |
| Level layout | `design/levels.md` |
| Tile art specs and PPU | `design/art-bible.md` |
| Official palette and rule-tile skill | `PACK/references/official-unity-skills.md` |
| Which 2D physics system this project uses | `PACK/references/unity-versions.md` |
| Scene, prefab and art folder layout | `PACK/rules/folder-conventions.md` |
| Culling and draw-call rules | `PACK/rules/performance.md` |

## Done checklist

- [ ] Tile art is imported at the project PPU, with no seams.
- [ ] Grid cell size is `1, 1, 0` and the Grid transform is unscaled.
- [ ] The layer stack exists with the sorting layers above, defined project-wide.
- [ ] Collision is on `Ground` only, with `CompositeCollider2D` and Used By Composite set.
- [ ] The collider type matches the 2D physics system the project actually uses.
- [ ] Level and tile assets are in the folders named above.
- [ ] Large levels are chunked into additive scenes, not one giant tilemap.
- [ ] Verified in play mode: traversal is smooth and draw order is correct.

## Common mistakes

- Tile art at a PPU that does not match the grid, leaving one-pixel seams between every tile.
- Scaling the Grid transform to make mismatched art fit, which breaks tile coordinates and physics.
- `TilemapCollider2D` with no `CompositeCollider2D`, so the character catches on every tile seam.
- Adding colliders to the decoration or foreground layer, so the player collides with scenery.
- Relying on `Order in Layer` across different sorting layers, where the layer always wins.
- Mixing legacy `Collider2D` with 2D Physics Core components — they share no code and never
  interact, so the result compiles, runs and does nothing.
- One enormous tilemap, which is slow to edit and cannot be culled.
- Building the level before the mechanic is spec'd, so the layout does not fit the movement.
