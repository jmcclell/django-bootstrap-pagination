import os


BASE_DIR = os.path.dirname(__file__)
SETTINGS_MODULE = "tests.test_settings"

INSTALLED_APPS = (
    'bootstrap_pagination',
)

DATABASES = {}
MIDDLEWARE_CLASSES = ()

ROOT_URLCONF = 'tests.test_settings.urls'
SECRET_KEY = 'secretkey'
SITE_ROOT = '.'


TEMPLATE_DEBUG = True
TEMPLATE_DIRS = ()

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': TEMPLATE_DIRS,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
            ],
            'debug': TEMPLATE_DEBUG,
        },
    },
]

urls = []
