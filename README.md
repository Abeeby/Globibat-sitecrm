# Globibat CRM - Système de Gestion d'Entreprise de Construction

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8+-green.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/flask-2.0+-red.svg)](https://flask.palletsprojects.com/)

## 🏗️ Description

**Globibat CRM** est un système de gestion complet pour entreprises de construction, développé spécifiquement pour le marché Suisse romande. Cette solution tout-en-un intègre :

- 🏢 **CRM Complet** : Gestion clients, projets, devis, factures
- 👷 **Gestion RH** : Système de badge, paie, congés
- 💰 **Module Finance** : Comptabilité, paiements, dépenses
- 📊 **Tableaux de Bord** : Statistiques et rapports en temps réel
- 🔒 **Sécurité** : Authentification 2FA, rôles et permissions
- 📱 **API REST** : Pour intégration mobile et externes

## 🚀 Fonctionnalités Principales

### Module CRM
- Gestion complète des clients et contacts
- Suivi des projets de construction avec phases et tâches
- Création et suivi des devis
- Facturation automatisée avec numérotation
- Génération PDF (devis, factures)

### Module RH
- Système de badge 4 points (arrivée matin/après-midi, départ matin/après-midi)
- Gestion des employés et équipes
- Suivi des congés et absences
- Génération automatique des fiches de paie
- Calcul des charges sociales suisses

### Module Finance
- Suivi des paiements clients
- Gestion des dépenses
- Rapports financiers
- Export Excel

### Module Inventaire
- Gestion des matériaux
- Suivi des équipements
- Gestion des fournisseurs
- Bons de commande

## 📋 Prérequis

- Python 3.8+
- MySQL 5.7+ ou PostgreSQL 12+
- Redis (optionnel, pour Celery)

## 🛠️ Installation

### 1. Cloner le repository

```bash
git clone https://github.com/Abeeby/Globibat-sitecrm.git
cd Globibat-sitecrm
```

### 2. Créer l'environnement virtuel

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
.\venv\Scripts\activate  # Windows
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 4. Configuration

Créer un fichier `.env` à la racine :

```env
SECRET_KEY=votre-cle-secrete
DATABASE_URL=mysql://user:pass@localhost/globibat_crm
MAIL_SERVER=smtp.example.com
MAIL_USERNAME=your-email@example.com
MAIL_PASSWORD=your-password
```

### 5. Initialiser la base de données

```bash
python run.py init_db
python run.py create_admin
```

### 6. Lancer l'application

```bash
python run.py
```

L'application sera accessible sur http://localhost:5000

## 🌐 Déploiement

### Hostinger VPS

Consultez le guide complet : [DEPLOIEMENT_VPS_HOSTINGER.md](DEPLOIEMENT_VPS_HOSTINGER.md)

### Docker

```bash
docker build -t globibat-crm .
docker run -p 5000:5000 --env-file .env globibat-crm
```

## 📱 API Documentation

L'API REST est disponible sur `/api/v1/`. Documentation complète :

- `GET /api/v1/projects` - Liste des projets
- `POST /api/v1/clients` - Créer un client
- `GET /api/v1/dashboard/stats` - Statistiques

## 🧪 Tests

```bash
pytest tests/
```

## 📄 License

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

## 👥 Contribution

Les contributions sont les bienvenues ! Merci de :

1. Fork le projet
2. Créer une branche (`git checkout -b feature/AmazingFeature`)
3. Commit vos changements (`git commit -m 'Add AmazingFeature'`)
4. Push sur la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

## 📞 Support

- 📧 Email : info@globibat.com
- 📱 Tél : +41 21 505 00 62
- 🌐 Site : https://www.globibat.com

## 🏆 SEO & Performance

- Page d'accueil optimisée pour "entreprise construction Genève"
- Score PageSpeed : 95+
- Mobile-friendly
- Schema.org intégré

---

**Développé avec ❤️ pour Globibat SA - Leader de la construction en Suisse romande**