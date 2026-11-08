---
name: 2d-physics-setup
description: Set up 2D collisions, rigidbodies and the layer collision matrix after determining which of Unity 6's two incompatible 2D physics systems the project uses. Use for any 2D physics work. Defer to Unity's create-2d-physics skill for the per-system procedure.
metadata:
  version: 0.1.0
---

# 2D physics setup

Paths written as `PACK/` mean wherever this pack's shared files live: `.unity-skillforge/` in a
game repo (`install.sh`), the sibling `unity-skillforge-pack` folder (`npx skills add`), the
plugin's root directory (plugin install), or `skills/unity-skillforge-pack/` in this repo.

## When to use

- Adding collision, triggers or rigidbody motion to a 2D game.
- Fixing a character falling through the floor, catching on seams, or jittering.
- Setting the layer collision matrix on a new project.

## Stop: there are two 2D physics systems

Unity 6 ships **two 2D physics systems. They share no code and never interact.** Code written
against the wrong one **compiles, runs, and does nothing** — which is the single most expensive
mistake in this area.

| Signal in the project | System |
| --- | --- |
| Physics Pose, Physics Area, Constraint or Simulation components | **Core components** — needs `com.unity.2d.physics` and Unity `6000.7+` |
| `Rigidbody 2D`, `Collider 2D`, `Joint 2D`, `Effector 2D` components | **Legacy** |
| `Unity.U2D.Physics` or `UnityEngine.LowLevelPhysics2D` types in script | **Core, in script** (no package needed) |
| `Rigidbody2D`, `Collider2D`, `Physics2D` types in script | **Legacy** |
| Both present | Two separate simulations — treat separately and say so |
| No signal at all | **Stop and ask.** Offer all three routes; never choose for the user |

Determine it in this order: existing scene components first (components are the reliable signal),
then the wording of the request, then `design/tech-decisions.md`. The project baseline is
`6000.3.x`, where Core *components* are unavailable — but verify rather than assume. Full table in
`PACK/references/unity-versions.md`.

## Prefer the official skill

If Unity's official plugin is installed:

- `/unity:create-2d-physics` — the authoritative per-system procedure for both systems.
- `/unity:fix-3d-physics-collisions` — if the problem turns out to be 3D.

What stays ours: **which system this project pins, the layer matrix, and the platformer feel
budget** below. See `PACK/references/official-unity-skills.md`.

## Inputs needed

- Which system (from the table above) — and record it in `design/tech-decisions.md` if it is not
  already there.
- The mechanic spec's rules and tuning values.
- The list of collision layers the game needs.

## Steps

1. Read `design/STATE.md`, `design/INDEX.md`, then `design/tech-decisions.md` → the 2D physics
   decision. If that entry is a placeholder, resolve it with the table above and write it down
   before touching any code.
2. Define collision layers explicitly: `Player`, `Enemy`, `Ground`, `Platform`, `Trigger`,
   `Projectile`. Then **set the layer collision matrix** in Project Settings → Physics 2D. The
   default matrix has everything colliding with everything, which is the most common quiet
   performance bug (`PACK/rules/performance.md`).
3. Put triggers on their own layer, colliding only with what must trigger them.
4. Hand the per-system component setup to `/unity:create-2d-physics`. Apply these project rules on
   top:
   - A moving body uses **Dynamic**; static geometry uses no rigidbody at all, not a Static one.
   - Interpolate = **Interpolate** on anything the camera follows, or it visibly stutters.
   - Collision Detection = **Continuous** for fast movers, to stop tunnelling through thin colliders.
   - Use primitive colliders. A non-convex mesh-style collider cannot move.
5. Move bodies through the physics API in `FixedUpdate` — velocity or `MovePosition`. **Never write
   `transform.position` on a body with a rigidbody**; it teleports past collision.
6. Use non-allocating queries only: `RaycastNonAlloc`, `OverlapCircleNonAlloc`, or a
   `ContactFilter2D`. The allocating overloads garbage on every call.
7. Leave the fixed timestep at 0.02 (50 Hz) unless the design demands otherwise; lowering it
   multiplies every physics cost.
8. For platformer feel, implement what the spec's **Feel** section asks for — coyote time, input
   buffering, variable jump height — with values from the mechanic's tuning asset, never constants.
9. Verify:
   ```bash
   unity recompile --strict --format json
   ```
   then `qa-playmode-check` against the acceptance checks: no falling through floors, no catching on
   seams, no jitter while the camera follows.

## Unity CLI commands used

```bash
unity status                              # live Editors: port, project path, version, PID
unity list                                # Editor-registered tools and their parameter schemas
unity commands --format json              # full CLI command manifest
unity recompile --strict --format json    # compile check
unity test --format json                  # PlayMode tests; advance with WaitForFixedUpdate
```

To probe which physics system is actually present, read it from the Editor rather than guessing —
use the eval tool `unity list` reports. `script eval` compiles a statement block, so use
fully-qualified names such as `UnityEngine.Rigidbody2D` or `Unity.U2D.Physics`, and no `using`
directives. See `PACK/references/unity-cli.md`.

## Files to read (exact paths)

| Need | Path |
| --- | --- |
| Project status | `design/STATE.md` |
| Design map | `design/INDEX.md` |
| Which physics system is pinned | `design/tech-decisions.md` |
| The two-system table and version gates | `PACK/references/unity-versions.md` |
| Rules, tuning and feel targets | `design/mechanic-*.md` (named in `INDEX.md`) |
| Official 2D physics skill | `PACK/references/official-unity-skills.md` |
| Layer matrix and non-alloc query rules | `PACK/rules/performance.md` |
| Style rules (FixedUpdate, no magic numbers) | `PACK/rules/csharp-style.md` |

## Done checklist

- [ ] The physics system was determined from evidence and is recorded in `design/tech-decisions.md`.
- [ ] No code mixes the two systems.
- [ ] Collision layers are defined and the layer collision matrix is set explicitly.
- [ ] Triggers are on their own layer.
- [ ] Static geometry has no rigidbody; moving bodies are Dynamic and Interpolated.
- [ ] Fast movers use Continuous collision detection.
- [ ] All motion goes through the physics API in `FixedUpdate`; no `transform.position` writes.
- [ ] Only non-allocating queries are used.
- [ ] Feel values come from a tuning asset, not constants.
- [ ] Verified in play mode: no falling through, no seam catching, no jitter.

## Common mistakes

- Writing legacy `Rigidbody2D` code in a project using 2D Physics Core, or the reverse. It compiles,
  runs, and does nothing — and nothing in the console tells you why.
- Guessing the system from the Unity version instead of checking the scene components.
- Leaving the default layer collision matrix, so everything tests against everything.
- Setting `transform.position` on a rigidbody and tunnelling straight through walls.
- Reading input inside `FixedUpdate`, which drops or doubles inputs.
- Interpolation left off, so a camera-followed character stutters at every frame rate.
- `TilemapCollider2D` with no composite collider, so the character catches on tile seams.
- Allocating physics queries in a per-frame path, causing GC stutter that reads as low frame rate.
- Lowering the fixed timestep to fix a feel problem that was actually missing interpolation.
