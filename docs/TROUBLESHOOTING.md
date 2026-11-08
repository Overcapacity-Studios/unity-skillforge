# Troubleshooting

Grouped by symptom. Each entry names the check that distinguishes causes, because most of these look
identical from the outside.

---

## Unity: the CLI cannot reach the Editor

**Symptom:** `unity status` lists nothing, or a skill reports "no Editor reachable".

Check in this order — each step is meaningless if the previous one failed:

```bash
unity --version          # 1. is the CLI installed and on PATH
unity auth status        # 2. are you signed in
unity pipeline list      # 3. expect "Pipeline: Installed"
unity status             # 4. expect port, project path, version, PID
```

| Step that fails | Cause and fix |
| --- | --- |
| `unity --version` | Not installed, or not on `PATH`. Reopen your shell; on Linux the binary is at `~/.local/bin/unity` |
| `unity auth status` | `unity auth login`. For CI, set `UNITY_SERVICE_ACCOUNT_ID` and `UNITY_SERVICE_ACCOUNT_SECRET` |
| `unity pipeline list` | Run `unity pipeline install` **with the project open**, then wait for the Editor to finish recompiling |
| `unity status` | The Editor is not running, or it is a different project. See below |

**Several Editors open.** The CLI connects to the first Editor it finds. Target one explicitly:

```bash
unity command --project-path=/path/to/your/project
```

**Unity version too old.** Driving a running Editor needs Unity 6.0 or later; this pack's baseline
is **6.3 LTS (`6000.3.x`)**. Unity 6.0 LTS support ended October 2026.

```bash
unity editors -i         # what is installed
unity install lts        # install the current LTS
```

**The project still has `com.unity.ai.assistant` below 2.13.** Versions 2.13+ fix a conflict between
the CLI and that package. Update it, or remove the package if you are not using the Assistant.

---

## Unity: MCP, and why you probably do not need it

Unity **deprecated** the in-Editor MCP server in `com.unity.ai.assistant`. Its docs say so directly
and point to the Unity CLI instead.

- **Claude Code and Codex both run shell commands**, so they use `unity` directly. No MCP server is
  involved, and that is the faster, cheaper path by Unity's own documentation.
- If an agent genuinely cannot run shell commands, use the CLI's **own** MCP mode — supported, and
  not part of the deprecation:

```bash
unity mcp configure claude      # also: cursor, vscode, windsurf
unity mcp configure --list
```

**Do not** configure the old relay in `~/.unity/relay/` for new work. If you inherit a project set
up that way, migrate: `unity pipeline install` → `unity mcp configure claude`.

**An agent is calling a tool name that does not exist.** That is a bug in how it was prompted, not a
Unity problem. Tool names vary by Unity version and installed packages, and the only honest source is:

```bash
unity list                       # Editor-registered tools, with parameter schemas
unity commands --format json     # the CLI's own command manifest
```

Every skill here is written to run those first. Names like `Unity.ManageScene` and
`Unity_ReadConsole` appear only in Unity's docs for the **deprecated** surface — see
[../references/unity-mcp-tools.md](../references/unity-mcp-tools.md).

---

## Skills are not triggering

**Check which directory your tool actually reads:**

| Tool | Reads | Does **not** read |
| --- | --- | --- |
| Claude Code | `.claude/skills/<name>/SKILL.md` | `.agents/skills/` |
| Codex | `.agents/skills/<name>/SKILL.md` | `.claude/skills/`, `~/.codex/skills` |

```bash
ls .claude/skills | head      # Claude Code
ls .agents/skills | head      # Codex
```

If one is missing, re-run `./scripts/install.sh /path/to/your/game`.

**Nested directories.** A skill at `.claude/skills/core/unity-script/SKILL.md` will not load. Skills
must be a **direct child** of the skills root. That is why everything here is flat with name
prefixes — see [ARCHITECTURE.md](ARCHITECTURE.md).

**Broken frontmatter.** The opening `---` must be the **first line of the file** — no blank line, no
BOM, no comment above it. A skill whose frontmatter fails to parse is dropped **silently**:

```bash
python3 scripts/validate-skills.py
```

**Frontmatter `name` does not match the folder.** Also silently dropped. Same check catches it.

**Too many skills installed.** Claude Code drops descriptions from the listing once it exceeds about
1% of the context window; Codex caps the listing at about 2%. With several packs installed, less
relevant skills stop being matched. Raise Codex's budget:

```toml
[skills]
max_context_tokens = 10000
```

Or disable packs you are not using.

**Invoke one explicitly** to prove the install is fine:
`/unity-skillforge:unity-game-router` in Claude Code, `$` or `/skills` in Codex.

---

## The rules are not being followed

**Symptom:** the agent reads the whole repo, uses legacy `Input`, or skips the design docs.

**On the plugin install path, this is expected.** Claude Code does not load a plugin's `AGENTS.md`
or `CLAUDE.md`. Either start with **"Use the unity-game-router skill"**, which carries the same
rules, or install with `./scripts/install.sh` so `AGENTS.md` loads automatically.

**On Codex:** `AGENTS.md` is read **once at session start** — restart after editing it. And a file
closer to your working directory **overrides** one further up, so a stale `AGENTS.md` in a
subdirectory can quietly win. Codex also takes at most one file per directory, so an
`AGENTS.override.md` means the neighbouring `AGENTS.md` is never read.

**`CLAUDE.md` must contain only `@AGENTS.md`.** If someone pasted rules into it directly, they now
exist in two places and will disagree.

---

## Version and API mismatches

| Symptom | Cause |
| --- | --- |
| A wall of `CS0246` on camera code | **Cinemachine 2.x API against a 3.x package.** `CinemachineVirtualCamera` became `CinemachineCamera`. Check the pin in `Packages/manifest.json` |
| 2D physics code compiles, runs, and does nothing | **The two 2D physics systems.** Legacy `Rigidbody2D` and 2D Physics Core (`Unity.U2D.Physics`, Unity 6000.7+) share no code and never interact. See [../references/unity-versions.md](../references/unity-versions.md) |
| Everything renders magenta | Built-in pipeline materials in a URP project. `assets-import-pipeline` converts them |
| The scene is black on one quality tier only | That tier's URP Asset is unassigned and silently falls back to Built-in |
| Lighting looks wrong and retuning does not help | Colour space is Gamma, not Linear |
| A CLI flag in the docs does not exist | The Unity CLI is **experimental**; `unity --help` is authoritative for your installed version |

---

## Builds

**It built but will not run.** `unity build` succeeding is not the same as the game working. Always:

```bash
unity build run
```

**Black screen on launch.** `Bootstrap` is not the first scene in the build list, so no services were
registered.

**Works in the Editor, broken in the build.** The usual causes, in order:

1. A ScriptableObject is being mutated at runtime. It persists in the Editor and is discarded in a
   build — always a defect.
2. A cross-scene reference set in the Inspector. Those do not survive a build.
3. A quality tier with no URP Asset.
4. Stale lightmaps after a renderer or colour-space change. Re-bake.

**`unity build` reports success but something is wrong.** Check `success` in the JSON envelope and
the `warnings` array, not just the exit code:

```bash
unity build --format json
```

Exit codes: `0` success, `1` error (read stderr), `2` usage error, `130` cancelled.

---

## Approval prompts and permissions

Agents ask before running shell commands. `unity status`, `unity list` and
`unity recompile` are read-only and safe to allow broadly; `unity build` and `unity test` are slow
but harmless; anything that writes to `Assets/` deserves a look first.

In Claude Code, `/permissions` manages the allowlist. The `fewer-permission-prompts` skill can
propose one from your transcripts.

**Unity may also prompt.** With the CLI's MCP mode, the Editor shows a pending connection the first
time a client connects — approve it in **Edit → Project Settings → AI**.

---

## Still stuck

1. `python3 scripts/validate-skills.py` — catches structural problems in the pack itself.
2. `claude plugin validate .` — catches manifest problems.
3. `unity --help` and `unity <command> --help` — authoritative for your installed version, which the
   published docs may lag.
4. Open an issue: <https://github.com/Overcapacity-Studios/unity-skillforge/issues>

When reporting, include your `unity --version`, Unity Editor version, agent and version, and the
exact command with its `--format json` output.
