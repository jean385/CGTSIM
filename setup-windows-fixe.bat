@echo off
echo ========================================
echo Installation automatique CGTSIM Backend
echo ========================================
echo.

REM Vérifier que Python est installé
py --version >nul 2>&1
if errorlevel 1 (
    echo ERREUR: Python n'est pas installe ou pas dans le PATH
    echo Telechargez Python depuis https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [1/6] Python detecte ✓
py --version
echo.

REM Créer l'environnement virtuel
echo [2/6] Creation de l'environnement virtuel...
py -m venv venv
if errorlevel 1 (
    echo ERREUR lors de la creation de l'environnement virtuel
    pause
    exit /b 1
)
echo Environnement virtuel cree ✓
echo.

REM Activer l'environnement virtuel
echo [3/6] Activation de l'environnement virtuel...
call venv\Scripts\activate.bat
echo Environnement virtuel active ✓
echo.

REM Mettre à jour pip
echo [4/6] Mise a jour de pip...
py -m pip install --upgrade pip --quiet
echo pip mis a jour ✓
echo.

REM Installer les dépendances
echo [5/6] Installation des dependances Python...
echo Cela peut prendre 2-3 minutes, patience...
echo.
pip install Django==5.0.1
pip install djangorestframework==3.14.0
pip install djangorestframework-simplejwt==5.3.1
pip install django-cors-headers==4.3.1
pip install django-filter==23.5
pip install python-dotenv==1.0.0
pip install Pillow==10.2.0

if errorlevel 1 (
    echo ERREUR lors de l'installation des dependances
    pause
    exit /b 1
)
echo Dependances installees ✓
echo.

REM Vérification
echo [6/6] Verification de l'installation...
py -c "import django; print('Django version:', django.get_version())"
echo.

echo ========================================
echo Installation terminee avec succes! ✓
echo ========================================
echo.
echo Votre environnement Python est pret!
echo Version Python: 
py --version
echo.
echo PROCHAINE ETAPE:
echo Double-cliquez sur: setup-database.bat
echo.
pause
