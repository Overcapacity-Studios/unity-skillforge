---
name: design-write-gdd
description: Turn a game pitch into the design folder this pack depends on - STATE.md, INDEX.md and pitch.md - with the dimension, pillars and minimum playable scope decided. Use at the start of a project or when design docs are missing. Every other skill reads what this produces.
metadata:
  version: 0.2.0
---

# Write the design docs

Paths written as `PACK/` mean wherever this pack's shared files live: `.unity-skillforge/` in a
game repo (`install.sh`), the sibling `unity-skillforge-pack` folder (`npx skills add`), the
plugin's root directory (plugin install), or `skills/unity-skillforge-pack/` in this repo.

## When to use

- A concept is **agreed** — the player's verbs, the loop and the scope are decided — and needs to
  become the pitch every other skill reads.
- A project has code but no `design/` folder, so no skill knows what it is building.
- The pitch has changed enough that the pillars or dimension need restating.

**If the idea is still rough, run `design-idea-discovery` first.** Writing a GDD from one sentence
hands the user a dozen decisions they never made, and they only find out when the game is wrong.

This runs **before** any code or art. Every other skill in this pack starts by reading
`design/STATE.md` and `design/INDEX.md`; if they do not exist, nothing else can work properly.

## Inputs needed

- `design/concept.md` if `design-idea-discovery` produced one. It carries the fantasy, verbs, loop,
  pillars and risks already, and **its confirmed lines are decisions, not suggestions** — carry them
  forward verbatim and do not re-ask them.
- Otherwise the pitch, in whatever form it exists — a sentence is enough to start.
- The target platform and frame target.
- The dimension, or enough information to recommend one. **This is the decision with the widest
  consequences:** it determines camera, renderer, physics, art cost and which skills load.

## Steps

1. Create `design/` in the game repo if it does not exist. If `design/concept.md` exists, read it
   first and treat its **confirmed** lines as settled; only its **assumed** lines are open.
2. Copy all three templates:
   - `PACK/templates/game-design/STATE.md` → `design/STATE.md`
   - `PACK/templates/game-design/INDEX.md` → `design/INDEX.md`
   - `PACK/templates/game-design/pitch.md` → `design/pitch.md`
3. Fill `design/pitch.md` first, because the other two summarise it:
   - **One line**: genre, core verb, goal. If you cannot write it in one line, the pitch is not
     decided yet — ask.
   - **The fantasy**: two or three sentences, written for a player, not a developer.
   - **Pillars**: at most three. Every later feature must serve one; a feature serving none gets
     cut. Three vague pillars are worse than two sharp ones.
   - **Core loop**: second-to-second, minute-to-minute, session-to-session, concretely.
   - **Dimension and why**: 2D, 2.5D or 3D with a one-sentence justification. Use the table below.
   - **Scope**, **Minimum playable**, and **Explicitly not in v1**.
4. Decide the dimension deliberately:
   | Dimension | Choose when | Costs |
   | --- | --- | --- |
   | **2D** | Art is flat, camera faces the plane, no depth gameplay | Cheapest art, simplest physics |
   | **2.5D** | 3D space and lighting, 2D presentation, fixed camera angle | Depth and sorting become the main source of visual bugs |
   | **3D** | Free camera, depth matters to gameplay | Most expensive art, most systems needed |
   Record it in `design/pitch.md` and `design/STATE.md`. Changing it later invalidates camera,
   renderer, art and physics work.
5. Fill `design/STATE.md`: the one line, **Stage**, dimension, Unity version, target platform and
   frame target, and the status table with everything honestly at "not started". Stage is
   `prototype` if the loop is still being tested, `production` once it is agreed. Keep it **under
   60 lines** — it is read on every single task, so it is the most expensive file per token.
6. Fill `design/INDEX.md` with a row for every document that exists. A design doc without a row is
   invisible to every agent.
7. Ask about scope only where it changes what gets built. Do not interview the user through the
   whole template — fill what you can from the pitch, state your assumptions, and name the gaps.
8. **Do not write mechanic specs here.** Each mechanic gets its own file via `design-mechanic-spec`
   when it is about to be built. Writing twelve specs up front produces eleven that are wrong by the
   time they are needed.
9. Record the decisions this pitch settles — dimension, failure model, what the game is not —
   through `design-decision-log`, as `APPROVED` only where the user actually agreed. The pitch
   states them; the log is where later tasks check them.
10. Run `assets-art-style-lock` next if **production** art will be generated. A prototype runs on
    placeholders and does not wait for it — see `design-prototype-plan`.
11. Report what you filled, what you assumed, and what still needs the user's decision.

## Unity CLI commands used

None. This skill writes design documents only and does not touch the Unity Editor. If the Unity
version needs recording:

```bash
unity --version                # the CLI version
unity editors -i               # installed Editors
```

See `PACK/references/unity-cli.md` and `PACK/references/unity-versions.md`.

## Files to read (exact paths)

| Need | Path |
| --- | --- |
| The agreed concept, if one exists | `design/concept.md` |
| Templates to copy | `PACK/templates/game-design/STATE.md` |
| | `PACK/templates/game-design/INDEX.md` |
| | `PACK/templates/game-design/pitch.md` |
| Unity and package pins to record | `PACK/references/unity-versions.md` |
| Routing table, to know what skills exist | the `unity-game-router` skill |
| Next gate for production art | the `assets-art-style-lock` skill |
| Where the pitch's decisions are logged | the `design-decision-log` skill |
| What to run first if the idea is rough | the `design-idea-discovery` skill |
| Per-mechanic specs, later | the `design-mechanic-spec` skill |

## Done checklist

- [ ] `design/STATE.md`, `design/INDEX.md` and `design/pitch.md` all exist.
- [ ] The one line is genuinely one line.
- [ ] At most three pillars, each specific enough to rule something out.
- [ ] The core loop is written concretely at all three timescales.
- [ ] A rough idea was sent to `design-idea-discovery` instead of being written up here.
- [ ] A concept doc's confirmed lines were carried forward, not re-asked.
- [ ] `STATE.md` has a Stage.
- [ ] The dimension is chosen, justified, and recorded in both `pitch.md` and `STATE.md`.
- [ ] Minimum playable is stated, and so is what is explicitly not in v1.
- [ ] `STATE.md` is under 60 lines and its status table is honest.
- [ ] `INDEX.md` has a row for every existing design document.
- [ ] No mechanic specs were written up front.
- [ ] Assumptions and open decisions were reported to the user.

## Common mistakes

- Writing a long GDD nobody reads. These three files are read on every task; length is a direct
  token cost on all future work.
- Leaving the dimension undecided, so the router cannot pick a path and later work has to be redone.
- Five or six pillars, which rule nothing out and so cut nothing.
- A status table that claims progress that does not exist, which misleads every later agent.
- Writing specs for every planned mechanic at the start; most will be wrong by the time they matter.
- Interviewing the user through the entire template instead of filling in the obvious and naming
  the real gaps.
- Creating a design doc without adding its row to `INDEX.md`, so no agent ever opens it.
- Letting `STATE.md` grow into a changelog. It describes now, not history.
- Writing a full GDD from a one-sentence idea, so the user inherits decisions they never made.
- Re-asking what `design/concept.md` already records as confirmed.
- Blocking a prototype on an art style it does not need.
