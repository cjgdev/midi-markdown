#!/usr/bin/env bash
# create-pr-with-template.sh - Create a PR with filled template

set -euo pipefail

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check if gh CLI is installed
if ! command -v gh &> /dev/null; then
    echo -e "${RED}Error: GitHub CLI (gh) is not installed${NC}"
    echo "Install it from: https://cli.github.com/"
    exit 1
fi

# Check if we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo -e "${RED}Error: Not in a git repository${NC}"
    exit 1
fi

# Get current branch
CURRENT_BRANCH=$(git branch --show-current)
echo -e "${BLUE}Current branch: ${CURRENT_BRANCH}${NC}"

# Check if branch has upstream
if ! git rev-parse --abbrev-ref --symbolic-full-name @{u} > /dev/null 2>&1; then
    echo -e "${YELLOW}Warning: Current branch has no upstream. Pushing...${NC}"
    git push -u origin "$CURRENT_BRANCH"
fi

# Get PR title (can be overridden with first argument)
if [ $# -ge 1 ]; then
    PR_TITLE="$1"
else
    # Auto-generate from branch name
    if [[ $CURRENT_BRANCH =~ ^(feature|fix|docs|refactor|perf|test|chore)/(.+)$ ]]; then
        TYPE="${BASH_REMATCH[1]}"
        DESC="${BASH_REMATCH[2]}"
        DESC=$(echo "$DESC" | tr '_-' ' ' | sed 's/\b\w/\u&/g')
        PR_TITLE="${TYPE}: $DESC"
    else
        PR_TITLE=$(git log -1 --pretty=format:"%s")
    fi
fi

echo -e "${BLUE}PR Title: ${PR_TITLE}${NC}"
echo ""

# Generate filled template
echo -e "${BLUE}Generating filled PR template...${NC}"
PR_BODY=$("$SCRIPT_DIR/fill-pr-template.sh" "$PR_TITLE")

# Save to temp file for editing
TEMP_FILE=$(mktemp)
echo "$PR_BODY" > "$TEMP_FILE"

echo -e "${GREEN}Template generated!${NC}"
echo ""
echo -e "${YELLOW}Options:${NC}"
echo "  1. Create PR with auto-filled template"
echo "  2. Edit template before creating PR"
echo "  3. Show template and exit"
echo ""

# If --auto flag is passed, skip interactive prompt
if [[ "${2:-}" == "--auto" ]]; then
    CHOICE=1
else
    read -p "Choose option [1-3]: " CHOICE
fi

case $CHOICE in
    1)
        echo -e "${BLUE}Creating PR...${NC}"
        gh pr create --title "$PR_TITLE" --body-file "$TEMP_FILE"
        ;;
    2)
        ${EDITOR:-nano} "$TEMP_FILE"
        echo -e "${BLUE}Creating PR with edited template...${NC}"
        gh pr create --title "$PR_TITLE" --body-file "$TEMP_FILE"
        ;;
    3)
        echo -e "${BLUE}PR Template:${NC}"
        echo "---"
        cat "$TEMP_FILE"
        echo "---"
        echo -e "${YELLOW}Template saved to: ${TEMP_FILE}${NC}"
        echo "To create PR manually: gh pr create --title \"$PR_TITLE\" --body-file \"$TEMP_FILE\""
        exit 0
        ;;
    *)
        echo -e "${RED}Invalid option${NC}"
        rm -f "$TEMP_FILE"
        exit 1
        ;;
esac

# Cleanup
rm -f "$TEMP_FILE"

echo -e "${GREEN}Done!${NC}"
