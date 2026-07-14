set windows-shell := ["pwsh.exe", "-NoLogo", "-Command"]
import 'scripts/just/fleet.just'

# Open the interactive recipe dashboard in the browser
default:
    @just --list

# ── Quality ───────────────────────────────────────────────────────────────────

# Execute Ruff linting (Python)
lint-py:
    uv run ruff check .

# Execute Biome linting (Frontend)
lint-web:
    uv run --directory web_sota npx @biomejs/biome check .

# Global lint (Python + Web)
lint: lint-py lint-web

# Execute Ruff fix and formatting
fix:
    uv run ruff check . --fix --unsafe-fixes
    uv run ruff format .
    uv run --directory web_sota npx @biomejs/biome check --apply .
    uv run --directory web_sota npx @biomejs/biome format --write .

# ── Testing ───────────────────────────────────────────────────────────────────

# Run all Python tests with pytest
test:
    uv run pytest tests/ -v

# ── Hardening ─────────────────────────────────────────────────────────────────

# Execute Bandit security audit
check-sec:
    cd '{{justfile_directory()}}' && uv run bandit -r src/

# Execute safety audit of dependencies
audit-deps:
    cd '{{justfile_directory()}}' && uv run safety check
