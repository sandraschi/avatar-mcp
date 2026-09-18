set windows-shell := ["powershell.exe", "-NoProfile", "-Command"]
import 'scripts/just/fleet.just'

# Open the interactive recipe dashboard in the browser
default:
    @just --list

# --- Quality ---

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

# --- Testing ---

# Run all Python tests with pytest
test:
    uv run pytest tests/ -v

# --- Hardening ---

# Execute Bandit security audit
check-sec:
    cd '{{justfile_directory()}}' && uv run bandit -r src/

# Execute safety audit of dependencies
audit-deps:
	cd '{{justfile_directory()}}' && uv run safety check

# --- Native  Tauri ---

# Build the Tauri NSIS desktop installer (full pipeline: frontend -> Rust -> NSIS)
build-native:
	$env:Path = "$env:USERPROFILE\.cargo\bin;$env:Path"; Set-Location '{{justfile_directory()}}\native'; pwsh -NoProfile -File '{{justfile_directory()}}\native\build.ps1'


# Bootstrap: install dev deps + pre-commit hook
bootstrap:
    uv sync --group dev
    uv run pre-commit install
    Write-Host "Pre-commit hooks installed." -ForegroundColor Green