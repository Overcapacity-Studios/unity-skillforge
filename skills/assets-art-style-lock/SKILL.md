---
name: assets-art-style-lock
description: Create or read the art bible that locks a project's visual style - reference images, a reusable style prompt, palette and per-dimension asset specs. Use before generating, buying or importing any asset. Every asset request must quote this file, and an unlocked style blocks asset work.
metadata:
  version: 0.1.0
---

# Art style lock

Paths written as `PACK/` mean wherever this pack's shared files live: `.unity-skillforge/` in a
game repo (`install.sh`), the sibling `unity-skillforge-pack` folder (`npx skills add`), the
plugin's root directory (plugin install), or `skills/unity-skillforge-pack/` in this repo.

## When to use

- Before the first asset of a project is generated, bought or imported.
- Any asset request where `design/art-bible.md` is missing or still has placeholder fields.
- The art has drifted: new assets do not look like older ones.

**This is a gate.** `assets-gen-2d-sprite`, `assets-gen-3d-model` and `assets-import-pipeline` all
refuse to proceed on an unlocked style, because an unlocked style means every asset is a different
guess and the set has to be regenerated.

## Inputs needed

- At least one **reference image**. A style cannot be locked with adjectives alone — "stylised
  fantasy" produces a different result every time it is read.
- The project dimension from `design/STATE.md`, which decides whether the 2D or 3D spec block must
  be filled.
- The pitch's mood and audience from `design/pitch.md`.

## Steps

1. Read `design/STATE.md`, `design/INDEX.md` and `design/pitch.md`.
2. If `design/art-bible.md` does not exist, copy
   `PACK/templates/game-design/art-bible.md` to `design/art-bible.md` and add a row for it in
   `design/INDEX.md`.
3. Collect reference images into `art-source/reference/` at the **repo root, outside `Assets/`** so
   Unity never imports them (`PACK/rules/folder-conventions.md`). Fill the reference table with at
   least a primary reference, and ideally a palette reference and a negative reference.
4. Write the **style prompt**: one paragraph, subject-neutral, covering medium, rendering, line
   treatment, shading model, colour character, detail level, lighting direction and mood. It must be
   reusable verbatim for any subject. If it mentions a specific subject, it is not a style prompt.
5. Write the **negative prompt**: what must never appear. Include the practical ones — watermark,
   text, extra limbs, busy background — plus the stylistic opposites of the chosen look.
6. Fill the palette table with hex values and a stated role for each. Reserve the accent colour for
   the player and interactables; a decorative accent destroys readability. Author hex as sRGB; the
   project renders in Linear (`PACK/references/urp-settings.md`).
7. Fill the spec block for the project dimension — and leave the other one empty rather than
   guessing:
   - **2D / 2.5D sprites:** PPU (one value project-wide), sprite resolutions, pivot, filter mode,
     compression, outline, animation frame rate. These feed `2d-sprite-import` directly.
   - **3D:** scale (1 unit = 1 metre), up axis and forward, poly budgets, LOD levels, texture
     resolutions, material type, rig type. These feed `assets-import-pipeline`.
8. Write the audio character line, which `assets-audio-sfx` reads.
9. Set up the **Licensing and provenance** table. Every asset added to the project gets a row with
   source, licence, whether commercial use is confirmed, and the date. This table is the record that
   the project can legally ship — see `docs/ASSETS.md` for per-provider caveats.
10. Set the status to 🟢 locked **only** when there is at least one reference image, a subject-neutral
    style prompt, a negative prompt, a filled palette, and the spec block for the project's
    dimension. Otherwise leave it 🔴 and say what is missing.
11. Note the lock in `design/STATE.md` via `design-update-state`. Changing the style prompt later is
    a style change: bump the date and say so, because existing assets will no longer match.

## Unity CLI commands used

None. This skill writes design documents only and does not touch the Unity Editor. If you need to
check the project's current colour space or PPU to fill the spec block, read it back:

```bash
unity status                   # confirm an Editor is reachable
unity list                     # Editor-registered tools and their parameter schemas
```

See `PACK/references/unity-cli.md`.

## Files to read (exact paths)

| Need | Path |
| --- | --- |
| Project status and dimension | `design/STATE.md` |
| Design map | `design/INDEX.md` |
| Mood, audience, pillars | `design/pitch.md` |
| The file being created | `design/art-bible.md` |
| Template to copy | `PACK/templates/game-design/art-bible.md` |
| Where reference images go | `PACK/rules/folder-conventions.md` |
| Colour space and material types | `PACK/references/urp-settings.md` |
| Provider licensing caveats | `PACK/references/asset-licensing.md` |

## Done checklist

- [ ] `design/art-bible.md` exists and has a row in `design/INDEX.md`.
- [ ] At least one reference image, stored in `art-source/reference/` outside `Assets/`.
- [ ] The style prompt is subject-neutral and reusable verbatim.
- [ ] A negative prompt exists.
- [ ] The palette table has hex values and a stated role for each, with the accent reserved.
- [ ] The spec block for the project's dimension is complete; the other is left empty.
- [ ] One project-wide PPU is stated (2D / 2.5D projects).
- [ ] The audio character line is filled.
- [ ] The licensing and provenance table exists.
- [ ] Status is 🟢 only if every item above holds; otherwise what is missing is stated.

## Common mistakes

- Locking the style with adjectives and no reference image, so every generation is a new guess.
- A style prompt that names a subject, making it unusable for the next asset.
- No negative prompt, so watermarks, text and busy backgrounds keep appearing.
- Per-sprite PPU instead of one project value, so nothing is the right relative size.
- Leaving spec fields as placeholders and generating anyway — the set then has to be redone.
- Using the accent colour decoratively, so the player can no longer be picked out at a glance.
- Filling in both the 2D and 3D blocks for a project that is one or the other, leaving later agents
  unsure which applies.
- Changing the style prompt without saying so, so old and new assets quietly stop matching.
- Skipping the licensing table, leaving the project unable to prove it can ship commercially.
