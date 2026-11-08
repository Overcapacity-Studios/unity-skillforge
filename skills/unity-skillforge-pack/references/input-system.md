# New Input System — pinned conventions

Package: `com.unity.inputsystem`. Pin the exact version in `Packages/manifest.json`.
Docs: <https://docs.unity3d.com/Packages/com.unity.inputsystem@latest>

## Hard rules

- **Legacy input is banned.** No `UnityEngine.Input`, `Input.GetKey`, `Input.GetAxis`,
  `Input.mousePosition`, or `GetComponent<CharacterController>()` driven by them.
- Active Input Handling = **Input System Package (New)**. Use "Both" only if a third-party package
  forces it, and record that exception in `design/tech-decisions.md`.
- One `.inputactions` asset per project: `Assets/Settings/Input/GameInput.inputactions`.
- **Generate the C# wrapper class** from the asset (Inspector → "Generate C# Class"). Reference the
  generated class; never look actions up by string at call sites.

## Action map layout

| Map | Purpose |
| --- | --- |
| `Player` | Movement and in-world verbs, enabled only during gameplay |
| `UI` | Menus and HUD navigation, enabled whenever a screen is open |
| `Debug` | Developer-only bindings, stripped from release builds |

Only one gameplay map is enabled at a time. Switching screens disables `Player` and enables `UI` —
do that in one place, not scattered across screens.

## Action naming and types

- Actions are PascalCase verbs: `Move`, `Look`, `Jump`, `Interact`, `Attack`, `Pause`.
- `Move` and `Look` are **Value / Vector2**. Buttons are **Button**. A hold uses a Hold interaction,
  not a per-frame poll.
- Add a **Stick Deadzone** processor to `Move` and `Look` for gamepad. Do not hand-roll a deadzone.
- Composite WASD is a **2D Vector composite**, not four separate actions.

## Reading input in code

- Prefer callbacks (`action.performed += ...`) over polling in `Update`.
- Subscribe in `OnEnable`, unsubscribe in `OnDisable`. An unsubscribed callback is a leak and will
  fire after the object is gone.
- Never call `Enable()` on an action map from more than one script.
- Movement intent belongs in a field written by the callback and consumed in `FixedUpdate` for
  physics-driven motion. Reading input inside `FixedUpdate` drops or doubles inputs.

## Device and rebinding notes

- Use `PlayerInput` for local multiplayer device assignment; a single-player game does not need it.
- Rebinding uses `PerformInteractiveRebinding`. Persist overrides with
  `SaveBindingOverridesAsJson` / `LoadBindingOverridesFromJson` through `core-save-system` — do not
  write a second persistence path.
- Always provide a cancel binding when rebinding, or the user can get stuck.

## Common mistakes

- Editing the `.inputactions` asset but not regenerating the C# class, so new actions are invisible.
- Leaving both input backends active and then debugging "double" input.
- Enabling the `UI` map without disabling `Player`, so gameplay reacts while a menu is open.
- Polling `action.ReadValue` in `Update` for a button and missing presses between frames.
