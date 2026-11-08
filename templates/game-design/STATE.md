# Project state

<!--
This is the FIRST file any agent reads, every time. Keep it under 60 lines.
It answers: what is this, where are we, what is next, what is broken.
It is not a changelog and not a design doc. Update it via the design-update-state skill.
-->

**Game:** <name>
**Dimension:** 2D | 2.5D | 3D  <!-- drives which skills the router loads. Pick one. -->
**Unity:** 6000.3.x · URP · new Input System
**Target platform(s):** <platform> @ <fps target>
**Updated:** YYYY-MM-DD

## One line

<What the player does, in one sentence.>

## Status

| Area | State |
| --- | --- |
| Core loop | not started / prototyped / playable / tuned |
| Player control | |
| Art | placeholder / first pass / final |
| Audio | |
| Build | not attempted / builds / shipped |

## Done

- <Mechanic or system that is playable and tested. Keep to one line each.>

## In progress

- <The ONE thing being worked on now, and who/what owns it.>

## Next (ordered)

1. <Next slice. Small enough to finish in one session.>
2. <...>

## Blocked / broken

- <Anything failing, with the error and where it shows. Empty is a valid answer — say "nothing".>

## Decisions that constrain new work

- <Short, e.g. "legacy Rigidbody2D, not 2D Physics Core — see tech-decisions.md">

## Where things are

| Need | Path |
| --- | --- |
| Full design index | `design/INDEX.md` |
| Art style lock | `design/art-bible.md` |
| Technical decisions | `design/tech-decisions.md` |
