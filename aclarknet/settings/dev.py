from .base import *  # noqa F403 F401

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-r5pm3)ob%3su=$c-2w&qyg)@zu58hl9di1h)vhj2jkn9!bakv@"

# SECURITY WARNING: define the correct hosts in production!
ALLOWED_HOSTS = ["*"]

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Google reCAPTCHA v3 test keys for development
# These are official Google test keys that always pass validation
RECAPTCHA_PUBLIC_KEY = "6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI"
RECAPTCHA_PRIVATE_KEY = "6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJWe"
RECAPTCHA_REQUIRED_SCORE = 0.5
# Optionally disable reCAPTCHA validation in development (uncomment to disable)
# RECAPTCHA_DISABLE = True
# Silence the test key warning in development
SILENCED_SYSTEM_CHECKS = ["django_recaptcha.recaptcha_test_key_error"]


try:
    from .local import *  # noqa F403 F401
except ImportError:
    pass

if DEBUG:
    INSTALLED_APPS += ["debug_toolbar", "hijack", "hijack.contrib.admin"]  # noqa F405
    MIDDLEWARE += [  # noqa F405
        "debug_toolbar.middleware.DebugToolbarMiddleware",
        "hijack.middleware.HijackUserMiddleware",
    ]
    INTERNAL_IPS = ["127.0.0.1"]
