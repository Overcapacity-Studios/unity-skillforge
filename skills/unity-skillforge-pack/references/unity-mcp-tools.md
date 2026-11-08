# Unity MCP tools — deprecated fallback surface

**Status: deprecated.** Unity's docs state: *"Unity MCP server is deprecated. Use the Unity
command-line interface (CLI) instead."* This file exists only so a skill can recognise the old
surface. For all new work use `references/unity-cli.md`.

Sources (snapshot 2026-11-08):
- <https://docs.unity3d.com/Packages/com.unity.ai.assistant@2.20/manual/integration/unity-mcp-overview.html>
- <https://docs.unity3d.com/Packages/com.unity.ai.assistant@2.20/manual/integration/unity-mcp-get-started.html>
- <https://docs.unity3d.com/Packages/com.unity.ai.assistant@2.20/manual/reference/unity-mcp-reference.html>
- <https://docs.unity.com/en-us/unity-cli/replace-mcp-server-unity-cli>

## Honest limits of this list

Unity has **never published a complete tool list** for the in-Editor MCP server. The docs say the
list is only visible in the Editor at **Edit > Project Settings > AI > Unity MCP Server**, under
"Tools", with enable/disable toggles. The names below are the only ones that appear anywhere in the
documentation — they are examples, not the full set.

| Tool name as written in Unity's docs | Where it appears |
| --- | --- |
| `Unity.ManageScene` | "Verify the connection" — example of a listed tool |
| `Unity.ManageGameObject` | "Verify the connection" — example of a listed tool |
| `Unity_ReadConsole` | Suggested for "Read the Unity console messages and summarize any warnings or errors" |
| `Unity_ManageScript` | Settings reference — the Validation Level dropdown governs this tool |

Note the docs are internally inconsistent about the separator (`Unity.` vs `Unity_`). **Do not
guess, extend or normalise these names.** If you must use MCP, enumerate the tools your client
actually advertises and use those strings verbatim.

## What replaced it

`unity mcp configure <client>` in the Unity CLI. Same protocol, so clients connect unchanged, and
Unity confirms *"The MCP mode in the Unity CLI is not part of the deprecation. It remains fully
supported."* Clients include `claude`, `cursor`, `vscode`, `windsurf`.

## The old architecture, for recognition only

- Unity Editor was the server; the MCP bridge started with the Editor.
- A relay binary installed to `~/.unity/relay/` and was launched by the client with `--mcp`,
  connecting over IPC (named pipes on Windows, Unix sockets on macOS/Linux).
- Relay paths: `~/.unity/relay/relay_mac_arm64.app/Contents/MacOS/relay_mac_arm64`,
  `relay_mac_x64...`, `%USERPROFILE%\.unity\relay\relay_win.exe`, `~/.unity/relay/relay_linux`.
- First connection required manual approval under **Pending Connections** in Project Settings.
- Prerequisites were Unity 6 (6000.0)+ and the `com.unity.ai.assistant` package.

If you find a project configured this way, the migration is:
`unity pipeline install` → `unity mcp configure claude` → `unity mcp configure --list`.
Versions 2.13+ of `com.unity.ai.assistant` fix a conflict between the CLI and the package; update
if the project is on an earlier version.
