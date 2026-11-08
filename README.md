# unity-skillforge

Agent skills, subagents, rules and templates that help AI coding agents build Unity games in 2D,
2.5D and 3D — code, scenes and generated assets. Works with **Claude Code** and **OpenAI Codex**
from one source of truth.

Targets **Unity 6.3 LTS (`6000.3.x`)**, URP and the new Input System. The Editor bridge is the
**Unity CLI** plus the Unity Pipeline package — Unity deprecated the in-Editor MCP server.

This repo is *how* we build. Each game repo keeps a `design/` folder describing *what* is being
built.

Full documentation lands in `docs/`. See `AGENTS.md` for the rules agents load first.
