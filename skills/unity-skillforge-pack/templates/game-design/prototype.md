# Prototype plan — <name>

<!--
Copy to design/prototype-<name>.md and add a row to design/INDEX.md.
Written BEFORE the prototype is built, by design-prototype-plan. One hypothesis per file.
Keep the plan under 90 lines. The Playtest log at the bottom grows as sessions happen.

THE PLAYTEST LOG IS FILLED IN BY A HUMAN WHO PLAYED IT, OR FROM WHAT THEY REPORTED.
An agent must never write an entry it did not receive from the user. "Not played yet" is the
correct content until someone plays it.
-->

**Status:** planned | built | played | concluded
**Tests hypothesis:** <the one riskiest claim this prototype exists to test>
**Updated:** YYYY-MM-DD

## Objective

<One sentence: what we will know after this that we do not know now.>

## Riskiest assumption

<The claim that, if false, invalidates the most other work. Quote the concept or mechanic doc.>

## In scope — the smallest feature set

Only what the hypothesis needs. Each item says why the test fails without it.

| Feature | Needed because |
| --- | --- |
| <Player can move and dash> | <the hypothesis is about dash timing> |

## Explicitly NOT in this prototype

Production features that would cost time and prove nothing here.

- <Menus, save, audio, art, settings, multiple levels, difficulty curve...>

## Placeholder assets

Prototype assets are allowed without a locked art bible. They must be obvious placeholders.

| Need | Placeholder | Path |
| --- | --- | --- |
| <Player> | <capsule, default material> | `Assets/_Project/Prototype/PH_Player.prefab` |

- Naming: `PH_` prefix, everything under `Assets/_Project/Prototype/`.
- Production art still requires `design/art-bible.md` to be 🟢 locked — see `assets-art-style-lock`.
- These are deleted or replaced before the mechanic is called production-ready.

## Technical validation — measurable, run by an agent

Verified by `qa-playmode-check`. Observable values only.

- [ ] <Dash moves the player 4 ± 0.2 units in 0.15 s.>
- [ ] <Frame time stays under 16.6 ms with 20 agents active.>
- [ ] <Controls respond to the bound action, with no console errors or warnings.>

## Gameplay validation — answered only by a human playing it

Questions, not checkboxes. An agent cannot answer these.

1. Did the player work out what to do without being told?
2. Did the experience match the intended fantasy: <quote it>?
3. Was the core interaction satisfying to repeat?
4. Where were they confused or frustrated?
5. Did they want another go? Why?

## Complexity estimate

**These are assumptions, not commitments.** Labelled so they are not quoted back as schedule.

| Part | Estimate | Assumes |
| --- | --- | --- |
| <Dash + input> | <1 session> | <input system already wired> |

## Decision criteria, agreed before building

| Outcome | Means | Then |
| --- | --- | --- |
| **Success** | <technical checks pass AND <the specific player response>> | `design-mechanic-spec`, then production |
| **Revise** | <loop works but <specific flaw>> | one named change, re-test |
| **Reject** | <the specific observation that kills it> | `design-scope-cut`, record in `design/decisions.md` |

## Implementation plan

1. <Step, with the skill that owns it.>
2. <...>

---

## Playtest log

<!-- One block per session. Written only from what a human actually observed or reported. -->

### Session <n> — YYYY-MM-DD — <who played, how long>

**Not played yet.** <Delete this line when a real session is recorded.>

- **What they did:** <observed behaviour>
- **Where they got stuck:** <...>
- **Their words:** "<quote>"
- **Against each gameplay question:** <answers, or "not observed">
- **Technical checks at the time:** <pass/fail with observed values, or "not run">

## Conclusion

**Verdict:** success | revise | reject | not concluded — no human has played it
**Evidence:** <the observations this rests on>
**Decision recorded as:** `design/decisions.md` → <D-00n>
