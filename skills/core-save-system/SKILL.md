---
name: core-save-system
description: Build or extend the single save system - versioned JSON save data, atomic writes to persistentDataPath, and a save service resolved through the service locator. Use for saving progress, settings or input rebinds. Nothing else in the project may write to disk.
metadata:
  version: 0.1.0
---

# Save system

Paths written as `PACK/` mean wherever this pack's shared files live: `.unity-skillforge/` in a
game repo (`install.sh`), the sibling `unity-skillforge-pack` folder (`npx skills add`), the
plugin's root directory (plugin install), or `skills/unity-skillforge-pack/` in this repo.

## When to use

- Persisting progress, settings, or input binding overrides.
- Adding a field to existing save data.
- Fixing corrupt saves, or saves that break after an update.

**There is exactly one save system.** If something else in the project writes to disk, consolidate it
here rather than adding a second path.

## Inputs needed

- What must persist, and what must not. Derived values are recomputed, never saved.
- Whether saving is manual, at checkpoints, or continuous.
- Whether old saves must keep working after a data change (usually yes once the game has shipped).

## Steps

1. Read `design/STATE.md` and `design/INDEX.md`.
2. Define the save data as a **plain serializable C# class**, not a MonoBehaviour and not a
   ScriptableObject. Put it in `Assets/_Project/Code/Systems/Save/SaveData.cs`.
3. **Include a version number as the first field** and default it to the current version:
   ```csharp
   [System.Serializable]
   public sealed class SaveData
   {
       public int Version = CurrentVersion;
       public const int CurrentVersion = 1;
   }
   ```
   Without this, the first data change breaks every existing save and there is no way back.
4. Define `ISaveService` in `Core` and implement it in `Systems`:
   `Save(SaveData)`, `TryLoad(out SaveData)`, `Delete()`, `Exists()`.
5. Serialize with `JsonUtility` for speed and no dependency, or `System.Text.Json` if you need
   dictionaries and polymorphism. Note `JsonUtility` ignores properties and dictionaries — fields
   only.
6. Write to `Application.persistentDataPath`. Never write into `Assets/` or next to the executable;
   that fails on every platform with a read-only install directory.
7. **Write atomically**: serialize to `save.tmp`, flush, then replace `save.json`. A crash mid-write
   must not destroy the previous save. Keep one backup (`save.bak`) and fall back to it on a failed
   parse.
8. Handle a failed load as a normal case, not an exception path: log the reason, return a fresh
   `SaveData`, and never overwrite the unreadable file until the next successful save.
9. On load, if `Version` is below `CurrentVersion`, run migration steps in order. Keep a `Migrate_1_2`
   style method per step so each is reviewable and testable.
10. Register the service in the bootstrap scene and resolve it with
    `PACK/templates/csharp/ServiceLocator.cs.txt`. No `public static Instance`.
11. Route input rebinds here (`SaveBindingOverridesAsJson` from `core-input-setup`) rather than
    adding a parallel store.
12. Add EditMode tests with `PACK/templates/csharp/EditModeTest.cs.txt` covering round-trip, a
    corrupt file, a missing file, and one version migration. Then:
    ```bash
    unity recompile --strict --format json
    unity test --format json
    ```

## Unity CLI commands used

```bash
unity status                              # confirm an Editor is reachable
unity list                                # Editor-registered tools and their parameter schemas
unity recompile --strict --format json    # compile check
unity test --format json                  # round-trip, corruption and migration tests
```

To find the real save location on the current machine, read it from the Editor rather than guessing:

```bash
unity command --format json   # discover the eval tool name first, then return Application.persistentDataPath
```

`script eval` compiles a statement block — no `using` directives, fully-qualified types, and the
value arrives at `data.result.result`. See `PACK/references/unity-cli.md`.

## Files to read (exact paths)

| Need | Path |
| --- | --- |
| Project status | `design/STATE.md` |
| Design map | `design/INDEX.md` |
| Service locator template | `PACK/templates/csharp/ServiceLocator.cs.txt` |
| Test template | `PACK/templates/csharp/EditModeTest.cs.txt` |
| Layer rules (Core vs Systems) | `PACK/rules/architecture.md` |
| Style rules | `PACK/rules/csharp-style.md` |
| Folder layout | `PACK/rules/folder-conventions.md` |
| Decision log | `design/tech-decisions.md` |

## Done checklist

- [ ] Save data is a plain serializable class with a `Version` field as its first member.
- [ ] Writes go to `Application.persistentDataPath`, never into `Assets/`.
- [ ] Writes are atomic (temp file then replace) with one backup kept.
- [ ] A corrupt or missing save returns fresh data and does not destroy the existing file.
- [ ] At least one version migration path exists and is tested.
- [ ] Exposed as `ISaveService`, registered in bootstrap, resolved via the service locator.
- [ ] Nothing else in the project writes to disk.
- [ ] Only state is saved; derived values are recomputed on load.
- [ ] Tests cover round-trip, corrupt file, missing file and migration, and all pass.
- [ ] The serialization choice is recorded in `design/tech-decisions.md`.

## Common mistakes

- No version field. The first data change then breaks every save with no migration route.
- Writing directly over the save file, so a crash or a full disk loses the player's progress.
- Saving to `Application.dataPath` or inside `Assets/`, which is read-only in a real install.
- Using `JsonUtility` with a `Dictionary` or a property and getting silent empty data — it
  serializes fields only.
- Saving derived state (current speed, cached totals) and then having it disagree with reality.
- Saving a `ScriptableObject` reference instead of an id, which does not survive serialization.
- Swallowing a parse exception and overwriting the only recoverable save on the next autosave.
- A second save path added "just for settings", which later disagrees with the main save.
