from pathlib import Path
from decouple import config, Csv
import os

BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY
DEBUG = config('DJANGO_DEBUG', cast=bool, default=False)
SECRET_KEY = config('DJANGO_SECRET_KEY', default='django-insecure-temp-key')

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core',  # Nuestra app
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'core.middleware.no_cache.NoCacheMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'dulceria_lilis.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'core' / 'templates'],
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

WSGI_APPLICATION = 'dulceria_lilis.wsgi.application'

# ===============================================
# CONFIGURACIÓN DE BASE DE DATOS MYSQL (AWS RDS)
# ===============================================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME':     config('DB_NAME'),
        'USER':     config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST':     config('DB_HOST'),
        'PORT':     config('DB_PORT', cast=int, default=3306),
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            'charset': 'utf8mb4',
        },
    }
}


ALLOWED_HOSTS = config(
    'DJANGO_ALLOWED_HOSTS',
    cast=Csv(),
    default='3.223.202.82,localhost,127.0.0.1'
)
CSRF_TRUSTED_ORIGINS = config(
    'DJANGO_CSRF_TRUSTED',
    cast=Csv(),
    default='http://3.223.202.82,https://3.223.202.82'
)



# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 12}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]
SECRET_KEY = config('DJANGO_SECRET_KEY', default='django-insecure-temp-key')
# Internationalization
LANGUAGE_CODE = config('DJANGO_LANGUAGE_CODE', default='es-cl')
TIME_ZONE = config('DJANGO_TIME_ZONE', default='America/Santiago')
USE_I18N = True
USE_TZ = True

# Static files
# Static files


STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Añade esta línea si tienes archivos estáticos propios
#STATICFILES_DIRS = [
 #   BASE_DIR / 'static',
#]

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Login URL
LOGIN_URL = 'core:login'
LOGIN_REDIRECT_URL = 'core:dashboard'

# duración de la cookie de sesión (en segundos)
SESSION_COOKIE_AGE = 60*60*2 # 2 horas 
# sesión expira al cerrar el navegador?
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
# cada vez que se hace una petición, se actualiza la expiración
SESSION_SAVE_EVERY_REQUEST = False
# seguridad de las cookies
SESSION_COOKIE_SECURE = False # en producción con HTTPS
# sólo enviar la cookie en el mismo sitio (protección CSRF) / Lax por defecto en Django
SESSION_COOKIE_SAMESITE = 'Lax' # o 'Strict'/'None'(+Secure)

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
PASSWORD_RESET_TIMEOUT = 3600
