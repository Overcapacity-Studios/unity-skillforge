# Architecture rules

## The dependency rule

Dependencies point **inward**. Outer layers know about inner layers; never the reverse.

```
Game  →  Features  →  Systems  →  Core
```

| Layer | Holds | May reference |
| --- | --- | --- |
| `Core` | Pure C#: math, utilities, interfaces, event-channel base types | nothing in this project |
| `Systems` | Engine-facing services: save, audio, input, scene loading | `Core` |
| `Features` | Gameplay: player, enemies, pickups, UI screens | `Systems`, `Core` |
| `Game` | Composition root, bootstrap, scene wiring | everything |

A feature must never reference another feature directly. Two features that need to talk do it
through an event channel (`core-event-channels`) or shared data (`core-scriptable-object-data`).

## Assembly definitions

- One `.asmdef` per layer, named `Game.Core`, `Game.Systems`, `Game.Features`, `Game.Game`.
- Tests get their own: `Game.Core.Tests` (EditMode), `Game.Features.PlayTests` (PlayMode).
- Set explicit references. Never tick "Auto Referenced" on a gameplay assembly.
- `Game.Core` must have **no** Unity engine reference where that is achievable; keep it testable
  without the Editor.
- An asmdef cycle will not compile. If you reach for one, the dependency is pointing the wrong way.

## Composition, not singletons

- There is exactly one composition root: a bootstrap scene with a single bootstrap object.
- Services are registered there and resolved through `ServiceLocator.cs.txt`. No
  `public static Instance` on a MonoBehaviour.
- A MonoBehaviour receives its dependencies via `[SerializeField]` or a registered service. It does
  not go looking for them.
- Nothing in `Features` may construct a service. It asks for one.

## State

- Behaviour with more than two states uses `StateMachine.cs.txt`, not a pile of booleans.
- One owner per piece of state. If two scripts can write the same value, one of them is wrong.
- Runtime state never lives on a ScriptableObject that ships with the build — SO data is
  *configuration*. Mutating it in play mode persists in the Editor and not in a build, which is the
  single most common source of "works in Editor, broken in build".

## Scenes

- `Bootstrap` scene loads first and is never unloaded.
- Gameplay scenes load additively; the bootstrap scene owns persistent services.
- A scene must not depend on another scene already being loaded; it asks the scene loader.
- No cross-scene references in the Inspector. They do not survive a build.

## Data flow

- Configuration: ScriptableObject assets, read-only at runtime.
- Communication: event channels (ScriptableObject-based), fire-and-forget.
- Queries: an interface on a registered service.
- Persistence: one save system (`core-save-system`). Nothing else writes to disk.

## When to add an abstraction

Add an interface when there is a second real implementation, or when a test needs a seam. Not
before. A one-implementation interface is cost without benefit, and the reviewer will ask you to
remove it.
