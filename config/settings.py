import json
import os
import re
from decimal import Decimal
from pathlib import Path

import pykakasi
import yaml
from dotenv import load_dotenv

import bot

load_dotenv()
kakasi = pykakasi.kakasi()

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = 'django-insecure-=ijf2u=)n_aom%_ph)_8p$aam9)z7j4#6r3bc$h$(p*-qk)r8q'
DEBUG = True
ALLOWED_HOSTS = ['*']

DISCORD_CLIENT = {
    'CLIENT-ID': os.environ["DISCORD_CLIENT_ID"],
    'CLIENT-SECRET': os.environ["DISCORD_CLIENT_SECRET"],
    'REDIRECT': os.environ["DISCORD_REDIRECT"],
    'URL': os.environ["DISCORD_LOGIN_URL"],
}
DISCORD_BOT_TOKEN = os.environ["DISCORD_BOT_TOKEN"]

HOST = os.environ["HOST"]

SERVER_ID = os.environ["SERVER_ID"]

POST_PASS = os.environ["POST_PASS"]

SOCKET_PORT = os.environ["SOCKET_PORT"]
SOCKET_HOST = os.environ["SOCKET_HOST"]

with open("setting_item.yml", encoding="utf-8") as sf:
    sf = yaml.load(sf, Loader=yaml.SafeLoader)

SESSION_EXPIRES = sf["session"]["expires"]
POINT_PER = Decimal(str(sf["point"]["point_per"]))
RETURN_RATE = Decimal(str(sf["point"]["return_rate"])) / Decimal("100")
RETURN_PERCENT = Decimal(str(sf["point"]["return_rate"]))
MONEY_UNIT = sf["money"]["unit"]
CANCELLATION_FEE = sf["return"]["cancellation_fee"]
ALLOCATION_PER = sf["revenues"]["allocation_per"]
EXPRESS_PRICE = sf["express"]["price"]

PRIDE_MONTHLY = sf["pride"]["monthly"]
PRIDE_YEARLY = sf["pride"]["yearly"]

# https://docs.djangoproject.com/en/4.2/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    },
    'item': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'sessions',
        'USER': 'root',
        'PASSWORD': 'myon1110',
    },
}
DATABASE_ROUTERS = ['config.db_router.DbRouter']

DATABASE_CONFIG = {
    'utazon': {
        'host': os.environ["DB_UTAZON_HOST"],
        'port': os.environ["DB_UTAZON_PORT"],
        'user': os.environ["DB_UTAZON_USER"],
        'password': os.environ["DB_UTAZON_PASS"],
        'database': os.environ["DB_UTAZON_DB"],
    },
    'address': {
        'host': os.environ["DB_ADDRESS_HOST"],
        'port': os.environ["DB_ADDRESS_PORT"],
        'user': os.environ["DB_ADDRESS_USER"],
        'password': os.environ["DB_ADDRESS_PASS"],
        'database': os.environ["DB_ADDRESS_DB"],
    },
    'linked': {
        'host': os.environ["DB_LINKED_HOST"],
        'port': os.environ["DB_LINKED_PORT"],
        'user': os.environ["DB_LINKED_USER"],
        'password': os.environ["DB_LINKED_PASS"],
        'database': os.environ["DB_LINKED_DB"],
    },
}

with open("setting_category.yml", encoding="utf-8") as f:
    CATEGORIES = yaml.load(f, Loader=yaml.SafeLoader)

with open("setting_suggest.yml", encoding="utf-8") as f:
    SUGGEST = yaml.load(f, Loader=yaml.SafeLoader)
for i in range(len(SUGGEST)):
    try:
        hiragana = SUGGEST[i][1]
        rs = kakasi.convert(hiragana)

        kana = ""
        hepburn = ""
        kunrei = ""
        passport = ""
        for j in rs:
            kana += j["kana"]
            hepburn += j["hepburn"]
            kunrei += j["kunrei"]
            passport += j["passport"]
        SUGGEST[i].append(kana)
        SUGGEST[i].append(hepburn)
        SUGGEST[i].append(kunrei)
        SUGGEST[i].append(passport)

        # 伸ばし棒への対応
        if "ー" in hiragana:
            hiragana = hiragana.replace("ー", "?")
            rs_ = kakasi.convert(hiragana)

            hepburn_ = ""
            kunrei_ = ""
            passport_ = ""
            for j in rs_:
                hepburn_ += j["hepburn"].replace("?", "-")
                kunrei_ += j["kunrei"].replace("?", "-")
                passport_ += j["passport"].replace("?", "-")
            SUGGEST[i].append(hepburn_)
            SUGGEST[i].append(kunrei_)
            SUGGEST[i].append(passport_)

    except IndexError:
        pass
SUGGEST = json.dumps(SUGGEST, ensure_ascii=False)

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'login.apps.LoginConfig',
    'item.apps.ItemConfig',
    'config.apps.Config',
    'account.apps.AccountConfig',
    'pride.apps.PrideConfig',
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
                'config.context_processors.context_processor',
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

DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'assets/'
STATICFILES_DIRS = [BASE_DIR / 'assets']

MEDIA_ROOT = BASE_DIR / 'media'
MEDIA_URL = 'media/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
