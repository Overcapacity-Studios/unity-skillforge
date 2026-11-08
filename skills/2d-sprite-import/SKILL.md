---
name: 2d-sprite-import
description: Import 2D sprites with this project's pinned settings - pixels per unit, pivot, filter mode, compression and atlas membership - so every sprite is consistent. Use when adding sprite art or fixing blurry, wrongly scaled or mis-pivoted sprites. Defer to Unity's sprite-editor for slicing.
metadata:
  version: 0.1.0
---

# Sprite import

Paths written as `PACK/` mean wherever this pack's shared files live: `.unity-skillforge/` in a
game repo (`install.sh`), the sibling `unity-skillforge-pack` folder (`npx skills add`), the
plugin's root directory (plugin install), or `skills/unity-skillforge-pack/` in this repo.

## When to use

- Adding new sprite art to the project.
- Sprites look blurry, are the wrong size on screen, or rotate around the wrong point.
- Setting up import settings for the first time on a project.

## Prefer the official skill

If Unity's official plugin is installed:

- `/unity:sprite-editor` — slicing a sheet into sprites, custom outlines, 9-slice.
- `/unity:manage-sprite-atlas` — Sprite Atlas creation and configuration.
- `/unity:2d-pixel-perfect` — the Pixel Perfect camera and crisp pixel-art rendering.

What stays ours: the **pinned import preset below** (PPU, pivot, filter, compression) and the folder
layout. Do not restate Unity's slicing procedure — link it. See
`PACK/references/official-unity-skills.md`.

## Inputs needed

- The source image(s), and whether each is a single sprite or a sheet.
- `design/art-bible.md` **2D specifications** — PPU, sprite resolution, pivot, filter mode,
  compression. If those fields are placeholders, the style is not locked: stop and run
  `assets-art-style-lock`.

## Steps

1. Read `design/STATE.md`, `design/INDEX.md`, then `design/art-bible.md` → 2D specifications.
2. Place the file per `PACK/rules/folder-conventions.md`:
   `Assets/_Project/Art/Sprites/<Subject>/`. A sheet is named `<Subject>_sheet.png`. Layered or
   full-resolution source art belongs in `art-source/` at the repo root, **outside** `Assets/`, so
   Unity never imports it.
3. Apply the pinned import settings. **One PPU for the whole project** — taken from the art bible,
   never per-sprite:
   | Setting | Value |
   | --- | --- |
   | Texture Type | Sprite (2D and UI) |
   | Sprite Mode | Single, or Multiple for a sheet |
   | Pixels Per Unit | the art bible value, identical for every sprite |
   | Pivot | the art bible value (commonly Bottom-Center for characters) |
   | Filter Mode | Point (no filter) for pixel art; Bilinear otherwise |
   | Compression | None for pixel art; platform default otherwise |
   | Generate Mip Maps | **off** for 2D |
   | Max Size | at least the source's largest dimension, or it is silently downscaled |
   | sRGB (Color Texture) | on — the project is Linear colour space |
4. For a sheet, hand slicing to `/unity:sprite-editor`, or use
   `PACK/scripts/slice-spritesheet.py` for a uniform grid. Sliced sprites are named
   `<sheet>_<index>`.
5. Add the sprites to a Sprite Atlas per subject. **Unatlased sprites are one draw call each**
   (`PACK/rules/performance.md`). Atlas configuration is `/unity:manage-sprite-atlas`.
6. Verify the on-screen size is what the design expects: a 32px sprite at PPU 32 is exactly 1 world
   unit. If a sprite is the wrong size, fix the art or the PPU — never the Transform scale. A scaled
   Transform breaks physics, pivots and tiling.
7. Reimport and verify:
   ```bash
   unity recompile --strict --format json
   ```
   then check the sprite in a scene via `qa-playmode-check`.
8. Record the asset and its licence in `design/art-bible.md` → Licensing and provenance.

## Unity CLI commands used

```bash
unity status                              # live Editors: port, project path, version, PID
unity list                                # Editor-registered tools and their parameter schemas
unity commands --format json              # full CLI command manifest
unity assets import <file>                # import a .unitypackage of art
unity recompile --strict --format json    # verify nothing broke
```

Import settings live in the asset's `.meta` file. Change them through the Editor tools reported by
`unity list`, or an Editor script run with `eval_file` — never by hand-editing `.meta`, which
desynchronises the asset database. See `PACK/references/unity-cli.md`.

## Files to read (exact paths)

| Need | Path |
| --- | --- |
| Project status | `design/STATE.md` |
| Design map | `design/INDEX.md` |
| PPU, pivot, filter, compression | `design/art-bible.md` |
| Official slicing and atlas skills | `PACK/references/official-unity-skills.md` |
| Art folder layout and naming | `PACK/rules/folder-conventions.md` |
| Draw-call and overdraw rules | `PACK/rules/performance.md` |
| Colour space | `PACK/references/urp-settings.md` |
| Grid slicing helper | `PACK/scripts/slice-spritesheet.py` |

## Done checklist

- [ ] The art bible's 2D specifications are filled in, not placeholders.
- [ ] File is under `Assets/_Project/Art/Sprites/<Subject>/` with the naming convention.
- [ ] Source art is in `art-source/`, outside `Assets/`.
- [ ] PPU matches the project value exactly — no per-sprite PPU.
- [ ] Filter Mode and Compression match the art bible (Point and None for pixel art).
- [ ] Mip maps are off; Max Size is not downscaling the source.
- [ ] Pivot matches the art bible.
- [ ] Sprites belong to a Sprite Atlas.
- [ ] On-screen size is correct with Transform scale at 1,1,1.
- [ ] Licence recorded in `design/art-bible.md`.

## Common mistakes

- A different PPU per sprite, so everything is subtly the wrong relative size and nothing lines up.
- Fixing a size problem with Transform scale, which then breaks colliders, pivots and tiling.
- Leaving Filter Mode on Bilinear for pixel art, giving permanently blurry sprites.
- Compressing pixel art, producing colour artefacts that no later setting recovers.
- Mip maps left on for 2D, so sprites blur at distance for no benefit.
- Max Size below the source resolution, silently downscaling the art.
- Hand-editing a `.meta` file and desynchronising the asset database.
- Importing layered source art into `Assets/`, bloating import time and the repo.
- Shipping unatlased sprites and wondering where the draw calls came from.
