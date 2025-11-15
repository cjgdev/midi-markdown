You are creating a GitHub pull request with the filled PR template.

Follow these steps:

1. **Analyze the changes**:
   - Run `git status` to see changed files
   - Run `git diff origin/$(git symbolic-ref refs/remotes/origin/HEAD | sed 's@^refs/remotes/origin/@@')..HEAD` to see all changes
   - Run `git log --oneline origin/$(git symbolic-ref refs/remotes/origin/HEAD | sed 's@^refs/remotes/origin/@@')..HEAD` to see commits

2. **Generate PR title and body**:
   - Use `.github/scripts/fill-pr-template.sh` to generate the filled template
   - Customize the title based on the changes
   - Fill in specific details in the template based on:
     * The actual changes made
     * Test results (check if tests were run)
     * Documentation updates
     * Breaking changes (if any)
     * Performance impact

3. **Create the PR**:
   - Use `gh pr create` with the filled template as the body
   - Use `--title` for a concise, descriptive title
   - Use `--body` with the filled template content
   - Format the body using a HEREDOC for proper formatting

4. **Example format**:
```bash
# Generate filled template
PR_BODY=$(.github/scripts/fill-pr-template.sh)

# Create PR with filled template
gh pr create --title "feat: Add new feature" --body "$(cat <<'EOF'
$PR_BODY
EOF
)"
```

5. **Customize these sections** based on the actual changes:
   - Description (summarize what the PR does)
   - Motivation (why the change is needed, link related issues)
   - Changes Made (specific files and modifications)
   - Test Coverage (what tests were added/updated)
   - Manual Testing (what you tested manually)
   - Breaking Changes (if applicable)
   - Performance Impact (if applicable)

6. **Important**:
   - DO NOT create the PR yet - first show the user the filled template
   - Ask if they want to customize any sections before creating
   - Only create the PR after user confirms

After generating the filled template, present it to the user and ask:
"I've generated a filled PR template based on your changes. Would you like me to:
1. Create the PR with this template as-is
2. Customize specific sections first
3. Show you the full template for review

What would you prefer?"
