# Design index

<!--
The SECOND and last file an agent reads by default. It is a map, not content.
One line per document so an agent can decide what to open without opening anything.
Never let a design doc exist without a row here.
-->

**Rule for agents:** read `design/STATE.md` and this file. Open anything below only when a task
needs it, and only the rows it needs.

## Core

| Document | Read it when | Path |
| --- | --- | --- |
| Pitch | You need the fantasy, audience, scope or pillars | `design/pitch.md` |
| Art bible | **Before generating or importing any asset** | `design/art-bible.md` |
| Technical decisions | Choosing a package, system or pattern | `design/tech-decisions.md` |

## Mechanics

<!-- One row per mechanic spec. File per mechanic: design/mechanic-<name>.md -->

| Mechanic | Status | Path |
| --- | --- | --- |
| <Movement> | spec'd / built / tuned | `design/mechanic-movement.md` |

## Content

| Document | Read it when | Path |
| --- | --- | --- |
| Level list | Building or editing a level | `design/levels.md` |
| Enemy / item tables | Adding or tuning content | `design/content-tables.md` |

## Out of scope

<!-- Explicitly cut, so no agent re-proposes it. Maintained by design-scope-cut. -->

- <Cut feature> — cut YYYY-MM-DD because <reason>.
