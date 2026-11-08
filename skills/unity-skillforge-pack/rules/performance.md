# Performance rules

Budgets first, then measure, then optimise. Never optimise from a guess.

## Frame budgets

| Target | Frame budget | CPU main thread |
| --- | --- | --- |
| 60 fps | 16.6 ms | ≤ 10 ms |
| 30 fps (mobile floor) | 33.3 ms | ≤ 22 ms |

Record the target in `design/tech-decisions.md`. A project without a stated target cannot be said to
have a performance problem.

## Allocation — the rule that matters most

Managed allocation in a per-frame path causes GC spikes, which read as stutter, not as low fps.

- **Zero allocation per frame** in `Update`, `FixedUpdate`, `LateUpdate` and any coroutine that runs
  every frame.
- No `new` in a per-frame path. Pool instead.
- No LINQ in a per-frame path. `Where`, `Select`, `OrderBy` and `foreach` over an interface all
  allocate.
- No `string` concatenation or interpolation per frame, including inside `Debug.Log`. A log call
  builds its string even when logging is filtered out.
- `foreach` over a `List<T>` is fine; over `IEnumerable<T>` it boxes the enumerator.
- Cache `new WaitForSeconds(...)` instead of allocating one per yield.
- Pass large structs by `in` / `ref`. Do not box.
- Prefer `TryGetComponent` over `GetComponent` when absence is normal — `GetComponent` returning
  null is fine, but the null check is easy to forget.

## Per-frame work

- Cache every component reference in `Awake`. `GetComponent` in `Update` is banned.
- `GameObject.Find`, `FindObjectOfType`, `Camera.main` and `transform.Find` are all searches. Cache
  them once. (`Camera.main` does a tagged search every call.)
- Do not run logic every frame that does not need to. Use a timer, a coroutine with an interval, or
  an event.
- Prefer events over polling. A script that checks a condition every frame to notice a change should
  be subscribing to it.
- Avoid `Update` on hundreds of objects. One manager iterating a list beats 500 Unity message calls.

## Physics

- Set the **layer collision matrix** explicitly. The default matrix has everything colliding with
  everything, which is the most common quiet performance bug.
- Fixed timestep stays at 0.02 (50 Hz) unless the design requires otherwise; lowering it multiplies
  every physics cost.
- Use primitive colliders. A mesh collider is a last resort, and a non-convex one cannot move.
- `Rigidbody` moves via `MovePosition` / velocity, never by writing `transform.position`.
- Use non-allocating queries: `Physics.RaycastNonAlloc`, `OverlapSphereNonAlloc`, and a
  `ContactFilter2D` for 2D. The allocating overloads garbage every call.
- Put triggers on their own layer, colliding only with what must trigger them.

## Rendering

- Watch **draw calls and SetPass calls**, not triangle count, on anything modern.
- Keep the SRP Batcher working: share materials, vary with `MaterialPropertyBlock`. Instantiating a
  material per object silently disables batching.
- Static geometry gets marked **Static** for occlusion and light baking.
- Bake lighting for anything that does not move. A real-time light with shadows is one extra render
  of everything it touches.
- LODs on any 3D asset seen at distance (`assets-import-pipeline` sets them up).
- Atlas 2D sprites (`manage-sprite-atlas` officially, our conventions in `2d-sprite-import`).
  Unatlased sprites are one draw call each.
- Overdraw is the 2D and mobile killer: watch large transparent quads, particle sheets and
  full-screen UI stacking.

## UI

- A Canvas rebuilds entirely when any element on it changes. Split static and dynamic UI onto
  separate canvases.
- Disable `Raycast Target` on anything non-interactive.
- Never leave an animated element on the same canvas as a large static one.

## Measuring

1. Build and profile on the **target device**. Editor numbers are not shippable evidence.
2. Use the Profiler with Deep Profile off first; find the spike, then narrow.
3. Check GC Alloc per frame in the Profiler's CPU module — the target is 0 B.
4. Use the Frame Debugger to confirm batching.
5. Unity's official `/unity:project-auditor-fixes` skill finds project-wide settings problems; see
   `references/official-unity-skills.md`.

Report a measurement with the device, the scene and the number. "It feels faster" is not a result.
