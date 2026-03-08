"""
Development settings — DEBUG mode, console email, local MySQL.
"""

from .base import *  # noqa: F401, F403

DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0', '*']

# Override email backend for development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Add django-extensions if available
try:
    import django_extensions  # noqa: F401
    INSTALLED_APPS = INSTALLED_APPS + ['django_extensions']  # noqa: F405
except ImportError:
    pass

# Logging — verbose in dev
LOGGING['loggers']['apps']['level'] = 'DEBUG'  # noqa: F405

# CORS — allow all in dev
CORS_ALLOW_ALL_ORIGINS = True
