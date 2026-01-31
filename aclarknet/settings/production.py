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
    raise ValueError(
        "DJANGO_ALLOWED_HOSTS environment variable must be set in production"
    )

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
WAGTAILADMIN_BASE_URL = os.environ.get("WAGTAIL_BASE_URL", "https://aclark.net")

# Email configuration for production
# Use AWS SES if configured, otherwise fall back to SMTP
USE_SES = os.environ.get("USE_SES", "False") == "True"

if USE_SES:
    # AWS SES Configuration
    EMAIL_BACKEND = "django_ses.SESBackend"

    # AWS SES region (e.g., us-east-1, us-west-2, eu-west-1)
    AWS_SES_REGION_NAME = os.environ.get("AWS_SES_REGION_NAME", "us-east-1")
    AWS_SES_REGION_ENDPOINT = f"email.{AWS_SES_REGION_NAME}.amazonaws.com"

    # AWS credentials (optional - only needed if NOT using IAM role)
    # When running on EC2/ECS/Lambda with an IAM role attached, boto3 will
    # automatically use the instance role credentials. Leave these empty to use IAM role.
    # Only set these if running outside AWS or if you need to use specific IAM user credentials.
    aws_access_key = os.environ.get("AWS_ACCESS_KEY_ID", "")
    aws_secret_key = os.environ.get("AWS_SECRET_ACCESS_KEY", "")

    if aws_access_key and aws_secret_key:
        # Using explicit IAM user credentials
        AWS_ACCESS_KEY_ID = aws_access_key
        AWS_SECRET_ACCESS_KEY = aws_secret_key
    # else: boto3 will automatically use IAM role credentials (recommended for EC2/ECS/Lambda)

    # Optional: Configuration set for tracking
    AWS_SES_CONFIGURATION_SET = os.environ.get("AWS_SES_CONFIGURATION_SET", "")

    # Optional: Use SES v2 (recommended for new implementations)
    USE_SES_V2 = os.environ.get("USE_SES_V2", "True") == "True"
else:
    # Standard SMTP Configuration (fallback)
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
            "filename": os.environ.get(
                "DJANGO_LOG_FILE", "/srv/aclarknet/logs/django.log"
            ),
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

INSTALLED_APPS += ["allauth.socialaccount.providers.github"]  # noqa F405
SOCIALACCOUNT_PROVIDERS = {
    "github": {
        "APP": {
            "client_id": os.environ.get("GITHUB_CLIENT_ID"),
            "secret": os.environ.get("GITHUB_SECRET"),
            "key": os.environ.get("GITHUB_KEY"),
        }
    },
}
ACCOUNT_DEFAULT_HTTP_PROTOCOL = "https"

RECAPTCHA_PRIVATE_KEY = os.environ.get("RECAPTCHA_PRIVATE_KEY")
RECAPTCHA_PUBLIC_KEY = os.environ.get("RECAPTCHA_PUBLIC_KEY")
# reCAPTCHA v3 score threshold (0.0 to 1.0, where 1.0 is very likely a human)
RECAPTCHA_REQUIRED_SCORE = float(os.environ.get("RECAPTCHA_REQUIRED_SCORE", "0.5"))
