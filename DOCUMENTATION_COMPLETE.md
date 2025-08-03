# 📚 Documentation Complète - Globibat CRM & Système de Badgage

## 🎯 Vue d'Ensemble

Le système Globibat CRM est une solution complète de gestion d'entreprise intégrant :
- **Système de badgage avancé** avec QR codes, PIN et géolocalisation
- **Gestion RH complète** avec paie automatisée et conformité suisse
- **Gestion des dépenses** avec workflow d'approbation multi-niveaux
- **Tableaux de bord temps réel** et analyses avancées
- **Conformité légale suisse** avec audit automatique

## 🚀 Fonctionnalités Principales

### 1. 🎫 Système de Badgage Avancé

#### Méthodes d'authentification
- **Badge physique** : Scan de carte magnétique
- **QR Code** : Code unique par employé
- **Code PIN** : Code à 6 chiffres sécurisé
- **Photo** : Capture anti-fraude (prêt pour biométrie future)

#### Caractéristiques
- Géolocalisation des pointages
- Photo optionnelle à chaque pointage
- 4 pointages par jour (arrivée/départ matin et après-midi)
- Calcul automatique des heures et heures supplémentaires
- Détection automatique des retards

### 2. 📊 Tableaux de Bord et Rapports

#### Dashboard Principal (`/dashboard`)
- Vue temps réel des présences
- KPIs : présents, heures travaillées, coûts du jour
- Graphiques interactifs (Chart.js)
- Alertes de conformité

#### Rapports Disponibles
- **Feuilles de temps** : PDF/Excel avec signatures
- **Rapports de présence** : Filtres par période, département, employé
- **Analyses de productivité** : Heures facturables vs non-facturables
- **Rapports financiers** : Coûts, marges, rentabilité par projet

### 3. 💰 Module de Paie

#### Calcul Automatique
- Salaires horaires ou mensuels
- Heures supplémentaires à 125%
- Déductions sociales suisses :
  - AVS/AI/APG : 5.25%
  - AC : 1.1%
  - LPP : 7.5%
  - LAA : 0.81%
  - Impôt à la source : Variable

#### Workflow
1. Calcul mensuel automatique
2. Validation par RH/Finance
3. Génération des fiches de paie PDF
4. Distribution aux employés
5. Intégration comptable

### 4. 💳 Gestion des Dépenses

#### Catégories
- Transport
- Repas
- Hébergement
- Fournitures bureau
- Outils et équipement
- Formation
- Frais de représentation
- Communication

#### Workflow d'Approbation
1. **Soumission** : Photo/scan du reçu
2. **Approbation Manager** : Si > 50 CHF
3. **Approbation Finance** : Si > 500 CHF ou violation de politique
4. **Remboursement** : Avec la paie mensuelle

#### Politiques Automatiques
- Limites journalières/mensuelles par catégorie
- Seuils d'approbation
- Détection des violations
- Rapports de conformité

### 5. 🏖️ Gestion des Absences

#### Types de Congés
- Congés payés (min. 20 jours/an)
- Maladie
- Maternité (14 semaines)
- Paternité (10 jours)
- Personnel
- Formation
- Service militaire

#### Fonctionnalités
- Demande en ligne avec justificatifs
- Workflow d'approbation manager
- Calendrier des absences par équipe
- Calcul automatique des soldes
- Intégration avec la paie

### 6. 📈 Statistiques et Analyses

#### Métriques RH
- Taux de présence/absentéisme
- Heures supplémentaires par période
- Turnover et évolution des effectifs
- Top performers
- Score de satisfaction

#### Analyses Financières
- Coûts salariaux par département
- Rentabilité par projet
- Evolution des dépenses
- Cash flow prévisionnel
- Ratios financiers

#### Productivité
- Heures travaillées vs facturables
- Utilisation des ressources
- Tendances hebdomadaires
- Analyses par projet

### 7. 🔐 Rôles et Permissions

#### Hiérarchie des Rôles
1. **Administrateur** (niveau 100)
   - Accès complet
   - Gestion des utilisateurs
   - Configuration système

2. **RH** (niveau 80)
   - Gestion complète des employés
   - Paie et congés
   - Rapports RH
   - Conformité

3. **Finance** (niveau 70)
   - Dépenses et factures
   - Validation paie
   - Rapports financiers

4. **Manager** (niveau 50)
   - Gestion de son équipe
   - Approbation congés/dépenses équipe
   - Statistiques équipe

5. **Employé** (niveau 10)
   - Données personnelles
   - Badge et pointage
   - Demandes congés/dépenses

### 8. 🔔 Notifications et Automatisation

#### Notifications Automatiques
- Documents expirés (30 jours avant)
- Approbations en attente (rappel après 2-3 jours)
- Violations temps de travail
- Fins de contrat (60 jours avant)
- Rappels de paie (25 du mois)

#### Canaux
- Notifications in-app
- Emails pour priorité haute/urgente
- Dashboard des alertes

### 9. ⚖️ Conformité Suisse

#### Règles Implémentées
- Maximum 10h/jour, 50h/semaine
- Pauses obligatoires après 5h30
- Repos minimum 11h/jour, 35h/semaine
- Détection travail de nuit (23h-6h)
- Alerte travail dimanche
- Maximum 170h supplémentaires/an

#### Audit Trail
- Journalisation de toutes les actions
- Traçabilité des modifications
- Rapports de conformité
- Archivage légal

### 10. 📱 Interface Mobile

#### Responsive Design
- Bootstrap 5 pour tous les écrans
- Interface tactile optimisée
- Menus adaptés mobile
- Graphiques responsifs

#### Fonctionnalités Mobile
- Badge par QR code/PIN
- Photo de pointage
- Consultation fiches de paie
- Demandes congés/dépenses
- Notifications push (PWA)

## 🛠️ Architecture Technique

### Backend
- **Framework** : Flask 2.x (Python 3.10+)
- **Base de données** : PostgreSQL/MySQL (SQLAlchemy ORM)
- **Authentication** : Flask-Login + 2FA optionnel
- **API** : RESTful JSON
- **Tâches** : APScheduler pour l'automatisation

### Frontend
- **Templates** : Jinja2
- **CSS** : Bootstrap 5 + CSS personnalisé
- **JavaScript** : Vanilla JS + jQuery
- **Graphiques** : Chart.js
- **QR/Photo** : HTML5 APIs

### Sécurité
- Mots de passe hashés (Werkzeug)
- CSRF protection
- Permissions granulaires
- Audit logging
- Chiffrement des données sensibles

## 📋 Installation et Configuration

### 1. Prérequis
```bash
- Python 3.10+
- PostgreSQL 13+ ou MySQL 8+
- Redis (optionnel pour cache)
- Serveur SMTP pour emails
```

### 2. Installation
```bash
# Cloner le projet
git clone https://github.com/globibat/crm-badge.git
cd Globibat_Badge_System

# Environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Dépendances
pip install -r requirements.txt

# Variables d'environnement
cp .env.example .env
# Éditer .env avec vos paramètres
```

### 3. Base de données
```bash
# Créer la base
flask db init
flask db migrate -m "Initial migration"
flask db upgrade

# Données de base
flask init-data

# Créer un admin
flask create-admin
```

### 4. Lancement
```bash
# Développement
flask run

# Production
gunicorn -w 4 -b 0.0.0.0:8000 "app:create_app()"
```

## 🎯 Utilisation

### Premier Démarrage
1. Connectez-vous avec le compte admin
2. Créez les départements et rôles
3. Configurez les politiques de dépenses
4. Ajoutez les employés
5. Générez les badges/QR codes

### Workflow Quotidien

#### Employé
1. Badge à l'arrivée (8h30)
2. Badge départ midi (12h)
3. Badge retour (13h30)
4. Badge départ soir (17h30)

#### Manager
- Consulter dashboard équipe
- Approuver congés/dépenses
- Générer rapports

#### RH
- Lancer calcul paie (25 du mois)
- Valider et distribuer fiches
- Gérer les absences
- Vérifier conformité

#### Finance
- Approuver dépenses importantes
- Valider la paie
- Analyses financières

## 🚨 Monitoring et Maintenance

### Tâches Automatiques
- **Quotidien** : Conformité (22h), Stats (2h), Documents (8h)
- **Bi-quotidien** : Rappels (9h, 16h)
- **Hebdomadaire** : Rapport (lundi 7h), Nettoyage (dimanche 3h)
- **Temps réel** : Dashboard (toutes les 5 min)

### Logs et Monitoring
```bash
# Logs application
tail -f logs/globibat.log

# Logs tâches
tail -f logs/scheduler.log

# Monitoring système
# Intégration possible avec Prometheus/Grafana
```

### Sauvegardes
```bash
# Script de backup quotidien
0 3 * * * /opt/globibat/scripts/backup.sh

# Inclut :
# - Base de données
# - Fichiers uploadés
# - Configurations
```

## 📞 Support

### Contacts
- **Support Technique** : support@globibat.ch
- **RH** : rh@globibat.ch
- **Urgences** : +41 21 505 00 62

### Ressources
- Documentation API : `/api/docs`
- Guide utilisateur : `/help`
- FAQ : `/faq`

---

**Version** : 2.0.0  
**Date** : Décembre 2024  
**Globibat SA** - Système de gestion d'entreprise nouvelle génération