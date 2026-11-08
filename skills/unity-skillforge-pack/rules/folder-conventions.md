# Folder conventions

Exact layout. Skills create folders; they do not invent new top-level ones.

```
Assets/
  _Project/                     # all first-party content, so imported packages stay separate
    Art/
      Sprites/                  # 2D: source sheets + sliced sprites
      Models/                   # 3D: .fbx / .glb source
      Materials/
      Textures/
      Animations/
      VFX/
    Audio/
      Music/
      SFX/
      Mixers/
    Code/
      Core/          Game.Core.asmdef
      Systems/       Game.Systems.asmdef
      Features/      Game.Features.asmdef
      Game/          Game.Game.asmdef
      Tests/
        EditMode/    Game.Core.Tests.asmdef
        PlayMode/    Game.Features.PlayTests.asmdef
    Data/                       # ScriptableObject instances
      Items/  Levels/  Tuning/  EventChannels/
    Prefabs/
      Player/  Enemies/  Props/  UI/  Systems/
    Prototype/                  # TEMPORARY placeholder assets only. PH_ prefix. Deleted, not shipped
    Scenes/
      Bootstrap.unity
      Gameplay/
      UI/
    UI/                         # UI Toolkit: .uxml, .uss
  Settings/
    Rendering/                  # URP assets, renderer data, volume profiles
    Input/                      # GameInput.inputactions + generated class
    Build/                      # build profiles
ProjectSettings/
Packages/                       # manifest.json is pinned; never floating versions
design/                         # the game's own design docs — what we are building
```

## Rules

- **Everything first-party lives under `Assets/_Project/`.** The leading underscore sorts it to the
  top and keeps it clearly separate from Asset Store imports, which stay wherever they land.
- Folder names are PascalCase. No spaces, ever — spaces break command-line and CI paths.
- A folder per *type*, then per *subject*. Not the reverse: `Prefabs/Enemies/`, not
  `Enemies/Prefabs/`.
- An asset's `.meta` file is part of the asset. Move assets through the Editor or `unity command`,
  never with a bare `mv`, or you break every reference pointing at it.
- Source art (layered, full-resolution) does not belong in `Assets/`. Keep it in `art-source/` at
  the repo root, outside the Unity project, so Unity does not import it.
- Generated assets land in the matching `Art/` folder with the generation prompt recorded in
  `design/art-bible.md`, not in a floating notes file.
- **Prototype placeholders live in `Assets/_Project/Prototype/` and are named with a `PH_`
  prefix** — `PH_Player.prefab`, `PH_Grey.mat`, `PH_Arena.unity`. They are the only assets allowed
  without a locked `design/art-bible.md`: Unity primitives, the built-in default material,
  untextured blockout geometry, debug gizmos and unstyled UI labels. The prefix and the folder exist
  so a single search finds every one of them when it is time to replace them. Nothing in
  `Prototype/` is production art, and **a placeholder never becomes production art by being
  renamed** — a production asset is generated or imported properly, against the art bible. List every placeholder in the
  prototype's `design/prototype-*.md`, so none of them survives by being forgotten.
- Tests mirror the layer they test. A test for `Features/Player/` lives in
  `Tests/PlayMode/Player/`.
- No scripts outside `Code/`. An `Editor/` folder is allowed inside any layer and compiles only in
  the Editor.
- Scene names are PascalCase and unique project-wide; `unity` CLI commands take them by name.

## Naming within folders

| Asset | Pattern | Example |
| --- | --- | --- |
| Prefab | Subject | `PlayerCharacter.prefab` |
| ScriptableObject instance | Subject + type | `Sword_ItemData.asset` |
| Event channel | Payload + `EventChannel` | `IntEventChannel.asset` |
| Sprite sheet | Subject + `_sheet` | `Player_sheet.png` |
| Sliced sprite | Sheet name + index | `Player_sheet_0` |
| Animation clip | Subject + action | `Player_Run.anim` |
| Material | Subject + variant | `Stone_Mossy.mat` |
| URP asset | `URP-` + tier | `URP-Balanced.asset` |
| Prototype placeholder | `PH_` + subject | `PH_Player.prefab` |
