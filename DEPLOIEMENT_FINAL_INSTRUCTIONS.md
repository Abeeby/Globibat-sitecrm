# 🚀 GUIDE DE DÉPLOIEMENT FINAL - GLOBIBAT CRM

## ✅ CE QUI A ÉTÉ FAIT

### 1. Système Complet Développé
- ✅ Système de badgage avancé (QR, PIN, Photo, Géolocalisation)
- ✅ Module de paie avec conformité suisse
- ✅ Gestion des dépenses avec workflow d'approbation
- ✅ Gestion des congés intégrée
- ✅ Tableaux de bord temps réel
- ✅ Analytics et statistiques avancés
- ✅ Système de permissions RBAC
- ✅ Audit trail complet
- ✅ Notifications automatiques
- ✅ Documentation complète

### 2. Fichiers Préparés
- ✅ `.env` créé (à mettre à jour avec vos credentials)
- ✅ `requirements.txt` mis à jour avec toutes les dépendances
- ✅ Scripts de déploiement créés
- ✅ Scripts d'initialisation prêts
- ✅ Code poussé sur GitHub

## 📋 ÉTAPES DE DÉPLOIEMENT

### Étape 1: Créer la Base de Données MySQL sur Hostinger

1. Connectez-vous au panneau Hostinger
2. Allez dans **Bases de données** → **MySQL**
3. Créez une nouvelle base de données:
   - Nom: `globibat_crm`
   - Créez un utilisateur: `globibat_user`
   - Générez un mot de passe fort
   - Accordez tous les privilèges

### Étape 2: Mettre à jour le fichier .env

Ouvrez le fichier `.env` et remplacez:
```
DATABASE_URL=mysql://globibat_user:VOTRE_MOT_DE_PASSE@localhost:3306/globibat_crm
```
Par vos vraies credentials MySQL.

### Étape 3: Préparer les fichiers pour l'upload

```bash
# Dans le dossier Globibat_Badge_System
# Supprimer le dossier venv (pas nécessaire sur le serveur)
rm -rf venv/

# Créer une archive ZIP sans le dossier venv
# (ou utilisez votre outil de compression préféré)
```

### Étape 4: Upload sur Hostinger

**Via File Manager (Recommandé):**
1. Connectez-vous au panneau Hostinger
2. Ouvrez **File Manager**
3. Naviguez vers `public_html`
4. Uploadez tous les fichiers du projet
5. Assurez-vous que la structure est correcte

**Via FTP:**
- Host: ftp.globibat.com
- Username: [votre username]
- Password: [votre password]
- Port: 21

### Étape 5: Configuration SSH et Installation

```bash
# Se connecter en SSH
ssh votre-username@globibat.com

# Aller dans public_html
cd public_html

# Donner les permissions d'exécution
chmod +x deploy_hostinger_complete.sh
chmod +x init_database.py

# Créer l'environnement virtuel Python
python3 -m venv venv
source venv/bin/activate

# Installer les dépendances
pip install --upgrade pip
pip install -r requirements.txt

# Initialiser la base de données
python init_database.py

# Créer le fichier index.py pour Hostinger
cat > index.py << 'EOF'
#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os

# Ajouter le chemin de l'environnement virtuel
activate_this = os.path.join(os.path.dirname(__file__), 'venv/bin/activate_this.py')
if os.path.exists(activate_this):
    exec(open(activate_this).read(), {'__file__': activate_this})

# Ajouter le chemin du projet
sys.path.insert(0, os.path.dirname(__file__))

# Importer et lancer l'application
from run import app as application

if __name__ == '__main__':
    application.run()
EOF

chmod +x index.py

# Créer le fichier .htaccess
cat > .htaccess << 'EOF'
RewriteEngine On
RewriteCond %{HTTPS} off
RewriteRule ^(.*)$ https://%{HTTP_HOST}%{REQUEST_URI} [L,R=301]

# Python application
RewriteCond %{REQUEST_FILENAME} !-f
RewriteCond %{REQUEST_FILENAME} !-d
RewriteRule ^(.*)$ /index.py/$1 [L]

# Sécurité
Options -Indexes
<FilesMatch "\.(env|db|sqlite|log)$">
    Order allow,deny
    Deny from all
</FilesMatch>
EOF

# Configurer les permissions
chmod -R 755 app/
chmod -R 777 instance/
chmod -R 777 app/static/uploads/
```

### Étape 6: Vérification

1. Accédez à https://www.globibat.com
2. Vous devriez voir la page d'accueil
3. Connectez-vous avec:
   - Email: `admin@globibat.ch`
   - Mot de passe: `Admin2024!`

### Étape 7: Configuration Post-Déploiement

1. **Changez immédiatement le mot de passe admin**
2. Créez les employés
3. Configurez les politiques de dépenses
4. Configurez les régulations de temps de travail
5. Testez chaque module

## 🔧 DÉPANNAGE

### Erreur 500
```bash
# Vérifier les logs
tail -f instance/logs/app.log

# Vérifier les permissions
ls -la app/static/uploads/
```

### Problème de connexion à la DB
```bash
# Tester la connexion
python -c "from run import app; from app import db; app.app_context().push(); db.create_all(); print('DB OK')"
```

### Module non trouvé
```bash
# Réinstaller les dépendances
pip install -r requirements.txt --force-reinstall
```

## 📱 ACCÈS ET CREDENTIALS

- **URL Production**: https://www.globibat.com
- **URL Alternative**: https://globibat.ch
- **Admin Email**: admin@globibat.ch
- **Admin Password**: Admin2024! (à changer immédiatement)
- **Email SMTP**: info@globibat.com configuré

## 🎯 CHECKLIST FINALE

- [ ] Base de données créée et configurée
- [ ] Fichiers uploadés sur Hostinger
- [ ] Environnement virtuel créé
- [ ] Dépendances installées
- [ ] Base de données initialisée
- [ ] Site accessible en HTTPS
- [ ] Login admin fonctionnel
- [ ] Mot de passe admin changé
- [ ] Tous les modules testés
- [ ] Employés créés
- [ ] Sauvegardes configurées

## 📞 SUPPORT

En cas de problème:
1. Consultez les logs dans `instance/logs/app.log`
2. Vérifiez la documentation dans `DOCUMENTATION_COMPLETE.md`
3. Consultez le guide de démarrage rapide `GUIDE_DEMARRAGE_RAPIDE.md`

## 🎉 FÉLICITATIONS!

Votre système CRM/Badge Globibat est maintenant prêt pour la production!

**Fonctionnalités disponibles:**
- Badgage des employés avec multiple méthodes
- Gestion complète de la paie
- Workflow de dépenses
- Gestion des congés
- Tableaux de bord en temps réel
- Conformité totale aux lois suisses

Bonne utilisation! 🚀