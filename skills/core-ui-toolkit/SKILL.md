---
name: core-ui-toolkit
description: Build a game UI screen with UI Toolkit - UXML layout, USS styling, and a screen stack driven by this project's architecture. Use for menus, HUD, settings and pause screens. Defer to Unity's own ui skill for framework choice and deep UI Toolkit questions.
metadata:
  version: 0.1.0
---

# UI Toolkit screens

Paths written as `PACK/` mean wherever this pack's shared files live: `.unity-skillforge/` in a
game repo (`install.sh`), the sibling `unity-skillforge-pack` folder (`npx skills add`), the
plugin's root directory (plugin install), or `skills/unity-skillforge-pack/` in this repo.

## When to use

- Adding a menu, HUD, settings panel or pause screen.
- Replacing an ad-hoc uGUI screen with the project's screen stack.
- Fixing input leaking to gameplay while a screen is open.

## Prefer the official skill

Unity's official plugin owns UI framework choice and deep UI Toolkit mechanics. If it is installed:

- `/unity:ui` — the framework router. Run it first if the choice between UI Toolkit, uGUI and IMGUI
  is not already settled in `design/tech-decisions.md`.
- `/unity:optimize-text-mesh-pro` — any TextMeshPro work.

What stays ours: the **screen stack contract**, naming, folder layout, and the input-map handoff
below. Do not restate Unity's UI Toolkit procedure here — link it. See
`PACK/references/official-unity-skills.md`.

## Inputs needed

- Which screen, and whether it is a full screen (pauses the game) or an overlay (does not).
- The data it shows and the actions it offers.
- Whether the UI framework choice is recorded in `design/tech-decisions.md`. If not, settle it first.

## Steps

1. Read `design/STATE.md` and `design/INDEX.md`, then `design/art-bible.md` for palette and type.
2. Confirm UI Toolkit is the recorded choice in `design/tech-decisions.md`. If it is not recorded,
   run `/unity:ui` (or decide and record it) before building anything.
3. Create the three files per screen under `Assets/_Project/UI/<ScreenName>/`:
   - `<ScreenName>.uxml` — structure only, no inline styles.
   - `<ScreenName>.uss` — styling, using variables for every colour from the art bible.
   - the controller script at `Assets/_Project/Code/Features/UI/<ScreenName>Screen.cs`.
4. Define shared design tokens once in `Assets/_Project/UI/Shared/Tokens.uss` as custom properties
   (`--color-accent`, `--space-2`, `--font-size-body`) and reference them. A hex value typed into a
   screen's USS is a bug — the art bible is the source.
5. Name elements in UXML with a `name` attribute in kebab-case (`start-button`) and query them once
   in the controller:
   ```csharp
   _startButton = _root.Q<Button>("start-button");
   ```
   Query in `OnEnable`, cache the result. Never query per frame.
6. Wire callbacks with `clicked +=` in `OnEnable` and `-=` in `OnDisable`. Paired, always.
7. Implement the screen stack contract:
   - A full screen pushes onto the stack, disables the `Player` input map and enables `UI`.
   - Popping the last full screen re-enables `Player`.
   - Map switching goes through the one place defined by `core-input-setup` — not here.
   - An overlay does not touch input maps.
8. Feed the screen data through an event channel or a service, never by reaching into a feature.
   See `core-event-channels` and `PACK/rules/architecture.md`.
9. Set `Raycast Target`/`picking-mode` to ignore on anything non-interactive, and keep static and
   dynamic UI on separate documents — see `PACK/rules/performance.md`.
10. Compile and verify:
    ```bash
    unity recompile --strict --format json
    ```
    then run `qa-playmode-check`: open the screen, confirm gameplay does not react, close it,
    confirm gameplay resumes.

## Unity CLI commands used

```bash
unity status                              # confirm an Editor is reachable
unity list                                # Editor-registered tools and their parameter schemas
unity recompile --strict --format json    # compile check
unity test --format json                  # PlayMode tests for open and close behaviour
```

`.uxml` and `.uss` are text, so they can be written directly — but create the `UIDocument` and
panel settings through the Editor or `eval_file` so `.meta` files stay consistent. See
`PACK/references/unity-cli.md`.

## Files to read (exact paths)

| Need | Path |
| --- | --- |
| Project status | `design/STATE.md` |
| Design map | `design/INDEX.md` |
| Palette, type, UI look | `design/art-bible.md` |
| Recorded UI framework choice | `design/tech-decisions.md` |
| Official skill map | `PACK/references/official-unity-skills.md` |
| Input map switching | `PACK/references/input-system.md` |
| Layer rules | `PACK/rules/architecture.md` |
| UI cost rules | `PACK/rules/performance.md` |
| Folder layout | `PACK/rules/folder-conventions.md` |

## Done checklist

- [ ] UI Toolkit is the recorded choice in `design/tech-decisions.md`.
- [ ] UXML holds structure only; all styling is in USS.
- [ ] Every colour and spacing value comes from `Tokens.uss`, sourced from the art bible.
- [ ] Elements are queried once and cached, never per frame.
- [ ] Every `clicked +=` has a matching `-=` in `OnDisable`.
- [ ] A full screen disables `Player` and enables `UI`; closing it reverses that.
- [ ] The screen gets its data via a channel or service, not by referencing a feature.
- [ ] Non-interactive elements do not block picking.
- [ ] Verified in play mode: gameplay is inert while the screen is open and resumes after.

## Common mistakes

- Hardcoding colours in a screen's USS, so an art-bible change misses half the UI.
- Querying elements in `Update`, which allocates and costs every frame.
- Opening a screen without disabling the `Player` map, so the player keeps moving behind the menu.
- Doing the map switch inside the screen instead of the one place that owns it, so two screens
  disagree about state.
- Leaving a `clicked` handler subscribed, so a reopened screen fires its buttons twice.
- Putting an animated element on the same document as a large static one, forcing a full rebuild.
- Reaching into a gameplay feature from the controller, creating the assembly cycle the architecture
  rules exist to prevent.
