@echo off
color 0B
echo ===========================================================
echo         CRM GLOBIBAT - DESIGN MODERNE
echo ===========================================================
echo.

echo Verification de Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERREUR] Python n'est pas installe ou pas dans le PATH
    echo Veuillez installer Python depuis https://python.org
    pause
    exit /b 1
)
echo [OK] Python detecte

echo.
echo Installation des dependances...
pip install flask flask-sqlalchemy flask-login >nul 2>&1

echo.
echo ===========================================================
echo            DEMARRAGE DU SERVEUR
echo ===========================================================
echo.
echo URL d'acces : http://localhost:5000
echo.
echo Pages principales :
echo   - Dashboard : http://localhost:5000/modern/dashboard
echo   - Chantiers : http://localhost:5000/modern/chantiers
echo.
echo Appuyez sur Ctrl+C pour arreter le serveur
echo ===========================================================
echo.

python app_modern.py