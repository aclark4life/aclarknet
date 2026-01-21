import os

from dotenv import load_dotenv

from .base import *  # noqa: F401, F403

# Load environment variables from .env file if it exists
load_dotenv()

DEBUG = False

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("DJANGO_SECRET_KEY environment variable must be set in production")

# SECURITY WARNING: define the correct hosts in production!
ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", "").split(",")
if not ALLOWED_HOSTS or ALLOWED_HOSTS == [""]:
    raise ValueError("DJANGO_ALLOWED_HOSTS environment variable must be set in production")

# CSRF trusted origins for HTTPS
CSRF_TRUSTED_ORIGINS = os.environ.get("DJANGO_CSRF_TRUSTED_ORIGINS", "").split(",")

# Security settings for HTTPS
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Database configuration from environment
DATABASES = {
    "default": {
        "ENGINE": "django_mongodb_backend",
        "NAME": os.environ.get("MONGODB_DB", "aclarknet"),
        "HOST": os.environ.get("MONGODB_URI", "localhost"),
    }
}

# Static files configuration for production
STATIC_ROOT = os.environ.get("DJANGO_STATIC_ROOT", "/srv/aclarknet/static")
MEDIA_ROOT = os.environ.get("DJANGO_MEDIA_ROOT", "/srv/aclarknet/media")

# ManifestStaticFilesStorage is recommended in production, to prevent
# outdated JavaScript / CSS assets being served from cache
# (e.g. after a Wagtail upgrade).
# See https://docs.djangoproject.com/en/6.0/ref/contrib/staticfiles/#manifeststaticfilesstorage
STORAGES["staticfiles"]["BACKEND"] = (  # noqa: F405
    "django.contrib.staticfiles.storage.ManifestStaticFilesStorage"
)

# Wagtail base URL for production
WAGTAILADMIN_BASE_URL = os.environ.get("WAGTAIL_BASE_URL", "https://m.aclark.net")

# Email configuration for production
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = os.environ.get("EMAIL_HOST", "localhost")
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", "25"))
EMAIL_USE_TLS = os.environ.get("EMAIL_USE_TLS", "False") == "True"
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")

# Logging configuration
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "file": {
            "level": "ERROR",
            "class": "logging.FileHandler",
            "filename": os.environ.get("DJANGO_LOG_FILE", "/srv/aclarknet/logs/django.log"),
        },
    },
    "loggers": {
        "django": {
            "handlers": ["file"],
            "level": "ERROR",
            "propagate": True,
        },
    },
}

try:
    from .local import *  # noqa: F401, F403
except ImportError:
    pass
