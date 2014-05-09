import os
import urlparse

from .settings import *


DEBUG = False
TEMPLATE_DEBUG = DEBUG

ALLOWED_HOSTS = [
    'new-project.cincoovnis.com',
    'www.new-project.cincoovnis.com',
]

SECRET_KEY = os.environ['SECRET_KEY']

SITE_ID = 1

if "NEW-PROJECT_DATABASE_URL" in os.environ:
    urlparse.uses_netloc.append("postgres")
    url = urlparse.urlparse(os.environ["NEW-PROJECT_DATABASE_URL"])
    DATABASES = {
        "default": {
            "ENGINE": {
                "postgres": "django.db.backends.postgresql_psycopg2"
            }[url.scheme],
            "NAME": url.path[1:],
            "USER": url.username,
            "PASSWORD": url.password,
            "HOST": url.hostname,
            "PORT": url.port
        }
    }

MEDIA_ROOT = os.path.join(os.environ["NEW-PROJECT_DATA_DIR"], "site_media", "media")
STATIC_ROOT = os.path.join(os.environ["NEW-PROJECT_DATA_DIR"], "site_media", "static")

MEDIA_URL = "/site_media/media/"
STATIC_URL = "/site_media/static/"

# Opbeat
OPBEAT = {
    "ORGANIZATION_ID": os.environ.get("OPBEAT_ORGANIZATION_ID"),
    "APP_ID": os.environ.get("OPBEAT_APP_ID"),
    "SECRET_TOKEN": os.environ.get("OPBEAT_SECRET_TOKEN")
}

INSTALLED_APPS += (
    'opbeat.contrib.django',
)
