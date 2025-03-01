import django_mongodb_backend
import dj_database_url
import os

from bson import ObjectId

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_DIR = os.path.dirname(PROJECT_DIR)

# Check environment variables
MONGODB_URI = os.getenv("MONGODB_URI")
POSTGRES_URI = os.getenv("POSTGRES_URI")

# Determine which URI to use
if MONGODB_URI:
    settings_dict = django_mongodb_backend.parse_uri(MONGODB_URI)
elif POSTGRES_URI:
    settings_dict = dj_database_url.parse(POSTGRES_URI)
else:
    settings_dict = django_mongodb_backend.parse_uri("mongodb://localhost:27017/backend")


if settings_dict["ENGINE"] == "django_mongodb_backend":
    DEFAULT_AUTO_FIELD = "django_mongodb_backend.fields.ObjectIdAutoField"
    INSTALLED_APPS = [
        "backend.mongo_apps.MongoWagtailFormsAppConfig",
        "backend.mongo_apps.MongoWagtailRedirectsAppConfig",
        "backend.mongo_apps.MongoWagtailEmbedsAppConfig",
        "wagtail.sites",
        "backend.mongo_apps.MongoWagtailUsersAppConfig",
        "wagtail.snippets",
        "backend.mongo_apps.MongoWagtailDocsAppConfig",
        "backend.mongo_apps.MongoWagtailImagesAppConfig",
        "backend.mongo_apps.MongoWagtailSearchAppConfig",
        "backend.mongo_apps.MongoWagtailAdminAppConfig",
        "backend.mongo_apps.MongoWagtailAppConfig",
        "modelcluster",
        "backend.mongo_apps.MongoTaggitAppConfig",
        'backend.mongo_apps.MongoAdminConfig',
        'backend.mongo_apps.MongoAuthConfig',
        'backend.mongo_apps.MongoContentTypesConfig',
        "django.contrib.sessions",
        "django.contrib.messages",
        "django.contrib.staticfiles",
        "django_extensions",
        "webpack_boilerplate",
        "debug_toolbar",
        "home",
        "db",
    ]

    MIGRATION_MODULES = {
        "admin": "mongo_migrations.admin",
        "auth": "mongo_migrations.auth",
        "contenttypes": "mongo_migrations.contenttypes",
        "taggit": "mongo_migrations.taggit",
        "wagtaildocs": "mongo_migrations.wagtaildocs",
        "wagtailredirects": "mongo_migrations.wagtailredirects",
        "wagtailimages": "mongo_migrations.wagtailimages",
        "wagtailsearch": "mongo_migrations.wagtailsearch",
        "wagtailadmin": "mongo_migrations.wagtailadmin",
        "wagtailcore": "mongo_migrations.wagtailcore",
        "wagtailforms": "mongo_migrations.wagtailforms",
        "wagtailembeds": "mongo_migrations.wagtailembeds",
        "wagtailusers": "mongo_migrations.wagtailusers",
    }

elif settings_dict["ENGINE"] == "django.db.backends.postgresql":
    INSTALLED_APPS = [
        "home",
        "wagtail.contrib.forms",
        "wagtail.contrib.redirects",
        "wagtail.embeds",
        "wagtail.sites",
        "wagtail.users",
        "wagtail.snippets",
        "wagtail.documents",
        "wagtail.images",
        "wagtail.search",
        "wagtail.admin",
        "wagtail",
        "modelcluster",
        "taggit",
        "django.contrib.admin",
        "django.contrib.auth",
        "django.contrib.contenttypes",
        "django.contrib.sessions",
        "django.contrib.messages",
        "django.contrib.staticfiles",
        "django_extensions",
        "webpack_boilerplate",
        "debug_toolbar",
    ]
else:
    raise ValueError("Neither MONGODB_URI nor POSTGRES_URI is set in the environment variables.")

DATABASES = {"default": settings_dict}
DEBUG = True

ROOT_URLCONF = "backend.urls"

STATICFILES_DIRS = [os.path.join(BASE_DIR, "frontend", "build")]

WEBPACK_LOADER = {
    "MANIFEST_FILE": os.path.join(BASE_DIR, "frontend", "build", "manifest.json")
}

SECRET_KEY = "django-insecure-y+6plg)7c7%65p*pji2qt&n_cme-&j%gg)vbg5p#mmmx*r5y@8"


ALLOWED_HOSTS = ["*"]

STATIC_URL = "static/"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        # "DIRS": [
        #     os.path.join(PROJECT_DIR, "templates"),
        # ],
        "DIRS": [os.path.join("backend", "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

MIDDLEWARE = [
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "wagtail.contrib.redirects.middleware.RedirectMiddleware",
    "debug_toolbar.middleware.DebugToolbarMiddleware",
]

WAGTAIL_SITE_NAME = "backend"

INTERNAL_IPS = [
    "127.0.0.1",
]

SITE_ID = ObjectId("000000000000000000000001")
