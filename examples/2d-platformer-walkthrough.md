# Walkthrough: a 2D platformer from nothing

A complete pass from a one-line pitch to a running build, showing which skill handles each step and
what it asks you for. Prompts are in blockquotes.

**Prerequisites:** the Unity CLI connected to an open Unity 6.3 LTS project
([../docs/INSTALL.md](../docs/INSTALL.md)), and this pack installed.

> This walkthrough has not been executed against a live Unity Editor. It documents the intended
> flow, the decision points and the failure modes — not a recorded session.

---

## 1. Pitch to design docs

> "I want a 2D platformer where a courier delivers parcels across rooftops during a storm. Use the
> unity-game-router skill."

`unity-game-router` reads `design/STATE.md`, finds nothing, and routes to **`design-write-gdd`**.

It will push back on three things, and these are the ones worth answering carefully:

- **Pillars** — at most three. "Momentum you can lose", "the storm is the antagonist", "every roof
  is a readable puzzle". A pillar that rules nothing out is not a pillar.
- **Dimension** — `2D` here. This decides camera, renderer, physics and art cost, so it is recorded
  in both `pitch.md` and `STATE.md`.
- **Minimum playable** — the smallest build that proves the loop. Probably: run, jump, one roof, one
  parcel.

You get `design/pitch.md`, `design/STATE.md`, `design/INDEX.md`.

## 2. Lock the art style

> "Lock the art style. Here's a reference image: art-source/reference/rooftop-mood.png"

**`assets-art-style-lock`** creates `design/art-bible.md`.

**Give it a real reference image.** A style cannot be locked with adjectives — "stylised pixel art"
produces a different result on every generation, and the set will not match itself.

It fills the 2D spec block, and these feed every later step:

| Field | Example | Why it matters later |
| --- | --- | --- |
| PPU | 32 | **One value project-wide.** Different PPUs mean nothing is the right relative size |
| Sprite resolution | character 32×32 | Generation requests use this exact size |
| Pivot | Bottom-Center | Characters stand on the ground instead of floating |
| Filter mode | Point | Bilinear gives permanently blurry pixel art |
| Compression | None | Compressed pixel art has colour artefacts nothing recovers |
| Frame rate | 12 fps | Clips authored at 12 but sampled at Unity's default 60 play five times too fast |

Status goes 🟢 only when the reference image, style prompt, negative prompt, palette and 2D specs
are all real. Until then the generation skills refuse to run.

## 3. Scene and input

> "Set up the bootstrap scene and player input."

**`core-scene-setup`** creates `Bootstrap.unity` (first in Build Settings, never unloaded, owns the
services) and the gameplay scene loaded additively. For 2D it sets an orthographic camera and
confirms every quality tier has a URP Asset using the **2D Renderer**.

**`core-input-setup`** creates `Assets/Settings/Input/GameInput.inputactions` with the `Player`,
`UI` and `Debug` maps, adds `Move` (Value/Vector2, 2D Vector composite, stick deadzone) and `Jump`
(Button), then **regenerates the C# class**.

> **Most common failure here:** editing the actions asset and not regenerating the C# wrapper. The
> new action then appears not to exist, and nothing explains why.

## 4. Spec the movement before writing it

> "Spec the movement mechanic."

**`design-mechanic-spec`** writes `design/mechanic-movement.md`. The sections that matter:

**Rules** — numbered, with numbers:
1. Move applies up to 6 m/s horizontally, reached over 0.12 s.
2. Jump applies 7.5 m/s upward velocity.
3. Jump is ignored while not grounded.
4. Releasing Jump early halves upward velocity.

**Feel** — coyote time 0.1 s, jump buffer 0.12 s, no air deceleration.

**Acceptance checks** — what `qa-playmode-check` will measure:
- [ ] Holding Move for 1 s moves the player 5 ± 0.2 units.
- [ ] Jump from flat ground peaks at 2.8 ± 0.15 units.
- [ ] Jumping within 0.1 s of leaving a ledge still jumps.
- [ ] Nothing logs an error to the console during the check.

Numbers you did not supply are proposed **and flagged as proposals**. Correct them here, not in the
code — it is far cheaper.

## 5. Physics — the branch that bites

> "Implement the movement."

**`2d-physics-setup`** stops and determines which 2D physics system the project uses, by looking at
the scene components rather than guessing.

> **Unity 6 has two 2D physics systems. They share no code and never interact.** Legacy
> (`Rigidbody2D`, `Collider2D`) and 2D Physics Core (`Unity.U2D.Physics`, needs `com.unity.2d.physics`
> and Unity 6000.7+). Code written against the wrong one **compiles, runs, and does nothing** — and
> nothing in the console tells you why.

On a `6000.3.x` baseline it will be legacy. The decision gets written to `design/tech-decisions.md`
so no later agent re-derives it.

It then sets the **layer collision matrix explicitly** (the default has everything colliding with
everything), and **`core-scriptable-object-data`** puts every tuning number on
`Assets/_Project/Data/Tuning/Player_MovementData.asset`. **`core-unity-script`** writes the
controller from the templates.

## 6. The level

> "Build the first rooftop level."

**`2d-tilemap-level`** builds the Grid (cell size `1,1,0`, unscaled) and the layer stack —
`Background`, `Ground`, `Decoration`, `Foreground` — with collision on `Ground` only, using
`TilemapCollider2D` **plus** `CompositeCollider2D` with Used By Composite.

> Without the composite, every tile is its own collider and the character catches on every seam
> between them. It reads as a physics bug and is a setup one.

Palettes and rule tiles go to `/unity:create-tile-palette-or-rule-tiles` if Unity's plugin is
installed.

## 7. Art

> "Generate the courier sprites and a rooftop tileset."

**`assets-gen-2d-sprite`** uses the art bible's style prompt **verbatim** plus the subject, with a
transparent background, at the art bible's resolution. Masters land in `art-source/generated/`,
outside `Assets/` so Unity never imports them.

Review against the **reference image**, not the prompt text. Then:

- **`2d-sprite-import`** applies PPU, pivot, filter and compression, and adds the sprites to an atlas.
  Unatlased sprites are one draw call each.
- `PACK/scripts/slice-spritesheet.py --cell 32x32` for a uniform sheet; it handles the top-left to
  bottom-left origin flip that otherwise makes animations play out of order.
- **`2d-sprite-animation`** builds clips at the art bible's frame rate, and an Animator driven by
  **parameters** (`Speed`, `IsGrounded`, `VerticalVelocity`) with transition durations of **0**.

> Never call `Animator.Play("Run")` from code. It creates a second source of truth that drifts from
> the gameplay state machine.

## 8. Verify

> "Verify the movement against the spec."

**`qa-playmode-check`** starts from `Bootstrap` — not by opening the gameplay scene directly — and
walks each acceptance check, recording the **observed** value:

```
- [x] Holding Move for 1s moves 5 units — observed: 4.94
- [x] Jump peaks at 2.8 units — observed: 2.83
- [ ] Coyote time at a ledge — observed: jump dropped. FAILED
```

A console warning fails the check even if the mechanic looked right. If no Editor is reachable, the
report says **"not verified"** — it never infers a pass.

## 9. Build

> "Ship a Windows build."

**`qa-run-tests`** then **`qa-build`**. The build gates on a clean `unity recompile --strict` and a
green suite, discovers real targets with `unity build --list-targets`, confirms `Bootstrap` is first
in the scene list, and then **launches it** with `unity build run`.

> "It built" is not "it runs". The black-screen-on-launch bug is almost always the wrong first scene.

## 10. Record where you are

Every task ends at **`design-update-state`**. A mechanic that only compiles is `prototyped`; it
becomes `playable` only after `qa-playmode-check` passed with a clean console.

---

## The failures this flow is built to prevent

| Failure | Prevented by |
| --- | --- |
| 2D physics code that compiles and does nothing | `2d-physics-setup` detecting the system instead of guessing |
| An art set where nothing matches | `assets-art-style-lock` as a hard gate |
| Sprites the wrong relative size | one project-wide PPU, and never fixing size with Transform scale |
| Character catching on tile seams | `CompositeCollider2D` with Used By Composite |
| "Done" being a matter of opinion | acceptance checks written before the code |
| Work redone next session | `design-update-state` and an honest status rung |
