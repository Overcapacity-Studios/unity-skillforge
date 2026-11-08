---
name: qa-run-tests
description: Run the Unity Edit Mode and Play Mode test suites through the Unity CLI and act on the results. Use after any logic change, before a build, and before declaring work done. Defer to Unity's unity-cli skill for the underlying test-runner mechanics.
metadata:
  version: 0.1.0
---

# Run tests

Paths written as `PACK/` mean wherever this pack's shared files live: `.unity-skillforge/` in a
game repo (`install.sh`), the sibling `unity-skillforge-pack` folder (`npx skills add`), the
plugin's root directory (plugin install), or `skills/unity-skillforge-pack/` in this repo.

## When to use

- After any change to logic, before saying the work is done.
- Before a build (`qa-build` assumes a green suite).
- When a test fails and you need to triage it.

## Prefer the official skill

If Unity's official plugin is installed:

- `/unity:unity-cli` — its `references/build-run-test.md` is authoritative for the test runner's
  flags and report format.
- `nowsprinting/unity-coding-skills` (optional pack) goes much deeper on test-first Unity C#.

What stays ours: the **test layout, the acceptance gate, and the triage order** below. See
`PACK/references/official-unity-skills.md`.

## Inputs needed

- Whether an Editor is running (`unity status`). The test runner drives the Editor.
- What changed, so you know whether EditMode, PlayMode or both are relevant.

## Steps

1. Read `design/STATE.md`. If the "Blocked / broken" section already lists a failure, fix that
   first — do not stack a second failure on top.
2. Confirm the Editor is reachable and the console is clean. A project that does not compile cannot
   run tests: run `qa-fix-console-errors` first if `recompile` fails.
   ```bash
   unity status
   unity recompile --strict --format json
   ```
3. Run the suite:
   ```bash
   unity test --format json
   ```
   For a fast inner loop while iterating:
   ```bash
   unity test --affected --format json
   unity watch test
   ```
4. Read the result from the JSON envelope: check `success`, then `data`, then `errors`. Do not judge
   the run by the exit code alone.
5. Triage failures in this order, and stop at the first that applies:
   1. **Compile error** → `qa-fix-console-errors`.
   2. **Every test failing** → environment, not code. Check the Editor is open, the Pipeline package
      is installed, and the test assemblies reference the test framework.
   3. **One test failing after your change** → your change. Fix the code, not the test.
   4. **A test failing that asserts the wrong thing** → fix the test, and say explicitly in your
      report that you changed a test rather than the code.
   5. **A flaky PlayMode test** → it almost always waits on wall-clock time. Replace the wait with
      `WaitForFixedUpdate` or a deterministic frame count.
6. Never delete, rename or `[Ignore]` a failing test to get green. If a test must be disabled, say so
   in your report and add a row to `design/STATE.md` under "Blocked / broken".
7. If the change added logic with no test, add one now using
   `PACK/templates/csharp/EditModeTest.cs.txt` (pure logic) or
   `PACK/templates/csharp/PlayModeTest.cs.txt` (needs a frame).
8. Report the actual numbers: total, passed, failed, skipped, and the name of each failure. "Tests
   pass" without numbers is not a result.

## Unity CLI commands used

```bash
unity status                              # live Editors: port, project path, version, PID
unity list                                # Editor-registered tools and their parameter schemas
unity commands --format json              # full CLI command manifest
unity recompile --strict --format json    # must pass before tests can run
unity test --format json                  # Edit Mode and Play Mode via the Editor test runner
unity test --affected --format json       # only tests affected by current changes
unity watch test                          # re-runs `unity test --affected` on file change
```

`unity test` writes an NUnit report. Exit codes: `0` success, `1` error, `2` usage, `130` cancelled.
See `PACK/references/unity-cli.md`.

## Files to read (exact paths)

| Need | Path |
| --- | --- |
| Project status and known failures | `design/STATE.md` |
| Design map | `design/INDEX.md` |
| Acceptance checks for the mechanic | `design/mechanic-*.md` (named in `INDEX.md`) |
| CLI surface, flags, exit codes | `PACK/references/unity-cli.md` |
| Official skill map | `PACK/references/official-unity-skills.md` |
| Test assembly layout | `PACK/rules/architecture.md` |
| Test folder layout | `PACK/rules/folder-conventions.md` |
| EditMode template | `PACK/templates/csharp/EditModeTest.cs.txt` |
| PlayMode template | `PACK/templates/csharp/PlayModeTest.cs.txt` |

## Done checklist

- [ ] `unity recompile --strict` passed before testing.
- [ ] `unity test --format json` reports `success: true`.
- [ ] Counts reported: total, passed, failed, skipped.
- [ ] No test was deleted, renamed or ignored to reach green.
- [ ] New logic has at least one test.
- [ ] Any remaining failure is recorded in `design/STATE.md` under "Blocked / broken".
- [ ] `design/STATE.md` updated via `design-update-state`.

## Common mistakes

- Reporting "tests pass" from the exit code without checking `success` in the JSON envelope.
- Running tests on a project that does not compile and reading the resulting noise as test failures.
- Changing an assertion to match the new behaviour without saying so — that silently removes the
  guarantee the test existed for.
- Adding `[Ignore]` to go green, which hides the regression from the next agent.
- Writing a PlayMode test that waits on seconds, making it flaky on a loaded machine.
- Writing everything as PlayMode tests. They are much slower; use EditMode for pure logic.
- Forgetting the test assembly must reference `UnityEngine.TestRunner`, so tests are simply invisible.
- Claiming a PlayMode result without an Editor running — the suite never ran at all.
