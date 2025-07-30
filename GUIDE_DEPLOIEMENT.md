# 🚀 Guide de Déploiement - Système de Badgeage Globibat

## Option 1 : Hostinger VPS (Si vous avez un VPS)

### Prérequis
- VPS avec Ubuntu 20.04 ou plus récent
- Accès SSH à votre VPS

### Étapes de déploiement

1. **Connectez-vous à votre VPS**
```bash
ssh votreuser@votre-ip-vps
```

2. **Installez les dépendances système**
```bash
sudo apt update
sudo apt install python3-pip python3-venv nginx supervisor postgresql postgresql-contrib
```

3. **Clonez votre application**
```bash
cd /var/www
sudo git clone [votre-repo] globibat
cd globibat
```

4. **Créez l'environnement virtuel**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements_production.txt
```

5. **Configurez PostgreSQL** (recommandé pour la production)
```bash
sudo -u postgres psql
CREATE DATABASE badgeage_db;
CREATE USER globibat_user WITH PASSWORD 'motdepasse_securise';
GRANT ALL PRIVILEGES ON DATABASE badgeage_db TO globibat_user;
\q
```

6. **Variables d'environnement**
Créez un fichier `.env`:
```
SECRET_KEY=une-cle-tres-securisee-generee-aleatoirement
DATABASE_URL=postgresql://globibat_user:motdepasse_securise@localhost/badgeage_db
```

7. **Configurez Nginx**
```nginx
server {
    listen 80;
    server_name votre-domaine.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /static {
        alias /var/www/globibat/static;
    }
}
```

8. **Configurez Supervisor**
```ini
[program:globibat]
command=/var/www/globibat/venv/bin/gunicorn -w 4 -b 127.0.0.1:8000 wsgi:app
directory=/var/www/globibat
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
```

9. **Démarrez l'application**
```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start globibat
sudo systemctl restart nginx
```

---

## Option 2 : Render.com (GRATUIT et SIMPLE) ⭐ Recommandé

### Avantages
- ✅ Gratuit pour petites applications
- ✅ HTTPS automatique
- ✅ Déploiement automatique depuis GitHub
- ✅ Base de données PostgreSQL gratuite

### Étapes

1. **Préparez votre code sur GitHub**
   - Créez un compte GitHub si nécessaire
   - Uploadez votre code

2. **Créez un compte sur Render.com**
   - Allez sur https://render.com
   - Inscrivez-vous gratuitement

3. **Créez un nouveau Web Service**
   - Cliquez sur "New +"
   - Choisissez "Web Service"
   - Connectez votre GitHub
   - Sélectionnez votre repository

4. **Configuration**
   - Name: `globibat-badge`
   - Environment: `Python 3`
   - Build Command: `pip install -r requirements_production.txt`
   - Start Command: `gunicorn wsgi:app`

5. **Variables d'environnement**
   Ajoutez dans Render:
   - `SECRET_KEY` : générez une clé sécurisée
   - `DATABASE_URL` : sera fourni automatiquement si vous créez une DB

6. **Créez une base de données PostgreSQL**
   - New + → PostgreSQL
   - Connectez-la à votre app

7. **Déployez !**
   - Render déploiera automatiquement
   - Vous aurez une URL comme : https://globibat-badge.onrender.com

---

## Option 3 : PythonAnywhere (Gratuit)

### Étapes

1. **Créez un compte sur PythonAnywhere**
   - https://www.pythonanywhere.com
   - Plan gratuit "Beginner"

2. **Uploadez vos fichiers**
   - Via l'interface web ou Git

3. **Configurez l'application Flask**
   - Dans "Web" → "Add a new web app"
   - Choisissez Flask
   - Python 3.10

4. **Modifiez le fichier WSGI**
```python
import sys
path = '/home/votreusername/globibat'
if path not in sys.path:
    sys.path.append(path)

from app import app as application
```

5. **Base de données**
   - PythonAnywhere supporte SQLite gratuitement
   - MySQL disponible aussi

---

## Option 4 : Railway.app (Simple et moderne)

### Étapes

1. **Installez Railway CLI**
```bash
npm install -g @railway/cli
```

2. **Dans votre dossier projet**
```bash
railway login
railway init
railway add
railway up
```

3. **Variables d'environnement**
   Dans le dashboard Railway, ajoutez vos variables

4. **Déployez**
   Railway déploiera automatiquement avec une URL

---

## 🔒 Sécurisation pour la production

### 1. **Générez une vraie clé secrète**
```python
import secrets
print(secrets.token_hex(32))
```

### 2. **Utilisez HTTPS** (automatique sur Render/Railway)

### 3. **Limitez les accès**
Ajoutez dans votre app:
```python
from flask_limiter import Limiter
limiter = Limiter(app, key_func=lambda: request.remote_addr)

@app.route('/badge', methods=['POST'])
@limiter.limit("10 per minute")
def badge():
    # votre code
```

### 4. **Sauvegardez régulièrement**
- Configurez des backups automatiques de la DB
- Exportez les données régulièrement

---

## 📱 Accès mobile

Une fois déployé, votre application sera accessible depuis :
- 💻 Ordinateurs
- 📱 Smartphones
- 📱 Tablettes

L'interface est déjà responsive !

---

## 🆘 Support

### Problèmes fréquents

1. **"Application Error" sur Render**
   - Vérifiez les logs
   - Assurez-vous que requirements.txt est correct

2. **Base de données vide**
   - L'admin par défaut sera recréé automatiquement
   - Réimportez vos employés

3. **Erreur 500**
   - Vérifiez les variables d'environnement
   - Regardez les logs d'erreur

### Commandes utiles

**Voir les logs (Render)**
```bash
render logs --tail
```

**Redémarrer l'app**
- Sur Render : Manual Deploy → Deploy
- Sur VPS : `sudo supervisorctl restart globibat`

---

## 🎉 Félicitations !

Votre système de badgeage est maintenant accessible depuis n'importe où dans le monde !

### URLs importantes
- Application : https://votre-app.onrender.com
- Admin : https://votre-app.onrender.com/login
- Badgeage : https://votre-app.onrender.com/badge 