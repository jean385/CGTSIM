@echo off
echo ========================================
echo Creation d'un nouveau compte admin
echo ========================================
echo.

call venv\Scripts\activate.bat

echo Vous allez creer un nouveau compte administrateur CGTSIM
echo.
py manage.py createsuperuser
echo.

echo ========================================
echo Compte cree avec succes! ✓
echo ========================================
echo.
echo Vous pouvez maintenant:
echo 1. Lancer le serveur: run-server-fixe.bat
echo 2. Vous connecter a l'admin Django
echo 3. Creer vos CSS
echo.
pause
