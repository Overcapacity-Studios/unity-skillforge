---
name: qa-fix-console-errors
description: Clear Unity compile errors, console errors and warnings until the project builds clean. Use whenever recompile fails, the console has red entries, or work is blocked by a compile failure. This is the stop-the-line skill - nothing else proceeds while the console is dirty.
metadata:
  version: 0.1.0
---

# Fix console errors

Paths written as `PACK/` mean wherever this pack's own files live: `.unity-skillforge/` in a game
repo (created by `install.sh`), the plugin's root directory when installed as a plugin, or the
repo root when working on the pack itself.

## When to use

- `unity recompile` fails.
- The Unity console has errors or warnings.
- Any other skill's "compile and verify" step did not come back clean.

**This is a stop-the-line skill.** While the console has errors, no new feature work starts. An
agent that keeps building on a broken compile produces changes nobody can verify.

## Prefer the official skill

If Unity's official plugin is installed:

- `/unity:project-auditor-fixes` — project-wide settings and configuration problems.
- `/unity:unity-pipeline` — its `references/playmode-verification-loop.md` covers the console-read
  and verify loop.

What stays ours: the **stop-the-line rule and the triage order** below. See
`PACK/references/official-unity-skills.md`.

## Inputs needed

- The error text, verbatim. Not a paraphrase — the error code matters.
- What changed most recently. The newest change is the first suspect.

## Steps

1. Read `design/STATE.md`, particularly "Blocked / broken".
2. Get the real state rather than guessing:
   ```bash
   unity status
   unity recompile --strict --format json
   ```
   Read `success`, `errors` and `warnings` from the JSON envelope.
3. Fix in strict order. Compile errors first — a console full of runtime errors from a stale
   assembly is noise.
   1. **Compile errors**, in file order. One file's error often causes several downstream.
   2. **Runtime errors** (red).
   3. **Warnings** (yellow). `--strict` fails on these, so they are not optional.
4. For each compile error, use the code, not the prose:
   | Code | Meaning | Usual fix |
   | --- | --- | --- |
   | `CS0246` / `CS0103` | Type or name not found | Missing `using`, wrong namespace, or a missing `.asmdef` reference |
   | `CS0117` / `CS1061` | Member does not exist | Wrong type, or a deprecated API — check the version pins |
   | `CS0229` / `CS0121` | Ambiguous | Two types with the same name; qualify it |
   | `CS1503` / `CS0029` | Argument or conversion mismatch | Wrong overload; read the signature |
   | `CS0115` | No suitable member to override | Base signature changed |
   An assembly-reference error means the dependency points the wrong way — fix the layering per
   `PACK/rules/architecture.md`, do not add a reference that creates a cycle.
5. If an API is reported as deprecated or obsolete, replace it rather than suppressing the warning.
   Check `PACK/references/unity-versions.md` for the pinned version, and the package docs for the
   current API. Never add `#pragma warning disable` to silence a real deprecation.
6. For runtime errors, read the whole message including the object name. A
   `NullReferenceException` in `Awake` is almost always an unassigned `[SerializeField]`; add the
   actionable `Debug.LogError` guard from `PACK/rules/csharp-style.md` so it names itself next time.
7. A `MissingReferenceException` firing after an object was destroyed means a subscription was never
   undone. Find the `OnEnable` with no matching `OnDisable`.
8. Re-run until clean:
   ```bash
   unity recompile --strict --format json
   ```
9. Then re-run the suite, because a compile fix can change behaviour:
   ```bash
   unity test --format json
   ```
10. Remove any temporary logging you added while diagnosing.
11. Update `design/STATE.md`: clear the "Blocked / broken" entry, or replace it with what is still
    outstanding.

## Unity CLI commands used

```bash
unity status                              # live Editors: port, project path, version, PID
unity list                                # Editor-registered tools and their parameter schemas
unity commands --format json              # full CLI command manifest
unity recompile --strict --format json    # compile errors without a full build; --strict fails on warnings
unity test --format json                  # re-verify after fixing
```

To read the Editor console, use the tool `unity list` actually reports. Unity's docs mention
`Unity_ReadConsole`, but only as part of the **deprecated** in-Editor MCP surface — do not assume
that name exists. See `PACK/references/unity-cli.md` and `PACK/references/unity-mcp-tools.md`.

## Files to read (exact paths)

| Need | Path |
| --- | --- |
| Known failures | `design/STATE.md` |
| Design map | `design/INDEX.md` |
| CLI surface and exit codes | `PACK/references/unity-cli.md` |
| Deprecated MCP names, for recognition only | `PACK/references/unity-mcp-tools.md` |
| Pinned versions and the 2D physics split | `PACK/references/unity-versions.md` |
| Assembly and layering rules | `PACK/rules/architecture.md` |
| Style rules, error-logging pattern | `PACK/rules/csharp-style.md` |
| Official skill map | `PACK/references/official-unity-skills.md` |

## Done checklist

- [ ] `unity recompile --strict --format json` returns `success: true` with zero errors and zero warnings.
- [ ] No warning was silenced with `#pragma warning disable` or an `[Obsolete]` suppression.
- [ ] Deprecated APIs were replaced, not suppressed.
- [ ] Any fixed `NullReferenceException` now has an actionable guard naming the object.
- [ ] `unity test --format json` passes after the fix.
- [ ] Temporary diagnostic logging removed.
- [ ] `design/STATE.md` "Blocked / broken" is accurate.

## Common mistakes

- Chasing runtime errors while the project does not compile — those errors come from a stale assembly.
- Fixing the last error in the list first; the first compile error often causes the rest.
- Adding an assembly reference to clear `CS0246`, creating a dependency cycle that then will not
  compile at all.
- Suppressing a deprecation warning instead of migrating, which breaks on the next Unity upgrade.
- Reading only the exception type and not the object name, so the same null returns tomorrow.
- Declaring success from the exit code without checking `warnings` under `--strict`.
- Leaving diagnostic `Debug.Log` lines in, so the next agent reads a cluttered console.
- Saying "fixed" without re-running `recompile` and `test`.
