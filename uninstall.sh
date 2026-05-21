#!/usr/bin/env bash
#
# uninstall.sh — remove de-legal-toolkit symlinks from Claude Code.
#
# Only removes symlinks that point at THIS toolkit. Safe if you have other
# Claude Code skills installed via different mechanisms.

set -euo pipefail

TOOLKIT="$(cd "$(dirname "$0")" && pwd)"
GLOBAL="${CLAUDE_GLOBAL_SKILLS:-$HOME/.claude/skills}"

echo "Toolkit: $TOOLKIT"
echo "Global:  $GLOBAL"
echo ""

removed=0

# Global
echo "Removing global symlinks pointing at $TOOLKIT..."
for link in "$GLOBAL"/*; do
  if [ -L "$link" ]; then
    target=$(readlink -f "$link")
    if [[ "$target" == "$TOOLKIT"/* ]]; then
      echo "  ✓ $(basename "$link")"
      rm "$link"
      removed=$((removed + 1))
    fi
  fi
done

# Toolkit-local
if [ -d "$TOOLKIT/.claude/skills" ]; then
  echo ""
  echo "Removing toolkit-local symlinks..."
  for link in "$TOOLKIT"/.claude/skills/*; do
    if [ -L "$link" ]; then
      echo "  ✓ $(basename "$link")"
      rm "$link"
      removed=$((removed + 1))
    fi
  done
fi

echo ""
echo "Removed $removed symlinks."
echo "The toolkit repo itself is untouched at $TOOLKIT — delete manually if desired."
