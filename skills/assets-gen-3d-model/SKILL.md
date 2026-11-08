---
name: assets-gen-3d-model
description: Generate, retexture, rig and animate 3D models through the Meshy MCP server, then hand the download to the import pipeline. Use when a 3D project needs a model it does not have. Requires a locked art bible and a paid Meshy plan, and generation is asynchronous.
metadata:
  version: 0.1.0
---

# Generate 3D models

Paths written as `PACK/` mean wherever this pack's own files live: `.unity-skillforge/` in a game
repo (created by `install.sh`), the plugin's root directory when installed as a plugin, or the
repo root when working on the pack itself.

## When to use

- A 3D or 2.5D project needs a character, prop or environment mesh it does not have.
- Retexturing, remeshing, rigging or animating an existing model.

Not for: importing a model already on disk (`assets-import-pipeline`), or 2D art
(`assets-gen-2d-sprite`).

## Gate: the art bible must be locked

Read `design/art-bible.md`. If its status is 🔴, or the style prompt, negative prompt or **3D
specifications** are placeholders, **stop and run `assets-art-style-lock`**. Generating against an
unlocked style produces a set that does not match and has to be redone — and 3D generation costs
real credits per attempt.

## Provider: Meshy MCP

The documented primary path is the Meshy MCP server. **Tool names are exact** — snake_case with a
`meshy_` prefix. The full verified list is in `PACK/references/meshy-mcp-tools.md`; do not invent
variants.

Requires a paid **Meshy Pro or higher** plan. Before any batch, confirm the server is actually
connected in this session and check the balance with `meshy_check_balance`. If it is not available,
say so and offer alternatives (asset store, a human artist, placeholder primitives) rather than
naming a provider you cannot reach.

## Inputs needed

- The subject list and how many models are needed.
- `design/art-bible.md`: style prompt, negative prompt, and the **3D specifications** — scale, up
  axis and forward, poly budget, LOD levels, texture resolution, material type, rig type.
- Whether each model needs rigging and animation, or is a static prop.

## Steps

1. Read `design/STATE.md`, `design/INDEX.md`, then `design/art-bible.md` in full.
2. Confirm the style is locked and the 3D spec block is filled. If not, stop.
3. Confirm the provider and the budget before spending:
   - The Meshy MCP tools are listed in this session.
   - `meshy_check_balance` — report the balance and the expected cost to the user **before**
     generating a set.
4. Generate, using the art bible style prompt verbatim plus the subject, and the negative prompt:
   - Text to mesh → `meshy_text_to_3d`, then `meshy_text_to_3d_refine` for the detailed pass.
   - From concept art → `meshy_image_to_3d`, or `meshy_multi_image_to_3d` for several views. If
     concept art exists, prefer this: it holds style far better than text alone.
5. **Generation is asynchronous.** Each call returns a task. Poll `meshy_get_task_status` until it
   completes, and only then download. Never assume a result is ready, and do not start a dependent
   step before the previous one has completed.
6. Only then refine the mesh, in this order, and only as needed:
   - `meshy_remesh` to hit the poly budget from the art bible.
   - `meshy_uv_unwrap` if UVs are unusable.
   - `meshy_retexture` to bring an off-style texture onto the bible's palette.
7. Rig and animate **only what moves**. For a static prop, stop at the mesh — rigging adds cost and
   constrains the skeleton:
   - `meshy_rig` → then `meshy_animate`, or `meshy_text_to_motion` for a described motion.
   - `meshy_list_animations` to see what is available before requesting a new one.
8. Download with `meshy_download_model` into `art-source/generated/<subject>/` at the **repo root,
   outside `Assets/`**. That file is the master; Unity must not import it from there.
9. Review before importing, and regenerate rather than importing something off-style: silhouette
   readable at gameplay distance, palette matching the bible, poly count within budget, no holes or
   inverted normals, and a skeleton that matches the rig type the project expects.
10. Hand the downloaded file to **`assets-import-pipeline`** for scale, axis conversion, LODs, URP
    material conversion and rig remapping. **Do not set import settings here** — that skill owns
    them. A raw download dropped into `Assets/` is not a finished asset.
11. Add a row to the art bible's **Licensing and provenance** table: asset, provider, licence,
    commercial use confirmed, date. Commercial rights depend on the user's Meshy plan, so confirm
    rather than assume — see `PACK/docs/ASSETS.md`. Then `design-update-state`.

## Unity CLI commands used

Generation happens outside Unity. Once the model is handed over:

```bash
unity status                              # live Editors: port, project path, version, PID
unity list                                # Editor-registered tools and their parameter schemas
unity recompile --strict --format json    # verify nothing broke after the import
```

Import settings are applied by `assets-import-pipeline`. See `PACK/references/unity-cli.md`.

## Files to read (exact paths)

| Need | Path |
| --- | --- |
| Project status and dimension | `design/STATE.md` |
| Design map | `design/INDEX.md` |
| Style prompt, 3D specs, provenance | `design/art-bible.md` |
| Exact Meshy tool names and working rules | `PACK/references/meshy-mcp-tools.md` |
| Provider licensing caveats | `PACK/docs/ASSETS.md` |
| Where generated masters live | `PACK/rules/folder-conventions.md` |
| Import settings owner | the `assets-import-pipeline` skill |
| Poly and LOD budgets | `PACK/rules/performance.md` |

## Done checklist

- [ ] The art bible is 🟢 locked and its 3D specifications are filled.
- [ ] The Meshy MCP server was confirmed available in this session.
- [ ] `meshy_check_balance` was run and the cost reported to the user before generating.
- [ ] Every request used the bible's style prompt verbatim, plus the negative prompt.
- [ ] Each async task was polled with `meshy_get_task_status` before the next step.
- [ ] Poly count is within the art bible budget.
- [ ] Rigging and animation were applied only to models that move.
- [ ] Masters are in `art-source/generated/`, outside `Assets/`.
- [ ] Output was reviewed for silhouette, palette, holes and normals before import.
- [ ] Import settings were left to `assets-import-pipeline`.
- [ ] A provenance row records provider, licence, commercial-use confirmation and date.

## Common mistakes

- Inventing a tool name. The names are exact and `meshy_`-prefixed; use
  `PACK/references/meshy-mcp-tools.md`.
- Downloading before `meshy_get_task_status` reports completion, and getting a partial or missing
  result.
- Generating a batch without checking the balance, spending the user's credits unannounced.
- Writing a fresh style description per model, so the set drifts.
- Using text-to-3D when concept art exists; image-to-3D holds style far better.
- Rigging static props, paying cost and locking in a skeleton nobody needs.
- Dropping the raw download into `Assets/` and calling it done — wrong scale, wrong axis, Built-in
  materials that render magenta in URP.
- Setting import settings here, so they disagree with `assets-import-pipeline`.
- Assuming commercial rights. They depend on the user's plan; confirm and record it.
- Generating before the poly budget exists, then remeshing the whole set afterwards.
