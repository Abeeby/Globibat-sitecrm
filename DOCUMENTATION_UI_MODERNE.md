# 🎨 Documentation UI Moderne - CRM Globibat

## 📋 Vue d'ensemble

Le CRM Globibat a été entièrement refondu avec une interface utilisateur moderne, premium et adaptée au secteur du BTP. Le nouveau design s'inspire des meilleurs CRM du marché (Monday.com, ClickUp, Notion) tout en restant spécifiquement adapté aux besoins de la construction.

## 🚀 Démarrage rapide

### Installation et lancement

```bash
# 1. Installer les dépendances
pip install -r requirements.txt

# 2. Lancer l'application avec le design moderne
python app_modern.py

# 3. Accéder au CRM
# Ouvrir dans le navigateur : http://localhost:5000
```

## 🎨 Système de design

### Palette de couleurs

- **Bleu corporate** : `#005BBB` - Couleur principale de la marque
- **Gris clair** : `#F4F6F8` - Arrière-plans secondaires
- **Blanc pur** : `#FFFFFF` - Arrière-plans principaux
- **Orange vif** : `#FF7A00` - Alertes et anomalies
- **Vert succès** : `#27AE60` - Statuts positifs et validations

### Typographie

- **Titres** : Poppins (600-700)
- **Contenu** : Inter (400-500)
- **Tailles** : Système responsive avec échelle modulaire

### Composants

- **Cartes** : Ombres douces, coins arrondis, animations au survol
- **Tableaux** : Design épuré avec hover states
- **Boutons** : Plusieurs variantes (primary, secondary, ghost)
- **Formulaires** : Inputs modernes avec états visuels clairs

## 🌓 Mode clair et sombre

Le CRM dispose d'un système de thème complet :

- **Switch instantané** : Bouton dans le header
- **Persistance** : Préférence sauvegardée localement
- **Adaptation complète** : Tous les composants s'adaptent

## 📱 Responsive Design

L'interface est entièrement responsive :

- **Desktop** : Layout complet avec sidebar
- **Tablette** : Sidebar collapsible, grilles adaptatives
- **Mobile** : Navigation optimisée, composants empilés

## 🏗️ Modules métier

### 1. Dashboard principal

- **KPI en temps réel** : 6 indicateurs clés
- **Tableau des badges** : Suivi des présences du jour
- **Anomalies** : Alertes prioritaires
- **Graphiques** : Activité des chantiers
- **Factures récentes** : Statut de facturation

### 2. Gestion des chantiers

#### Vue d'ensemble
- Cartes visuelles des chantiers
- Progression en temps réel
- Statuts codés par couleur
- Statistiques par chantier

#### Planning Gantt
- Vue chronologique des phases
- Dépendances entre tâches
- Progression visuelle
- Modes jour/semaine/mois

#### Carte interactive
- Localisation géographique
- Clustering des chantiers
- Informations au clic
- Filtres par région

#### Timeline d'avancement
- Journal chronologique
- Photos avant/après
- Événements importants
- Documentation associée

#### Check-list par phase
- Phases de construction
- Validation des étapes
- Progression automatique
- Rappels et alertes

#### Galerie photos
- Upload drag & drop
- Organisation par date
- Comparaison avant/après
- Métadonnées automatiques

### 3. Gestion des factures

- **Création directe** : Formulaire intégré
- **Calcul automatique** : TVA et totaux
- **Export PDF** : Génération instantanée
- **Envoi email** : Intégration messagerie
- **Import** : Excel et PDF existants
- **Suivi paiements** : États et relances

### 4. Ressources & Matériel

#### Inventaire machines
- État opérationnel
- Localisation actuelle
- Planning maintenance
- Historique utilisation

#### Stock matériaux
- Niveaux en temps réel
- Alertes réapprovisionnement
- Consommation par chantier
- Commandes automatiques

### 5. RH Chantier

- **Planning équipes** : Affectation par chantier
- **Géolocalisation** : Pointages GPS
- **Documents** : CACES, permis, certifications
- **Formations** : Suivi et renouvellement

### 6. Sécurité & Conformité

- **Rapports incidents** : Formulaire avec photos
- **Check-list sécurité** : Quotidienne par chantier
- **Contrôles** : Historique et planification
- **Documentation** : Normes et procédures

### 7. Suivi financier

- **Budget vs Réel** : Comparaison graphique
- **Facturation par étape** : Jalons de paiement
- **Alertes dépassement** : Notifications automatiques
- **Rapports** : Export Excel/PDF

### 8. Communication interne

- **Chat par chantier** : Messages en temps réel
- **Journal d'activité** : Log automatique
- **Partage documents** : Cloud intégré
- **Notifications** : Push et email

## 🔧 Architecture technique

### Structure des fichiers

```
/workspace/
├── app_modern.py              # Point d'entrée principal
├── app/
│   ├── static/
│   │   └── css/
│   │       └── modern-design-system.css  # Système de design
│   ├── templates/
│   │   ├── base_modern.html             # Template de base
│   │   ├── dashboard_modern.html        # Dashboard
│   │   └── chantiers_modern.html       # Module chantiers
│   └── views/
│       └── modern_views.py             # Contrôleurs Flask
```

### Technologies utilisées

- **Backend** : Flask 2.x, SQLAlchemy
- **Frontend** : HTML5, CSS3 moderne, JavaScript ES6+
- **CSS** : Variables CSS, Grid, Flexbox
- **Icônes** : RemixIcon
- **Graphiques** : Chart.js 4.x
- **Cartes** : Leaflet
- **Planning** : Frappe Gantt

## 🔌 API Endpoints

### Dashboard
- `GET /modern/dashboard` - Dashboard principal
- `GET /modern/api/stats` - Statistiques temps réel
- `GET /modern/api/notifications` - Notifications

### Chantiers
- `GET /modern/chantiers` - Liste des chantiers
- `GET /modern/api/chantiers/<id>` - Détails chantier
- `POST /modern/api/chantiers` - Créer chantier
- `PUT /modern/api/chantiers/<id>` - Modifier chantier

### Recherche
- `GET /modern/api/search?q=<query>` - Recherche globale

## 🎯 Fonctionnalités clés

### Recherche globale
- Recherche instantanée dans tous les modules
- Suggestions en temps réel
- Filtres par type
- Historique de recherche

### Notifications temps réel
- Badge sur l'icône
- Panel dédié
- Types : succès, warning, danger, info
- Actions directes

### Animations et transitions
- Fade in/out fluides
- Slide animations
- Hover states
- Loading states

## 📊 Performances

### Optimisations
- CSS minifié en production
- Lazy loading des images
- Cache navigateur optimisé
- Requêtes API asynchrones

### Métriques cibles
- First Paint : < 1s
- Interactive : < 2s
- Fully loaded : < 3s
- Lighthouse score : > 90

## 🔒 Sécurité

- **CSRF Protection** : Tokens sur tous les formulaires
- **XSS Prevention** : Échappement automatique
- **HTTPS** : SSL/TLS en production
- **Authentication** : Flask-Login avec 2FA optionnel
- **Permissions** : Système de rôles granulaire

## 🚀 Déploiement

### Production

```bash
# Variables d'environnement
export FLASK_ENV=production
export SECRET_KEY=<clé-secrète-sécurisée>
export DATABASE_URL=<url-base-production>

# Lancer avec Gunicorn
gunicorn app_modern:app -w 4 -b 0.0.0.0:8000
```

### Docker

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "app_modern:app", "-w", "4", "-b", "0.0.0.0:8000"]
```

## 📝 Roadmap

### Phase 1 (Complété) ✅
- [x] Nouveau système de design
- [x] Mode clair/sombre
- [x] Dashboard moderne
- [x] Module chantiers complet
- [x] Responsive design

### Phase 2 (En cours)
- [ ] Module factures avancé
- [ ] Intégration comptabilité
- [ ] App mobile native
- [ ] Webhooks API

### Phase 3 (Planifié)
- [ ] IA prédictive
- [ ] Réalité augmentée chantiers
- [ ] Blockchain documents
- [ ] IoT capteurs chantier

## 🆘 Support

### Problèmes fréquents

**Le mode sombre ne fonctionne pas**
- Vider le cache navigateur
- Vérifier localStorage activé

**Les graphiques ne s'affichent pas**
- Vérifier Chart.js chargé
- Console pour erreurs JS

**Performance lente**
- Optimiser requêtes DB
- Activer cache Redis
- CDN pour assets

### Contact

- **Email** : support@globibat.ch
- **Documentation** : https://docs.globibat.ch
- **GitHub** : https://github.com/globibat/crm

## 📜 Licence

Copyright © 2024 Globibat SA. Tous droits réservés.

---

*Documentation mise à jour le 15 février 2024*
*Version 2.0.0 - Design Moderne*