
"""
Django settings for pianoly project.
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

ROOT_URLCONF = 'pianoly.urls'

WSGI_APPLICATION = 'pianoly.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

pwd = 'systemtestrocks!!'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'pianoly',
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
    "D:/python/pianoly/static",
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
    "C:/Users/derigible/workspace/pianoly/templates/",
    "/p_lessons/templates/", #prod server needs this to be explicit
)

if 'linux' in sys.platform.lower():
    TEMPLATE_LOADERS = (
        ('django.template.loaders.cached.Loader', (
            'django.template.loaders.filesystem.Loader',
            'django.template.loaders.app_directories.Loader',
        )),
    )


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
