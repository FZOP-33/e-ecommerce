import os
from pathlib import Path
from decouple import config
import pymysql
import dj_database_url

# ⚠️ Si tu utilises MySQL avec PyMySQL
pymysql.install_as_MySQLdb()

# Chemin de base du projet
BASE_DIR = Path(__file__).resolve().parent.parent

# 🔐 Clé Django
SECRET_KEY = config("DJANGO_SECRET_KEY", default="dev-secret")

# Mode debug
DEBUG = config("DEBUG", default=True, cast=bool)

ALLOWED_HOSTS = ["*"]

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

# Base de données (Render ou local)
#DATABASES = {
#    "default": {
#        "ENGINE": "django.db.backends.postgresql",
#        "NAME": config("DB_NAME", default="ecommerce_db"),
#        "USER": config("DB_USER", default="postgres"),
#        "PASSWORD": config("DB_PASSWORD", default="root1234"),
#        "HOST": config("DB_HOST", default="localhost"),
#        "PORT": config("DB_PORT", default="5432"),
#    }
#}
DATABASES = {
    'default': dj_database_url.parse(config("DATABASE_URL"))
}


# Validation des mots de passe
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

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