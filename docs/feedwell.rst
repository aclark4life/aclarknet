feedwell: Unified Social Feed
==============================

Overview
--------

`feedwell <https://github.com/aclark4life/feedwell>`_ is a reusable Django
app that provides a unified, local-first feed for connected social media
accounts — one place to read posts from Mastodon, Bluesky, and (optionally)
X/Facebook, instead of juggling separate apps.

It's integrated into aclarknet as the ``feedwell.feeds`` app, mounted at
``/feedwell/``.

How It's Integrated
--------------------

feedwell is installed as a regular pip dependency (see ``pyproject.toml``),
not run as its own standalone project, so no separate process or service is
needed — it's just another Django app inside aclarknet:

- ``feedwell.feeds`` is listed in ``INSTALLED_APPS``
  (``aclarknet/settings/base.py``).
- Its URLs are mounted at ``/feedwell/`` in ``aclarknet/urls.py``.
- Its ``auth_urls`` context processor is registered in ``TEMPLATES`` so the
  app's login/logout links resolve against django-allauth's
  ``account_login``/``account_logout`` URLs instead of Django's defaults.
- Its models use MongoDB's ``ObjectIdAutoField`` as their default auto
  field, matching the rest of this project's ``django-mongodb-backend``
  setup, so no custom migration shims were needed (unlike some other
  third-party apps added to this project).

Because it's a normal pip dependency, it's installed, migrated, and
deployed automatically by the existing pipeline — ``deploy.sh`` already
runs ``pip install -e .`` (which includes feedwell) and ``migrate`` on every
deploy, and CI's ``Test with MongoDB`` job already exercises feedwell's
migrations as part of setting up the test database. No extra deployment or
CI steps are required.

Connected Platforms
--------------------

Mastodon and Bluesky connections work out of the box — no app-level
credentials required, since both use per-instance registration or app
passwords entered by the user.

X and Facebook connections are **not currently enabled** on aclarknet —
they require project-level OAuth app credentials
(``X_CLIENT_ID``/``X_CLIENT_SECRET``, ``FACEBOOK_CLIENT_ID``/
``FACEBOOK_CLIENT_SECRET``) to be added to Django settings, which hasn't
been done. Until then, those two platforms simply stay unavailable in the
connect-account UI; everything else continues to work normally.
