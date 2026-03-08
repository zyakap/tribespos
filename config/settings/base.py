"""
Harhurum POS — Base Settings
Shared across all environments. Do not use directly; import from
development.py or production.py.
"""

import environ
from pathlib import Path
from datetime import timedelta

# ─────────────────────────────────────────────────────────────────────────────
# Paths
# ─────────────────────────────────────────────────────────────────────────────

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# ─────────────────────────────────────────────────────────────────────────────
# django-environ initialisation
# ─────────────────────────────────────────────────────────────────────────────

env = environ.Env(
    DEBUG=(bool, False),
    ALLOWED_HOSTS=(list, []),
    REDIS_URL=(str, 'redis://localhost:6379/0'),
    DB_HOST=(str, 'localhost'),
    DB_PORT=(str, '3306'),
    MANAGER_EMAIL=(str, ''),
    HARHURUM_TIN=(str, ''),
    HARHURUM_GST_REG=(str, ''),
    TAX_ALERT_EMAIL=(str, ''),
)

environ.Env.read_env(BASE_DIR / '.env')

# ─────────────────────────────────────────────────────────────────────────────
# Core Django settings
# ─────────────────────────────────────────────────────────────────────────────

SECRET_KEY = env('SECRET_KEY')

DEBUG = env('DEBUG')

ALLOWED_HOSTS = env('ALLOWED_HOSTS')

# ─────────────────────────────────────────────────────────────────────────────
# Application definition
# ─────────────────────────────────────────────────────────────────────────────

DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'channels',
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'django_filters',
    'import_export',
    'simple_history',
    'crispy_forms',
    'crispy_bootstrap5',
]

LOCAL_APPS = [
    'apps.core',
    'apps.accounts',
    'apps.customers',
    'apps.suppliers',
    'apps.products',
    'apps.warehouse',
    'apps.procurement',
    'apps.pos',
    'apps.cafe',
    'apps.restaurant',
    'apps.tailoring',
    'apps.accounting',
    'apps.irc_tax',
    'apps.reporting',
    'apps.api',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# ─────────────────────────────────────────────────────────────────────────────
# Middleware
# ─────────────────────────────────────────────────────────────────────────────

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'simple_history.middleware.HistoryRequestMiddleware',
]

ROOT_URLCONF = 'config.urls'

# ─────────────────────────────────────────────────────────────────────────────
# Templates
# ─────────────────────────────────────────────────────────────────────────────

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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
ASGI_APPLICATION = 'config.asgi.application'

# ─────────────────────────────────────────────────────────────────────────────
# Database — MySQL 8
# ─────────────────────────────────────────────────────────────────────────────

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': env('DB_NAME'),
        'USER': env('DB_USER'),
        'PASSWORD': env('DB_PASSWORD'),
        'HOST': env('DB_HOST', default='localhost'),
        'PORT': env('DB_PORT', default='3306'),
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            'charset': 'utf8mb4',
        },
        'CONN_MAX_AGE': 60,
    }
}

# ─────────────────────────────────────────────────────────────────────────────
# Auth
# ─────────────────────────────────────────────────────────────────────────────

AUTH_USER_MODEL = 'auth.User'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/accounts/login/'

# ─────────────────────────────────────────────────────────────────────────────
# Internationalisation — PNG time zone
# ─────────────────────────────────────────────────────────────────────────────

LANGUAGE_CODE = 'en-au'

TIME_ZONE = 'Pacific/Port_Moresby'

USE_I18N = True

USE_TZ = True

# ─────────────────────────────────────────────────────────────────────────────
# Static & Media files
# ─────────────────────────────────────────────────────────────────────────────

STATIC_URL = '/static/'
STATIC_ROOT = env('STATIC_ROOT', default=str(BASE_DIR / 'staticfiles'))
STATICFILES_DIRS = [BASE_DIR / 'static']
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = env('MEDIA_ROOT', default=str(BASE_DIR / 'media'))

# ─────────────────────────────────────────────────────────────────────────────
# Default primary key
# ─────────────────────────────────────────────────────────────────────────────

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ─────────────────────────────────────────────────────────────────────────────
# Django REST Framework
# ─────────────────────────────────────────────────────────────────────────────

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 50,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
    'EXCEPTION_HANDLER': 'rest_framework.views.exception_handler',
}

# ─────────────────────────────────────────────────────────────────────────────
# SimpleJWT
# ─────────────────────────────────────────────────────────────────────────────

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=8),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256',
    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
}

# ─────────────────────────────────────────────────────────────────────────────
# Django Channels — WebSocket (Kitchen Display System)
# ─────────────────────────────────────────────────────────────────────────────

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [env('REDIS_URL', default='redis://localhost:6379/0')],
        },
    },
}

# ─────────────────────────────────────────────────────────────────────────────
# Celery
# ─────────────────────────────────────────────────────────────────────────────

CELERY_BROKER_URL = env('REDIS_URL', default='redis://localhost:6379/0')
CELERY_RESULT_BACKEND = env('REDIS_URL', default='redis://localhost:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Pacific/Port_Moresby'
CELERY_ENABLE_UTC = True

from celery.schedules import crontab  # noqa: E402

CELERY_BEAT_SCHEDULE = {
    'auto-generate-monthly-returns': {
        'task': 'apps.irc_tax.tasks.auto_generate_monthly_returns',
        'schedule': crontab(hour=0, minute=5, day_of_month=1),  # 1st of month at 00:05
    },
    'check-tax-deadline-alerts': {
        'task': 'apps.irc_tax.tasks.check_tax_deadline_alerts',
        'schedule': crontab(hour=8, minute=0),  # Daily at 8:00 AM PNG time
    },
}

# ─────────────────────────────────────────────────────────────────────────────
# Caching — Redis
# ─────────────────────────────────────────────────────────────────────────────

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': env('REDIS_URL', default='redis://localhost:6379/0'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
    }
}

# ─────────────────────────────────────────────────────────────────────────────
# Email
# ─────────────────────────────────────────────────────────────────────────────

EMAIL_BACKEND = env('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = env('EMAIL_HOST', default='localhost')
EMAIL_PORT = env.int('EMAIL_PORT', default=587)
EMAIL_USE_TLS = env.bool('EMAIL_USE_TLS', default=True)
EMAIL_HOST_USER = env('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL', default='Harhurum POS <noreply@harhurum.com.pg>')
SERVER_EMAIL = DEFAULT_FROM_EMAIL

# ─────────────────────────────────────────────────────────────────────────────
# Crispy Forms — Bootstrap 5
# ─────────────────────────────────────────────────────────────────────────────

CRISPY_ALLOWED_TEMPLATE_PACKS = 'bootstrap5'
CRISPY_TEMPLATE_PACK = 'bootstrap5'

# ─────────────────────────────────────────────────────────────────────────────
# django-simple-history
# ─────────────────────────────────────────────────────────────────────────────

SIMPLE_HISTORY_REVERT_DISABLED = False
SIMPLE_HISTORY_HISTORY_CHANGE_REASON_USE_TEXT_FIELD = True

# ─────────────────────────────────────────────────────────────────────────────
# WeasyPrint — PDF generation
# ─────────────────────────────────────────────────────────────────────────────

# WeasyPrint uses system fonts; no extra Django config required.
# Ensure Pango/Cairo libs are installed on the host (see Dockerfile).

# ─────────────────────────────────────────────────────────────────────────────
# Harhurum business configuration
# ─────────────────────────────────────────────────────────────────────────────

HARHURUM_CONFIG = {
    'COMPANY_NAME': 'Harhurum',
    'COMPANY_WEBSITE': 'harhurum.com.pg',
    'DEFAULT_CURRENCY': 'PGK',
    'DEFAULT_TAX_RATE': 10.0,
    'TAX_INCLUSIVE': True,
    'RECEIPT_FOOTER': 'Thank you for your business!',
    'LOW_STOCK_NOTIFY_EMAIL': env('MANAGER_EMAIL', default=''),
    # IRC Tax Compliance
    'IRC_TIN': env('HARHURUM_TIN', default=''),
    'IRC_GST_REG_NO': env('HARHURUM_GST_REG', default=''),
    'TAX_ALERT_EMAIL': env('TAX_ALERT_EMAIL', default=''),
    'CIT_RATE': 30.0,
    'SWT_TAX_FREE_THRESHOLD': 20_000.0,
    'FISCAL_YEAR_START_MONTH': 1,  # January
}

# ─────────────────────────────────────────────────────────────────────────────
# Session
# ─────────────────────────────────────────────────────────────────────────────

SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 28800  # 8 hours in seconds
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

# ─────────────────────────────────────────────────────────────────────────────
# Logging
# ─────────────────────────────────────────────────────────────────────────────

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {asctime} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'harhurum.log',
            'maxBytes': 1024 * 1024 * 10,  # 10 MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'apps': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}
