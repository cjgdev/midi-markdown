#!/usr/bin/env bash
# Cleanup merged worktrees and their branches
# Usage: ./.claude/scripts/cleanup-worktrees.sh [--dry-run]

set -euo pipefail

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

DRY_RUN=false
if [[ "${1:-}" == "--dry-run" ]]; then
    DRY_RUN=true
    echo -e "${YELLOW}Running in DRY RUN mode - no changes will be made${NC}"
    echo ""
fi

REPO_ROOT="$(git rev-parse --show-toplevel)"
cd "$REPO_ROOT"

echo -e "${BLUE}Checking for worktrees to cleanup...${NC}"
echo ""

# Get list of all worktrees except main
WORKTREES=$(git worktree list --porcelain | grep -E "^worktree " | grep -v "^worktree $REPO_ROOT$" | sed 's/^worktree //' || true)

if [ -z "$WORKTREES" ]; then
    echo -e "${GREEN}No additional worktrees found - nothing to cleanup${NC}"
    exit 0
fi

echo -e "${YELLOW}Found worktrees:${NC}"
git worktree list
echo ""

# Update main branch
echo -e "${BLUE}Fetching latest changes from origin...${NC}"
git fetch origin

CLEANED=0
SKIPPED=0

while IFS= read -r worktree; do
    # Get branch for this worktree
    BRANCH=$(git worktree list --porcelain | grep -A 2 "worktree $worktree" | grep "^branch " | sed 's/^branch refs\/heads\///' || echo "")

    if [ -z "$BRANCH" ]; then
        echo -e "${YELLOW}Skipping $worktree - no branch found${NC}"
        ((SKIPPED++))
        continue
    fi

    # Only process claude/* branches
    if [[ ! "$BRANCH" =~ ^claude/ ]]; then
        echo -e "${YELLOW}Skipping $worktree - not a claude/ branch: $BRANCH${NC}"
        ((SKIPPED++))
        continue
    fi

    # Check if branch exists on remote
    REMOTE_EXISTS=$(git ls-remote --heads origin "$BRANCH" | wc -l)

    if [ "$REMOTE_EXISTS" -eq 0 ]; then
        echo -e "${YELLOW}Branch $BRANCH not on remote - might not be pushed yet${NC}"
        echo -e "  Worktree: $worktree"
        ((SKIPPED++))
        continue
    fi

    # Check if branch is merged into main
    MERGED=$(git branch --merged origin/main | grep -E "^\*? *${BRANCH}$" | wc -l || true)

    if [ "$MERGED" -eq 1 ]; then
        echo -e "${GREEN}✓ Branch $BRANCH is merged${NC}"
        echo -e "  Worktree: $worktree"

        if [ "$DRY_RUN" = true ]; then
            echo -e "  ${BLUE}[DRY RUN] Would remove worktree: $worktree${NC}"
            echo -e "  ${BLUE}[DRY RUN] Would delete branch: $BRANCH${NC}"
        else
            echo -e "  Removing worktree..."
            if git worktree remove "$worktree"; then
                echo -e "  ${GREEN}✓ Worktree removed${NC}"
            else
                echo -e "  ${RED}✗ Failed to remove worktree${NC}"
                ((SKIPPED++))
                continue
            fi

            echo -e "  Deleting local branch..."
            if git branch -d "$BRANCH"; then
                echo -e "  ${GREEN}✓ Branch deleted${NC}"
            else
                echo -e "  ${RED}✗ Failed to delete branch (might need -D)${NC}"
            fi
        fi

        ((CLEANED++))
    else
        echo -e "${YELLOW}Branch $BRANCH is NOT merged into main${NC}"
        echo -e "  Worktree: $worktree"
        echo -e "  ${YELLOW}Skipping (use manual cleanup if needed)${NC}"
        ((SKIPPED++))
    fi

    echo ""
done <<< "$WORKTREES"

# Prune stale worktree references
echo -e "${BLUE}Pruning stale worktree references...${NC}"
if [ "$DRY_RUN" = true ]; then
    echo -e "${BLUE}[DRY RUN] Would run: git worktree prune${NC}"
else
    git worktree prune
    echo -e "${GREEN}✓ Pruned stale references${NC}"
fi
echo ""

# Summary
echo -e "${BLUE}Cleanup Summary:${NC}"
echo -e "  ${GREEN}Cleaned: $CLEANED${NC}"
echo -e "  ${YELLOW}Skipped: $SKIPPED${NC}"
echo ""

if [ "$DRY_RUN" = true ]; then
    echo -e "${YELLOW}This was a DRY RUN - no changes were made${NC}"
    echo -e "Run without --dry-run to actually cleanup"
else
    echo -e "${GREEN}Cleanup complete!${NC}"
fi

echo ""
echo -e "${BLUE}Current worktrees:${NC}"
git worktree list
