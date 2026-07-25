Managing Dependencies with Renovate
====================================

This guide explains how automated dependency updates work in aclarknet
via Renovate, and what to do when a Renovate PR arrives.

Overview
--------

`Renovate <https://docs.renovatebot.com/>`_ is configured to
automatically open pull requests when Python or JavaScript dependencies
have new versions available. This keeps the project current without
manual scanning.

Configuration is in ``renovate.json`` at the project root.

Schedule
--------

Renovate runs on a **weekly schedule** — Monday before 6am ET. Expect
a batch of PRs early Monday morning when updates are available.

What Gets Updated
-----------------

- **Python packages** — defined in ``pyproject.toml``
- **npm packages** — defined in ``package.json``

Automerge vs. Manual Review
----------------------------

Most patch and minor updates are grouped and may be automerged if CI
passes. However, the following require **manual review** before merging:

- **Django** — major and minor upgrades can require migration changes,
  settings updates, or deprecation fixes.
- **Wagtail** — similarly complex; always review the Wagtail changelog
  before merging.

For any Renovate PR touching Django or Wagtail:

1. Read the relevant changelog/release notes.
2. Run migrations locally: ``just m``
3. Run tests: ``just t``
4. Check the admin and Wagtail interfaces manually.
5. Merge only if everything passes.

Merging a Routine Renovate PR
------------------------------

For non-Django/Wagtail updates:

1. Review the PR diff — confirm only version numbers changed.
2. Check CI passes (GitHub Actions).
3. Pull the branch locally and run ``just t`` if in doubt.
4. Merge and deploy with ``just deploy-remote`` (or ``just dpr``).

Skipping or Deferring an Update
---------------------------------

If a dependency update is not ready to merge, close the PR. Renovate
will re-open it on the next scheduled run. To permanently ignore a
package, add it to the ``ignoreDeps`` list in ``renovate.json``.
