"""
Django settings for project.

Generated by 'django-admin startproject' using Django 1.8.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import logging
from django.core.urlresolvers import reverse_lazy
from .secure import SECURE_SETTINGS

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# Application definition

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_auth_lti',
    'icommons_common',
    'lti_permissions',
    'icommons_ui',
    'proxy',
    'canvas_account_admin_tools',
    'course_info',
    'cross_list_courses',
    'canvas_site_creator',
    'canvas_course_site_wizard',
    'djangular',
    'people_tool',
)

MIDDLEWARE_CLASSES = (
    # NOTE - djangular needs to be the first item in this list
    'djangular.middleware.DjangularUrlMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'cached_auth.Middleware',
    'django_auth_lti.middleware_patched.MultiLTILaunchAuthMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
)

AUTHENTICATION_BACKENDS = (
    'django_auth_lti.backends.LTIAuthBackend',
)

LOGIN_URL = reverse_lazy('lti_auth_error')

ROOT_URLCONF = 'canvas_account_admin_tools.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'canvas_account_admin_tools.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

DATABASE_ROUTERS = ['icommons_common.routers.CourseSchemaDatabaseRouter']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': SECURE_SETTINGS.get('db_default_name', 'canvas_account_admin_tools'),
        'USER': SECURE_SETTINGS.get('db_default_user', 'postgres'),
        'PASSWORD': SECURE_SETTINGS.get('db_default_password'),
        'HOST': SECURE_SETTINGS.get('db_default_host', '127.0.0.1'),
        'PORT': SECURE_SETTINGS.get('db_default_port', 5432),  # Default postgres port
    },
    'termtool': {
        'ENGINE': 'django.db.backends.oracle',
        'NAME': SECURE_SETTINGS.get('db_termtool_name'),
        'USER': SECURE_SETTINGS.get('db_termtool_user'),
        'PASSWORD': SECURE_SETTINGS.get('db_termtool_password'),
        'HOST': SECURE_SETTINGS.get('db_termtool_host'),
        'PORT': str(SECURE_SETTINGS.get('db_termtool_port')),
        'OPTIONS': {
            'threaded': True,
        },
        'CONN_MAX_AGE': 0,
    }
}

# Cache
# https://docs.djangoproject.com/en/1.8/ref/settings/#std:setting-CACHES

REDIS_HOST = SECURE_SETTINGS.get('redis_host', '127.0.0.1')
REDIS_PORT = SECURE_SETTINGS.get('redis_port', 6379)

CACHES = {
    'default': {
        'BACKEND': 'redis_cache.RedisCache',
        'LOCATION': "redis://%s:%s/0" % (REDIS_HOST, REDIS_PORT),
        'OPTIONS': {
            'PARSER_CLASS': 'redis.connection.HiredisParser'
        },
        'KEY_PREFIX': 'canvas_account_admin_tools',  # Provide a unique value for intra-app cache
        # See following for default timeout (5 minutes as of 1.7):
        # https://docs.djangoproject.com/en/1.8/ref/settings/#std:setting-CACHES-TIMEOUT
        'TIMEOUT': SECURE_SETTINGS.get('default_cache_timeout_secs', 300),
    },
    'shared': {
        'BACKEND': 'redis_cache.RedisCache',
        'LOCATION': "redis://%s:%s/0" % (REDIS_HOST, REDIS_PORT),
        'OPTIONS': {
            'PARSER_CLASS': 'redis.connection.HiredisParser'
        },
        'KEY_PREFIX': 'tlt_shared',
        'TIMEOUT': SECURE_SETTINGS.get('default_cache_timeout_secs', 300),
    }
}

# Sessions

SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
# NOTE: This setting only affects the session cookie, not the expiration of the session
# being stored in the cache.  The session keys will expire according to the value of
# SESSION_COOKIE_AGE, which defaults to 2 weeks when no value is given.
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'
# A boolean that specifies whether Django's translation system should be enabled. This provides
# an easy way to turn it off, for performance. If this is set to False, Django will make some
# optimizations so as not to load the translation machinery.
USE_I18N = False

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_URL = '/static/'

STATIC_ROOT = os.path.normpath(os.path.join(BASE_DIR, 'http_static'))

# Logging
# https://docs.djangoproject.com/en/1.8/topics/logging/#configuring-logging

# Turn off default Django logging
# https://docs.djangoproject.com/en/1.8/topics/logging/#disabling-logging-configuration
LOGGING_CONFIG = None

_DEFAULT_LOG_LEVEL = SECURE_SETTINGS.get('log_level', logging.DEBUG)
_LOG_ROOT = SECURE_SETTINGS.get('log_root', '')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s\t%(asctime)s.%(msecs)03dZ\t%(name)s:%(lineno)s\t%(message)s',
            'datefmt': '%Y-%m-%dT%H:%M:%S'
        },
        'simple': {
            'format': '%(levelname)s\t%(name)s:%(lineno)s\t%(message)s',
        }
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        # Log to a text file that can be rotated by logrotate
        'default': {
            'class': 'logging.handlers.WatchedFileHandler',
            'level': _DEFAULT_LOG_LEVEL,
            'formatter': 'verbose',
            'filename': os.path.join(_LOG_ROOT, 'django-canvas_account_admin_tools.log'),
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
            'filters': ['require_debug_true'],
        },
        # Log to a text file that can be rotated by logrotate
        'app_logfile': {
            'level': _DEFAULT_LOG_LEVEL,
            'class': 'logging.handlers.WatchedFileHandler',
            'filename': os.path.join(_LOG_ROOT, 'django-icommons_lti_tools.log'),
            'formatter': 'verbose',
        },
    },
    # This is the default logger for any apps or libraries that use the logger
    # package, but are not represented in the `loggers` dict below.  A level
    # must be set and handlers defined.  Setting this logger is equivalent to
    # setting and empty string logger in the loggers dict below, but the separation
    # here is a bit more explicit.  See link for more details:
    # https://docs.python.org/2.7/library/logging.config.html#dictionary-schema-details
    'root': {
        'level': logging.WARNING,
        'handlers': ['default'],
    },
    'loggers': {
        'django': {
            'level': _DEFAULT_LOG_LEVEL,
            'handlers': ['default'],
            'propagate': False,
        },
        'canvas_account_admin_tools': {
            'level': _DEFAULT_LOG_LEVEL,
            'handlers': ['default'],
            'propagate': False,
        },
        'canvas_site_creator': {
            'level': _DEFAULT_LOG_LEVEL,
            'handlers': ['default'],
            'propagate': False,
        },
        'canvas_course_site_wizard': {
            'level': 'DEBUG',
            'handlers': ['console', 'app_logfile'],
            'propagate': False,
        },
        'course_info': {
            'level': _DEFAULT_LOG_LEVEL,
            'handlers': ['default'],
            'propagate': False,
        },
        'cross_list_courses': {
            'level': _DEFAULT_LOG_LEVEL,
            'handlers': ['default'],
            'propagate': False,
        },
    }
}

# Currently deployed environment
ENV_NAME = SECURE_SETTINGS.get('env_name', 'local')

# Other app specific settings

LTI_OAUTH_CREDENTIALS = SECURE_SETTINGS.get('lti_oauth_credentials', None)

CANVAS_URL = SECURE_SETTINGS.get('canvas_url', 'https://canvas.instructure.com')

# Used by canvas course site wizard jobs

CANVAS_SITE_SETTINGS = {
    'base_url': CANVAS_URL + '/',
}

CANVAS_SDK_SETTINGS = {
    'auth_token': SECURE_SETTINGS.get('canvas_token', None),
    'base_api_url': CANVAS_URL + '/api',
    'max_retries': 3,
    'per_page': 40,
    'session_inactivity_expiration_time_secs': 50,
}

ICOMMONS_COMMON = {
    'ICOMMONS_API_HOST': SECURE_SETTINGS.get('icommons_api_host', None),
    'ICOMMONS_API_USER': SECURE_SETTINGS.get('icommons_api_user', None),
    'ICOMMONS_API_PASS': SECURE_SETTINGS.get('icommons_api_pass', None),
    'CANVAS_API_BASE_URL': CANVAS_URL + '/api/v1',
    'CANVAS_API_HEADERS': {
        'Authorization': 'Bearer ' + SECURE_SETTINGS.get('canvas_token', 'canvas_token_missing_from_config')
    },
    'CANVAS_ROOT_ACCOUNT_ID': 1,
}

ICOMMONS_REST_API_HOST = SECURE_SETTINGS.get('icommons_rest_api_host', 'http://localhost:8000')
ICOMMONS_REST_API_TOKEN = SECURE_SETTINGS.get('icommons_rest_api_token')
ICOMMONS_REST_API_SKIP_CERT_VERIFICATION = False

PERMISSION_ACCOUNT_ADMIN_TOOLS = 'account_admin_tools'
PERMISSION_PEOPLE_TOOL = 'people_tool'
PERMISSION_XLIST_TOOL = 'cross_listing'
PERMISSION_SITE_CREATOR = 'manage_courses'


# in search courses, when you add a person to a course. This list
# controls which roles show up in the drop down. The list contains
# user role id's from the course manager database
ADD_PEOPLE_TO_COURSE_ALLOWED_ROLES_LIST = [0, 1, 2, 5, 7, 9, 10, 11, 12, 15]

BULK_COURSE_CREATION = {
    'log_long_running_jobs': True,
    'long_running_age_in_minutes': 30,
    'notification_email_subject': 'Sites created for {school} {term} term',
    'notification_email_body': 'Canvas course sites have been created for the '
                               '{school} {term} term.\n\n - {success_count} '
                               'course sites were created successfully.\n',
    'notification_email_body_failed_count': ' - {} course sites were not '
                                            'created.',
}

CANVAS_EMAIL_NOTIFICATION = {
    'from_email_address': 'icommons-bounces@harvard.edu',
    'support_email_address': 'tlt_support@harvard.edu',
    'course_migration_success_subject': 'Course site is ready',
    'course_migration_success_body': 'Success! \nYour new Canvas course site has been created and is ready for you at:\n'+
            ' {0} \n\n Here are some resources for getting started with your site:\n http://tlt.harvard.edu/getting-started#teachingstaff',

    'course_migration_failure_subject': 'Course site not created',
    'course_migration_failure_body': 'There was a problem creating your course site in Canvas.\n'+
            'Your local academic support staff has been notified and will be in touch with you.\n\n'+
            'If you have questions please contact them at:\n'+
            ' FAS: atg@fas.harvard.edu\n'+
            ' DCE/Summer: AcademicTechnology@dce.harvard.edu\n'+
            ' (Let them know that course site creation failed for sis_course_id: {0} ',

    'support_email_subject_on_failure': 'Course site not created',
    'support_email_body_on_failure': 'There was a problem creating a course site in Canvas via the wizard.\n\n'+
            'Course site creation failed for sis_course_id: {0}\n'+
            'User: {1}\n'+
            '{2}\n'+
            'Environment: {3}\n',
    'environment': ENV_NAME.capitalize(),
}
