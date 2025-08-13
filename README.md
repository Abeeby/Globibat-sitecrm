# 🏗️ Globibat CRM - Système de Gestion Intégré

## 📋 Description

**Globibat CRM** est une solution complète de gestion d'entreprise pour le secteur de la construction et de la rénovation. Le système intègre plusieurs modules essentiels :

- 🌐 **Site Internet Public** - Vitrine de l'entreprise
- 💼 **CRM Complet** - Gestion clients, projets et devis
- 👤 **Espace Employé** - Portail personnel pour chaque employé
- 🎫 **Système de Badge** - Pointage et suivi des présences
- 📊 **Tableaux de Bord** - Analytics et rapports en temps réel
- 💰 **Gestion Financière** - Factures, paiements et comptabilité
- 📱 **API REST** - Intégration avec d'autres systèmes

## 🚀 Installation Rapide

### Prérequis

- Python 3.8 ou supérieur
- pip (gestionnaire de paquets Python)
- Git (optionnel)

### Windows

1. **Cloner le projet** (ou télécharger le ZIP)
```bash
git clone https://github.com/votre-repo/globibat-crm.git
cd globibat-crm
```

2. **Lancer l'application**
```bash
LANCER_CRM_LOCAL.bat
```

Le script s'occupe automatiquement de :
- Créer l'environnement virtuel Python
- Installer toutes les dépendances
- Initialiser la base de données
- Lancer le serveur

### Linux/Mac

1. **Cloner le projet**
```bash
git clone https://github.com/votre-repo/globibat-crm.git
cd globibat-crm
```

2. **Créer l'environnement virtuel**
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
```

3. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

4. **Configurer l'environnement**
```bash
cp .env.example .env
# Éditer .env avec vos paramètres
```

5. **Initialiser la base de données**
```bash
python init_database.py
```

6. **Lancer l'application**
```bash
python app.py
```

## 🔐 Accès au Système

### Points d'Accès

| Module | URL | Description |
|--------|-----|-------------|
| Site Public | http://localhost:5000 | Page d'accueil publique |
| Admin CRM | http://localhost:5000/admin | Panneau d'administration |
| Espace Employé | http://localhost:5000/employee | Portail employé |
| Système Badge | http://localhost:5000/badge | Interface de pointage |
| API REST | http://localhost:5000/api/v1/ | Documentation API |

### Comptes de Test

**Administrateur CRM**
- Email : `info@globibat.com`
- Mot de passe : (défini dans init_database.py)

**Employés de Test**
- Matricules : `EMP001` à `EMP005`
- Mot de passe : `Employee2024!`

## 📁 Structure du Projet

```
globibat-crm/
│
├── app/                    # Application principale
│   ├── __init__.py        # Initialisation Flask
│   ├── models/            # Modèles de données
│   │   ├── user.py       # Gestion utilisateurs
│   │   ├── employee.py   # Gestion employés
│   │   ├── client.py     # Gestion clients
│   │   ├── project.py    # Gestion projets
│   │   └── ...
│   ├── views/             # Vues et routes
│   │   ├── auth.py       # Authentification
│   │   ├── crm.py        # Routes CRM
│   │   ├── badge.py      # Système de badge
│   │   └── ...
│   ├── templates/         # Templates HTML
│   ├── static/           # Fichiers statiques
│   └── utils/            # Utilitaires
│
├── instance/             # Données d'instance
│   └── globibat.db      # Base de données SQLite
│
├── logs/                 # Fichiers de logs
├── venv/                 # Environnement virtuel
│
├── app.py               # Point d'entrée
├── config.py            # Configuration
├── init_database.py     # Initialisation DB
├── requirements.txt     # Dépendances Python
├── .env                 # Variables d'environnement (non versionné)
├── .env.example         # Exemple de configuration
├── .gitignore          # Fichiers ignorés par Git
└── README.md           # Ce fichier
```

## 🛠️ Fonctionnalités Principales

### CRM
- ✅ Gestion complète des clients
- ✅ Suivi des projets et chantiers
- ✅ Création de devis et factures
- ✅ Gestion des stocks et matériaux
- ✅ Planning et calendrier

### Système de Badge
- ✅ Pointage par matricule
- ✅ 4 moments de badge par jour
- ✅ Calcul automatique des heures
- ✅ Détection des retards
- ✅ Notifications automatiques

### Espace Employé
- ✅ Consultation des pointages
- ✅ Demandes de congés
- ✅ Notes de frais
- ✅ Documents personnels
- ✅ Fiches de paie

### Rapports et Analytics
- ✅ Tableaux de bord temps réel
- ✅ Rapports Excel exportables
- ✅ Graphiques interactifs
- ✅ Statistiques de présence
- ✅ Analyse de rentabilité

## 🔧 Configuration

### Variables d'Environnement

Copier `.env.example` vers `.env` et configurer :

```env
# Flask
FLASK_ENV=development
FLASK_DEBUG=False

# Sécurité
SECRET_KEY=votre-clé-secrète

# Base de données
DATABASE_URL=sqlite:///instance/globibat.db

# Email (pour les notifications)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=votre-email@gmail.com
MAIL_PASSWORD=votre-mot-de-passe
```

### Configuration Email

Pour activer les notifications par email :

1. Activer l'accès aux applications moins sécurisées (Gmail)
2. Ou utiliser un mot de passe d'application
3. Configurer les variables MAIL_* dans .env

## 📊 API REST

L'API REST permet l'intégration avec d'autres systèmes :

### Endpoints Principaux

- `GET /api/v1/employees` - Liste des employés
- `GET /api/v1/attendance` - Données de présence
- `POST /api/v1/badge` - Enregistrer un pointage
- `GET /api/v1/projects` - Liste des projets
- `GET /api/v1/clients` - Liste des clients

### Authentification

L'API utilise des tokens JWT pour l'authentification :

```bash
curl -X POST http://localhost:5000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"info@globibat.com","password":"***"}'
```

## 🚀 Déploiement

### Production

Pour déployer en production :

1. Configurer les variables d'environnement de production
2. Utiliser une base de données PostgreSQL ou MySQL
3. Configurer un serveur web (Nginx/Apache)
4. Utiliser Gunicorn ou uWSGI comme serveur WSGI
5. Activer HTTPS avec certificat SSL

### Docker

Un Dockerfile est disponible pour containeriser l'application :

```bash
docker build -t globibat-crm .
docker run -p 5000:5000 globibat-crm
```

## 🤝 Contribution

Les contributions sont les bienvenues ! Pour contribuer :

1. Fork le projet
2. Créer une branche (`git checkout -b feature/AmazingFeature`)
3. Commit les changements (`git commit -m 'Add AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

## 📝 Licence

Ce projet est sous licence propriétaire. Tous droits réservés à Globibat SA.

## 📞 Support

Pour toute question ou assistance :

- 📧 Email : support@globibat.ch
- 📱 Téléphone : +41 79 123 45 67
- 🌐 Site : https://www.globibat.ch

## 🏆 Équipe

Développé avec ❤️ par l'équipe Globibat

---

© 2024 Globibat SA - Tous droits réservés