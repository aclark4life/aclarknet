# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Tech stack and high-level architecture

- **Backend**
  - Django project in the `aclarknet` package, configured for **MongoDB** via `django_mongodb_backend`.
  - Core settings live in `aclarknet/settings/base.py`; the `aclarknet/settings/aclarknet.py` module imports `base` and then:
    - Adds Mongo-aware app configs from `aclarknet.apps` (custom `Admin/Auth/ContentTypes/Sites` configs that default to `ObjectIdAutoField`).
    - Registers the `db` app.
    - Sets `SITE_ID` to a MongoDB `ObjectId` and silences the default `sites` system check.
  - `DATABASES["default"]` is a MongoDB database named `aclarknet`, with the connection string taken from the `MONGODB_URI` environment variable.
  - Debug tooling is enabled via `django-debug-toolbar` and `django_mongodb_extensions` (MQL panel) and wired into `aclarknet/urls.py` using `debug_toolbar_urls()`.
  - Future/optional **Queryable Encryption** support is scaffolded in `aclarknet/settings/aclarknet.py` and `aclarknet/routers.py` (currently commented out). The `EncryptedRouter` routes reads/writes & migrations between `default` and an `encrypted` database based on whether a model has encrypted fields.

- **Domain app (`db`)**
  - `db/models.py` implements a small **time-tracking and invoicing** domain:
    - `Company`, `Client`, `Project` (with derived `total_hours`, `total_revenue`, `total_cost`, `profit`), `Task`, `Invoice`, `Time`, and `Employee` (linked one-to-one to `AUTH_USER_MODEL`).
    - `Time.cost` calculates cost preferentially from the attached `Employee.hourly_rate` or falls back to the `Task.hourly_rate`.
  - `db/admin.py` builds a MongoDB-backed **Django admin UI** around these models:
    - Rich inlines linking Companies → Clients → Projects → Invoices → Time entries.
    - Aggregated financial metrics on `InvoiceAdmin` (`total_time`, `total_amount`, `total_cost`, `total_revenue`, `profit`) using annotated querysets.
    - A PDF-export workflow (via `reportlab`) that can export one or many invoices, with a custom change-form button and custom admin URL.

- **Frontend**
  - Frontend assets live under `frontend/` and are built with **webpack 5** using the `python-webpack-boilerplate` template.
  - Entry points:
    - `frontend/webpack/webpack.common.js` scans `frontend/src/application/*.js` and turns each file into a bundle entry.
    - The primary JS entry is `frontend/src/application/app.js`, which:
      - Imports global styles from `frontend/src/styles/index.scss` (Bootstrap-based).
      - Initializes the `Jumbotron` component (`frontend/src/components/jumbotron.js`) on elements matching `[data-jumbotron]` after `DOMContentLoaded`.
  - Bundles are written to `frontend/build` and exposed to Django via:
    - `STATICFILES_DIRS = [frontend_dir / "frontend/build"]` and `WEBPACK_LOADER["MANIFEST_FILE"]` in `aclarknet/settings/base.py`.
    - Templates can reference JS bundles using the `webpack_boilerplate` integration (see `frontend/src/application/README.md`).
  - `frontend/webpack/webpack.config.dev.js` runs a webpack dev server on **http://localhost:9091** with hot-reload, writes assets to disk, and wires in **ESLint** and **Stylelint** via plugins, so JS/SCSS linting happens automatically while the dev server runs.

## Settings and environment

- **Settings modules**
  - `manage.py` uses `DJANGO_SETTINGS_MODULE=aclarknet.settings.aclarknet` for runtime (includes `db` and `MongoDBSitesConfig`).
  - `pyproject.toml` configures pytest with `DJANGO_SETTINGS_MODULE=aclarknet.settings.base`.
  - When writing tests that rely on the `db` app or the Sites framework, be mindful of this difference; you may need to adjust the pytest setting or ensure the test settings import from `aclarknet` instead of `base`.

- **Database configuration**
  - MongoDB connection string is read from `MONGODB_URI` in the environment.
  - Default database name is `aclarknet`; optional encrypted database configuration is scaffolded (but commented out) in `aclarknet/settings/aclarknet.py` and routed by `aclarknet.routers.EncryptedRouter`.

- **Static assets and webpack**
  - Webpack builds to `frontend/build`; Django serves these via `STATICFILES_DIRS` and `WEBPACK_LOADER["MANIFEST_FILE"]`.
  - The webpack manifest is used to map logical entry names (e.g. `app`) to hashed asset filenames.

## Commands and workflows

### Installation and environment

- **Python dependencies (editable install)**
  - Use the Justfile recipe to install backend dependencies into the active Python environment:
    - `just pip-install` (alias: `just i`)

- **Node dependencies**
  - From the repo root, use the Justfile task or run the commands directly:
    - `just npm-install`
    - or: `cd frontend && npm install`

### Running the app in development

- **Full stack dev (recommended)**
  - Spin up webpack (watch mode) and the Django dev server together:
    - `just serve`
    - or: `just s`
  - This runs `npm-install`, `npm run watch` inside `frontend/`, and `python manage.py runserver`.

- **Django-only commands** (from repo root)
  - Run the development server:
    - `just django-serve`
  - Apply migrations:
    - `just django-migrate` (alias: `just m`)
  - Open the dev server in a browser:
    - `just django-open` (alias: `just o`)
  - Create a superuser with a predefined password (for local dev only):
    - `just django-su` (alias: `just su`)

- **Frontend-only commands** (from `frontend/`)
  - Start webpack dev server with live reload and linting (port 9091):
    - `npm run start`
  - Run webpack in watch mode (no dev server; emits bundles to `frontend/build`):
    - `npm run watch`
  - Build production assets (minified bundles and manifest):
    - `npm run build`

### Testing

- **Test runner**
  - Tests are configured to use **pytest** with Django integration via `pyproject.toml`.
  - From the repo root, run all tests:
    - `pytest`

- **Running a single test**
  - Target a specific test module:
    - `pytest db/tests.py`
  - Target a specific test case or method:
    - `pytest db/tests.py::SomeTestCase::test_scenario`

### Linting and formatting

- **Pre-commit**
  - This repo is configured with **pre-commit** hooks in `.pre-commit-config.yaml`, including:
    - Core hygiene hooks (trailing whitespace, EOF fixer, YAML checks, large file checks).
    - Python linting and formatting via **Ruff** (`ruff` and `ruff-format` hooks).
    - HTML formatting via **djhtml`** for a specific template path.
  - Typical usage:
    - Install hooks (once per clone): `pre-commit install`
    - Run all hooks on the full codebase: `pre-commit run --all-files`

- **Python linting/formatting directly**
  - If `ruff` is available in your environment (it is listed as a dev dependency):
    - Lint: `ruff check .`
    - Format: `ruff format`

- **Frontend linting**
  - ESLint and Stylelint are wired into the webpack dev configuration via `ESLintPlugin` and `StylelintPlugin`:
    - Running `npm run start` will automatically lint JS and SCSS under `frontend/src` as part of the dev build.

## Additional notes for agents

- The domain logic for billing, costs, and profits is split between `db/models.py` (per-object properties on `Project` and `Time`) and `db/admin.py` (queryset-level aggregations and PDF export). When changing the finance model, check both places to keep derived values consistent.
- MongoDB-specific behavior is centralized in `aclarknet/apps.py`, `aclarknet/settings/*`, and `aclarknet/routers.py`. Prefer extending these modules when you need new Mongo-aware apps, routers, or encrypted database behavior.
