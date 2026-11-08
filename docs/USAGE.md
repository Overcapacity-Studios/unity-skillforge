# Usage

## The contract: `design/` is the game, this pack is the method

Every skill starts by reading **`design/STATE.md`** and **`design/INDEX.md`** — and nothing else
until one of them points further. That is what keeps context cost flat as a project grows.

```
your-game/
  design/
    STATE.md            # where we are now. Read on EVERY task. Under 60 lines.
    INDEX.md            # a map of every other design doc. A doc with no row here is invisible.
    pitch.md            # fantasy, pillars, core loop, dimension, scope
    art-bible.md        # the style lock. No asset is made without it
    tech-decisions.md   # append-only decision log
    mechanic-<name>.md  # one per mechanic: rules, tuning, feel, acceptance checks
```

`install.sh` creates `STATE.md` and `INDEX.md`. The rest are created by the skills that own them.
If you have no `design/` folder, start with the first workflow below.

**The single most important field is `Dimension`** in `STATE.md`: `2D`, `2.5D` or `3D`. It decides
camera, renderer, physics, art cost and which skills load. The router asks rather than guessing.

---

## Workflow: a new game from a pitch

> **Prompt:** "I want to build a 2D platformer where a courier delivers parcels through a storm.
> Use the unity-game-router skill."

What happens:

1. `unity-game-router` finds no `design/` and routes to `design-write-gdd`.
2. `design-write-gdd` writes `pitch.md`, `STATE.md` and `INDEX.md`, and pins the dimension.
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

Describe the symptom, not a guess at the cause. The router picks the skill — here `3d-navmesh-ai`,
where a stale NavMesh is the usual answer. For 2.5D draw-order problems it is `25d-sorting-and-depth`.

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
| `designer` | opus / GPT-6.1 Sol | Pitch to docs, mechanic specs, scope cuts |
| `architect` | opus / GPT-6.1 Sol | Layers, assemblies, package and pattern decisions |
| `gameplay-coder` | sonnet / GPT-6.1 Terra | Implementing a specified mechanic |
| `asset-producer` | sonnet / GPT-6.1 Terra | Art and audio, generation and import |
| `qa` | haiku / GPT-6.1 Terra | Compile, test, play-mode verification |
| `reviewer` | opus / GPT-6.1 Sol | Accepting or rejecting a change |

> **Prompt:** "Use the designer agent to spec the grapple hook."

Each one reads only `design/STATE.md` and `design/INDEX.md` to start, and ends in a fixed handoff
format naming what it wrote, what it verified, and the next skill. Codex has no subagent directory —
[CODEX.md](CODEX.md) ships the same six as copy-paste prompts.

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
