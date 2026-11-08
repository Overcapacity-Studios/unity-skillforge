---
name: design-idea-discovery
description: Develop a rough game idea into a coherent concept through a short collaborative conversation - player fantasy, core verbs, loop hypothesis, pillars, risks and the minimum playable experience. Use before design-write-gdd, when the idea is still vague. Needs no Unity project.
metadata:
  version: 0.1.0
---

# Game idea discovery

Paths written as `PACK/` mean wherever this pack's shared files live: `.unity-skillforge/` in a
game repo (`install.sh`), the sibling `unity-skillforge-pack` folder (`npx skills add`), the
plugin's root directory (plugin install), or `skills/unity-skillforge-pack/` in this repo.

## When to use

- "I have a rough game idea, help me develop it."
- A pitch exists as a vibe, a mood or a reference game, but the player's actions are not decided.
- The user is deciding *between* ideas, or wants an idea challenged before committing to it.

Skip it when the concept is already agreed — go straight to `design-write-gdd`. Skip it for a
mechanic inside an existing game: that is `design-mechanic-spec`, with a `game-director` review
if it is significant.

**This skill needs no Unity project, no Unity CLI and no `design/` folder.** It runs on a
conversation, and it is allowed to be the whole session.

## Inputs needed

- The idea, in any form — one sentence, a reference game, a feeling, a mechanic.
- Whatever constraints are already true: time per week, deadline, solo or not, budget, platform.
- Nothing else. **Do not block on missing information**; the point of this skill is to find out
  what matters and ask only about that.

## Steps

1. If `design/STATE.md` exists, read it and `design/INDEX.md` first — this may be a second idea
   for an existing project, and the existing stage, dimension and decisions still apply.
2. **Play the idea back in one sentence** before asking anything. If you cannot, say which part is
   missing — that gap is usually the first real question.
3. **Ask at most three questions per turn**, and only high-impact ones: questions whose answer
   changes what gets built. Never present the concept template as a questionnaire.
   The four that are almost always high-impact:
   - What does the player *do*, second to second?
   - What should it feel like when it goes well?
   - What happens when the player fails?
   - How many hours a week does the user actually have?
4. **Propose, do not interrogate.** Where an answer is missing, offer two or three concrete options
   with their tradeoffs and a recommendation, and let the user pick:
   > "Three ways the dash could work: (a) unlimited but slow-recovering — forgiving, risks
   > spamming; (b) stamina-gated — adds a resource to read, costs a UI element; (c) one per
   > room — creates planning, may feel stingy. I would start with (b) because your pillar is
   > deliberate movement."
5. **Find the core verbs.** Three to five things the player does. If the idea has no verbs yet, it
   is a setting rather than a game — say so and work on the verbs first.
6. **Build the loop hypothesis** at second-to-second and minute-to-minute scale, and name the claim
   that makes it interesting. Label it a hypothesis; a loop is not known to be fun until a human
   plays it.
7. **Challenge the idea, specifically and constructively.** For each of these, raise it only if it
   is genuinely there:
   - **Contradiction** — two goals that cannot both hold ("relaxing" plus "punishing timers").
   - **Unnecessary complexity** — a system that adds no decision the player cares about.
   - **Unearned scope** — procedural generation, multiplayer, dialogue trees, open world, crafting:
     each one roughly doubles a solo project. Name the cost in sessions, not adjectives.
   - **Verb bloat** — eight verbs means none of them gets deep.
   - **A loop with no escalation** — nothing changes after five minutes.
   Offer a cheaper alternative with every challenge. A challenge with no alternative is just a no.
8. **Check feasibility against the real constraints**, solo-developer first: art cost by dimension
   (2D cheapest, 3D most expensive), systems needed, and whether assets can be placeholders for a
   long time. Say which parts of the idea are bought, not built.
9. **Name the differentiation hypothesis** — what this gives a player that the obvious comparable
   does not. If the honest answer is "nothing yet", say that; it is useful information, not a
   failure.
10. **List the risks in two buckets** — gameplay risks (the loop may not be fun) and technical
    risks (it may not be buildable at this scale) — and for each, the cheapest way to find out.
11. **Recommend a minimum playable experience**: the smallest thing a human could play that would
    settle the biggest gameplay risk.
12. Write `design/concept.md` from `PACK/templates/game-design/concept.md`, creating `design/` and
    copying `PACK/templates/game-design/INDEX.md` and `STATE.md` if they are missing. Set
    `STATE.md` → **Stage: concept** and leave the status table at "not started".
    **Mark every line confirmed or assumed.** Never record an assumption as a decision.
13. Add a row for `design/concept.md` in `design/INDEX.md`.
14. Record only genuinely settled choices through `design-decision-log`, as `PROPOSED` unless the
    user explicitly approved them.
15. Recommend the next step and stop: keep exploring one named question, `design-prototype-plan`
    to test the riskiest assumption, or `design-write-gdd` once the concept is agreed. Do not
    write `pitch.md` here, and do not start building.

## Unity CLI commands used

**None, by design.** Idea discovery happens before there is a project to touch, and must work with
no Unity installed and no Editor reachable. If the user asks what is technically possible, answer
from `PACK/references/unity-versions.md` rather than probing the Editor.

## Files to read (exact paths)

| Need | Path |
| --- | --- |
| Existing project state, if any | `design/STATE.md` |
| Design map, if any | `design/INDEX.md` |
| Decisions already approved | `design/decisions.md` (its Index table only) |
| Template to copy | `PACK/templates/game-design/concept.md` |
| Created when missing | `PACK/templates/game-design/STATE.md` |
| | `PACK/templates/game-design/INDEX.md` |
| What a dimension costs | `PACK/references/unity-versions.md` |
| Where the concept goes next | the `design-write-gdd` skill |
| How to test the riskiest claim | the `design-prototype-plan` skill |
| Reviewing the concept as a whole | the `game-director` agent |

## Done checklist

- [ ] The idea was played back in one sentence before any question was asked.
- [ ] No more than three questions per turn, each one high-impact.
- [ ] Options were proposed with tradeoffs and a recommendation, not open questions alone.
- [ ] Three to five core verbs are named.
- [ ] The loop is written at two timescales and labelled a hypothesis.
- [ ] At least one weak point was challenged, with a cheaper alternative offered.
- [ ] Gameplay risks and technical risks are listed separately, each with a cheap test.
- [ ] Solo-developer feasibility is addressed, including art cost by dimension.
- [ ] A differentiation hypothesis is stated, or honestly marked absent.
- [ ] A minimum playable experience is recommended.
- [ ] `design/concept.md` exists, is under 100 lines, and has a row in `design/INDEX.md`.
- [ ] Every line is marked confirmed or assumed; no assumption is written as a decision.
- [ ] `STATE.md` Stage is `concept`.
- [ ] A single next step is recommended, and no GDD or code was written.

## Common mistakes

- Generating a full GDD from one sentence. The user then owns twelve decisions they never made.
- Interviewing with twenty questions. The idea dies of admin before it is tested.
- Asking open questions with no options, which makes the user do all the work.
- Agreeing with everything. A design partner that never pushes back adds nothing — but a challenge
  without a cheaper alternative is just discouragement.
- Recording an assumption as a decision, so later work treats a guess as settled.
- Calling a loop fun. Nobody has played it. It is a hypothesis until a human does.
- Ignoring the solo constraint and blessing a concept that needs a team of eight.
- Letting the idea stay a setting with no verbs, so there is nothing to prototype.
- Demanding a Unity project, a dimension or an art style before the idea is worth building.
- Writing `pitch.md` here, duplicating `design-write-gdd` and skipping the user's agreement.
