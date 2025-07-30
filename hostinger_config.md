# Guide de Configuration Hostinger pour Globibat CRM

## 1. Variables d'Environnement

Créez un fichier `.env` à la racine du projet avec ces variables :

```env
# Flask
SECRET_KEY=votre-cle-secrete-tres-longue-et-complexe
FLASK_ENV=production

# Base de données MySQL Hostinger
DATABASE_URL=mysql://username:password@localhost:3306/database_name

# Email (SMTP Hostinger)
MAIL_SERVER=smtp.hostinger.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=votre-email@votredomaine.com
MAIL_PASSWORD=votre-mot-de-passe-email
MAIL_DEFAULT_SENDER=votre-email@votredomaine.com

# Domaine
DOMAIN_NAME=www.globibat.ch

# Sécurité
SESSION_COOKIE_SECURE=True
SESSION_COOKIE_HTTPONLY=True
SESSION_COOKIE_SAMESITE=Lax

# API Key
API_KEY=votre-cle-api-secrete
```

## 2. Configuration Base de Données MySQL

Dans votre panneau Hostinger :
1. Créez une base de données MySQL
2. Créez un utilisateur avec tous les privilèges
3. Notez les informations de connexion

## 3. Déploiement

### Étape 1 : Upload des fichiers
```bash
# Via FTP ou panneau de fichiers Hostinger
# Uploadez tout le contenu du dossier Globibat_Badge_System
# dans public_html/
```

### Étape 2 : Installation des dépendances
```bash
# Se connecter en SSH
cd public_html
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Étape 3 : Initialiser la base de données
```bash
python run.py init_db
python run.py create_admin
```

### Étape 4 : Configuration du serveur web

Créez un fichier `.htaccess` dans public_html :
```apache
RewriteEngine On
RewriteCond %{REQUEST_FILENAME} !-f
RewriteCond %{REQUEST_FILENAME} !-d
RewriteRule ^(.*)$ /wsgi.py/$1 [QSA,L]

# Force HTTPS
RewriteCond %{HTTPS} off
RewriteRule ^(.*)$ https://%{HTTP_HOST}%{REQUEST_URI} [L,R=301]
```

### Étape 5 : Script de démarrage

Créez `start.sh` :
```bash
#!/bin/bash
source venv/bin/activate
gunicorn --workers 4 --bind 0.0.0.0:5000 wsgi:app
```

## 4. Maintenance

### Sauvegardes automatiques
```bash
# Créer un cron job pour sauvegarder la DB
0 2 * * * mysqldump -u username -p'password' database_name > backup_$(date +\%Y\%m\%d).sql
```

### Logs
Les logs sont dans :
- `instance/logs/app.log`
- Logs Hostinger dans le panneau de contrôle

## 5. SSL et Sécurité

1. Activez SSL gratuit Let's Encrypt dans Hostinger
2. Forcez HTTPS via .htaccess (déjà configuré)
3. Configurez les headers de sécurité (déjà dans l'app)

## 6. Performance

1. Activez la compression Gzip dans Hostinger
2. Configurez le cache statique via .htaccess
3. Utilisez CDN Cloudflare (optionnel)

## 7. Monitoring

1. Activez les alertes email dans Hostinger
2. Configurez Sentry (optionnel) en ajoutant SENTRY_DSN
3. Vérifiez régulièrement les logs