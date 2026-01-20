@echo off
echo ========================================
echo Installation CGTSIM Backend (simplifie)
echo ========================================
echo.

REM Vérifier que Python est installé
py --version >nul 2>&1
if errorlevel 1 (
    echo ERREUR: Python n'est pas installe
    pause
    exit /b 1
)

echo [1/6] Python detecte ✓
py --version
echo.

REM Créer l'environnement virtuel
echo [2/6] Creation de l'environnement virtuel...
if exist venv (
    echo Environnement virtuel existe deja
) else (
    py -m venv venv
    if errorlevel 1 (
        echo ERREUR lors de la creation
        pause
        exit /b 1
    )
)
echo Environnement virtuel cree ✓
echo.

REM Activer l'environnement virtuel
echo [3/6] Activation de l'environnement virtuel...
call venv\Scripts\activate.bat
echo Active ✓
echo.

REM Mettre à jour pip
echo [4/6] Mise a jour de pip...
py -m pip install --upgrade pip
echo pip mis a jour ✓
echo.

REM Installer les dépendances SANS Pillow (pas critique pour débuter)
echo [5/6] Installation des dependances essentielles...
echo Cela peut prendre 2-3 minutes...
echo.

echo Installation de Django...
pip install Django==5.0.1
if errorlevel 1 goto error

echo Installation de Django REST Framework...
pip install djangorestframework==3.14.0
if errorlevel 1 goto error

echo Installation de JWT...
pip install djangorestframework-simplejwt==5.3.1
if errorlevel 1 goto error

echo Installation de CORS headers...
pip install django-cors-headers==4.3.1
if errorlevel 1 goto error

echo Installation de django-filter...
pip install django-filter==23.5
if errorlevel 1 goto error

echo Installation de python-dotenv...
pip install python-dotenv==1.0.0
if errorlevel 1 goto error

echo.
echo NOTE: Pillow (images) sera installe plus tard si necessaire
echo.
echo Toutes les dependances essentielles sont installees ✓
echo.

REM Vérification
echo [6/6] Verification de l'installation...
py -c "import django; print('Django version:', django.get_version())"
py -c "import rest_framework; print('DRF installe ✓')"
echo.

echo ========================================
echo Installation terminee avec succes! ✓
echo ========================================
echo.
echo Votre environnement Python est pret!
echo.
echo PROCHAINE ETAPE:
echo Double-cliquez sur: setup-database-fixe.bat
echo.
pause
exit /b 0

:error
echo.
echo ERREUR lors de l'installation
echo.
pause
exit /b 1
