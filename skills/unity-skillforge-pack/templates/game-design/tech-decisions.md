# Technical decisions — <game name>

<!--
An append-only decision log. One entry per decision that constrains future work.
An agent reads this before choosing a package, pattern or system, so it does not
re-litigate something already settled. Never delete an entry: supersede it.
-->

**Updated:** YYYY-MM-DD

## Pinned versions

| Thing | Version | Notes |
| --- | --- | --- |
| Unity Editor | `6000.3.__f_` | Unity 6.3 LTS; see `references/unity-versions.md` |
| Render pipeline | URP `__._._` | |
| Input System | `__._._` | Active Input Handling = Input System Package (New) |
| Cinemachine | `3._._` | 3.x API; 2.x is a different API surface |
| Test Framework | `__._._` | |
| Unity CLI | `unity --version` output | Experimental; re-verify commands per version |

Record the versions actually resolved in `Packages/packages-lock.json`, not what was requested.

## Decisions

### <YYYY-MM-DD> — <Decision title>

- **Decision:** <what was chosen>
- **Alternatives:** <what was rejected>
- **Why:** <the reason, in one or two sentences>
- **Constrains:** <what future work must now respect>
- **Reversible?** <cheap / expensive / one-way — and what it would cost>

### <YYYY-MM-DD> — 2D physics system

- **Decision:** legacy `Rigidbody2D` / `Collider2D` | 2D Physics Core (`Unity.U2D.Physics`)
- **Why:** <e.g. baseline is 6000.3.x, and Core components require 6000.7+>
- **Constrains:** every 2D physics script. The two systems share no code and never interact —
  mixing them produces code that compiles, runs and does nothing.
- **Reversible?** expensive — it is a rewrite of all physics code.

### <YYYY-MM-DD> — Renderer

- **Decision:** 2D Renderer | Universal Renderer (Forward | Forward+ | Deferred)
- **Constrains:** lighting approach; changing it later invalidates light bakes.

## Open questions

| Question | Blocks | Needs a decision by |
| --- | --- | --- |
| <...> | <...> | <...> |

## Superseded

| Date | Was | Now | Why |
| --- | --- | --- | --- |
