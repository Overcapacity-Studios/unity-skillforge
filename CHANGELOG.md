# Changelog

All notable changes to this project are documented here. Format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versioning is
[semantic](https://semver.org/spec/v2.0.0.html).

## [0.2.0] — 2026-11-08

Extends the pack from "build what is specified" to "work out what is worth building, then build
it". The existing architecture, routing and install guarantees are unchanged.

### Added

- **`design-idea-discovery`** — develops a rough idea into `design/concept.md` through a
  collaborative conversation: plays the idea back, asks at most three high-impact questions at a
  time, proposes options with tradeoffs, challenges contradictions and unearned scope, separates
  gameplay from technical risk, and recommends a minimum playable experience. Needs no Unity
  project, no CLI and no art decision. Every line it writes is marked confirmed or assumed.
- **`design-prototype-plan`** — plans the smallest playable test of one falsifiable hypothesis:
  minimum feature set, an explicit NOT list, `PH_` placeholders, measurable technical criteria for
  `qa-playmode-check`, human-only gameplay questions, complexity estimates labelled as assumptions,
  and success/revise/reject criteria agreed before building. Its playtest log is filled only from
  what a human reports.
- **`design-decision-log`** — records and queries `design/decisions.md`: context, alternatives, the
  recommendation, the user-approved choice, affected systems, dependencies and status
  (`PROPOSED`, `APPROVED`, `REJECTED`, `SUPERSEDED`, `NEEDS VALIDATION`). Append-only, read by its
  Index table, and it surfaces a conflict with an approved decision rather than absorbing it.
- **`game-director` subagent** — judges a feature against the whole game: pillars, core loop,
  mechanic interactions, conflicts, production cost, risks, options with tradeoffs, a
  recommendation, and an explicit "needs your approval" line. It never approves its own
  recommendation, never overrides the user, and never claims a mechanic is fun.
- **Three design templates**: `concept.md`, `prototype.md` (with the playtest log) and
  `decisions.md`.
- **`Stage`** field in `design/STATE.md` — `concept`, `prototype`, `production`, `polish`,
  `shipped` — so an existing project resumes instead of restarting. A `design/` folder with no
  Stage is treated as `production`, so older projects keep working unchanged.
- **The prototype asset exception.** Unity primitives, flat materials, blockout geometry, debug
  visuals and unstyled UI need no locked art bible, provided they live in
  `Assets/_Project/Prototype/` with a `PH_` prefix and are listed in the prototype doc. Generated,
  bought or downloaded production art is still gated on a 🟢 lock, and a placeholder never becomes
  production art by being renamed.
- **`scripts/test-workflows.py`** — 126 static checks covering the six workflow cases (vague idea,
  conflicting mechanic, prototype before art style, resuming a project, bug fix, no Editor) plus
  packaging. Wired into CI. They check what the documents say; they run no agent and contact no
  Unity Editor.
- **`examples/idea-to-prototype-walkthrough.md`** — a rough idea to a played prototype, a new
  mechanic that conflicts with an approved decision, and the changes that correctly get no process
  at all.

### Changed

- `unity-game-router` routes by **kind of beginning** and by **Stage**: a rough idea to discovery, an
  agreed concept to the GDD, a significant change through a `game-director` review, and trivial work
  straight to the skill that fixes it. It no longer sends every new game to `design-write-gdd`, and
  creative discussion no longer requires a Unity project or a dimension.
- `design-mechanic-spec` gained a **fit review** — pillars, core loop, affected mechanics, system
  dependencies, player impact, decision conflicts, whether a prototype is needed, and a verdict —
  with explicit triage so a trivial change skips it entirely.
- `design-write-gdd` treats a concept doc's confirmed lines as settled, sets `Stage`, logs what the
  pitch decides, and gates only **production** art on the art bible.
- `design-update-state` maintains `Stage` and prototype status, points at both decision logs, and
  refuses to record a playtest outcome the user did not report.
- `assets-art-style-lock` documents the prototype exception; `assets-gen-2d-sprite` and
  `assets-gen-3d-model` keep their gate and name the placeholder route instead.
- `designer`, `asset-producer`, `gameplay-coder`, `qa` and `reviewer` updated for the new documents:
  the designer may run the new design skills, the asset producer reports an asset class, the coder
  can build to a prototype plan, QA reports gameplay questions as "requires a human playtest", and
  the reviewer treats a decision conflict or a shipped placeholder as blocking.
- `AGENTS.md`: hard rule 8 now distinguishes production art from placeholders, rule 3 adds "respect
  what is already there", and the output discipline adds proportionality and "a hypothesis is not a
  result".
- Docs and manifests updated throughout: 36 skills, 7 subagents, the end-to-end workflow and the
  role table in `README.md`, new workflows in `docs/USAGE.md`, the design-log and agent-vs-skill
  rationale in `docs/ARCHITECTURE.md`.

## [0.1.0] — 2026-11-08

First release.

### Added

- **33 skills**, flat under `skills/`, grouped by name prefix:
  - `unity-game-router` — classifies task and project dimension, loads the minimum skill set, and
    acts as Tier 0 on the plugin install path.
  - `design-*` (4) — pitch to design docs, mechanic specs, scope cuts, state updates.
  - `core-*` (7) — scripts, ScriptableObject data, event channels, input, save, UI Toolkit, scenes.
  - `2d-*` (5) — sprite import, tilemaps, 2D physics, sprite animation, 2D lighting.
  - `25d-*` (3) — fixed-angle camera, billboard sprites, sorting and depth.
  - `3d-*` (4) — character controller, Cinemachine, URP lighting, NavMesh AI.
  - `assets-*` (5) — art style lock, 2D and 3D generation, import pipeline, audio.
  - `qa-*` (4) — tests, play-mode verification, console errors, builds.
- **6 subagents** in `agents/` with model hints, exact read lists and fixed handoff formats.
- **Rules** (`rules/`): C# style, architecture, folder conventions, performance.
- **References** (`references/`): Unity CLI surface, version pins, the official-skill overlap map,
  URP settings, Input System conventions, Meshy MCP tool names, and the deprecated Unity MCP surface.
- **Templates**: seven copy-ready C# files and the six-file `design/` contract.
- **Scripts**: `validate-skills.py`, `install.sh`, `install.ps1`, `sync-agents-dir.sh`,
  `slice-spritesheet.py`.
- **Plugin manifests** for both agents: `.claude-plugin/` (the repo is both a marketplace and the
  plugin it lists) and `.codex-plugin/` plus `.agents/plugins/`.
- **Docs**: install, usage, architecture, Codex, assets, troubleshooting, contributing, and two
  end-to-end walkthroughs.

### Decisions worth knowing

These departed from the original specification, each for a documented reason:

- **The Editor bridge is the Unity CLI, not MCP.** Unity deprecated the in-Editor MCP server in
  `com.unity.ai.assistant`. The CLI plus the Pipeline package replaces it, is free (no Unity AI
  subscription or Unity Cloud link required), and is faster and cheaper in tokens by Unity's own
  documentation. `unity mcp configure` remains the documented fallback for agents that cannot run
  shell commands.
- **Baseline is Unity 6.3 LTS (`6000.3.x`), not 6.0.** Unity 6.0 LTS support ended October 2026.
- **Skills are flat, with name prefixes.** Nested skill directories are not a supported layout in
  either Claude Code or Codex.
- **Skill frontmatter is restricted** to `name`, `description` and `metadata`, so a skill stays
  valid outside Claude Code, where any other key is a hard error.
- **Unity's official plugin is linked, never vendored** (Unity Companion License). The 13 skills
  whose topics overlap defer to the `/unity:*` skill by name and contribute only this project's
  conventions.

### Reviewed

A fresh-context agent read only `README.md` and `docs/INSTALL.md` as a newcomer and reported gaps,
all of which were fixed before release: `PACK/` had no defined resolution on the plugin install
path, there was no uninstall script, the two install paths were described contradictorily, the
verification step assumed one of them, PowerShell switches were documented as Bash flags, and the
glossary terms this project leans on (skill, router, dimension, `design/`, Tier 0) were used
without ever being defined.

One of its findings was wrong and was not acted on: Homebrew's `unity-cli` cask does ship Linux
binaries, so "macOS / Linux via Homebrew" was correct.

A second round ran a real install and uninstall and found two code bugs — `install.sh` skipped
`design/STATE.md` whenever a `design/` folder already existed, and `uninstall.sh` left behind the
section it had appended to an existing `AGENTS.md`, pointing at a directory it had just deleted.

A third audit checked `USAGE.md`, `ARCHITECTURE.md`, `CODEX.md` and `TROUBLESHOOTING.md` against the
repo and against Anthropic's and OpenAI's published documentation. It found the Codex role-file path
dangled (nothing installed `agents/` where `CODEX.md` said to look), the validator claimed to
enforce seven skill sections while checking six, and several rationale claims in `ARCHITECTURE.md`
were stated more confidently than the sources support — notably that a plugin-root `AGENTS.md` is
not loaded (the `CLAUDE.md` half is documented; the `AGENTS.md` half is an assumption), that extra
frontmatter keys are a hard error, and that the angle-bracket rule comes from Anthropic rather than
from Unity's CI. All are corrected or hedged to match the evidence.

### Installable with `npx skills`

`npx skills add Overcapacity-Studios/unity-skillforge --all` installs the pack for Claude Code,
Codex and the other agents the [`skills` CLI](https://github.com/vercel-labs/skills) supports, and
`-s <name>` takes individual skills.

That CLI installs a skill by copying its own folder and nothing else, so the shared `references/`,
`rules/` and `templates/` tree moved from the repo root into `skills/unity-skillforge-pack/` — a
package that carries data and no procedure. It installs as a sibling of the skills that cite it, so
`PACK/...` resolves on every route. Bundling a copy into each skill instead was rejected on the
numbers: `references/unity-cli.md` alone is cited by 32 of 34 skills, which would have turned 70 KB
into roughly 700 KB and made every correction a 32-place edit.

### Not yet verified

No part of this release has been executed against a running Unity Editor. Every `unity` command,
import setting, play-mode check and Meshy call is documented from official sources rather than
observed. `install.ps1` has not been run on Windows. See `README.md` and `docs/TROUBLESHOOTING.md`.
