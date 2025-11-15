#!/usr/bin/env bash
# Create a new git worktree for Claude Code development
# Usage: ./.claude/scripts/create-worktree.sh <feature-name>

set -euo pipefail

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if feature name is provided
if [ $# -eq 0 ]; then
    echo -e "${RED}Error: Feature name required${NC}"
    echo "Usage: $0 <feature-name>"
    echo ""
    echo "Examples:"
    echo "  $0 add-looper-support"
    echo "  $0 fix-timing-bug"
    echo "  $0 update-h90-library"
    exit 1
fi

FEATURE_NAME="$1"
REPO_ROOT="$(git rev-parse --show-toplevel)"
REPO_NAME="$(basename "$REPO_ROOT")"

# Generate session ID (simple timestamp-based)
SESSION_ID="$(date +%s | base64 | head -c 22)"

# Create branch name with claude/ prefix
BRANCH_NAME="claude/${FEATURE_NAME}-${SESSION_ID}"

# Create worktree directory (sibling to main repo)
WORKTREE_DIR="${REPO_ROOT}/../${REPO_NAME}-${FEATURE_NAME}"

echo -e "${BLUE}Creating worktree for feature: ${FEATURE_NAME}${NC}"
echo ""
echo -e "  ${GREEN}Branch:${NC} ${BRANCH_NAME}"
echo -e "  ${GREEN}Directory:${NC} ${WORKTREE_DIR}"
echo ""

# Check if directory already exists
if [ -d "$WORKTREE_DIR" ]; then
    echo -e "${RED}Error: Directory already exists: ${WORKTREE_DIR}${NC}"
    echo "Remove it first or choose a different feature name"
    exit 1
fi

# Ensure we're in the main repository
cd "$REPO_ROOT"

# Fetch latest changes
echo -e "${BLUE}Fetching latest changes...${NC}"
git fetch origin

# Create the worktree
echo -e "${BLUE}Creating worktree...${NC}"
git worktree add "$WORKTREE_DIR" -b "$BRANCH_NAME"

echo ""
echo -e "${GREEN}✓ Worktree created successfully!${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo ""
echo "  1. Navigate to the worktree:"
echo "     ${BLUE}cd ${WORKTREE_DIR}${NC}"
echo ""
echo "  2. Start Claude Code in this directory"
echo ""
echo "  3. When ready to create PR, use:"
echo "     ${BLUE}git push -u origin ${BRANCH_NAME}${NC}"
echo "     ${BLUE}gh pr create --title \"<title>\" --body \"<description>\"${NC}"
echo ""
echo "  4. After PR is merged, cleanup with:"
echo "     ${BLUE}cd ${REPO_ROOT}${NC}"
echo "     ${BLUE}git worktree remove ${WORKTREE_DIR}${NC}"
echo "     ${BLUE}git branch -d ${BRANCH_NAME}${NC}"
echo ""
echo -e "${YELLOW}Active worktrees:${NC}"
git worktree list
