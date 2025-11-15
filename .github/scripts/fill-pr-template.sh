#!/usr/bin/env bash
# fill-pr-template.sh - Generate a filled PR template based on git changes

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to extract PR title from branch name or git log
get_pr_title() {
    local branch_name=$(git branch --show-current)

    # If branch follows pattern like "feature/add-xyz" or "fix/bug-123"
    if [[ $branch_name =~ ^(feature|fix|docs|refactor|perf|test|chore)/(.+)$ ]]; then
        local type="${BASH_REMATCH[1]}"
        local desc="${BASH_REMATCH[2]}"
        # Convert hyphens/underscores to spaces and capitalize
        desc=$(echo "$desc" | tr '_-' ' ' | sed 's/\b\w/\u&/g')
        echo "${type^}: $desc"
    else
        # Fall back to latest commit message
        git log -1 --pretty=format:"%s"
    fi
}

# Function to get base branch name
get_base_branch() {
    # Try to get default branch from origin/HEAD
    local base_branch=$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@')

    # If that fails, try common branch names
    if [ -z "$base_branch" ]; then
        for branch in main master develop; do
            if git rev-parse "origin/$branch" >/dev/null 2>&1; then
                base_branch="$branch"
                break
            fi
        done
    fi

    # Default to main if nothing found
    echo "${base_branch:-main}"
}

# Function to get description from recent commits
get_description() {
    echo "<!-- Provide a clear and concise summary of what this PR does -->"
    echo ""
    echo "## Summary"
    echo ""
    # Get commit messages since divergence from main/master
    local base_branch=$(get_base_branch)
    if git rev-parse "origin/$base_branch" >/dev/null 2>&1; then
        echo "This PR includes the following changes:"
        echo ""
        git log --reverse --pretty=format:"- %s" "origin/$base_branch..HEAD" 2>/dev/null | head -10
    else
        git log -1 --pretty=format:"%b"
    fi
}

# Function to detect change type from branch name and git diff
detect_change_type() {
    local branch_name=$(git branch --show-current)
    local base_branch=$(get_base_branch)
    local changed_files=$(git diff --name-only HEAD "origin/$base_branch" 2>/dev/null || git diff --name-only HEAD~1 2>/dev/null || echo "")

    # Initialize all as unchecked
    local bug_fix="- [ ]"
    local new_feature="- [ ]"
    local breaking_change="- [ ]"
    local documentation="- [ ]"
    local performance="- [ ]"
    local refactoring="- [ ]"
    local test_improvements="- [ ]"
    local ci_cd="- [ ]"
    local build_tooling="- [ ]"

    # Detect from branch name
    if [[ $branch_name =~ ^fix/ ]] || [[ $branch_name =~ bug ]]; then
        bug_fix="- [x]"
    elif [[ $branch_name =~ ^feature/ ]] || [[ $branch_name =~ ^feat/ ]]; then
        new_feature="- [x]"
    elif [[ $branch_name =~ ^docs/ ]]; then
        documentation="- [x]"
    elif [[ $branch_name =~ ^refactor/ ]]; then
        refactoring="- [x]"
    elif [[ $branch_name =~ ^perf/ ]]; then
        performance="- [x]"
    elif [[ $branch_name =~ ^test/ ]]; then
        test_improvements="- [x]"
    fi

    # Detect from changed files
    if echo "$changed_files" | grep -q "^docs/"; then
        documentation="- [x]"
    fi
    if echo "$changed_files" | grep -q "^tests/"; then
        test_improvements="- [x]"
    fi
    if echo "$changed_files" | grep -q "^.github/workflows/"; then
        ci_cd="- [x]"
    fi
    if echo "$changed_files" | grep -qE "^(justfile|pyproject.toml|setup.py|requirements.*\.txt)"; then
        build_tooling="- [x]"
    fi

    cat <<EOF
$bug_fix Bug fix (non-breaking change that fixes an issue)
$new_feature New feature (non-breaking change that adds functionality)
$breaking_change Breaking change (fix or feature that would cause existing functionality to not work as expected)
$documentation Documentation update
$performance Performance improvement
$refactoring Code refactoring (no functional changes)
$test_improvements Test improvements
$ci_cd CI/CD improvements
$build_tooling Build/tooling changes
EOF
}

# Function to list key changes
list_changes() {
    echo "<!-- List the key changes in this PR. Be specific and concise. -->"
    echo ""
    local base_branch=$(get_base_branch)
    if git rev-parse "origin/$base_branch" >/dev/null 2>&1; then
        git diff --stat "origin/$base_branch..HEAD" 2>/dev/null | head -20
        echo ""
        echo "### Files Changed"
        git diff --name-status "origin/$base_branch..HEAD" 2>/dev/null | head -20
    else
        git diff --stat HEAD~1 2>/dev/null | head -20
    fi
}

# Function to detect test changes
detect_test_changes() {
    local base_branch=$(get_base_branch)
    local changed_files=$(git diff --name-only HEAD "origin/$base_branch" 2>/dev/null || git diff --name-only HEAD~1 2>/dev/null || echo "")

    local unit_tests="- [ ]"
    local integration_tests="- [ ]"
    local e2e_tests="- [ ]"
    local all_pass="- [ ]"
    local no_decrease="- [ ]"

    if echo "$changed_files" | grep -q "^tests/.*test.*\.py"; then
        unit_tests="- [x]"
        all_pass="- [x]"
        no_decrease="- [x]"
    fi
    if echo "$changed_files" | grep -q "^tests/integration/"; then
        integration_tests="- [x]"
    fi
    if echo "$changed_files" | grep -q "^tests/e2e/"; then
        e2e_tests="- [x]"
    fi

    cat <<EOF
$unit_tests Unit tests added/updated
$integration_tests Integration tests added/updated
$e2e_tests E2E tests added/updated (if applicable)
$all_pass All tests pass locally (\`just test\` or \`uv run pytest\`)
$no_decrease No test coverage decrease (or justified if decreased)
EOF
}

# Function to detect documentation changes
detect_doc_changes() {
    local base_branch=$(get_base_branch)
    local changed_files=$(git diff --name-only HEAD "origin/$base_branch" 2>/dev/null || git diff --name-only HEAD~1 2>/dev/null || echo "")

    local docstrings="- [ ]"
    local type_hints="- [ ]"
    local cli_help="- [ ]"
    local user_docs="- [ ]"
    local examples="- [ ]"
    local changelog="- [ ]"
    local readme="- [ ]"

    if echo "$changed_files" | grep -qE "^src/.*\.py$"; then
        docstrings="- [x]"
        type_hints="- [x]"
    fi
    if echo "$changed_files" | grep -q "^src/midi_markdown/cli/"; then
        cli_help="- [x]"
    fi
    if echo "$changed_files" | grep -q "^docs/"; then
        user_docs="- [x]"
    fi
    if echo "$changed_files" | grep -q "^examples/"; then
        examples="- [x]"
    fi
    if echo "$changed_files" | grep -q "^CHANGELOG\.md"; then
        changelog="- [x]"
    fi
    if echo "$changed_files" | grep -q "^README\.md"; then
        readme="- [x]"
    fi

    cat <<EOF
$docstrings Code docstrings added/updated
$type_hints Type hints added for all new functions/methods
$cli_help CLI help text updated (if CLI changes made)
$user_docs User documentation updated in \`docs/\` (if applicable)
$examples Examples added/updated in \`examples/\` (if applicable)
$changelog CHANGELOG.md updated (required for notable changes)
$readme README.md updated (if applicable)
EOF
}

# Main function to generate PR template
generate_pr_template() {
    local pr_title="${1:-$(get_pr_title)}"

    cat <<EOF
## Description

$(get_description)

## Motivation

<!-- Why is this change needed? What problem does it solve? -->
<!-- Link to related issues using: Closes #123, Fixes #456, Resolves #789 -->


## Type of Change

<!-- Mark all applicable options with an 'x' -->

$(detect_change_type)

## Changes Made

$(list_changes)

## Testing

<!-- Describe how you tested these changes -->

### Test Coverage

$(detect_test_changes)

**Coverage change**: <!-- e.g., 72.53% → 75.20% (+2.67%) or "no change" -->

### Manual Testing

<!-- Describe what manual testing you performed -->

**Test commands run**:
\`\`\`bash
just test
just lint
just typecheck
\`\`\`

**Test scenarios**:
<!-- List specific scenarios you tested -->
-
-

## Documentation

<!-- Check all applicable items -->

$(detect_doc_changes)

## Code Quality

<!-- Ensure your code meets quality standards -->

- [x] Code follows project style guidelines (\`just fmt\` or \`uv run ruff format .\`)
- [x] Linting passes with no warnings (\`just lint\` or \`uv run ruff check .\`)
- [x] Type checking passes (\`just typecheck\` or \`uv run mypy src\`)
- [ ] No new compiler warnings or errors
- [ ] Error messages are clear and actionable
- [ ] Performance impact assessed (if applicable)
- [ ] Security implications considered (if applicable)

**Style checks run**:
\`\`\`bash
just check  # runs fmt + lint + typecheck
\`\`\`

## Pre-submission Checklist

<!-- Complete all items before requesting review -->

- [ ] I have read [CONTRIBUTING.md](../CONTRIBUTING.md)
- [ ] My code follows the project's architecture and design patterns
- [ ] I have performed a self-review of my code
- [ ] I have commented complex/non-obvious code sections
- [ ] My changes generate no new warnings or errors
- [ ] I have added tests that prove my fix/feature works
- [ ] New and existing unit tests pass locally
- [ ] Any dependent changes have been merged and published
- [ ] I have checked my code for security vulnerabilities
- [ ] I have verified backwards compatibility (or documented breaking changes)

## Breaking Changes

<!-- If this PR includes breaking changes, describe them here -->
<!-- Update CHANGELOG.md with migration guide if needed -->

**Breaking changes**: None

## Performance Impact

<!-- If this PR affects performance, provide details -->

**Performance impact**: None

## Screenshots / Output Examples

<!-- Add screenshots for UI changes or CLI output examples -->

### Before
\`\`\`
<!-- Example output before changes -->
\`\`\`

### After
\`\`\`
<!-- Example output after changes -->
\`\`\`

## Additional Context

<!-- Any additional information, links, design decisions, or context -->
<!-- Link to related PRs, external documentation, or discussion threads -->


## Dependencies

<!-- List any new dependencies added or dependency version changes -->

**New dependencies**: None

## Deployment Notes

<!-- Any special deployment considerations? -->
<!-- Required database migrations, config changes, etc. -->

**Deployment notes**: None

## Reviewer Notes

<!-- Anything specific you want reviewers to focus on? -->
<!-- Areas where you're unsure or want specific feedback? -->

**Focus areas for review**:
-
-

**Questions for reviewers**:
-
-

---

<!--
Thank you for contributing to MIDI Markdown!
Your effort helps make this project better for everyone.
-->
EOF
}

# Run the script
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    generate_pr_template "$@"
fi
