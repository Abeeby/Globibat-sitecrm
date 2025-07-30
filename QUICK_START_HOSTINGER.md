# 🚀 Guide Rapide Déploiement Hostinger - Globibat CRM

## ⚡ Démarrage Rapide (15 minutes)

### 1️⃣ Préparation Locale
```bash
# Dans le dossier Globibat_Badge_System
cp hostinger_config.md .env
# Éditer .env avec vos vraies valeurs
```

### 2️⃣ Sur Hostinger - Base de Données
1. **Panneau Hostinger** → **Bases de données MySQL**
2. **Créer une base de données** :
   - Nom : `globibat_crm`
   - Utilisateur : `globibat_user`
   - Mot de passe : [noter le mot de passe]
3. **Copier les infos** dans votre `.env`

### 3️⃣ Upload des Fichiers
```bash
# Option 1 : Via FTP
# Host : ftp.votredomaine.com
# User : votre-user-ftp
# Upload tout le contenu dans public_html/

# Option 2 : Via File Manager Hostinger
# Zipper le dossier et uploader
```

### 4️⃣ Configuration SSH Hostinger
```bash
# Se connecter en SSH
ssh votre-user@votredomaine.com

# Aller dans public_html
cd public_html

# Donner les permissions
chmod +x deploy_hostinger.sh
chmod +x index.py

# Lancer le déploiement
./deploy_hostinger.sh
```

### 5️⃣ Créer l'Administrateur
```bash
python run.py create_admin
# Email : admin@globibat.ch
# Mot de passe : choisir un fort
```

## ✅ Vérification

1. **Accéder à** : https://www.globibat.ch
2. **Se connecter** avec admin@globibat.ch
3. **Vérifier** :
   - ✓ Page d'accueil (SEO optimisé)
   - ✓ Dashboard admin
   - ✓ CRM fonctionnel
   - ✓ Système de badge

## 🔧 Dépannage Rapide

### Erreur 500
```bash
# Vérifier les logs
tail -f instance/logs/app.log
# Vérifier .env
cat .env
```

### Base de données
```bash
# Tester la connexion
python -c "from run import app; app.app_context().push(); from app.models import db; db.create_all(); print('DB OK')"
```

### Permissions
```bash
chmod -R 755 app/
chmod -R 777 instance/
chmod -R 777 app/static/uploads/
```

## 📱 Configuration Email

Dans Hostinger :
1. **Email** → **Configuration Email**
2. **SMTP** : smtp.hostinger.com
3. **Port** : 587
4. **Sécurité** : STARTTLS

## 🎯 SEO Final

1. **Google Search Console** :
   - Ajouter le site
   - Soumettre sitemap.xml
   
2. **Meta Tags** déjà configurés pour :
   - Construction Suisse Romande
   - Bâtiment Genève/Vaud
   - CRM Construction

## 📞 Support

- **Logs** : `instance/logs/app.log`
- **Backup** : Automatique quotidien
- **SSL** : Auto Let's Encrypt

---

**🎉 Votre CRM Globibat est prêt !**

Top SEO + CRM Complet + Système Badge + Interface Moderne