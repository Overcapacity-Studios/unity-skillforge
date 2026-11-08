# C# style rules

Non-negotiable. A reviewer rejects code that breaks these.

## Naming

| Thing | Convention | Example |
| --- | --- | --- |
| Class, struct, enum, method, property | PascalCase | `PlayerHealth`, `TakeDamage` |
| Private field | `_camelCase` | `_currentHealth` |
| Serialized private field | `_camelCase` with `[SerializeField]` | `[SerializeField] private float _moveSpeed;` |
| Public field | Do not use one — expose a property | — |
| Constant, static readonly | PascalCase | `MaxHealth` |
| Local, parameter | camelCase | `damageAmount` |
| Interface | `I` + PascalCase | `IDamageable` |
| Async method | PascalCase + `Async` | `LoadSceneAsync` |
| Boolean | Reads as a question | `_isGrounded`, `HasKey` |

- No Hungarian notation, no `m_` prefix, no abbreviations beyond `UI`, `ID`, `VFX`, `SFX`.
- File name always equals the top-level type name.
- One top-level type per file. Nested helper types are fine.

## Fields and serialization

- `private` by default. Widen only when something outside genuinely needs it.
- Expose state as `public float Health { get; private set; }`, never a public field.
- Use `[SerializeField] private` for Inspector values. Never make a field public just to serialize.
- Add `[Range]`, `[Min]` or `[Tooltip]` to any designer-facing number.
- No magic numbers in logic. Tunables live on a ScriptableObject
  (`core-scriptable-object-data`) or a `[SerializeField]` with a range.

## Unity lifecycle

- `Awake` for self-wiring (own components, own state). `Start` for cross-object lookups.
- Cache component references in `Awake`. Never call `GetComponent` in `Update`.
- **Never** use `GameObject.Find`, `FindObjectOfType`, or `FindObjectsOfType` in gameplay code.
  Wire references in the Inspector, or resolve through the service locator.
- Subscribe in `OnEnable`, unsubscribe in `OnDisable` — always paired. An unpaired subscription is a
  leak that fires on a destroyed object.
- Physics reads and writes go in `FixedUpdate`. Input and camera go in `Update` / `LateUpdate`.
- No empty `Update`, `Start` or `Awake` — an empty Unity message still costs a call every frame.

## Banned

- `UnityEngine.Input` and the legacy input manager. Use the new Input System
  (`references/input-system.md`).
- `SendMessage`, `BroadcastMessage`.
- Singletons with a mutable `public static Instance`. Use `ServiceLocator.cs.txt`.
- `async void`, except a Unity event handler that cannot be `async Task`.
- `Task.Run` and thread pool work touching the Unity API. Unity API calls are main-thread only.
- `string` concatenation in a per-frame path.
- `Resources.Load`. Use Addressables or a direct serialized reference.
- Catching `Exception` with an empty block. If you catch, log with context.
- `#region`. If a file needs regions it needs splitting.

## Formatting

- 4 spaces, no tabs. Allman braces (brace on its own line).
- Braces on every control-flow block, even single statements.
- Max line length 120.
- `var` only when the right-hand side makes the type obvious; otherwise write the type.
- `using` directives at the top, `System` first, no unused directives.
- Prefer early return over nesting. Guard clauses first.

## Comments and documentation

- Comment *why*, never *what*. `// add 1 to i` is noise.
- XML docs (`///`) on every `public` member of a system other code consumes.
- No commented-out code. Delete it; git remembers.
- No `TODO` without an owner and a reason: `// TODO(design): confirm damage curve, see design/mechanic-combat.md`.

## Errors

- Validate serialized references in `Awake` and log an actionable error naming the object:
  `Debug.LogError($"{name}: _target is not assigned", this);`
- A null check that silently returns hides a setup bug. Log it.
- Remove temporary `Debug.Log` lines before finishing. Leftover logging clutters the console the
  next agent has to read.
