# This file is exec'd from settings.py, so it has access to and can
# modify all the variables in settings.py.
# If this file is changed in development, the development server will
# have to be manually restarted because changes will not be noticed
# immediately.

SECRET_KEY = "A_TOP_SECRET_KEY"

SITE_ID = 1

DEBUG = True

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": "dev.db",
        "USER": "",
        "PASSWORD": "",
        "HOST": "",
        "PORT": "",
    }
}

CACHE_MIDDLEWARE_SECONDS = 60

CACHE_MIDDLEWARE_KEY_PREFIX = "AIC_RUNNER_TEST"

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.memcached.MemcachedCache",
        "LOCATION": "127.0.0.1:11211",
    }
}
SESSION_ENGINE = "django.contrib.sessions.backends.cache"


EMAIL_HOST = 'localhost'
EMAIL_HOST_USER = 'webmaster@localhost'
EMAIL_HOST_PASSWORD = 'TOPSECRET'
EMAIL_PORT = 25
EMAIL_USE_TLS = True



SFTP_STORAGE_HOST = "localhost"
SFTP_STORAGE_ROOT = '/home/user/media/'
SFTP_STORAGE_PARAMS = {'username': 'user', 'password': 'password', 'look_for_keys': False}


# WARNING: Queue name must be unique among computers using the same broker
BROKER_URL = 'redis://localhost:6379/1'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/1'
CELERY_ROUTES = {'queued_storage.tasks.Transfer': {'queue': 'filestorage_queue_UID'},
                 'queued_storage.tasks.TransferAndDelete': {'queue': 'filestorage_queue_UID'},
                 }

CPU_MANAGER_REDIS_HOST = "localhost"
CPU_MANAGER_REDIS_PORT = 6379
CPU_MANAGER_REDIS_CODE_COMPILER_DB = 3
CPU_MANAGER_REDIS_GAME_RUNNER_DB = 4

### STORAGE SETTINGS ###

from django.core.files.storage import FileSystemStorage

BASE_AND_GAME_STORAGE = FileSystemStorage()

