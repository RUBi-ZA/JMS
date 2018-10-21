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

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'),
            os.path.join(BASE_DIR, 'src/filemanager/templates')
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
            ]
        }
    },
]

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

ROOT_URLCONF = 'JMS.urls'

WSGI_APPLICATION = 'JMS.wsgi.application'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'rest_framework',
    'accounts',
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
	),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PARSER_CLASSES': (
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser',
        'utilities.django_ext.parsers.PlainTextParser',
    ),
}

SWAGGER_SETTINGS = {
	"exclude_namespaces": ['internal_urls'],
}

AUTHENTICATION_BACKENDS = (
    "accounts.backends.ImpersonatorBackend",
)

JMS_SETTINGS = {
    "JMS_shared_directory": os.path.expanduser(SHARED_DIRECTORY),
    "temp_dir": os.path.expanduser(TEMP_DIRECTORY),
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
