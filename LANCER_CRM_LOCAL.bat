@echo off
chcp 65001 > nul
color 0A
title GLOBIBAT CRM - Système Intégré

echo.
echo  ╔════════════════════════════════════════════════════════════╗
echo  ║                                                            ║
echo  ║              GLOBIBAT CRM - SYSTÈME INTÉGRÉ               ║
echo  ║                                                            ║
echo  ║          Entreprise de construction et rénovation          ║
echo  ║                                                            ║
echo  ╚════════════════════════════════════════════════════════════╝
echo.

:: Vérifier si Python est installé
echo [INFO] Vérification de Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo  ╔═══════════════════════════════════════════════════════╗
    echo  ║   ⚠️  ERREUR : Python n'est pas installé              ║
    echo  ╠═══════════════════════════════════════════════════════╣
    echo  ║   Veuillez installer Python 3.8 ou supérieur depuis  ║
    echo  ║   https://www.python.org/downloads/                  ║
    echo  ╚═══════════════════════════════════════════════════════╝
    echo.
    pause
    exit /b 1
)

:: Se placer dans le bon répertoire
cd /d "%~dp0"
echo [INFO] Répertoire de travail : %CD%
echo.

:: Vérifier si l'environnement virtuel existe
if not exist "venv\" (
    echo [INFO] Création de l'environnement virtuel Python...
    echo        Cela peut prendre quelques minutes...
    python -m venv venv
    if errorlevel 1 (
        echo.
        echo [ERREUR] Impossible de créer l'environnement virtuel
        pause
        exit /b 1
    )
    echo [OK] Environnement virtuel créé
    echo.
)

:: Activer l'environnement virtuel
echo [INFO] Activation de l'environnement virtuel...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ERREUR] Impossible d'activer l'environnement virtuel
    pause
    exit /b 1
)

:: Installer/Mettre à jour pip
echo [INFO] Mise à jour de pip...
python -m pip install --upgrade pip --quiet 2>nul

:: Vérifier et installer les dépendances
echo [INFO] Vérification des dépendances...
pip show Flask >nul 2>&1
if errorlevel 1 (
    echo [INFO] Installation des dépendances requises...
    echo        Cela peut prendre quelques minutes lors de la première installation...
    
    :: Créer requirements.txt minimal si nécessaire
    if not exist "requirements.txt" (
        echo Flask>=2.3.0 > requirements.txt
        echo Flask-SQLAlchemy>=3.0.0 >> requirements.txt
        echo Flask-Login>=0.6.0 >> requirements.txt
        echo Flask-Migrate>=4.0.0 >> requirements.txt
        echo Flask-CORS>=4.0.0 >> requirements.txt
        echo Flask-Mail>=0.9.0 >> requirements.txt
        echo python-dotenv>=1.0.0 >> requirements.txt
        echo Werkzeug>=2.3.0 >> requirements.txt
        echo pyotp>=2.8.0 >> requirements.txt
        echo qrcode>=7.4.0 >> requirements.txt
        echo Pillow>=10.0.0 >> requirements.txt
        echo openpyxl>=3.1.0 >> requirements.txt
        echo reportlab>=4.0.0 >> requirements.txt
        echo plotly>=5.14.0 >> requirements.txt
        echo pandas>=2.0.0 >> requirements.txt
    )
    
    pip install -r requirements.txt --quiet
    if errorlevel 1 (
        echo [ERREUR] Impossible d'installer les dépendances
        pause
        exit /b 1
    )
    echo [OK] Dépendances installées
)

:: Créer les dossiers nécessaires
echo [INFO] Création des dossiers nécessaires...
if not exist "instance" mkdir instance
if not exist "logs" mkdir logs
if not exist "app\static\uploads" mkdir app\static\uploads
if not exist "app\static\uploads\avatars" mkdir app\static\uploads\avatars
if not exist "app\static\uploads\documents" mkdir app\static\uploads\documents
if not exist "app\static\uploads\expenses" mkdir app\static\uploads\expenses
if not exist "app\static\uploads\attendance" mkdir app\static\uploads\attendance

:: Vérifier si la base de données existe
if not exist "instance\globibat.db" (
    echo.
    echo  ╔═══════════════════════════════════════════════════════╗
    echo  ║         INITIALISATION DE LA BASE DE DONNÉES         ║
    echo  ╚═══════════════════════════════════════════════════════╝
    echo.
    
    if exist "init_database.py" (
        echo [INFO] Création de la base de données et des données de test...
        python init_database.py
        if errorlevel 1 (
            echo [ERREUR] Impossible d'initialiser la base de données
            pause
            exit /b 1
        )
    ) else (
        echo [AVERTISSEMENT] init_database.py non trouvé
        echo                 La base de données sera créée au premier lancement
    )
    echo.
)

:: Afficher les informations de connexion
cls
echo.
echo  ╔════════════════════════════════════════════════════════════╗
echo  ║                                                            ║
echo  ║              GLOBIBAT CRM - PRÊT À DÉMARRER               ║
echo  ║                                                            ║
echo  ╚════════════════════════════════════════════════════════════╝
echo.
echo  ┌──────────────────────────────────────────────────────────┐
echo  │  🌐 POINTS D'ACCÈS DISPONIBLES :                         │
echo  ├──────────────────────────────────────────────────────────┤
echo  │                                                          │
echo  │  📱 Site Internet Public                                 │
echo  │     URL : http://localhost:5000                         │
echo  │                                                          │
echo  │  🔐 Administration CRM                                   │
echo  │     URL : http://localhost:5000/admin                   │
echo  │     Compte : info@globibat.com                          │
echo  │                                                          │
echo  │  👤 Espace Employé                                       │
echo  │     URL : http://localhost:5000/employee                │
echo  │     Matricules de test : EMP001 à EMP005                │
echo  │                                                          │
echo  │  🎫 Système de Badge                                     │
echo  │     URL : http://localhost:5000/badge                   │
echo  │     Utiliser les matricules employés                    │
echo  │                                                          │
echo  │  📊 API REST                                             │
echo  │     URL : http://localhost:5000/api/v1/                 │
echo  │                                                          │
echo  └──────────────────────────────────────────────────────────┘
echo.
echo  [INFO] Démarrage du serveur Flask...
echo  [INFO] Appuyez sur Ctrl+C pour arrêter le serveur
echo.
echo ══════════════════════════════════════════════════════════════
echo.

:: Lancer Flask
python app.py

:: Si l'application se ferme
echo.
echo ══════════════════════════════════════════════════════════════
echo.
echo  [INFO] Serveur arrêté
echo.
pause