---
name: design-decision-log
description: Record and query the game's design decisions - context, alternatives, the user-approved choice, affected systems and status. Use when a design choice is settled, and to check a new proposal against approved decisions before building. Append-only, so history survives.
metadata:
  version: 0.1.0
---

# Design decision log

Paths written as `PACK/` mean wherever this pack's shared files live: `.unity-skillforge/` in a
game repo (`install.sh`), the sibling `unity-skillforge-pack` folder (`npx skills add`), the
plugin's root directory (plugin install), or `skills/unity-skillforge-pack/` in this repo.

## When to use

- A design choice has been made and will constrain later work: progression shape, economy, failure
  model, control scheme, what the game is not.
- **Before proposing a significant feature**, to check it against what is already approved.
- A prototype concluded, so a `NEEDS VALIDATION` entry can be resolved.
- A proposal contradicts an approved decision and the conflict must be surfaced.

Not for technical choices — packages, assemblies, patterns and renderers go in
`design/tech-decisions.md`, owned by the `architect`. The split is deliberate: this file answers
*what the game is*, that one answers *how it is built*.

## Inputs needed

- The decision, in one line.
- Whether the **user approved it**. If they did not, it is `PROPOSED` and not in effect.
- The alternatives that were actually considered, and what each would have cost.
- Which gameplay systems it affects.

## Steps

1. Read `design/STATE.md` and `design/INDEX.md`.
2. Read **only the Index table** of `design/decisions.md`. Open a full entry when the task touches
   it. Loading the whole history for an unrelated task is the failure this file's shape exists to
   prevent.
3. If `design/decisions.md` does not exist, copy
   `PACK/templates/game-design/decisions.md` to `design/decisions.md` and add a row to
   `design/INDEX.md`.
4. **Querying — check a proposal against the log.** Scan the Index for entries whose *Affects*
   column overlaps the proposal. For each overlap, open that entry and classify:
   | Finding | Do this |
   | --- | --- |
   | No overlap | Say so in one line and continue |
   | Overlaps, compatible | Note the dependency in the new entry |
   | **Contradicts an `APPROVED` entry** | Stop. Raise the conflict (step 5) |
   | Matches a `REJECTED` entry | Say it was rejected and when. Re-propose only with new information, and name what is new |
5. **Surfacing a conflict.** Never edit the approved entry to fit the new proposal. Add a row to
   **Conflicts raised** and report to the user:
   - which decision ID it contradicts, quoted;
   - what adopting the proposal would reopen — the mechanics, UI, saves and assets that were built
     on the old decision;
   - the cost of each path: adopt and supersede, drop the proposal, or find a third option.
   The user decides. Record their choice; do not infer it from their interest in the idea.
6. **Writing an entry.** Take the next ID from the `Next ID` field, increment it, and fill every
   field: context, alternatives with costs, the recommendation made, the final user-approved
   choice, rationale against the pillars, affected systems, dependencies, reversibility, and
   whether it needs validation.
7. Set the status honestly:
   - `PROPOSED` — the default for anything an agent suggests. **An agent never writes `APPROVED`
     for its own proposal.**
   - `APPROVED` — only when the user said yes. Quote or paraphrase their words in the final-choice
     field.
   - `REJECTED` — considered and declined, with the reason, so it is not re-proposed blindly.
   - `NEEDS VALIDATION` — approved in principle, pending a prototype or playtest result. Name the
     prototype file and the question that settles it, and the agreed fallback if it fails.
   - `SUPERSEDED` — set on the old entry when a new one replaces it, with a row in **Superseded**.
8. Add the entry to the **Index** table, and mirror only genuinely constraining ones into
   `STATE.md` → *Decisions that constrain new work* as a single line naming the ID. `STATE.md`
   stays under 60 lines; it is a pointer, not a copy.
9. **Append only.** Correct a typo; never rewrite the context, alternatives or rationale of an
   approved entry, and never delete one. The reasoning is the asset — a decision whose reasoning is
   lost gets re-argued every few sessions.
10. Resolving a `NEEDS VALIDATION` entry after a prototype: add a new entry recording the result and
    the outcome, and supersede the old one rather than editing it. Cite the prototype file and the
    actual observation. If no human played it, it stays `NEEDS VALIDATION`.
11. Set the Updated date and report: the ID, the status, and explicitly what still needs the user's
    approval.

## Unity CLI commands used

None. This skill edits a design document only and does not touch the Unity Editor. A decision
constrained by what the project actually does should cite the file or the `architect`'s entry in
`design/tech-decisions.md` rather than probing the Editor.

## Files to read (exact paths)

| Need | Path |
| --- | --- |
| Project status | `design/STATE.md` |
| Design map | `design/INDEX.md` |
| The log — Index table first, entries on demand | `design/decisions.md` |
| Template to copy | `PACK/templates/game-design/decisions.md` |
| Pillars a decision must serve | `design/pitch.md` |
| Technical decisions, which are not this file | `design/tech-decisions.md` |
| Prototype that validates an entry | `design/prototype-*.md` |
| Who reviews cross-system impact | the `game-director` agent |
| Where a cut is recorded instead | the `design-scope-cut` skill |

## Done checklist

- [ ] Only the Index table was read, plus the entries the task actually touched.
- [ ] A new proposal was checked against overlapping entries before being written.
- [ ] A contradiction with an `APPROVED` entry was raised, with consequences, not absorbed.
- [ ] A `REJECTED` entry was not re-proposed without naming what is new.
- [ ] The entry has an ID, and `Next ID` was incremented.
- [ ] Context, alternatives with costs, recommendation, final choice and rationale are all filled.
- [ ] Affected systems and dependencies are listed.
- [ ] The status is honest; nothing is `APPROVED` that the user did not approve.
- [ ] Any `NEEDS VALIDATION` entry names its prototype, its question and its fallback.
- [ ] A superseded entry was superseded, not rewritten or deleted.
- [ ] The Index row exists, and `STATE.md` carries at most a one-line pointer.

## Common mistakes

- **Recording an agent's own recommendation as `APPROVED`.** The log then claims the user decided
  something they never saw, and every later task treats it as binding.
- Editing an approved entry so a new idea no longer conflicts with it. The conflict was the
  information.
- Deleting a superseded entry, losing the reasoning and guaranteeing the argument happens again.
- Logging technical choices here instead of `design/tech-decisions.md`, so neither file is trusted.
- Copying whole entries into `STATE.md`, which then blows its 60-line budget on history.
- Reading the entire log on every task, which is exactly the cost the Index table exists to avoid.
- Logging trivia. A decision that constrains nothing is noise that hides the ones that do.
- Leaving a `NEEDS VALIDATION` entry open forever, so nobody knows whether it is in effect.
- Treating "the user seemed keen" as approval.
