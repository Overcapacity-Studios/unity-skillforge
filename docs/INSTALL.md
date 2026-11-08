# Install

Written for someone who has not seen this repo before. Work top to bottom.

**Order matters.** Do these sections in order: Unity first (§1–3), then the pack (§4), then verify
(§6). The README's quickstart is the same sequence, compressed.

## 0. If you do not have a Unity project yet

Create one first; the pack works on an existing project, it does not create one.

In **Unity Hub** → New project → pick a **Universal 3D** (or **Universal 2D**) template on **Unity
6.3 LTS or later**. That gives you URP configured. Then set Project Settings → Player → **Active
Input Handling** to **Input System Package (New)**, which prompts a restart.

Once the Unity CLI is installed (§2) you can also do this from the command line:

```bash
unity install lts                 # install the current LTS Editor
unity projects create --help      # see the template options available to you
```

### Already have a Unity project?

That is the expected case, and nothing here overwrites your work — see §4 for exactly what gets
written. Two strict rules are worth knowing up front:

- **URP only.** Built-in RP is unsupported by these skills. If your project is Built-in RP, Unity's
  own `/unity:migrate-birp-to-urp` skill owns that migration; do it before relying on the lighting
  and rendering skills here.
- **New Input System only.** `UnityEngine.Input`, `Input.GetKey` and `Input.GetAxis` are banned by
  `rules/csharp-style.md`.

Both rules govern **new** code the agent writes. It will not refactor your existing scripts unless
you ask. If a third-party package forces Active Input Handling to "Both", record that exception in
`design/tech-decisions.md` and carry on.

## 1. Prerequisites

Have these **before** you start. Everything else in this document gets installed as you go.

| Requirement | Why | Check |
| --- | --- | --- |
| **Python 3.9+** | `validate-skills.py`, `slice-spritesheet.py` | `python3 --version` |
| **Claude Code** or **OpenAI Codex** | The agent that runs the skills | `claude --version` / `codex --version` |
| **Unity 6.3 LTS (`6000.3.x`)** or later | Unity 6.0 LTS support ended October 2026 | Unity Hub, or `unity editors -i` after §2 |
| **A Unity project**, URP, new Input System | Every skill assumes URP; legacy input is banned by the rules | see §0 |

You do **not** need: a Unity AI subscription, a Unity Cloud–linked project, or Node.js. Unity's docs
state *"The CLI is free and separate from Unity AI. Installing the CLI doesn't require a Unity AI
subscription."* The scripts here are Python and Bash.

The Unity CLI and the Pipeline package are **installed by §2 and §3** — you cannot check them yet.

## 2. Install the Unity CLI

**Pick one** of these:

```bash
curl -fsSL https://unity.com/install.sh | bash     # macOS / Linux
brew install --cask unity-cli                      # macOS, or Linux with Homebrew 6.0+
winget install Unity.CLI                           # Windows
```

The CLI is currently **beta** (`1.0.0-beta.x`) and Unity labels it experimental. Commands and flags
can change between versions, so `unity --help` and `unity <command> --help` are authoritative for
your install — more so than any document, including this one.

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

### Which path?

| | Path A — plugin | Path B — installer | Path C — `npx skills` |
| --- | --- | --- | --- |
| Works with | Claude Code only | **Claude Code and Codex** | Claude Code, Codex and ~70 other agents |
| Ships the 33 skills | yes | yes | yes |
| Ships the shared rules/templates | yes (plugin root) | yes (`.unity-skillforge/`) | yes — **as the `unity-skillforge-pack` skill** |
| Ships the 6 subagents | yes | yes | no |
| **Loads the rules automatically** | **no** | **yes**, via `AGENTS.md` | **no** |
| Creates `design/STATE.md` | no | yes (never overwrites an existing one) | no |
| Lets you take just one skill | no | no | **yes** |
| Updates | `/plugin marketplace update` | re-run the script | `npx skills update` |

**Use Path B unless you have a reason not to.** It is the only route that also gives you the
always-on rules and the `design/` contract. Use **Path C** when you want a couple of specific
skills rather than the whole pack, or when your agent is neither Claude Code nor Codex.

On Paths A and C the rules are not loaded automatically, so open each session with **"Use the
unity-game-router skill"** — it carries the same hard rules and routing table. Running more than one
path is fine.

### Path A — Claude Code plugin

> If you already have this folder on disk, Path B needs no clone at all — just
> `./scripts/install.sh /path/to/your/game`.

```
/plugin install unity-skillforge --marketplace Overcapacity-Studios/unity-skillforge
```

On Claude Code older than 2.1.275, or to pin a version:

```
/plugin marketplace add Overcapacity-Studios/unity-skillforge
/plugin install unity-skillforge@unity-skillforge
```

Verify it: type `/unity-skillforge:` (with the trailing colon, and do **not** press Enter) and the
slash menu should filter to this pack's skills — `unity-game-router`, `core-unity-script` and the
rest. `/plugin` also lists `unity-skillforge` as installed and enabled.

**Two limitations of this path.** Both have the same cause: a plugin ships skills, and nothing else.

1. **The rules do not load by themselves.** Claude Code does not read a plugin's `AGENTS.md` or
   `CLAUDE.md`. The `unity-game-router` skill carries the same hard rules and routing table, so
   open each session with **"Use the unity-game-router skill"**.
2. **There is no `design/` folder.** The skills read `design/STATE.md` on every task. The router
   handles its absence — it routes you to `design-write-gdd`, which creates it — so this is a first
   prompt, not a blocker. Starting with the router sentence above covers both points.

To remove both limitations, run Path B as well.

Auto-update is **off by default** for third-party marketplaces. Refresh with:

```
/plugin marketplace update unity-skillforge
```

### Path B — install into your game repo (works for Codex, and for both tools at once)

**If you already have this folder on disk** — you cloned it earlier, a colleague sent it, or you are
reading this file from inside it — skip the clone entirely:

```bash
cd /path/to/unity-skillforge          # wherever this folder lives
./scripts/install.sh /path/to/your/game --dry-run   # preview first
./scripts/install.sh /path/to/your/game
```

Otherwise clone it first (needs the repo to be published):

```bash
git clone https://github.com/Overcapacity-Studios/unity-skillforge.git
cd unity-skillforge
./scripts/install.sh /path/to/your/game
```

Windows PowerShell — note these are **PowerShell switches** (`-Symlink`), not the Bash long flags:

```powershell
.\scripts\install.ps1 C:\dev\MyGame
.\scripts\install.ps1 C:\dev\MyGame -DryRun     # preview, change nothing
.\scripts\install.ps1 C:\dev\MyGame -Symlink    # needs Developer Mode or an elevated shell
```

| Bash | PowerShell | Does |
| --- | --- | --- |
| `--dry-run` | `-DryRun` | Print what would happen, change nothing |
| `--symlink` | `-Symlink` | Link instead of copy, so the game repo tracks your clone |
| `--copy` | *(default)* | Copy the files in |
| `--no-agents-md` | `-NoAgentsMd` | Skip writing `AGENTS.md` and `CLAUDE.md` |

This writes:

```
your-game/
  .claude/skills/<33 skills>      # Claude Code
  .claude/agents/<6 agents>       # Claude Code subagents
  .agents/skills/<33 skills>      # Codex  (NOT .codex/skills)
  .unity-skillforge/              # the read-by-path tier: references, rules, templates, scripts,
                                  # docs, and the six agent role files (Codex reads them from here)
  .unity-skillforge/AGENTS.md     # the rules file your AGENTS.md points at
  AGENTS.md                       # Tier 0 rules (appended to, never overwritten)
  CLAUDE.md                       # contains only @AGENTS.md
  design/STATE.md, design/INDEX.md # each created only if absent; yours are never overwritten
```

Two terms used above, since the installer prints them at you:

- **Tier 0** — the rules that load on *every* task: `AGENTS.md`. Deliberately short (under 150
  lines) because you pay for it constantly.
- **Tier 1** — a single skill's `SKILL.md`, loaded only when your task matches it. Capped at 200
  lines.
- **Tier 2** — `references/`, `rules/`, `templates/`: read **only** when a skill names the exact
  file. This is how 33 skills and a few thousand lines of reference cost nearly nothing until used.

`.unity-skillforge/` is a **fixed path on purpose**: every skill refers to its own files as
`PACK/references/...`, and a fixed location is the only thing that resolves for both tools. Claude
Code offers `${CLAUDE_SKILL_DIR}`; Codex documents no equivalent.

The installer never overwrites an existing `AGENTS.md`, `CLAUDE.md` or `design/` folder — it appends
a pointer instead. Re-running it is safe and refreshes the skills.

Use `--symlink` instead of copying if you want the game repo to track your local clone. On Windows
that needs Developer Mode or an elevated shell, which is why copying is the default.

### Should you commit all this?

The installer copies the skills **twice** (once per tool) plus the Tier 2 tree — about 115 files in
total. Both answers are defensible:

- **Commit it** if your team shares one agent setup. Everyone gets the same skills and rules at the
  same version with no setup step, which is usually what you want on a team.
- **Ignore it** if you would rather each person install their own, or you dislike the diff noise.
  Add to your game repo's `.gitignore`:

  ```gitignore
  .claude/skills/
  .agents/skills/
  .unity-skillforge/
  ```

  Keep `AGENTS.md`, `CLAUDE.md` and **`design/` committed either way** — `design/` is your game's
  own documentation, not part of the pack.

### Uninstalling

```bash
./scripts/uninstall.sh /path/to/your/game            # asks first; --yes to skip, --dry-run to preview
```

It removes only the skills and agents this pack owns, plus `.unity-skillforge/`. A skill you wrote
yourself in the same folder survives, and **`design/` and `Assets/` are never touched.** It then
tells you what it deliberately left behind, such as the section it appended to your `AGENTS.md`.

> **Only using Claude Code?** You can ignore every mention of `.agents/skills` and Codex below —
> the installer writes it, it costs you nothing, and it is simply unused. Codex-specific setup lives
> in [CODEX.md](CODEX.md).

### Path C — `npx skills`

Works with any agent the [`skills` CLI](https://github.com/vercel-labs/skills) supports, which is
most of them.

```bash
npx skills add Overcapacity-Studios/unity-skillforge -l       # list what is in the repo
npx skills add Overcapacity-Studios/unity-skillforge --all    # install everything
```

To pick and choose — note that `-s` and `-a` must be **repeated**, not comma-joined:

```bash
npx skills add Overcapacity-Studios/unity-skillforge \
  -s unity-skillforge-pack -s unity-game-router -s 25d-sorting-and-depth \
  -a claude-code -a codex -y
```

**Always include `unity-skillforge-pack`**, or use `--all`. The CLI copies each skill's own folder
and nothing else, so that package is how the shared rules, references and templates travel. Without
it, every `PACK/...` path in the other skills points at nothing. The skills resolve it as a sibling
folder next to themselves.

Useful flags: `--copy` to copy rather than symlink, `-g` for a user-level install instead of this
project, `--json` for machine-readable output. It writes a `skills-lock.json`, and
`npx skills update` upgrades them later.

What this path does **not** give you: the six subagents, the always-on `AGENTS.md`, or
`design/STATE.md`. Open each session with *"Use the unity-game-router skill"*, which will create the
`design/` folder on its first run.

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

First, an offline check that needs no Editor and no agent — count what landed:

```bash
ls -1 .claude/skills | wc -l     # expect 33
ls -1 .agents/skills | wc -l     # expect 33  (Codex; harmless if you only use Claude Code)
ls -1 .claude/agents | wc -l     # expect 6
ls -1 .unity-skillforge          # expect: AGENTS.md docs references rules scripts templates
```

If those numbers are right, the pack is installed correctly and anything else that goes wrong is
Unity-side or agent-side.

Then the Unity side:

```bash
unity status                              # Editor reachable
unity list                                # the tools your Editor actually registers
unity recompile --strict --format json    # expect "success": true
```

Then check the pack itself, using the prompt that matches how you installed:

- **Path B** (or both paths): *"Read design/STATE.md and design/INDEX.md and tell me what this
  project is."* On a fresh install those are **unfilled templates**, so the correct answer is
  roughly *"a blank project template — no game defined yet, dimension not chosen"*. That is a pass.
  A failure looks like the agent reading the whole repo, or dozens of files, instead of those two —
  which means the rules are not loaded; see [TROUBLESHOOTING.md](TROUBLESHOOTING.md).
- **Path A only**, where `design/` does not exist yet: *"Use the unity-game-router skill."* It should
  tell you there is no `design/` folder and offer to create one. That is the correct response, not
  an error.

Either way, your real first task is the same prompt:

> **"Use the unity-game-router skill. I want to build \<your game, in one sentence\>."**

For what happens next, read a walkthrough:
[2D platformer](../examples/2d-platformer-walkthrough.md) or
[3D third-person](../examples/3d-third-person-walkthrough.md).

## 6b. Costs

The pack and the Unity CLI are free. The one paid dependency is **optional**: the
`assets-gen-3d-model` skill uses Meshy, which needs a **paid Meshy Pro or higher** plan and spends
credits per generation — it reports the cost before spending. Everything else, including all 2D
work, QA and builds, needs nothing beyond your agent subscription. Details and the licensing
caveats that matter for a commercial game: [ASSETS.md](ASSETS.md).

## 7. Strongly recommended: Unity's official plugin

Complementary, not overlapping. Install both.

```
/plugin marketplace add Unity-Technologies/unity-agent-plugin
/plugin install unity@unity-agent-plugin
```

It ships 36 skills covering tilemaps, sprite atlases, NavMesh, Cinemachine recipes, URP
post-processing, builds and monetisation. Where our skills touch the same ground they defer to it by
name. See [../references/official-unity-skills.md](../skills/unity-skillforge-pack/references/official-unity-skills.md) for the
full map and other packs worth adding.

## 8. Optional: working on the pack itself

```bash
python3 scripts/validate-skills.py    # structural checks; must exit 0
claude plugin validate .              # manifest checks
```

`claude plugin validate` reports one expected warning — *"CLAUDE.md at the plugin root is not
loaded as project context."* That is correct and deliberate: `CLAUDE.md` serves the Path B install,
and on the plugin path the `unity-game-router` skill carries the rules instead. You did not break
anything. See [ARCHITECTURE.md](ARCHITECTURE.md).

See [CONTRIBUTING.md](CONTRIBUTING.md).
