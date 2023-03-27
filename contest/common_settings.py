import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DEBUG = False

SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'django.forms',
    'ckeditor',
    'ckeditor_uploader',
    'pagedown',
    'accounts',
    'contests',
    'schedule',
    'support',
    'contest_telegram_bot',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    #'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'contest.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'contest/templates'),
        ],
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

FORM_RENDERER = 'django.forms.renderers.TemplatesSetting'

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

WSGI_APPLICATION = 'contest.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'contest',
        'USER': 'contest',
        'PASSWORD': 'contest',
        'HOST': '127.0.0.1',
        'PORT': '3306',
        'TEST': {
            'CHARSET': 'utf8',
            'COLLATION': 'utf8_general_ci',
        },
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'ru-ru'

TIME_ZONE = 'Europe/Moscow'

USE_I18N = True

USE_L10N = True

USE_TZ = True

CONTEST_DOMAIN = 'contest.msu.uz'

LOGIN_URL = '/login'
LOGIN_REDIRECT_URL = '/'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

CELERY_RESULT_BACKEND = 'db+mysql://celery:celery@localhost/celery'
CELERY_RESULT_ACCEPT_CONTENT = ['json']
CELERY_DATABASE_SHORT_LIVED_SESSIONS = True
CELERY_TASK_TRACK_STARTED = True

FILE_UPLOAD_PERMISSIONS = 0o640

MEDIA_ROOT = os.path.join(BASE_DIR, 'upload/')
MEDIA_URL = '/upload/'

STATIC_ROOT = os.path.join(BASE_DIR, 'static/')
STATIC_URL = '/static/'

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'contest/static/'),
]

CKEDITOR_UPLOAD_PATH = 'uploads/'
CKEDITOR_ALLOW_NONIMAGE_FILES = False
CKEDITOR_CONFIGS = {
    'default': {
        'skin': 'moono-lisa',
        'toolbar_CustomToolbarConfig': [
            {'name': 'clipboard', 'items': ['Undo', 'Redo', '-', 'Cut', 'Copy', 'Paste']},
            {'name': 'basicstyles',
             'items': ['Bold', 'Italic', 'Underline', 'Strike', 'codeTag', 'Subscript', 'Superscript', '-', 'RemoveFormat']},
            {'name': 'colors', 'items': ['TextColor']},
            {'name': 'paragraph',
             'items': ['NumberedList', 'BulletedList', '-', 'Outdent', 'Indent', '-', 'Blockquote', '-',
                       'JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock']},
            {'name': 'links', 'items': ['Link', 'Unlink']},
            {'name': 'insert', 'items': ['Image', 'Table', 'HorizontalRule']},
            {'name': 'styles', 'items': ['Styles', 'Format', 'Font', 'FontSize']},
            {'items': [
                # put the name of your editor.ui.addButton here
                'Maximize',
            ]},
        ],
        'toolbar': 'CustomToolbarConfig',  # put selected toolbar config here
        'width': '100%',
        'tabSpaces': 4,
        'extraPlugins': ','.join([
            'uploadimage',  # the upload image feature
            'autolink',
            'autoembed',
            'embedsemantic',
            'autogrow',
            'lineutils',
            'clipboard',
            'elementspath',
            'pastefromword',
            'mathjax',
            'table',
        ]),
    },
    'minimal': {
        'skin': 'moono-lisa',
        'toolbar_MinimalToolbarConfig': [
            {'name': 'clipboard', 'items': ['Undo', 'Redo', '-', 'Cut', 'Copy', 'Paste']},
            {'name': 'basicstyles',
             'items': ['Bold', 'Italic', 'Underline', 'Strike', 'codeTag', 'Subscript', 'Superscript', '-', 'RemoveFormat']},
            {'name': 'colors', 'items': ['TextColor']},
            {'name': 'paragraph',
             'items': ['NumberedList', 'BulletedList', '-', 'Outdent', 'Indent', '-', 'Blockquote', '-',
                       'JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock']},
            {'name': 'insert',
             'items': ['Table', 'HorizontalRule']},
            {'name': 'styles', 'items': ['Styles', 'Format']},
            {'items': [
                # put the name of your editor.ui.addButton here
                'Maximize',
            ]},
        ],
        'toolbar': 'MinimalToolbarConfig',  # put selected toolbar config here
        'width': '100%',
        'tabSpaces': 4,
        'extraPlugins': ','.join([
            'uploadimage',  # the upload image feature
            'autolink',
            'autoembed',
            'embedsemantic',
            'autogrow',
            'lineutils',
            'clipboard',
            'pastefromword',
            'mathjax',
            'table',
        ]),
        'removePlugins': ','.join([
            'elementspath',
        ]),
    }
}
