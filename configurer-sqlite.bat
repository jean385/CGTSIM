@echo off
echo ========================================
echo Configuration SQLite (simple)
echo ========================================
echo.

echo Ce script va modifier settings.py pour utiliser SQLite
echo au lieu de PostgreSQL (beaucoup plus simple!)
echo.
echo Appuyez sur une touche pour continuer...
pause >nul
echo.

REM Sauvegarder l'ancien settings.py
if exist config\settings.py (
    echo Sauvegarde de l'ancien settings.py...
    copy config\settings.py config\settings.py.backup >nul
    echo Sauvegarde creee: settings.py.backup
)
echo.

echo Creation du nouveau settings.py avec SQLite...

REM Créer le nouveau settings.py avec SQLite
(
echo """
echo Configuration Django pour le projet CGTSIM - Version SQLite
echo """
echo.
echo import os
echo from pathlib import Path
echo from datetime import timedelta
echo.
echo # Build paths
echo BASE_DIR = Path^(__file__^).resolve^(^).parent.parent
echo.
echo # SECURITY WARNING: keep the secret key used in production secret!
echo SECRET_KEY = os.environ.get^('SECRET_KEY', 'django-insecure-dev-key-CHANGE-IN-PRODUCTION'^)
echo.
echo # SECURITY WARNING: don't run with debug turned on in production!
echo DEBUG = os.environ.get^('DEBUG', 'True'^) == 'True'
echo.
echo ALLOWED_HOSTS = os.environ.get^('ALLOWED_HOSTS', 'localhost,127.0.0.1'^).split^(','^)
echo.
echo # Application definition
echo INSTALLED_APPS = [
echo     'django.contrib.admin',
echo     'django.contrib.auth',
echo     'django.contrib.contenttypes',
echo     'django.contrib.sessions',
echo     'django.contrib.messages',
echo     'django.contrib.staticfiles',
echo     'rest_framework',
echo     'rest_framework_simplejwt',
echo     'corsheaders',
echo     'django_filters',
echo     'cgtsim',
echo ]
echo.
echo MIDDLEWARE = [
echo     'django.middleware.security.SecurityMiddleware',
echo     'corsheaders.middleware.CorsMiddleware',
echo     'django.contrib.sessions.middleware.SessionMiddleware',
echo     'django.middleware.common.CommonMiddleware',
echo     'django.middleware.csrf.CsrfViewMiddleware',
echo     'django.contrib.auth.middleware.AuthenticationMiddleware',
echo     'django.contrib.messages.middleware.MessageMiddleware',
echo     'django.middleware.clickjacking.XFrameOptionsMiddleware',
echo ]
echo.
echo ROOT_URLCONF = 'config.urls'
echo.
echo TEMPLATES = [
echo     {
echo         'BACKEND': 'django.template.backends.django.DjangoTemplates',
echo         'DIRS': [BASE_DIR / 'templates'],
echo         'APP_DIRS': True,
echo         'OPTIONS': {
echo             'context_processors': [
echo                 'django.template.context_processors.debug',
echo                 'django.template.context_processors.request',
echo                 'django.contrib.auth.context_processors.auth',
echo                 'django.contrib.messages.context_processors.messages',
echo             ],
echo         },
echo     },
echo ]
echo.
echo WSGI_APPLICATION = 'config.wsgi.application'
echo.
echo # Database - SQLite pour developpement
echo DATABASES = {
echo     'default': {
echo         'ENGINE': 'django.db.backends.sqlite3',
echo         'NAME': BASE_DIR / 'db.sqlite3',
echo     }
echo }
echo.
echo # Custom User Model
echo AUTH_USER_MODEL = 'cgtsim.User'
echo.
echo # Password validation
echo AUTH_PASSWORD_VALIDATORS = [
echo     {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
echo     {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 8}},
echo     {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
echo     {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
echo ]
echo.
echo # Internationalization
echo LANGUAGE_CODE = 'fr-ca'
echo TIME_ZONE = 'America/Toronto'
echo USE_I18N = True
echo USE_TZ = True
echo.
echo # Static files
echo STATIC_URL = '/static/'
echo STATIC_ROOT = BASE_DIR / 'staticfiles'
echo STATICFILES_DIRS = [BASE_DIR / 'static']
echo.
echo # Media files
echo MEDIA_URL = '/media/'
echo MEDIA_ROOT = BASE_DIR / 'media'
echo.
echo # Default primary key field type
echo DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
echo.
echo # REST Framework configuration
echo REST_FRAMEWORK = {
echo     'DEFAULT_AUTHENTICATION_CLASSES': [
echo         'rest_framework_simplejwt.authentication.JWTAuthentication',
echo     ],
echo     'DEFAULT_PERMISSION_CLASSES': ['rest_framework.permissions.IsAuthenticated'],
echo     'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
echo     'PAGE_SIZE': 50,
echo     'DEFAULT_FILTER_BACKENDS': [
echo         'django_filters.rest_framework.DjangoFilterBackend',
echo         'rest_framework.filters.SearchFilter',
echo         'rest_framework.filters.OrderingFilter',
echo     ],
echo     'DATETIME_FORMAT': '%%Y-%%m-%%d %%H:%%M:%%S',
echo     'DATE_FORMAT': '%%Y-%%m-%%d',
echo }
echo.
echo # Simple JWT configuration
echo SIMPLE_JWT = {
echo     'ACCESS_TOKEN_LIFETIME': timedelta^(minutes=60^),
echo     'REFRESH_TOKEN_LIFETIME': timedelta^(days=7^),
echo     'ROTATE_REFRESH_TOKENS': True,
echo     'BLACKLIST_AFTER_ROTATION': True,
echo     'UPDATE_LAST_LOGIN': True,
echo     'ALGORITHM': 'HS256',
echo     'SIGNING_KEY': SECRET_KEY,
echo     'AUTH_HEADER_TYPES': ^('Bearer',^),
echo     'USER_ID_FIELD': 'id',
echo     'USER_ID_CLAIM': 'user_id',
echo }
echo.
echo # CORS configuration
echo CORS_ALLOWED_ORIGINS = os.environ.get^(
echo     'CORS_ALLOWED_ORIGINS',
echo     'http://localhost:3000,http://127.0.0.1:3000'
echo ^).split^(','^)
echo CORS_ALLOW_CREDENTIALS = True
echo.
echo # Email configuration
echo EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
echo DEFAULT_FROM_EMAIL = 'noreply@cgtsim.ca'
) > config\settings.py

echo.
echo ========================================
echo Configuration SQLite terminee! ✓
echo ========================================
echo.
echo Le fichier settings.py a ete modifie pour utiliser SQLite.
echo C'est beaucoup plus simple et parfait pour le developpement!
echo.
echo PROCHAINE ETAPE:
echo Double-cliquez sur: setup-database-fixe.bat
echo.
pause
