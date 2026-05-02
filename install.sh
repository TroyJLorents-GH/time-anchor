#!/usr/bin/env bash
# time-anchor installer for Linux/macOS.
# One-liner:
#   curl -fsSL https://raw.githubusercontent.com/TroyJLorents-GH/time-anchor/main/install.sh | bash
#
# Downloads the latest main branch as a tarball over HTTPS (no git, no SSH),
# extracts to ~/.claude/skills/time-anchor and ~/.claude/commands/.

set -euo pipefail

REPO="TroyJLorents-GH/time-anchor"
BRANCH="main"
SKILL_DIR="${HOME}/.claude/skills/time-anchor"
COMMANDS_DIR="${HOME}/.claude/commands"
TMPDIR="$(mktemp -d)"
trap 'rm -rf "${TMPDIR}"' EXIT

echo "→ Downloading time-anchor from github.com/${REPO}..."
curl -fsSL "https://github.com/${REPO}/archive/refs/heads/${BRANCH}.tar.gz" \
    | tar -xz -C "${TMPDIR}"

EXTRACTED="${TMPDIR}/time-anchor-${BRANCH}"

echo "→ Installing skill to ${SKILL_DIR}"
mkdir -p "$(dirname "${SKILL_DIR}")"
rm -rf "${SKILL_DIR}"
cp -r "${EXTRACTED}/skills/time-anchor" "${SKILL_DIR}"

echo "→ Installing slash commands to ${COMMANDS_DIR}"
mkdir -p "${COMMANDS_DIR}"
cp "${EXTRACTED}"/commands/*.md "${COMMANDS_DIR}/"

echo ""
echo "✓ time-anchor installed."
echo ""
echo "Restart Claude Code, then try:"
echo "  /current-time"
echo "  /set-timezone"
echo ""
echo "Memory file: ${SKILL_DIR}/memory.json (created on first use)"
