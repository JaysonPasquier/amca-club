"""
Django settings for amca project.
"""

import os
import sys
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-amca-project-secret-key-change-in-production'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0', '.ngrok.io', '.ngrok-free.app', 'ab4e-176-133-46-196.ngrok-free.app']

# Add CSRF trusted origins for ngrok domain
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:8000',
    'http://127.0.0.1:8000',
    'https://*.ngrok-free.app',
    'https://sensible-horribly-raven.ngrok-free.app',
    'https://amc-f.com',
]

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party apps
    'rest_framework',
    'corsheaders',
    'crispy_forms',
    'crispy_bootstrap5',

    # Custom apps
    'core',
    'accounts',
    'api',
    'forum',  # Ajouter l'application forum ici
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'amca.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'core.context_processors.club_info',  # Ajout du processeur de contexte
            ],
        },
    },
]

WSGI_APPLICATION = 'amca.wsgi.application'

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

# Switch to SQLite for easier development setup
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Commented out PostgreSQL config for future reference
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': 'amca_db',
#         'USER': 'scorpio',
#         'PASSWORD': '',
#         'HOST': 'localhost',
#         'PORT': '5432',
#     }
# }

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'fr-fr'  # Changer de 'en-us' à 'fr-fr'
TIME_ZONE = 'Europe/Paris'  # Adapter à votre fuseau horaire
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# Dynamic media and static path configuration
# Check if we're running on production server
if '/var/www/vhosts/amc-f.com' in str(BASE_DIR):
    # Production paths
    MEDIA_URL = '/media/'
    MEDIA_ROOT = os.path.join(str(BASE_DIR).replace('/home/scorpio/personall-website', '/var/www/vhosts/amc-f.com/httpdocs/amca-club'), 'media')
    STATIC_ROOT = os.path.join(str(BASE_DIR).replace('/home/scorpio/personall-website', '/var/www/vhosts/amc-f.com/httpdocs/amca-club'), 'staticfiles')
else:
    # Development paths
    MEDIA_URL = '/media/'
    MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
    STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Ensure media directories exist with proper permissions
import os
try:
    os.makedirs(MEDIA_ROOT, exist_ok=True)
    # Give full permissions to ensure writability
    os.chmod(MEDIA_ROOT, 0o777)

    for directory in ['profile_images', 'banner_images', 'posts']:
        dir_path = os.path.join(MEDIA_ROOT, directory)
        os.makedirs(dir_path, exist_ok=True)
        # Give full permissions to the directories too
        os.chmod(dir_path, 0o777)
except Exception as e:
    print(f"Error setting permissions: {e}")

# File permission settings (less restrictive)
FILE_UPLOAD_PERMISSIONS = 0o666
FILE_UPLOAD_DIRECTORY_PERMISSIONS = 0o777

# Media file settings
FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
MEDIA_FILE_EXTENSIONS = ['jpg', 'jpeg', 'png', 'gif']
MAX_UPLOAD_SIZE = 5242880  # 5MB

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Crispy Forms
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# CORS settings
CORS_ALLOW_ALL_ORIGINS = True  # Change in production

# Login/Logout URLs
LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'home'
LOGIN_URL = 'login'
