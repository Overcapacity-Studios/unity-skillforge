#!/usr/bin/env bash
# Mirror the canonical skills/ tree into the per-tool directories a target repo needs.
#
# Claude Code reads  .claude/skills/<name>/SKILL.md
# Codex reads        .agents/skills/<name>/SKILL.md   (NOT .codex/skills)
# Neither tool scans those directories recursively, which is why skills/ is flat.
#
# Usage: scripts/sync-agents-dir.sh [TARGET_DIR] [--symlink] [--dry-run]
#        TARGET_DIR defaults to the current directory.
set -euo pipefail

PACK_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET="${PWD}"
MODE="copy"
DRY_RUN=0

for arg in "$@"; do
  case "$arg" in
    --symlink) MODE="symlink" ;;
    --copy)    MODE="copy" ;;
    --dry-run) DRY_RUN=1 ;;
    -h|--help) sed -n '2,10p' "${BASH_SOURCE[0]}"; exit 0 ;;
    -*) echo "unknown option: $arg" >&2; exit 2 ;;
    *)  TARGET="$arg" ;;
  esac
done

if [[ ! -d "$TARGET" ]]; then
  echo "error: target directory does not exist: $TARGET" >&2
  exit 1
fi
TARGET="$(cd "$TARGET" && pwd)"

if [[ "$TARGET" == "$PACK_ROOT" ]]; then
  echo "error: target is the pack itself. Pass the game repo's path." >&2
  exit 1
fi

run() {
  if [[ "$DRY_RUN" == 1 ]]; then
    echo "  would: $*"
  else
    "$@"
  fi
}

# install.sh prints this header itself; printing it again mid-install looks like a bug.
if [[ -z "${UNITY_SKILLFORGE_QUIET_HEADER:-}" ]]; then
  echo "pack:   $PACK_ROOT"
  echo "target: $TARGET"
  echo "mode:   $MODE$([[ $DRY_RUN == 1 ]] && echo ' (dry run)')"
fi

for dest in "$TARGET/.claude/skills" "$TARGET/.agents/skills"; do
  run mkdir -p "$dest"
  count=0
  for skill_dir in "$PACK_ROOT"/skills/*/; do
    name="$(basename "$skill_dir")"
    # The shared data package is installed once to .unity-skillforge/ by install.sh,
    # so it does not also belong in the skills directories.
    if [[ "$name" == "unity-skillforge-pack" ]]; then continue; fi
    link="$dest/$name"
    # Replace an existing entry so a re-run picks up changes instead of
    # leaving a stale copy that silently disagrees with the pack.
    if [[ -e "$link" || -L "$link" ]]; then
      run rm -rf "$link"
    fi
    if [[ "$MODE" == "symlink" ]]; then
      run ln -s "$skill_dir" "$link"
    else
      run cp -R "$skill_dir" "$link"
    fi
    count=$((count + 1))
  done
  echo "  $dest  <- $count skills"
done

# Subagents are a Claude Code concept; Codex has no equivalent directory, and
# docs/CODEX.md ships the same seven roles as copy-paste prompts instead.
if [[ -d "$PACK_ROOT/agents" ]]; then
  run mkdir -p "$TARGET/.claude/agents"
  for agent in "$PACK_ROOT"/agents/*.md; do
    dest="$TARGET/.claude/agents/$(basename "$agent")"
    if [[ -e "$dest" || -L "$dest" ]]; then run rm -f "$dest"; fi
    if [[ "$MODE" == "symlink" ]]; then run ln -s "$agent" "$dest"; else run cp "$agent" "$dest"; fi
  done
  echo "  $TARGET/.claude/agents  <- $(ls -1 "$PACK_ROOT"/agents/*.md | wc -l | tr -d ' ') agents"
fi

echo "done."
