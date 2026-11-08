---
name: 3d-navmesh-ai
description: Give enemies and NPCs navigation with Unity's AI Navigation package - NavMesh surfaces, agents, obstacles and links - plus the behaviour state machine that drives them. Use for pathfinding or patrol AI. Defer to Unity's initialize-ai-navigation skill for NavMesh setup itself.
metadata:
  version: 0.1.0
---

# NavMesh AI

Paths written as `PACK/` mean wherever this pack's own files live: `.unity-skillforge/` in a game
repo (created by `install.sh`), the plugin's root directory when installed as a plugin, or the
repo root when working on the pack itself.

## When to use

- Enemies or NPCs need to move toward a target or patrol.
- Agents will not move, stop short, walk through walls, or jitter against each other.
- Setting up navigation on a new 3D or 2.5D scene.

## Prefer the official skill

If Unity's official plugin is installed:

- `/unity:initialize-ai-navigation` — the authoritative procedure for NavMesh surfaces, agents,
  obstacles and links with the `com.unity.ai.navigation` package. Run it for the NavMesh setup.

What stays ours: **agent and area naming, and wiring navigation to the behaviour state machine**
below. Do not restate Unity's NavMesh procedure — link it. See
`PACK/references/official-unity-skills.md`.

## Inputs needed

- The AI behaviour from the mechanic spec: patrol, chase, flee, ranged, and the transitions between
  them. If it is not spec'd, run `design-mechanic-spec` — "make an enemy that chases" is not enough
  to build against.
- Agent dimensions (radius, height, step height, max slope) consistent with the character.
- The scene geometry, already built and marked Static.

## Steps

1. Read `design/STATE.md`, `design/INDEX.md`, and the mechanic spec's rules and tuning values.
2. Confirm `com.unity.ai.navigation` is pinned in `Packages/manifest.json`. Modern Unity uses the
   package's `NavMeshSurface` component, not the old scene-wide "Navigation window" bake. Record
   the version in `design/tech-decisions.md`.
3. Hand surface, agent-type and link setup to `/unity:initialize-ai-navigation`. Apply these project
   conventions on top:
   - **Agent types** named by role: `Humanoid`, `Small`, `Large`, `Flying`. Define each once with
     explicit radius, height, step height and max slope; never leave one on defaults.
   - **Areas** named by cost intent: `Walkable`, `NotWalkable`, `Jump`, `Water` (high cost),
     `Hazard` (very high cost). Costs are what makes AI choose sensible routes.
4. **The agent type must match the character's actual capsule.** An agent radius smaller than the
   collider is why agents clip corners and walk into walls; larger is why they refuse doorways.
5. Mark navigation geometry Static and bake the surface. **Re-bake after any geometry change** — a
   stale NavMesh looks correct and routes agents through walls that now exist.
6. Use `NavMeshObstacle` with **Carve** for dynamic blockers like doors and crates. Do not rebake at
   runtime for a moving object; carving is what that feature is for.
7. Add `NavMeshLink` wherever agents must jump, drop or use a ladder. Disconnected NavMesh islands
   are the usual cause of "the agent just stands there": there is no path, and nothing logs an error.
8. Drive behaviour with `PACK/templates/csharp/StateMachine.cs.txt`, not with logic scattered through
   `Update`: `Idle`, `Patrol`, `Chase`, `Attack`, `Flee`. The NavMeshAgent is the *movement*
   mechanism; the state machine owns the *decisions*.
9. Call `SetDestination` only when the destination actually changes, not every frame. Re-pathing
   every frame on many agents is a common and avoidable cost (`PACK/rules/performance.md`).
10. Check `agent.pathStatus` and handle `PathPartial` and `PathInvalid` explicitly. An unreachable
    target must produce a behaviour change, not an agent walking into a wall forever.
11. Let the agent drive motion. Do not also write `transform.position`, and do not put a
    `Rigidbody` on an agent unless it is kinematic — the two fight and produce jitter.
12. Verify:
    ```bash
    unity recompile --strict --format json
    ```
    then `qa-playmode-check`: agents path around obstacles, cross every link, handle an unreachable
    target, and several agents crowding one doorway do not jitter or stack.

## Unity CLI commands used

```bash
unity status                              # live Editors: port, project path, version, PID
unity list                                # Editor-registered tools and their parameter schemas
unity commands --format json              # full CLI command manifest
unity recompile --strict --format json    # compile check
unity test --format json                  # PlayMode tests asserting pathStatus and arrival
```

NavMesh baking is Editor work and can be slow: start it through the tools `unity list` reports, and
consider `unity job` for detached jobs. Use fully-qualified names such as
`UnityEngine.AI.NavMeshAgent`. See `PACK/references/unity-cli.md`.

## Files to read (exact paths)

| Need | Path |
| --- | --- |
| Project status and dimension | `design/STATE.md` |
| Design map | `design/INDEX.md` |
| AI behaviour, rules, tuning | `design/mechanic-*.md` (named in `INDEX.md`) |
| Package pin for AI Navigation | `design/tech-decisions.md` |
| Official NavMesh skill | `PACK/references/official-unity-skills.md` |
| Package pins | `PACK/references/unity-versions.md` |
| State machine template | `PACK/templates/csharp/StateMachine.cs.txt` |
| Per-frame cost rules | `PACK/rules/performance.md` |
| Character capsule dimensions | the `3d-character-controller` skill |

## Done checklist

- [ ] `com.unity.ai.navigation` is pinned and recorded; `NavMeshSurface` is used, not the legacy bake.
- [ ] Agent types are named by role with explicit radius, height, step and slope.
- [ ] Areas are named by cost intent, with costs set deliberately.
- [ ] Agent dimensions match the character's actual capsule.
- [ ] Navigation geometry is Static and the surface was re-baked after the last geometry change.
- [ ] Dynamic blockers use `NavMeshObstacle` with Carve, not runtime rebakes.
- [ ] `NavMeshLink` exists wherever agents must jump, drop or climb; no disconnected islands.
- [ ] Behaviour is in a state machine; the agent only moves.
- [ ] `SetDestination` is called on change, not every frame.
- [ ] `pathStatus` is checked, and `PathPartial` / `PathInvalid` change behaviour.
- [ ] No `transform.position` writes and no non-kinematic `Rigidbody` on agents.
- [ ] Verified in play mode, including crowding and an unreachable target.

## Common mistakes

- A stale NavMesh after geometry changed, routing agents confidently through new walls.
- Disconnected NavMesh islands with no link, so agents stand still and nothing is logged.
- Agent radius not matching the character capsule, so agents clip corners or refuse doorways.
- Calling `SetDestination` every frame for every agent, which re-paths constantly.
- Ignoring `pathStatus`, so an unreachable target makes the agent walk into a wall indefinitely.
- Rebaking the NavMesh at runtime for a door, instead of carving an obstacle.
- A non-kinematic `Rigidbody` on an agent, so physics and the agent fight and the agent jitters.
- Writing `transform.position` while the agent is also moving, producing stutter.
- Behaviour logic spread across `Update`, so no one can tell why an agent chose a state.
- Building the AI before the behaviour is spec'd, then rewriting it when the design is stated.
