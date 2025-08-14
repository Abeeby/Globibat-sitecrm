# 🚀 GUIDE DE DÉPLOIEMENT VPS - GLOBIBAT CRM

## ✅ Configuration Sécurisée

Les identifiants admin sont maintenant **sécurisés** :
- **Email**: info@globibat.com
- **Mot de passe**: Stocké de manière sécurisée dans `.env`
- **⚠️ Important**: Les identifiants ne sont PAS visibles dans le code

## 📋 Prérequis VPS

- VPS avec Ubuntu 20.04 ou plus récent
- Accès SSH root
- Domaine configuré (www.globibat.com)

## 🔧 Déploiement Rapide

### 1. Configurer l'IP du VPS

Éditez le fichier `deploy_vps_secure.sh` et remplacez :
```bash
VPS_HOST="your_vps_ip_here"  # Remplacez par l'IP de votre VPS
```

### 2. Lancer le Déploiement

```bash
chmod +x deploy_vps_secure.sh
./deploy_vps_secure.sh
```

Le script va automatiquement :
- ✅ Uploader les fichiers de manière sécurisée
- ✅ Configurer l'environnement Python
- ✅ Initialiser la base de données avec les identifiants sécurisés
- ✅ Configurer Nginx et Supervisor
- ✅ Démarrer l'application

### 3. Configuration SSL (HTTPS)

Une fois l'application déployée, activez HTTPS :

```bash
# Se connecter au VPS
ssh root@[IP_VPS]

# Installer Certbot
apt-get install certbot python3-certbot-nginx -y

# Obtenir le certificat SSL
certbot --nginx -d www.globibat.com -d globibat.com

# Redémarrer Nginx
systemctl restart nginx
```

## 🔐 Sécurité

### Fichiers Sensibles
- `.env` : Contient les identifiants (exclu de Git)
- `instance/globibat.db` : Base de données (créée automatiquement)

### Bonnes Pratiques
1. **Ne jamais** commiter le fichier `.env` sur Git
2. **Changer** régulièrement les mots de passe
3. **Sauvegarder** régulièrement la base de données
4. **Activer** le firewall sur le VPS

## 📊 Vérification

### Test Local
```bash
python3 check_admin_config.py
```

### Test après Déploiement
1. Accéder à : https://www.globibat.com
2. Se connecter avec : info@globibat.com
3. Vérifier toutes les fonctionnalités

## 🛠️ Commandes Utiles

### Sur le VPS

```bash
# Voir les logs
tail -f /var/www/globibat/instance/logs/gunicorn.log

# Redémarrer l'application
supervisorctl restart globibat

# Vérifier le statut
supervisorctl status globibat

# Mettre à jour l'application
cd /var/www/globibat
git pull
supervisorctl restart globibat
```

## 📝 Résolution de Problèmes

### L'application ne démarre pas
```bash
# Vérifier les logs
journalctl -u supervisor -n 50
supervisorctl tail -f globibat
```

### Erreur 502 Bad Gateway
```bash
# Redémarrer les services
systemctl restart nginx
supervisorctl restart globibat
```

### Problème de permissions
```bash
chown -R www-data:www-data /var/www/globibat
chmod -R 755 /var/www/globibat
```

## 📞 Support

Pour toute question ou problème :
- Email : info@globibat.com
- Documentation : [README.md](README.md)

---

**✨ L'application est prête pour le déploiement !**

Les identifiants admin sont sécurisés et ne sont pas visibles dans le code.