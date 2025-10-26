from pathlib import Path

import os

base_dir = Path(__file__).resolve().parent.parent
frontend_dir = Path(__file__).resolve().parent.parent.parent

ALLOWED_HOSTS = []
DEBUG = True
DEFAULT_AUTO_FIELD = "django_mongodb_backend.fields.ObjectIdAutoField"
SECRET_KEY = "your-secret-key"

INSTALLED_APPS = [
    "aclarknet.apps.MongoDBAdminConfig",
    "aclarknet.apps.MongoDBAuthConfig",
    "aclarknet.apps.MongoDBContentTypesConfig",
    "debug_toolbar",
    "django_mongodb_extensions",  # MQL Panel for Debug Toolbar
    "django.contrib.messages",
    "django.contrib.sessions",
    "django.contrib.staticfiles",
    "webpack_boilerplate",
]

MIDDLEWARE = [
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "debug_toolbar.middleware.DebugToolbarMiddleware",
]

ROOT_URLCONF = "aclarknet.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [base_dir / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.request",
            ],
        },
    },
]

WSGI_APPLICATION = "aclarknet.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django_mongodb_backend",
        "HOST": os.getenv("MONGODB_URI"),
        "NAME": "aclarknet",
    },
}

STATIC_URL = "static/"

# Debug toolbar
INTERNAL_IPS = [
    "127.0.0.1",
]

DEBUG_TOOLBAR_PANELS = [
    "debug_toolbar.panels.history.HistoryPanel",
    "debug_toolbar.panels.versions.VersionsPanel",
    "debug_toolbar.panels.timer.TimerPanel",
    "debug_toolbar.panels.settings.SettingsPanel",
    "debug_toolbar.panels.headers.HeadersPanel",
    "debug_toolbar.panels.request.RequestPanel",
    "django_mongodb_extensions.debug_toolbar.panels.MQLPanel",
    "debug_toolbar.panels.staticfiles.StaticFilesPanel",
    "debug_toolbar.panels.templates.TemplatesPanel",
    "debug_toolbar.panels.alerts.AlertsPanel",
    "debug_toolbar.panels.cache.CachePanel",
    "debug_toolbar.panels.signals.SignalsPanel",
    "debug_toolbar.panels.redirects.RedirectsPanel",
    "debug_toolbar.panels.profiling.ProfilingPanel",
]

# Webpack
STATICFILES_DIRS = [
    frontend_dir / "frontend/build",
]

WEBPACK_LOADER = {
    "MANIFEST_FILE": frontend_dir / "frontend/build/manifest.json",
}

MIGRATION_MODULES = {
    "admin": "aclarknet.migrations.admin",
    "auth": "aclarknet.migrations.auth",
    "contenttypes": "aclarknet.migrations.contenttypes",
}
