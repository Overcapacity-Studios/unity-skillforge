# URP — pinned settings

Package: `com.unity.render-pipelines.universal`. Pin the exact version in `Packages/manifest.json`.
URP is mandatory for every project in this pack; see `references/unity-versions.md`.

## Asset layout

```
Assets/Settings/Rendering/
  URP-Performant.asset          # URP Asset (low/mobile quality tier)
  URP-Balanced.asset            # URP Asset (default tier)
  URP-HighFidelity.asset        # URP Asset (high tier)
  URP-*-Renderer.asset          # one Renderer Data per URP Asset
  Volumes/Global.asset          # Volume Profile for the global volume
```

Assign the tiers under Project Settings → Quality, and set Graphics → Default Render Pipeline to the
balanced asset. Do not leave a quality tier pointing at `None` — it silently falls back to Built-in.

## Renderer choice

| Project type | Renderer | Notes |
| --- | --- | --- |
| 2D | **2D Renderer** | Required for `Light2D`; see `skills/2d-lighting` |
| 2.5D | **Universal Renderer**, Forward | Sprites live in a 3D scene; the 2D Renderer cannot light meshes |
| 3D | **Universal Renderer** | Forward+ when you need many real-time lights; Deferred for heavy static lighting |

Changing the renderer after lighting work invalidates bakes. Decide in `design/tech-decisions.md`
before building scenes.

## Settings we always set explicitly

- **Color space: Linear** (Project Settings → Player). Gamma breaks lighting maths and is not
  recoverable later without redoing art.
- **HDR**: on for 3D and 2.5D; off for 2D pixel art unless bloom is in the art bible.
- **MSAA**: off when post-processing is in use (it costs resolve bandwidth and post needs a
  resolved target anyway); prefer SMAA in the Volume for 3D.
- **Shadow cascades**: 1 for 2.5D and small 3D scenes; 2–4 only for open scenes. Each cascade is a
  full extra shadow render.
- **Depth Texture / Opaque Texture**: leave **off** unless a shader needs them. Turning both on is a
  common silent cost.
- **Render Scale**: 1.0. Use it as a performance dial, never as a default.
- **SRP Batcher**: on. Verify in the Frame Debugger that batches are actually merging.

## Materials

- URP Lit / Simple Lit / Unlit only. A Built-in RP `Standard` material renders magenta in URP.
- Imported models arrive with Built-in materials: convert them in `assets-import-pipeline`, do not
  hand-assign one at a time.
- Share materials; vary via `MaterialPropertyBlock` or shader keywords. A per-instance material
  clone breaks SRP batching.

## Volumes and post-processing

- Exactly one **global** Volume per scene, profile at `Assets/Settings/Rendering/Volumes/Global.asset`.
- Local volumes use a trigger collider and a blend distance; never set a local volume to Global.
- Tonemapping (Neutral or ACES) goes on the global profile, chosen once in `design/art-bible.md`.
- For deeper post-processing work, Unity's official `/unity:urp-postprocessing` skill is
  authoritative — see `references/official-unity-skills.md`.

## Common mistakes

- A scene lit beautifully under one quality tier and black under another, because only one tier was
  assigned a URP Asset.
- Bloom and heavy post added before tonemapping is set, so every later art decision is re-tuned.
- Enabling Forward+ and then wondering why mobile frame time collapsed.
- Baking lighting, then switching renderer or color space, and silently shipping stale lightmaps.
