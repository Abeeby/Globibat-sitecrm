# ✅ CHECKLIST DÉPLOIEMENT GLOBIBAT CRM

## 📋 Avant l'Upload

- [ ] **Créer le fichier .env**
  ```powershell
  .\create_env_file.ps1
  ```

- [ ] **Vérifier que .gitignore protège .env**
  - Le fichier .env ne doit JAMAIS être uploadé sur Git

- [ ] **Supprimer le dossier venv** (sera recréé sur le serveur)

- [ ] **Vérifier les fichiers critiques** :
  - ✓ `DEPLOIEMENT_HOSTINGER_FINAL.md` (guide complet)
  - ✓ `deploy_hostinger.sh` (script de déploiement)
  - ✓ `requirements.txt` (dépendances)
  - ✓ `.env` (configuration)

## 🌐 Sur Hostinger

### Base de données MySQL
- [ ] Créer la base `globibat_crm`
- [ ] Créer l'utilisateur `globibat_user`
- [ ] Noter le mot de passe
- [ ] Mettre à jour DATABASE_URL dans .env

### Upload des fichiers
- [ ] Zipper le dossier Globibat_Badge_System
- [ ] Uploader dans public_html
- [ ] Extraire le contenu

### Configuration SSH
- [ ] Se connecter en SSH
- [ ] Exécuter `deploy_hostinger.sh`
- [ ] Créer l'administrateur

### Configuration finale
- [ ] Vérifier le SSL (Let's Encrypt)
- [ ] Configurer le cron job pour les backups
- [ ] Tester les deux domaines

## 🧪 Tests Post-Déploiement

### Fonctionnalités
- [ ] Page d'accueil (SEO)
- [ ] Connexion admin
- [ ] Dashboard
- [ ] CRM - Créer un client
- [ ] CRM - Créer un projet
- [ ] Badge - Pointer
- [ ] Email - Envoyer un test

### SEO
- [ ] Vérifier robots.txt
- [ ] Vérifier sitemap.xml
- [ ] Soumettre à Google Search Console

### Sécurité
- [ ] HTTPS fonctionne
- [ ] Redirection HTTP → HTTPS
- [ ] 2FA activé pour admin
- [ ] Headers de sécurité

## 📱 Informations de Connexion

**Admin par défaut** :
- Email : admin@globibat.ch
- Mot de passe : (à définir lors de la création)

**URLs** :
- Principal : https://www.globibat.com
- Alternatif : https://globibat.ch

**Email** :
- SMTP : smtp.hostinger.com:465 (SSL)
- Email : info@globibat.com

## 🆘 En cas de problème

1. **Logs** : `tail -f instance/logs/app.log`
2. **Permissions** : `chmod -R 777 instance/`
3. **Base de données** : Vérifier DATABASE_URL
4. **Support** : Consulter DEPLOIEMENT_HOSTINGER_FINAL.md

---

**🎯 Objectif** : CRM fonctionnel + Top SEO Suisse Romande Construction