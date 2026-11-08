# Meshy MCP — real tool names

**Snapshot 2026-11-08.** Source: [`meshy-dev/meshy-mcp-server`](https://github.com/meshy-dev/meshy-mcp-server)
(MIT), npm `@meshy-ai/meshy-mcp-server` 0.6.9. Also published: Meshy's agent skill pack
[`meshy-dev/meshy-3d-agent`](https://github.com/meshy-dev/meshy-3d-agent) (MIT) — instructions only,
and it contains **no Unity import guidance**, which is exactly the gap `assets-import-pipeline` fills.

**Requires a paid Meshy Pro or higher plan.** Check credits before starting a batch.

## Install

```bash
npm install -g @meshy-ai/meshy-mcp-server@0.6.9
```

Claude Code: add it as an MCP server (`.mcp.json` or `claude mcp add`). Codex: a
`[mcp_servers.meshy]` table in `~/.codex/config.toml` with `command` and `args`. Supply the API key
through an environment variable — never inline it in a committed file.

## Tool names — use these verbatim

All names are snake_case with a `meshy_` prefix. **Do not invent variants.** Confirm availability by
listing the server's tools in your client before use; this list is a snapshot.

Generation:
`meshy_text_to_3d`, `meshy_text_to_3d_refine`, `meshy_image_to_3d`, `meshy_multi_image_to_3d`,
`meshy_text_to_image`, `meshy_image_to_image`, `meshy_creative_lab`

Mesh and texture operations:
`meshy_retexture`, `meshy_remesh`, `meshy_uv_unwrap`, `meshy_convert`, `meshy_resize`,
`meshy_auto_split`

Rigging and animation:
`meshy_rig`, `meshy_animate`, `meshy_text_to_motion`, `meshy_list_animations`

Retrieval and account:
`meshy_download_model`, `meshy_get_task_status`, `meshy_cancel_task`, `meshy_list_tasks`,
`meshy_list_models`, `meshy_list_usage`, `meshy_check_balance`, `meshy_output`

3D printing (not used by this pack):
`meshy_analyze_printability`, `meshy_repair_printability`, `meshy_process_multicolor`,
`meshy_send_to_slicer`

## Working rules for this pack

1. **Style lock first.** Never call a generation tool without quoting `design/art-bible.md`. See
   `skills/assets-art-style-lock/SKILL.md`.
2. **Generation is asynchronous.** `meshy_text_to_3d` and friends return a task; poll
   `meshy_get_task_status` before `meshy_download_model`. Do not assume a result is ready.
3. **Budget before batching.** Call `meshy_check_balance` and tell the user the cost before
   generating a set. Generation spends real credits.
4. **Download, then hand off.** `meshy_download_model` writes a file; importing it correctly is
   `assets-import-pipeline`'s job (scale, axis, LODs, URP materials, rig remap). Never drop a raw
   download into `Assets/` and call it done.
5. **Rig and animate only what needs it.** `meshy_rig` then `meshy_animate` adds cost and
   constrains the skeleton; for static props, stop at the mesh.
6. **Licensing is the user's call.** Commercial-use terms depend on their Meshy plan. Record what
   they confirmed in `design/tech-decisions.md`; see `docs/ASSETS.md`.
