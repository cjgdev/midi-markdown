# MIDI Markdown - Development Commands
# https://github.com/casey/just

# Default recipe - show available commands
default:
    @just --list

# Install dependencies and sync environment
install:
    uv sync

# Install pre-commit hooks
install-hooks:
    uv run pre-commit install

# Uninstall pre-commit hooks
uninstall-hooks:
    uv run pre-commit uninstall

# Run pre-commit on all files (manual run)
pre-commit:
    uv run pre-commit run --all-files

# Update pre-commit hooks to latest versions
update-hooks:
    uv run pre-commit autoupdate

# Run all tests
test:
    uv run pytest

# Run tests with verbose output
test-v:
    uv run pytest -v

# Run tests with coverage report
test-cov:
    uv run pytest --cov --cov-report=html --cov-report=term

# Run only unit tests
test-unit:
    uv run pytest tests/unit -v

# Run only integration tests
test-integration:
    uv run pytest tests/integration -v

# Run specific test file or pattern
test-file FILE:
    uv run pytest {{FILE}} -v

# Run tests matching a keyword expression
test-k KEYWORD:
    uv run pytest -k {{KEYWORD}} -v

# Run tests and stop on first failure
test-x:
    uv run pytest -x

# Run tests with extra verbose output and stop on first failure
test-xvs:
    uv run pytest -xvs

# Format code with ruff
fmt:
    uv run ruff format .

# Check code formatting without making changes
fmt-check:
    uv run ruff format --check .

# Lint code with ruff
lint:
    uv run ruff check .

# Lint and auto-fix issues
lint-fix:
    uv run ruff check --fix .

# Run type checking with mypy
typecheck:
    uv run mypy src

# Run all quality checks (format, lint, typecheck)
check: fmt-check lint typecheck

# Fix all auto-fixable issues (format + lint)
fix: fmt lint-fix

# Run the CLI (shows help)
run *ARGS:
    uv run mmdc {{ARGS}}

# Compile an MMD file
compile INPUT OUTPUT:
    uv run mmdc compile {{INPUT}} -o {{OUTPUT}}

# Validate an MMD file
validate FILE:
    uv run mmdc validate {{FILE}}

# Show version information
version:
    uv run mmdc version

# Clean build artifacts and cache
clean:
    rm -rf build/
    rm -rf dist/
    rm -rf *.egg-info
    rm -rf .pytest_cache/
    rm -rf .mypy_cache/
    rm -rf .ruff_cache/
    rm -rf htmlcov/
    rm -rf .coverage
    find . -type d -name __pycache__ -exec rm -rf {} +
    find . -type f -name "*.pyc" -delete

# Build Python package (wheels for PyPI)
build:
    uv build

# Build standalone executable for current platform (onedir mode - faster startup)
build-exe:
    @echo "Building standalone executable with PyInstaller..."
    uv sync --group build
    uv run pyinstaller mmdc.spec --clean --noconfirm
    @echo "\nExecutable built in: dist/mmdc/"
    @ls -lh dist/mmdc/

# Build standalone executable (onefile mode - single portable file)
build-exe-onefile:
    @echo "Building single-file executable with PyInstaller..."
    uv sync --group build
    uv run pyinstaller mmdc.spec --clean --noconfirm --onefile
    @echo "\nExecutable built: dist/mmdc"
    @ls -lh dist/mmdc

# Test the built executable with sample files
test-exe:
    @echo "Testing built executable..."
    @if [ -f dist/mmdc/mmdc ]; then \
        echo "Testing version command:"; \
        ./dist/mmdc/mmdc --version; \
        echo "\nTesting compilation:"; \
        ./dist/mmdc/mmdc compile $(pwd)/examples/00_basics/01_hello_world.mmd -o /tmp/test_exe_output.mid; \
        echo "\nVerifying output file:"; \
        ls -lh /tmp/test_exe_output.mid; \
    elif [ -f dist/mmdc.exe ]; then \
        echo "Testing version command:"; \
        ./dist/mmdc.exe --version; \
        echo "\nTesting compilation:"; \
        ./dist/mmdc.exe compile $(pwd)/examples/00_basics/01_hello_world.mmd -o /tmp/test_exe_output.mid; \
        echo "\nVerifying output file:"; \
        ls -lh /tmp/test_exe_output.mid; \
    else \
        echo "ERROR: Executable not found. Run 'just build-exe' first."; \
        exit 1; \
    fi

# Run example files to test compilation
examples:
    @echo "Compiling 00_hello_world.mmd..."
    uv run mmdc compile examples/00_basics/01_hello_world.mmd -o /tmp/hello_world.mid
    @echo "Compiling alias_showcase.mmd..."
    uv run mmdc compile examples/03_advanced/03_alias_showcase.mmd -o /tmp/alias_showcase.mid
    @echo "\nExamples compiled to /tmp/"
    @ls -lh /tmp/*.mid

# Run quick smoke test (fastest tests)
smoke:
    uv run pytest tests/unit/test_parser.py tests/integration/test_cli.py -v

# Run comprehensive test suite with coverage
ci: check test-cov

# Watch tests (requires pytest-watch: pip install pytest-watch)
watch:
    uv run ptw

# Generate coverage HTML report and open it
coverage:
    uv run pytest --cov --cov-report=html
    open htmlcov/index.html

# Run linter and show statistics
stats:
    @echo "Code statistics:"
    @echo "==============="
    @echo ""
    @echo "Lines of code:"
    @find src -name "*.py" | xargs wc -l | tail -1
    @echo ""
    @echo "Test coverage:"
    @uv run pytest --cov --cov-report=term | grep "TOTAL"
    @echo ""
    @echo "Linter issues:"
    @uv run ruff check . --statistics

# Run all device library parsing tests
test-devices:
    uv run pytest tests/integration/test_device_libraries.py -v

# Run E2E compilation tests
test-e2e:
    uv run pytest tests/integration/test_end_to_end.py -v

# Run tests for specific MIDI command
test-command CMD:
    uv run pytest -k {{CMD}} -v

# Benchmark/performance tests
bench:
    uv run pytest tests/integration/test_complex_documents.py::TestPerformance -v

# Update dependencies
update:
    uv lock --upgrade
    uv sync

# Show dependency tree
deps:
    uv tree

# Launch Python REPL with project loaded
repl:
    uv run python -i -c "from midi_markdown.parser.parser import MMLParser; from midi_markdown.midi.events import EventGenerator; from midi_markdown.midi.generator import MIDIGenerator; parser = MMLParser(); print('Parser loaded. Try: doc = parser.parse_file(\"examples/00_basics/01_hello_world.mmd\")')"

# Run formatter, linter, and tests in sequence
qa: fmt lint-fix test

# Show project info
info:
    @echo "MIDI Markup Language (MML)"
    @echo "=========================="
    @echo ""
    @echo "Version: $(uv run python -c 'from midi_markdown import __version__; print(__version__)')"
    @echo "Python: $(uv run python --version)"
    @echo ""
    @echo "Project structure:"
    @tree -L 2 -I '__pycache__|*.pyc|.git|.venv|htmlcov|.pytest_cache|.mypy_cache|.ruff_cache' || ls -R

# Validate all device library files
validate-devices:
    @echo "Validating device libraries..."
    @for file in devices/*.mmd; do \
        echo "Checking $file..."; \
        uv run mmdc validate "$file" || exit 1; \
    done
    @echo "All device libraries validated successfully!"

# Validate all example files
validate-examples:
    @echo "Validating example files..."
    @for file in examples/**/*.mmd; do \
        echo "Checking $file..."; \
        uv run mmdc validate "$file" || exit 1; \
    done
    @echo "All examples validated successfully!"

# Run all validations (devices + examples)
validate-all: validate-devices validate-examples

# Serve documentation locally with MkDocs
docs-serve:
    uv run mkdocs serve

# Build documentation site
docs-build:
    uv run mkdocs build

# Deploy documentation to GitHub Pages
docs-deploy:
    uv run mkdocs gh-deploy

# Clean documentation build artifacts
docs-clean:
    rm -rf site/

# ============================================
# Release Management
# ============================================

# Show current version
show-version:
    @echo "Current version: $(uv run python -c 'from midi_markdown import __version__; print(__version__)')"

# Run pre-release checks (comprehensive)
pre-release:
    @echo "Running pre-release checks..."
    @echo "\n1. Formatting check..."
    just fmt-check
    @echo "\n2. Linting..."
    just lint
    @echo "\n3. Type checking..."
    just typecheck
    @echo "\n4. Running tests with coverage..."
    just test-cov
    @echo "\n5. Validating device libraries..."
    just validate-devices
    @echo "\n6. Validating examples..."
    just validate-examples
    @echo "\n✅ All pre-release checks passed!"
    @echo "\nReady to release. Next steps:"
    @echo "  1. Review CHANGELOG.md [Unreleased] section"
    @echo "  2. Run: just release-patch (or release-minor/release-major)"

# Bump patch version (0.1.0 -> 0.1.1) and create tag
release-patch:
    @echo "Creating patch release..."
    uv run python scripts/bump_version.py patch

# Bump minor version (0.1.0 -> 0.2.0) and create tag
release-minor:
    @echo "Creating minor release..."
    uv run python scripts/bump_version.py minor

# Bump major version (0.1.0 -> 1.0.0) and create tag
release-major:
    @echo "Creating major release..."
    uv run python scripts/bump_version.py major

# Set specific version and create tag
release-version VERSION:
    @echo "Creating release for version {{VERSION}}..."
    uv run python scripts/bump_version.py {{VERSION}}

# Preview version bump (dry run)
release-preview TYPE:
    @echo "Previewing {{TYPE}} release..."
    uv run python scripts/bump_version.py {{TYPE}} --dry-run

# Push release tag to trigger GitHub Actions workflow
release-push:
    @echo "Pushing release tag..."
    @TAG=$(git describe --tags --abbrev=0) && \
    echo "Latest tag: $$TAG" && \
    read -p "Push $$TAG to origin? [y/N] " -n 1 -r && \
    echo && \
    if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
        echo "Pushing main branch..."; \
        git push origin main; \
        echo "Pushing tag $$TAG..."; \
        git push origin $$TAG; \
        echo "✅ Release pushed! Monitor at: https://github.com/cjgdev/midi-markdown/actions"; \
    else \
        echo "Aborted."; \
    fi

# Complete release workflow: checks -> bump -> push
release TYPE: pre-release
    @echo "\nAll checks passed. Creating {{TYPE}} release..."
    just release-{{TYPE}}
    @echo "\n✅ Release created! Review changes:"
    @git log -1 --stat
    @echo "\nTo push and trigger GitHub Actions:"
    @echo "  just release-push"

# ============================================
# Pull Request Management
# ============================================

# Create PR with filled template (interactive)
pr TITLE="":
    .github/scripts/create-pr-with-template.sh "{{TITLE}}"

# Create PR with filled template (auto, no prompts)
pr-auto TITLE="":
    .github/scripts/create-pr-with-template.sh "{{TITLE}}" --auto

# Generate filled PR template and save to file
pr-template OUTPUT="pr-template.md":
    .github/scripts/fill-pr-template.sh > {{OUTPUT}}
    @echo "PR template generated: {{OUTPUT}}"

# Show what would be in the PR template
pr-preview:
    @.github/scripts/fill-pr-template.sh
