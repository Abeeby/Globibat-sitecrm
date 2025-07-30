#!/bin/bash
# Script de déploiement pour Hostinger

echo "=== Déploiement Globibat CRM sur Hostinger ==="

# Vérifier que .env existe
if [ ! -f .env ]; then
    echo "❌ Erreur: Fichier .env manquant!"
    echo "Créez le fichier .env en suivant hostinger_config.md"
    exit 1
fi

# Créer les dossiers nécessaires
echo "📁 Création des dossiers..."
mkdir -p instance/logs
mkdir -p app/static/uploads
mkdir -p backups

# Installer/Mettre à jour les dépendances
echo "📦 Installation des dépendances..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
pip install -r requirements.txt

# Initialiser la base de données
echo "🗄️ Initialisation de la base de données..."
python run.py init_db

# Créer un admin si nécessaire
echo "👤 Vérification de l'administrateur..."
python -c "from run import app; from app.models import db, User; app.app_context().push(); admin_exists = User.query.filter_by(email='admin@globibat.ch').first(); print('Admin existe' if admin_exists else 'Créer admin')"

# Collecter les fichiers statiques
echo "🎨 Préparation des fichiers statiques..."
# Les fichiers statiques sont déjà dans app/static/

# Créer le fichier .htaccess
echo "🔧 Configuration Apache..."
cat > .htaccess <<EOF
RewriteEngine On

# Force HTTPS
RewriteCond %{HTTPS} off
RewriteRule ^(.*)$ https://%{HTTP_HOST}%{REQUEST_URI} [L,R=301]

# Rediriger vers l'application Flask
RewriteCond %{REQUEST_FILENAME} !-f
RewriteCond %{REQUEST_FILENAME} !-d
RewriteRule ^(.*)$ /index.py/\$1 [QSA,L]

# Protection des dossiers
<FilesMatch "\.env$">
    Order allow,deny
    Deny from all
</FilesMatch>

# Cache pour les fichiers statiques
<IfModule mod_expires.c>
    ExpiresActive On
    ExpiresByType image/jpg "access plus 1 year"
    ExpiresByType image/jpeg "access plus 1 year"
    ExpiresByType image/gif "access plus 1 year"
    ExpiresByType image/png "access plus 1 year"
    ExpiresByType text/css "access plus 1 month"
    ExpiresByType application/javascript "access plus 1 month"
</IfModule>

# Compression
<IfModule mod_deflate.c>
    AddOutputFilterByType DEFLATE text/html text/plain text/xml text/css application/javascript
</IfModule>
EOF

# Créer index.py pour Hostinger
echo "🚀 Création du point d'entrée..."
cat > index.py <<EOF
#!/usr/bin/env python3
import sys
import os

# Ajouter le répertoire au path
sys.path.insert(0, os.path.dirname(__file__))

# Charger les variables d'environnement
from dotenv import load_dotenv
load_dotenv()

# Importer l'application
from run import app as application

# Pour Hostinger CGI
if __name__ == "__main__":
    from wsgiref.handlers import CGIHandler
    CGIHandler().run(application)
EOF

chmod +x index.py

# Créer le script de maintenance
echo "🛠️ Création des scripts de maintenance..."
cat > maintenance.sh <<EOF
#!/bin/bash
# Script de maintenance quotidienne

# Backup de la base de données
DATE=\$(date +%Y%m%d)
source .env
mysqldump -u \${DB_USER} -p\${DB_PASS} \${DB_NAME} > backups/backup_\$DATE.sql

# Nettoyer les vieux backups (garder 30 jours)
find backups -name "*.sql" -mtime +30 -delete

# Nettoyer les logs de plus de 90 jours
find instance/logs -name "*.log" -mtime +90 -delete
EOF

chmod +x maintenance.sh

# Test de configuration
echo "✅ Test de configuration..."
python -c "from run import app; print('✓ Application chargée avec succès')"

echo "=== Déploiement terminé ==="
echo ""
echo "📋 Prochaines étapes:"
echo "1. Uploadez tous les fichiers vers public_html/ sur Hostinger"
echo "2. Configurez le cron job pour ./maintenance.sh (quotidien)"
echo "3. Créez l'administrateur avec: python run.py create_admin"
echo "4. Testez l'application sur votre domaine"
echo ""
echo "📖 Consultez hostinger_config.md pour plus de détails"