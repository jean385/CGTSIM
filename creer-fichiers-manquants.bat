@echo off
echo ========================================
echo Creation des fichiers manquants
echo ========================================
echo.

echo [1/10] Creation des fichiers __init__.py...
type nul > cgtsim\__init__.py
type nul > config\__init__.py
echo OK
echo.

echo [2/10] Creation du dossier migrations...
if not exist cgtsim\migrations mkdir cgtsim\migrations
type nul > cgtsim\migrations\__init__.py
echo OK
echo.

echo [3/10] Creation de cgtsim\admin.py...
(
echo from django.contrib import admin
echo from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
echo from .models import User, CSS, DemandeFonds, Avance, EmpruntBanque, CompteBancaire
echo.
echo @admin.register^(User^)
echo class CustomUserAdmin^(BaseUserAdmin^):
echo     list_display = ['username', 'email', 'role', 'css', 'is_active']
echo     list_filter = ['role', 'is_active']
echo.
echo @admin.register^(CSS^)
echo class CSSAdmin^(admin.ModelAdmin^):
echo     list_display = ['code', 'name', 'contact_person', 'is_active']
echo     search_fields = ['code', 'name']
echo.
echo @admin.register^(DemandeFonds^)
echo class DemandeAdmin^(admin.ModelAdmin^):
echo     list_display = ['reference', 'css', 'montant', 'date_besoins', 'statut']
echo     list_filter = ['statut', 'type_depense']
echo.
echo admin.site.register^(Avance^)
echo admin.site.register^(EmpruntBanque^)
echo admin.site.register^(CompteBancaire^)
) > cgtsim\admin.py
echo OK
echo.

echo [4/10] Creation de cgtsim\apps.py...
(
echo from django.apps import AppConfig
echo.
echo class CgtsimConfig^(AppConfig^):
echo     default_auto_field = 'django.db.models.BigAutoField'
echo     name = 'cgtsim'
) > cgtsim\apps.py
echo OK
echo.

echo [5/10] Creation de config\__init__.py...
type nul > config\__init__.py
echo OK
echo.

echo [6/10] Creation de config\urls.py...
(
echo from django.contrib import admin
echo from django.urls import path, include
echo from django.conf import settings
echo from django.conf.urls.static import static
echo.
echo urlpatterns = [
echo     path^('admin/', admin.site.urls^),
echo     path^('api/', include^('cgtsim.urls'^)^),
echo ]
echo.
echo if settings.DEBUG:
echo     urlpatterns += static^(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT^)
) > config\urls.py
echo OK
echo.

echo [7/10] Creation de config\wsgi.py...
(
echo import os
echo from django.core.wsgi import get_wsgi_application
echo.
echo os.environ.setdefault^('DJANGO_SETTINGS_MODULE', 'config.settings'^)
echo application = get_wsgi_application^(^)
) > config\wsgi.py
echo OK
echo.

echo [8/10] Creation de config\asgi.py...
(
echo import os
echo from django.core.asgi import get_asgi_application
echo.
echo os.environ.setdefault^('DJANGO_SETTINGS_MODULE', 'config.settings'^)
echo application = get_asgi_application^(^)
) > config\asgi.py
echo OK
echo.

echo [9/10] Creation de manage.py...
(
echo #!/usr/bin/env python
echo import os
echo import sys
echo.
echo if __name__ == '__main__':
echo     os.environ.setdefault^('DJANGO_SETTINGS_MODULE', 'config.settings'^)
echo     try:
echo         from django.core.management import execute_from_command_line
echo     except ImportError as exc:
echo         raise ImportError^(
echo             "Couldn't import Django. Are you sure it's installed?"
echo         ^) from exc
echo     execute_from_command_line^(sys.argv^)
) > manage.py
echo OK
echo.

echo [10/10] Creation du fichier .env...
(
echo # Configuration Django CGTSIM
echo SECRET_KEY=django-insecure-dev-CHANGE-THIS-IN-PRODUCTION-xyz789abc123
echo DEBUG=True
echo ALLOWED_HOSTS=localhost,127.0.0.1
echo.
echo # CORS
echo CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
echo.
echo # Email
echo EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
) > .env
echo OK
echo.

echo [BONUS] Creation des dossiers necessaires...
if not exist logs mkdir logs
if not exist media mkdir media
if not exist static mkdir static
if not exist fixtures mkdir fixtures
echo OK
echo.

echo ========================================
echo TOUS les fichiers ont ete crees! ✓
echo ========================================
echo.
echo Structure du projet:
echo.
echo projet-cgtsim\
echo ├── cgtsim\
echo │   ├── __init__.py ✓
echo │   ├── models.py ✓
echo │   ├── views.py ✓
echo │   ├── serializers.py ✓
echo │   ├── urls.py ✓
echo │   ├── permissions.py ✓
echo │   ├── services.py ✓
echo │   ├── admin.py ✓
echo │   ├── apps.py ✓
echo │   └── migrations\
echo │       └── __init__.py ✓
echo ├── config\
echo │   ├── __init__.py ✓
echo │   ├── settings.py ✓
echo │   ├── urls.py ✓
echo │   ├── wsgi.py ✓
echo │   └── asgi.py ✓
echo ├── manage.py ✓
echo ├── requirements.txt ✓
echo ├── .env ✓
echo └── setup-*.bat ✓
echo.
echo PROCHAINE ETAPE:
echo Double-cliquez sur: setup-windows.bat
echo.
pause
