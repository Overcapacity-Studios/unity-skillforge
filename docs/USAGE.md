# Usage

## The contract: `design/` is the game, this pack is the method

Every skill starts by reading **`design/STATE.md`** and **`design/INDEX.md`** — and nothing else
until one of them points further. That is what keeps context cost flat as a project grows.

```
your-game/
  design/
    STATE.md            # where we are now, incl. Stage. Read on EVERY task. Under 60 lines.
    INDEX.md            # a map of every other design doc. A doc with no row here is invisible.
    concept.md          # the early hypothesis: verbs, loop, risks. Pre-pitch, pre-Unity
    pitch.md            # fantasy, pillars, core loop, dimension, scope
    decisions.md        # DESIGN decisions: what the game is. Read its Index table, not the file
    art-bible.md        # the style lock. No production asset is made without it
    tech-decisions.md   # TECHNICAL decisions: how it is built. Append-only
    mechanic-<name>.md  # one per mechanic: rules, tuning, feel, acceptance checks
    prototype-<name>.md # one per hypothesis: minimum test, criteria, and the playtest log
```

`decisions.md` and `tech-decisions.md` are deliberately separate: *what the game is* versus *how it
is built*. The first is owned by the designer and the game-director, the second by the architect.

`install.sh` creates `STATE.md` and `INDEX.md`. The rest are created by the skills that own them.
If you have no `design/` folder, start with the first workflow below.

**The single most important field is `Dimension`** in `STATE.md`: `2D`, `2.5D` or `3D`. It decides
camera, renderer, physics, art cost and which skills load. The router asks rather than guessing.

**`Stage`** — `concept`, `prototype`, `production`, `polish`, `shipped` — is how an existing project
resumes instead of restarting. A project with no Stage field is treated as `production`, so older
`design/` folders keep working unchanged.

---

## Workflow: a rough idea

> **Prompt:** "I have a rough idea — a game about repairing lighthouses in a storm. Help me develop
> it. Use the unity-game-router skill."

```
design-idea-discovery → (you agree) → design-write-gdd → design-prototype-plan
```

`design-idea-discovery` is a conversation, not a document generator. It plays the idea back, asks at
most three high-impact questions at a time, offers concrete options with tradeoffs, challenges what
contradicts itself, names the gameplay and technical risks, and writes `design/concept.md` with
every line marked **confirmed** or **assumed**. It will not write a GDD from one sentence, and it
needs no Unity project, no Unity CLI and no art decision.

Walkthrough: [idea to prototype](../examples/idea-to-prototype-walkthrough.md).

## Workflow: get the design challenged

> **Prompt:** "Act as my game director. Find the weaknesses in my core loop."
> **Prompt:** "Would adding multiplayer damage the current design?"
> **Prompt:** "Review the grapple hook against the whole game."

The `game-director` agent reads `STATE.md`, `INDEX.md` and the Index table of `decisions.md`, then
only the mechanics the question touches. It reports design context, player impact, effect on
existing mechanics, conflicts with approved decisions, production cost, risks, options with
tradeoffs, a recommendation, and **what needs your approval**.

What it will not do: approve its own recommendation, override something you decided, rewrite the
GDD for a small change, block a bug fix, or tell you a mechanic is fun. Fun is observed, not
derived — it will route you to a prototype instead.

## Workflow: prototype before committing

> **Prompt:** "I want to test whether the repair mechanic is tense before building it properly."

```
design-prototype-plan → core-* / dimension skills on PH_ placeholders → qa-playmode-check → you play it → design-decision-log
```

- **Placeholders are allowed with no art bible**: Unity primitives, flat materials, blockout
  geometry, debug visuals, unstyled UI. They go in `Assets/_Project/Prototype/` with a `PH_` prefix
  and are listed in the prototype doc. Generated production art is still gated on a locked style.
- Two kinds of validation are kept apart. **Technical** criteria (does it work, is it fast enough,
  do the controls behave) are measurable and run by `qa-playmode-check`. **Gameplay** questions (was
  it understood, did it feel right, were you frustrated) are answered only by a human who played it.
- **Agents never fill in the playtest log.** Until you report a session it says "not played yet",
  and the verdict stays "not concluded". Tell the agent what happened and it transcribes it.

## Workflow: a new game from an agreed pitch

> **Prompt:** "I want to build a 2D platformer where a courier delivers parcels through a storm.
> Use the unity-game-router skill."

What happens:

1. `unity-game-router` finds no `design/` and, because the concept is already settled, routes to
   `design-write-gdd`. A vaguer idea would have gone to `design-idea-discovery` instead.
2. `design-write-gdd` writes `pitch.md`, `STATE.md` and `INDEX.md`, pins the dimension and the
   Stage, and logs what the pitch settles through `design-decision-log`.
3. `assets-art-style-lock` creates `art-bible.md`. **Give it a reference image** — a style cannot be
   locked with adjectives, and every later asset depends on this.
4. `core-scene-setup` builds the bootstrap scene; `core-input-setup` wires the Input System.
5. `design-mechanic-spec` specs the first mechanic, then the matching build skill implements it.
6. `qa-playmode-check` verifies it against the spec's acceptance checks.
7. `design-update-state` records where things stand.

Expect to be asked about the dimension and the art style. Those are the two answers nothing else can
be derived from.

## Workflow: add a mechanic

> **Prompt:** "Add a dash: short burst, brief invulnerability, cooldown."

```
design-mechanic-spec → core-scriptable-object-data → core-unity-script → qa-playmode-check
```

For a **significant** mechanic — a new system, a core-loop change, a scope increase — a
`game-director` review comes first, and `design-mechanic-spec`'s fit review checks it against the
pillars, the loop, the mechanics it touches and `decisions.md`. For a **trivial** change — a tuning
value, a rename, a bug — none of that runs: edit the number and re-verify. Process is proportional
on purpose.

The spec comes first on purpose. It produces the **acceptance checks**, which are what makes "done"
decidable instead of a matter of opinion. If you skip it, `qa-playmode-check` has nothing to measure
and `gameplay-coder` will refuse to start.

Numbers you do not supply are proposed and flagged as proposals. Correct them in the spec, not in
the code.

## Workflow: generate an asset set

> **Prompt:** "Generate four enemy sprites for the game."

```
assets-art-style-lock (gate) → assets-gen-2d-sprite → 2d-sprite-import → 2d-sprite-animation
```

- If `art-bible.md` is not locked, the generation skills **stop**. That is deliberate: an unlocked
  style means every asset is a fresh guess and the set has to be redone.
- For 3D: `assets-gen-3d-model` → `assets-import-pipeline`. It reports credit cost **before**
  spending, and generation is asynchronous, so it polls before downloading.
- A raw download is never the finished asset. `assets-import-pipeline` owns scale, axis, LODs, URP
  material conversion and Avatar retargeting.
- Every asset gets a licensing row. See [ASSETS.md](ASSETS.md).

## Workflow: fix errors

> **Prompt:** "The project won't compile."

```
qa-fix-console-errors
```

This is a **stop-the-line** skill: while the console has errors, no new feature work starts. It
fixes compile errors first, then runtime errors, then warnings — `--strict` treats a warning as a
failure, and so does the skill.

> **Prompt:** "Enemies walk through walls."

Describe the symptom, not a guess at the cause, and let the router disambiguate. This particular
symptom is genuinely ambiguous: if the enemies are *pathing* through a wall that exists, it is a
stale NavMesh (`3d-navmesh-ai`); if they are *passing through* a collider that should stop them, it
is collision, which Unity's own `/unity:fix-3d-physics-collisions` owns. Saying which one you see —
"they walk a straight line through the wall" versus "they slide through it when pushed" — picks the
right skill immediately. For 2.5D draw-order problems it is `25d-sorting-and-depth`.

## Workflow: build

> **Prompt:** "Make a Windows build."

```
qa-run-tests → qa-build
```

`qa-build` gates on a clean `unity recompile --strict` and a green test suite before it starts, then
discovers real targets with `unity build --list-targets` rather than assuming, and **launches the
build** afterwards — "it compiled" is not "it runs".

## Workflow: review before committing

> **Prompt:** "Review this change with the reviewer agent."

The reviewer reads the diff and the mechanic spec, re-runs the checks rather than trusting the
report, and ranks findings as blocking, should-fix or nit. It reports; it does not rewrite.

---

## Using the subagents

| Agent | Model hint | Use it for |
| --- | --- | --- |
| `game-director` | opus / GPT-6.1 Sol | Judging a feature against the whole game, scope, conflicts |
| `designer` | opus / GPT-6.1 Sol | Concept, pitch, mechanic specs, prototype plans, scope cuts |
| `architect` | opus / GPT-6.1 Sol | Layers, assemblies, package and pattern decisions |
| `gameplay-coder` | sonnet / GPT-6.1 Terra | Implementing a specified mechanic |
| `asset-producer` | sonnet / GPT-6.1 Terra | Art and audio, generation and import |
| `qa` | haiku / GPT-6.1 Terra | Compile, test, play-mode verification |
| `reviewer` | opus / GPT-6.1 Sol | Accepting or rejecting a change |

> **Prompt:** "Use the designer agent to spec the grapple hook."

Each one reads only `design/STATE.md` and `design/INDEX.md` to start, and ends in a fixed handoff
format naming what it wrote, what it verified, and where the work goes next — the next skill for the
building roles, "hand back to" for `qa` and `reviewer`.

Codex has no subagent directory. `install.sh` copies the seven role files to
`.unity-skillforge/agents/`, and [CODEX.md](CODEX.md) gives a one-line prompt for each that points
at them.

## Habits that keep it working

- **Describe the symptom, not the fix.** "Sprites draw in front of walls" routes correctly; "change
  the sorting layer" sends the agent to the wrong system.
- **One mechanic at a time.** The rules require a clean compile and green tests before the next one.
- **Answer the dimension and art-style questions properly.** They are the two inputs everything else
  derives from.
- **Treat "not verified" as a real answer.** If no Editor was reachable, the skills say so rather
  than inferring a pass. That is the behaviour you want.
- **Let it update `STATE.md`.** The next session starts from that file, and a stale one causes
  finished work to be redone.
- **Say when a proposed number is wrong.** Agents propose defaults and flag them; correcting the
  spec is cheaper than correcting the code.
- **You approve decisions; agents propose them.** Anything in `decisions.md` marked `PROPOSED` is
  waiting on you. Nothing becomes `APPROVED` because an agent liked its own idea.
- **Report playtests in your own words.** "I got lost after the second room" is worth more than any
  metric here, and it is the only input that can answer a gameplay question.
