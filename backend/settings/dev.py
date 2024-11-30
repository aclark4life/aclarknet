from .base import *  # noqa: F403

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure--bpuep8!6(eocqe*gsp!6jxl%t^x_ge#bn^5vf=!8ao$yvg%ls"

# SECURITY WARNING: define the correct hosts in production!
ALLOWED_HOSTS = ["*"]

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"


try:
    from .local import *  # noqa: F403
except ImportError:
    pass


INTERNAL_IPS = [
    "127.0.0.1",
]
