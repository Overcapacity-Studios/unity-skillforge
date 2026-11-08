---
name: core-scriptable-object-data
description: Move tunable game values into ScriptableObject configuration assets and wire components to read them. Use when numbers are hardcoded, a designer needs to tune values, or content needs data-driven definitions for items, enemies or levels. Configuration only, never runtime state.
metadata:
  version: 0.1.0
---

# ScriptableObject data assets

Paths written as `PACK/` mean wherever this pack's shared files live: `.unity-skillforge/` in a
game repo (`install.sh`), the sibling `unity-skillforge-pack` folder (`npx skills add`), the
plugin's root directory (plugin install), or `skills/unity-skillforge-pack/` in this repo.

## When to use

- A tuning number is hardcoded in a script, or duplicated across scripts.
- Content needs definitions: items, enemies, levels, abilities, loot tables.
- A value should be editable without recompiling or entering code.

## The one rule that matters

**A ScriptableObject is configuration. It is read-only at runtime.**

Mutating one in play mode writes to the asset in the Editor and is discarded in a build. This is the
single most common cause of "works in the Editor, broken in the build". Runtime state belongs on a
MonoBehaviour, a plain C# object owned by a system, or the save system.

## Inputs needed

- The values to extract, and a sensible default and valid range for each.
- Whether this is a **single tuning asset** (one per subject, e.g. player movement) or a **content
  definition** (many instances, e.g. one per item).
- Who edits it: a human in the Inspector, or only agents.

## Steps

1. Read `design/STATE.md` and `design/INDEX.md`. Pull the numbers and ranges from the mechanic spec
   named in `INDEX.md`; if there is no spec, run `design-mechanic-spec` first.
2. Copy `PACK/templates/csharp/ScriptableObject.cs.txt` to
   `Assets/_Project/Code/Features/<Subject>/<Subject><Kind>Data.cs`. Replace `__NAMESPACE__`,
   `__TYPE__` and `__SUBJECT__`.
3. Name the type by what it configures plus `Data`: `PlayerMovementData`, `ItemData`, `WaveData`.
4. Declare fields as `[SerializeField] private`, expose them as get-only properties. Add `[Range]`
   or `[Min]` to every number and `[Tooltip]` to anything a human will read.
5. Set `[CreateAssetMenu(menuName = "Game/Data/<Type>")]` so instances can be created from the
   Create menu.
6. Create the instances into the right folder per `PACK/rules/folder-conventions.md`:
   `Assets/_Project/Data/{Tuning|Items|Levels}/<Subject>_<Type>.asset`.
7. Reference the asset from the consumer with `[SerializeField] private PlayerMovementData _data;`
   and validate it in `Awake` with an actionable error. Never look the asset up by name or path, and
   never use `Resources.Load`.
8. Delete the hardcoded values you replaced. Leaving both is how the two drift apart.
9. If a value must change at runtime, copy it into a runtime field on `Awake` and mutate the copy —
   never the asset.
10. Compile and verify:
    ```bash
    unity recompile --strict --format json
    ```
11. Record the asset path in the mechanic spec's tuning table so the next agent finds it.

## Unity CLI commands used

```bash
unity status                              # confirm an Editor is reachable
unity list                                # Editor-registered tools and their parameter schemas
unity recompile --strict --format json    # compile check
unity test --format json                  # if logic reads the data
```

Creating assets is best done through an Editor script run with `eval_file` rather than a long inline
block — `script eval` compiles a statement block, so no `using` directives and fully-qualified type
names only. See `PACK/references/unity-cli.md`.

## Files to read (exact paths)

| Need | Path |
| --- | --- |
| Project status | `design/STATE.md` |
| Design map | `design/INDEX.md` |
| Values and ranges | `design/mechanic-*.md` (the one named in `INDEX.md`) |
| Template | `PACK/templates/csharp/ScriptableObject.cs.txt` |
| Asset folder rules and naming | `PACK/rules/folder-conventions.md` |
| Style rules | `PACK/rules/csharp-style.md` |
| Layer rules | `PACK/rules/architecture.md` |

## Done checklist

- [ ] No hardcoded tuning numbers remain in the consuming scripts.
- [ ] Every serialized number has a `[Range]` or `[Min]`.
- [ ] Fields are `[SerializeField] private`, exposed as get-only properties.
- [ ] The asset lives under `Assets/_Project/Data/` with the naming from the folder rules.
- [ ] The consumer holds a serialized reference, validated in `Awake`. No `Resources.Load`.
- [ ] Nothing writes to the asset at runtime.
- [ ] `unity recompile --strict` returns `success: true`.
- [ ] The asset path is recorded in the mechanic spec.

## Common mistakes

- Mutating the asset at runtime, then being surprised the build does not persist it.
- Making fields `public` to see them in the Inspector, instead of `[SerializeField] private`.
- Creating one giant `GameData` asset holding everything, so every change touches one file and every
  consumer depends on all of it. Split by subject.
- Loading the asset with `Resources.Load` or by string name, which breaks silently on rename.
- Forgetting `[CreateAssetMenu]`, leaving no way to create an instance.
- Putting runtime state like `currentHealth` on the data asset next to `maxHealth`.
