# Walkthrough: a 3D third-person game from nothing

A complete pass from pitch to build for a 3D project, including the generated-3D-asset pipeline.
Prompts are in blockquotes.

**Prerequisites:** the Unity CLI connected to an open Unity 6.3 LTS project
([../docs/INSTALL.md](../docs/INSTALL.md)), and this pack installed. The Meshy section additionally
needs a paid Meshy plan and its MCP server configured.

> This walkthrough has not been executed against a live Unity Editor. It documents the intended
> flow, the decision points and the failure modes — not a recorded session.

---

## 1. Pitch to design docs

> "A third-person exploration game: a surveyor mapping an abandoned research station. Use the
> unity-game-router skill."

**`design-write-gdd`** produces `pitch.md`, `STATE.md` and `INDEX.md`.

**Dimension: 3D.** The cost is real and worth stating up front — 3D means the most expensive art,
the most systems, and lighting that must be baked and verified in a build rather than judged in the
viewport. If the game would work with a fixed camera, 2.5D is dramatically cheaper; see
[2d-platformer-walkthrough.md](2d-platformer-walkthrough.md) for the 2D end of that spectrum.

## 2. Architecture decisions, before any code

> "Use the architect agent to decide the structure."

The **architect** records decisions in `design/tech-decisions.md` that everything downstream
depends on:

| Decision | Options | Why it matters |
| --- | --- | --- |
| Character controller | `CharacterController` vs `Rigidbody` | Switching later is a rewrite |
| Renderer | Universal: Forward, Forward+, Deferred | Changing it **invalidates light bakes** |
| Colour space | **Linear** | Gamma breaks lighting maths and is not recoverable |
| Cinemachine | **3.x** | 2.x code will not compile against it |

Default to **`CharacterController`** for precise platforming feel; choose `Rigidbody` only if the
character must genuinely be pushed by physics.

## 3. Lock the art style

> "Lock the art style from this reference: art-source/reference/station-mood.png"

**`assets-art-style-lock`** fills the **3D** spec block, which drives every import later:

| Field | Example | Why |
| --- | --- | --- |
| Scale | 1 unit = 1 m, character 1.8 m | Fix scale at import, never with Transform scale |
| Axis | Y up, +Z forward | glTF matches Unity; FBX from many tools is Z-up |
| Poly budget | character 15k, prop 2k | `meshy_remesh` targets this |
| LODs | LOD0 100%, LOD1 50%, LOD2 25% | Set against real camera distance |
| Texture resolution | 1024 character, 512 prop | Import Max Size |
| Material | URP Lit | Built-in materials render **magenta** in URP |
| Rig | Humanoid | Decides Avatar setup and retargeting |

## 4. Scene, input and camera

> "Set up the bootstrap scene, input and the third-person camera."

**`core-scene-setup`** builds `Bootstrap.unity` and the gameplay scene, with the **Universal
Renderer** and one global Volume.

**`core-input-setup`** adds `Move` and `Look` (both Value/Vector2 with stick deadzones) and `Jump`.

**`3d-cinemachine-camera`** adds one `CinemachineBrain` and `CM_Gameplay` with an orbital follow,
aiming at a **dedicated child transform** of the character rather than the root — otherwise the
camera inherits every animation bob.

> **Check the Cinemachine pin first.** A wall of `CS0246` on camera code almost always means 2.x API
> against a 3.x package: `CinemachineVirtualCamera` is now `CinemachineCamera`.
>
> **Never shake the camera by writing to its transform.** The brain overwrites it every frame, so
> the shake silently does nothing. Use `CinemachineImpulse`.

## 5. Spec the locomotion

> "Spec the locomotion mechanic."

**`design-mechanic-spec`** writes `design/mechanic-locomotion.md`:

**Rules:** walk 2 m/s, sprint 5.5 m/s, acceleration 0.15 s, jump height exactly 1.2 m, slope limit
45°, step offset 0.3 m.

**Acceptance checks:**
- [ ] Jump from flat ground peaks at 1.2 ± 0.05 m.
- [ ] Walking up a 44° slope succeeds; 46° does not.
- [ ] A 0.3 m step is climbed without a jump.
- [ ] Jumping within 0.1 s of leaving a ledge still jumps.
- [ ] Holding into a wall does not stick or climb.
- [ ] Nothing logs an error to the console during the check.

## 6. The controller

> "Implement the locomotion."

**`3d-character-controller`** builds it from the templates, with tuning on
`Player_MovementData.asset`. The parts that are usually got wrong:

- **Ground detection does not use `isGrounded` alone.** `CharacterController.isGrounded` is only
  valid right after `Move` and is false on the first frame of a slope or step. A non-allocating
  `SphereCast` against a ground `LayerMask` that excludes the player replaces it.
- **Jump velocity is derived from the target height:** `v = sqrt(2 * g * height)`. That makes "jump
  1.2 m" literally true and keeps it stable if gravity is retuned.
- **Grounded vertical velocity resets to a small negative value, not zero**, so the controller stays
  snapped to slopes instead of skipping down them.
- **Camera-relative movement uses yaw only** — `Vector3.ProjectOnPlane(cameraForward, Vector3.up)`.
  Using the camera's full forward makes the character walk into the floor as the camera pitches.
- Three or more states means `StateMachine.cs.txt`, not booleans.

## 7. Generate the character and props

> "Generate the surveyor character and three props."

**`assets-gen-3d-model`** gates on the art bible, then:

1. Runs `meshy_check_balance` and **reports the cost before spending**. Generation uses real credits.
2. Uses `meshy_image_to_3d` if concept art exists — it holds style far better than text alone —
   otherwise `meshy_text_to_3d` then `meshy_text_to_3d_refine`.
3. **Polls `meshy_get_task_status` until complete.** Generation is asynchronous; downloading early
   gets a partial or missing result.
4. `meshy_remesh` to hit the poly budget; `meshy_retexture` if the texture is off-palette.
5. `meshy_rig` then `meshy_animate` **only for the character**. Static props stop at the mesh —
   rigging costs credits and locks in a skeleton nobody needs.
6. `meshy_download_model` into `art-source/generated/`, outside `Assets/`.

Exact tool names are in [../references/meshy-mcp-tools.md](../references/meshy-mcp-tools.md). They
are snake_case with a `meshy_` prefix; inventing a variant is the usual failure.

## 8. Import — where raw downloads become assets

> "Import the surveyor model."

**A downloaded `.glb` dropped into `Assets/` is not a finished asset.** **`assets-import-pipeline`**
handles:

| Problem | Fix |
| --- | --- |
| Wrong size | Importer **Scale Factor**, never Transform scale — a scaled Transform breaks physics, colliders and LOD distances |
| On its side or facing backwards | Fix at import, **not** with a rotated parent, which breaks root motion |
| Renders magenta | Convert Built-in materials to URP Lit, in one pass, sharing materials so the SRP Batcher keeps working |
| Lighting subtly wrong | Normal maps **must** be marked Normal Map; sRGB **off** for roughness and metallic |
| Animations will not retarget | Humanoid Avatar with every bone verified, then **Copy From Other Avatar** for shared clips |
| Mesh memory doubled | Read/Write **off** unless something genuinely needs mesh data at runtime |

## 9. Lighting

> "Light the station interior."

**`3d-urp-lighting`** confirms Linear colour space and a URP Asset on **every** quality tier, adds
one directional key light, then bakes:

- **Start lightmap resolution low** (10–20 texels/unit) and raise it only where seams show. Starting
  high makes every iteration a long bake for no visible gain.
- **Adaptive Probe Volumes** over hand-placed light probe groups.
- Shadow cascades sized to the scene, since each is a full extra shadow render.
- **Judge quality with lightmap compression off**, then enable it for shipping — compression
  artefacts are easily mistaken for bake errors.

> **Re-bake after any renderer, colour-space or light-mode change.** Stale lightmaps render
> convincingly and are wrong.

## 10. Enemies

> "Add patrolling drones."

**`design-mechanic-spec`** first — "make a drone that chases" is not enough to build against. Then
**`3d-navmesh-ai`**:

- `NavMeshSurface` from `com.unity.ai.navigation`, not the legacy scene-wide bake.
- **Agent radius must match the character's actual capsule**, or agents clip corners or refuse
  doorways.
- `NavMeshLink` wherever agents drop or climb. **Disconnected NavMesh islands are the usual cause of
  "the agent just stands there"** — there is no path, and nothing is logged.
- Behaviour in a state machine; the agent only moves. `SetDestination` on change, not every frame.
- Check `pathStatus` and handle `PathPartial` / `PathInvalid`, or an unreachable target walks an
  agent into a wall forever.

## 11. Verify and build

> "Verify locomotion, then make a build."

**`qa-playmode-check`** starts from `Bootstrap` and reports **observed** values per check. Then
**`qa-run-tests`** and **`qa-build`**, which launches the result with `unity build run`.

> **Works in the Editor, broken in the build** — in order of likelihood: a ScriptableObject being
> mutated at runtime, a cross-scene Inspector reference, a quality tier with no URP Asset, or stale
> lightmaps.

## 12. Review

> "Use the reviewer agent on this change."

The **reviewer** re-runs the checks rather than trusting the report, and ranks findings blocking /
should-fix / nit. It treats a **claimed but unverified** play-mode result as a high-severity
finding: a false pass is worse than a known failure.

---

## The failures this flow is built to prevent

| Failure | Prevented by |
| --- | --- |
| Camera code that will not compile | Pinning Cinemachine 3.x before writing any |
| A character that skips down slopes | Grounded velocity reset to a small negative, not zero |
| "Jump 1.2 m" that is never 1.2 m | Deriving jump velocity from the target height |
| Magenta models | `assets-import-pipeline` converting materials, not a manual pass |
| Physics broken by an asset import | Fixing scale at import rather than with Transform scale |
| Credits spent twice | The art-bible gate, and reporting cost before generating |
| Agents standing still with no error | `NavMeshLink` and checking `pathStatus` |
| Lighting signed off that is wrong in the build | Verifying in a build and on a second quality tier |
