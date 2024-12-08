import os

from .base import *  # noqa: F403
from backend.utils import get_ec2_metadata

DEBUG = False

try:
    from .local import *  # noqa: F403
except ImportError:
    pass

MIDDLEWARE.append("whitenoise.middleware.WhiteNoiseMiddleware")  # noqa

SECRET_KEY = os.environ.get("SECRET_KEY")

LOCAL_IPV4 = get_ec2_metadata()
ALLOWED_HOSTS.append(LOCAL_IPV4)  # noqa
