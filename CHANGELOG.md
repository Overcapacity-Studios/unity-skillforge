# Changelog

All notable changes to this project are documented here. Format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versioning is
[semantic](https://semver.org/spec/v2.0.0.html).

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

### Not yet verified

No part of this release has been executed against a running Unity Editor. Every `unity` command,
import setting, play-mode check and Meshy call is documented from official sources rather than
observed. `install.ps1` has not been run on Windows. See `README.md` and `docs/TROUBLESHOOTING.md`.
