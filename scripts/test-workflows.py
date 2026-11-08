#!/usr/bin/env python3
"""Workflow-contract tests for unity-skillforge.

Run from the repo root:   python3 scripts/test-workflows.py
Exits 0 when everything passes, 1 otherwise.

WHAT THESE ARE: static checks that the pack's own documents tell an agent the right thing —
that the router routes a rough idea to discovery, that the art-bible gate still holds for
production art while placeholders are exempt, that nothing instructs an agent to invent a
Play Mode or playtest result, and so on.

WHAT THESE ARE NOT: they do not run an agent, and they do not touch a Unity Editor. A pass
here means the instructions are consistent, not that any runtime behaviour was observed.

Stdlib only, like validate-skills.py, so it runs on a clean machine.
"""
from __future__ import annotations

import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PACK = os.path.join(ROOT, "skills", "unity-skillforge-pack")

failures: list[str] = []
checks = 0


def read(*parts: str) -> str:
    path = os.path.join(ROOT, *parts)
    if not os.path.exists(path):
        failures.append(f"missing file: {os.path.join(*parts)}")
        return ""
    return open(path, encoding="utf-8").read()


def skill(name: str) -> str:
    return read("skills", name, "SKILL.md")


def agent(name: str) -> str:
    return read("agents", f"{name}.md")


def template(name: str) -> str:
    return read("skills", "unity-skillforge-pack", "templates", "game-design", name)


def expect(test: str, condition: bool, detail: str) -> None:
    global checks
    checks += 1
    if not condition:
        failures.append(f"{test}: {detail}")


def flat(text: str) -> str:
    """Collapse whitespace and lowercase, so a line-wrapped sentence still matches."""
    return re.sub(r"\s+", " ", text).lower()


def contains(test: str, text: str, needle: str, where: str) -> None:
    expect(test, flat(needle) in flat(text), f"{where} does not say: {needle!r}")


def absent(test: str, text: str, needle: str, where: str) -> None:
    expect(test, flat(needle) not in flat(text), f"{where} must not say: {needle!r}")


# --------------------------------------------------------------------------- A
def test_a_vague_idea_gets_discovery() -> None:
    """A user presents a vague game idea. Expected: discovery, not implementation."""
    T = "TEST A (vague idea routes to discovery)"
    router = skill("unity-game-router")
    discovery = skill("design-idea-discovery")
    gdd = skill("design-write-gdd")
    agents_md = read("AGENTS.md")

    expect(T, bool(discovery), "skills/design-idea-discovery/SKILL.md is missing")

    # The router must map a rough idea to discovery, in a table row.
    rough_row = re.search(r"^\|.*rough idea.*\|\s*`design-idea-discovery`\s*\|\s*$",
                          router, re.M | re.I)
    expect(T, rough_row is not None,
           "unity-game-router has no table row sending a rough idea to design-idea-discovery")

    # Both routing tables must know the skill.
    for where, text in (("AGENTS.md", agents_md), ("unity-game-router", router)):
        contains(T, text, "`design-idea-discovery`", where)

    # Discovery must not jump to a GDD or to code.
    contains(T, discovery, "Do not write `pitch.md` here", "design-idea-discovery")
    contains(T, discovery, "do not start building", "design-idea-discovery")
    contains(T, discovery, "at most three questions", "design-idea-discovery")
    contains(T, discovery, "confirmed or assumed", "design-idea-discovery")

    # And it must work with no Unity project at all.
    contains(T, discovery, "no unity project", "design-idea-discovery")
    contains(T, router, "no `design/` folder", "unity-game-router")

    # The GDD skill must hand a rough idea back rather than absorbing it.
    contains(T, gdd, "`design-idea-discovery` first", "design-write-gdd")

    # The concept template must carry the lightweight concept contract.
    concept = template("concept.md")
    for field in ("High concept", "Player fantasy", "Target audience", "Core verbs",
                  "Core gameplay loop hypothesis", "Design pillars",
                  "Unique selling proposition hypothesis", "Major gameplay risks",
                  "Technical risks", "Scope constraints", "Open questions",
                  "Recommended next step"):
        contains(T, concept, field, "templates/game-design/concept.md")


# --------------------------------------------------------------------------- B
def test_b_conflict_with_approved_decision() -> None:
    """A request conflicts with an approved decision. Expected: conflict analysis + recommendation."""
    T = "TEST B (conflict with an approved decision)"
    log = skill("design-decision-log")
    spec = skill("design-mechanic-spec")
    director = agent("game-director")
    decisions = template("decisions.md")

    expect(T, bool(log), "skills/design-decision-log/SKILL.md is missing")
    expect(T, bool(director), "agents/game-director.md is missing")

    # All five statuses must be defined.
    for status in ("PROPOSED", "APPROVED", "REJECTED", "SUPERSEDED", "NEEDS VALIDATION"):
        contains(T, decisions, status, "templates/game-design/decisions.md")

    # History must be preserved, not rewritten.
    contains(T, decisions, "Append-only", "templates/game-design/decisions.md")
    contains(T, decisions, "Conflicts raised", "templates/game-design/decisions.md")
    contains(T, log, "never edit the approved entry", "design-decision-log")
    contains(T, log, "supersede", "design-decision-log")

    # Only the user approves.
    contains(T, log, "never writes `APPROVED`", "design-decision-log")
    contains(T, director, "never `APPROVED` for your own", "game-director")

    # The conflict must be surfaced with its consequences, and the user decides.
    contains(T, log, "what adopting the proposal would reopen", "design-decision-log")
    contains(T, log, "The user decides", "design-decision-log")
    contains(T, spec, "Raise\n     it; do not design around it", "design-mechanic-spec")

    # The director's report must carry a recommendation and an approval boundary.
    for heading in ("**Conflicts with approved decisions:**", "**Recommendation:**",
                    "**Needs your approval:**", "**Risks and tradeoffs:**",
                    "**Player impact:**"):
        contains(T, director, heading, "game-director handoff format")

    # The log must be read by its index, not whole.
    contains(T, decisions, "read the Index table only", "templates/game-design/decisions.md")
    contains(T, log, "only the Index table", "design-decision-log")


# --------------------------------------------------------------------------- C
def test_c_prototype_assets_vs_production_art() -> None:
    """Prototype before an art style. Expected: placeholders allowed, production art still gated."""
    T = "TEST C (prototype placeholders vs production art)"
    lock = skill("assets-art-style-lock")
    proto = skill("design-prototype-plan")
    agents_md = read("AGENTS.md")
    folders = read("skills", "unity-skillforge-pack", "rules", "folder-conventions.md")

    # The exception exists and is explicit.
    contains(T, lock, "## The prototype exception", "assets-art-style-lock")
    contains(T, lock, "does not need a locked art bible", "assets-art-style-lock")
    contains(T, agents_md, "No generated production asset without", "AGENTS.md hard rule 8")
    contains(T, agents_md, "Prototypes are exempt", "AGENTS.md hard rule 8")

    # Placeholders are identifiable and recorded.
    for where, text in (("assets-art-style-lock", lock),
                        ("design-prototype-plan", proto),
                        ("rules/folder-conventions.md", folders),
                        ("AGENTS.md", agents_md)):
        contains(T, text, "PH_", where)
        contains(T, text, "Assets/_Project/Prototype/", where)
    contains(T, folders, "never becomes production art by being renamed",
             "rules/folder-conventions.md")
    contains(T, proto, "Placeholders are named", "design-prototype-plan")

    # The production gate is untouched: both generators still refuse an unlocked style.
    for name in ("assets-gen-2d-sprite", "assets-gen-3d-model"):
        text = skill(name)
        contains(T, text, "stop and run `assets-art-style-lock`", name)
        contains(T, text, "Gate: the art bible must be locked", name)
        contains(T, text, "design-prototype-plan", name)

    # The prototype doc separates the two kinds of validation.
    contains(T, proto, "Technical validation", "design-prototype-plan")
    contains(T, proto, "Gameplay validation", "design-prototype-plan")
    contains(T, proto, "qa-playmode-check", "design-prototype-plan")
    # qa-playmode-check must accept a prototype's criteria rather than bouncing it for
    # having no mechanic spec, and must refuse to answer the gameplay questions.
    pmc = skill("qa-playmode-check")
    contains(T, pmc, "design/prototype-", "qa-playmode-check")
    contains(T, pmc, "Verify technical criteria only", "qa-playmode-check")
    contains(T, pmc, "requires a human playtest", "qa-playmode-check")
    tmpl = template("prototype.md")
    contains(T, tmpl, "Technical validation", "templates/game-design/prototype.md")
    contains(T, tmpl, "Gameplay validation", "templates/game-design/prototype.md")
    contains(T, tmpl, "Playtest log", "templates/game-design/prototype.md")


# --------------------------------------------------------------------------- D
def test_d_existing_project_is_respected() -> None:
    """A user resumes an existing Unity project. Expected: existing state respected."""
    T = "TEST D (existing project resumes)"
    router = skill("unity-game-router")
    state_tmpl = template("STATE.md")
    update = skill("design-update-state")
    install = read("scripts", "install.sh")

    # Stage exists, and the router resumes from it.
    contains(T, state_tmpl, "**Stage:**", "templates/game-design/STATE.md")
    contains(T, router, "respect what is there", "unity-game-router")
    for stage in ("concept", "prototype", "production", "polish"):
        contains(T, router, f"`{stage}`", "unity-game-router stage table")

    # Backwards compatibility: an older design/ folder with no Stage must still work.
    contains(T, router, "missing Stage field", "unity-game-router")
    contains(T, update, "no\n   Stage field is an older one", "design-update-state")

    # Nothing settled gets re-proposed, and discovery is not forced.
    contains(T, router, "Do\n   not re-run discovery", "unity-game-router")
    contains(T, router, "not for every new session", "unity-game-router")

    # The installer never overwrites a user's design file.
    contains(T, install, "already exists, leaving it alone", "scripts/install.sh")

    # STATE.md stays cheap to read.
    lines = len(state_tmpl.splitlines())
    expect(T, 0 < lines < 60,
           f"templates/game-design/STATE.md is {lines} lines; the contract is under 60")


# --------------------------------------------------------------------------- E
def test_e_bug_fix_skips_design() -> None:
    """A simple bug fix. Expected: no discovery, no design review."""
    T = "TEST E (a bug fix skips the design process)"
    router = skill("unity-game-router")
    spec = skill("design-mechanic-spec")
    director = agent("game-director")

    contains(T, router, "Trivial work gets no review", "unity-game-router")
    contains(T, router, "`qa-fix-console-errors`", "unity-game-router")
    contains(T, router, "Sending a bug fix or a tuning tweak through design review",
             "unity-game-router common mistakes")

    # The spec skill triages instead of applying one depth to everything.
    contains(T, spec, "Scale the review to the change", "design-mechanic-spec")
    contains(T, spec, "Skip step 1 entirely", "design-mechanic-spec")
    contains(T, spec, "friction", "design-mechanic-spec")

    # The director refuses to block small work.
    contains(T, director, "Proportional review", "game-director")
    contains(T, director, "no director review needed", "game-director")
    contains(T, director, "Blocking small work is its own failure mode", "game-director")
    contains(T, director, "none needed", "game-director handoff format")


# --------------------------------------------------------------------------- F
def test_f_no_fabricated_validation() -> None:
    """The Unity Editor is unavailable. Expected: no fabricated editor validation."""
    T = "TEST F (honesty when nothing could be verified)"
    contains(T, read("AGENTS.md"), "Report honestly", "AGENTS.md")
    contains(T, skill("unity-game-router"), "stated as unverified", "unity-game-router")
    contains(T, skill("qa-playmode-check"), "not verified — no Editor reachable",
             "qa-playmode-check")
    contains(T, agent("qa"), "not verified — no Editor reachable", "agents/qa.md")
    contains(T, agent("gameplay-coder"), "Never report a play-mode result you did not observe",
             "agents/gameplay-coder.md")

    # The new, human-only claims: playtest results and "it is fun".
    proto = skill("design-prototype-plan")
    contains(T, proto, "Never write an entry you did not receive from the user",
             "design-prototype-plan")
    contains(T, proto, "Writing playtest observations no human made",
             "design-prototype-plan")
    contains(T, proto, "no human has played it", "design-prototype-plan")
    contains(T, template("prototype.md"), "Not played yet",
             "templates/game-design/prototype.md")
    contains(T, skill("design-update-state"), "Never record a playtest outcome the user did not",
             "design-update-state")
    contains(T, agent("qa"), "requires a human playtest", "agents/qa.md")
    contains(T, agent("game-director"), "Never claim a mechanic is fun", "game-director")
    contains(T, skill("design-idea-discovery"), "it is a hypothesis until a human does",
             "design-idea-discovery")

    # An agent must never self-approve a design decision.
    contains(T, skill("design-decision-log"), "never writes `APPROVED`", "design-decision-log")


# ------------------------------------------------------------------ packaging
def test_packaging_carries_the_new_pieces() -> None:
    """Every install route must carry the new skills, agent and templates."""
    T = "PACKAGING (all install routes carry the additions)"
    install = read("scripts", "install.sh")
    uninstall = read("scripts", "uninstall.sh")
    sync = read("scripts", "sync-agents-dir.sh")

    # The scripts must enumerate skills and agents by glob, so additions travel for free.
    contains(T, sync, '"$PACK_ROOT"/skills/*/', "scripts/sync-agents-dir.sh")
    contains(T, sync, '"$PACK_ROOT"/agents/*.md', "scripts/sync-agents-dir.sh")
    contains(T, uninstall, '"$PACK_ROOT"/skills/*/', "scripts/uninstall.sh")
    contains(T, uninstall, '"$PACK_ROOT"/agents/*.md', "scripts/uninstall.sh")
    contains(T, install, "templates", "scripts/install.sh")

    # New skills exist on disk with the folder/name contract validate-skills.py enforces.
    for name in ("design-idea-discovery", "design-prototype-plan", "design-decision-log"):
        text = skill(name)
        expect(T, f"name: {name}" in text,
               f"skills/{name}/SKILL.md frontmatter name does not match its folder")
    expect(T, "name: game-director" in agent("game-director"),
           "agents/game-director.md frontmatter name does not match its filename")

    # New templates exist where the skills cite them.
    for name in ("concept.md", "prototype.md", "decisions.md"):
        expect(T, bool(template(name)),
               f"templates/game-design/{name} is missing, but a skill cites it")

    # INDEX.md must have a row for each new document type, or they are invisible.
    index = template("INDEX.md")
    for cite in ("`design/concept.md`", "`design/decisions.md`", "`design/prototype-"):
        contains(T, index, cite, "templates/game-design/INDEX.md")


def main() -> int:
    for test in (test_a_vague_idea_gets_discovery,
                 test_b_conflict_with_approved_decision,
                 test_c_prototype_assets_vs_production_art,
                 test_d_existing_project_is_respected,
                 test_e_bug_fix_skips_design,
                 test_f_no_fabricated_validation,
                 test_packaging_carries_the_new_pieces):
        test()

    if failures:
        print(f"{len(failures)} failure(s) out of {checks} checks:", file=sys.stderr)
        for failure in failures:
            print(f"  {failure}", file=sys.stderr)
        return 1
    print(f"OK — {checks} workflow-contract checks pass (TEST A-F plus packaging).")
    print("These are STATIC checks on the pack's instructions. No agent was run and no Unity")
    print("Editor was contacted, so nothing here is evidence of runtime behaviour.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
