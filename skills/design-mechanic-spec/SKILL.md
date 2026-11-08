---
name: design-mechanic-spec
description: Specify one mechanic before building it - rules with numbers, tuning values, feel targets and the acceptance checks QA verifies against. Use before implementing any gameplay. Without a spec there is nothing to verify, so playmode-check cannot pass.
metadata:
  version: 0.1.0
---

# Specify a mechanic

Paths written as `PACK/` mean `.unity-skillforge/` in a game repo, or this pack's root.

## When to use

- Before implementing any mechanic. This is the input `qa-playmode-check` verifies against.
- A mechanic exists in code but has no spec, so nobody can say whether it is correct.
- A mechanic "feels wrong" and there are no stated targets to compare against.

Writing the spec first is not ceremony: the **acceptance checks** are what makes "done" decidable
instead of a matter of opinion.

## Inputs needed

- Which mechanic, and which pitch pillar it serves. **If it serves no pillar, say so and recommend
  cutting it** (`design-scope-cut`).
- The input actions it needs.
- Whatever numbers the user already has in mind. Where they have none, propose defaults and say they
  are proposals.

## Steps

1. Read `design/STATE.md`, `design/INDEX.md`, and `design/pitch.md` for the pillars.
2. Copy `PACK/templates/game-design/mechanic.md` to `design/mechanic-<name>.md` and add a row to
   `design/INDEX.md`. One mechanic per file.
3. Name the pillar it serves. If none fits, stop and raise it before writing anything else.
4. Write the **player-facing description** in two sentences with no implementation words. If it
   cannot be described without naming a component, it is not a mechanic yet.
5. Fill the **Inputs** table with action names that match `core-input-setup` conventions
   (`Player/Jump`, Button). Inventing a different action name here guarantees a mismatch later.
6. Write the **Rules** as numbered, individually testable statements **with numbers**. Include at
   least one edge case and one failure case. "The player jumps" is not a rule; "Jump applies 7.5 m/s
   upward velocity and is ignored while not grounded" is two.
7. Fill the **Tuning values** table. Every number gets a default, a valid range, and the
   ScriptableObject asset path it will live on. These feed `core-scriptable-object-data` directly;
   a number not in this table ends up hardcoded.
8. Write the **Feel** section with numbers: coyote time, input buffer, acceleration curve, camera
   response, hitstop, screen shake. This is the difference between correct and good, and it is the
   part most often left as adjectives and then argued about.
9. Write the **Acceptance checks** as observable outcomes a different agent could verify without
   reading the code. Each must be unambiguous:
   - Good: "Holding Move for 1s moves the player 5 ± 0.2 units."
   - Bad: "Movement feels responsive."
   Include "nothing logs an error to the console during the check" as a standing check.
10. List dependencies: systems, assets, and what blocks this. If it is blocked, say so in
    `design/STATE.md` rather than starting anyway.
11. State what is **out of scope** for this mechanic, especially anything a reader would assume is
    included.
12. Keep it **under 80 lines**. If it needs more, it is two mechanics — split it.
13. Report the spec, flag every number you proposed rather than were given, and only then hand off
    to the implementing skill from the routing table in `PACK/AGENTS.md`.

## Unity CLI commands used

None. This skill writes a design document only and does not touch the Unity Editor. To ground a
proposed value in what the project already does, read existing tuning assets rather than guessing:

```bash
unity status                   # confirm an Editor is reachable
unity list                     # Editor-registered tools and their parameter schemas
```

See `PACK/references/unity-cli.md`.

## Files to read (exact paths)

| Need | Path |
| --- | --- |
| Project status and dimension | `design/STATE.md` |
| Design map | `design/INDEX.md` |
| Pillars this must serve | `design/pitch.md` |
| Template to copy | `PACK/templates/game-design/mechanic.md` |
| Routing table for the implementing skill | `PACK/AGENTS.md` |
| Input action conventions | `PACK/references/input-system.md` |
| Where tuning values will live | `PACK/skills/core-scriptable-object-data/SKILL.md` |
| Who verifies the acceptance checks | `PACK/skills/qa-playmode-check/SKILL.md` |

## Done checklist

- [ ] The file is `design/mechanic-<name>.md` with a row in `design/INDEX.md`.
- [ ] The pillar it serves is named, or cutting it was recommended.
- [ ] The player-facing description uses no implementation words.
- [ ] Input action names match `core-input-setup` conventions.
- [ ] Rules are numbered, testable, and contain numbers.
- [ ] At least one edge case and one failure case are specified.
- [ ] Every tuning value has a default, a range and a target asset path.
- [ ] The Feel section gives numbers, not adjectives.
- [ ] Acceptance checks are observable and verifiable by someone who has not read the code.
- [ ] Dependencies and out-of-scope items are listed.
- [ ] Under 80 lines.
- [ ] Proposed-versus-given numbers were distinguished in the report.

## Common mistakes

- Rules without numbers, which makes the mechanic unverifiable and "done" a matter of opinion.
- Acceptance checks phrased as feelings, so `qa-playmode-check` has nothing to measure.
- Only happy-path rules, so every edge case is discovered during implementation.
- Leaving feel as adjectives, then relitigating it after the code exists.
- A tuning table missing values, which then get hardcoded in the controller.
- Inventing input action names that do not match the actions asset.
- Specifying three mechanics in one file, so none can be marked done independently.
- Writing the spec after the code, which just documents whatever was built.
- Presenting proposed defaults as if the user had chosen them.
- Specifying a mechanic that serves no pillar instead of recommending it be cut.
