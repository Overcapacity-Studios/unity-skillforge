---
name: design-prototype-plan
description: Plan the smallest playable experiment that tests a game's riskiest assumption - objective, minimum feature set, placeholder assets, measurable technical criteria, human playtest questions and agreed success or reject criteria. Use before building a prototype.
metadata:
  version: 0.1.0
---

# Prototype plan

Paths written as `PACK/` mean wherever this pack's shared files live: `.unity-skillforge/` in a
game repo (`install.sh`), the sibling `unity-skillforge-pack` folder (`npx skills add`), the
plugin's root directory (plugin install), or `skills/unity-skillforge-pack/` in this repo.

## When to use

- A concept or mechanic rests on an assumption nobody has tested, and building the production
  version would be expensive if it is wrong.
- The user says "I want to try this before committing", or a `game-director` review returned
  "prototype first".
- Before choosing an art style: a prototype runs on placeholders, so it does not wait on
  `assets-art-style-lock`.

Not for: verifying a finished mechanic against its spec (`qa-playmode-check`), or specifying a
mechanic that is already agreed (`design-mechanic-spec`).

## Inputs needed

- The assumption to test. If several are offered, pick the one whose failure invalidates the most
  other work, and say why.
- `design/concept.md` or the relevant `design/mechanic-*.md`.
- The real time budget. A prototype that takes three weeks is not a prototype.

## Steps

1. Read `design/STATE.md` and `design/INDEX.md`, then the one concept or mechanic document this
   prototype tests. Read `design/decisions.md`'s Index table to check the test is not re-litigating
   an `APPROVED` decision.
2. **Name the single riskiest hypothesis**, in one falsifiable sentence. "Dashing through enemies
   feels committing rather than fiddly" is falsifiable; "the game is fun" is not. One hypothesis
   per prototype — two hypotheses produce a result you cannot attribute.
3. Copy `PACK/templates/game-design/prototype.md` to `design/prototype-<name>.md` and add a row to
   `design/INDEX.md` under Prototypes.
4. Write the **objective** as what you will know afterwards that you do not know now.
5. Define the **minimum feature set**. Each item must state why the test fails without it. If an
   item is there to make the prototype nicer, it does not belong.
6. Write the **Explicitly NOT in this prototype** list, and make it long: menus, save, audio,
   settings, art, difficulty curve, multiple levels, tutorial. This list is what keeps a prototype
   from becoming a slow first version of the game.
7. Plan **placeholder assets**, which are permitted with no locked art bible: Unity primitives, the
   built-in default material, untextured blockout geometry, debug gizmos and lines, and unstyled
   UI labels. Name each one, put it under `Assets/_Project/Prototype/` with a `PH_` prefix, and say
   what it stands in for. **Generated production art still requires a 🟢 locked
   `design/art-bible.md`** — see `assets-art-style-lock`.
8. Write **technical validation** criteria: measurable, observable, verifiable by an agent. These
   are handed to `qa-playmode-check` exactly as written — do not restate its procedure here.
   Cover function ("the dash moves 4 ± 0.2 units"), performance ("frame time under 16.6 ms with 20
   agents") and controls ("the bound action fires, console clean").
9. Write **gameplay validation** as questions only a human who played it can answer:
   understanding, fantasy match, satisfaction, confusion or frustration, and whether they wanted
   another go. Keep them as questions. A checkbox invites an agent to tick it.
10. Estimate complexity **as labelled assumptions**: the estimate, and what it assumes. Never
    present an estimate as a commitment, and never convert sessions into dates.
11. Agree **success, revise and reject criteria before building**. Each must name the specific
    observation that triggers it. Deciding afterwards is how a failed prototype gets rationalised
    into a success.
12. Write the **implementation plan**: ordered steps, each naming the skill that owns it. Route
    build steps through the normal skills (`core-scene-setup`, `core-input-setup`, the dimension's
    skills) — a prototype is still built under this pack's rules, it just has no art and no polish.
13. Leave the **Playtest log** section empty, marked "Not played yet". **Never write an entry you
    did not receive from the user.** When they report a session, transcribe what they observed,
    quote their words, and leave unanswered questions as "not observed".
14. Set `STATE.md` → **Stage: prototype** via `design-update-state`, with the prototype as the
    single In-progress item.
15. After the prototype is played, write the conclusion from the real observations and record the
    outcome through `design-decision-log`. A prototype with no human session concludes
    "not concluded — no human has played it", which is a valid and final answer until someone plays
    it.

## Unity CLI commands used

None. This skill writes a design document only. The prototype it plans is built and verified by
other skills, which discover the Editor surface themselves:

```bash
unity status                   # confirm an Editor is reachable, before planning build steps
```

Technical criteria are executed by `qa-playmode-check`. See `PACK/references/unity-cli.md`.

## Files to read (exact paths)

| Need | Path |
| --- | --- |
| Project status and stage | `design/STATE.md` |
| Design map | `design/INDEX.md` |
| The hypothesis being tested | `design/concept.md` or `design/mechanic-*.md` |
| Approved decisions, Index table only | `design/decisions.md` |
| Template to copy | `PACK/templates/game-design/prototype.md` |
| Placeholder asset rules and the `PH_` prefix | `PACK/rules/folder-conventions.md` |
| Frame budget for a performance criterion | `PACK/rules/performance.md` |
| Who runs the technical criteria | the `qa-playmode-check` skill |
| The production-art gate, still in force | the `assets-art-style-lock` skill |
| Where the result is recorded | the `design-decision-log` skill |

## Done checklist

- [ ] Exactly one falsifiable hypothesis, and it is the riskiest one available.
- [ ] `design/prototype-<name>.md` exists with a row in `design/INDEX.md`.
- [ ] Every in-scope feature states why the test fails without it.
- [ ] The explicit NOT list covers the production features a prototype does not need.
- [ ] Placeholders are named, `PH_`-prefixed, under `Assets/_Project/Prototype/`.
- [ ] Technical criteria are measurable and observable, ready for `qa-playmode-check`.
- [ ] Gameplay questions are questions, answerable only by a human who played it.
- [ ] Complexity estimates are labelled as assumptions, with what they assume.
- [ ] Success, revise and reject criteria were agreed before building.
- [ ] The implementation plan names the owning skill for each step.
- [ ] The playtest log is empty and marked not played yet.
- [ ] `STATE.md` Stage and In progress are updated.

## Common mistakes

- Prototyping two hypotheses at once, so a bad result cannot be attributed to either.
- A hypothesis that cannot fail, which means the prototype cannot teach anything.
- Letting the prototype grow a menu, a save system and real art, at which point it is the game.
- Waiting on an art style a prototype does not need, delaying the test by a week.
- **Writing playtest observations no human made.** An invented "players found it satisfying" is the
  single most damaging thing this skill can produce — every later decision rests on it.
- Treating green technical checks as gameplay validation. Correct and fun are different claims.
- Agreeing the success criteria after seeing the result.
- Presenting a complexity estimate as a deadline.
- Shipping placeholder assets into production because nobody recorded that they were temporary.
- Duplicating `qa-playmode-check`: write the criteria, let that skill run them.
