from .base import *  # noqa F403 F401

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-r5pm3)ob%3su=$c-2w&qyg)@zu58hl9di1h)vhj2jkn9!bakv@"

# SECURITY WARNING: define the correct hosts in production!
ALLOWED_HOSTS = ["*"]

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"


try:
    from .local import *  # noqa F403 F401
except ImportError:
    pass

if DEBUG:
    INSTALLED_APPS += ["debug_toolbar"]  # noqa F405
    MIDDLEWARE += ["debug_toolbar.middleware.DebugToolbarMiddleware"]  # noqa F405
    INTERNAL_IPS = ["127.0.0.1"]
