# Assets: providers, pipelines and licensing

This pack is **provider-agnostic**. The skills define the contract — style lock, generate, review,
import with pinned settings, record provenance — and stay neutral about which tool produces the
pixels or polygons.

> **Read this before generating anything commercial.** Licensing differs per provider and per plan,
> and in several cases the output's copyright status is genuinely unsettled. Nothing here is legal
> advice; confirm with the provider's current terms.

## The rule that comes before any provider

**No asset is made without a locked `design/art-bible.md`.** `assets-art-style-lock` owns that file,
and the generation skills stop if its status is 🔴.

This is not bureaucracy. Without a locked style prompt, reference image and palette, each generation
is an independent guess, the set does not match itself, and it has to be redone — which for 3D means
spending credits twice.

## 2D pipeline

```
assets-art-style-lock  →  assets-gen-2d-sprite  →  2d-sprite-import  →  2d-sprite-animation
   (gate)                  (any image model)        (PPU, pivot, filter)   (clips, Animator)
```

| Step | Owner | Key points |
| --- | --- | --- |
| Generate | `assets-gen-2d-sprite` | Style prompt verbatim + subject; transparent background; resolution an exact integer multiple of the art bible's |
| Store master | — | `art-source/generated/` at the repo root, **outside `Assets/`** so Unity never imports it |
| Review | you | Judge against the **reference image**, not the prompt text |
| Slice | `/unity:sprite-editor`, or `scripts/slice-spritesheet.py` for a uniform grid | The script handles the top-left to bottom-left origin flip |
| Import | `2d-sprite-import` | One project-wide PPU; Point filter and no compression for pixel art; mip maps off |
| Atlas | `/unity:manage-sprite-atlas` | Unatlased sprites are one draw call each |

### Image providers

Use whichever model you already have. The skills never name one you have not confirmed is available
in the session.

| Consideration | What to check |
| --- | --- |
| Commercial use | Allowed on your tier? Some providers restrict it to paid plans |
| Training data | Does the provider indemnify you, or disclaim all responsibility? |
| Copyrightability | In the US, purely AI-generated images are generally **not copyrightable**. You may be able to use them and still be unable to stop others from doing so |
| Output ownership | Separate from copyright: the terms may grant you broad use rights regardless |
| Attribution | Some licences require credit in-game |

**Practical consequence:** for a commercial game, generated art is usually safest as a starting
point that a human then edits, and risky as a final shipped asset you intend to defend.

## 3D pipeline

```
assets-art-style-lock  →  assets-gen-3d-model  →  assets-import-pipeline
   (gate)                  (Meshy MCP)             (scale, axis, LODs, URP materials, rig)
```

### Meshy

The documented primary path. Exact tool names are in
[../references/meshy-mcp-tools.md](../references/meshy-mcp-tools.md) — they are snake_case with a
`meshy_` prefix, and inventing a variant is a common failure.

| | |
| --- | --- |
| Server | [`meshy-dev/meshy-mcp-server`](https://github.com/meshy-dev/meshy-mcp-server), MIT |
| Package | `@meshy-ai/meshy-mcp-server` |
| Plan required | **Paid Meshy Pro or higher** |
| Cost | Real credits per generation. `meshy_check_balance` before a batch, and report cost first |
| Asynchronous | Every generation returns a task; poll `meshy_get_task_status` before downloading |
| Commercial use | **Depends on your plan.** Free-tier output is typically not licensed for commercial use. Confirm and record it |

Meshy also publishes an agent skill pack, `meshy-dev/meshy-3d-agent`, which contains **no Unity
import guidance** — that gap is exactly what `assets-import-pipeline` fills.

### Import is not optional

A downloaded `.glb` or `.fbx` dropped into `Assets/` is **not a finished asset**. It will typically
have the wrong scale, possibly the wrong up-axis, and Built-in pipeline materials that render
**magenta** in URP. `assets-import-pipeline` owns scale, axis, LODs, material conversion, texture
types and Avatar retargeting.

## Audio

`assets-audio-sfx` owns the bus layout and loudness targets; `/unity:audio-setup-mixers` and
`/unity:optimize-audio` own the mixer and compression mechanics.

For generated or purchased audio, the same licensing questions apply, plus two of its own:

- **Music with a recognisable melody** carries more risk than sound effects.
- **Streaming platforms** mute videos over audio claims, so check whether the licence covers
  let's-plays and trailers, not just the game binary.

## Asset stores and human artists

Often the right answer, and the skills support it: skip the `assets-gen-*` step and go straight to
`2d-sprite-import` or `assets-import-pipeline`. The art bible still applies — it is what keeps
purchased assets from clashing with each other.

For store assets, record the **licence name and the purchase/seat terms**. Many store licences are
per-seat and non-transferable, which matters the moment a second person joins the project.

## Provenance: the record that lets you ship

`design/art-bible.md` ends with a table that every asset-producing skill appends to:

| Asset / set | Source | Licence | Commercial use confirmed | Date |
| --- | --- | --- | --- | --- |
| Player sprites | (provider) | (licence) | yes / no | YYYY-MM-DD |

Keep it current. The moment you want to sell the game, put it on a store, or bring in a publisher,
this table is the difference between a short conversation and an audit of every file in the repo.

**"Commercial use confirmed" means you checked the provider's terms**, not that you assumed. The
skills are instructed to confirm rather than assume, and to say so when they could not.

## Keys and secrets

Provider API keys live in **environment variables**, never in a committed file, never in a skill,
and never in `design/`. `MESHY_API_KEY` and equivalents belong in your shell profile or your MCP
client's env configuration.
