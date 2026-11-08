---
name: 3d-character-controller
description: Build a 3D player movement controller - choosing between CharacterController and Rigidbody, ground detection, slopes and steps, camera-relative movement, jump and air control. Use for player locomotion in a 3D game. Nothing official covers this, so it is built from the templates here.
metadata:
  version: 0.1.0
---

# 3D character controller

Paths written as `PACK/` mean `.unity-skillforge/` in a game repo, or this pack's root.

## When to use

- Implementing player locomotion in a 3D game.
- Fixing a character that sticks to walls, slides down slopes, cannot climb steps, or jitters.
- Replacing an ad-hoc movement script with the project's state-machine approach.

## Decide this first: CharacterController or Rigidbody

Record the choice in `design/tech-decisions.md`. Switching later is a rewrite.

| | `CharacterController` | `Rigidbody` |
| --- | --- | --- |
| Movement | Kinematic, you author it | Physics-driven, forces and velocity |
| Slopes and steps | Built in (`slopeLimit`, `stepOffset`) | You implement them |
| Pushed by physics | No | Yes |
| Pushes other bodies | Only via explicit code | Yes |
| Predictability | High — good for platformers | Lower — good for physics-driven games |
| Capsule shape only | Yes | No |

Default to **`CharacterController`** for a platformer or action game with precise feel. Choose
`Rigidbody` only when the character must genuinely participate in physics (being knocked back by
explosions, pushing crates, riding moving platforms physically).

## Inputs needed

- The mechanic spec's rules, tuning values and **Feel** section. If there is no spec, run
  `design-mechanic-spec` first — feel values cannot be invented.
- Input actions already set up via `core-input-setup`.
- The camera rig, since movement is camera-relative (`3d-cinemachine-camera`).

## Steps

1. Read `design/STATE.md`, `design/INDEX.md`, the mechanic spec, and `design/tech-decisions.md`.
2. Record the controller choice using the table above if it is not already recorded.
3. Put the tuning values on a ScriptableObject via `core-scriptable-object-data`
   (`PlayerMovementData`): move speed, acceleration, deceleration, air control, jump height, gravity
   multiplier, coyote time, jump buffer, slope limit, step offset. **No constants in the controller.**
4. Model states with `PACK/templates/csharp/StateMachine.cs.txt`: `Grounded`, `Airborne`, and
   whatever the spec adds (`Dashing`, `Climbing`). Three or more states means a state machine, not
   booleans.
5. Ground detection — the usual source of bugs. Do **not** rely on `isGrounded` alone:
   - `CharacterController.isGrounded` is only valid immediately after `Move`, and is false on the
     first frame of a step or slope.
   - Use a `SphereCast` down from the capsule base with a small skin offset, against a ground
     `LayerMask` that excludes the player's own layer. Use the non-allocating overload.
   - Add **coyote time** from the tuning asset: remain "grounded" for a few frames after leaving the
     ground. Without it, jumps feel like they are being dropped.
6. Camera-relative movement: convert input to world space using the camera's yaw only.
   ```
   flatForward = Vector3.ProjectOnPlane(cameraForward, Vector3.up).normalized
   ```
   Using the camera's full forward makes the character walk into the ground when the camera pitches.
7. Jump from height, not from an invented impulse: `v = sqrt(2 * g * jumpHeight)`. That makes the
   designer's "jump 2 metres" literally true, and keeps jump height stable if gravity changes.
8. Apply gravity yourself with `CharacterController`, accumulating vertical velocity and resetting it
   on ground contact — but reset it to a small negative value, not zero, so the controller stays
   snapped to the ground on slopes.
9. Add a **jump buffer**: remember a jump pressed shortly before landing and execute it on landing.
   With coyote time, this is most of what "responsive" means.
10. Read input in `Update`, store intent, and apply movement in one place. For `CharacterController`
    that is `Update`; for `Rigidbody` it is `FixedUpdate`. Never read input in `FixedUpdate`.
11. Set `slopeLimit` and `stepOffset` from the tuning asset. `stepOffset` must be less than the
    capsule height, or the controller behaves erratically.
12. Verify:
    ```bash
    unity recompile --strict --format json
    ```
    then `qa-playmode-check` against the spec: walk up and down the steepest intended slope, up
    every step height, jump the exact stated height, hold against a wall, and jump at the edge of a
    platform to confirm coyote time.

## Unity CLI commands used

```bash
unity status                              # live Editors: port, project path, version, PID
unity list                                # Editor-registered tools and their parameter schemas
unity commands --format json              # full CLI command manifest
unity recompile --strict --format json    # compile check
unity test --format json                  # PlayMode tests; step physics with WaitForFixedUpdate
```

See `PACK/references/unity-cli.md`. Measure the achieved jump height by reading it back from the
Editor rather than asserting it from the formula.

## Files to read (exact paths)

| Need | Path |
| --- | --- |
| Project status and dimension | `design/STATE.md` |
| Design map | `design/INDEX.md` |
| Rules, tuning values, feel targets | `design/mechanic-*.md` (named in `INDEX.md`) |
| Recorded controller choice | `design/tech-decisions.md` |
| State machine template | `PACK/templates/csharp/StateMachine.cs.txt` |
| Component template | `PACK/templates/csharp/MonoBehaviour.cs.txt` |
| Input conventions | `PACK/references/input-system.md` |
| Camera rig | `PACK/skills/3d-cinemachine-camera/SKILL.md` |
| Non-alloc queries, per-frame budget | `PACK/rules/performance.md` |
| Style rules | `PACK/rules/csharp-style.md` |

## Done checklist

- [ ] Controller choice recorded in `design/tech-decisions.md`.
- [ ] Every tuning value lives on a ScriptableObject; no constants in the controller.
- [ ] States use the state machine template, not a set of booleans.
- [ ] Ground detection uses a non-allocating cast with a layer mask, not `isGrounded` alone.
- [ ] Coyote time and jump buffering are implemented with values from the tuning asset.
- [ ] Movement is camera-relative using yaw only.
- [ ] Jump velocity is derived from the target height.
- [ ] Grounded vertical velocity resets to a small negative value, not zero.
- [ ] Input is read in `Update`; `Rigidbody` motion is applied in `FixedUpdate`.
- [ ] `stepOffset` is less than the capsule height.
- [ ] Verified in play mode: slopes, steps, exact jump height, wall contact, coyote time at an edge.

## Common mistakes

- Trusting `CharacterController.isGrounded`, which is false on the first frame of a slope or step and
  only meaningful right after `Move`.
- Resetting grounded vertical velocity to exactly zero, so the character skips down slopes instead
  of staying snapped.
- Camera-relative movement using the camera's full forward vector, so the character walks into the
  floor as the camera pitches down.
- An invented jump impulse, so "jump 2 metres" is never actually 2 metres and retuning gravity
  silently changes it.
- No coyote time or jump buffer, giving a controller that is technically correct and feels broken.
- Reading input in `FixedUpdate`, dropping or doubling presses.
- Allocating ground-check raycasts every frame, causing GC stutter read as low frame rate.
- A ground `LayerMask` that includes the player, so the character is always "grounded" on itself.
- `stepOffset` larger than the capsule, producing erratic climbing.
- Writing `transform.position` on a `Rigidbody` character, teleporting through collision.
