# Release Checklist

Use this checklist when preparing a new release of MIDI Markdown.

**Version:** _____________ (e.g., 0.2.0)
**Release Date:** _____________ (YYYY-MM-DD)
**Release Type:** [ ] Patch  [ ] Minor  [ ] Major

---

## Pre-Release

### Code Quality
- [ ] All tests pass locally: `just test`
- [ ] Code is formatted: `just fmt-check`
- [ ] No linting errors: `just lint`
- [ ] Type checking passes: `just typecheck`
- [ ] Coverage maintained/improved: `just test-cov`
- [ ] Run full check: `just pre-release`

### Documentation
- [ ] CHANGELOG.md updated with all changes in `[Unreleased]` section
- [ ] All changes categorized (Added, Changed, Deprecated, Removed, Fixed, Security)
- [ ] README.md is current and accurate
- [ ] User guides updated for new features
- [ ] Developer guides updated if architecture changed
- [ ] API documentation up-to-date
- [ ] Documentation builds without errors: `just docs-build`

### Examples and Validation
- [ ] All examples compile: `just validate-examples`
- [ ] Device libraries validate: `just validate-devices`
- [ ] New features have example files in `examples/`
- [ ] Example README.md updated with new examples

### Repository State
- [ ] All changes committed to main branch
- [ ] Branch is up-to-date: `git pull origin main`
- [ ] No uncommitted changes: `git status`
- [ ] CI/CD passes on GitHub Actions
- [ ] No open critical bugs blocking release

### Version Planning
- [ ] Reviewed all changes since last release
- [ ] Version number chosen (follows SemVer)
- [ ] Breaking changes documented (if major release)
- [ ] Deprecation warnings added (if removing features)

---

## Release Process

### Version Bump
- [ ] Run version bump script:
  ```bash
  just release-patch    # or release-minor / release-major
  ```
- [ ] Review git commit created by script
- [ ] Review git tag created: `git tag -l`
- [ ] Verify pyproject.toml version updated
- [ ] Verify __init__.py version updated
- [ ] Verify CHANGELOG.md updated

### Push to GitHub
- [ ] Push commits and tag:
  ```bash
  just release-push
  ```
  Or manually:
  ```bash
  git push origin main
  git push origin vX.Y.Z
  ```

### Monitor CI/CD
- [ ] GitHub Actions workflow triggered
- [ ] Monitor build progress: [Actions](https://github.com/cjgdev/midi-markdown/actions)
- [ ] Linux executable builds successfully
- [ ] Windows executable builds successfully
- [ ] macOS executable builds successfully
- [ ] GitHub Release created automatically
- [ ] All artifacts uploaded to release

**Build Time:** Approximately 15-20 minutes

---

## Post-Release

### Verification
- [ ] GitHub Release published: [Releases](https://github.com/cjgdev/midi-markdown/releases)
- [ ] Release notes look correct
- [ ] All executables attached to release:
  - [ ] `mmdc-linux-x86_64.tar.gz` + `.sha256`
  - [ ] `mmdc-windows-x86_64.zip` + `.sha256`
  - [ ] `mmdc-macos-universal.zip` + `.sha256`
- [ ] Downloaded and tested one executable:
  ```bash
  ./mmdc --version
  ./mmdc compile examples/00_basics/00_hello_world.mmd -o test.mid
  ```
- [ ] Checksums verified

### PyPI Publishing (Optional)
- [ ] Built distributions: `just build`
- [ ] Uploaded to TestPyPI: `twine upload --repository testpypi dist/*`
- [ ] Tested installation from TestPyPI
- [ ] Uploaded to PyPI: `twine upload dist/*`
- [ ] Verified on PyPI: https://pypi.org/project/midi-markdown/

### Communication
- [ ] Announcement posted in GitHub Discussions (if enabled)
- [ ] Release notes shared with community
- [ ] Documentation site updated (if separate)
- [ ] Social media announcement (optional)

### Monitoring
- [ ] Watch for bug reports in Issues
- [ ] Respond to installation problems
- [ ] Monitor for platform-specific issues

---

## Rollback Plan (If Needed)

If critical issues are found after release:

### Option 1: Hotfix Release
1. Create hotfix branch: `git checkout -b hotfix/vX.Y.Z v{previous}`
2. Fix the issue
3. Bump patch version: `just release-patch`
4. Follow normal release process

### Option 2: Yank Release (PyPI only)
```bash
# Mark version as yanked on PyPI
pip install --upgrade twine
twine upload --skip-existing --repository pypi dist/*
# Then manually yank in PyPI web interface
```

### Option 3: Delete Release (GitHub)
1. Go to: https://github.com/cjgdev/midi-markdown/releases
2. Edit the problematic release
3. Delete the release (keeps the tag)
4. Delete tag: `git push origin :refs/tags/vX.Y.Z`

---

## Notes

**Problems encountered:**


**Lessons learned:**


**Future improvements:**


---

**Completed by:** _____________
**Date:** _____________
**Release URL:** https://github.com/cjgdev/midi-markdown/releases/tag/vX.Y.Z
