@echo off
echo ========================================
echo Mise a jour du Backend CGTSIM
echo Structure de demande detaillee
echo ========================================
echo.
echo Ce script va:
echo 1. Sauvegarder l'ancien models.py
echo 2. Installer le nouveau models.py
echo 3. Creer les nouvelles migrations
echo 4. Appliquer les migrations
echo.
echo ATTENTION: Cette operation va modifier la base de donnees
echo.
pause

REM Activer l'environnement virtuel
call venv\Scripts\activate.bat

echo [1/5] Sauvegarde de l'ancien models.py...
if exist cgtsim\models.py (
    copy cgtsim\models.py cgtsim\models.py.old
    echo Sauvegarde creee: models.py.old
)
echo.

echo [2/5] Suppression de l'ancienne base de donnees...
echo Pour repartir avec la nouvelle structure
if exist db.sqlite3 (
    del db.sqlite3
    echo Base de donnees supprimee
)
echo.

echo [3/5] Suppression des anciennes migrations...
if exist cgtsim\migrations (
    del cgtsim\migrations\*.py
    type nul > cgtsim\migrations\__init__.py
    echo Migrations supprimees
)
echo.

echo [4/5] Creation des nouvelles migrations...
py manage.py makemigrations
if errorlevel 1 (
    echo ERREUR lors de la creation des migrations
    pause
    exit /b 1
)
echo.

echo [5/5] Application des migrations...
py manage.py migrate
if errorlevel 1 (
    echo ERREUR lors de l'application des migrations
    pause
    exit /b 1
)
echo.

echo ========================================
echo Mise a jour terminee! ✓
echo ========================================
echo.
echo La base de donnees a ete recreee avec la nouvelle structure
echo.
echo IMPORTANT: Vous devez recreer un compte administrateur
echo Double-cliquez sur: creer-superuser.bat
echo.
pause
