@echo off
echo ========================================
echo Configuration de la base de donnees
echo ========================================
echo.

REM Activer l'environnement virtuel
call venv\Scripts\activate.bat

echo [1/4] Creation des migrations...
py manage.py makemigrations
if errorlevel 1 (
    echo.
    echo ERREUR lors de la creation des migrations
    echo.
    pause
    exit /b 1
)
echo Migrations creees ✓
echo.

echo [2/4] Application des migrations...
py manage.py migrate
if errorlevel 1 (
    echo.
    echo ERREUR lors de l'application des migrations
    echo.
    pause
    exit /b 1
)
echo Base de donnees creee ✓
echo.

echo [3/4] Creation d'un compte administrateur...
echo.
echo Vous allez creer un compte administrateur CGTSIM
echo.
echo NOTES:
echo - Username: choisissez ce que vous voulez (ex: admin)
echo - Password: vous ne le verrez pas quand vous tapez (normal!)
echo.
py manage.py createsuperuser
echo.
echo Compte administrateur cree ✓
echo.

echo [4/4] Verification de la configuration...
py manage.py check
echo.

echo ========================================
echo Configuration terminee! ✓
echo ========================================
echo.
echo Vous pouvez maintenant lancer le serveur avec:
echo run-server.bat
echo.
pause
