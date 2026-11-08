---
name: qa-build
description: Produce a player build with the Unity CLI using a named build profile, then verify it launches. Use when a shippable or testable build is needed. Defer to Unity's build-gtk and build-live-game skills for platform specifics and store requirements.
metadata:
  version: 0.1.0
---

# Build

Paths written as `PACK/` mean wherever this pack's own files live: `.unity-skillforge/` in a game
repo (created by `install.sh`), the plugin's root directory when installed as a plugin, or the
repo root when working on the pack itself.

## When to use

- A testable or shippable player build is needed.
- Verifying that something working in the Editor also works in a build.
- Setting up a build profile for a new target.

## Prefer the official skill

If Unity's official plugin is installed:

- `/unity:build-gtk` — platform build specifics and the go-to-market checklist.
- `/unity:build-live-game` — live-game and backend-connected builds.
- `/unity:manage-cloud-build` — Unity Build Automation.
- `/unity:optimize-web` — WebGL builds specifically.

What stays ours: the **target matrix, build-profile naming, and the pre-build gate** below. Do not
restate platform build procedures — link them. See `PACK/references/official-unity-skills.md`.

## Inputs needed

- The target platform and whether it is a development or release build.
- The target from `design/STATE.md`; if it is not recorded there, ask rather than guessing.
- Signing or store credentials for a release build. These come from environment variables and are
  **never** committed.

## Steps

1. Read `design/STATE.md` for the target platform and frame target.
2. **Pre-build gate — all three must pass before building.** A build on a dirty project wastes
   minutes and produces an artefact nobody can trust.
   ```bash
   unity status
   unity recompile --strict --format json    # zero errors, zero warnings
   unity test --format json                  # suite green
   ```
   If either fails, stop: `qa-fix-console-errors`, then `qa-run-tests`.
3. Discover what this project can actually build, instead of assuming:
   ```bash
   unity build --list-targets
   unity build --list-profiles
   ```
4. If no profile exists for the target, create one and name it `<Target>-<Dev|Release>`:
   ```bash
   unity build --create-profile <target>
   ```
   Store build profiles under `Assets/Settings/Build/` per `PACK/rules/folder-conventions.md`.
5. Confirm the scene list: `Bootstrap` **first**, then the gameplay scenes. A build with the wrong
   first scene starts on a black screen and no service registered.
6. Confirm the quality tier used by the build has a URP Asset assigned
   (`PACK/references/urp-settings.md`). A tier set to `None` falls back to Built-in and renders wrong
   in the build only.
7. Run the build, capturing structured output:
   ```bash
   unity build --format json
   ```
   Check `success`, `errors` and `warnings` in the envelope as well as the exit code
   (`0` ok, `1` error, `2` usage, `130` cancelled).
8. Launch and smoke-test it — a build that compiles is not a build that runs:
   ```bash
   unity build run
   ```
   Confirm it boots from `Bootstrap`, the first interaction works, and nothing logs an error.
9. For a release build, confirm `Debug` input bindings are stripped and development build flags are
   off.
10. Report the artefact path, the size, the target, and the build duration. Then update
    `design/STATE.md` via `design-update-state`.

## Unity CLI commands used

```bash
unity status                              # live Editors: port, project path, version, PID
unity commands --format json              # full CLI command manifest
unity recompile --strict --format json    # pre-build gate
unity test --format json                  # pre-build gate
unity build --list-targets                # what this install can target
unity build --list-profiles               # existing build profiles
unity build --create-profile <target>     # create a Unity 6 build profile
unity build --format json                 # the build itself
unity build run                           # launch the most recent recorded build
```

`unity build` runs in batch mode with CI-friendly flags, including Android signing and export
options. Flags differ by version — run `unity build --help` for the authoritative list on the
installed CLI. See `PACK/references/unity-cli.md`.

For CI, authenticate with a service account rather than an interactive login:
`UNITY_SERVICE_ACCOUNT_ID`, `UNITY_SERVICE_ACCOUNT_SECRET`.

## Files to read (exact paths)

| Need | Path |
| --- | --- |
| Target platform and frame target | `design/STATE.md` |
| Design map | `design/INDEX.md` |
| CLI surface, exit codes, CI auth | `PACK/references/unity-cli.md` |
| Official build skills | `PACK/references/official-unity-skills.md` |
| URP tiers and renderer | `PACK/references/urp-settings.md` |
| Version and package pins | `PACK/references/unity-versions.md` |
| Build profile location | `PACK/rules/folder-conventions.md` |
| Frame budget to check against | `PACK/rules/performance.md` |

## Done checklist

- [ ] `unity recompile --strict` clean and `unity test` green **before** the build started.
- [ ] Target and profile chosen from `--list-targets` / `--list-profiles`, not assumed.
- [ ] Profile named `<Target>-<Dev|Release>` and stored under `Assets/Settings/Build/`.
- [ ] `Bootstrap` is the first scene in the build list.
- [ ] The build's quality tier has a URP Asset assigned.
- [ ] `unity build --format json` returned `success: true`.
- [ ] The build was launched and smoke-tested, not just compiled.
- [ ] Release builds have `Debug` bindings stripped and development flags off.
- [ ] No credentials committed; CI uses service-account environment variables.
- [ ] Artefact path, size, target and duration reported.

## Common mistakes

- Building on a project with warnings, then debugging a build-only failure that `--strict` would
  have caught in seconds.
- Assuming a target is installed. `unity build --list-targets` is the only honest source; a missing
  platform module fails late and confusingly.
- The wrong first scene, so the build boots with no services registered and a black screen.
- A quality tier without a URP Asset — fine in the Editor, wrong in the build.
- Reporting success from the exit code without checking `success` and `warnings` in the envelope.
- Calling it done without launching it. "It built" is not "it runs".
- Shipping a release build with development flags or Debug bindings still active.
- Hardcoding a keystore password or token into a profile or script instead of an environment variable.
