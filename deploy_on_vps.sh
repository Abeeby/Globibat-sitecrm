#!/bin/bash
# Script de déploiement automatique pour VPS Hostinger
# Pour Globibat CRM - IP: 148.230.105.25

echo "=== Déploiement Globibat CRM sur VPS ==="

# Variables
VPS_IP="148.230.105.25"
DB_NAME="globibat_crm"
DB_USER="globibat_user"
DB_PASS="Globibat2024Secure!"
APP_DIR="/var/www/globibat"

# Étape 1: Extraction des fichiers
echo "📦 Extraction des fichiers..."
cd /var/www
mkdir -p globibat
cd globibat

# Extraire l'archive uploadée
if [ -f /tmp/globibat_upload.zip ]; then
    tar -xzf /tmp/globibat_upload.zip
    rm /tmp/globibat_upload.zip
    echo "✅ Fichiers extraits"
else
    echo "❌ Archive non trouvée dans /tmp/"
    exit 1
fi

# Étape 2: Installation des dépendances système
echo "📦 Installation des dépendances système..."
apt update
apt install -y python3-pip python3-venv python3-dev mysql-server nginx git

# Étape 3: Configuration MySQL
echo "🗄️ Configuration de la base de données..."
mysql -u root <<EOF
CREATE DATABASE IF NOT EXISTS ${DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS '${DB_USER}'@'localhost' IDENTIFIED BY '${DB_PASS}';
GRANT ALL PRIVILEGES ON ${DB_NAME}.* TO '${DB_USER}'@'localhost';
FLUSH PRIVILEGES;
EOF
echo "✅ Base de données configurée"

# Étape 4: Configuration de l'environnement Python
echo "🐍 Configuration de l'environnement Python..."
cd $APP_DIR
python3 -m venv venv
source venv/bin/activate

# Installer les dépendances
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn

# Étape 5: Configuration du fichier .env
echo "⚙️ Configuration des variables d'environnement..."
cat > .env <<EOF
SECRET_KEY=globibat-crm-2024-secret-key-très-longue-et-complexe-ne-jamais-partager
FLASK_ENV=production

# Base de données MySQL
DATABASE_URL=mysql://${DB_USER}:${DB_PASS}@localhost:3306/${DB_NAME}

# Email Configuration
MAIL_SERVER=smtp.hostinger.com
MAIL_PORT=465
MAIL_USE_SSL=True
MAIL_USE_TLS=False
MAIL_USERNAME=info@globibat.com
MAIL_PASSWORD=Miser1597532684\$
MAIL_DEFAULT_SENDER=info@globibat.com

# Domaines
DOMAIN_NAME=www.globibat.com
DOMAIN_ALT=globibat.ch

# Sécurité
SESSION_COOKIE_SECURE=True
SESSION_COOKIE_HTTPONLY=True
SESSION_COOKIE_SAMESITE=Lax
WTF_CSRF_ENABLED=True

# API Key
API_KEY=CfGCaMikAbXvnvJvmnuFlsCNS5jYx9Gm5zcCvqd9qLs

# Chemins
UPLOAD_FOLDER=app/static/uploads
MAX_CONTENT_LENGTH=16777216
LOG_FILE=instance/logs/app.log
EOF

# Créer les dossiers nécessaires
mkdir -p instance/logs
mkdir -p app/static/uploads
chmod 755 instance/logs app/static/uploads

# Étape 6: Initialisation de la base de données
echo "🗄️ Initialisation de la base de données..."
python run.py init_db

# Étape 7: Configuration Nginx
echo "🌐 Configuration du serveur web..."
cat > /etc/nginx/sites-available/globibat <<EOF
server {
    listen 80;
    server_name ${VPS_IP} www.globibat.com globibat.ch;

    root ${APP_DIR};
    
    # Page d'accueil statique
    location = / {
        try_files /index.html @app;
    }
    
    location = /index.html {
        try_files \$uri @app;
    }
    
    # Fichiers statiques
    location /static {
        alias ${APP_DIR}/app/static;
        expires 30d;
    }
    
    location /robots.txt {
        alias ${APP_DIR}/robots.txt;
    }
    
    location /sitemap.xml {
        alias ${APP_DIR}/sitemap.xml;
    }
    
    # Application Flask
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# Activer le site
ln -sf /etc/nginx/sites-available/globibat /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl restart nginx

# Étape 8: Service systemd pour Gunicorn
echo "⚙️ Configuration du service Gunicorn..."
cat > /etc/systemd/system/globibat.service <<EOF
[Unit]
Description=Globibat CRM
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=${APP_DIR}
Environment="PATH=${APP_DIR}/venv/bin"
ExecStart=${APP_DIR}/venv/bin/gunicorn -w 4 -b 127.0.0.1:5000 wsgi:app
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Permissions
chown -R www-data:www-data $APP_DIR
chmod -R 755 $APP_DIR

# Démarrer le service
systemctl daemon-reload
systemctl enable globibat
systemctl start globibat

# Étape 9: Firewall
echo "🔒 Configuration du firewall..."
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
echo "y" | ufw enable

# Étape 10: Créer l'admin
echo "👤 Création du compte administrateur..."
cd $APP_DIR
source venv/bin/activate
python run.py create_admin

echo "
✅ ========================================
✅ DÉPLOIEMENT TERMINÉ AVEC SUCCÈS !
✅ ========================================

📌 Votre site est accessible à :
   - http://${VPS_IP}/
   - http://${VPS_IP}/index.html (Page publique)
   - http://${VPS_IP}/login (CRM Backend)

📊 Statut des services :
"
systemctl status globibat --no-pager
systemctl status nginx --no-pager

echo "
💡 Commandes utiles :
   - Logs : journalctl -u globibat -f
   - Restart : systemctl restart globibat
   - Status : systemctl status globibat
"