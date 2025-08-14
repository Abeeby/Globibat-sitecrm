#!/bin/bash

echo "=============================================="
echo "🚀 DÉPLOIEMENT SÉCURISÉ GLOBIBAT CRM SUR VPS"
echo "=============================================="

# Variables VPS
VPS_USER="root"
VPS_HOST="your_vps_ip_here"
VPS_PORT="22"
APP_DIR="/var/www/globibat"

# Couleurs
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Fonction pour afficher les messages
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ️ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# 1. Préparation locale
print_info "Préparation des fichiers..."

# Créer une archive sans les fichiers sensibles
tar --exclude='*.pyc' \
    --exclude='__pycache__' \
    --exclude='venv' \
    --exclude='instance/*.db' \
    --exclude='.git' \
    --exclude='*.log' \
    --exclude='node_modules' \
    -czf globibat_deploy.tar.gz .

print_success "Archive créée"

# 2. Upload vers VPS
print_info "Upload vers le VPS..."
scp -P $VPS_PORT globibat_deploy.tar.gz $VPS_USER@$VPS_HOST:/tmp/
scp -P $VPS_PORT .env $VPS_USER@$VPS_HOST:/tmp/.env

# 3. Script d'installation distant
print_info "Installation sur le VPS..."

ssh -p $VPS_PORT $VPS_USER@$VPS_HOST << 'ENDSSH'
set -e

echo "Configuration sur le VPS..."

# Créer le répertoire de l'application
mkdir -p /var/www/globibat
cd /var/www/globibat

# Extraire l'archive
tar -xzf /tmp/globibat_deploy.tar.gz
cp /tmp/.env .env

# Supprimer les fichiers temporaires
rm /tmp/globibat_deploy.tar.gz
rm /tmp/.env

# Installer Python et dépendances système
apt-get update
apt-get install -y python3 python3-pip python3-venv nginx supervisor

# Créer l'environnement virtuel
python3 -m venv venv
source venv/bin/activate

# Installer les dépendances Python
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn

# Créer les dossiers nécessaires
mkdir -p instance instance/logs
mkdir -p app/static/uploads/{receipts,photos,documents}

# Initialiser la base de données avec les identifiants sécurisés
python init_database_secure.py

# Configuration Nginx
cat > /etc/nginx/sites-available/globibat << 'EOF'
server {
    listen 80;
    server_name www.globibat.com globibat.com;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /static {
        alias /var/www/globibat/app/static;
    }
    
    client_max_body_size 20M;
}
EOF

ln -sf /etc/nginx/sites-available/globibat /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Configuration Supervisor
cat > /etc/supervisor/conf.d/globibat.conf << 'EOF'
[program:globibat]
command=/var/www/globibat/venv/bin/gunicorn -w 4 -b 127.0.0.1:8000 'app:create_app()'
directory=/var/www/globibat
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/www/globibat/instance/logs/gunicorn.log
environment=PATH="/var/www/globibat/venv/bin",FLASK_ENV="production"
EOF

# Permissions
chown -R www-data:www-data /var/www/globibat

# Redémarrer les services
systemctl restart nginx
supervisorctl reread
supervisorctl update
supervisorctl restart globibat

echo "✅ Déploiement terminé!"
ENDSSH

# 4. Nettoyage local
rm -f globibat_deploy.tar.gz

# 5. Test de l'application
print_info "Test de l'application..."
sleep 5

response=$(curl -s -o /dev/null -w "%{http_code}" http://$VPS_HOST)
if [ $response -eq 200 ] || [ $response -eq 302 ]; then
    print_success "Application accessible!"
else
    print_error "Erreur: HTTP $response"
fi

# Résumé
echo ""
echo "=============================================="
echo "✨ DÉPLOIEMENT TERMINÉ AVEC SUCCÈS!"
echo "=============================================="
echo ""
echo "📌 INFORMATIONS:"
echo "   URL: http://$VPS_HOST"
echo "   Admin: Sécurisé dans .env"
echo ""
echo "📝 PROCHAINES ÉTAPES:"
echo "1. Configurer le domaine pour pointer vers $VPS_HOST"
echo "2. Installer un certificat SSL avec Let's Encrypt"
echo "3. Tester toutes les fonctionnalités"
echo ""