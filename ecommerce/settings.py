import os
from pathlib import Path
from decouple import config
import pymysql
import dj_database_url
from django.conf.global_settings import CSRF_TRUSTED_ORIGINS
from dotenv import load_dotenv
load_dotenv()
# ⚠️ Si tu utilises MySQL avec PyMySQL
pymysql.install_as_MySQLdb()

# Chemin de base du projet
BASE_DIR = Path(__file__).resolve().parent.parent

# 🔐 Clé Django
SECRET_KEY = config("DJANGO_SECRET_KEY", default="dev-secret")

# Mode debug
DEBUG = config("DEBUG", default=True, cast=bool)

ALLOWED_HOSTS = ["*"]

CSRF_TRUSTED_ORIGINS = ["https://e-ecommerce-production-85a7.up.railway.app"]
# Applications Django
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "boutique",  # ton application
]

# Middleware
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

ROOT_URLCONF = "ecommerce.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "boutique.context_processors.categories_processor",
                "boutique.context_processors.panier_info",
            ],
        },
    },
]

WSGI_APPLICATION = "ecommerce.wsgi.application"
DB_LIVE=os.environ.get("DB_LIVE")


if DB_LIVE in ["False", False]:

    DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': BASE_DIR / 'db.sqlite3',
            }
        }
else:

    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.environ.get("DB_NAME"),
            "USER": os.environ.get("DB_USER"),
            "PASSWORD": os.environ.get("DB_PASSWORD"),
            "HOST": os.environ.get("DB_HOST"),
            "PORT": os.environ.get("DB_PORT"),
        }
    }

    #DATABASES = {
    #   'default': os.environ.get('DATABASE_URL'),
    #}


# Validation des mots de passe
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Internationalisation
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# Static & Media

STATIC_URL = "static/"
MEDIA_URL = "media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# Default primary key
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


STRIPE_SECRET_KEY = config("STRIPE_SECRET_KEY")
STRIPE_PUBLISHABLE_KEY = config("STRIPE_PUBLISHABLE_KEY")