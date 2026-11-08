---
name: design-scope-cut
description: Cut a project's scope back to what can actually ship - test features against the pitch pillars, rank by cost against the minimum playable, and record cuts so they are not re-proposed. Use when the backlog exceeds the time available or progress has stalled.
metadata:
  version: 0.1.0
---

# Cut scope

Paths written as `PACK/` mean `.unity-skillforge/` in a game repo, or this pack's root.

## When to use

- The planned feature list cannot be built in the time available.
- Work has stalled: many things started, nothing finished.
- A deadline moved in, or the team shrank.
- Before a jam or a milestone, to decide what is genuinely in.

## Inputs needed

- `design/pitch.md`: the pillars and the stated minimum playable.
- `design/STATE.md`: what is done, in progress and planned.
- `design/INDEX.md`: every mechanic spec and its status.
- The real constraint — a date, a session count, or a budget. Without one there is no basis for
  cutting, so ask rather than cutting arbitrarily.

## Steps

1. Read `design/STATE.md`, `design/INDEX.md` and `design/pitch.md`. Read individual mechanic specs
   only for items you are about to judge.
2. List everything currently in scope: Done, In progress, and Next from `STATE.md`, plus every
   mechanic row in `INDEX.md`.
3. Test each item against the **pillars**. A feature serving no pillar is the first and easiest cut —
   the pitch already says it does not matter.
4. Classify what remains against the stated **minimum playable**:
   | Class | Meaning | Action |
   | --- | --- | --- |
   | **Core** | The loop does not work without it | Keep |
   | **Load-bearing** | Core depends on it existing in some form | Keep, but simplify |
   | **Amplifier** | Makes core better, core works without it | Cut or defer |
   | **Orphan** | Serves no pillar, nothing depends on it | Cut now |
5. For each Amplifier, look for the **cheaper version** before cutting outright. A fixed camera
   instead of a dynamic one, three enemy types instead of ten, a static level instead of procedural
   generation. Simplifying usually preserves more of the design than deleting.
6. Prefer cutting **content breadth over system depth**. Ten shallow mechanics read as an unfinished
   game; three deep ones read as a small finished one.
7. Protect the in-progress item. Finishing one thing beats half-finishing three — if several things
   are in progress, that itself is the problem, and the fix is to finish or explicitly park them.
8. Record every cut in `design/INDEX.md` under **Out of scope**, with the date and the reason:
   `- Procedural levels — cut 2026-11-08 because core loop needs tuning first, not more content.`
   This is the point of the exercise: an unrecorded cut gets re-proposed next session and the whole
   argument happens again.
9. Update `design/STATE.md` via `design-update-state`: a shortened Next list, and the cuts reflected
   in the status table.
10. Delete nothing from the repo. Cutting scope is a planning decision, not a code change. If code
    for a cut feature exists, leave it and note it — removing it is a separate, explicit task.
11. Report the cut list, the kept list, and your honest assessment of whether what remains fits the
    constraint. **If it still does not fit, say so** rather than presenting a plan you do not
    believe.

## Unity CLI commands used

None. This skill edits design documents only and does not touch the Unity Editor or the codebase.

## Files to read (exact paths)

| Need | Path |
| --- | --- |
| Project status, in progress, next | `design/STATE.md` |
| Mechanic list and out-of-scope log | `design/INDEX.md` |
| Pillars and minimum playable | `design/pitch.md` |
| Specs for items being judged | `design/mechanic-*.md` (only the relevant ones) |
| Where to record the new state | the `design-update-state` skill |

## Done checklist

- [ ] The real constraint is stated — a date, a session count or a budget.
- [ ] Every in-scope item was tested against the pillars.
- [ ] Items are classified Core, Load-bearing, Amplifier or Orphan.
- [ ] A cheaper version was considered for each Amplifier before cutting it.
- [ ] Content breadth was cut before system depth.
- [ ] At most one item remains In progress.
- [ ] Every cut is recorded in `design/INDEX.md` Out of scope, with a date and a reason.
- [ ] `design/STATE.md` reflects the shortened plan.
- [ ] No code or assets were deleted.
- [ ] An honest verdict on whether the remaining scope fits was given.

## Common mistakes

- Cutting without a stated constraint, which makes every cut arbitrary and easy to reverse.
- Cutting the thing that is currently in progress, wasting the work and leaving nothing finished.
- Trimming a bit from everything, so the project is the same size and nothing is complete.
- Cutting system depth and keeping breadth, producing many shallow mechanics that read as unfinished.
- Deleting a feature outright when a cheaper version would have preserved the design intent.
- Not recording the cut, so it is re-proposed next session and re-argued from scratch.
- Deleting code as part of a scope cut, conflating a planning decision with a code change.
- Presenting a plan you do not believe fits, rather than saying the scope is still too large.
- Cutting a Core item because it is hard. Hard and core means it is the work, not the fat.
