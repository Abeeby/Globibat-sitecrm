#!/bin/bash
# Script de déploiement complet pour VPS
# Optimisé pour le système CRM/Badge avancé Globibat

echo "=================================================="
echo "🚀 DÉPLOIEMENT COMPLET GLOBIBAT CRM SUR VPS"
echo "=================================================="

# Variables de configuration
PROJECT_DIR="/var/www/globibat"
BACKUP_DIR="/var/backups/globibat"
SERVICE_NAME="globibat"
NGINX_SITE="globibat"

# Couleurs pour les messages
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Fonction pour afficher les messages
log_success() { echo -e "${GREEN}✅ $1${NC}"; }
log_info() { echo -e "${YELLOW}ℹ️  $1${NC}"; }
log_error() { echo -e "${RED}❌ $1${NC}"; }

# Vérification des droits root
if [[ $EUID -ne 0 ]]; then
   log_error "Ce script doit être exécuté en tant que root"
   exit 1
fi

# Étape 1: Backup de l'ancien système
echo -e "\n[1/10] 📦 Backup du système existant..."
if [ -d "$PROJECT_DIR" ]; then
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    mkdir -p "$BACKUP_DIR"
    tar -czf "$BACKUP_DIR/backup_$TIMESTAMP.tar.gz" "$PROJECT_DIR"
    log_success "Backup créé: $BACKUP_DIR/backup_$TIMESTAMP.tar.gz"
else
    log_info "Pas de système existant à sauvegarder"
fi

# Étape 2: Arrêt des services
echo -e "\n[2/10] 🛑 Arrêt des services..."
systemctl stop $SERVICE_NAME 2>/dev/null || log_info "Service $SERVICE_NAME non trouvé"
systemctl stop nginx

# Étape 3: Mise à jour du code
echo -e "\n[3/10] 📥 Mise à jour du code source..."
if [ ! -d "$PROJECT_DIR" ]; then
    mkdir -p "$PROJECT_DIR"
fi

# Copier les nouveaux fichiers
cp -r . "$PROJECT_DIR/"
log_success "Code source mis à jour"

# Étape 4: Configuration de l'environnement
echo -e "\n[4/10] 🐍 Configuration de l'environnement Python..."
cd "$PROJECT_DIR"

# Créer l'environnement virtuel s'il n'existe pas
if [ ! -d "venv" ]; then
    python3 -m venv venv
    log_success "Environnement virtuel créé"
fi

# Activer l'environnement et installer les dépendances
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
log_success "Dépendances installées"

# Étape 5: Configuration des permissions
echo -e "\n[5/10] 🔐 Configuration des permissions..."
chown -R www-data:www-data "$PROJECT_DIR"
chmod -R 755 "$PROJECT_DIR"
chmod -R 777 "$PROJECT_DIR/instance"
chmod -R 777 "$PROJECT_DIR/app/static/uploads"

# Créer les dossiers nécessaires
mkdir -p "$PROJECT_DIR/instance/logs"
mkdir -p "$PROJECT_DIR/app/static/uploads/receipts"
mkdir -p "$PROJECT_DIR/app/static/uploads/photos"
mkdir -p "$PROJECT_DIR/app/static/uploads/documents"
log_success "Permissions configurées"

# Étape 6: Initialisation de la base de données
echo -e "\n[6/10] 🗄️ Initialisation de la base de données..."
python init_database.py
log_success "Base de données initialisée"

# Étape 7: Configuration Gunicorn
echo -e "\n[7/10] 🦄 Configuration de Gunicorn..."
cat > /etc/systemd/system/$SERVICE_NAME.service << EOF
[Unit]
Description=Globibat CRM Gunicorn Application
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=$PROJECT_DIR
Environment="PATH=$PROJECT_DIR/venv/bin"
ExecStart=$PROJECT_DIR/venv/bin/gunicorn --workers 4 --bind unix:$PROJECT_DIR/$SERVICE_NAME.sock --log-level info --access-logfile $PROJECT_DIR/instance/logs/access.log --error-logfile $PROJECT_DIR/instance/logs/error.log run:app

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable $SERVICE_NAME
log_success "Service Gunicorn configuré"

# Étape 8: Configuration Nginx
echo -e "\n[8/10] 🌐 Configuration de Nginx..."
cat > /etc/nginx/sites-available/$NGINX_SITE << EOF
server {
    listen 80;
    server_name www.globibat.com globibat.ch;
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name www.globibat.com globibat.ch;

    # SSL configuration (à adapter selon vos certificats)
    ssl_certificate /etc/letsencrypt/live/globibat.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/globibat.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # Logs
    access_log /var/log/nginx/globibat_access.log;
    error_log /var/log/nginx/globibat_error.log;

    # Limite de taille pour les uploads
    client_max_body_size 16M;

    # Timeouts
    proxy_connect_timeout 300s;
    proxy_send_timeout 300s;
    proxy_read_timeout 300s;

    location / {
        include proxy_params;
        proxy_pass http://unix:$PROJECT_DIR/$SERVICE_NAME.sock;
    }

    location /static {
        alias $PROJECT_DIR/app/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Sécurité
    add_header X-Content-Type-Options nosniff;
    add_header X-Frame-Options DENY;
    add_header X-XSS-Protection "1; mode=block";
    add_header Referrer-Policy "strict-origin-when-cross-origin";
}
EOF

# Activer le site
ln -sf /etc/nginx/sites-available/$NGINX_SITE /etc/nginx/sites-enabled/
nginx -t && log_success "Configuration Nginx valide"

# Étape 9: Démarrage des services
echo -e "\n[9/10] 🚀 Démarrage des services..."
systemctl start $SERVICE_NAME
systemctl start nginx
systemctl status $SERVICE_NAME --no-pager
log_success "Services démarrés"

# Étape 10: Configuration des tâches planifiées
echo -e "\n[10/10] ⏰ Configuration des tâches planifiées..."
cat > /etc/cron.d/globibat << EOF
# Backup quotidien à 2h du matin
0 2 * * * root cd $PROJECT_DIR && ./scripts/backup.sh

# Nettoyage des fichiers temporaires tous les dimanches
0 3 * * 0 root find $PROJECT_DIR/app/static/uploads -name "*.tmp" -mtime +7 -delete

# Vérification de conformité hebdomadaire
0 8 * * 1 root cd $PROJECT_DIR && venv/bin/python -c "from app.utils.scheduler import check_weekly_compliance; check_weekly_compliance()"
EOF
log_success "Tâches planifiées configurées"

# Résumé final
echo -e "\n=================================================="
echo -e "${GREEN}✨ DÉPLOIEMENT TERMINÉ AVEC SUCCÈS!${NC}"
echo "=================================================="
echo "🌐 Votre application est accessible sur:"
echo "   https://www.globibat.com"
echo "   https://globibat.ch"
echo ""
echo "📧 Compte administrateur:"
echo "   Email: admin@globibat.ch"
echo "   Mot de passe: Admin2024!"
echo ""
echo "📊 Vérifications:"
echo "   - Logs d'accès: tail -f $PROJECT_DIR/instance/logs/access.log"
echo "   - Logs d'erreur: tail -f $PROJECT_DIR/instance/logs/error.log"
echo "   - Service status: systemctl status $SERVICE_NAME"
echo ""
echo "⚠️  IMPORTANT:"
echo "   1. Changez le mot de passe admin après la première connexion"
echo "   2. Vérifiez que votre fichier .env contient les bonnes credentials"
echo "   3. Configurez les certificats SSL si pas déjà fait"
echo "=================================================="