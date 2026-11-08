---
name: assets-import-pipeline
description: Import an external 3D model or texture into Unity correctly - scale and axis conversion, LODs, Built-in to URP material conversion, and rig remapping. Use after downloading a generated or purchased model. A raw file dropped into Assets is not a finished asset.
metadata:
  version: 0.1.0
---

# Import pipeline

Paths written as `PACK/` mean wherever this pack's shared files live: `.unity-skillforge/` in a
game repo (`install.sh`), the sibling `unity-skillforge-pack` folder (`npx skills add`), the
plugin's root directory (plugin install), or `skills/unity-skillforge-pack/` in this repo.

## When to use

- A generated model from `assets-gen-3d-model` needs importing.
- A purchased or downloaded model, texture or animation needs importing.
- An imported model is the wrong size, faces the wrong way, renders magenta, or its animation does
  not play on the project's character.

This skill exists because **nothing official or third-party owns this handoff.** Meshy's own skills
contain no Unity import guidance, and Unity's asset skills assume the asset is already correct.

## Inputs needed

- The file to import, and where it came from.
- `design/art-bible.md` **3D specifications**: scale, up axis and forward, poly budget, LOD levels,
  texture resolution, material type, rig type.
- Whether the model needs to animate using the project's existing rig.

## Steps

1. Read `design/STATE.md`, `design/INDEX.md`, then `design/art-bible.md` → 3D specifications.
2. Put the source file under `Assets/_Project/Art/Models/<Subject>/`
   (`PACK/rules/folder-conventions.md`). Keep the untouched original in `art-source/` as the master.
3. **Fix scale at import, not with Transform scale.** The project convention is 1 unit = 1 metre.
   Set the model importer's Scale Factor, or `Convert Units` for an FBX authored in centimetres. A
   scaled Transform breaks physics, colliders, LOD distances and child offsets, and the damage
   spreads to every prefab using it.
4. **Fix the axis at import.** glTF and GLB are Y-up, +Z forward, which matches Unity. FBX from many
   tools is Z-up. If the model lies on its side or faces backwards, correct it in the importer or
   re-export — do not add a rotated parent GameObject, which breaks animation root motion and makes
   every later rotation confusing.
5. Materials: imported models arrive with Built-in pipeline materials, which render **magenta** in
   URP. Convert them — use the importer's material settings and the project's URP material type from
   the art bible (Lit, Simple Lit or Unlit). Convert the set in one pass rather than assigning
   materials one at a time, and **share materials** so the SRP Batcher keeps working
   (`PACK/rules/performance.md`).
6. Textures: set the correct type per map — normal maps **must** be marked Normal Map, or lighting
   is subtly and permanently wrong. Set Max Size to the art bible's resolution; enable mip maps for
   3D (unlike 2D); keep sRGB on for colour maps and **off** for data maps such as roughness,
   metallic and masks.
7. LODs: generate or author the levels from the art bible for anything seen at distance. Set LOD
   group transition distances against the actual camera distance, not Unity's defaults.
8. Mesh settings: enable **Read/Write only if** something genuinely needs mesh data at runtime — it
   doubles memory. Enable Optimize Mesh. Generate colliders only for static geometry, and prefer a
   primitive collider added by hand over an auto-generated mesh collider.
9. Rig, if the model animates:
   - Set Animation Type to **Humanoid** for a humanoid skeleton, **Generic** otherwise, matching the
     art bible rig type.
   - For Humanoid, configure the Avatar and check every bone mapping. One mis-mapped bone is why an
     animation looks subtly broken with no error.
   - To reuse the project's existing animations, set the new model's Avatar to **Copy From Other
     Avatar** and point it at the project's reference Avatar. Without this, shared clips will not
     retarget.
   - Set the root motion source deliberately; the default is often not what the controller expects.
10. Verify in the project, not in the importer preview:
    ```bash
    unity recompile --strict --format json
    ```
    then `qa-playmode-check`: correct size next to the character, facing the right way, lit
    correctly with no magenta, LODs switching without popping, and animation playing cleanly.
11. Add a row to the art bible's **Licensing and provenance** table, then `design-update-state`.

## Unity CLI commands used

```bash
unity status                              # live Editors: port, project path, version, PID
unity list                                # Editor-registered tools and their parameter schemas
unity commands --format json              # full CLI command manifest
unity assets import <file>                # import a .unitypackage
unity assets inspect <file>               # list a .unitypackage's contents without importing
unity recompile --strict --format json    # verify nothing broke
```

Import settings live in the asset's `.meta`. Change them through the Editor tools `unity list`
reports, or an Editor script run with `eval_file` — never by hand-editing `.meta`, which
desynchronises the asset database. Use fully-qualified names such as `UnityEditor.ModelImporter`.
See `PACK/references/unity-cli.md`.

## Files to read (exact paths)

| Need | Path |
| --- | --- |
| Project status and dimension | `design/STATE.md` |
| Design map | `design/INDEX.md` |
| Scale, axis, poly, LOD, texture, material, rig specs | `design/art-bible.md` |
| Model and art folder layout | `PACK/rules/folder-conventions.md` |
| URP material types and colour space | `PACK/references/urp-settings.md` |
| Batching, LOD and memory rules | `PACK/rules/performance.md` |
| Where the model came from | the `assets-gen-3d-model` skill |
| Provider licensing caveats | `PACK/references/asset-licensing.md` |

## Done checklist

- [ ] Scale fixed at import; every Transform scale is 1,1,1.
- [ ] Axis and facing fixed at import, not with a rotated parent.
- [ ] Materials converted to the project's URP material type; nothing renders magenta.
- [ ] Materials are shared, not cloned per instance.
- [ ] Normal maps are marked Normal Map; data maps have sRGB off.
- [ ] Texture Max Size matches the art bible; mip maps on for 3D.
- [ ] LODs exist for distant assets, with transition distances set against real camera distance.
- [ ] Read/Write is off unless runtime mesh access is genuinely required.
- [ ] Animation Type matches the art bible rig type, with every Humanoid bone verified.
- [ ] Shared clips retarget via Copy From Other Avatar where applicable.
- [ ] Verified in play mode: size, facing, lighting, LOD switching, animation.
- [ ] A provenance row was added to the art bible.

## Common mistakes

- Fixing size with Transform scale, which breaks physics, colliders and LOD distances everywhere the
  prefab is used.
- Adding a rotated parent GameObject to fix facing, which breaks root motion.
- Leaving Built-in materials in place and shipping magenta meshes.
- Forgetting to mark a normal map as Normal Map, giving lighting that is wrong in a way nobody can
  point at.
- sRGB left on for roughness or metallic maps, so the material response is wrong.
- Read/Write enabled by default on every mesh, silently doubling mesh memory.
- Auto-generated mesh colliders on moving objects, which cannot work if non-convex.
- Humanoid rig with one mis-mapped bone — animations look broken and nothing is logged.
- Skipping Copy From Other Avatar, so existing clips refuse to retarget to the new model.
- Hand-editing `.meta` files and desynchronising the asset database.
- Declaring the asset done from the importer preview rather than checking it in a scene.
