#!/usr/bin/env bash
# Install unity-skillforge into a Unity game repo.
#
# This copies the pack's skills into both tools' directories and places the
# read-by-path tier at a FIXED path, .unity-skillforge/, so every SKILL.md can
# cite `PACK/references/...` and have it resolve. Claude Code has
# ${CLAUDE_SKILL_DIR} for this; Codex documents no equivalent, so a fixed path
# is the only thing that works in both.
#
# Usage: scripts/install.sh [TARGET_DIR] [--symlink] [--dry-run] [--no-agents-md]
#        TARGET_DIR defaults to the current directory.
set -euo pipefail

PACK_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET="${PWD}"
MODE="copy"
DRY_RUN=0
WRITE_AGENTS_MD=1

for arg in "$@"; do
  case "$arg" in
    --symlink)       MODE="symlink" ;;
    --copy)          MODE="copy" ;;
    --dry-run)       DRY_RUN=1 ;;
    --no-agents-md)  WRITE_AGENTS_MD=0 ;;
    -h|--help) sed -n '2,12p' "${BASH_SOURCE[0]}"; exit 0 ;;
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

run() { if [[ "$DRY_RUN" == 1 ]]; then echo "  would: $*"; else "$@"; fi; }

echo "Installing unity-skillforge"
echo "  pack:   $PACK_ROOT"
echo "  target: $TARGET"
echo "  mode:   $MODE$([[ $DRY_RUN == 1 ]] && echo ' (dry run)')"
echo

# 1. Skills and agents, into both tools' directories.
if [[ "$DRY_RUN" == 1 ]]; then
  "$PACK_ROOT/scripts/sync-agents-dir.sh" "$TARGET" "--$MODE" --dry-run
else
  "$PACK_ROOT/scripts/sync-agents-dir.sh" "$TARGET" "--$MODE"
fi
echo

# 2. The read-by-path tier, at the fixed path skills cite as PACK/.
PACK_DIR="$TARGET/.unity-skillforge"
echo "Tier 2 (read by path) -> $PACK_DIR"
run mkdir -p "$PACK_DIR"
for dir in references rules templates scripts; do
  if [[ -e "$PACK_DIR/$dir" || -L "$PACK_DIR/$dir" ]]; then run rm -rf "$PACK_DIR/$dir"; fi
  if [[ "$MODE" == "symlink" ]]; then
    run ln -s "$PACK_ROOT/$dir" "$PACK_DIR/$dir"
  else
    run cp -R "$PACK_ROOT/$dir" "$PACK_DIR/$dir"
  fi
  echo "  $dir"
done
for file in AGENTS.md; do
  if [[ -e "$PACK_DIR/$file" ]]; then run rm -f "$PACK_DIR/$file"; fi
  run cp "$PACK_ROOT/$file" "$PACK_DIR/$file"
done
if [[ -d "$PACK_ROOT/docs" ]]; then
  if [[ -e "$PACK_DIR/docs" || -L "$PACK_DIR/docs" ]]; then run rm -rf "$PACK_DIR/docs"; fi
  run cp -R "$PACK_ROOT/docs" "$PACK_DIR/docs"
  echo "  docs"
fi
echo

# 3. Tier 0. AGENTS.md is the canonical rules file; CLAUDE.md only points at it.
#    Never overwrite a repo's existing AGENTS.md — append an include instead, so
#    the game's own rules survive.
if [[ "$WRITE_AGENTS_MD" == 1 ]]; then
  echo "Tier 0 (always loaded)"
  if [[ -f "$TARGET/AGENTS.md" ]]; then
    if grep -q 'unity-skillforge' "$TARGET/AGENTS.md" 2>/dev/null; then
      echo "  AGENTS.md already references unity-skillforge, leaving it alone"
    else
      echo "  AGENTS.md exists — appending a pointer rather than overwriting it"
      if [[ "$DRY_RUN" == 1 ]]; then
        echo "  would: append a unity-skillforge section to $TARGET/AGENTS.md"
      else
        cat >> "$TARGET/AGENTS.md" <<'APPEND'

## Unity rules (unity-skillforge)

Read `.unity-skillforge/AGENTS.md` before any Unity work. It holds the hard rules and the routing
table that maps a task to the skill that handles it.
APPEND
      fi
    fi
  else
    run cp "$PACK_ROOT/AGENTS.md" "$TARGET/AGENTS.md"
    echo "  AGENTS.md"
  fi

  if [[ -f "$TARGET/CLAUDE.md" ]]; then
    echo "  CLAUDE.md exists, leaving it alone"
  else
    if [[ "$DRY_RUN" == 1 ]]; then
      echo "  would: write $TARGET/CLAUDE.md containing '@AGENTS.md'"
    else
      printf '@AGENTS.md\n' > "$TARGET/CLAUDE.md"
    fi
    echo "  CLAUDE.md"
  fi
  echo
fi

# 4. The design/ contract, if the repo does not have one yet.
if [[ ! -d "$TARGET/design" ]]; then
  echo "design/ (the game's own docs: what we are building)"
  run mkdir -p "$TARGET/design"
  for template in STATE.md INDEX.md; do
    run cp "$PACK_ROOT/templates/game-design/$template" "$TARGET/design/$template"
    echo "  design/$template"
  done
  echo "  Fill these in with the design-write-gdd skill. pitch.md, art-bible.md,"
  echo "  mechanic.md and tech-decisions.md are copied by the skills that own them."
else
  echo "design/ already exists, leaving it alone"
fi
echo

cat <<'NEXT'
Next steps
  1. Install the Unity CLI and the Pipeline package:
       curl -fsSL https://unity.com/install.sh | bash     # or: brew install --cask unity-cli
       unity --version && unity auth login
       unity pipeline install        # with the project open in Unity 6.3 LTS or later
       unity status                  # confirm the CLI can reach the Editor
  2. Strongly recommended, and complementary rather than overlapping:
       /plugin marketplace add Unity-Technologies/unity-agent-plugin
       /plugin install unity@unity-agent-plugin
  3. Start with:  "Use the unity-game-router skill" or fill in design/STATE.md.

Docs: .unity-skillforge/docs/INSTALL.md and .unity-skillforge/docs/USAGE.md
NEXT
