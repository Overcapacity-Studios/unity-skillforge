---
name: qa-playmode-check
description: Verify a mechanic actually plays by running it in the Unity Editor and checking it against the acceptance checks in its spec. Use before calling any gameplay work done. Compiling and passing unit tests is not evidence the game plays correctly.
metadata:
  version: 0.1.0
---

# Play mode check

Paths written as `PACK/` mean wherever this pack's own files live: `.unity-skillforge/` in a game
repo (created by `install.sh`), the plugin's root directory when installed as a plugin, or the
repo root when working on the pack itself.

## When to use

- Before declaring any gameplay change done.
- After wiring an event channel, input action, or camera, where compiling proves nothing.
- When a mechanic is reported as "not feeling right".

Compiling is not playing. Unit tests passing is not playing. This skill is the gate.

## Prefer the official skill

If Unity's official plugin is installed:

- `/unity:unity-pipeline` — its `references/playmode-verification-loop.md` is authoritative for the
  Play Mode loop, hot reload and screenshots.

What stays ours: the **per-mechanic acceptance checks and the honesty rule** below. See
`PACK/references/official-unity-skills.md`.

## Inputs needed

- The mechanic's **Acceptance checks** list from its spec. If the spec has none, stop and run
  `design-mechanic-spec` — you cannot verify against an unstated expectation.
- A running Unity Editor with the Pipeline package installed.

## Steps

1. Read `design/STATE.md` and `design/INDEX.md`, then the mechanic spec's **Acceptance checks** and
   **Feel** sections.
2. Confirm the environment can actually be driven. If any of these fail, say so and stop — do not
   report a verification you could not perform:
   ```bash
   unity status                  # an Editor must be reachable
   unity pipeline list           # expect "Pipeline: Installed"
   unity recompile --strict --format json
   ```
3. Start from the `Bootstrap` scene, not the gameplay scene directly. A scene that only works when
   opened directly is a bug `core-scene-setup` covers.
4. Enter Play Mode through the Editor tools reported by `unity list`, and drive the check. Prefer a
   checked-in Editor script run with `eval_file` over a long inline block.
5. Walk the acceptance checks one at a time. For each, record the **observed** value, not the
   expected one:
   - Numeric check → read the value back from the Editor and report it.
   - Behavioural check → describe what happened.
   - Edge case → trigger it deliberately; do not assume it holds.
6. Read the console during the run. **Any error or warning fails the check**, even if the mechanic
   looked right. Hand off to `qa-fix-console-errors`.
7. Check the "Feel" section separately from the rules. A mechanic can satisfy every numeric rule and
   still feel wrong; report that as a tuning item against the spec, not as a pass.
8. Use temporary `Debug.Log` lines to observe values if you must, then **remove them**. The user did
   not ask for logging, and leftover lines clutter the console the next agent reads.
9. Exit Play Mode cleanly. Confirm nothing was left mutated — in particular, check no
   ScriptableObject was written to during the run, which persists in the Editor and not in a build.
10. Report honestly, as a list of checks with pass or fail and the observed value. If you could not
    reach a running Editor, the correct report is "not verified — no Editor reachable", never an
    inferred pass.
11. Update `design/STATE.md` via `design-update-state`: move the mechanic to Done only when every
    check passed with a clean console.

## Unity CLI commands used

```bash
unity status                              # live Editors: port, project path, version, PID
unity pipeline list                       # confirm the Pipeline package is installed
unity list                                # Editor-registered tools and their parameter schemas
unity commands --format json              # full CLI command manifest
unity recompile --strict --format json    # must be clean before entering Play Mode
unity test --format json                  # PlayMode tests, where a check can be automated
```

Entering Play Mode and reading values back uses the Editor tools `unity list` reports. `script eval`
compiles a statement block — no `using` directives, fully-qualified types, result at
`data.result.result`. See `PACK/references/unity-cli.md`.

## Files to read (exact paths)

| Need | Path |
| --- | --- |
| Project status | `design/STATE.md` |
| Design map | `design/INDEX.md` |
| Acceptance checks and feel targets | `design/mechanic-*.md` (named in `INDEX.md`) |
| CLI surface and exit codes | `PACK/references/unity-cli.md` |
| Official skill map | `PACK/references/official-unity-skills.md` |
| Frame budget for the project | `PACK/rules/performance.md` |
| Scene bootstrap contract | `PACK/rules/architecture.md` |
| PlayMode test template | `PACK/templates/csharp/PlayModeTest.cs.txt` |

## Done checklist

- [ ] An Editor was genuinely reachable and the Pipeline package was installed.
- [ ] Started from `Bootstrap`, not the gameplay scene directly.
- [ ] Every acceptance check was exercised, with the **observed** value recorded.
- [ ] Edge cases were triggered deliberately, not assumed.
- [ ] The console was clean during the whole run — no errors, no warnings.
- [ ] Feel was assessed separately from the numeric rules.
- [ ] Temporary logging removed.
- [ ] No ScriptableObject was mutated during the run.
- [ ] Anything unverifiable is stated as unverified, not inferred.
- [ ] `design/STATE.md` updated.

## Common mistakes

- Reporting a pass because the code compiles and the unit tests are green.
- Describing expected values as if they were observed. If you did not read it back, you did not
  verify it.
- Claiming a Play Mode result with no Editor reachable. State that it could not be verified instead.
- Ignoring a console warning because the mechanic looked fine; `--strict` treats it as a failure and
  so should you.
- Testing by opening the gameplay scene directly, so missing bootstrap services go unnoticed.
- Only testing the happy path and never the edge cases the spec lists.
- Leaving the project in Play Mode, or leaving a mutated ScriptableObject behind.
- Treating "feels fine" as a pass on the Feel section without naming the numbers you tried.
