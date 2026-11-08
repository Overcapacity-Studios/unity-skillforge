---
name: 3d-cinemachine-camera
description: Set up a Cinemachine 3.x camera rig for a 3D or 2.5D game - follow, orbit and aim cameras, collider and confiner extensions, and blends between cameras. Use for any gameplay camera. Defer to Unity's craft-game-floors camera-rigs reference for the recipes themselves.
metadata:
  version: 0.1.0
---

# Cinemachine camera

Paths written as `PACK/` mean wherever this pack's own files live: `.unity-skillforge/` in a game
repo (created by `install.sh`), the plugin's root directory when installed as a plugin, or the
repo root when working on the pack itself.

## When to use

- Setting up a follow, orbit, third-person or fixed gameplay camera.
- Blending between gameplay and cutscene or aim cameras.
- Fixing a camera that clips through walls, jitters, or lags the player.

## Prefer the official skill

If Unity's official plugin is installed:

- `/unity:craft-game-floors` — its `references/camera-rigs.md` is the **authoritative** set of
  Cinemachine 3.x recipes, including how to handle the 2.x API break. Use it for the recipe.

What stays ours: **camera naming, the per-genre defaults table, and the 2.5D angle constraint**
below. Do not restate Unity's recipes — link them. See
`PACK/references/official-unity-skills.md`.

## Cinemachine 3.x, not 2.x

Cinemachine 3 renamed most of the API. `CinemachineVirtualCamera` became `CinemachineCamera`, and
the body/aim components were renamed and restructured. Code or guidance written for 2.x will not
compile against 3.x. Confirm the pinned version in `Packages/manifest.json` and record it in
`design/tech-decisions.md` before writing any camera code
(`PACK/references/unity-versions.md`).

## Inputs needed

- The project dimension from `design/STATE.md`. **2.5D has a hard constraint** — see step 4.
- Genre and intended camera behaviour from `design/pitch.md`.
- The follow target, usually created by `3d-character-controller`.

## Steps

1. Read `design/STATE.md`, `design/INDEX.md`, `design/pitch.md`, and `design/tech-decisions.md`.
2. Confirm the Cinemachine 3.x pin. If the project is on 2.x, resolve that first — do not write
   code against both.
3. Add one `CinemachineBrain` to the main camera. Exactly one, in the scene that owns the camera.
4. **If the project is 2.5D:** the camera angle is fixed by `25d-ortho-3d-camera`. The rig may
   translate but must not change rotation. Do not add orbital or free-look behaviour, and do not let
   a blend rotate the camera — it will break art authored for one angle.
5. Create cameras with explicit names and priorities, so blends are predictable:
   | Name | Priority | Role |
   | --- | --- | --- |
   | `CM_Gameplay` | 10 | The default camera |
   | `CM_Aim` | 20 | Raised while aiming |
   | `CM_Cutscene` | 30 | Raised during a cutscene |
   Switch cameras by priority, never by enabling and disabling GameObjects — that loses blend state.
6. Pick the per-genre defaults, then tune against the mechanic spec's Feel section:
   | Genre | Body | Aim |
   | --- | --- | --- |
   | Third-person action | Orbital follow with a damped arm | Rotation composer on the character's chest height |
   | 2.5D / isometric | Position composer, **rotation locked** | None — keep the authored angle |
   | First person | Hard-locked to the head transform | Hard look at |
   | Top-down | Position composer with an offset | Hard look down |
7. Set damping deliberately and asymmetrically — more on Z than X for a follow camera. Zero damping
   feels rigid; too much feels like the camera is on a rubber band.
8. Add extensions rather than custom code:
   - `CinemachineDeoccluder` so the camera does not clip through geometry.
   - `CinemachineConfiner` to keep the camera inside play space.
   - `CinemachineImpulse` for shake. **Never shake by writing to the camera transform** — the brain
     overwrites it every frame and the shake silently does nothing.
9. Set the follow target to a dedicated child transform of the character, not the character root.
   That lets the camera target chest height without inheriting animation bob.
10. Verify:
    ```bash
    unity recompile --strict --format json
    ```
    then `qa-playmode-check`: walk against walls, into corners, and through the full camera range;
    trigger each blend. In 2.5D, confirm the angle never changes.

## Unity CLI commands used

```bash
unity status                              # live Editors: port, project path, version, PID
unity list                                # Editor-registered tools and their parameter schemas
unity commands --format json              # full CLI command manifest
unity recompile --strict --format json    # compile check; catches 2.x API usage immediately
unity test --format json                  # PlayMode tests for blends
```

Camera rig setup is Editor work: use the tools `unity list` reports, or an Editor script run with
`eval_file`. Use fully-qualified names such as `Unity.Cinemachine.CinemachineCamera`. See
`PACK/references/unity-cli.md`.

## Files to read (exact paths)

| Need | Path |
| --- | --- |
| Project dimension | `design/STATE.md` |
| Design map | `design/INDEX.md` |
| Genre and camera intent | `design/pitch.md` |
| Feel targets | `design/mechanic-*.md` (named in `INDEX.md`) |
| Cinemachine version pin | `design/tech-decisions.md` |
| Official camera-rig recipes | `PACK/references/official-unity-skills.md` |
| Package pins and Cinemachine 3.x note | `PACK/references/unity-versions.md` |
| 2.5D fixed-angle constraint | the `25d-ortho-3d-camera` skill |
| Follow target source | the `3d-character-controller` skill |

## Done checklist

- [ ] Cinemachine 3.x is pinned and recorded; no 2.x API is referenced.
- [ ] Exactly one `CinemachineBrain` on the main camera.
- [ ] Cameras are named `CM_*` with explicit priorities; switching is by priority, not by enabling.
- [ ] In a 2.5D project, the camera angle is locked and no camera rotates it.
- [ ] Body and aim match the genre table, then tuned against the Feel section.
- [ ] Damping is set deliberately and is not symmetric by accident.
- [ ] Deoccluder added where the camera could clip geometry.
- [ ] Shake uses impulse, not direct transform writes.
- [ ] The follow target is a dedicated child transform, not the character root.
- [ ] Verified in play mode against walls, corners and every blend.

## Common mistakes

- Writing Cinemachine 2.x API against a 3.x package, producing a wall of `CS0246` errors.
- Shaking the camera by writing to its transform, which the brain overwrites every frame — the shake
  does nothing and nothing explains why.
- Switching cameras by enabling and disabling GameObjects, which drops the blend and cuts hard.
- Adding orbital or free-look behaviour in a 2.5D project, breaking art authored for one angle.
- Following the character root, so the camera inherits every animation bob.
- Zero damping, giving a camera welded to the character, or heavy damping that feels elastic.
- No deoccluder, so the camera clips through walls in every corner.
- More than one `CinemachineBrain`, giving unpredictable control of the camera.
- Tuning the camera before the character controller exists, then retuning it all afterwards.
