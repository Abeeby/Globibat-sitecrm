@echo off
chcp 65001 > nul
title GLOBIBAT CRM - Lancement Local
color 0A

echo ============================================================
echo                  GLOBIBAT CRM - LANCEMENT LOCAL
echo ============================================================
echo.

:: Vérifier Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python n'est pas installé!
    echo    Téléchargez Python depuis: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo ✅ Python détecté
echo.

:: Lancer le script Python
echo 🚀 Démarrage de l'application...
echo.
echo ============================================================
echo    IDENTIFIANTS DE CONNEXION:
echo    Email: info@globibat.com
echo    Mot de passe: Miser1597532684$
echo ============================================================
echo.

python lancer_local.py

pause