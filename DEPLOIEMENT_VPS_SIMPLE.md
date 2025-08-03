# 🚀 DÉPLOIEMENT RAPIDE SUR VOTRE VPS

Puisque vous avez déjà un VPS configuré avec votre `.env` et base de données, voici les étapes simplifiées :

## 📋 ÉTAPES RAPIDES

### 1. Upload des fichiers sur le VPS

```bash
# Depuis votre machine locale (PowerShell)
# Créer une archive sans le dossier venv
cd Globibat_Badge_System
tar -czf globibat_update.tar.gz --exclude='venv' --exclude='.git' --exclude='*.pyc' --exclude='__pycache__' .

# Uploader sur le VPS
scp globibat_update.tar.gz root@VOTRE_IP_VPS:/tmp/
```

### 2. Connexion au VPS et déploiement

```bash
# Se connecter au VPS
ssh root@VOTRE_IP_VPS

# Aller dans le dossier temporaire
cd /tmp

# Extraire les fichiers
tar -xzf globibat_update.tar.gz

# Copier le script de déploiement et l'exécuter
chmod +x deploy_vps_complete.sh
./deploy_vps_complete.sh
```

### 3. Vérifications importantes

Après le déploiement, vérifiez que votre fichier `.env` existant contient ces nouvelles variables :

```env
# Nouvelles configurations pour les modules avancés
ENABLE_2FA=True
SESSION_TIMEOUT=1440
MAX_LOGIN_ATTEMPTS=5
PASSWORD_MIN_LENGTH=8

# Activation des modules
ENABLE_BADGE_SYSTEM=True
ENABLE_PAYROLL=True
ENABLE_EXPENSE_MANAGEMENT=True
ENABLE_LEAVE_MANAGEMENT=True
ENABLE_ANALYTICS=True
ENABLE_COMPLIANCE=True
```

## 🔧 COMMANDES UTILES

### Redémarrer l'application
```bash
systemctl restart globibat
systemctl status globibat
```

### Voir les logs
```bash
# Logs de l'application
tail -f /var/www/globibat/instance/logs/app.log

# Logs Nginx
tail -f /var/log/nginx/globibat_error.log
```

### Tester la base de données
```bash
cd /var/www/globibat
source venv/bin/activate
python -c "from run import app; from app import db; app.app_context().push(); db.create_all(); print('DB OK')"
```

## ✅ CHECKLIST POST-DÉPLOIEMENT

- [ ] Site accessible (https://www.globibat.com)
- [ ] Login admin fonctionnel
- [ ] Module de badge testé
- [ ] Module de paie testé
- [ ] Module de dépenses testé
- [ ] Module de congés testé
- [ ] Tableaux de bord fonctionnels
- [ ] Emails de test envoyés

## 🆘 EN CAS DE PROBLÈME

### Si erreur 502 Bad Gateway
```bash
# Vérifier que le service tourne
systemctl status globibat

# Redémarrer si nécessaire
systemctl restart globibat
systemctl restart nginx
```

### Si erreur de permissions
```bash
cd /var/www/globibat
chown -R www-data:www-data .
chmod -R 755 .
chmod -R 777 instance/
chmod -R 777 app/static/uploads/
```

### Si modules non trouvés
```bash
cd /var/www/globibat
source venv/bin/activate
pip install -r requirements.txt --force-reinstall
```

## 🎉 C'EST FAIT !

Votre système CRM/Badge avancé est maintenant déployé avec toutes les nouvelles fonctionnalités !

**Connectez-vous avec :**
- Email : admin@globibat.ch
- Mot de passe : Admin2024! (à changer)