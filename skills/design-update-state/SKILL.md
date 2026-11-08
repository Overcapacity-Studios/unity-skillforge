---
name: design-update-state
description: Update the design folder's STATE.md and INDEX.md at the end of a task so the next agent starts from the truth - status, what is in progress, what is next and what is broken. Run at the end of every task. STATE.md is the first file every skill reads.
metadata:
  version: 0.1.0
---

# Update project state

Paths written as `PACK/` mean wherever this pack's own files live: `.unity-skillforge/` in a game
repo (created by `install.sh`), the plugin's root directory when installed as a plugin, or the
repo root when working on the pack itself.

## When to use

**At the end of every task.** Every skill in this pack ends by handing off here, because
`design/STATE.md` is the first file every skill reads. A stale `STATE.md` misleads the next agent
into redoing finished work or building on something broken.

Also use when `STATE.md` has drifted from reality and needs reconciling.

## Inputs needed

- What actually changed in this task — files, mechanics, assets.
- Whether it was **verified** (`qa-playmode-check` passed with a clean console) or only compiles.
  These are different statuses and must not be conflated.
- Anything newly broken or newly blocked.

## Steps

1. Read `design/STATE.md` and `design/INDEX.md`.
2. Update the **status table** honestly. Use the real rung, not the hopeful one:
   `not started` → `prototyped` (exists, not verified) → `playable` (verified via
   `qa-playmode-check`) → `tuned` (feel targets met). Something that merely compiles is
   `prototyped`, never `playable`.
3. Move finished items into **Done**, one line each. Keep them terse; this is not a changelog.
4. Set **In progress** to the single thing now being worked on, or empty it. If it lists more than
   one item, that is a problem to name, and `design-scope-cut` is the fix.
5. Re-order **Next**. Put the actual next slice first, small enough to finish in one session. Drop
   anything that this task made unnecessary.
6. Update **Blocked / broken** precisely: the error text, where it appears, and what it blocks.
   **"Nothing" is a valid and valuable answer** — write it rather than leaving a stale entry.
7. Add any new constraint to **Decisions that constrain new work**, one line, pointing at
   `design/tech-decisions.md` for the detail. If this task made a real technical decision, write the
   full entry there too — that log is append-only and never rewritten.
8. Update `design/INDEX.md` if this task created a design document, changed a mechanic's status, or
   cut something. **A document with no row in `INDEX.md` is invisible to every agent.**
9. Set the **Updated** date on both files.
10. Keep `STATE.md` **under 60 lines**. It is read on every single task, making it the most
    expensive file in the project per token. If it is growing, the cause is usually history that
    belongs in git or detail that belongs in a mechanic spec.
11. Re-read what you wrote as if you were the next agent with no memory of this session. If it does
    not tell them where to start, it is not finished.

## Unity CLI commands used

None. This skill edits design documents only. If you need to confirm a status claim before writing
it down, verify rather than assume:

```bash
unity recompile --strict --format json    # supports a "prototyped" claim
unity test --format json                  # supports a "playable" claim
```

Do not record a status you did not verify. See `PACK/references/unity-cli.md`.

## Files to read (exact paths)

| Need | Path |
| --- | --- |
| The file being updated | `design/STATE.md` |
| The index being updated | `design/INDEX.md` |
| Decision log, for new constraints | `design/tech-decisions.md` |
| Mechanic whose status changed | `design/mechanic-*.md` |
| Verification standard for "playable" | the `qa-playmode-check` skill |
| Fix for too many in-progress items | the `design-scope-cut` skill |

## Done checklist

- [ ] The status table uses the real rung; nothing that only compiles is marked `playable`.
- [ ] Done lists finished work, one terse line each.
- [ ] In progress names at most one item, or is empty.
- [ ] Next is re-ordered, and its first item fits in one session.
- [ ] Blocked / broken is precise, or explicitly says nothing.
- [ ] New constraints are noted, with full entries in `design/tech-decisions.md`.
- [ ] `INDEX.md` has a row for every design document, with current statuses.
- [ ] The Updated date is set on both files.
- [ ] `STATE.md` is under 60 lines.
- [ ] It was re-read from the perspective of an agent with no memory of this session.

## Common mistakes

- Marking something `playable` when it only compiles. The next agent then builds on untested work.
- Leaving a stale Blocked / broken entry, so the next agent hunts a bug that was already fixed.
- Letting `STATE.md` become a changelog. It describes the present; git holds the history.
- Several items in In progress, which hides that nothing is being finished.
- A Next list of twenty items, which is a backlog, not a next step.
- Creating a design document and forgetting its `INDEX.md` row, making it invisible.
- Writing a decision into `STATE.md` but not `tech-decisions.md`, so it is lost on the next update.
- Rewriting history in `tech-decisions.md` instead of superseding an entry.
- Skipping this skill because the task felt small. The next agent still starts from `STATE.md`.
- Recording a status that was never verified.
