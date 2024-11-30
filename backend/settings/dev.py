from .base import *  # noqa: F403

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-d*y)n=o_7*i#^gy41r_=1(8cqfa1sv+=^9j1l52_z7po&cbah-"

# SECURITY WARNING: define the correct hosts in production!
ALLOWED_HOSTS = ["*"]

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"


try:
    from .local import *  # noqa: F403
except ImportError:
    pass
