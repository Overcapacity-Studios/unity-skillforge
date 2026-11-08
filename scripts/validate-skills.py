#!/usr/bin/env python3
"""Validate unity-skillforge's structure, limits and cross-references.

Run from the repo root:   python3 scripts/validate-skills.py
Exits 0 when everything passes, 1 otherwise.

Stdlib only, on purpose: this must run on a fresh machine with no pip install.
The frontmatter parser handles the restricted shape this repo allows (see
PORTABLE_KEYS) and fails loudly on anything else rather than guessing.
"""
from __future__ import annotations

import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Outside Claude Code (claude.ai uploads, the Skills API) any other frontmatter
# key is a hard error, so the repo stays loadable everywhere.
PORTABLE_KEYS = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
METADATA_KEYS = {"version", "support"}

# Claude Code subagent frontmatter. `allowed-tools` is a SKILL key, not an agent
# key, and Claude Code ignores unknown agent fields silently — so we reject them.
AGENT_REQUIRED = {"name", "description"}
AGENT_OPTIONAL = {
    "tools", "disallowedTools", "model", "permissionMode", "maxTurns", "autoCompactWindow",
    "skills", "mcpServers", "hooks", "memory", "background", "omitClaudeMd", "effort",
    "isolation", "color", "initialPrompt",
}
AGENT_MODELS = {"sonnet", "opus", "haiku", "fable", "inherit"}

MAX_SKILL_LINES = 200
MAX_AGENTS_MD_LINES = 150
MAX_DESCRIPTION_CHARS = 300
MIN_README_WORDS = 40

SKILL_SECTIONS = [
    "## When to use",
    "## Inputs needed",
    "## Steps",
    "## Files to read (exact paths)",
    "## Done checklist",
    "## Common mistakes",
]

# Paths belonging to a game project, not to this pack. Skills legitimately cite
# these and they must not exist here.
PROJECT_PREFIXES = ("design/", "Assets/", "Packages/", "ProjectSettings/", "art-source/")

problems: list[str] = []


def fail(where: str, message: str) -> None:
    problems.append(f"{where}: {message}")


def split_frontmatter(path: str, text: str) -> dict[str, object] | None:
    """Return the parsed frontmatter mapping, or None after recording a problem."""
    if not text.startswith("---\n"):
        fail(path, "frontmatter must start with '---' as the very first line")
        return None
    end = text.find("\n---\n", 3)
    if end == -1:
        fail(path, "frontmatter block is not closed with '---'")
        return None

    data: dict[str, object] = {}
    current_block: str | None = None
    for raw in text[4:end + 1].splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        if raw[0] in " \t":
            if current_block is None:
                fail(path, f"indented frontmatter line with no parent key: {raw.strip()!r}")
                continue
            match = re.match(r"\s+([A-Za-z0-9_-]+):\s*(.*)$", raw)
            if not match:
                fail(path, f"cannot parse nested frontmatter line: {raw.strip()!r}")
                continue
            data.setdefault(current_block, {})
            data[current_block][match.group(1)] = match.group(2).strip()  # type: ignore[index]
            continue
        match = re.match(r"([A-Za-z0-9_-]+):\s*(.*)$", raw)
        if not match:
            fail(path, f"cannot parse frontmatter line: {raw.strip()!r}")
            continue
        key, value = match.group(1), match.group(2).strip()
        current_block = key if value == "" else None
        if value == "":
            data[key] = {}
        else:
            if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
                value = value[1:-1]
            data[key] = value
    return data


def is_placeholder(path: str) -> bool:
    """A path written as an example rather than a real one, e.g. PACK/skills/<name>/."""
    return "<" in path or ">" in path or "..." in path or "*" in path


def cited_pack_paths(text: str) -> set[str]:
    """Every real PACK/... path the document cites, in backticks or a markdown link."""
    found = set(re.findall(r"`PACK/([^`\s]+)`", text))
    found |= set(re.findall(r"\]\(PACK/([^)\s]+)\)", text))
    return {p for p in found if not is_placeholder(p)}


def check_relative_links(path: str, text: str) -> None:
    for target in re.findall(r"\]\(([^)]+)\)", text):
        if target.startswith(("http://", "https://", "#", "mailto:", "PACK/")):
            continue
        if target.startswith(PROJECT_PREFIXES):
            continue
        resolved = os.path.normpath(os.path.join(os.path.dirname(path), target.split("#")[0]))
        if not os.path.exists(resolved):
            fail(path, f"broken relative link: {target}")


def routing_table(text: str) -> set[str]:
    """Skill names in a markdown table's final column, written in backticks."""
    return set(re.findall(r"\|\s*`([a-z0-9][a-z0-9-]*)`\s*\|?\s*$", text, re.M))


def validate_skills() -> set[str]:
    skills_dir = os.path.join(ROOT, "skills")
    names: set[str] = set()
    for entry in sorted(os.listdir(skills_dir)):
        folder = os.path.join(skills_dir, entry)
        if not os.path.isdir(folder):
            continue
        names.add(entry)
        rel = f"skills/{entry}/SKILL.md"
        skill_md = os.path.join(folder, "SKILL.md")
        if not os.path.exists(skill_md):
            fail(rel, "missing")
            continue
        text = open(skill_md, encoding="utf-8").read()

        line_count = len(text.splitlines())
        if line_count > MAX_SKILL_LINES:
            fail(rel, f"{line_count} lines, limit is {MAX_SKILL_LINES}")

        data = split_frontmatter(rel, text)
        if data is None:
            continue

        extra = set(data) - PORTABLE_KEYS
        if extra:
            fail(rel, f"non-portable frontmatter key(s): {sorted(extra)}")
        if isinstance(data.get("metadata"), dict):
            unknown = set(data["metadata"]) - METADATA_KEYS  # type: ignore[arg-type]
            if unknown:
                fail(rel, f"unknown metadata key(s): {sorted(unknown)}")

        name = data.get("name")
        if not isinstance(name, str) or not name.strip():
            fail(rel, "missing or empty 'name'")
        elif name != entry:
            fail(rel, f"name {name!r} does not match folder {entry!r}")

        desc = data.get("description")
        if not isinstance(desc, str) or not desc.strip():
            fail(rel, "missing or empty 'description'")
        else:
            if len(desc) > MAX_DESCRIPTION_CHARS:
                fail(rel, f"description is {len(desc)} chars, limit is {MAX_DESCRIPTION_CHARS}")
            if "<" in desc or ">" in desc:
                fail(rel, "description contains angle brackets; the plugin directory scan rejects them")

        # Required sections, present and in order.
        positions = []
        for heading in SKILL_SECTIONS:
            index = text.find(f"\n{heading}\n")
            if index == -1:
                fail(rel, f"missing required section {heading!r}")
            else:
                positions.append((index, heading))
        if len(positions) == len(SKILL_SECTIONS) and positions != sorted(positions):
            fail(rel, "required sections are out of order: " + " then ".join(h for _, h in positions))

        for cited in cited_pack_paths(text):
            if not os.path.exists(os.path.join(ROOT, cited)):
                fail(rel, f"cited path does not exist: PACK/{cited}")
        check_relative_links(skill_md, text)
    return names


def validate_agents() -> None:
    agents_dir = os.path.join(ROOT, "agents")
    for entry in sorted(os.listdir(agents_dir)):
        if not entry.endswith(".md"):
            continue
        rel = f"agents/{entry}"
        text = open(os.path.join(agents_dir, entry), encoding="utf-8").read()
        data = split_frontmatter(rel, text)
        if data is None:
            continue

        missing = AGENT_REQUIRED - set(data)
        if missing:
            fail(rel, f"missing required frontmatter key(s): {sorted(missing)}")
        unknown = set(data) - AGENT_REQUIRED - AGENT_OPTIONAL
        if unknown:
            fail(rel, f"unknown agent frontmatter key(s) (Claude Code ignores these silently): {sorted(unknown)}")

        name = data.get("name")
        expected = entry[:-3]
        if isinstance(name, str):
            if name != expected:
                fail(rel, f"name {name!r} does not match filename {expected!r}")
            if ":" in name:
                fail(rel, "agent name must not contain ':'")
            if len(name) > 256:
                fail(rel, f"agent name is {len(name)} chars, limit is 256")

        model = data.get("model")
        if isinstance(model, str) and model not in AGENT_MODELS and not model.startswith("claude-"):
            fail(rel, f"model {model!r} is not one of {sorted(AGENT_MODELS)} or a full model id")

        for cited in cited_pack_paths(text):
            bare = cited.rstrip("/")
            if not os.path.exists(os.path.join(ROOT, bare)):
                fail(rel, f"cited path does not exist: PACK/{cited}")
        check_relative_links(os.path.join(agents_dir, entry), text)


def validate_root(skill_names: set[str]) -> None:
    agents_md = os.path.join(ROOT, "AGENTS.md")
    text = open(agents_md, encoding="utf-8").read()
    line_count = len(text.splitlines())
    if line_count > MAX_AGENTS_MD_LINES:
        fail("AGENTS.md", f"{line_count} lines, limit is {MAX_AGENTS_MD_LINES}")

    table = routing_table(text)
    if table != skill_names:
        fail("AGENTS.md", f"routing table out of sync — missing {sorted(skill_names - table)}, "
                          f"unknown {sorted(table - skill_names)}")
    for cited in cited_pack_paths(text):
        if not os.path.exists(os.path.join(ROOT, cited.rstrip("/"))):
            fail("AGENTS.md", f"cited path does not exist: PACK/{cited}")

    claude_md = open(os.path.join(ROOT, "CLAUDE.md"), encoding="utf-8").read().strip()
    if claude_md != "@AGENTS.md":
        fail("CLAUDE.md", f"must contain only '@AGENTS.md', found {claude_md!r}")

    # The router is Tier 0 on the plugin path, so it carries the same table —
    # minus itself, since a router does not route to itself.
    router = os.path.join(ROOT, "skills", "unity-game-router", "SKILL.md")
    if os.path.exists(router):
        router_table = routing_table(open(router, encoding="utf-8").read())
        expected = skill_names - {"unity-game-router"}
        if router_table != expected:
            fail("skills/unity-game-router/SKILL.md",
                 f"routing table out of sync with AGENTS.md — missing {sorted(expected - router_table)}, "
                 f"unknown {sorted(router_table - expected)}")

    readme_path = os.path.join(ROOT, "README.md")
    if not os.path.exists(readme_path):
        fail("README.md", "missing at the repo root")
    else:
        words = [w for w in re.split(r"\s+", open(readme_path, encoding="utf-8").read()) if re.search(r"\w", w)]
        if len(words) < MIN_README_WORDS:
            fail("README.md", f"{len(words)} words, the plugin directory needs at least {MIN_README_WORDS}")

    for doc in sorted(os.listdir(os.path.join(ROOT, "docs"))) if os.path.isdir(os.path.join(ROOT, "docs")) else []:
        if not doc.endswith(".md"):
            continue
        path = os.path.join(ROOT, "docs", doc)
        text = open(path, encoding="utf-8").read()
        for cited in cited_pack_paths(text):
            if not os.path.exists(os.path.join(ROOT, cited.rstrip("/"))):
                fail(f"docs/{doc}", f"cited path does not exist: PACK/{cited}")
        check_relative_links(path, text)


def main() -> int:
    skill_names = validate_skills()
    validate_agents()
    validate_root(skill_names)

    if problems:
        print(f"{len(problems)} problem(s):", file=sys.stderr)
        for problem in problems:
            print(f"  {problem}", file=sys.stderr)
        return 1
    print(f"OK — {len(skill_names)} skills, "
          f"{len([f for f in os.listdir(os.path.join(ROOT, 'agents')) if f.endswith('.md')])} agents, "
          "frontmatter portable, limits respected, routing tables in sync, references resolve.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
