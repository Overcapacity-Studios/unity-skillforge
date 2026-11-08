# Unity's official agent skills — and what we defer to them

**Snapshot 2026-11-08.** Unity ships a first-party skill pack. When it is installed, **prefer it**
for any topic in the map below and contribute only this pack's conventions on top.

Repos:
- [`Unity-Technologies/unity-agent-plugin`](https://github.com/Unity-Technologies/unity-agent-plugin)
  — the installable plugin (v0.1.9-beta at snapshot time).
- [`Unity-Technologies/skills`](https://github.com/Unity-Technologies/skills) — the upstream skill
  source (36 skills, actively maintained).

**Licence: Unity Companion License** — not an open-source licence, and limited to Unity-dependent
projects. **Never vendor or copy these skills into this repo.** Link and install them.

## Install

```
/plugin marketplace add Unity-Technologies/unity-agent-plugin
/plugin install unity@unity-agent-plugin
```

Verify by typing `/unity:` — the skills appear in the slash menu. Docs:
<https://docs.unity.com/en-us/ai/unity-plugin/claude-code> (sibling pages exist for Codex, Grok and
Antigravity).

Important: the plugin **ships skills only and does not install an MCP server**. Its Editor-touching
skills shell out to the Unity CLI, exactly as ours do. It therefore needs the Unity CLI installed,
`unity pipeline install` run in the project, and the Editor open.

## Overlap map — our skill → defer to

| Our skill | Unity's official skill | What stays ours |
| --- | --- | --- |
| `2d-sprite-import` | `sprite-editor`, `manage-sprite-atlas`, `2d-pixel-perfect` | Our PPU/pivot/compression presets and folder layout |
| `2d-tilemap-level` | `create-tile-palette-or-rule-tiles` | Grid/chunk conventions, level folder layout |
| `2d-physics-setup` | `create-2d-physics` | Which system this project pins, and our layer matrix |
| `3d-navmesh-ai` | `initialize-ai-navigation` | Agent/area naming and our AI state-machine wiring |
| `3d-cinemachine-camera` | `craft-game-floors` → `references/camera-rigs.md` (authoritative Cinemachine 3.x recipes) | Our camera naming and per-genre defaults |
| `3d-urp-lighting` | `urp-postprocessing`, `migrate-birp-to-urp`, `validate-urp-render-graph-renderer-feature`, `craft-game-floors` → `references/scene-lighting.md` | Baked GI / lightmap / Adaptive Probe Volume settings, which are thin officially |
| `core-scene-setup` | `new-unity-project`, `craft-game-floors` | Our bootstrap scene and additive-loading contract |
| `core-ui-toolkit` | `ui` (framework router) | Our screen/stack architecture and naming |
| `qa-run-tests` | `unity-cli` → `references/build-run-test.md` | Our test layout and acceptance gates |
| `qa-playmode-check` | `unity-pipeline` → `references/playmode-verification-loop.md` | Our per-mechanic acceptance checks |
| `qa-fix-console-errors` | `project-auditor-fixes`, `unity-pipeline` | Our stop-the-line rule and triage order |
| `qa-build` | `build-gtk`, `build-live-game`, `manage-cloud-build` | Our target matrix and build-profile naming |
| `assets-audio-sfx` | `audio-setup-mixers`, `optimize-audio` | Our mixer bus names and loudness targets |

## Topics fully owned by Unity — do not write a skill for these

`shader-graph-create-custom-node`, `optimize-text-mesh-pro`, `optimize-web`,
`localize-unity-project`, `unity-package-management`, `implement-in-app-purchases`,
`levelplay-unity-integration`, `setup-vivox-voice-chat`, `setup-multiplayer-services`,
`asset-transformer-toolkit` (Pixyz), `generate-editor-search-query`, `sprite-segment-3x3grid`,
`fix-3d-physics-collisions`, `manage-cloud-build`, `build-live-game`.

If a user asks for one of these, route to the `/unity:*` skill. If the plugin is not installed, say
so and offer the install commands above rather than improvising.

## Topics nothing official covers — fully ours

2.5D in every form (`25d-*`), a 3D character controller, the generated-asset import glue
(`assets-gen-2d-sprite`, `assets-gen-3d-model`, `assets-import-pipeline`, `assets-art-style-lock`),
the design-doc workflow (`design-*`), the core architecture patterns (`core-event-channels`,
`core-scriptable-object-data`, `core-save-system`, `core-unity-script`), `core-input-setup`, and the
2D/2.5D/3D router (`unity-game-router`).

## Other complementary packs

| Pack | Licence | Install | Why |
| --- | --- | --- | --- |
| [gamedev-skills/awesome-gamedev-agent-skills](https://github.com/gamedev-skills/awesome-gamedev-agent-skills) | Apache-2.0 | `claude plugin marketplace add gamedev-skills/awesome-gamedev-agent-skills` then `claude plugin install unity@awesome-gamedev-agent-skills` | 8-skill Unity bundle plus engine-neutral `camera-systems`, `create-game-assets`, `save-systems`, `game-feel` |
| [nowsprinting/unity-coding-skills](https://github.com/nowsprinting/unity-coding-skills) | Unlicense | `/plugin marketplace add nowsprinting/unity-coding-skills` | Deep test-first Unity C#. Caveat: several skills expect the JetBrains Rider MCP server |
| [Besty0728/Unity-Skills](https://github.com/Besty0728/Unity-Skills) | MIT | UPM package plus a local HTTP server | Optional: a very large REST editor-automation surface |

Do not link these, which were stale at snapshot time: `tea-x-random/unity-game-skills`,
`tjboudreaux/cc-plugin-unity-gamedev`, `jahro-console/unity-agent-skills`,
`Xenoneqq/unity-ai-skills`. `nowsprinting/claude-code-settings-for-unity` is archived and superseded
by `unity-coding-skills`.
