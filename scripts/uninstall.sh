#!/usr/bin/env bash
# Remove unity-skillforge from a game repo.
#
# Removes only what install.sh adds, and NEVER touches design/ — those are your
# game's own documents, not the pack's. Your Assets/ are not touched either.
#
# Usage: scripts/uninstall.sh [TARGET_DIR] [--dry-run] [--yes]
set -euo pipefail

TARGET="${PWD}"
DRY_RUN=0
ASSUME_YES=0

for arg in "$@"; do
  case "$arg" in
    --dry-run) DRY_RUN=1 ;;
    --yes|-y)  ASSUME_YES=1 ;;
    -h|--help) sed -n '2,8p' "${BASH_SOURCE[0]}"; exit 0 ;;
    -*) echo "unknown option: $arg" >&2; exit 2 ;;
    *)  TARGET="$arg" ;;
  esac
done

[[ -d "$TARGET" ]] || { echo "error: no such directory: $TARGET" >&2; exit 1; }
TARGET="$(cd "$TARGET" && pwd)"

PACK_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [[ "$TARGET" == "$PACK_ROOT" ]]; then
  echo "error: that is the pack itself, not a game repo." >&2
  exit 1
fi

echo "Removing unity-skillforge from: $TARGET"
echo

# Only remove skills this pack owns, so a hand-written or third-party skill in
# the same directory survives. Avoids `mapfile`, which is bash 4+ and so absent
# from the bash 3.2 that ships with macOS.
to_remove=()
for skill_dir in "$PACK_ROOT"/skills/*/; do
  name="$(basename "$skill_dir")"
  for base in "$TARGET/.claude/skills" "$TARGET/.agents/skills"; do
    if [[ -e "$base/$name" || -L "$base/$name" ]]; then to_remove+=("$base/$name"); fi
  done
done
for agent_file in "$PACK_ROOT"/agents/*.md; do
  [[ -e "$agent_file" ]] || continue
  name="$(basename "$agent_file")"
  if [[ -e "$TARGET/.claude/agents/$name" || -L "$TARGET/.claude/agents/$name" ]]; then
    to_remove+=("$TARGET/.claude/agents/$name")
  fi
done
if [[ -e "$TARGET/.unity-skillforge" || -L "$TARGET/.unity-skillforge" ]]; then
  to_remove+=("$TARGET/.unity-skillforge")
fi

if [[ ${#to_remove[@]} -eq 0 ]]; then
  echo "Nothing to remove — unity-skillforge does not appear to be installed here."
else
  echo "Will remove ${#to_remove[@]} item(s), including:"
  printf '  %s\n' "${to_remove[@]:0:6}"
  [[ ${#to_remove[@]} -gt 6 ]] && echo "  ... and $(( ${#to_remove[@]} - 6 )) more"
  echo

  if [[ "$DRY_RUN" == 1 ]]; then
    echo "(dry run: nothing changed)"
  else
    if [[ "$ASSUME_YES" != 1 ]]; then
      read -r -p "Proceed? [y/N] " reply
      [[ "$reply" =~ ^[Yy]$ ]] || { echo "Aborted."; exit 0; }
    fi
    for path in "${to_remove[@]}"; do rm -rf "$path"; done
    # Clean up directories we created, only if they are now empty.
    for dir in "$TARGET/.claude/skills" "$TARGET/.claude/agents" "$TARGET/.claude" \
               "$TARGET/.agents/skills" "$TARGET/.agents"; do
      [[ -d "$dir" ]] && rmdir "$dir" 2>/dev/null || true
    done
    echo "Removed."
  fi
fi

# Remove the section install.sh appended to an AGENTS.md that already existed.
# Leaving it behind points the agent at a directory we just deleted, and it would
# try to read it every session.
AGENTS_FILE="$TARGET/AGENTS.md"
if [[ -f "$AGENTS_FILE" ]] && grep -q '^## Unity rules (unity-skillforge)$' "$AGENTS_FILE"; then
  if [[ "$DRY_RUN" == 1 ]]; then
    echo "would: remove the '## Unity rules (unity-skillforge)' section from $AGENTS_FILE"
  else
    python3 - "$AGENTS_FILE" <<'STRIP'
import re, sys
path = sys.argv[1]
text = open(path, encoding="utf-8").read()
# The section runs from its heading to the next top-level heading, or end of file.
new = re.sub(r"\n*^## Unity rules \(unity-skillforge\)$.*?(?=^## |\Z)",
             "\n\n", text, flags=re.S | re.M)
new = re.sub(r"\n{3,}", "\n\n", new)
if new != text:
    open(path, "w", encoding="utf-8").write(new.rstrip() + "\n")
    print("  removed the unity-skillforge section from AGENTS.md")
STRIP
  fi
fi

echo
cat <<'MANUAL'
Left in place deliberately — review and remove by hand if you want them gone:

  design/          YOUR game's design documents. Never removed by this script.
  AGENTS.md        If the installer created it, it is this pack's rules file and is safe to
                   delete. If it already existed, the appended "## Unity rules" section has
                   been removed for you and your own rules are untouched.
  CLAUDE.md        Contains just "@AGENTS.md" if the installer wrote it.
MANUAL
