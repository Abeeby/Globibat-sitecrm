# 🚀 Guide Déploiement sur VPS Hostinger - Globibat CRM

## 📋 Prérequis VPS

- VPS Ubuntu 20.04/22.04 ou Debian 11/12
- Accès root SSH
- Au moins 2GB RAM
- 20GB d'espace disque

## 1️⃣ Connexion au VPS

```bash
# Depuis votre terminal Windows/PowerShell
ssh root@VOTRE_IP_VPS
```

## 2️⃣ Installation des Dépendances Système

```bash
# Mettre à jour le système
apt update && apt upgrade -y

# Installer Python et dépendances
apt install python3 python3-pip python3-venv python3-dev -y
apt install mysql-server nginx git -y
apt install build-essential libssl-dev libffi-dev -y

# Vérifier les versions
python3 --version  # Doit être 3.8+
mysql --version
nginx -v
```

## 3️⃣ Configuration MySQL

```bash
# Sécuriser MySQL
mysql_secure_installation
# Répondre Y à toutes les questions
# Définir un mot de passe root fort

# Se connecter à MySQL
mysql -u root -p

# Créer la base de données et l'utilisateur
CREATE DATABASE globibat_crm CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'globibat_user'@'localhost' IDENTIFIED BY 'MotDePasseFort123!';
GRANT ALL PRIVILEGES ON globibat_crm.* TO 'globibat_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

## 4️⃣ Configuration du Projet

```bash
# Créer le répertoire web
mkdir -p /var/www/globibat
cd /var/www/globibat

# Cloner ou uploader votre projet
# Option 1 : Via Git (si vous avez un repo)
git clone https://votre-repo.git .

# Option 2 : Via SCP depuis votre PC
# Sur votre PC Windows, dans PowerShell :
# scp -r "C:\Users\AminT\Downloads\Globibat badge\Globibat_Badge_System\*" root@VOTRE_IP_VPS:/var/www/globibat/

# Créer l'environnement virtuel
python3 -m venv venv
source venv/bin/activate

# Installer les dépendances
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn
```

## 5️⃣ Configuration du Fichier .env

```bash
# Créer le fichier .env
nano /var/www/globibat/.env
```

Contenu (remplacez DATABASE_URL) :
```env
SECRET_KEY=globibat-crm-2024-secret-key-très-longue-et-complexe-ne-jamais-partager
FLASK_ENV=production
DATABASE_URL=mysql://globibat_user:MotDePasseFort123!@localhost:3306/globibat_crm
MAIL_SERVER=smtp.hostinger.com
MAIL_PORT=465
MAIL_USE_SSL=True
MAIL_USE_TLS=False
MAIL_USERNAME=info@globibat.com
MAIL_PASSWORD=Miser1597532684$
MAIL_DEFAULT_SENDER=info@globibat.com
DOMAIN_NAME=www.globibat.com
DOMAIN_ALT=globibat.ch
SESSION_COOKIE_SECURE=True
SESSION_COOKIE_HTTPONLY=True
SESSION_COOKIE_SAMESITE=Lax
WTF_CSRF_ENABLED=True
WTF_CSRF_TIME_LIMIT=None
API_KEY=CfGCaMikAbXvnvJvmnuFlsCNS5jYx9Gm5zcCvqd9qLs
UPLOAD_FOLDER=app/static/uploads
MAX_CONTENT_LENGTH=16777216
LOG_LEVEL=INFO
LOG_FILE=instance/logs/app.log
```

## 6️⃣ Initialiser l'Application

```bash
# Toujours dans l'environnement virtuel
cd /var/www/globibat
source venv/bin/activate

# Créer les dossiers nécessaires
mkdir -p instance/logs
mkdir -p app/static/uploads

# Initialiser la base de données
python run.py init_db

# Créer l'administrateur
python run.py create_admin
# Email: admin@globibat.ch
# Mot de passe: [choisir un fort]
```

## 7️⃣ Configuration Gunicorn

```bash
# Créer le fichier de service systemd
nano /etc/systemd/system/globibat.service
```

Contenu :
```ini
[Unit]
Description=Globibat CRM
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/globibat
Environment="PATH=/var/www/globibat/venv/bin"
ExecStart=/var/www/globibat/venv/bin/gunicorn --workers 3 --bind unix:globibat.sock -m 007 wsgi:app

[Install]
WantedBy=multi-user.target
```

```bash
# Définir les permissions
chown -R www-data:www-data /var/www/globibat

# Démarrer le service
systemctl start globibat
systemctl enable globibat
systemctl status globibat
```

## 8️⃣ Configuration Nginx

```bash
# Créer la configuration Nginx
nano /etc/nginx/sites-available/globibat
```

Contenu :
```nginx
server {
    listen 80;
    server_name www.globibat.com globibat.ch;

    location / {
        include proxy_params;
        proxy_pass http://unix:/var/www/globibat/globibat.sock;
    }

    location /static {
        alias /var/www/globibat/app/static;
        expires 30d;
    }

    client_max_body_size 16M;
}
```

```bash
# Activer le site
ln -s /etc/nginx/sites-available/globibat /etc/nginx/sites-enabled
nginx -t
systemctl restart nginx
```

## 9️⃣ Configuration SSL avec Let's Encrypt

```bash
# Installer Certbot
apt install certbot python3-certbot-nginx -y

# Obtenir les certificats SSL
certbot --nginx -d www.globibat.com -d globibat.ch
# Suivre les instructions, entrer votre email

# Renouvellement automatique
systemctl enable certbot.timer
```

## 🔟 Configuration du Firewall

```bash
# Configurer UFW
ufw allow 22/tcp   # SSH
ufw allow 80/tcp   # HTTP
ufw allow 443/tcp  # HTTPS
ufw --force enable
```

## 🛠️ Maintenance et Monitoring

### Script de sauvegarde automatique
```bash
# Créer le script
nano /var/www/globibat/backup.sh
```

```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/var/backups/globibat"
mkdir -p $BACKUP_DIR

# Backup database
mysqldump -u globibat_user -p'MotDePasseFort123!' globibat_crm > $BACKUP_DIR/db_$DATE.sql

# Backup uploads
tar -czf $BACKUP_DIR/uploads_$DATE.tar.gz /var/www/globibat/app/static/uploads

# Garder seulement 30 jours
find $BACKUP_DIR -name "*.sql" -mtime +30 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete
```

```bash
chmod +x /var/www/globibat/backup.sh

# Ajouter au cron
crontab -e
# Ajouter : 0 2 * * * /var/www/globibat/backup.sh
```

### Monitoring des logs
```bash
# Voir les logs de l'application
tail -f /var/www/globibat/instance/logs/app.log

# Voir les logs Nginx
tail -f /var/log/nginx/error.log

# Voir les logs du service
journalctl -u globibat -f
```

## ✅ Vérification Finale

1. Accédez à https://www.globibat.com
2. Vérifiez le certificat SSL
3. Connectez-vous avec admin@globibat.ch
4. Testez toutes les fonctionnalités

## 🆘 Dépannage

### Service ne démarre pas
```bash
journalctl -u globibat -n 50
```

### Erreur 502 Bad Gateway
```bash
# Vérifier que le socket existe
ls -la /var/www/globibat/globibat.sock

# Redémarrer les services
systemctl restart globibat
systemctl restart nginx
```

### Problème de permissions
```bash
chown -R www-data:www-data /var/www/globibat
chmod -R 755 /var/www/globibat
chmod -R 777 /var/www/globibat/instance
chmod -R 777 /var/www/globibat/app/static/uploads
```

---

**🎉 Votre CRM Globibat est maintenant déployé sur votre VPS !**