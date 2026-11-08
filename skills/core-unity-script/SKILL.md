---
name: core-unity-script
description: Write or refactor a Unity C# MonoBehaviour or plain service class with this project's style, layer and assembly rules. Use when adding gameplay code, splitting a bloated component, or fixing code that violates the C# rules. Not for data assets or event plumbing.
metadata:
  version: 0.1.0
---

# Write a Unity script

Paths written as `PACK/` mean `.unity-skillforge/` in a game repo, or this pack's root when working
on the pack itself.

## When to use

- Adding a new MonoBehaviour, service or plain C# class.
- Splitting a component that has grown past one responsibility.
- Bringing existing code in line with `PACK/rules/csharp-style.md`.

Do **not** use for: tunable data (`core-scriptable-object-data`), cross-system messaging
(`core-event-channels`), or input reading (`core-input-setup`).

## Inputs needed

- What the class owns, in one sentence. If you cannot write that sentence, the class is doing too
  much — stop and split it first.
- Which layer it belongs to: `Core`, `Systems`, `Features` or `Game`.
- Whether it needs a frame (`MonoBehaviour`) or not (plain C# class — prefer this).

## Steps

1. Read `design/STATE.md` and `design/INDEX.md`. Confirm the mechanic this serves is spec'd; if it
   is not, run `design-mechanic-spec` first.
2. Decide the layer using the dependency table in `PACK/rules/architecture.md`. Dependencies point
   inward only. If your new class needs to reference another feature, it is in the wrong layer —
   use an event channel instead.
3. Pick the form:
   - Needs Unity messages or Inspector wiring → `MonoBehaviour`.
   - Pure logic, or you want an EditMode test → plain C# class in `Core`. **Prefer this.**
4. Copy the template rather than writing from scratch:
   - `PACK/templates/csharp/MonoBehaviour.cs.txt` for a component.
   - `PACK/templates/csharp/StateMachine.cs.txt` if the behaviour has three or more states.
   - `PACK/templates/csharp/ServiceLocator.cs.txt` if you were about to write a singleton.
5. Place the file per `PACK/rules/folder-conventions.md`:
   `Assets/_Project/Code/{Core|Systems|Features|Game}/<Subject>/<TypeName>.cs`. The file name must
   equal the type name.
6. Replace `__NAMESPACE__` and `__TYPE__`. Namespace mirrors the folder path: `Game.Features.Player`.
7. Apply the style rules without exception — `_camelCase` private fields, `[SerializeField] private`
   for Inspector values, properties not public fields, cached component references in `Awake`,
   paired `OnEnable`/`OnDisable`. Re-read `PACK/rules/csharp-style.md` if unsure.
8. Move every tunable number onto a ScriptableObject or a `[SerializeField]` with `[Range]`/`[Min]`.
   No magic numbers in logic.
9. If the class belongs to a layer whose `.asmdef` does not exist yet, create it per
   `PACK/rules/architecture.md` and set explicit references. Do not enable Auto Referenced.
10. Compile and fix everything before moving on:
    ```bash
    unity status
    unity recompile --strict --format json
    ```
11. Add an EditMode test for any pure logic using `PACK/templates/csharp/EditModeTest.cs.txt`, then
    run `qa-run-tests`.
12. Remove every temporary `Debug.Log` you added.

## Unity CLI commands used

Discover the real surface first — never call a name you have not seen in this output:

```bash
unity status                     # confirm an Editor is reachable
unity list                       # Editor-registered tools, with parameter schemas
unity commands --format json     # full CLI command manifest
```

Then:

```bash
unity recompile --strict --format json   # compile check; --strict also fails on warnings
unity test --format json                 # run tests after a logic change
```

Exit codes: `0` success, `1` error (read stderr), `2` usage, `130` cancelled. Also check `success`
in the JSON envelope, not just the exit code. Details in `PACK/references/unity-cli.md`.

## Files to read (exact paths)

| Need | Path |
| --- | --- |
| Project status | `design/STATE.md` |
| Design map | `design/INDEX.md` |
| Style rules | `PACK/rules/csharp-style.md` |
| Layer and assembly rules | `PACK/rules/architecture.md` |
| Where the file goes | `PACK/rules/folder-conventions.md` |
| Per-frame cost rules | `PACK/rules/performance.md` |
| Component template | `PACK/templates/csharp/MonoBehaviour.cs.txt` |
| State machine template | `PACK/templates/csharp/StateMachine.cs.txt` |
| Service locator template | `PACK/templates/csharp/ServiceLocator.cs.txt` |

## Done checklist

- [ ] One sentence describes what the class owns.
- [ ] File is in the correct layer folder, and the file name equals the type name.
- [ ] No `GameObject.Find`, `FindObjectOfType`, `SendMessage`, legacy `Input`, or `public static Instance`.
- [ ] Component references cached in `Awake`; no `GetComponent` in a per-frame method.
- [ ] Every `OnEnable` subscription has a matching `OnDisable` unsubscription.
- [ ] Physics reads and writes are in `FixedUpdate`.
- [ ] Zero allocation in any per-frame path (no `new`, no LINQ, no string building).
- [ ] Serialized references validated in `Awake` with an actionable `Debug.LogError`.
- [ ] `unity recompile --strict` returns `success: true` with no warnings.
- [ ] Temporary logging removed.
- [ ] `design/STATE.md` updated via `design-update-state`.

## Common mistakes

- Writing a `MonoBehaviour` for logic that needs no frame, which makes it untestable in EditMode.
- Reaching for a singleton because wiring felt tedious — use the service locator.
- Referencing another feature's type directly, creating an assembly cycle that will not compile.
- Leaving an empty `Update` or `Start`; an empty Unity message still costs a call per frame.
- Caching `Camera.main` nowhere and calling it per frame — it is a tagged search every call.
- Mutating a ScriptableObject at runtime to hold state. It persists in the Editor, not in a build.
- Declaring the work done after it compiles. Compiling is not playing — run `qa-playmode-check`.
