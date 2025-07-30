# 🚀 Guide de Déploiement sur Hostinger VPS

## 📌 Informations nécessaires
- **IP du VPS** : (fournie par Hostinger après création)
- **Utilisateur** : root
- **Mot de passe** : (celui que vous avez créé)

## 🔧 Étape 1 : Connexion au VPS

### Sur Windows (PowerShell) :
```bash
ssh root@VOTRE_IP_VPS
```
Exemple : `ssh root@185.123.45.67`

Entrez le mot de passe quand demandé.

## 📦 Étape 2 : Préparation du serveur

Copiez-collez ces commandes une par une :

```bash
# Mettre à jour le système
apt update && apt upgrade -y

# Installer Python et les outils nécessaires
apt install python3 python3-pip python3-venv nginx supervisor postgresql postgresql-contrib -y

# Installer Git
apt install git -y

# Créer un utilisateur pour l'application (sécurité)
adduser globibat --disabled-password --gecos ""
usermod -aG sudo globibat
```

## 📂 Étape 3 : Installer l'application

```bash
# Aller dans le bon dossier
cd /var/www

# Créer le dossier et donner les permissions
mkdir globibat
chown globibat:globibat globibat
cd globibat

# Basculer vers l'utilisateur globibat
su - globibat
cd /var/www/globibat
```

## 🔄 Étape 4 : Transférer votre code

### Option A : Via Git (recommandé si vous avez GitHub)
```bash
git clone https://github.com/VOTRE_USERNAME/globibat-badge.git .
```

### Option B : Via transfert direct
Sur votre PC Windows, utilisez WinSCP ou FileZilla :
1. Connectez-vous avec : root@VOTRE_IP_VPS
2. Naviguez vers `/var/www/globibat`
3. Uploadez tous les fichiers

## 🎉 Excellent ! Je vois que les fichiers sont bien transférés !

Maintenant, continuons avec la configuration sur le serveur.

### 📝 Dans PowerShell (connexion SSH), exécutez ces commandes :

#### 1. Configuration Python et installation des dépendances

```bash
cd /var/www/globibat
python3 -m venv venv
source venv/bin/activate
pip install -r requirements_production.txt
```

#### 2. Configuration de PostgreSQL

```bash
# Configurer PostgreSQL
sudo -u postgres psql
```

Une fois dans PostgreSQL (vous verrez `postgres=#`), copiez-collez :

```sql
CREATE DATABASE badgeage_db;
CREATE USER globibat_user WITH PASSWORD 'MotDePasseSecurise123!';
GRANT ALL PRIVILEGES ON DATABASE badgeage_db TO globibat_user;
\q
```

#### 3. Créer le fichier de configuration

```bash
# Créer le fichier .env
nano .env
```

Dans l'éditeur nano, ajoutez :

```
SECRET_KEY=cle-secrete-globibat-2024-production
DATABASE_URL=postgresql://globibat_user:MotDePasseSecurise123!@localhost/badgeage_db
```

Sauvegardez avec `Ctrl+X`, puis `Y`, puis `Entrée`.

#### 4. Initialiser la base de données

```bash
# Toujours avec l'environnement virtuel activé
python app.py
```

Cela va créer les tables. Vous verrez l'admin créé. Après quelques secondes, arrêtez avec `Ctrl+C`.

#### 5. Configuration Nginx

```bash
# Créer la configuration Nginx
sudo nano /etc/nginx/sites-available/globibat
```

Copiez-collez :

```nginx
server {
    listen 80;
    server_name 148.230.105.25;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location /static {
        alias /var/www/globibat/static;
    }

    client_max_body_size 10M;
}
```

Sauvegardez (`Ctrl+X`, `Y`, `Entrée`).

#### 6. Activer le site

```bash
sudo ln -s /etc/nginx/sites-available/globibat /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx
```

#### 7. Configuration Supervisor

```bash
<code_block_to_apply_changes_from>
```

Copiez-collez :

```ini
[program:globibat]
command=/var/www/globibat/venv/bin/gunicorn -w 4 -b 127.0.0.1:8000 wsgi:app
directory=/var/www/globibat
user=root
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/globibat.log
environment=PATH="/var/www/globibat/venv/bin"
```

#### 8. Lancer l'application !

```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start globibat
```

### ✅ C'est terminé !

Votre application devrait maintenant être accessible à :

## 🌐 http://148.230.105.25

Essayez d'y accéder avec votre navigateur !

- **Admin** : `admin`
- **Mot de passe** : `admin123`

### 🔍 Si ça ne fonctionne pas :

Vérifiez avec :
```bash
sudo supervisorctl status globibat
sudo tail -f /var/log/globibat.log
```

Dites-moi si vous pouvez accéder à l'application !

## 🔒 Sécurisation (important !)

1. **Changez le mot de passe admin** immédiatement
2. **Configurez un firewall** :
```bash
ufw allow 22
ufw allow 80
ufw allow 443
ufw enable
```

3. **Ajoutez un nom de domaine** (si vous en avez un)
4. **Installez un certificat SSL** avec Let's Encrypt

## 🆘 Dépannage

**L'application ne démarre pas ?**
```bash
# Vérifier les logs
tail -f /var/log/globibat.log
supervisorctl status
```

**Erreur 502 Bad Gateway ?**
```bash
# Redémarrer les services
supervisorctl restart globibat
systemctl restart nginx
```

**Base de données vide ?**
```bash
su - globibat
cd /var/www/globibat
source venv/bin/activate
python
>>> from app import db, init_db
>>> init_db()
>>> exit()
``` 

Je vois le problème ! Les fichiers modifiés n'ont pas encore été transférés sur votre serveur. Voici ce qu'il faut faire :

## 🔄 1. Transférer les fichiers modifiés

### Avec FileZilla :

1. **Reconnectez-vous** à votre serveur dans FileZilla
2. **Transférez ces fichiers** du dossier local vers `/var/www/globibat/` :
   - `app.py` (modifié)
   - `reset_admin.py` (nouveau)
   - `templates/base.html` (modifié)
   - `templates/index.html` (modifié)
   - `templates/login.html` (modifié)

## 🛠️ 2. Appliquer les changements sur le serveur

Dans PowerShell (SSH), exécutez :

```bash
<code_block_to_apply_changes_from>
```

## 🔍 3. Vérifier que tout fonctionne

Après le redémarrage, vérifiez avec :

```bash
sudo supervisorctl status globibat
```

Vous devriez voir : `globibat RUNNING`

## 📝 4. Pour l'instant, utilisez l'ancienne URL

En attendant que les fichiers soient transférés :
- **URL actuelle** : http://148.230.105.25/login
- **Identifiants actuels** : `admin` / `admin123`

## ⚡ Alternative rapide :

Si vous voulez aller plus vite, je peux vous montrer comment créer le nouveau compte admin directement sans transférer tous les fichiers. Voulez-vous qu'on fasse ça ? 