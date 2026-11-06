# Contributing to avatar-mcp

Small fleet repo, one maintainer plus collaborators, zero patience for process theatre. These rules exist so your contribution gets merged instead of stalled.

## Issues first

- **Search before you file.** Duplicates get closed.
- **One issue, one request.** Two features = two issues.
- **Bug reports need the reproducer**: the avatar tool called, its operation and params, plus the exact error or receipt text. Without those, most reports cannot be reproduced.
- **Feature requests need a use case**: which avatar setup you are driving, doing what?

## Pull requests

- **File the issue first** (unless it's a trivial fix: typo, broken link, lint). The issue is where scope gets agreed before code exists.
- **Keep diffs small.** One concern per PR. Max 5 files per commit.
- **Tests required.** New behavior without a test is a draft, not a PR. Run `uv run pytest tests -q` before pushing.
- **Lint green:** `uv run ruff check src tests`.
- **The maintainer merges.** Don't merge your own PR.

## Avatar rules: the hard parts

- **Portmanteau tools use `operation` enums** — one tool per domain (avatar management, animation, bone control), not dozens of single-purpose tools.
- **No stubs presented as implementations.** Unfinished code is explicit, never plausible-looking filler.
- **Timestamped `.bak` before any edit touching 3+ files.** Cleanup when satisfied.
- **No em dashes anywhere** (Unicode safety). ASCII prose.

## What this repo never does

- **No live VRChat/OSC endpoints in tests.** Mock the OSC boundary; live verification is manual + documented.
- **No hardcoded secrets or tokens**, in code or examples. Keys come from env, always optional.
- **No fake avatar state.** No bone or morph data invented from memory — device output or honest empty, never filler.

Issue forms: [.github/ISSUE_TEMPLATE/](.github/ISSUE_TEMPLATE/) (bug report, feature request).
