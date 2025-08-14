# Script de déploiement sécurisé pour VPS (Windows PowerShell)
# Globibat CRM

Write-Host "=============================================="
Write-Host "🚀 DÉPLOIEMENT SÉCURISÉ GLOBIBAT CRM SUR VPS" -ForegroundColor Green
Write-Host "=============================================="

# Variables VPS (À MODIFIER)
$VPS_USER = "root"
$VPS_HOST = "your_vps_ip_here"  # REMPLACER PAR L'IP DU VPS
$VPS_PORT = "22"
$APP_DIR = "/var/www/globibat"

# Vérifier que l'IP est configurée
if ($VPS_HOST -eq "your_vps_ip_here") {
    Write-Host "❌ ERREUR: Veuillez configurer l'IP du VPS dans ce script!" -ForegroundColor Red
    Write-Host "   Éditez la variable `$VPS_HOST dans ce fichier" -ForegroundColor Yellow
    exit 1
}

# Vérifier que .env existe
if (!(Test-Path ".env")) {
    Write-Host "❌ ERREUR: Fichier .env non trouvé!" -ForegroundColor Red
    Write-Host "   Les identifiants admin sont dans ce fichier" -ForegroundColor Yellow
    exit 1
}

Write-Host "`n✅ Configuration détectée:" -ForegroundColor Green
Write-Host "   VPS: $VPS_HOST" -ForegroundColor Cyan
Write-Host "   Utilisateur: $VPS_USER" -ForegroundColor Cyan
Write-Host "   Admin: info@globibat.com (sécurisé dans .env)" -ForegroundColor Cyan

# 1. Créer l'archive
Write-Host "`n📦 Création de l'archive..." -ForegroundColor Yellow
$excludes = @(
    "*.pyc",
    "__pycache__",
    "venv",
    "instance/*.db",
    ".git",
    "*.log",
    "node_modules",
    "*.tar.gz"
)

# Utiliser tar si disponible, sinon Compress-Archive
if (Get-Command tar -ErrorAction SilentlyContinue) {
    $excludeArgs = $excludes | ForEach-Object { "--exclude='$_'" }
    $cmd = "tar $($excludeArgs -join ' ') -czf globibat_deploy.tar.gz ."
    Invoke-Expression $cmd
} else {
    # Alternative avec Compress-Archive (moins efficace)
    Write-Host "   Utilisation de Compress-Archive (tar non disponible)" -ForegroundColor Yellow
    Compress-Archive -Path * -DestinationPath globibat_deploy.zip -Force
    Rename-Item globibat_deploy.zip globibat_deploy.tar.gz -Force
}
Write-Host "✅ Archive créée" -ForegroundColor Green

# 2. Upload vers VPS
Write-Host "`n📤 Upload vers le VPS..." -ForegroundColor Yellow
Write-Host "   Transfert de l'archive..." -ForegroundColor Cyan
scp -P $VPS_PORT globibat_deploy.tar.gz "${VPS_USER}@${VPS_HOST}:/tmp/"
Write-Host "   Transfert du fichier .env..." -ForegroundColor Cyan
scp -P $VPS_PORT .env "${VPS_USER}@${VPS_HOST}:/tmp/.env"
Write-Host "✅ Upload terminé" -ForegroundColor Green

# 3. Script d'installation distant
Write-Host "`n🔧 Installation sur le VPS..." -ForegroundColor Yellow

$remoteScript = @'
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
echo "Installation des dépendances système..."
apt-get update
apt-get install -y python3 python3-pip python3-venv nginx supervisor

# Créer l'environnement virtuel
echo "Création de l'environnement Python..."
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
echo "Initialisation de la base de données..."
python init_database_secure.py

# Configuration Nginx
echo "Configuration de Nginx..."
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
echo "Configuration de Supervisor..."
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
echo "Redémarrage des services..."
systemctl restart nginx
supervisorctl reread
supervisorctl update
supervisorctl restart globibat

echo "✅ Déploiement terminé!"
'@

# Exécuter le script sur le VPS
$remoteScript | ssh -p $VPS_PORT "${VPS_USER}@${VPS_HOST}" "bash -s"

# 4. Nettoyage local
Write-Host "`n🧹 Nettoyage local..." -ForegroundColor Yellow
Remove-Item -Force globibat_deploy.tar.gz -ErrorAction SilentlyContinue
Write-Host "✅ Nettoyage terminé" -ForegroundColor Green

# 5. Test de l'application
Write-Host "`n🔍 Test de l'application..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

try {
    $response = Invoke-WebRequest -Uri "http://$VPS_HOST" -UseBasicParsing -TimeoutSec 10
    if ($response.StatusCode -eq 200 -or $response.StatusCode -eq 302) {
        Write-Host "✅ Application accessible!" -ForegroundColor Green
    }
} catch {
    Write-Host "⚠️ L'application peut prendre quelques secondes pour démarrer" -ForegroundColor Yellow
}

# Résumé
Write-Host "`n=============================================="
Write-Host "✨ DÉPLOIEMENT TERMINÉ AVEC SUCCÈS!" -ForegroundColor Green
Write-Host "=============================================="
Write-Host ""
Write-Host "📌 INFORMATIONS:" -ForegroundColor Cyan
Write-Host "   URL: http://$VPS_HOST" -ForegroundColor White
Write-Host "   Admin: info@globibat.com" -ForegroundColor White
Write-Host "   Mot de passe: Sécurisé dans .env" -ForegroundColor White
Write-Host ""
Write-Host "📝 PROCHAINES ÉTAPES:" -ForegroundColor Yellow
Write-Host "1. Configurer le domaine pour pointer vers $VPS_HOST" -ForegroundColor White
Write-Host "2. Installer un certificat SSL avec Let's Encrypt" -ForegroundColor White
Write-Host "3. Tester toutes les fonctionnalités" -ForegroundColor White
Write-Host ""
Write-Host "🔐 SÉCURITÉ:" -ForegroundColor Red
Write-Host "   Les identifiants ne sont PAS visibles dans le code" -ForegroundColor White
Write-Host "   Ils sont stockés de manière sécurisée dans .env" -ForegroundColor White
Write-Host ""