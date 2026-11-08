# Using this pack with OpenAI Codex

Everything here is Codex-specific. For the Unity side, start with [INSTALL.md](INSTALL.md).

## Install

Codex does not read `.claude/skills/`. It reads **`.agents/skills/`**.

```bash
git clone https://github.com/Overcapacity-Studios/unity-skillforge.git
cd unity-skillforge
./scripts/install.sh /path/to/your/game
```

That writes `.agents/skills/<33 skills>`, the `.unity-skillforge/` Tier-2 tree, and a root
`AGENTS.md`.

Where Codex looks for skills:

| Scope | Path |
| --- | --- |
| Repo | `.agents/skills` — scanned in every directory from your CWD up to the repo root |
| User | `~/.agents/skills` |
| Admin | `/etc/codex/skills` |
| System | Skills bundled with Codex itself, such as `skill-creator` and `skill-installer` |

**`~/.codex/skills` is not a skills path.** Guides that say otherwise are out of date. The only
`.codex` paths that matter are `~/.codex/config.toml` and a trusted project's `.codex/config.toml`.

To install for every project at once, copy or symlink into `~/.agents/skills/` instead. Codex
follows symlinked skill folders.

## AGENTS.md behaviour

This is where Codex differs most from Claude Code, and it works in our favour: **Codex loads
`AGENTS.md` automatically**, so Tier 0 needs no prompting.

- Codex builds the instruction set **once when it starts**, not per message.
- It reads a global file first: `~/.codex/AGENTS.override.md` if present, otherwise
  `~/.codex/AGENTS.md`.
- Then it walks from the project root **down** to your working directory, taking **at most one file
  per directory** (`AGENTS.override.md` wins over `AGENTS.md`).
- Files are concatenated root-first, so **a file closer to your CWD overrides one further up.**
- There is a size limit: `project_doc_max_bytes`, default **32 KiB**. Once reached, Codex stops
  adding files.

Our `AGENTS.md` is well under 150 lines, so the budget is not a concern unless your repo also has
large ones. If you hit the limit, raise it in `~/.codex/config.toml`:

```toml
project_doc_max_bytes = 65536
```

If your game repo already had an `AGENTS.md`, `install.sh` appended a pointer rather than
overwriting it, so your own rules survive and still load.

## Choosing a model

| Model | Slug | Use it for |
| --- | --- | --- |
| **GPT-6.1 Sol** | `gpt-6.1-sol` | Design, architecture, review — the decisions that are expensive to reverse. Near-flagship capability, 500k default context |
| **GPT-6.1 Terra** | `gpt-6.1-terra` | Implementation, asset production, QA. Fast and efficient. Recent Codex CLI builds only — if it is not offered, update the CLI |
| GPT-6 Astra | `gpt-6-astra` | A genuinely hard architectural problem, or a debugging session that Sol has stalled on |
| GPT-6 Luna | `gpt-6-luna` | High-volume mechanical work; usually below what these skills need |

Map it to the roles in [USAGE.md](USAGE.md): `designer`, `architect` and `reviewer` want **Sol**;
`gameplay-coder`, `asset-producer` and `qa` want **Terra**.

Set a default in `~/.codex/config.toml`:

```toml
model = "gpt-6.1-sol"
```

Switching for one task is cheaper than it looks — a bad architectural decision costs far more than
the model that made it.

## Subagents: what Codex does not have

Codex has **no `agents/` directory**. The six roles in `agents/` are a Claude Code feature.

Use them as prompts instead. `install.sh` copies all six to **`.unity-skillforge/agents/`**, and
each file is self-contained — role, model hint, exact read list, allowed skills, rules and handoff
format. Reference the file rather than pasting it, so the role stays in one place:

| Role | Prompt | Model |
| --- | --- | --- |
| Designer | *"Follow `.unity-skillforge/agents/designer.md`. Spec the grapple hook mechanic."* | Sol |
| Architect | *"Follow `.unity-skillforge/agents/architect.md`. Decide whether this needs a new assembly."* | Sol |
| Gameplay coder | *"Follow `.unity-skillforge/agents/gameplay-coder.md`. Implement the mechanic in `design/mechanic-grapple.md`."* | Terra |
| Asset producer | *"Follow `.unity-skillforge/agents/asset-producer.md`. Produce the enemy sprites."* | Terra |
| QA | *"Follow `.unity-skillforge/agents/qa.md`. Verify the grapple against its acceptance checks."* | Terra |
| Reviewer | *"Follow `.unity-skillforge/agents/reviewer.md`. Review the last change before I commit."* | Sol |

Each role file tells the model to read only `design/STATE.md` and `design/INDEX.md` first, so it
behaves the same way a Claude Code subagent would — minus the isolated context window, which Codex
does not provide here.

The one Codex-native equivalent is `agents/openai.yaml` **inside a skill**, which can declare an
interface and tool dependencies for that skill. This pack does not use it — the roles are
cross-cutting, not per-skill.

## Invoking skills

- `/skills` or `$` in the CLI and IDE (`@` in ChatGPT) lists them explicitly.
- Codex also matches implicitly on the `description`, which is why the descriptions here state when
  a skill does *and does not* apply.
- The initial listing is name + description + file path, capped at about 2% of the context window.
  With 33 skills that is worth knowing; raise it if needed:

```toml
[skills]
max_context_tokens = 10000
```

- Duplicate names are **not** merged — if two packs ship the same skill name, both appear. Our
  prefixes (`core-`, `2d-`, `25d-`, …) exist partly to avoid colliding with Unity's official skills.

Disable a skill you do not want:

```toml
[[skills.config]]
name = "assets-gen-3d-model"
enabled = false
```

Exactly one selector per entry — `path` **or** `name`, not both. A `name` selector disables every
skill with that name.

## MCP servers

Codex uses TOML tables with an **underscore**: `[mcp_servers.<name>]`, not `mcpServers`.

You generally **do not need an MCP server for Unity** — Codex runs shell commands, so the skills
call `unity` directly, which Unity's docs recommend as faster and cheaper.

For Meshy 3D generation (stdio):

```toml
[mcp_servers.meshy]
command = "npx"
args = ["-y", "@meshy-ai/meshy-mcp-server@0.6.9"]
env_vars = ["MESHY_API_KEY"]
```

For a remote server, Codex documents **Streamable HTTP** (not SSE):

```toml
[mcp_servers.example]
url = "https://mcp.example.com/mcp"
bearer_token_env_var = "EXAMPLE_TOKEN"
```

Or from the CLI:

```bash
codex mcp add meshy -- npx -y @meshy-ai/meshy-mcp-server@0.6.9
codex mcp list
```

Keep API keys in environment variables, never inline in a committed file.

If you do want Unity over MCP — only necessary when an agent cannot run shell commands — use the
CLI's own MCP mode, which is supported and not deprecated:

```bash
unity mcp configure vscode
unity mcp configure --list
```

## Unity's official plugin on Codex

Also available, and recommended alongside this pack:

```bash
codex plugin marketplace add Unity-Technologies/unity-agent-plugin
```

Then install it from Codex's in-app `/plugins` browser. An install subcommand is reported by
third-party write-ups but is not in OpenAI's documentation, so use the browser rather than guessing
at a command. Alternatively install the skills directly from
[`Unity-Technologies/skills`](https://github.com/Unity-Technologies/skills).

## Codex-specific gotchas

- **Skills in `.agents/skills`, not `.claude/skills`.** Codex will not find the latter, and the
  symptom is simply that no skill ever triggers.
- **`AGENTS.md` is read once at startup.** Edit it and you must restart the session.
- **A nearer `AGENTS.md` overrides a further one.** A stale `AGENTS.md` in a subdirectory can
  quietly override the root rules.
- **One file per directory.** An `AGENTS.override.md` next to `AGENTS.md` means the latter is never
  read.
- **The 32 KiB budget is cumulative** across all the files Codex concatenates.
- Codex does **not** read `CLAUDE.md`. That file exists only for Claude Code.
