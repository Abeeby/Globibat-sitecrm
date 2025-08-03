# Script de déploiement simplifié pour Hostinger
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "DEPLOIEMENT PRODUCTION GLOBIBAT CRM" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan

# Créer le fichier .env
Write-Host "`nCreation du fichier .env..." -ForegroundColor Green
@'
# Configuration Globibat CRM pour Hostinger
SECRET_KEY=globibat-crm-2024-secret-key-très-longue-et-complexe-ne-jamais-partager
FLASK_ENV=production

# Base de données MySQL Hostinger
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

# Configuration modules
ENABLE_2FA=True
ENABLE_BADGE_SYSTEM=True
ENABLE_PAYROLL=True
ENABLE_EXPENSE_MANAGEMENT=True
ENABLE_LEAVE_MANAGEMENT=True
ENABLE_ANALYTICS=True
ENABLE_COMPLIANCE=True
'@ | Out-File -FilePath ".env" -Encoding UTF8
Write-Host "OK - Fichier .env cree" -ForegroundColor Green

# Copier requirements
Write-Host "`nMise a jour des requirements..." -ForegroundColor Green
Copy-Item "requirements_complete.txt" "requirements.txt" -Force
Write-Host "OK - Requirements mis a jour" -ForegroundColor Green

# Créer les dossiers
Write-Host "`nCreation des dossiers..." -ForegroundColor Green
@(
    "instance",
    "instance/logs",
    "app/static/uploads",
    "app/static/uploads/receipts",
    "app/static/uploads/photos",
    "app/static/uploads/documents"
) | ForEach-Object {
    if (!(Test-Path $_)) {
        New-Item -ItemType Directory -Path $_ -Force | Out-Null
    }
}
Write-Host "OK - Dossiers crees" -ForegroundColor Green

# Créer le script d'init
Write-Host "`nCreation du script d'initialisation..." -ForegroundColor Green
@'
#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import Admin
from app.utils.init_data import create_initial_data
from datetime import datetime

def init_database():
    app = create_app()
    with app.app_context():
        print("Creation des tables...")
        db.create_all()
        print("Tables creees")
        
        print("Creation des donnees initiales...")
        create_initial_data()
        print("Donnees initiales creees")
        
        admin = Admin.query.filter_by(email='admin@globibat.ch').first()
        if not admin:
            print("Creation de l'administrateur...")
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
            print("Administrateur cree")
            print("Email: admin@globibat.ch")
            print("Mot de passe: Admin2024!")
        else:
            print("Administrateur existe deja")
        
        print("Initialisation terminee!")

if __name__ == '__main__':
    init_database()
'@ | Out-File -FilePath "init_database.py" -Encoding UTF8
Write-Host "OK - Script d'initialisation cree" -ForegroundColor Green

# Créer la checklist
Write-Host "`nCreation de la checklist..." -ForegroundColor Green
@'
# CHECKLIST DE DEPLOIEMENT PRODUCTION

## Avant le deploiement:
[ ] Base de donnees MySQL creee sur Hostinger
[ ] Fichier .env mis a jour avec le mot de passe MySQL
[ ] Backup du site actuel effectue
[ ] Nom de domaine pointe vers Hostinger

## Pendant le deploiement:
[ ] Fichiers uploades dans public_html/
[ ] Script deploy_hostinger_complete.sh execute
[ ] Base de donnees initialisee
[ ] Permissions configurees

## Apres le deploiement:
[ ] Site accessible en HTTPS
[ ] Login admin fonctionnel
[ ] Tous les modules testes
[ ] Mot de passe admin change
[ ] Employes crees

## IMPORTANT:
- EMAIL ADMIN: admin@globibat.ch
- MOT DE PASSE INITIAL: Admin2024!
- CHANGER LE MOT DE PASSE APRES LA PREMIERE CONNEXION!
'@ | Out-File -FilePath "CHECKLIST_DEPLOIEMENT_FINAL.md" -Encoding UTF8
Write-Host "OK - Checklist creee" -ForegroundColor Green

Write-Host "`n==================================================" -ForegroundColor Cyan
Write-Host "PREPARATION TERMINEE!" -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "PROCHAINES ETAPES:" -ForegroundColor Yellow
Write-Host "1. Creer la base de donnees MySQL sur Hostinger" -ForegroundColor White
Write-Host "2. Mettre a jour le mot de passe dans .env" -ForegroundColor White
Write-Host "3. Uploader les fichiers dans public_html/" -ForegroundColor White
Write-Host "4. Executer deploy_hostinger_complete.sh via SSH" -ForegroundColor White
Write-Host ""
Write-Host "Consultez CHECKLIST_DEPLOIEMENT_FINAL.md pour les details" -ForegroundColor Yellow
Write-Host "==================================================" -ForegroundColor Cyan