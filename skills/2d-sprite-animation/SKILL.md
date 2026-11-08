---
name: 2d-sprite-animation
description: Build sprite-sheet animation for a 2D character or prop - clips from sliced sprites, an Animator with parameter-driven states, and code that sets parameters rather than playing clips by name. Use when animating 2D art or fixing animation that does not match state.
metadata:
  version: 0.1.0
---

# 2D sprite animation

Paths written as `PACK/` mean `.unity-skillforge/` in a game repo, or this pack's root.

## When to use

- Animating a 2D character or prop from a sprite sheet.
- Animation not matching the character's actual state, or getting stuck in one clip.
- Adding a new animation state to an existing Animator.

## Inputs needed

- Sliced sprites, already imported at the project PPU via `2d-sprite-import`.
- The animation frame rate from `design/art-bible.md` → 2D specifications.
- The character's states, from the mechanic spec. If the behaviour uses a state machine, the
  Animator should mirror it rather than invent its own states.

## Steps

1. Read `design/STATE.md`, `design/INDEX.md`, `design/art-bible.md` → 2D specifications, and the
   mechanic spec's rules.
2. Confirm the sprites are sliced and named `<sheet>_<index>` in order. Out-of-order slices produce
   an animation that plays backwards or jumps, and that is an import problem, not an animation one.
3. Create one clip per state at `Assets/_Project/Art/Animations/<Subject>/<Subject>_<Action>.anim`,
   per `PACK/rules/folder-conventions.md`. Set the clip's sample rate to the art bible frame rate —
   not Unity's default 60.
4. Set looping correctly per clip: `Idle`, `Run` loop; `Jump`, `Attack`, `Death` do not. A
   non-looping clip left looping is why a death animation restarts forever.
5. Create the Animator Controller at
   `Assets/_Project/Art/Animations/<Subject>/<Subject>.controller`.
6. Drive transitions with **parameters**, never by playing clips by name from code:
   | Parameter | Type | Set from |
   | --- | --- | --- |
   | `Speed` | Float | movement magnitude |
   | `IsGrounded` | Bool | ground check |
   | `VerticalVelocity` | Float | rigidbody velocity y |
   | `Attack` | Trigger | the attack action |
   | `IsDead` | Bool | health reaching zero |
7. Set transition durations to **0** for sprite animation. Blending between two sprite frames does
   nothing useful and only adds latency.
8. Cache parameter hashes once (`Animator.StringToHash`) and set parameters by hash. Setting by
   string every frame allocates and is banned by `PACK/rules/performance.md`.
9. Mirror, do not duplicate, the gameplay state machine. If the behaviour uses
   `PACK/templates/csharp/StateMachine.cs.txt`, the Animator reads the same conditions rather than
   maintaining a second, divergent idea of state.
10. Flip facing with `SpriteRenderer.flipX` or a Y rotation of 180 — not a negative Transform scale,
    which breaks child colliders and physics.
11. Set the `SpriteRenderer` sorting layer and order per `25d-sorting-and-depth` conventions if the
    project is 2.5D, otherwise per the project's 2D sorting layers.
12. Verify:
    ```bash
    unity recompile --strict --format json
    ```
    then `qa-playmode-check`: every state reached, none stuck, transitions match the mechanic rules.

## Unity CLI commands used

```bash
unity status                              # live Editors: port, project path, version, PID
unity list                                # Editor-registered tools and their parameter schemas
unity commands --format json              # full CLI command manifest
unity recompile --strict --format json    # compile check
unity test --format json                  # PlayMode tests asserting the active state
```

Clip and Animator authoring is Editor work: use the tools `unity list` reports, or a checked-in
Editor script run with `eval_file`. Use fully-qualified names such as
`UnityEditor.Animations.AnimatorController`. See `PACK/references/unity-cli.md`.

## Files to read (exact paths)

| Need | Path |
| --- | --- |
| Project status | `design/STATE.md` |
| Design map | `design/INDEX.md` |
| Frame rate and 2D specs | `design/art-bible.md` |
| States and rules | `design/mechanic-*.md` (named in `INDEX.md`) |
| Animation folder layout and naming | `PACK/rules/folder-conventions.md` |
| No per-frame string allocation | `PACK/rules/performance.md` |
| State machine template | `PACK/templates/csharp/StateMachine.cs.txt` |
| Sorting conventions | `PACK/skills/25d-sorting-and-depth/SKILL.md` |

## Done checklist

- [ ] Sprites are sliced and ordered correctly before any clip was made.
- [ ] Clip sample rate matches the art bible frame rate, not Unity's default.
- [ ] Looping is set per clip; one-shot clips do not loop.
- [ ] Transitions are driven by parameters, not by playing clips by name.
- [ ] Transition durations are 0.
- [ ] Parameters are set by cached hash, not by string every frame.
- [ ] The Animator mirrors the gameplay state machine; there is no second source of truth.
- [ ] Facing uses `flipX` or a Y rotation, not a negative scale.
- [ ] Sorting layer and order are set deliberately.
- [ ] Verified in play mode: every state reachable, none stuck.

## Common mistakes

- Calling `Animator.Play("Run")` from code, which creates a second source of truth that drifts from
  the gameplay state machine.
- Leaving the clip sample rate at 60 when the art is authored at 12, so everything plays too fast.
- A non-looping clip left looping, so death or attack animations restart forever.
- Non-zero transition durations, which cross-fade sprite frames into mush and add input latency.
- `SetFloat("Speed", v)` by string every frame, allocating in a per-frame path.
- Negative Transform scale to flip a character, which inverts child colliders and physics behaviour.
- Animating from unsliced or wrongly ordered sprites and then debugging the Animator.
- Forgetting a transition out of a state, so the character is stuck in it with no error logged.
