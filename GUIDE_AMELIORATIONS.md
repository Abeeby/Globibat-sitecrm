# 🚀 Guide de déploiement des améliorations Globibat

## 📍 Étape 1 : Connexion au VPS Hostinger

```bash
ssh root@[VOTRE_IP_VPS]
cd /var/www/globibat
```

## 📍 Étape 2 : Arrêt temporaire de l'application

```bash
sudo supervisorctl stop globibat
```

## 📍 Étape 3 : Mise à jour des fichiers

### Option A : Copier les fichiers modifiés via FileZilla
1. Connectez-vous via FileZilla
2. Copiez les fichiers suivants vers `/var/www/globibat/` :
   - `app.py`
   - `config.py`
   - Tout le dossier `templates/`

### Option B : Utiliser Git (si configuré)
```bash
git pull origin main
```

## 📍 Étape 4 : Configuration du domaine globibat.com

### 4.1 - Dans votre panel Hostinger :
1. Allez dans "Domaines"
2. Pointez globibat.com vers l'IP de votre VPS
3. Ajoutez les enregistrements DNS :
   - Type A : @ → [IP_VPS]
   - Type A : www → [IP_VPS]

### 4.2 - Configuration Nginx sur le VPS :
```bash
# Copier la configuration
sudo cp nginx_config.conf /etc/nginx/sites-available/globibat

# Créer le lien symbolique
sudo ln -s /etc/nginx/sites-available/globibat /etc/nginx/sites-enabled/

# Supprimer la configuration par défaut si elle existe
sudo rm /etc/nginx/sites-enabled/default

# Tester la configuration
sudo nginx -t

# Recharger Nginx
sudo systemctl reload nginx
```

## 📍 Étape 5 : Installation du certificat SSL (HTTPS)

```bash
# Installer Certbot
sudo apt-get update
sudo apt-get install certbot python3-certbot-nginx

# Obtenir le certificat SSL
sudo certbot --nginx -d globibat.com -d www.globibat.com

# Suivez les instructions et choisissez l'option 2 (redirect)
```

## 📍 Étape 6 : Mise à jour de la configuration après SSL

Modifiez `/var/www/globibat/config.py` :
```bash
sudo nano /var/www/globibat/config.py
```

Changez :
```python
SESSION_COOKIE_SECURE = True  # Réactiver maintenant qu'on a HTTPS
```

## 📍 Étape 7 : Redémarrage de l'application

```bash
# Redémarrer l'application
sudo supervisorctl start globibat

# Vérifier le statut
sudo supervisorctl status globibat

# Voir les logs si problème
sudo tail -f /var/log/globibat.log
```

## 📍 Étape 8 : Créer le premier employé test

1. Allez sur https://globibat.com/admin-globibat
2. Connectez-vous avec : Globibat / Miser1597532684$
3. Allez dans "Employés" → "Ajouter"
4. Créez un employé test :
   - Matricule : TEST001
   - Nom : Test
   - Prénom : Employé

## 📍 Étape 9 : Tester le portail employé

1. Allez sur https://globibat.com/employe
2. Connectez-vous avec le matricule TEST001
3. Vérifiez que le tableau de bord s'affiche

## 🔧 Commandes utiles

### Voir les logs en temps réel :
```bash
sudo tail -f /var/log/globibat.log
```

### Redémarrer l'application :
```bash
sudo supervisorctl restart globibat
```

### Vérifier Nginx :
```bash
sudo systemctl status nginx
```

## 🚨 En cas de problème

### L'application ne démarre pas :
```bash
# Vérifier les erreurs Python
cd /var/www/globibat
source venv/bin/activate
python app.py
```

### Erreur 502 Bad Gateway :
```bash
# Vérifier que Gunicorn tourne
sudo supervisorctl status globibat
# Vérifier les logs
sudo tail -50 /var/log/globibat.log
```

### Le domaine ne fonctionne pas :
1. Vérifiez que les DNS sont propagés (peut prendre jusqu'à 48h)
2. Testez avec : `ping globibat.com`
3. Vérifiez Nginx : `sudo nginx -t`

## ✅ URLs importantes après déploiement

- **Page d'accueil** : https://globibat.com
- **Badgeage rapide** : https://globibat.com/badge
- **Portail employé** : https://globibat.com/employe
- **Admin (caché)** : https://globibat.com/admin-globibat

## 📊 Prochaines améliorations suggérées

1. **Notifications email** pour les retards
2. **Application mobile** PWA
3. **Graphiques** de présence
4. **Export PDF** des fiches de paie
5. **API REST** pour intégrations futures 