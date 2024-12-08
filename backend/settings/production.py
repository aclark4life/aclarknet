import os

from .base import *  # noqa: F403

DEBUG = False

try:
    from .local import *  # noqa: F403
except ImportError:
    pass

MIDDLEWARE.append("whitenoise.middleware.WhiteNoiseMiddleware")  # noqa

SECRET_KEY = os.environ.get("SECRET_KEY")
