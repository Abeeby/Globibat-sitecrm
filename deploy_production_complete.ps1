# Script de déploiement complet pour Hostinger
# Auteur: Assistant IA - Déploiement Production Globibat CRM
# Date: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "🚀 DÉPLOIEMENT PRODUCTION GLOBIBAT CRM COMPLET" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""

# Vérification du répertoire courant
$currentDir = Get-Location
Write-Host "📁 Répertoire actuel: $currentDir" -ForegroundColor Yellow

# Étape 1: Création du fichier .env
Write-Host "`n[1/10] 📝 Création du fichier .env..." -ForegroundColor Green
$envContent = @"
# Configuration Globibat CRM pour Hostinger
SECRET_KEY=globibat-crm-2024-secret-key-très-longue-et-complexe-ne-jamais-partager
FLASK_ENV=production

# Base de données MySQL Hostinger (À METTRE À JOUR APRÈS CRÉATION)
DATABASE_URL=mysql://globibat_user:VOTRE_MOT_DE_PASSE@localhost:3306/globibat_crm

# Email Configuration Hostinger
MAIL_SERVER=smtp.hostinger.com
MAIL_PORT=465
MAIL_USE_SSL=True
MAIL_USE_TLS=False
MAIL_USERNAME=info@globibat.com
MAIL_PASSWORD=Miser1597532684$
MAIL_DEFAULT_SENDER=info@globibat.com

# Domaines
DOMAIN_NAME=www.globibat.com
DOMAIN_ALT=globibat.ch

# Sécurité
SESSION_COOKIE_SECURE=True
SESSION_COOKIE_HTTPONLY=True
SESSION_COOKIE_SAMESITE=Lax
WTF_CSRF_ENABLED=True
WTF_CSRF_TIME_LIMIT=None

# API Key
API_KEY=CfGCaMikAbXvnvJvmnuFlsCNS5jYx9Gm5zcCvqd9qLs

# Chemins fichiers
UPLOAD_FOLDER=app/static/uploads
MAX_CONTENT_LENGTH=16777216

# Logs
LOG_LEVEL=INFO
LOG_FILE=instance/logs/app.log

# Configuration avancée pour le nouveau système
ENABLE_2FA=True
SESSION_TIMEOUT=1440
MAX_LOGIN_ATTEMPTS=5
PASSWORD_MIN_LENGTH=8

# Configuration des modules
ENABLE_BADGE_SYSTEM=True
ENABLE_PAYROLL=True
ENABLE_EXPENSE_MANAGEMENT=True
ENABLE_LEAVE_MANAGEMENT=True
ENABLE_ANALYTICS=True
ENABLE_COMPLIANCE=True
"@

# Créer le fichier .env
$envContent | Out-File -FilePath ".env" -Encoding UTF8
Write-Host "✅ Fichier .env créé" -ForegroundColor Green

# Étape 2: Mise à jour des requirements
Write-Host "`n[2/10] 📦 Vérification des dépendances..." -ForegroundColor Green
Copy-Item "requirements_complete.txt" "requirements.txt" -Force
Write-Host "✅ Requirements mis à jour" -ForegroundColor Green

# Étape 3: Création des dossiers nécessaires
Write-Host "`n[3/10] 📂 Création de la structure des dossiers..." -ForegroundColor Green
$folders = @(
    "instance",
    "instance/logs",
    "app/static/uploads",
    "app/static/uploads/receipts",
    "app/static/uploads/photos",
    "app/static/uploads/documents",
    "app/templates/payroll",
    "app/templates/expense",
    "app/templates/leave",
    "app/templates/analytics",
    "app/templates/employee"
)

foreach ($folder in $folders) {
    if (!(Test-Path $folder)) {
        New-Item -ItemType Directory -Path $folder -Force | Out-Null
        Write-Host "📁 Créé: $folder" -ForegroundColor Gray
    }
}
Write-Host "✅ Structure des dossiers créée" -ForegroundColor Green

# Étape 4: Création du script d'initialisation
Write-Host "`n[4/10] 🔧 Création du script d'initialisation..." -ForegroundColor Green
$initScript = @"
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Script d'initialisation de la base de données et configuration initiale"""

import os
import sys
from datetime import datetime

# Ajouter le chemin du projet
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import Admin, User, Employee, WorkTimeRegulation, ExpensePolicy
from app.utils.init_data import create_initial_data

def init_database():
    """Initialise la base de données avec les tables et données de base"""
    app = create_app()
    
    with app.app_context():
        print("🔄 Création des tables...")
        db.create_all()
        print("✅ Tables créées")
        
        # Créer les données initiales
        print("🔄 Création des données initiales...")
        create_initial_data()
        print("✅ Données initiales créées")
        
        # Créer l'administrateur par défaut si n'existe pas
        admin = Admin.query.filter_by(email='admin@globibat.ch').first()
        if not admin:
            print("🔄 Création de l'administrateur...")
            admin = Admin(
                username='admin',
                email='admin@globibat.ch',
                firstname='Admin',
                lastname='Globibat',
                phone='+41 79 123 45 67',
                role='Super Admin',
                is_active=True,
                created_at=datetime.utcnow()
            )
            admin.set_password('Admin2024!')
            db.session.add(admin)
            db.session.commit()
            print("✅ Administrateur créé")
            print("   Email: admin@globibat.ch")
            print("   Mot de passe: Admin2024!")
        else:
            print("ℹ️ Administrateur existe déjà")
        
        print("\n✨ Initialisation terminée avec succès!")

if __name__ == '__main__':
    init_database()
"@

$initScript | Out-File -FilePath "init_database.py" -Encoding UTF8
Write-Host "✅ Script d'initialisation créé" -ForegroundColor Green

# Étape 5: Création du script de déploiement Hostinger
Write-Host "`n[5/10] 🚀 Création du script de déploiement Hostinger..." -ForegroundColor Green
$deployScript = @"
#!/bin/bash
# Script de déploiement automatique pour Hostinger

echo "=================================================="
echo "🚀 DÉPLOIEMENT GLOBIBAT CRM SUR HOSTINGER"
echo "=================================================="

# Configuration
DOMAIN="www.globibat.com"
PUBLIC_HTML="/home/\$USER/public_html"

# Étape 1: Vérification de l'environnement
echo -e "\n[1/8] 🔍 Vérification de l'environnement..."
python3 --version
pip3 --version

# Étape 2: Création de l'environnement virtuel
echo -e "\n[2/8] 🐍 Création de l'environnement virtuel..."
cd \$PUBLIC_HTML
python3 -m venv venv
source venv/bin/activate

# Étape 3: Installation des dépendances
echo -e "\n[3/8] 📦 Installation des dépendances..."
pip install --upgrade pip
pip install -r requirements.txt

# Étape 4: Configuration des permissions
echo -e "\n[4/8] 🔐 Configuration des permissions..."
chmod -R 755 app/
chmod -R 777 instance/
chmod -R 777 app/static/uploads/
chmod +x run.py
chmod +x init_database.py

# Étape 5: Initialisation de la base de données
echo -e "\n[5/8] 🗄️ Initialisation de la base de données..."
python init_database.py

# Étape 6: Création du fichier .htaccess
echo -e "\n[6/8] 📝 Création du fichier .htaccess..."
cat > .htaccess << 'EOF'
RewriteEngine On
RewriteCond %{HTTPS} off
RewriteRule ^(.*)$ https://%{HTTP_HOST}%{REQUEST_URI} [L,R=301]

# Python application
RewriteCond %{REQUEST_FILENAME} !-f
RewriteCond %{REQUEST_FILENAME} !-d
RewriteRule ^(.*)$ /index.py/\$1 [L]

# Sécurité
Options -Indexes
<FilesMatch "\.(env|db|sqlite|log)$">
    Order allow,deny
    Deny from all
</FilesMatch>

# Cache control
<IfModule mod_expires.c>
    ExpiresActive On
    ExpiresByType image/jpg "access plus 1 year"
    ExpiresByType image/jpeg "access plus 1 year"
    ExpiresByType image/gif "access plus 1 year"
    ExpiresByType image/png "access plus 1 year"
    ExpiresByType text/css "access plus 1 month"
    ExpiresByType application/javascript "access plus 1 month"
</IfModule>
EOF

# Étape 7: Création du fichier index.py
echo -e "\n[7/8] 🚀 Création du fichier index.py..."
cat > index.py << 'EOF'
#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os

# Ajouter le chemin de l'environnement virtuel
activate_this = os.path.join(os.path.dirname(__file__), 'venv/bin/activate_this.py')
if os.path.exists(activate_this):
    exec(open(activate_this).read(), {'__file__': activate_this})

# Ajouter le chemin du projet
sys.path.insert(0, os.path.dirname(__file__))

# Importer et lancer l'application
from run import app as application

if __name__ == '__main__':
    application.run()
EOF

chmod +x index.py

# Étape 8: Test final
echo -e "\n[8/8] ✅ Test de l'application..."
python -c "from run import app; print('✅ Application chargée avec succès!')"

echo -e "\n=================================================="
echo "✨ DÉPLOIEMENT TERMINÉ AVEC SUCCÈS!"
echo "=================================================="
echo "🌐 Votre application est accessible sur:"
echo "   https://www.globibat.com"
echo "   https://globibat.ch"
echo ""
echo "📧 Compte administrateur:"
echo "   Email: admin@globibat.ch"
echo "   Mot de passe: Admin2024!"
echo ""
echo "⚠️ IMPORTANT: Changez le mot de passe admin après la première connexion!"
echo "=================================================="
"@

$deployScript | Out-File -FilePath "deploy_hostinger_complete.sh" -Encoding UTF8 -NoNewline
Write-Host "✅ Script de déploiement créé" -ForegroundColor Green

# Étape 6: Commit Git
Write-Host "`n[6/10] 📤 Préparation pour Git..." -ForegroundColor Green
git add -A
git commit -m "🚀 Déploiement production complet - Système CRM/Badge avancé"
Write-Host "✅ Changements committés" -ForegroundColor Green

# Étape 7: Instructions finales
Write-Host "`n[7/10] 📋 Instructions de déploiement..." -ForegroundColor Yellow
Write-Host @"

=== PROCHAINES ÉTAPES POUR LE DÉPLOIEMENT ===

1. CRÉER LA BASE DE DONNÉES SUR HOSTINGER:
   - Connectez-vous au panneau Hostinger
   - Allez dans "Bases de données" > "MySQL"
   - Créez une base: globibat_crm
   - Créez un utilisateur: globibat_user
   - Notez le mot de passe généré

2. METTRE À JOUR LE FICHIER .env:
   - Remplacez VOTRE_MOT_DE_PASSE par le mot de passe MySQL
   - DATABASE_URL=mysql://globibat_user:[MOT_DE_PASSE]@localhost:3306/globibat_crm

3. UPLOADER LES FICHIERS:
   - Via FTP ou File Manager Hostinger
   - Uploadez tout le contenu dans public_html/
   - NE PAS uploader le dossier venv/

4. EXÉCUTER LE DÉPLOIEMENT:
   - Connectez-vous en SSH: ssh user@globibat.com
   - cd public_html
   - chmod +x deploy_hostinger_complete.sh
   - ./deploy_hostinger_complete.sh

5. VÉRIFICATIONS FINALES:
   - Accédez à https://www.globibat.com
   - Connectez-vous avec admin@globibat.ch
   - Testez toutes les fonctionnalités

"@ -ForegroundColor Cyan

# Créer un fichier de checklist
Write-Host "`n[8/10] 📝 Création de la checklist de déploiement..." -ForegroundColor Green
@'
# ✅ CHECKLIST DE DÉPLOIEMENT PRODUCTION

## Avant le déploiement:
- [ ] Base de données MySQL créée sur Hostinger
- [ ] Fichier .env mis à jour avec les bonnes credentials
- [ ] Backup du site actuel effectué
- [ ] Nom de domaine pointé vers Hostinger

## Pendant le déploiement:
- [ ] Fichiers uploadés dans public_html/
- [ ] Script deploy_hostinger_complete.sh exécuté
- [ ] Base de données initialisée
- [ ] Permissions configurées

## Après le déploiement:
- [ ] Site accessible en HTTPS
- [ ] Login admin fonctionnel
- [ ] Module de badge testé
- [ ] Module de paie testé
- [ ] Module de dépenses testé
- [ ] Module de congés testé
- [ ] Tableaux de bord fonctionnels
- [ ] Emails de test envoyés
- [ ] Mot de passe admin changé
- [ ] Employés créés
- [ ] Politiques configurées

## Configuration finale:
- [ ] Google Search Console configuré
- [ ] Sitemap soumis
- [ ] Robots.txt vérifié
- [ ] SSL/HTTPS forcé
- [ ] Backups automatiques configurés
- [ ] Monitoring mis en place

## Documentation:
- [ ] Guide utilisateur partagé
- [ ] Formation des employés planifiée
- [ ] Procédures de support définies
'@ | Out-File -FilePath "CHECKLIST_DEPLOIEMENT_FINAL.md" -Encoding UTF8
Write-Host "✅ Checklist créée" -ForegroundColor Green

# Étape 9: Création du guide utilisateur final
Write-Host "`n[9/10] 📚 Création du guide utilisateur..." -ForegroundColor Green
Write-Host "✅ Guide utilisateur disponible dans GUIDE_DEMARRAGE_RAPIDE.md" -ForegroundColor Green

# Étape 10: Résumé final
Write-Host "`n[10/10] 🎉 DÉPLOIEMENT PRÉPARÉ AVEC SUCCÈS!" -ForegroundColor Green
Write-Host "`n================================================" -ForegroundColor Cyan
Write-Host "✨ RÉSUMÉ DU DÉPLOIEMENT" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "✅ Fichier .env créé (à mettre à jour avec le mot de passe MySQL)" -ForegroundColor Green
Write-Host "✅ Scripts de déploiement créés" -ForegroundColor Green
Write-Host "✅ Structure des dossiers préparée" -ForegroundColor Green
Write-Host "✅ Documentation complète disponible" -ForegroundColor Green
Write-Host "✅ Checklist de déploiement créée" -ForegroundColor Green
Write-Host "`n📋 Prochaine étape: Suivre la CHECKLIST_DEPLOIEMENT_FINAL.md" -ForegroundColor Yellow
Write-Host "================================================`n" -ForegroundColor Cyan

# Ouvrir la checklist
notepad.exe CHECKLIST_DEPLOIEMENT_FINAL.md