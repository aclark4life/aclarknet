# WARP
Guidelines for using Warp and Agent Mode in this repository.

## Purpose
This document explains how to collaborate with Warp's Agent Mode when working in this project. It is meant to be short, practical, and repository-specific.

## How to use Agent Mode in this repo
- Ask the agent to **read files** before changing them.
- Prefer **small, incremental edits** over large refactors in a single step.
- When you ask for changes, be explicit about scope, for example:
  - "Update the README badges only."
  - "Add tests, but do not change existing function signatures."
- If the agent proposes a larger change, have it **outline a brief plan first**.

## Coding conventions
- Backend: Django / Wagtail (`manage.py`, multiple top-level Django apps)
- Python: >= 3.10 (see `pyproject.toml`)
- Packaging: `setuptools` with `pyproject.toml`
- Frontend: `frontend/` and other per-app static assets (not yet standardized here)
- Style: Prefer small, focused Django apps; keep settings and secrets out of version control; follow existing patterns in each app directory.

## Common commands
### Local development
- Install project in editable mode:
  - `just pip-install` (alias: `just i`)
- Run Django development server:
  - `just django-serve` (alias: `just s`)
- Open local site in browser:
  - `just django-open` (alias: `just o`)

### AWS Elastic Beanstalk / deployment
- Create a new EB environment (uses branch + git hash in the name):
  - `just eb-create`
- Deploy current code to EB:
  - `just eb-deploy` (alias: `just d`)
- Fetch EB logs:
  - `just eb-logs` (alias: `just l`)

### Database utilities
- From `Makefile`, dump the EB Postgres database locally:
  - `make pg-dump`

(If you add test or lint commands later, document them here.)

## Safety / constraints
- Do not touch CI configuration or deployment scripts (e.g. `buildspec.yml`, `Dockerfile`, `Procfile`) without explicit instruction.
- Do not modify historical database migrations; only create new ones when asked.
- Do not commit changes; the human developer will handle commits.
- Be careful with AWS/EB commands (`eb`, `aws`) – assume they target real infrastructure unless told otherwise.

## Repository structure
High-level layout:
- `backend/`, `blog/`, `home/`, `newsletter/`, `privacy/`, `resume/`, `search/`, `sitepage/`, `siteuser/`: Django/Wagtail apps.
- `frontend/`, `lounge/`: Frontend- or Node-related code.
- `manage.py`: Django entry point for management commands.
- `requirements.txt`, `requirements-test.txt`: Python dependencies.
- `pyproject.toml`: Packaging metadata and setuptools configuration.
- `justfile`: Convenience commands for dev, Django, and EB.
- `Makefile`: Database and EB-related utilities.

## Updating this file
As the project or your workflow with Warp evolves, update this file so future agent sessions behave as you expect.

When you add new commands (tests, linters, type checkers) or change deployment practices, please also update the relevant sections above.
