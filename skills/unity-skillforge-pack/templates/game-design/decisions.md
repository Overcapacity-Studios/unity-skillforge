# Design decisions — <game name>

<!--
The DESIGN decision log, owned by design-decision-log. Sibling of tech-decisions.md:
that one records technical choices, this one records what the game IS.

Append-only. Never rewrite or delete an approved entry — supersede it, so the history of
why the game is like this survives.

READING THIS FILE: read the Index table only. Open a full entry when a task actually
touches that decision. Never load the whole history for an unrelated task.
-->

**Updated:** YYYY-MM-DD
**Next ID:** D-004

## Status legend

| Status | Means |
| --- | --- |
| `PROPOSED` | An agent or the user suggested it. **Not** in effect. Needs user approval |
| `APPROVED` | The user approved it. Binding on all later work |
| `REJECTED` | Considered and declined. Do not re-propose without new information |
| `SUPERSEDED` | Was approved, replaced by a later decision. Kept for its reasoning |
| `NEEDS VALIDATION` | Approved in principle, conditional on a playtest or prototype result |

Only the user moves an entry to `APPROVED` or `REJECTED`. An agent may write `PROPOSED`
and may suggest, but never record, an approval.

## Index

Scan this. Open a full entry below only when the task touches it.

| ID | Decision | Status | Affects | Date |
| --- | --- | --- | --- | --- |
| D-001 | <Single-run structure, no save mid-run> | APPROVED | progression, UI, save | YYYY-MM-DD |
| D-002 | <No multiplayer in v1> | APPROVED | scope, netcode, UI | YYYY-MM-DD |
| D-003 | <Stamina gates dashing> | NEEDS VALIDATION | movement, combat | YYYY-MM-DD |

## Entries

### D-001 — <Decision summary in one line>

- **Status:** APPROVED
- **Date:** YYYY-MM-DD
- **Context:** <what forced a choice here — the problem, not the solution>
- **Alternatives considered:**
  1. <Option> — <advantage> / <cost>
  2. <Option> — <advantage> / <cost>
- **Recommendation made:** <what the agent recommended, and why>
- **Final choice (user-approved):** <what the user chose — exactly, including any amendment>
- **Rationale:** <why this serves the pillars and the player experience>
- **Affected gameplay systems:** <mechanics, UI, progression, economy>
- **Dependencies:** <decisions or mechanics this relies on, by ID or file>
- **Reversibility:** cheap | expensive | one-way — <what reversing would cost>
- **Validation needed:** <none | the playtest question that would confirm it>

### D-003 — <Decision that is conditional>

- **Status:** NEEDS VALIDATION
- **Date:** YYYY-MM-DD
- **Validated by:** `design/prototype-<name>.md` → <which gameplay question>
- **If it fails:** <the fallback, agreed now so the failure is not a crisis>

## Conflicts raised

<!-- When a new proposal contradicts an APPROVED entry, record it here rather than
     quietly changing the entry. The user decides. -->

| Date | Proposal | Conflicts with | Consequence if adopted | Outcome |
| --- | --- | --- | --- | --- |
| YYYY-MM-DD | <Add co-op> | D-002 | <save, UI and camera all reopen> | <pending user decision> |

## Superseded

| ID | Was | Superseded by | Why |
| --- | --- | --- | --- |
| D-00n | <...> | D-00m | <...> |
