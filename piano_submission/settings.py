
"""
Django settings for piano_submission project.
For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/
For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os, sys
from django.core.urlresolvers import reverse_lazy
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'ap5%93+6$rquw*#0(z6!l425i2ls)-9##b!3zv^xz$7t68=-0%'

AUTH_USER_MODEL = 'db.User'

# SECURITY WARNING: don't run with debug turned on in production!
if 'linux' in sys.platform.lower():
    DEBUG = False
    TEMPLATE_DEBUG = False
    ALLOWED_HOSTS = []
else:
    DEBUG = True
    TEMPLATE_DEBUG = True
    ALLOWED_HOSTS = []

LOGIN_REDIRECT_URL = reverse_lazy("homepage")

# Application definition

INSTALLED_APPS = (
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'mviews',
    'db'
)

ROUTE_AUTO_CREATE = "app_module_view"
REGISTER_VIEWS_PY_FUNCS = False
RETURN_SINGLES = False

MIDDLEWARE_CLASSES = (
    'django.middleware.gzip.GZipMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware'
)

ROOT_URLCONF = 'piano_submission.urls'

WSGI_APPLICATION = 'piano_submission.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

if 'win32' not in sys.platform.lower():
    pwd = 'systemtestrocks!!'
else:
    pwd = 'Is systemtest an aw3some team?'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'p_lessons',
        'USER': 'postgres',
        'PASSWORD': pwd,
        'HOST': 'localhost',
        'PORT': ''
    },
    'OPTIONS' : {
        'autocommit' : True,
    }
}


OPTIONS = {
        'CULL_FREQUENCY' : 0
    }

CONN_MAX_AGE = 60*17

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/Denver'

USE_I18N = False

USE_L10N = False

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

    # Absolute filesystem path to the directory that will hold user-uploaded files.
    # Example: "/home/media/media.lawrence.com/media/"
if 'linux' in sys.platform.lower():
    MEDIA_ROOT = '/data/'
else:
    MEDIA_ROOT = 'C:\\Users\\derigible\\test_data\\parsed_xlgs'
    
#add the systemtest tools directory to the python path 
if 'linux' not in sys.platform.lower():
    JSON_INDENT = -1
    JSON_SORT = False
else:
    JSON_INDENT = -1
    JSON_SORT = False

    # URL that handles the media served from MEDIA_ROOT. Make sure to use a
    # trailing slash.
    # Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'

STATIC_URL = '/static/'

    # Absolute path to the directory static files should be collected to.
    # Don't put anything in this directory yourself; store your static files
    # in apps' "static/" subdirectories and in STATICFILES_DIRS.
    # Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = ''

    # Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    "C:/Users/derigible/workspace/piano_submission/static/",
    "/p_lessons/static",
    )

    # List of finder classes that know how to find static files in
    # various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    #    'django.contrib.staticfiles.finders.DefaultStorageFinder',
    )

TEMPLATE_DIRS = (
    "C:/Users/derigible/workspace/piano_submission/templates/",
    "/p_lessons/templates/", #prod server needs this to be explicit
)

if 'linux' in sys.platform.lower():
    TEMPLATE_LOADERS = (
        ('django.template.loaders.cached.Loader', (
            'django.template.loaders.filesystem.Loader',
            'django.template.loaders.app_directories.Loader',
        )),
    )

file_root = '/var/log/django/' if 'linux' in sys.platform.lower()  else os.path.join('C:\\Users', 'derigible', 'logs')
if not os.path.exists(file_root):
    os.mkdir(file_root, 0o755)

if 'linux' in sys.platform.lower():
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': True,
        'formatters': {
            'verbose': {
                'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
            },
            'simple': {
                'format': '[%(levelname)s] [%(asctime)s] [%(module)s]: %(message)s'
            },
        },
        'filters': {
            'require_debug_false': {
                '()': 'django.utils.log.RequireDebugFalse'
            },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
            }
         },
        'handlers': {
            'null': {
                'level': 'DEBUG',
                'class': 'logging.NullHandler',
            },
            'mail_admins': {
                'level': 'ERROR',
                'filters': ['require_debug_false'],
                'class': 'django.utils.log.AdminEmailHandler',
                'formatter': 'simple'
                },
            'file_request': {
                'level': 'WARNING',
                'class': 'logging.handlers.RotatingFileHandler',   
                'filename': os.path.join(file_root, 'request.log'),
                'maxBytes': 1024*1024*1, # 1MB
                'backupCount': 0,
                'formatter': 'simple'
                },    
            'file_backend': {
                'level': 'DEBUG',
                'class': 'logging.handlers.RotatingFileHandler',
                'filters': ['require_debug_true'],    
                'filename': os.path.join(file_root, 'backend.log'),
                'maxBytes': 1024*1024*6, # 6MB
                'backupCount': 0,
                'formatter': 'simple'
                },    
            'file_security': {
                'level': 'DEBUG',
                'class': 'logging.handlers.RotatingFileHandler',   
                'filename': os.path.join(file_root, 'security.log'),
                'maxBytes': 1024*1024*6, # 6MB
                'backupCount': 0,
                'formatter': 'simple'
                },    
            'file_migrations': {
                'level': 'DEBUG',
                'class': 'logging.handlers.RotatingFileHandler',   
                'filename': os.path.join(file_root, 'migrations.log'),
                'maxBytes': 1024*1024*1, # 1MB
                'backupCount': 0,
                'formatter': 'simple'
                },    
            'file_debug': {
                'level': 'INFO',
                'class': 'logging.handlers.RotatingFileHandler', 
                'filename': os.path.join(file_root, 'debug.log'),
                'maxBytes': 1024*1024*1, # 1MB
                'backupCount': 0,
                'formatter': 'verbose'
                },    
         },
        'loggers': {
            'django': {
                'handlers': ['null'],
                'propagate': True,
                'level': 'INFO',
                },
            'django.request': {
                'handlers': ['file_request'],
                'level': 'WARNING',
                'propagate': True,
                },
            'django.security': {
                'handlers': ['file_security'],
                'level': 'INFO',
                'propagate': True,
                },
            'django.db.backends': {
                'handlers': ['file_backend'],
                'level': 'DEBUG',
                'propagate': False,
                },
            'django.db.backends.schema': {
                'handlers': ['file_migrations'],
                'level': 'DEBUG',
                'propagate': False,
                },
            'p_lessons': {
                'handlers': ['file_debug'],
                'level': 'INFO',
                'propagate': True,
                },
        }
    }
else:
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
