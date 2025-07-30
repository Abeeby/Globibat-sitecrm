# 📊 Guide Création Base de Données MySQL sur Hostinger

## Option 1 : Via le Panneau de Contrôle Hostinger (Hébergement Web)

### Étapes :

1. **Connectez-vous à votre compte Hostinger**
   - Allez sur https://www.hostinger.fr
   - Connectez-vous avec vos identifiants

2. **Accédez aux Bases de Données**
   - Dans le panneau de contrôle, cherchez "Bases de données"
   - Cliquez sur "Bases de données MySQL"

3. **Créer une Nouvelle Base de Données**
   - Cliquez sur "Créer une nouvelle base de données MySQL"
   - **Nom de la base** : `globibat_crm`
   - Cliquez sur "Créer"

4. **Créer un Utilisateur MySQL**
   - Dans la même page, section "Utilisateurs MySQL"
   - Cliquez sur "Créer un nouvel utilisateur"
   - **Nom d'utilisateur** : `globibat_user`
   - **Mot de passe** : [Générez un mot de passe fort]
   - Notez bien ces informations !

5. **Attribuer les Privilèges**
   - Dans "Ajouter un utilisateur à la base de données"
   - Sélectionnez : `globibat_user`
   - Base de données : `globibat_crm`
   - Cliquez sur "Ajouter"
   - Cochez "TOUS LES PRIVILÈGES"
   - Cliquez sur "Apporter des modifications"

6. **Récupérer les Informations de Connexion**
   - Host : `localhost` (ou l'IP fournie par Hostinger)
   - Database : `globibat_crm`
   - Username : `globibat_user`
   - Password : [votre mot de passe]

## Option 2 : Via SSH sur VPS Hostinger

### Si vous avez un VPS, voici les commandes :

```bash
# 1. Se connecter au VPS
ssh root@votre-ip-vps

# 2. Se connecter à MySQL
mysql -u root -p

# 3. Créer la base de données
CREATE DATABASE globibat_crm CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# 4. Créer l'utilisateur
CREATE USER 'globibat_user'@'localhost' IDENTIFIED BY 'VotreMotDePasseFort';

# 5. Donner tous les privilèges
GRANT ALL PRIVILEGES ON globibat_crm.* TO 'globibat_user'@'localhost';

# 6. Appliquer les changements
FLUSH PRIVILEGES;

# 7. Quitter MySQL
EXIT;
```

### Installation de MySQL sur VPS (si pas déjà installé) :

```bash
# Pour Ubuntu/Debian
apt update
apt install mysql-server -y

# Sécuriser MySQL
mysql_secure_installation

# Démarrer MySQL
systemctl start mysql
systemctl enable mysql
```

## 📝 Mettre à Jour le Fichier .env

Une fois la base de données créée, mettez à jour votre fichier `.env` :

### Pour Hébergement Web :
```env
DATABASE_URL=mysql://globibat_user:VotreMotDePasse@localhost:3306/globibat_crm
```

### Pour VPS :
```env
DATABASE_URL=mysql://globibat_user:VotreMotDePasse@127.0.0.1:3306/globibat_crm
```

## 🧪 Tester la Connexion

Pour vérifier que tout fonctionne :

```bash
# Sur votre serveur Hostinger
cd public_html
source venv/bin/activate
python -c "
from run import app
from app import db
with app.app_context():
    db.create_all()
    print('✅ Connexion DB réussie !')
"
```

## ⚠️ Notes Importantes

1. **Mot de passe fort** : Utilisez au moins 12 caractères avec majuscules, minuscules, chiffres et symboles
2. **Sauvegarder** : Notez toutes les informations dans un endroit sûr
3. **Préfixe** : Certains hébergements ajoutent un préfixe automatique (ex: `user_globibat_crm`)

## 🆘 En Cas de Problème

### Erreur "Access denied" :
- Vérifiez le nom d'utilisateur et mot de passe
- Vérifiez que l'utilisateur a les privilèges

### Erreur "Unknown database" :
- Vérifiez le nom de la base de données
- Vérifiez les préfixes automatiques

### Sur VPS - Port MySQL fermé :
```bash
# Ouvrir le port MySQL
ufw allow 3306/tcp
```

---

**Une fois la base de données créée, retournez au guide `DEPLOIEMENT_HOSTINGER_FINAL.md` pour continuer !**