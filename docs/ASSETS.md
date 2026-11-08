# Assets: providers, pipelines and licensing

The full reference now lives with the pack's other skill-read data, because the asset skills read it
at runtime rather than only humans reading it:

**[`skills/unity-skillforge-pack/references/asset-licensing.md`](../skills/unity-skillforge-pack/references/asset-licensing.md)**

After an install it is at `.unity-skillforge/references/asset-licensing.md`, or
`unity-skillforge-pack/references/asset-licensing.md` next to the skills if you installed with
`npx skills`.

## The short version

- **Nothing is generated without a locked `design/art-bible.md`.** The generation skills stop if it
  is not locked, because an unlocked style means every asset is a fresh guess and the set has to be
  redone — which for 3D costs real credits twice.
- **Prototypes are the exception, and need no lock.** Unity primitives, flat materials, blockout
  geometry and debug visuals, in `Assets/_Project/Prototype/` with a `PH_` prefix, listed in the
  prototype doc. Nothing is generated for a prototype — a capsule is free — so the gate on
  generated art is untouched.
- **2D:** any image model → `assets-gen-2d-sprite` → `2d-sprite-import` (PPU, pivot, filter) →
  `2d-sprite-animation`. Masters stay in `art-source/`, outside `Assets/`.
- **3D:** Meshy MCP → `assets-gen-3d-model` → `assets-import-pipeline` (scale, axis, LODs, URP
  materials, Avatar retargeting). A raw download is never a finished asset.
- **Cost:** Meshy needs a paid Pro or higher plan and spends credits per generation. Everything else
  here is free.
- **Licensing:** record every asset's source, licence and whether commercial use is confirmed in the
  art bible's provenance table. In the US, purely AI-generated images are generally **not
  copyrightable** — you may be able to use one and still be unable to stop others from doing so.
  Confirm terms with the provider; none of this is legal advice.

The full reference covers each pipeline step, the per-provider questions to ask, and what the
provenance table must record before a project can ship commercially.
