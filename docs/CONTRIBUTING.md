# Contributing

## Before anything else

```bash
python3 scripts/validate-skills.py    # must exit 0
claude plugin validate .              # must pass
shellcheck -S warning scripts/*.sh    # must be clean
```

CI (`.github/workflows/validate.yml`) runs all three on every push and pull request, plus manifest
checks, an end-to-end install/uninstall into a scratch repo, and the sprite-slicer's grid maths. The
validator is stdlib-only so it works on a clean machine.

Shell scripts must run on **bash 3.2**, which is what macOS ships. No `mapfile`, no associative
arrays, no `${var,,}`.

## The constraints you cannot change

These come from how Claude Code and Codex actually load files, not from taste:

1. **Skills are flat.** `skills/<name>/SKILL.md`, direct children only. Nesting is not a supported
   layout in either tool, and a nested skill loads nowhere.
2. **Frontmatter is `name`, `description` and `metadata` only.** Outside Claude Code, any other key
   is a hard error. `name` must equal the folder name, or the skill is dropped **silently**.
3. **The opening `---` is the first line of the file.** No blank line, no BOM.
4. **No angle brackets in a description**, and the root `README.md` stays above 40 words — both are
   Claude Code plugin-directory scan rules.
5. **Limits:** `SKILL.md` ≤ 200 lines, `AGENTS.md` ≤ 150 lines, `description` ≤ 300 characters.
6. **Routing tables stay in parity.** `AGENTS.md` lists every skill; `unity-game-router` lists every
   skill but itself.

[ARCHITECTURE.md](ARCHITECTURE.md) explains why each of these exists.

## Adding a skill

1. **Check it is not already covered.** Read
   [../references/official-unity-skills.md](../references/official-unity-skills.md) first. If
   Unity's official plugin or another maintained pack covers the topic well, the right contribution
   is a link, not a skill. Duplicating something Unity maintains means maintaining a copy that
   drifts.
2. **Name it with the right prefix:** `core-`, `2d-`, `25d-`, `3d-`, `assets-`, `qa-`, `design-`.
   Prefixes group the skill and keep it from colliding with other packs' names.
3. **Create `skills/<name>/SKILL.md`** with these sections, in this order — the validator enforces
   both presence and order:

   **When to use · Inputs needed · Steps · Unity CLI commands used · Files to read (exact paths) ·
   Done checklist · Common mistakes**

   Add `## Prefer the official skill` right after "When to use" if the topic overlaps Unity's.
4. **Write the description to say when the skill does *and does not* apply.** It sits in context
   permanently, for every user, forever. That is the 300-character budget's whole justification.
5. **Cite Tier 2 files as `PACK/...`** — `PACK/rules/csharp-style.md`,
   `PACK/templates/csharp/StateMachine.cs.txt`. The validator checks every one resolves. Paths under
   `design/`, `Assets/` or `art-source/` belong to a game project and are not checked.
6. **Add a row to the routing table in both `AGENTS.md` and
   `skills/unity-game-router/SKILL.md`.** The validator fails if they drift.
7. **Update the counts** in `README.md` and `docs/ARCHITECTURE.md` if the group size changed.

## Writing style for skills

- **Steps are numbered and imperative.** No essays.
- **Copy a template or run a script before generating code.** If you find yourself writing 40 lines
  of C# into a skill, it belongs in `templates/csharp/` instead.
- **Never invent a Unity tool name.** The registered set varies by version and installed packages.
  Every Editor-touching skill opens by running `unity status`, `unity list` and
  `unity commands --format json`, and uses only names seen in that output.
- **"Common mistakes" is the highest-value section.** Write the failure that is silent — the thing
  that compiles, runs, and quietly does the wrong thing. Those are what a checklist cannot catch.
- **Pin things.** Versions, import settings, PPU. No "latest", no setting left at a default you did
  not state.
- **Be honest about verification.** If something can only be confirmed in a running Editor, the
  skill says so rather than implying a pass.

## Adding or changing a reference

`references/` holds snapshots of external documentation so skills never reason from memory. Each:

- **states the date it was captured** and links its primary sources;
- records **only what the documentation actually says.** If a complete list was never published —
  as with the deprecated MCP tool names — say that, rather than filling the gap;
- marks deprecated material clearly as deprecated.

## Adding an agent

`agents/<name>.md`, frontmatter `name` matching the filename, plus `description`, `tools` and
`model` (`sonnet`, `opus`, `haiku`, `fable`, `inherit`, or a full model id).

Two traps the validator guards:

- **Claude Code ignores an unrecognised agent field without reporting an error**, so a typo fails
  silently. Only allowlisted keys pass.
- **`allowed-tools` is a *skill* key, not an agent key.** Agents use `tools` and `disallowedTools`.

Do not add a `skills:` key. It injects **full skill content**, not descriptions, and defeats the
tiering the whole repo is built around. List allowed skills in the body instead.

Every agent must open by reading only `design/STATE.md` and `design/INDEX.md`, and end in its fixed
handoff format.

## Commits

Conventional commits: `feat:`, `fix:`, `docs:`, `refactor:`, `chore:`, with a scope where it helps
(`feat(skills):`). Explain **why** in the body, not just what — the reason a constraint exists is
the part that is expensive to rediscover.

## What not to contribute

- **Vendored third-party skills.** Unity's are under the Unity Companion License, which is not open
  source. Link and document; never copy.
- **A skill duplicating something Unity maintains**, unless it adds this project's conventions and
  defers to the official one by name.
- **Node.js tooling.** The scripts are Python and Bash so the pack runs with no install step.
- **Secrets, API keys, or a provider key in an example.** Environment variables only.
