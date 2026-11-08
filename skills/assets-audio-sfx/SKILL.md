---
name: assets-audio-sfx
description: Add sound effects and music with this project's mixer bus layout, naming and loudness targets, plus import settings that keep memory sane. Use when adding audio or fixing clipping, inconsistent volume or audio memory use. Defer to Unity's audio skills for mixer and optimisation specifics.
metadata:
  version: 0.1.0
---

# Audio and SFX

Paths written as `PACK/` mean wherever this pack's shared files live: `.unity-skillforge/` in a
game repo (`install.sh`), the sibling `unity-skillforge-pack` folder (`npx skills add`), the
plugin's root directory (plugin install), or `skills/unity-skillforge-pack/` in this repo.

## When to use

- Adding sound effects, music or ambience.
- Audio is clipping, inconsistently loud, or drowns out other sounds.
- Audio memory or load time is too high.

## Prefer the official skill

If Unity's official plugin is installed:

- `/unity:audio-setup-mixers` — AudioMixer setup, groups, snapshots and effects.
- `/unity:optimize-audio` — import settings, compression and memory optimisation.

What stays ours: the **bus layout, naming and loudness targets** below. Do not restate Unity's
mixer procedure — link it. See `PACK/references/official-unity-skills.md`.

## Inputs needed

- The audio character line from `design/art-bible.md`.
- What the sound is for, and whether it is 2D (UI, music) or 3D (positional).
- Whether it plays once, loops, or plays many times at once.

## Steps

1. Read `design/STATE.md`, `design/INDEX.md`, then `design/art-bible.md` → audio character.
2. Create the mixer at `Assets/_Project/Audio/Mixers/Main.mixer` with this bus layout. Hand the
   mixer mechanics to `/unity:audio-setup-mixers`; the names and structure are ours:
   | Bus | Parent | Holds |
   | --- | --- | --- |
   | `Master` | — | Everything; the only bus with a limiter |
   | `Music` | `Master` | Music and stingers |
   | `SFX` | `Master` | Gameplay sounds |
   | `UI` | `Master` | Menu and HUD sounds |
   | `Ambience` | `Master` | Loops and beds |
   | `Voice` | `Master` | Dialogue, ducking the others |
   Player-facing volume sliders map to `Music`, `SFX` and `UI` — never to `Master`, so the limiter
   stays in control.
3. Set loudness targets rather than mixing by ear per clip. Normalise source audio to roughly
   **-16 LUFS** for music and ambience, and **-12 to -10 LUFS** peaks for one-shot SFX, then balance
   at the bus. Mixing clip by clip is how a project ends up with one deafening sound.
4. Put a **limiter on `Master` only**. Limiters on individual buses fight each other and pump.
5. Apply import settings by role — this is where audio memory is won or lost
   (`PACK/rules/performance.md`):
   | Role | Load Type | Compression |
   | --- | --- | --- |
   | Short one-shot SFX | Decompress On Load | ADPCM or PCM |
   | Many simultaneous SFX | Compressed In Memory | ADPCM |
   | Music and long ambience | **Streaming** | Vorbis, quality ~70 |
   Streaming a short SFX adds latency for no benefit; Decompress On Load on a music track loads the
   whole uncompressed file into memory.
6. Force mono on 3D positional sounds. A stereo clip played in 3D wastes memory and its spatial
   behaviour is undefined.
7. Set Spatial Blend deliberately: 0 for UI and music, 1 for positional sounds. The default of 0
   means a "3D" sound plays at full volume everywhere, which is a common silent bug.
8. Set rolloff and max distance per sound rather than leaving the default logarithmic curve, which
   drops to near-silence much faster than most games want.
9. Never play audio from many `AudioSource` components created at runtime. Pool them, or route
   one-shots through one audio service registered via `PACK/templates/csharp/ServiceLocator.cs.txt`.
10. Store clips per `PACK/rules/folder-conventions.md`: `Assets/_Project/Audio/{Music,SFX}/`.
11. Verify:
    ```bash
    unity recompile --strict --format json
    ```
    then `qa-playmode-check`: nothing clips on `Master`, relative levels are sensible, positional
    sounds attenuate with distance, and audio memory is within budget.
12. Add a provenance row to `design/art-bible.md` for purchased or generated audio, then
    `design-update-state`.

## Unity CLI commands used

```bash
unity status                              # live Editors: port, project path, version, PID
unity list                                # Editor-registered tools and their parameter schemas
unity commands --format json              # full CLI command manifest
unity recompile --strict --format json    # verify nothing broke
```

Import settings live in the clip's `.meta`. Change them through the Editor tools `unity list`
reports, or an Editor script run with `eval_file`. Use fully-qualified names such as
`UnityEditor.AudioImporter`. See `PACK/references/unity-cli.md`.

## Files to read (exact paths)

| Need | Path |
| --- | --- |
| Project status | `design/STATE.md` |
| Design map | `design/INDEX.md` |
| Audio character and provenance | `design/art-bible.md` |
| Official mixer and optimisation skills | `PACK/references/official-unity-skills.md` |
| Audio folder layout | `PACK/rules/folder-conventions.md` |
| Memory and per-frame budgets | `PACK/rules/performance.md` |
| Service locator template | `PACK/templates/csharp/ServiceLocator.cs.txt` |
| Provider licensing caveats | `PACK/references/asset-licensing.md` |

## Done checklist

- [ ] The mixer uses the bus layout and names above.
- [ ] Player volume sliders map to `Music`, `SFX` and `UI`, not `Master`.
- [ ] Source audio was normalised to a loudness target, not mixed clip by clip.
- [ ] A limiter is on `Master` only.
- [ ] Load Type and compression match each clip's role; music streams, short SFX do not.
- [ ] 3D sounds are mono.
- [ ] Spatial Blend is set deliberately on every source.
- [ ] Rolloff and max distance are set per sound, not left at the default curve.
- [ ] One-shots are pooled or routed through an audio service; no runtime `AudioSource` churn.
- [ ] Verified in play mode: no clipping, sensible balance, correct attenuation, memory in budget.
- [ ] Provenance recorded for purchased or generated audio.

## Common mistakes

- Mapping the player's volume slider to `Master`, which bypasses the limiter and allows clipping.
- Mixing each clip by ear instead of normalising to a target, producing one sound far louder than
  everything else.
- Limiters on several buses, which fight each other and pump audibly.
- Decompress On Load on a music track, loading the whole uncompressed file into memory.
- Streaming a short SFX, adding latency for no benefit.
- A stereo clip used as a 3D positional sound, wasting memory with undefined spatialisation.
- Spatial Blend left at 0 on a sound meant to be positional, so it plays at full volume everywhere.
- The default rolloff curve left in place, so sounds vanish far sooner than intended.
- Creating an `AudioSource` per one-shot at runtime, churning allocations.
- Signing off audio from the Editor without checking the `Master` bus for clipping.
