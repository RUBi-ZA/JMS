import os

SRC_DIR = os.path.dirname(os.path.dirname(__file__))
BASE_DIR = os.path.dirname(SRC_DIR)
PYTHON_BIN = os.path.join(SRC_DIR, "venv/bin/python")

ENVIRONMENT = os.environ.get("ENVIRONMENT", "development")

exec("from %s import *" % ENVIRONMENT)

MANAGERS = ADMINS

LANGUAGE_CODE = 'en-us'

SITE_ID = 1

USE_I18N = False
USE_L10N = True
USE_TZ = False

MEDIA_ROOT = os.path.join(BASE_DIR, "media")

MEDIA_URL = '/media/'

STATIC_URL = '/assets/'

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "static"),
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder'
)


TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

ROOT_URLCONF = 'JMS.urls'

WSGI_APPLICATION = 'JMS.wsgi.application'

TEMPLATE_DIRS = (
    os.path.join(BASE_DIR, 'templates'),
    os.path.join(BASE_DIR, 'src/filemanager/templates')
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'rest_framework',
    'users',
    'jobs',
    'filemanager',
    'interface',
)

SESSION_SERIALIZER = 'django.contrib.sessions.serializers.JSONSerializer'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
	'rest_framework.renderers.JSONRenderer',
	)
}

SWAGGER_SETTINGS = {
	"exclude_namespaces": ['internal_urls'],
}

AUTHENTICATION_BACKENDS = (
    "filemanager.backends.ImpersonatorBackend",
)

AUTH_PROFILE_MODULE = 'users.UserProfile'

JMS_SETTINGS = {
    "JMS_shared_directory": SHARED_DIRECTORY,
    "resource_manager": {
        "name": "torque",
        "poll_interval": 30
    },
    "ansible": False,
    "modules": False,
    "impersonator": {
        "host": IMPERSONATOR_HOST,
        "port": IMPERSONATOR_PORT
    },
    "filemanager": {
        "root_url": os.path.join(SHARED_DIRECTORY, "users/"),
        "temp_dir": TEMP_DIRECTORY
    }
}

FILEMANAGER_SETTINGS = {
    "root_url": os.path.join(JMS_SETTINGS["JMS_shared_directory"], "users/"),
    "temp_dir": "/tmp/jms/"
}

SERVER_EMAIL = EMAIL_HOST_USER
