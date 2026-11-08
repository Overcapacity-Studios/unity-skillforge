# Art bible — <game name>

<!--
MANDATORY. No asset is generated, bought or imported without quoting this file.
Owned by the assets-art-style-lock skill. If a field below is still a placeholder,
the style is NOT locked and asset generation must stop and ask.
-->

**Status:** 🔴 not locked | 🟢 locked
**Updated:** YYYY-MM-DD

## Reference images

The style is defined by images, not adjectives. At least one is required to lock.

| Role | Path | What it fixes |
| --- | --- | --- |
| Primary reference | `art-source/reference/<file>.png` | Overall look, rendering, line, shading |
| Palette reference | `art-source/reference/<file>.png` | Colour relationships |
| Negative reference | `art-source/reference/<file>.png` | What to avoid |

Reference images live in `art-source/` at the repo root — **outside** `Assets/`, so Unity does not
import them.

## Style prompt

The exact text appended to every generation request. Changing it is a style change: bump the
"Updated" date and say so in `design/STATE.md`.

```
<One paragraph. Subject-neutral. Covers: medium, rendering, line treatment, shading model,
colour character, level of detail, lighting direction, mood. Example:
"flat vector illustration, thick uniform dark outlines, two-tone cel shading, warm muted palette,
no gradients, no texture noise, soft top-left light, readable at small size, friendly tone">
```

## Negative prompt

```
<What must never appear: e.g. "photorealistic, 3d render, gradients, drop shadows, text,
watermark, extra limbs, busy background">
```

## Palette

| Role | Hex | Used for |
| --- | --- | --- |
| Primary | `#______` | |
| Secondary | `#______` | |
| Accent | `#______` | Player, interactables — reserved, never decorative |
| Dark | `#______` | Outlines, shadow |
| Light | `#______` | Highlight, UI background |

Colour space is **Linear** (see `references/urp-settings.md`). Author hex values as sRGB.

## 2D specifications

| | |
| --- | --- |
| Pixels per unit (PPU) | <e.g. 32> — one value project-wide, never per-sprite |
| Sprite resolution | <e.g. character 32×32, prop 16×16> |
| Pivot | <e.g. Bottom-Center for characters> |
| Filter mode | Point (pixel art) / Bilinear (hi-res) |
| Compression | <e.g. None for pixel art, otherwise platform default> |
| Outline | <width in pixels, colour> |
| Animation frame rate | <e.g. 12 fps> |

## 3D specifications

| | |
| --- | --- |
| Scale | 1 unit = 1 metre; character height <e.g. 1.8> |
| Up axis / forward | Y up, +Z forward |
| Poly budget | <character / prop / environment> |
| LOD levels | <e.g. LOD0 100%, LOD1 50%, LOD2 25%> |
| Texture resolution | <e.g. 1024 character, 512 prop> |
| Material | URP Lit / Simple Lit / Unlit — <which and why> |
| Rig | <humanoid / generic; bone count limit> |

## Audio character

<Instrumentation, mood, whether SFX are organic or synthetic, loudness target. See
`assets-audio-sfx`.>

## Licensing and provenance

Every asset gets a row. This is the record that the project can ship commercially.

| Asset / set | Source | Licence | Commercial use confirmed | Date |
| --- | --- | --- | --- | --- |
| <Player sprites> | <provider / artist> | <licence> | yes / no | YYYY-MM-DD |

See `docs/ASSETS.md` for per-provider caveats.
