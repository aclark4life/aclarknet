Managing Dependencies with Dependabot
======================================

This guide explains how automated dependency updates work in aclarknet
via GitHub Dependabot, and what to do when a Dependabot PR arrives.

Overview
--------

`Dependabot <https://docs.github.com/en/code-security/dependabot>`_ is
configured to automatically open pull requests when Python, JavaScript,
or GitHub Actions dependencies have new versions available. This keeps
the project current without manual scanning.

Configuration is in ``.github/dependabot.yml`` at the project root.

Schedule
--------

Dependabot runs on a **weekly schedule** — Monday at 6am ET. Expect a
batch of PRs early Monday morning when updates are available.

What Gets Updated
-----------------

- **Python packages** — defined in ``pyproject.toml``
- **npm packages** — defined in ``package.json``
- **GitHub Actions** — defined in ``.github/workflows/``

Updates within each ecosystem are grouped into a single PR where
possible, except Django and Wagtail, which are excluded from the
Python group so they always arrive as separate PRs requiring review.

Automerge vs. Manual Review
----------------------------

Most grouped patch and minor updates can be merged once CI passes.
However, the following require **manual review** before merging:

- **Django** — major and minor upgrades can require migration changes,
  settings updates, or deprecation fixes.
- **Wagtail** — similarly complex; always review the Wagtail changelog
  before merging.

For any Dependabot PR touching Django or Wagtail:

1. Read the relevant changelog/release notes.
2. Run migrations locally: ``just m``
3. Run tests: ``just t``
4. Check the admin and Wagtail interfaces manually.
5. Merge only if everything passes.

Merging a Routine Dependabot PR
---------------------------------

For non-Django/Wagtail updates:

1. Review the PR diff — confirm only version numbers changed.
2. Check CI passes (GitHub Actions).
3. Pull the branch locally and run ``just t`` if in doubt.
4. Merge and deploy with ``just deploy-remote`` (or ``just dpr``).

Branch Protection and CI Checks
--------------------------------

``main`` requires pull requests and two passing status checks before
merging: ``Test with MongoDB`` and ``Build frontend assets``. The
latter runs ``npm ci && npm run build`` on every push/PR — this exists
specifically to catch npm peer-dependency conflicts (for example, a
major-version bump that's incompatible with another package's peer
dependency range) that ``pytest`` alone would never detect. Don't
merge a Dependabot PR if this check fails; the dependency bump is
likely broken even if the version diff looks harmless.

When several npm Dependabot PRs are open at once, it's often faster to
validate them together: create a scratch worktree off ``origin/main``,
merge each branch into it, then run ``npm ci && npm run build`` once
for the whole batch before merging each PR individually.

Periodically Audit for Unused Dependencies
-------------------------------------------

Dependabot only updates packages already listed in ``package.json``
or ``pyproject.toml`` — it has no way of knowing whether a dependency
is actually used. An unrelated, unused npm package once sat in
``dependencies`` for a long time and its outdated transitive
dependencies accounted for the majority of open vulnerability alerts.
When Dependabot alert counts seem disproportionate to the project's
actual dependency footprint, check ``npm ls <package>`` for the
offending package's dependents — if nothing in the codebase requires
it, removing it entirely is often the real fix, not chasing every
downstream alert one at a time.

Skipping or Deferring an Update
---------------------------------

If a dependency update is not ready to merge, close the PR. Dependabot
will re-open it on the next scheduled run if the dependency is still
outdated. To permanently ignore a package or version range, add an
``ignore`` entry for it under the relevant ``package-ecosystem`` in
``.github/dependabot.yml``.
