import environ

from pathlib import Path

import loguru

BASE_DIR = Path(__file__).resolve().parent.parent

ROOT_DIR = environ.Path(__file__) - 3

APPS_DIR = ROOT_DIR.path("binance_bot")

env = environ.Env()

env.read_env(str(ROOT_DIR.path(".env")))

DEBUG = env.bool("DJANGO_DEBUG", False)

CORS_ORIGIN_ALLOW_ALL = True

CORS_REPLACE_HTTPS_REFERER = True

CSRF_TRUSTED_ORIGINS = env.tuple("CSRF_TRUSTED_ORIGINS")

CSRF_COOKIE_DOMAIN = env("CSRF_COOKIE_DOMAIN")

CORS_ORIGIN_WHITELIST = env.tuple("CORS_ORIGIN_WHITELIST")

TIME_ZONE = "America/New_York"

LANGUAGE_CODE = "en-us"

SITE_ID = 1

USE_I18N = True

USE_L10N = True

USE_TZ = True

DATABASES = {
    'default': {
        'ENGINE': env('DJANGO_DB_ENGINE'),
        'NAME': env('POSTGRES_NAME'),
        'USER': env('POSTGRES_USER'),
        'PASSWORD': env('POSTGRES_PASSWORD'),
        'HOST': env('POSTGRES_HOST'),
        'PORT': env('POSTGRES_PORT'),
    }
}

DATABASES["default"]["ATOMIC_REQUESTS"] = True

ROOT_URLCONF = "config.urls"

WSGI_APPLICATION = "config.wsgi.application"

SECRET_KEY = env('DJANGO_SECRET_KEY')

ALLOWED_HOSTS = env.tuple('DJANGO_ALLOWED_HOSTS')

DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'loguru',
]

LOCAL_APPS = [
    "binance_bot.trades.apps.TradesConfig",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

STATIC_ROOT = str(ROOT_DIR("static"))

STATIC_URL = "/static/"

STATICFILES_DIRS = [
    str(APPS_DIR.path("static")),
]

STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]

MEDIA_ROOT = str(APPS_DIR.path("media"))

MEDIA_URL = "/media/"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [str(APPS_DIR.path("templates")),],
        "APP_DIRS": True,
        "OPTIONS": {
            "debug": DEBUG,
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

FIXTURE_DIRS = (str(APPS_DIR.path("fixtures")),)

SESSION_COOKIE_HTTPONLY = False

SESSION_COOKIE_AGE = 86400

SESSION_EXPIRE_AT_BROWSER_CLOSE = True

CSRF_COOKIE_HTTPONLY = False

SECURE_BROWSER_XSS_FILTER = True

DATA_UPLOAD_MAX_MEMORY_SIZE = 104857600

X_FRAME_OPTIONS = "DENY"

ADMIN_URL = "admin/"

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

loguru.logger.add(f"{BASE_DIR}/logs.log", level='DEBUG', format="{time} {level} {message}")

BINANCE_API_KEY = env('BINANCE_API_KEY')

BINANCE_API_SECRET = env('BINANCE_API_SECRET')
