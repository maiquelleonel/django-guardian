import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

SECRET_KEY = "django-guardian-test-secret-key-very-secret"

DEBUG = True

ALLOWED_HOSTS = []

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "django_guardian",
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
    }
}

USE_TZ = True

# Silence system checks during test execution to keep output extremely clean and token-efficient
SILENCED_SYSTEM_CHECKS = [
    "guardian.W001",
    "guardian.W007",
]
