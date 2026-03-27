
from pathlib import Path
from decouple import config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-d+6*inw(%6@q_1%vcaqg*2vitj-4u6u6mqwle!q#t58pn_%fni'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'videos',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'youtube_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'youtube_project.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'bliblioteca_youtube',
        'USER': 'root',
        'PASSWORD': '',
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {
            'charset': 'utf8mb4',
        }
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ============================================================
# CONFIGURACIÓN DE SESIONES (IMPORTANTE PARA OAUTH)
# ============================================================

# Usar sesiones en base de datos (más confiable que cache)
SESSION_ENGINE = 'django.contrib.sessions.backends.db'

# La sesión NO expira al cerrar el navegador
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

# Duración de la sesión: 1 día (86400 segundos)
SESSION_COOKIE_AGE = 86400

# Nombre de la cookie de sesión
SESSION_COOKIE_NAME = 'youtube_manager_sessionid'

# La cookie de sesión solo se envía sobre conexiones seguras en producción
SESSION_COOKIE_SECURE = False  # False para desarrollo, True para producción

# Prevenir JavaScript de acceder a la cookie de sesión
SESSION_COOKIE_HTTPONLY = True

# Permitir que la cookie se envíe en peticiones cross-site
SESSION_COOKIE_SAMESITE = 'Lax'

# Guardar sesión en cada request (importante para OAuth)
SESSION_SAVE_EVERY_REQUEST = True

# ============================================================
# CONFIGURACIÓN DE AUTENTICACIÓN
# ============================================================

# Redirigir a la página de inicio después de login
LOGIN_REDIRECT_URL = '/'

# Redirigir al login cuando se requiere autenticación
LOGIN_URL = '/login/'

# Redirigir después de logout
LOGOUT_REDIRECT_URL = '/'

# ============================================================
# YOUTUBE API & OAUTH CONFIGURATION
# ============================================================

# YouTube Data API v3
YOUTUBE_API_KEY = config('YOUTUBE_API_KEY')
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'

# OAuth 2.0
GOOGLE_CLIENT_ID = config('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = config('GOOGLE_CLIENT_SECRET')
GOOGLE_REDIRECT_URI = config('GOOGLE_REDIRECT_URI')

# Scopes para YouTube
YOUTUBE_SCOPES = [
    'https://www.googleapis.com/auth/youtube',
    'https://www.googleapis.com/auth/youtube.upload',
    'https://www.googleapis.com/auth/youtube.readonly',
]

# Configuración de cuotas
YOUTUBE_QUOTA_CONFIG = {
    'daily_limit': 15000,
    'warning_threshold': 12000,
    'enable_cache': True,
    'cache_ttl': 3600,
}

# Categorías de YouTube actualizadas 2026
YOUTUBE_CATEGORIES = {
    '1': 'Film & Animation',
    '2': 'Autos & Vehicles',
    '10': 'Music',
    '15': 'Pets & Animals',
    '17': 'Sports',
    '19': 'Travel & Events',
    '20': 'Gaming',
    '22': 'People & Blogs',
    '23': 'Comedy',
    '24': 'Entertainment',
    '25': 'News & Politics',
    '26': 'Howto & Style',
    '27': 'Education',
    '28': 'Science & Technology',
    '29': 'Nonprofits & Activism',
    '44': 'Shorts',
}

SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SAMESITE = 'Lax'

CSRF_TRUSTED_ORIGINS = [
    "http://127.0.0.1:8000",
    "http://localhost:8000",
]

# settings.py

# Permite que la cookie de sesión se envíe de vuelta desde Google
SESSION_COOKIE_SAMESITE = 'Lax'

# Como estás en HTTP (sin S), asegúrate de que esto sea False
SESSION_COOKIE_SECURE = False

LOGOUT_REDIRECT_URL = 'videos:inicio'

import os

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'