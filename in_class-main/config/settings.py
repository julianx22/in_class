"""
Django settings for config project.
"""

from pathlib import Path
import os  # <- NECESARIO para leer variables de entorno

# =======================
# Paths
# =======================
BASE_DIR = Path(__file__).resolve().parent.parent

# =======================
# Core
# =======================
SECRET_KEY = 'django-insecure-o@9$jwqcq-jm%8&e_rja97i(f=2nfp0r_i2coh3-eu-6nlv1#*'
DEBUG = True
# config/settings.py
ALLOWED_HOSTS = ['127.0.0.1', 'localhost', '192.168.80.79', '192.168.80.77','172.16.101.11'] 
# si te cansas de actualizar: ALLOWED_HOSTS = ['*']  # solo en dev

CSRF_TRUSTED_ORIGINS = [
    'http://127.0.0.1:8000',
    'http://localhost:8000',
    'http://192.168.80.79:8000',
    'http://192.168.80.77:8000',
    'http://192.168.80.77:8000',
    'http://172.16.110.217:8000',
    
]



# =======================
# Apps
# =======================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Tu backend legacy y tu app
    'inclass_legacy.apps.InClassLegacyConfig',
    'core',
]

# =======================
# Middleware
# =======================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

# =======================
# Templates
# =======================
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # Muy importante para que encuentre templates/pages/*.html y registration/login.html
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# =======================
# Database
# =======================
DATABASES = {
    'default': {
        "ENGINE": "mssql",
        "NAME": "in_Class",
        "HOST": r"Hp_Pavilion-96\SQLEXPRESS",
        "OPTIONS": {
            "driver": "ODBC Driver 18 for SQL Server",
            "extra_params": "Encrypt=yes;TrustServerCertificate=yes;",
        },
    }
}

# =======================
# Auth
# =======================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

AUTHENTICATION_BACKENDS = [
    "inclass_legacy.backends.LegacyBackend",
    "django.contrib.auth.backends.ModelBackend",
]

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/home/'      # cámbialo a '/' si no tienes home
LOGOUT_REDIRECT_URL = '/login/'

# =======================
# I18N / TZ
# =======================
LANGUAGE_CODE = 'es'
TIME_ZONE = 'America/Bogota'   # <-- antes tenías 'UTC'
USE_I18N = True
USE_TZ = True

# =======================
# Static & Media
# =======================
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

# Si más adelante usas media:
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# =======================
# Django defaults
# =======================
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# =======================
# Email (SMTP con fallback a consola)
# =======================
# Var de entorno:
#   EMAIL_HOST_USER = "inclass49@gmail.com"
#   EMAIL_HOST_PASSWORD = "<tu App Password>"
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "inclass49@gmail.com")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "eqbultiotpivveag")

if EMAIL_HOST_PASSWORD:
    # Enviar correos reales
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
    EMAIL_HOST = "smtp.gmail.com"
    EMAIL_PORT = 587
    EMAIL_USE_TLS = True
else:
    # Fallback: imprime emails en consola
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

DEFAULT_FROM_EMAIL = "In Class <inclass49@gmail.com>"
