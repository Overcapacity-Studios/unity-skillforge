---
name: assets-gen-2d-sprite
description: Generate 2D sprites, tilesets or UI art with an image model, then hand them to slicing and import. Use when the project needs 2D art it does not have. Requires a locked art bible, and stays provider-agnostic so any image generator can be used.
metadata:
  version: 0.1.0
---

# Generate 2D sprites

Paths written as `PACK/` mean `.unity-skillforge/` in a game repo, or this pack's root.

## When to use

- The project needs a sprite, sprite sheet, tileset or UI element it does not have.
- Replacing placeholder art with something consistent.

Not for: importing existing art (`2d-sprite-import`), or 3D models (`assets-gen-3d-model`).

## Gate: the art bible must be locked

Read `design/art-bible.md` first. If its status is 🔴, or the style prompt, negative prompt, palette
or 2D specifications are placeholders, **stop and run `assets-art-style-lock`**. Generating against
an unlocked style produces a set that does not match itself and has to be redone.

## Provider

This skill is deliberately **provider-agnostic**: it defines the contract, not the tool. Use
whichever image model the user has available. Record which one was used, and its licence terms, in
the art bible's provenance table — see `PACK/docs/ASSETS.md` for per-provider caveats, especially
commercial-use rights and whether generated output can be copyrighted.

Never call a generation tool you have not confirmed is available in this session. If no image model
is available, say so plainly and offer the alternatives (placeholder art, an asset store, a human
artist) rather than inventing a provider.

## Inputs needed

- The subject list: exactly what sprites are needed and at what resolution.
- `design/art-bible.md`: style prompt, negative prompt, palette, PPU, sprite resolution, pivot,
  filter mode.
- Whether the output is a single sprite, a sheet of frames, or a tileset.

## Steps

1. Read `design/STATE.md`, `design/INDEX.md`, then `design/art-bible.md` in full.
2. Confirm the style is locked. If not, stop (see the gate above).
3. Build each request as **art bible style prompt + subject**, in that order, plus the negative
   prompt. Never write a fresh style description per asset — that is how a set drifts.
4. Request a **transparent background** where the asset is a sprite rather than a scene. Cutting a
   subject out of a generated background is lossy and shows at sprite scale.
5. Generate at the sprite resolution from the art bible, or an exact integer multiple of it.
   Downscaling by a non-integer factor destroys pixel art and softens edges on everything else.
6. For animation frames, generate the full set in **one request** where the model supports it, so
   frames share lighting and proportions. Frame-by-frame generation produces a set that jitters.
7. Save output to `art-source/generated/<subject>/` at the **repo root, outside `Assets/`**
   (`PACK/rules/folder-conventions.md`). Keep the original full-resolution output there — it is the
   master, and Unity must not import it.
8. Review before importing. Reject and regenerate rather than importing something off-style:
   - Does it match the reference image, not just the words?
   - Is the palette the art bible's palette?
   - Is the accent colour used only where the bible reserves it?
   - At the final on-screen size, is the subject readable?
   - Any watermark, text, extra limbs, or background fragments?
9. Copy approved output into `Assets/_Project/Art/Sprites/<Subject>/` and hand over to
   `2d-sprite-import` for PPU, pivot, filter, compression and atlas membership. **Do not set import
   settings here** — that skill owns them.
10. For a sheet, slice with `/unity:sprite-editor` or `PACK/scripts/slice-spritesheet.py` for a
    uniform grid, then animate with `2d-sprite-animation`.
11. Add a row to the art bible's **Licensing and provenance** table: asset set, provider, licence,
    commercial use confirmed, date. Then update `design/STATE.md` via `design-update-state`.

## Unity CLI commands used

Generation happens outside Unity. Once art is in the project:

```bash
unity status                              # live Editors: port, project path, version, PID
unity list                                # Editor-registered tools and their parameter schemas
unity recompile --strict --format json    # verify nothing broke after the import
```

Import settings are applied by `2d-sprite-import`, through the Editor tools `unity list` reports.
See `PACK/references/unity-cli.md`.

## Files to read (exact paths)

| Need | Path |
| --- | --- |
| Project status and dimension | `design/STATE.md` |
| Design map | `design/INDEX.md` |
| Style prompt, palette, 2D specs, provenance | `design/art-bible.md` |
| Provider licensing caveats | `PACK/docs/ASSETS.md` |
| Where generated masters live | `PACK/rules/folder-conventions.md` |
| Import settings owner | the `2d-sprite-import` skill |
| Slicing helper | `PACK/scripts/slice-spritesheet.py` |
| Animation next step | the `2d-sprite-animation` skill |

## Done checklist

- [ ] The art bible is 🟢 locked.
- [ ] Every request used the bible's style prompt verbatim, plus the negative prompt.
- [ ] Sprites were generated with a transparent background.
- [ ] Resolution is the bible's value or an exact integer multiple.
- [ ] Animation frames were generated as one set, not individually.
- [ ] Masters are in `art-source/generated/`, outside `Assets/`.
- [ ] Output was reviewed against the reference image, palette and readability, not just the prompt.
- [ ] No watermarks, text or background fragments.
- [ ] Import settings were left to `2d-sprite-import`.
- [ ] A provenance row records provider, licence, commercial-use confirmation and date.

## Common mistakes

- Writing a new style description per asset, so the set drifts and nothing matches.
- Generating without a transparent background and cutting the subject out afterwards.
- Non-integer downscaling, which softens every edge and ruins pixel art outright.
- Generating animation frames one at a time, producing a set that jitters between frames.
- Importing generated art into `Assets/` at full resolution and letting Unity carry the master.
- Judging output against the prompt text rather than the reference image.
- Setting import settings here, so they disagree with what `2d-sprite-import` would set.
- Using the accent colour decoratively because the generator liked it, breaking readability.
- Skipping the provenance row, leaving the project unable to prove its right to ship the art.
- Naming a provider or tool that is not actually available in the session.
