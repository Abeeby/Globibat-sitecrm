# Script PowerShell pour créer le fichier .env
# Utilisation : .\create_env_file.ps1

Write-Host "=== Création du fichier .env pour Globibat CRM ===" -ForegroundColor Green

# Vérifier si .env existe déjà
if (Test-Path ".env") {
    $response = Read-Host "Le fichier .env existe déjà. Voulez-vous le remplacer ? (o/n)"
    if ($response -ne "o") {
        Write-Host "Opération annulée." -ForegroundColor Yellow
        exit
    }
}

# Contenu du fichier .env
$envContent = @"
# Configuration Globibat CRM pour Hostinger
SECRET_KEY=globibat-crm-2024-secret-key-très-longue-et-complexe-ne-jamais-partager
FLASK_ENV=production

# Base de données MySQL Hostinger (À COMPLÉTER)
DATABASE_URL=mysql://username:password@localhost:3306/database_name

# Email Configuration Hostinger
MAIL_SERVER=smtp.hostinger.com
MAIL_PORT=465
MAIL_USE_SSL=True
MAIL_USE_TLS=False
MAIL_USERNAME=info@globibat.com
MAIL_PASSWORD=Miser1597532684`$
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

# Optionnel
SENTRY_DSN=
CELERY_BROKER_URL=
CELERY_RESULT_BACKEND=
"@

# Créer le fichier
$envContent | Out-File -FilePath ".env" -Encoding UTF8
Write-Host "Fichier .env cree avec succes !" -ForegroundColor Green

# Rappel pour la base de données
Write-Host "`nIMPORTANT :" -ForegroundColor Yellow
Write-Host "N'oubliez pas de mettre à jour DATABASE_URL avec vos informations MySQL Hostinger !" -ForegroundColor Yellow
Write-Host "Format : mysql://username:password@localhost:3306/database_name" -ForegroundColor Cyan

# Afficher le chemin
Write-Host "`nFichier cree : $(Get-Location)\.env" -ForegroundColor Cyan