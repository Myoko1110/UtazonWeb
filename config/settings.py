import os
from pathlib import Path
import mysql.connector
from dotenv import load_dotenv

load_dotenv()
BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = 'django-insecure-=ijf2u=)n_aom%_ph)_8p$aam9)z7j4#6r3bc$h$(p*-qk)r8q'
DEBUG = True
ALLOWED_HOSTS = []


DISCORD_CLIENT = {
    'CLIENT-ID': os.environ["DISCORD_CLIENT_ID"],
    'CLIENT-SECRET': os.environ["DISCORD_CLIENT_SECRET"],
    'REDIRECT': os.environ["DISCORD_REDIRECT"],
}

SERVER_ID = os.environ["SERVER_ID"]

SESSION_EXPIRES = os.environ["SESSION_EXPIRES"]

# https://docs.djangoproject.com/en/4.2/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }, 'session': {
        'HOST': os.environ["DATABASE_HOST"],
        'USER': os.environ["DATABASE_USERNAME"],
        'PASSWORD': os.environ["DATABASE_PASS"],
        'DATABASE': os.environ["DATABASE_TABLE"],
    }
}

DATABASE_CONFIG = {
    'user': DATABASES['session']['USER'],
    'password': DATABASES['session']['PASSWORD'],
    'host': DATABASES['session']['HOST'],
    'database': DATABASES['session']['DATABASE'],
}


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'login.apps.LoginConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [Path.joinpath(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'ja-jp'

TIME_ZONE = 'Asia/Tokyo'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'assets/'
STATICFILES_DIRS = [BASE_DIR / 'assets']

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
