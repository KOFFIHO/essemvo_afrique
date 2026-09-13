"""
Réglages Django pour le projet ARGILE
(Plateforme de rapports d'élevage - ESSEMVO Afrique)
"""

from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

# --- Sécurité (à adapter en production) --------------------------------
SECRET_KEY = "django-insecure-change-moi-en-production-argile-2025"
DEBUG = True
ALLOWED_HOSTS = ["*"]

# --- Applications --------------------------------------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    "rapports",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "rapports.context_processors.exploitation_courante",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# --- Base de données (SQLite par défaut) ---------------------------------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# --- Validation des mots de passe ----------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# --- Internationalisation --------------------------------------------------
LANGUAGE_CODE = "fr-fr"
TIME_ZONE = "Africa/Abidjan"
USE_I18N = True
USE_TZ = True

# --- Fichiers statiques et médias ------------------------------------------
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --- Connexion / redirections -----------------------------------------------
LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "accueil"
LOGOUT_REDIRECT_URL = "login"

# --- Infos affichées dans le pied de page ------------------------------------
SITE_NAME = "ARGILE"
SITE_BASELINE = "La Mémoire du Fermier — Plateforme de rapports d'élevage"

# --- Intégration Google Drive (OAuth2) --------------------------------------
# Ces 2 valeurs viennent de Google Cloud Console (identifiant OAuth "Application
# Web") — voir le README pour la marche à suivre. Ne jamais commiter ces
# secrets : passez-les en variables d'environnement en production.
GOOGLE_OAUTH_CLIENT_ID = os.environ.get("GOOGLE_OAUTH_CLIENT_ID", "")
GOOGLE_OAUTH_CLIENT_SECRET = os.environ.get("GOOGLE_OAUTH_CLIENT_SECRET", "")
GOOGLE_OAUTH_REDIRECT_URI = os.environ.get(
    "GOOGLE_OAUTH_REDIRECT_URI", "http://localhost:8000/drive/callback/"
)
SOCIETE = "ESSEMVO AFRIQUE — Bp 79 Man, Côte d'Ivoire — (+225) 07 47 56 97 05"
