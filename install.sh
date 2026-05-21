#!/usr/bin/env bash
#
# install.sh — wire de-legal-toolkit skills into Claude Code.
#
# Idempotent. Safe to re-run after `git pull` (symlinks resolve to the latest files).
#
# What it does:
#   1. Creates toolkit-local symlinks at <toolkit>/.claude/skills/ for ALL skills.
#      → When Claude Code is opened in the toolkit, every skill is available.
#   2. Creates global symlinks at ~/.claude/skills/ for the audit / supporting skills.
#      → When Claude Code is opened in ANY project, those skills are available.
#      → `legal-research` is intentionally excluded — it only ever runs from
#        the toolkit, where it commits to findings/.
#
# Override the global path with: CLAUDE_GLOBAL_SKILLS=/some/other/path ./install.sh

set -euo pipefail

TOOLKIT="$(cd "$(dirname "$0")" && pwd)"
GLOBAL="${CLAUDE_GLOBAL_SKILLS:-$HOME/.claude/skills}"

LOCAL_SKILLS=(legal-research audit compliance-init defense)
GLOBAL_SKILLS=(audit compliance-init defense)

echo "Toolkit: $TOOLKIT"
echo "Global:  $GLOBAL"
echo ""

# Toolkit-local
mkdir -p "$TOOLKIT/.claude/skills"
echo "Toolkit-local symlinks (in $TOOLKIT/.claude/skills/):"
for skill in "${LOCAL_SKILLS[@]}"; do
  if [ -d "$TOOLKIT/skills/$skill" ]; then
    ln -sfn "../../skills/$skill" "$TOOLKIT/.claude/skills/$skill"
    echo "  ✓ $skill"
  else
    echo "  - $skill (not present in skills/ — skipping)"
  fi
done

echo ""

# Global
mkdir -p "$GLOBAL"
echo "Global symlinks (in $GLOBAL/):"
for skill in "${GLOBAL_SKILLS[@]}"; do
  if [ -d "$TOOLKIT/skills/$skill" ]; then
    ln -sfn "$TOOLKIT/skills/$skill" "$GLOBAL/$skill"
    echo "  ✓ $skill"
  else
    echo "  - $skill (not present in skills/ — skipping)"
  fi
done

echo ""
echo "Done."
echo ""
echo "Next steps:"
echo "  - From the toolkit:    Skill(legal-research) for case-law sweeps; commit findings."
echo "  - From any project:    Skill(compliance-init) to onboard, then Skill(audit) to run."
echo ""
echo "Uninstall with: ./uninstall.sh"
