---
name: 2d-lighting
description: Light a 2D scene with URP's 2D Renderer - Light2D types, blend styles, normal maps and shadow casters. Use when adding 2D lighting or fixing sprites that render black, unlit or washed out after enabling lights. Requires the 2D Renderer, which excludes 3D meshes.
metadata:
  version: 0.1.0
---

# 2D lighting

Paths written as `PACK/` mean `.unity-skillforge/` in a game repo, or this pack's root.

## When to use

- Adding lighting to a 2D scene.
- Sprites went black, flat or washed out after lights were introduced.
- Setting up the 2D Renderer on a project for the first time.

## Decide this first: 2D Renderer or not

`Light2D` requires URP's **2D Renderer**. The 2D Renderer **cannot light 3D meshes**.

| Project dimension | Renderer | 2D lighting |
| --- | --- | --- |
| 2D | 2D Renderer | Yes — this skill |
| 2.5D | Universal Renderer | **No** — sprites live in a 3D scene; use `3d-urp-lighting` |
| 3D | Universal Renderer | No — `3d-urp-lighting` |

If `design/STATE.md` says 2.5D, stop and use `3d-urp-lighting` instead. Switching renderer later
invalidates lighting work, so confirm the dimension before starting
(`PACK/references/urp-settings.md`).

## Inputs needed

- The project dimension from `design/STATE.md`.
- The mood and lighting direction from `design/art-bible.md`.
- Whether sprites have normal maps authored (they usually do not).

## Steps

1. Read `design/STATE.md` (confirm 2D), `design/INDEX.md`, then `design/art-bible.md` for mood,
   palette and light direction.
2. Confirm the URP Asset for **every quality tier** uses a 2D Renderer. A tier pointing at a
   Universal Renderer, or at `None`, renders that tier wrong and only that tier
   (`PACK/references/urp-settings.md`).
3. Add a **Global Light 2D** first and set the scene's base brightness with it. Without one, every
   sprite outside a light's radius renders black — which is the usual cause of "my sprites
   disappeared".
4. Add local lights by type:
   | Type | Use |
   | --- | --- |
   | Global | Scene ambient. Exactly one per blend style |
   | Point / Spot | Lamps, torches, muzzle flashes |
   | Freeform | Hand-shaped pools of light |
   | Sprite | Light shaped by a sprite's alpha |
5. Configure **Blend Styles** in the 2D Renderer Data asset before assigning lights to them. There
   are a limited number of blend style slots, they are shared project-wide, and renaming one
   silently changes every light using it.
6. Set each light's **Target Sorting Layers** deliberately. A light that targets every layer will
   light the background and the UI-adjacent foreground along with the gameplay layer.
7. Only enable **Normal Map** quality on a light if the sprites actually have normal maps assigned
   in their Secondary Textures. Enabling it without them costs performance and changes nothing.
8. For shadows, add `ShadowCaster2D` to the casting sprites and enable shadows on the light. Each
   shadow-casting light is an extra render pass over everything it touches — budget them per
   `PACK/rules/performance.md`.
9. Keep HDR off for pixel art unless bloom is explicitly in the art bible; and set tonemapping once
   on the global Volume rather than per scene.
10. Verify across quality tiers and in a build, not just the Editor:
    ```bash
    unity recompile --strict --format json
    ```
    then `qa-playmode-check`, then `qa-build` if the look matters for release.

## Unity CLI commands used

```bash
unity status                              # live Editors: port, project path, version, PID
unity list                                # Editor-registered tools and their parameter schemas
unity commands --format json              # full CLI command manifest
unity recompile --strict --format json    # compile check
```

Light and renderer asset configuration is Editor work: use the tools `unity list` reports, or an
Editor script run with `eval_file`. Use fully-qualified names such as
`UnityEngine.Rendering.Universal.Light2D`. See `PACK/references/unity-cli.md`.

## Files to read (exact paths)

| Need | Path |
| --- | --- |
| Project dimension | `design/STATE.md` |
| Design map | `design/INDEX.md` |
| Mood, palette, light direction | `design/art-bible.md` |
| Renderer choice, tiers, volumes, colour space | `PACK/references/urp-settings.md` |
| Recorded renderer decision | `design/tech-decisions.md` |
| Shadow and overdraw budgets | `PACK/rules/performance.md` |
| 3D or 2.5D lighting instead | `PACK/skills/3d-urp-lighting/SKILL.md` |

## Done checklist

- [ ] The project is genuinely 2D; 2.5D went to `3d-urp-lighting`.
- [ ] Every quality tier's URP Asset uses a 2D Renderer.
- [ ] Exactly one Global Light 2D sets the base brightness.
- [ ] Blend styles were configured in the Renderer Data before lights were assigned to them.
- [ ] Each light's Target Sorting Layers are set deliberately, not left as all layers.
- [ ] Normal map quality is on only where normal maps actually exist.
- [ ] Shadow-casting lights are counted against the performance budget.
- [ ] HDR and tonemapping match the art bible.
- [ ] Verified on more than one quality tier and in a build.

## Common mistakes

- No global light, so every sprite outside a light radius is black and the art looks deleted.
- Using `Light2D` with the Universal Renderer, where it does nothing at all.
- Using the 2D Renderer in a 2.5D project, then finding 3D meshes cannot be lit.
- Assigning lights to a blend style before configuring it, then renaming the style and changing
  every light at once.
- Lights targeting all sorting layers, washing out background and foreground together.
- Normal map quality enabled with no normal maps, paying the cost for no visual change.
- Many shadow-casting lights, each adding a full render pass, then blaming the sprite count.
- Lighting one quality tier and shipping another, so the build looks nothing like the Editor.
