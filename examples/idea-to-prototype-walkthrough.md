# Walkthrough — a rough idea to a played prototype

What the design side of this pack actually does, with the two cases that come up most: a brand-new
game that is still an idea, and a new mechanic on a game that already exists.

Nothing here has been executed against a running Unity Editor. The Unity CLI output shown is the
shape the skills expect, from Unity's published documentation.

---

## Part 1 — "I have a rough idea"

**You:**

> I have a rough idea. A game about repairing lighthouses on a stormy coast. Help me develop it.

**Route:** `unity-game-router` → `design-idea-discovery`. No `design/` folder, and the idea is a
setting rather than a game yet, so it does **not** go to `design-write-gdd`.

### What discovery does, in order

1. **Plays it back and names the gap.**
   > "A game about repairing lighthouses on a stormy coast. The setting is clear; what the player
   > *does* is not. Repairing could be a puzzle, a resource run, or a dexterity task — those are
   > three different games."

2. **Asks three high-impact questions.** Not the template, not twenty questions:
   - What does the player do, second to second, during a repair?
   - What should it feel like when a repair goes well?
   - How many hours a week do you actually have for this?

3. **Proposes options with tradeoffs** instead of asking you to invent them:

   | Option | Player does | Advantage | Cost |
   | --- | --- | --- | --- |
   | A. Puzzle repair | Routes power through a damaged panel | Deep, cheap to build, readable | Slow; storm pressure is cosmetic |
   | B. Timed scramble | Fetches parts while the storm escalates | The storm becomes the antagonist | Needs level layout and a tension curve |
   | C. Dexterity repair | Hand-tools a mechanism under wind | Tactile, feels physical | Hardest to tune, most animation |

   > "Recommending B: your own words were 'the storm should feel like it's winning', and only B puts
   > the storm in the loop. A makes it wallpaper."

4. **Challenges what does not hold.**
   > "Two things fight each other: you said 'meditative' and 'the storm is winning'. Pick which one
   > the game is. If it is meditative, the storm is weather, and the tension has to come from
   > something else — cheaper: a lantern that dims. If the storm is the antagonist, meditative is
   > the wrong word and the pacing has to escalate."
   >
   > "And procedural coastlines roughly doubles the project. Six hand-built lighthouses give you the
   > same first hour for a fraction of the work. Cut it from v1, keep it as a later idea."

5. **Writes `design/concept.md`** with every line marked `(confirmed)` or `(assumed)`:

   ```markdown
   ## Core verbs
   | Verb | What it feels like | Confirmed? |
   | --- | --- | --- |
   | Climb | exposed, slow | confirmed |
   | Fetch | urgent | confirmed |
   | Repair | fiddly under pressure | assumed |

   ## Core gameplay loop hypothesis
   1. Storm damages a component →
   2. Player climbs to diagnose it →
   3. Fetches the part under escalating wind →
   4. Repairs it before the light fails → back to 1.

   **What makes this loop interesting (claim to be tested):** the fetch and the repair compete for
   the same shrinking time budget.
   ```

   `design/STATE.md` is created with **Stage: concept**. Nothing is built. No Unity project is
   required to get this far.

6. **Recommends one next step:** `design-prototype-plan`, because the riskiest assumption is that
   repairing under time pressure is tense rather than annoying.

### Optional: a director review

**You:**

> Act as my game director and challenge this before I build anything.

The `game-director` reads `STATE.md`, `INDEX.md`, the `decisions.md` Index table and `concept.md`,
then reports the fixed format: design context, player impact, effect on existing mechanics,
conflicts, implications, risks, options, **a recommendation**, and what needs your approval. It will
not tell you the loop is fun — nobody has played it.

### The prototype plan

**Route:** `design-prototype-plan` → `design/prototype-repair-pressure.md`.

- **Hypothesis:** "Repairing a component while the fetch timer runs is tense, not annoying."
- **In scope:** climb, one fetch route, one repair interaction, one escalating timer.
- **Explicitly not in:** art, audio, menus, save, multiple lighthouses, a difficulty curve.
- **Placeholders:** `PH_Lighthouse.prefab` (stacked cubes), `PH_Player.prefab` (capsule),
  `PH_Grey.mat` — all under `Assets/_Project/Prototype/`. **No art bible needed.** That gate applies
  to production art, and locking a style now would be guessing.
- **Technical validation** (run by `qa-playmode-check`): the climb reaches the platform in
  3 ± 0.3 s; the repair interaction completes in 2.0 s of held input; the console stays clean.
- **Gameplay validation** (a human answers these): did you understand what to do? Was the pressure
  tense or irritating? Did you want another go?
- **Decision criteria, agreed now:** success if the technical checks pass *and* you wanted another
  go; revise if it was tense but unreadable; reject if the fetch felt like padding.

Then it is built with the ordinary skills — `core-scene-setup`, `core-input-setup`,
`3d-character-controller` — on placeholders.

### After you play it

**You:**

> Played it for ten minutes. I understood it, but the fetch felt like padding. The repair itself was
> the good bit.

That goes into the prototype's **Playtest log** as what you reported, in your words. The verdict is
**revise**, not reject: `design-decision-log` records it as

```
D-004 — Fetch is removed; the repair minigame carries the tension
Status: APPROVED   Affects: core loop, level layout, timer
Alternatives: shorten the fetch / keep it as an occasional event / remove it
Final choice (user-approved): remove the fetch from the core loop
```

An agent would have written that entry as `PROPOSED`. It is `APPROVED` because you said so.

---

## Part 2 — a new mechanic on an existing game

**You:**

> I want to add a grappling hook.

**Route:** `unity-game-router` reads `design/STATE.md` (Stage: `production`) and classifies this as
**significant** — a new system that touches movement and level design. So: `game-director` review
first, then `design-mechanic-spec`.

The director's review comes back with a conflict:

```
**Conflicts with approved decisions:** D-002 (APPROVED) — "no vertical traversal; every route is
walkable". Adopting the grapple reopens: all six level layouts, the camera's vertical limits, and
the fall-damage rule that exists because falls were short.

**Options:**
1. Adopt and supersede D-002 — strongest movement, ~4 sessions, reversibility: expensive
2. Horizontal-only grapple (swing across gaps, never up) — keeps D-002 intact, ~1 session,
   reversibility: cheap
3. Drop it — the dash already covers gap-crossing

**Recommendation:** option 2. It gets most of the player value without reopening six levels.
**Needs your approval:** whether D-002 stands.
```

Nothing was changed in `decisions.md` except a row in **Conflicts raised**. The approved entry was
not edited to fit the new idea — that conflict was the whole point of having the log.

You pick option 2. `design-decision-log` records D-005 as `APPROVED`, `design-mechanic-spec` writes
the rules, tuning table, feel numbers and acceptance checks, `gameplay-coder` implements it, and
`qa-playmode-check` reports observed values.

---

## Part 3 — what does *not* get this treatment

**You:**

> The jump height feels slightly too low. Try 8 instead of 7.5.

No discovery, no director review, no new spec. `design-mechanic-spec`'s triage calls this trivial:
edit the value in `design/mechanic-movement.md` and the tuning asset, re-run
`qa-playmode-check`, done.

**You:**

> The project won't compile.

`qa-fix-console-errors`, immediately. Design has nothing to say about a missing semicolon, and
`STATE.md` → **Blocked / broken** takes priority over whatever else was planned.

---

## What to take from this

- **A hypothesis is labelled a hypothesis** until a human plays it. The pack will not tell you your
  game is fun.
- **Placeholders are legitimate.** A prototype on capsules is the point, not a shortcut.
- **Approved decisions are load-bearing.** A new idea that contradicts one surfaces the conflict
  with its consequences, and you decide.
- **Process is proportional.** A new system earns a review; a tuning value does not.

Related: [2D platformer walkthrough](2d-platformer-walkthrough.md) ·
[3D third-person walkthrough](3d-third-person-walkthrough.md) · [USAGE.md](../docs/USAGE.md)
