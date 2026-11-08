# Install

Written for someone who has not seen this repo before. Work top to bottom.

## 1. Prerequisites

| Requirement | Why | Check |
| --- | --- | --- |
| **Unity 6.3 LTS (`6000.3.x`)** or later | Unity 6.0 LTS support ended October 2026 | `unity editors -i` |
| **URP** project | Every skill assumes URP; Built-in RP is not supported | Project Settings → Graphics |
| **New Input System** | Legacy input is banned by the rules | Project Settings → Player |
| **Unity CLI** | The Editor bridge | `unity --version` |
| **Unity Pipeline package** | Lets the CLI drive a running Editor | `unity pipeline list` |
| **Python 3.9+** | `validate-skills.py`, `slice-spritesheet.py` | `python3 --version` |
| **Claude Code** or **OpenAI Codex** | The agent | `claude --version` / `codex --version` |

**You do not need a Unity AI subscription or a Unity Cloud–linked project.** Unity's docs state:
*"The CLI is free and separate from Unity AI. Installing the CLI doesn't require a Unity AI
subscription."* Node.js is not required either — the scripts here are Python and Bash.

## 2. Install the Unity CLI

```bash
curl -fsSL https://unity.com/install.sh | bash     # macOS / Linux
brew install --cask unity-cli                      # macOS / Linux via Homebrew
winget install Unity.CLI                           # Windows
```

Then verify and sign in:

```bash
unity --version          # if "command not found", reopen your shell or add the install dir to PATH
unity auth login         # opens a browser; the session is stored
unity auth status
```

On Linux the binary lands at `~/.local/bin/unity`; set `UNITY_CLI_HOME` before running the script to
put it elsewhere. Unity Hub keeps the CLI updated automatically and that cannot be disabled.

For CI, skip the interactive login and set `UNITY_SERVICE_ACCOUNT_ID` and
`UNITY_SERVICE_ACCOUNT_SECRET` instead.

## 3. Let the CLI drive your Editor

Open your Unity project, then:

```bash
unity pipeline install     # installs com.unity.pipeline; wait for the Editor to recompile
unity pipeline list        # expect "Pipeline: Installed"
unity status               # should list your Editor: port, project path, version, PID
```

`unity status` listing your Editor is the real test. If it does not, go to
[TROUBLESHOOTING.md](TROUBLESHOOTING.md).

The Pipeline package exposes a **localhost-only** HTTP API. Nothing is exposed to the network.

## 4. Install the pack

Pick **one** of the two paths.

### Path A — Claude Code plugin (fastest)

```
/plugin install unity-skillforge --marketplace Overcapacity-Studios/unity-skillforge
```

On Claude Code older than 2.1.275, or to pin a version:

```
/plugin marketplace add Overcapacity-Studios/unity-skillforge
/plugin install unity-skillforge@unity-skillforge
```

Verify by typing `/unity-skillforge:` — the skills appear in the slash menu.

**Important limitation of this path:** Claude Code does not load a plugin's `AGENTS.md` or
`CLAUDE.md`. The `unity-game-router` skill carries the same hard rules and routing table, so start a
session with **"Use the unity-game-router skill"**. If you want the rules loaded automatically, also
run the installer from Path B with `--no-agents-md` omitted, or use Path B alone.

Auto-update is **off by default** for third-party marketplaces. Refresh with:

```
/plugin marketplace update unity-skillforge
```

### Path B — install into your game repo (works for Codex, and for both tools at once)

```bash
git clone https://github.com/Overcapacity-Studios/unity-skillforge.git
cd unity-skillforge
./scripts/install.sh /path/to/your/game --dry-run   # preview first
./scripts/install.sh /path/to/your/game
```

Windows PowerShell:

```powershell
.\scripts\install.ps1 C:\dev\MyGame
```

This writes:

```
your-game/
  .claude/skills/<33 skills>      # Claude Code
  .claude/agents/<6 agents>       # Claude Code subagents
  .agents/skills/<33 skills>      # Codex  (NOT .codex/skills)
  .unity-skillforge/              # the read-by-path tier: references, rules, templates, scripts, docs
  AGENTS.md                       # Tier 0 rules (appended to, never overwritten)
  CLAUDE.md                       # contains only @AGENTS.md
  design/STATE.md, design/INDEX.md
```

`.unity-skillforge/` is a **fixed path on purpose**: every skill cites `PACK/references/...`, and
that is the only location that resolves for both tools. Claude Code has `${CLAUDE_SKILL_DIR}`;
Codex documents no equivalent.

The installer never overwrites an existing `AGENTS.md`, `CLAUDE.md` or `design/` folder — it appends
a pointer instead. Re-running it is safe and refreshes the skills.

Use `--symlink` instead of copying if you want the game repo to track your local clone. On Windows
that needs Developer Mode or an elevated shell, which is why copying is the default.

## 5. Connect your agent to Unity

**Claude Code and Codex can both run shell commands, so no MCP server is needed** — the skills call
`unity` directly, which Unity's own docs recommend as faster and cheaper in tokens than MCP.

Only if your agent cannot run shell commands, configure the CLI's MCP mode (this is the supported
one; the in-Editor MCP server in `com.unity.ai.assistant` is deprecated):

```bash
unity mcp configure claude      # also: cursor, vscode, windsurf
unity mcp configure --list
```

## 6. Verify the whole thing

```bash
unity status                              # Editor reachable
unity list                                # the tools your Editor actually registers
unity recompile --strict --format json    # expect "success": true
```

Then ask your agent: *"Read design/STATE.md and tell me what this project is."* It should read
exactly two files and report the project state. If it starts reading the whole repo, the rules are
not loaded — see [TROUBLESHOOTING.md](TROUBLESHOOTING.md).

## 7. Strongly recommended: Unity's official plugin

Complementary, not overlapping. Install both.

```
/plugin marketplace add Unity-Technologies/unity-agent-plugin
/plugin install unity@unity-agent-plugin
```

It ships 36 skills covering tilemaps, sprite atlases, NavMesh, Cinemachine recipes, URP
post-processing, builds and monetisation. Where our skills touch the same ground they defer to it by
name. See [../references/official-unity-skills.md](../references/official-unity-skills.md) for the
full map and other packs worth adding.

## 8. Optional: working on the pack itself

```bash
python3 scripts/validate-skills.py    # structural checks; must exit 0
claude plugin validate .              # manifest checks
```

See [CONTRIBUTING.md](CONTRIBUTING.md).
