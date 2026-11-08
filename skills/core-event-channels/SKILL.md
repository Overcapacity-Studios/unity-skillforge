---
name: core-event-channels
description: Decouple two systems with a ScriptableObject event channel so neither references the other. Use when a feature needs to react to another feature, when an assembly cycle appears, or when code reaches across scenes. Prefer a direct reference inside one feature.
metadata:
  version: 0.1.0
---

# Event channels

Paths written as `PACK/` mean wherever this pack's shared files live: `.unity-skillforge/` in a
game repo (`install.sh`), the sibling `unity-skillforge-pack` folder (`npx skills add`), the
plugin's root directory (plugin install), or `skills/unity-skillforge-pack/` in this repo.

## When to use

- Two features must communicate, and `PACK/rules/architecture.md` forbids them referencing each
  other.
- An `.asmdef` cycle appeared, which will not compile.
- A UI element must react to gameplay, or something must react across an additively loaded scene.

**Do not** use for communication inside a single feature, or where a parent already holds a
reference to its child — a direct call is simpler, traceable and cheaper. An event channel for
everything makes control flow impossible to follow.

## Inputs needed

- The payload type: none, `int`, `float`, or a small struct. Keep payloads small and immutable.
- Who raises it (exactly one system should own raising) and who listens.
- Whether a late listener needs the last value. Channels are fire-and-forget; if the answer is yes,
  you want queryable state on a service instead, not a channel.

## Steps

1. Read `design/STATE.md` and `design/INDEX.md`.
2. Confirm a channel is actually the right tool: if the raiser could simply hold a serialized
   reference to the listener within the same feature, do that instead and stop here.
3. Copy `PACK/templates/csharp/EventChannel.cs.txt` to
   `Assets/_Project/Code/Core/Events/EventChannel.cs` if the base type does not exist yet. It lives
   in `Core` so every layer can reference it.
4. For a new payload type, add a small concrete subclass next to the existing ones:
   ```csharp
   [CreateAssetMenu(menuName = "Game/Events/Damage Event Channel", fileName = "NewDamage_EventChannel")]
   public sealed class DamageEventChannel : EventChannel<DamageInfo> { }
   ```
   Reuse `VoidEventChannel`, `IntEventChannel` or `FloatEventChannel` where they fit.
5. Create the asset into `Assets/_Project/Data/EventChannels/` named `<Payload>_EventChannel.asset`
   per `PACK/rules/folder-conventions.md`.
6. In the raiser: `[SerializeField] private IntEventChannel _healthChanged;` then
   `_healthChanged.Raise(value);`. Validate the reference in `Awake`.
7. In the listener: register in `OnEnable`, unregister in `OnDisable`. **Always paired.**
   ```csharp
   private void OnEnable()  => _healthChanged.Register(OnHealthChanged);
   private void OnDisable() => _healthChanged.Unregister(OnHealthChanged);
   ```
8. Assign the same asset to both in the Inspector. A channel with one side unassigned fails
   silently — that is why step 6 validates.
9. Compile and verify the wiring actually fires:
   ```bash
   unity recompile --strict --format json
   ```
   then run `qa-playmode-check` with a temporary log on the listener, and remove the log after.
10. Record the channel in the mechanic spec's dependencies so the next agent knows it exists.

## Unity CLI commands used

```bash
unity status                              # confirm an Editor is reachable
unity list                                # Editor-registered tools and their parameter schemas
unity recompile --strict --format json    # compile check
unity test --format json                  # EditMode tests can raise and assert without a frame
```

See `PACK/references/unity-cli.md`. Prefer `eval_file` with a checked-in Editor script over a long
inline `script eval` block.

## Files to read (exact paths)

| Need | Path |
| --- | --- |
| Project status | `design/STATE.md` |
| Design map | `design/INDEX.md` |
| Template | `PACK/templates/csharp/EventChannel.cs.txt` |
| Layer and dependency rules | `PACK/rules/architecture.md` |
| Asset naming | `PACK/rules/folder-conventions.md` |
| Style rules | `PACK/rules/csharp-style.md` |

## Done checklist

- [ ] A channel is genuinely needed; a direct reference would not have worked.
- [ ] The base type lives in `Core`, so no layer rule is broken.
- [ ] The asset is in `Assets/_Project/Data/EventChannels/` with `<Payload>_EventChannel` naming.
- [ ] Exactly one system raises the event.
- [ ] Every `Register` has a matching `Unregister` in `OnDisable`.
- [ ] Both raiser and listener validate their channel reference in `Awake`.
- [ ] Verified firing in play mode, not just compiling.
- [ ] Temporary logs removed.
- [ ] The channel is listed in the mechanic spec's dependencies.

## Common mistakes

- Registering in `Awake` or `Start` and never unregistering, which leaks and then fires callbacks on
  destroyed objects — usually surfacing as a `MissingReferenceException` minutes later.
- Forgetting to assign the asset in the Inspector on one side, so nothing happens and nothing errors.
- Using a channel where a direct call belongs, which makes the flow untraceable.
- Putting mutable state in the payload, so listeners mutate each other's data.
- Expecting the last value on subscribe. Channels do not replay; use a service with state.
- Having two systems raise the same channel, so no one can tell where an event came from.
- Stale delegates surviving an Editor domain reload — the template clears them in `OnDisable`; do
  not remove that.
