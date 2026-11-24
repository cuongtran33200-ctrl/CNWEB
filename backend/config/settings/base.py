
import os
from pathlib import Path
from urllib.parse import unquote, urlparse

import dj_database_url
from decouple import Config, Csv, RepositoryEnv

BASE_DIR = Path(__file__).resolve().parents[2]
ROOT_DIR = BASE_DIR.parent

ENV_FILE = ROOT_DIR / ".env"
config = (
    Config(RepositoryEnv(str(ENV_FILE)))
    if ENV_FILE.is_file()
    else Config(os.environ)
)

# ==========================================
# BASIC CONFIGURATION
# ==========================================

SECRET_KEY = config(
    "SECRET_KEY",
    default="django-insecure-build-only-change-this-in-vercel",
)

DEBUG = config("DEBUG", default=False, cast=bool)

ALLOWED_HOSTS = config(
    "ALLOWED_HOSTS",
    default="127.0.0.1,localhost,.vercel.app",
    cast=Csv(),
)

# ==========================================
# CLOUDINARY CONFIGURATION
# ==========================================

CLOUDINARY_URL = config("CLOUDINARY_URL", default="")

CLOUDINARY_CLOUD_NAME = config("CLOUDINARY_CLOUD_NAME", default="")

CLOUDINARY_API_KEY = config(
    "CLOUDINARY_API_KEY",
    default=""
)

CLOUDINARY_API_SECRET = config(
    "CLOUDINARY_API_SECRET",
    default=""
)

if CLOUDINARY_URL and CLOUDINARY_URL.startswith("cloudinary://"):
    cloudinary_parts = urlparse(CLOUDINARY_URL)
    CLOUDINARY_CLOUD_NAME = cloudinary_parts.hostname or CLOUDINARY_CLOUD_NAME
    CLOUDINARY_API_KEY = cloudinary_parts.username or CLOUDINARY_API_KEY
    CLOUDINARY_API_SECRET = (
        unquote(cloudinary_parts.password or "") or CLOUDINARY_API_SECRET
    )

CLOUDINARY_ENABLED = all([
    CLOUDINARY_CLOUD_NAME,
    CLOUDINARY_API_KEY,
    CLOUDINARY_API_SECRET,
])

# ==========================================
# INSTALLED APPS
# ==========================================

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    "django.contrib.sitemaps",

    "tinymce",
    "crispy_forms",
    "crispy_bootstrap5",

    "apps.accounts",
    "apps.blog",
    "apps.interactions",
]

if CLOUDINARY_ENABLED:
    INSTALLED_APPS += [
        "cloudinary",
        "cloudinary_storage",
    ]

# ==========================================
# MIDDLEWARE
# ==========================================

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# ==========================================
# URL CONFIGURATION
# ==========================================

ROOT_URLCONF = "config.urls"

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

# ==========================================
# TEMPLATES
# ==========================================

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            ROOT_DIR / "frontend" / "templates"
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.debug",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
            ],
        },
    },
]

# ==========================================
# DATABASE
# ==========================================

DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    DATABASES = {
        "default": dj_database_url.parse(
            DATABASE_URL,
            conn_max_age=600,
        ),
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.mysql",
            "NAME": config("DB_NAME", default="blogdb"),
            "USER": config("DB_USER", default="bloguser"),
            "PASSWORD": config("DB_PASSWORD", default=""),
            "HOST": config("DB_HOST", default="127.0.0.1"),
            "PORT": config("DB_PORT", default="3306"),
            "OPTIONS": {
                "charset": "utf8mb4",
                "init_command": (
                    "SET sql_mode='STRICT_TRANS_TABLES'"
                ),
            },
        }
    }

# ==========================================
# CLOUDINARY STORAGE
# ==========================================

if CLOUDINARY_ENABLED:
    import cloudinary

    cloudinary.config(
        cloud_name=CLOUDINARY_CLOUD_NAME,
        api_key=CLOUDINARY_API_KEY,
        api_secret=CLOUDINARY_API_SECRET,
        secure=True,
    )

    CLOUDINARY_STORAGE = {
        "CLOUD_NAME": CLOUDINARY_CLOUD_NAME,
        "API_KEY": CLOUDINARY_API_KEY,
        "API_SECRET": CLOUDINARY_API_SECRET,
    }

    STORAGES = {
        "default": {
            "BACKEND": (
                "cloudinary_storage.storage.MediaCloudinaryStorage"
            ),
        },
        "staticfiles": {
            "BACKEND": (
                "django.contrib.staticfiles.storage.StaticFilesStorage"
            ),
        },
    }

else:
    STORAGES = {
        "default": {
            "BACKEND": (
                "django.core.files.storage.FileSystemStorage"
            ),
        },
        "staticfiles": {
            "BACKEND": (
                "django.contrib.staticfiles.storage.StaticFilesStorage"
            ),
        },
    }

# ==========================================
# PASSWORD VALIDATION
# ==========================================

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "UserAttributeSimilarityValidator"
        )
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "MinimumLengthValidator"
        )
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "CommonPasswordValidator"
        )
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "NumericPasswordValidator"
        )
    },
]

# ==========================================
# LANGUAGE AND TIME
# ==========================================

LANGUAGE_CODE = "vi"

TIME_ZONE = config(
    "TIME_ZONE",
    default="Asia/Ho_Chi_Minh"
)

USE_I18N = True
USE_TZ = False

# ==========================================
# STATIC FILES
# ==========================================

STATIC_URL = "/static/"

STATICFILES_DIRS = [
    ROOT_DIR / "frontend" / "static"
]

STATIC_ROOT = ROOT_DIR / "staticfiles"

# ==========================================
# MEDIA FILES
# ==========================================

MEDIA_URL = "/media/"
MEDIA_ROOT = ROOT_DIR / "media"

# ==========================================
# DEFAULT SETTINGS
# ==========================================

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_USER_MODEL = "accounts.User"

LOGIN_URL = "accounts:login"
LOGIN_REDIRECT_URL = "home"
LOGOUT_REDIRECT_URL = "home"

# ==========================================
# CRISPY FORMS
# ==========================================

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# ==========================================
# TINYMCE
# ==========================================

TINYMCE_DEFAULT_CONFIG = {
    "height": 420,
    "width": "100%",
    "menubar": False,
    "license_key": "gpl",
    "plugins": (
        "advlist autolink lists link image charmap preview anchor "
        "searchreplace visualblocks code fullscreen insertdatetime media "
        "table help wordcount"
    ),
    "toolbar": (
        "undo redo | blocks | bold italic underline | alignleft aligncenter "
        "alignright | bullist numlist outdent indent | link image table | "
        "code fullscreen"
    ),
}

# ==========================================
# WEBSITE CONFIGURATION
# ==========================================

SITE_NAME = config(
    "SITE_NAME",
    default="SBCB Blog"
)

SITE_URL = config(
    "SITE_URL",
    default="http://127.0.0.1:8000"
)
