# Mechanic — <name>

<!--
Copy to design/mechanic-<name>.md. Add a row to design/INDEX.md.
One mechanic per file. Written BEFORE code, so the acceptance checks come first.
Keep under 80 lines: if it needs more, it is two mechanics.
-->

**Status:** spec'd | built | tuned
**Pillar served:** <which pitch pillar — if none, this mechanic should be cut>
**Updated:** YYYY-MM-DD

## Player-facing description

<What the player does and what happens, in two sentences, with no implementation words.>

## Inputs

| Action | Binding (new Input System) | Type |
| --- | --- | --- |
| <Jump> | `Player/Jump` | Button |

## Rules

Numbered, testable statements. Each one should be checkable in play mode.

1. <Precise rule, with numbers. "Jump applies 7.5 m/s upward velocity.">
2. <Edge case. "Jump is ignored while not grounded.">
3. <Failure case. "Jump during a dash is queued, not dropped.">

## Tuning values

Every number lives on a ScriptableObject, not in code. Name the asset.

| Value | Default | Range | Asset |
| --- | --- | --- | --- |
| <Jump velocity> | 7.5 | 4–12 | `Assets/_Project/Data/Tuning/Player_MovementData.asset` |

## Feel

<Coyote time, input buffer, acceleration curve, camera response, hitstop, screen shake. The
difference between correct and good lives here. Give numbers.>

## Acceptance checks

The `qa-playmode-check` skill verifies exactly these. Write them so a failure is unambiguous.

- [ ] <Observable outcome, e.g. "Holding Move for 1s moves the player 5 ± 0.2 units.">
- [ ] <Edge case holds.>
- [ ] <Nothing logs an error to the console during the check.>

## Dependencies

- Systems: <e.g. core-input-setup, core-event-channels>
- Assets: <e.g. Player_Run animation — see art-bible.md>
- Blocked by: <mechanic or decision, or "nothing">

## Out of scope for this mechanic

- <Thing a reader might assume is included but is not.>
