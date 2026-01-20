@echo off
echo ========================================
echo Demarrage du serveur Django CGTSIM
echo ========================================
echo.

REM Activer l'environnement virtuel
call venv\Scripts\activate.bat

echo Le serveur va demarrer sur http://localhost:8000
echo.
echo API accessible sur: http://localhost:8000/api/
echo Admin accessible sur: http://localhost:8000/admin/
echo.
echo Pour arreter le serveur, appuyez sur CTRL+C
echo.
echo ========================================
echo.

py manage.py runserver

pause
