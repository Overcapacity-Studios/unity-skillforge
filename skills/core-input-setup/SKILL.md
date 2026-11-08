---
name: core-input-setup
description: Set up or extend player input with Unity's new Input System - action maps, bindings, the generated C# class, map switching and rebinding. Use when adding a control, wiring a new device, or replacing legacy UnityEngine.Input calls. Legacy input is banned in this project.
metadata:
  version: 0.1.0
---

# Input setup

Paths written as `PACK/` mean wherever this pack's shared files live: `.unity-skillforge/` in a
game repo (`install.sh`), the sibling `unity-skillforge-pack` folder (`npx skills add`), the
plugin's root directory (plugin install), or `skills/unity-skillforge-pack/` in this repo.

## When to use

- First-time input setup on a new project.
- Adding an action, a binding or a device.
- Replacing legacy `UnityEngine.Input` calls, which are banned by `PACK/rules/csharp-style.md`.
- Adding rebinding, or fixing gameplay reacting while a menu is open.

## Inputs needed

- The actions the mechanic needs, from its spec's Inputs table.
- Devices to support: keyboard and mouse, gamepad, touch.
- Whether local multiplayer is in scope (that is the only reason to add `PlayerInput`).

## Steps

1. Read `design/STATE.md` and `design/INDEX.md`, then the mechanic spec's **Inputs** table.
2. Read `PACK/references/input-system.md` in full. It holds the pinned conventions; do not improvise
   action names or map layout.
3. Verify the package and backend:
   - `com.unity.inputsystem` pinned in `Packages/manifest.json`.
   - Project Settings → Player → **Active Input Handling = Input System Package (New)**. If it is
     "Both", change it, or record the forcing package in `design/tech-decisions.md`.
4. Create or open the single actions asset at
   `Assets/Settings/Input/GameInput.inputactions`. One asset per project — never a second one.
5. Ensure the three maps exist: `Player`, `UI`, `Debug`. Put the new action in the right one.
6. Add the action with the correct type:
   - `Move`, `Look` → **Value / Vector2**, with a **Stick Deadzone** processor.
   - Buttons → **Button**. A hold uses a **Hold** interaction, never a per-frame poll.
   - WASD is a **2D Vector composite**, not four actions.
   Name actions as PascalCase verbs.
7. In the asset's Inspector, enable **Generate C# Class** and regenerate it. Skipping this is why a
   new action appears to not exist.
8. Consume it in code:
   - Subscribe in `OnEnable`, unsubscribe in `OnDisable`.
   - Store movement intent in a field; consume it in `FixedUpdate` for physics motion. Reading input
     inside `FixedUpdate` drops or doubles inputs.
   - Never read an action by string at a call site.
9. Map switching lives in exactly one place: enabling `UI` disables `Player`, and the reverse. Do not
   scatter `Enable()` calls across screens.
10. For rebinding, use `PerformInteractiveRebinding`, always provide a cancel binding, and persist
    overrides with `SaveBindingOverridesAsJson` through `core-save-system` — do not add a second
    persistence path.
11. Compile and verify in play mode:
    ```bash
    unity recompile --strict --format json
    ```
    then run `qa-playmode-check` against the mechanic's acceptance checks.

## Unity CLI commands used

```bash
unity status                              # confirm an Editor is reachable
unity list                                # Editor-registered tools and their parameter schemas
unity recompile --strict --format json    # compile check after regenerating the C# class
unity test --format json                  # input-driven tests
```

The `.inputactions` asset is JSON on disk, so it can be read directly — but write it through the
Editor or `eval_file` so the generated class and `.meta` stay consistent. See
`PACK/references/unity-cli.md`.

## Files to read (exact paths)

| Need | Path |
| --- | --- |
| Project status | `design/STATE.md` |
| Design map | `design/INDEX.md` |
| Actions required | `design/mechanic-*.md` (named in `INDEX.md`) |
| Pinned input conventions | `PACK/references/input-system.md` |
| Version and package pins | `PACK/references/unity-versions.md` |
| Style rules (legacy input ban) | `PACK/rules/csharp-style.md` |
| Backend exception log | `design/tech-decisions.md` |

## Done checklist

- [ ] Active Input Handling is Input System Package (New), or the exception is recorded.
- [ ] Exactly one `.inputactions` asset exists, at `Assets/Settings/Input/GameInput.inputactions`.
- [ ] The action is in the correct map with the correct type and a deadzone where it is a stick.
- [ ] The C# class was regenerated after editing the asset.
- [ ] No `UnityEngine.Input`, `Input.GetKey`, `Input.GetAxis` or `Input.mousePosition` anywhere.
- [ ] Subscriptions are paired across `OnEnable` and `OnDisable`.
- [ ] Physics-driven movement consumes a stored intent in `FixedUpdate`.
- [ ] Map switching happens in one place; gameplay does not react while a menu is open.
- [ ] `unity recompile --strict` returns `success: true`, and the control works in play mode.

## Common mistakes

- Editing the asset and not regenerating the C# class, then concluding the action is broken.
- Leaving Active Input Handling on "Both" and debugging doubled input for an hour.
- Enabling the `UI` map without disabling `Player`, so the player moves behind an open menu.
- Polling `ReadValue` in `Update` for a button and missing presses between frames.
- Hand-rolling a deadzone instead of adding the processor.
- Four separate actions for WASD instead of a 2D Vector composite.
- Calling `Enable()` on the same map from several scripts, so disabling it in one place has no effect.
- Rebinding with no cancel binding, leaving the user stuck in the rebind prompt.
