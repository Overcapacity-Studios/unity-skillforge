# Unity CLI — the Editor bridge

**Snapshot taken 2026-11-08 from Unity's official docs.** The Unity CLI is labelled *experimental*
and its own docs state that `unity --help` is authoritative for the installed version. Treat this
file as a map, not as truth: discover the live surface at runtime (see "Discovery" below).

Primary sources:
- <https://docs.unity.com/en-us/unity-cli>
- <https://docs.unity.com/en-us/unity-cli/replace-mcp-server-unity-cli>
- <https://docs.unity.com/en-us/unity-cli/unity-pipeline/unity-pipeline-package>
- <https://docs.unity.com/en-us/unity-cli/reference/output-formats>

## Why the CLI and not MCP

Unity's docs carry this banner on the `com.unity.ai.assistant` MCP pages:

> Unity MCP server is deprecated. Use the Unity command-line interface (CLI) instead.

Scope of the deprecation:

| Setup | Deprecated |
| --- | --- |
| In-Editor MCP server in `com.unity.ai.assistant` | **Yes** |
| `unity mcp` / `unity command` in the Unity CLI | No — "remains fully supported" |
| A third-party MCP package installed from GitHub | No |

Unity also states the direct commands are cheaper: `unity command` and `unity eval` are *"faster and
use fewer tokens than MCP. Use these commands if your agent can run shell commands."* MCP mode
exists for agents that cannot run arbitrary shell commands.

**Licensing:** *"The CLI is free and separate from Unity AI. Installing the CLI doesn't require a
Unity AI subscription."* A Unity Cloud link and a Unity AI plan are **not** prerequisites for the
bridge. `unity auth login` is still required before `unity pipeline install`.

## Install and authenticate

```bash
curl -fsSL https://unity.com/install.sh | bash   # macOS / Linux
brew install --cask unity-cli                    # macOS / Linux (Homebrew)
winget install Unity.CLI                         # Windows
unity --version                                  # verify; reopen the shell if not found
unity auth login                                 # browser sign-in, session is stored
unity auth status
```

Linux installs to `~/.local/bin/unity`; override with `UNITY_CLI_HOME` (binary lands in
`<UNITY_CLI_HOME>/bin`). Unity Hub keeps the CLI updated automatically and that cannot be disabled.

CI / build agents sign in with a service account instead:
`UNITY_SERVICE_ACCOUNT_ID`, `UNITY_SERVICE_ACCOUNT_SECRET`.

## Enable Editor control — the Pipeline package

Controlling a running Editor requires the **Unity Pipeline package** (`com.unity.pipeline`), which
exposes a **localhost-only** HTTP API. Unity 6.0 or later is required to drive a running Editor.

```bash
unity auth login
unity pipeline install     # run with the project open; then let the Editor recompile
unity pipeline list        # expect "Pipeline: Installed"
unity status               # confirm the CLI can reach the Editor
```

`unity pipeline list` in Unity's own screenshot reports the server on port 7800; that is an example,
not a documented default. Do not hardcode a port.

If several Editors are open, target one:
`unity command --project-path=<path>`.

## Discovery — do this before calling anything

```bash
unity status                      # live Editors: port, project path, version, PID
unity list                        # every tool a connected Editor registers, WITH parameter schemas
unity commands --format json      # machine-readable manifest of all CLI commands and subcommands
```

`unity list` and `unity commands` are the only honest source of tool names for the project in front
of you. **Never invoke a name you have not seen in that output.** Registered tools differ by Unity
version and by which packages the project has installed.

## Commands that matter to us

| Command | Use |
| --- | --- |
| `unity command` (alias `cmd`) | Forward a command to a connected Editor, or list what it exposes |
| `unity commands --format json` | Manifest of every command/subcommand, for agents and tooling |
| `unity list` | Every Editor-registered tool plus its parameter schema |
| `unity status` | Live state of connected Editors |
| `unity recompile [--strict]` | Recompile a running Editor's scripts and report compile errors without a full build; `--strict` also fails on warnings |
| `unity test [--affected]` | Run Edit Mode and Play Mode tests through the Editor test runner, writing an NUnit report |
| `unity watch test` | Re-run `unity test --affected` on file change |
| `unity build` | Batch-mode build with CI-friendly flags; `--list-targets`, `--list-profiles`, `--create-profile <target>` |
| `unity build run` | Launch the most recent recorded build |
| `unity run [--command] [--log-file <path>]` | Batch-mode run, or a registered Editor command headless |
| `unity job` | Manage detached Editor command jobs |
| `unity open <path> [--wait]` | Open a project (`--wait` is macOS/Linux only; exits 2 on Windows) |
| `unity projects` (alias `p`) | `list`, `create`, `clone`, `open`, `link`, `pin`, `close` |
| `unity assets import\|export\|inspect` | `.unitypackage` handling |
| `unity install <version>` | e.g. `unity install 6000.3.7f1`; aliases `latest`, `lts`, `default`, `6`, `6.3` |
| `unity editors [-i\|-r]` | Installed / available Editors |
| `unity pipeline` (alias `pipe`) | Install, upgrade, inspect the Pipeline package |
| `unity mcp configure <client>` | MCP fallback: clients include `claude`, `cursor`, `vscode`, `windsurf`; `--list` shows status |
| `unity skill install <agent-name>` | Install Unity's own agent skills |

## Running C# in the Editor — `script eval`

The Pipeline package exposes `eval` / `eval_file`. **`script eval` compiles a statement block, not a
file.** Therefore:

- No `using` directives. Use fully-qualified type names.
- `return` the value you want to read; it arrives at `data.result.result`.

| Compile error | Cause | Fix |
| --- | --- | --- |
| `CS0210` | A `using` directive, read as a resource-disposal statement | Remove it and qualify types |
| `CS0246` / `CS0103` | An unqualified type such as `Rigidbody2D` | Use `UnityEngine.Rigidbody2D` |
| `CS0104` | A bare `Object`, ambiguous with `object` | Use `UnityEngine.Object` |

Prefer `eval_file` with a checked-in editor script over a long inline block: it is reviewable,
re-runnable, and does not fight the statement-block restriction.

## Output, parsing and exit codes

- Interactive output is human-readable; **piped output defaults to TSV**.
- `--format json` returns an envelope: `{ success, command, data, errors, warnings }`.
- `ndjson` emits one JSON object per line. `json`, `tsv` and `ndjson` never emit colour.
- Errors go to stderr, keeping stdout clean for data. In JSON mode: `{"error": "..."}` on stderr.
- `UNITY_FORMAT` sets the default format; an explicit flag beats the environment variable.

| Exit code | Meaning |
| --- | --- |
| `0` | Success |
| `1` | General error — read stderr |
| `2` | Usage error (bad flag, missing argument) |
| `130` | Cancelled by the user |

Always pass `--format json` when a skill needs to branch on a result, and check `success` as well as
the exit code.

## MCP fallback

For an agent that cannot run shell commands, the CLI's own MCP mode — not the deprecated in-Editor
server — is the supported route:

```bash
unity mcp configure claude
unity mcp configure --list
```

It speaks the same protocol, so clients connect unchanged. See
`references/unity-mcp-tools.md` for the little that is documented about tool names.
