"""
Django settings for project.

Generated by 'django-admin startproject' using Django 1.8.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""

import logging
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import time

from dj_secure_settings.loader import load_secure_settings
from django.urls import reverse_lazy
from harvard_django_utils.logging import JSON_LOG_FORMAT

SECURE_SETTINGS = load_secure_settings()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

SILENCED_SYSTEM_CHECKS = ['fields.W342']

# THESE ADDRESSES WILL RECEIVE EMAIL ABOUT CERTAIN ERRORS!
# Note: If this list (technically a tuple) has only one element, that
#       element must be followed by a comma for it to be processed
#       (cf section 3.2 of https://docs.python.org/2/reference/datamodel.html)
ADMINS = (
    ('iCommons Tech', 'icommons-technical@g.harvard.edu'),
)

MANAGERS = ADMINS
ENV_NAME = SECURE_SETTINGS.get('env_name', 'local')

# This is the address that admin emails (sent to the addresses in the ADMINS list) will be sent 'from'.
# It can be overridden in specific settings files to indicate what environment
# is producing admin emails (e.g. 'app env <email>').
SERVER_EMAIL_DISPLAY_NAME = 'canvas_account_admin_tools - %s' % ENV_NAME
SERVER_EMAIL = '%s <%s>' % (SERVER_EMAIL_DISPLAY_NAME, 'icommons-bounces@harvard.edu')

# Email subject prefix is what's shown at the beginning of the ADMINS email subject line
# Django's default is "[Django] ", which isn't helpful and wastes space in the subject line
# So this overrides the default and removes that unhelpful [Django] prefix.
# Specific settings files can override, for example to show the settings file being used:
# EMAIL_SUBJECT_PREFIX = '[%s] ' % SERVER_EMAIL_DISPLAY_NAME
# TLT-458: currently the tech_logger inserts its own hostname prefix if available, so this
#          is not being overridden in environment settings files at present.
EMAIL_SUBJECT_PREFIX = ''

# Application definition

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'async_operations',
    'bulk_utilities',
    'canvas_account_admin_tools',
    'canvas_course_site_wizard',
    'canvas_site_creator',
    'course_info',
    'crispy_forms',
    'cross_list_courses',
    'django_auth_lti',
    'django_cas_ng',
    'django_rq',
    'djng',
    'icommons_common',
    'coursemanager',
    'icommons_ui',
    'lti_permissions',
    'lti_school_permissions',
    'people_tool',
    'proxy',
    'publish_courses',
    'bulk_course_settings',
    'canvas_site_deletion',
    'masquerade_tool',
    'self_enrollment_tool',
    'pylti1p3.contrib.django.lti1p3_tool_config',
    'self_unenrollment_tool',
    'rest_framework',
    'watchman'
]


MIDDLEWARE = [
    # NOTE - djng needs to be the first item in this list
    'djng.middleware.AngularUrlMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'cached_auth.Middleware',
    'django_auth_lti.middleware_patched.MultiLTILaunchAuthMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'allow_cidr.middleware.AllowCIDRMiddleware'
]

AUTHENTICATION_BACKENDS = [
    'django_auth_lti.backends.LTIAuthBackend',
    'django.contrib.auth.backends.ModelBackend',
    'harvardkey_cas.backends.CASAuthBackend',
]

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
DATABASE_MIGRATION_WHITELIST = ['default']
DATABASE_ROUTERS = ['icommons_common.routers.CourseSchemaDatabaseRouter', ]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': SECURE_SETTINGS.get('db_default_name', 'canvas_account_admin_tools'),
        'USER': SECURE_SETTINGS.get('db_default_user', 'postgres'),
        'PASSWORD': SECURE_SETTINGS.get('db_default_password'),
        'HOST': SECURE_SETTINGS.get('db_default_host', '127.0.0.1'),
        'PORT': SECURE_SETTINGS.get('db_default_port', 5432),  # Default postgres port
    },
    'coursemanager': {
        'ENGINE': 'django.db.backends.oracle',
        'NAME': SECURE_SETTINGS.get('db_coursemanager_name'),
        'USER': SECURE_SETTINGS.get('db_coursemanager_user'),
        'PASSWORD': SECURE_SETTINGS.get('db_coursemanager_password'),
        'HOST': SECURE_SETTINGS.get('db_coursemanager_host'),
        'PORT': str(SECURE_SETTINGS.get('db_coursemanager_port')),
        'OPTIONS': {
            'threaded': True,
        },
        'CONN_MAX_AGE': 0,
    }
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Cache
# https://docs.djangoproject.com/en/1.8/ref/settings/#std:setting-CACHES
# Note as well: RQ_QUEUES cache settings below should match the LOCATION of
# the redis server (including DB number)

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

MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'

# RQ
# http://python-rq.org/docs/

RQWORKER_QUEUE_NAME = 'bulk_publish_canvas_sites'

_rq_redis_config = {
    'HOST': REDIS_HOST,
    'PORT': REDIS_PORT,
    'DB': 0,
    'DEFAULT_TIMEOUT': SECURE_SETTINGS.get('default_rq_timeout_secs', 300),
}

RQ_QUEUES = {
    'default': _rq_redis_config,
    RQWORKER_QUEUE_NAME: _rq_redis_config
}

# Sessions

SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
# NOTE: This setting only affects the session cookie, not the expiration of the session
# being stored in the cache.  The session keys will expire according to the value of
# SESSION_COOKIE_AGE, which defaults to 2 weeks when no value is given.
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_SAMESITE = 'None'
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_SAMESITE = 'None'

# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/New_York'
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
# https://docs.djangoproject.com/en/2.2/topics/logging/#configuring-logging

# Make sure log timestamps are in GMT
logging.Formatter.converter = time.gmtime

_DEFAULT_LOG_LEVEL = SECURE_SETTINGS.get('log_level', logging.DEBUG)
_LOG_ROOT = SECURE_SETTINGS.get('log_root', '')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s\t%(asctime)s.%(msecs)03dZ\t%(name)s:%(lineno)s\t%(message)s',
            'datefmt': '%Y-%m-%dT%H:%M:%S'
        },
        'json': {
            '()': 'pythonjsonlogger.jsonlogger.JsonFormatter',
            'format': JSON_LOG_FORMAT,
        },
        'simple': {
            'format': '%(levelname)s\t%(name)s:%(lineno)s\t%(message)s',
        }
    },
    'filters': {
        'context': {
            '()': 'icommons_common.logging.ContextFilter',
            'env': SECURE_SETTINGS.get('env_name'),
            'project': 'canvas_account_admin_tools',
            'department': 'uw',
        },
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        }
    },
    'handlers': {
        'default': {
            'class': 'splunk_handler.SplunkHandler',
            'formatter': 'json',
            'sourcetype': 'json',
            'source': 'django-canvas_account_admin_tools',
            'host': 'http-inputs-harvard.splunkcloud.com',
            'port': '443',
            'index': 'soc-isites',
            'token': SECURE_SETTINGS['splunk_token'],
            'level': _DEFAULT_LOG_LEVEL,
            'filters': ['context'],
        },
        'gunicorn': {
            'class': 'splunk_handler.SplunkHandler',
            'formatter': 'json',
            'sourcetype': 'json',
            'source': 'gunicorn-canvas_account_admin_tools',
            'host': 'http-inputs-harvard.splunkcloud.com',
            'port': '443',
            'index': 'soc-isites',
            'token': SECURE_SETTINGS['splunk_token'],
            'level': _DEFAULT_LOG_LEVEL,
            'filters': ['context'],
        },
        'console': {
            'level': _DEFAULT_LOG_LEVEL,
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
            'filters': ['require_debug_true'],
        }
    },
    # This is the default logger for any apps or libraries that use the logger
    # package, but are not represented in the `loggers` dict below.  A level
    # must be set and handlers defined.  Setting this logger is equivalent to
    # setting and empty string logger in the loggers dict below, but the separation
    # here is a bit more explicit.  See link for more details:
    # https://docs.python.org/2.7/library/logging.config.html#dictionary-schema-details
    'root': {
        'level': logging.WARNING,
        'handlers': ['console', 'default'],
    },
    'loggers': {
        'gunicorn': {
            'handlers': ['gunicorn', 'console'],
            'level': logging.WARNING,
            'propagate': False,
        },
        'bulk_utilities': {
            'level': _DEFAULT_LOG_LEVEL,
            'handlers': ['console', 'default'],
            'propagate': False,
        },
        'canvas_account_admin_tools': {
            'level': _DEFAULT_LOG_LEVEL,
            'handlers': ['console', 'default'],
            'propagate': False,
        },
        'canvas_course_site_wizard': {
            'level': _DEFAULT_LOG_LEVEL,
            'handlers': ['console', 'default'],
            'propagate': False,
        },
        'canvas_site_creator': {
            'level': _DEFAULT_LOG_LEVEL,
            'handlers': ['console', 'default'],
            'propagate': False,
        },
        'canvas_site_deletion': {
            'level': _DEFAULT_LOG_LEVEL,
            'handlers': ['console', 'default'],
            'propagate': False,
        },
        'masquerade_tool': {
            'level': _DEFAULT_LOG_LEVEL,
            'handlers': ['console', 'default'],
            'propagate': False,
        },
        'self_enrollment_tool': {
            'level': _DEFAULT_LOG_LEVEL,
            'handlers': ['console', 'default'],
            'propagate': False,
        },
        'self_unenrollment_tool': {
            'level': _DEFAULT_LOG_LEVEL,
            'handlers': ['console', 'default'],
            'propagate': False,
        },
        'course_info': {
            'level': _DEFAULT_LOG_LEVEL,
            'handlers': ['console', 'default'],
            'propagate': False,
        },
        'cross_list_courses': {
            'level': _DEFAULT_LOG_LEVEL,
            'handlers': ['console', 'default'],
            'propagate': False,
        },
        'publish_courses': {
            'level': _DEFAULT_LOG_LEVEL,
            'handlers': ['console', 'default'],
            'propagate': False,
        },
        'bulk_course_settings': {
            'level': _DEFAULT_LOG_LEVEL,
            'handlers': ['console', 'default'],
            'propagate': False,
        },
        'rq.worker': {
            'level': _DEFAULT_LOG_LEVEL,
            'handlers': ['console', 'default'],
            'propagate': False,
        },
        'canvas_sdk': {
            'level': _DEFAULT_LOG_LEVEL,
            'handlers': ['console', 'default'],
            'propagate': False,
        },
        'django_auth_lti': {
            'level': logging.ERROR,
            'handlers': ['console', 'default'],
            'propagate': False,
        },
    }
}

# Currently deployed environment
ENV_NAME = SECURE_SETTINGS.get('env_name', 'local')

# Other app specific settings

LTI_OAUTH_CREDENTIALS = SECURE_SETTINGS.get('lti_oauth_credentials', None)

CANVAS_URL = SECURE_SETTINGS.get('canvas_url', 'https://canvas.instructure.com')

# Used by canvas_course_site_wizard jobs invoked by Canvas Site creator

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
PERMISSION_SEARCH_COURSES = 'search_courses'  # aka course_info
PERMISSION_PEOPLE_TOOL = 'people_tool'
PERMISSION_XLIST_TOOL = 'cross_listing'
PERMISSION_SITE_CREATOR = 'manage_courses'
PERMISSION_PUBLISH_COURSES = 'publish_courses'
PERMISSION_BULK_COURSE_SETTING = 'bulk_course_settings'
PERMISSION_CANVAS_SITE_DELETION = 'canvas_site_deletion'
PERMISSION_SELF_ENROLLMENT_TOOL = 'self_enrollment_tool'
PERMISSION_MASQUERADE_TOOL = 'masquerade_tool'

LTI_SCHOOL_PERMISSIONS_TOOL_PERMISSIONS = (
    PERMISSION_ACCOUNT_ADMIN_TOOLS,
    PERMISSION_SEARCH_COURSES,
    PERMISSION_PEOPLE_TOOL,
    PERMISSION_XLIST_TOOL,
    PERMISSION_SITE_CREATOR,
    PERMISSION_PUBLISH_COURSES,
    PERMISSION_BULK_COURSE_SETTING,
    PERMISSION_CANVAS_SITE_DELETION,
    PERMISSION_SELF_ENROLLMENT_TOOL,
    PERMISSION_MASQUERADE_TOOL,
)

# in search courses, when you add a person to a course. This list
# controls which roles show up in the drop down. The list contains
# user role id's from the course manager database
ADD_PEOPLE_TO_COURSE_ALLOWED_ROLES_LIST = [0, 1, 2, 5, 6, 7, 9, 10, 11, 12, 14, 15, 16, 18, 19,
                                           20, 22, 23, 24, 25, 26, 27, 28, 400, 401]

# These are the roles available when configuring self-enrollment for a course
SELF_ENROLLMENT_TOOL_ROLES_LIST = SECURE_SETTINGS.get('self_enrollment_roles', [0,10,14])

# This is the LTI 1.3 client_id for the self-unenrollment tool; this tool will be installed
# into the Canvas course site when a course is enabled for self-enrollment.
SELF_UNENROLL_CLIENT_ID = SECURE_SETTINGS.get('self_unenroll_client_id', None)

SELF_ENROLL_HOSTNAME = SECURE_SETTINGS.get('self_enroll_hostname', 'self_enroll_hostname_setting_missing')

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


BULK_COURSE_SETTINGS = {
    'aws_region_name':  SECURE_SETTINGS.get('aws_region_name', 'us-east-1'),
    's3_bucket': SECURE_SETTINGS.get('bulk_course_settings_s3_bucket'),
    'aws_access_key_id': SECURE_SETTINGS.get('aws_access_key_id'),
    'aws_secret_access_key': SECURE_SETTINGS.get('aws_secret_access_key'),
    'job_queue_name': SECURE_SETTINGS.get('job_queue_name'),
    'visibility_timeout': SECURE_SETTINGS.get('visibility_timeout', 120),

}

CANVAS_EMAIL_NOTIFICATION = {
    'from_email_address': 'icommons-bounces@harvard.edu',
    'support_email_address': 'tlt_support@harvard.edu',
    'course_migration_success_subject': 'Course site is ready',
    'course_migration_success_body': 'Success! \nYour new Canvas course site has been created and is ready for you at:\n' +
            ' {0} \n\n Here are some resources for getting started with your site:\n http://tlt.harvard.edu/getting-started#teachingstaff',

    'course_migration_failure_subject': 'Course site not created',
    'course_migration_failure_body': 'There was a problem creating your course site in Canvas.\n' +
            'Your local academic support staff has been notified and will be in touch with you.\n\n' +
            'If you have questions please contact them at:\n' +
            ' FAS: atg@fas.harvard.edu\n' +
            ' DCE/Summer: AcademicTechnology@dce.harvard.edu\n' +
            ' (Let them know that course site creation failed for sis_course_id: {0} ',

    'support_email_subject_on_failure': 'Course site not created',
    'support_email_body_on_failure': 'There was a problem creating a course site in Canvas via the wizard.\n\n' +
            'Course site creation failed for sis_course_id: {0}\n' +
            'User: {1}\n' +
            '{2}\n' +
            'Environment: {3}\n',
    'environment': ENV_NAME.capitalize(),
}

MASQUERADE_TOOL_SETTINGS = {
    'aws_region_name':  SECURE_SETTINGS.get('aws_region_name', 'us-east-1'),
    'temporary_masquerade_function_arn': SECURE_SETTINGS.get('temporary_masquerade_function_arn'),
    'masquerade_session_minutes': SECURE_SETTINGS.get('masquerade_session_minutes', 60),
}


REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 10,  # default result set size without a limit GET param
    'DEFAULT_RENDERER_CLASSES': ('rest_framework.renderers.JSONRenderer',),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',),
    'TEST_REQUEST_DEFAULT_FORMAT': 'json',
}

WATCHMAN_TOKENS = SECURE_SETTINGS['watchman_token']
WATCHMAN_TOKEN_NAME = SECURE_SETTINGS['watchman_token_name']
WATCHMAN_CHECKS = (
    'watchman.checks.databases',
    'watchman.checks.caches',
)

try:
    from build_info import BUILD_INFO
except ImportError:
    BUILD_INFO = {}
