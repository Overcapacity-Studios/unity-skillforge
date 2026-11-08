# Unity version and package pins

**Snapshot 2026-11-08.** Source: <https://unity.com/releases/unity-6/support>

## Editor

| Stream | Status | Supported until |
| --- | --- | --- |
| Unity 6.0 LTS (`6000.0.x`) | **End of support** | October 2026 — expired |
| **Unity 6.3 LTS (`6000.3.x`)** | **Current LTS — our baseline** | December 2027 |
| Update releases (e.g. `6000.7.x`) | Supported | Until the next release publishes |

Version-prefix map: Unity `6.3` is `6000.3.x` (Unity's own CLI docs use `unity install 6000.3.7f1`
as the example). Unity `6.7` is `6000.7.x`.

- **Baseline for this pack: `6000.3.x` (Unity 6.3 LTS).**
- Driving a running Editor through the Pipeline package needs Unity 6.0 or later.
- Install with `unity install 6000.3.7f1`, or `unity install lts` to track the current LTS.
- Never target `6000.0.x` in new work — it is out of support.

## Render pipeline and input

- **URP** is the pipeline for every project in this pack. Built-in RP is not supported here; if you
  inherit a Built-in RP project, Unity's official `/unity:migrate-birp-to-urp` skill owns that move.
- **New Input System** (`com.unity.inputsystem`) only. Do not use `UnityEngine.Input`, `Input.GetKey`
  or `Input.GetAxis` — they are the legacy manager and are banned by `rules/csharp-style.md`.
- Set Active Input Handling to **Input System Package (New)**, not "Both", unless a third-party
  package forces it; record the exception in `design/tech-decisions.md`.

## The 2D physics split — read this before any 2D physics work

Unity 6 has **two 2D physics systems. They share no code and never interact.** Code written against
the wrong one compiles, runs, and does nothing.

| Signal in the project | System |
| --- | --- |
| Physics Pose, Physics Area, Constraint or Simulation components | **Core components** — needs `com.unity.2d.physics` and Unity `6000.7+` |
| `Rigidbody 2D`, `Collider 2D`, `Joint 2D`, `Effector 2D` components | **Legacy** |
| `Unity.U2D.Physics` or `UnityEngine.LowLevelPhysics2D` types in scripts | **Core, in script** (no package needed) |
| `Rigidbody2D`, `Collider2D`, `Physics2D` types in scripts | **Legacy** |
| Both present | Two separate simulations — treat them separately and say so |
| No signal at all | **Stop and ask.** Do not choose for the user |

Check scene components first (components are the reliable signal), then the wording of the request,
then probe the project. On a `6000.3.x` baseline the Core *components* are unavailable, so legacy is
the default — but always verify rather than assume.

## Package pins

Pin exact versions in `Packages/manifest.json`; never rely on a floating version. Record the version
you actually resolved in `design/tech-decisions.md` so a later agent can reproduce the project.

Packages this pack touches: `com.unity.render-pipelines.universal`, `com.unity.inputsystem`,
`com.unity.cinemachine` (3.x API — not 2.x), `com.unity.ai.navigation`, `com.unity.2d.tilemap`,
`com.unity.2d.sprite`, `com.unity.test-framework`, `com.unity.pipeline` (installed by
`unity pipeline install`).

Verify what is actually installed before writing code against it:

```bash
unity command --format json   # discover the Editor's registered tools first
```

then read `Packages/manifest.json` and `Packages/packages-lock.json` directly.
