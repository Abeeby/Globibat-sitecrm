@echo off
echo ===============================================
echo     SYSTEME DE BADGEAGE GLOBIBAT
echo ===============================================
echo.

:: Vérifier si Python est installé
python --version >nul 2>&1
if errorlevel 1 (
    echo ERREUR : Python n'est pas installe ou n'est pas dans le PATH
    echo Veuillez installer Python depuis https://www.python.org/
    pause
    exit /b 1
)

:: Vérifier si l'environnement virtuel existe
if not exist "venv" (
    echo Creation de l'environnement virtuel...
    python -m venv venv
)

:: Activer l'environnement virtuel
echo Activation de l'environnement virtuel...
call venv\Scripts\activate

:: Installer/Mettre à jour les dépendances
echo.
echo Installation des dependances...
pip install -r requirements.txt

:: Lancer l'application
echo.
echo ===============================================
echo Lancement de l'application...
echo ===============================================
echo.
echo L'application sera accessible a : http://localhost:5000
echo.
echo Identifiants administrateur par defaut :
echo   - Utilisateur : admin
echo   - Mot de passe : admin123
echo.
echo Appuyez sur Ctrl+C pour arreter l'application
echo ===============================================
echo.

:: Démarrer l'application
python app.py

:: Désactiver l'environnement virtuel à la fermeture
deactivate

pause 