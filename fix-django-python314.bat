@echo off
echo ========================================
echo Mise a jour de Django pour Python 3.14
echo ========================================
echo.

echo Python 3.14 est trop recent pour Django 5.0.1
echo On va mettre a jour vers Django 5.1 (compatible)
echo.
pause

REM Activer l'environnement virtuel
call venv\Scripts\activate.bat

echo Mise a jour de Django...
pip install --upgrade Django==5.1
echo.

echo Verification...
py -c "import django; print('Django version:', django.get_version())"
echo.

echo ========================================
echo Mise a jour terminee! ✓
echo ========================================
echo.
echo IMPORTANT: Redemarrez le serveur
echo 1. Fermez la fenetre du serveur (CTRL+C)
echo 2. Relancez: run-server-fixe.bat
echo.
pause
