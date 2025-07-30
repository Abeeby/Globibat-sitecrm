# 🚀 GUIDE DE DÉPLOIEMENT FINAL - GLOBIBAT CRM SUR HOSTINGER

## ✅ Configuration Email (DÉJÀ CONFIGURÉE)
- **SMTP** : smtp.hostinger.com
- **Port** : 465 (SSL)
- **Email** : info@globibat.com
- **Mot de passe** : Miser1597532684$

## 📋 ÉTAPES À SUIVRE

### 1️⃣ Créer le fichier .env
```bash
# Copier le contenu de env_configuration.txt vers .env
# Remplacer API_KEY par : CfGCaMikAbXvnvJvmnuFlsCNS5jYx9Gm5zcCvqd9qLs
```

**Contenu final de .env** (copier-coller ceci) :
```env
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
MAIL_PASSWORD=Miser1597532684$
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
```

### 2️⃣ Sur Hostinger - Créer Base de Données MySQL

1. **Panneau Hostinger** → **Bases de données** → **MySQL**
2. **Créer une nouvelle base de données** :
   - Nom de la base : `globibat_crm`
   - Créer un utilisateur : `globibat_user`
   - Mot de passe : [choisir un mot de passe fort]
   - Privilèges : Tous les privilèges

3. **Mettre à jour DATABASE_URL dans .env** :
   ```
   DATABASE_URL=mysql://globibat_user:VOTRE_MOT_DE_PASSE@localhost:3306/globibat_crm
   ```

### 3️⃣ Préparer les Fichiers pour l'Upload

```bash
# Dans le dossier Globibat_Badge_System

# 1. Créer le fichier .env avec le contenu ci-dessus
# 2. Supprimer le dossier venv (pas nécessaire sur le serveur)
# 3. Zipper tout le contenu
```

### 4️⃣ Upload sur Hostinger

**Option 1 : Via File Manager (Recommandé)**
1. Connectez-vous au panneau Hostinger
2. Allez dans **File Manager**
3. Naviguez vers `public_html`
4. Uploadez le fichier ZIP
5. Extrayez le contenu directement dans `public_html`

**Option 2 : Via FTP**
- Host : ftp.globibat.com
- Port : 21
- Uploadez tous les fichiers dans `public_html`

### 5️⃣ Configuration SSH et Installation

```bash
# Se connecter en SSH
ssh votre-user@globibat.com

# Aller dans public_html
cd public_html

# Donner les permissions d'exécution
chmod +x deploy_hostinger.sh
chmod +x index.py

# Créer l'environnement virtuel Python
python3 -m venv venv
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt

# Initialiser la base de données
python run.py init_db

# Créer l'administrateur
python run.py create_admin
# Email : admin@globibat.ch
# Mot de passe : [choisir un mot de passe fort]
```

### 6️⃣ Configuration Finale

1. **Vérifier le fichier .htaccess** (créé automatiquement par deploy_hostinger.sh)
2. **Configurer le Cron Job** pour les sauvegardes :
   ```
   0 2 * * * cd /home/votre-user/public_html && ./maintenance.sh
   ```

### 7️⃣ Test et Vérification

1. Accéder à : https://www.globibat.com
2. Vérifier HTTPS (doit rediriger automatiquement)
3. Se connecter avec admin@globibat.ch
4. Tester :
   - ✓ Dashboard
   - ✓ CRM (clients, projets)
   - ✓ Système de badge
   - ✓ Envoi d'email

## 🔧 Dépannage

### Si erreur 500 :
```bash
# Vérifier les logs
tail -f instance/logs/app.log

# Vérifier les permissions
chmod -R 755 app/
chmod -R 777 instance/
chmod -R 777 app/static/uploads/
```

### Si problème de base de données :
```bash
# Tester la connexion
python -c "from run import app; from app import db; app.app_context().push(); db.create_all(); print('DB OK')"
```

## 📱 Configuration Multi-Domaine

Comme vous avez 2 domaines (www.globibat.com et globibat.ch), configurez dans Hostinger :
1. **Domaines** → **Gérer les domaines**
2. Pointer les deux vers le même `public_html`
3. Le .htaccess forcera HTTPS pour les deux

## 🎯 SEO Post-Déploiement

1. **Google Search Console** :
   - Ajouter www.globibat.com
   - Ajouter globibat.ch
   - Soumettre sitemap : https://www.globibat.com/sitemap.xml

2. **Google My Business** :
   - Mettre à jour l'URL vers le nouveau CRM

## ✨ C'est Terminé !

Votre CRM Globibat est maintenant :
- ✅ SEO optimisé pour "construction Suisse romande"
- ✅ CRM complet avec gestion clients/projets/factures
- ✅ Système de badge employés
- ✅ Interface moderne et responsive
- ✅ Sécurisé avec HTTPS et 2FA
- ✅ Email configuré avec info@globibat.com

**Support** : Les logs sont dans `instance/logs/app.log`