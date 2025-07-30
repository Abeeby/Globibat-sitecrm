# 🏗️ Projet Globibat - CRM & Site Web Ultra-Moderne

## 🎯 Vue d'Ensemble

Ce projet comprend :
1. **Un CRM complet** pour gérer l'entreprise de construction
2. **Une page web ultra-moderne** optimisée SEO pour être #1 sur Google
3. **Un système de badge** pour les employés
4. **Des outils de gestion** (devis, factures, projets, RH)

## 🌟 Fonctionnalités de la Page Web

### 1. **Design Ultra-Moderne**
- Animations fluides et professionnelles
- Mode sombre/clair
- Responsive sur tous les appareils
- Effets visuels impressionnants

### 2. **Fonctionnalités Interactives**
- ✅ **Calculateur de devis instantané** : Les visiteurs peuvent calculer le prix de leur projet en 30 secondes
- ✅ **Système de prise de RDV** : Formulaire complet pour réserver une consultation
- ✅ **Galerie de projets** : Avec filtres par catégorie (rénovation, construction, etc.)
- ✅ **Compteurs animés** : 21 ans d'expérience, 847 projets, 98% satisfaction
- ✅ **FAQ interactive** : Questions/réponses avec animations
- ✅ **Newsletter** : Inscription pour recevoir des conseils
- ✅ **Blog intégré** : Articles et actualités du secteur
- ✅ **Chat widget** : Pour contact instantané
- ✅ **Témoignages clients** : Défilement automatique des avis 5 étoiles

### 3. **SEO Optimisé pour Nyon**
- Title : "Globibat Nyon - Entreprise Construction 5⭐"
- Meta descriptions avec l'adresse exacte
- Schema.org pour entreprise locale
- Géolocalisation GPS Nyon
- Mots-clés : "entreprise construction nyon", "bâtiment vaud"

### 4. **Informations Réelles**
- 📍 Adresse : Rie des Tattes d'Oie 93, 1260 Nyon
- 📞 Téléphone : 021 505 00 62
- ⭐ Note : 5.0/5 (25 avis Google)
- 🕐 Horaires : Lun-Ven 8h-18h, Sam 8h-12h

## 💻 CRM Backend

### Modules Disponibles
1. **Gestion Clients** : Fiches clients, contacts, notes
2. **Projets** : Phases, tâches, documents, budgets
3. **Devis & Factures** : Génération PDF, numérotation auto
4. **RH** : Employés, pointage, congés, fiches de paie
5. **Finance** : Paiements, dépenses, rapports
6. **Inventaire** : Matériaux, équipements, fournisseurs
7. **Planning** : Calendrier, réunions, rappels

## 🚀 Comment Utiliser

### 1. Tester la Page Web Localement
```bash
python test_page.py
```
Cela ouvrira automatiquement la page dans votre navigateur.

### 2. Tester le CRM
```bash
# Créer l'environnement virtuel
python -m venv venv
.\venv\Scripts\activate  # Windows

# Installer les dépendances
pip install -r requirements.txt

# Lancer le CRM
python run.py
```

### 3. Déployer sur GitHub
```bash
.\git_commit.ps1
```

### 4. Déployer sur Hostinger VPS
Suivre le guide : `DEPLOIEMENT_VPS_HOSTINGER.md`

## 📁 Structure du Projet

```
Globibat_Badge_System/
├── index.html              # Page web ultra-moderne (SEO)
├── app/                    # Application CRM Flask
│   ├── models/            # Modèles de données
│   ├── views/             # Routes et contrôleurs
│   ├── templates/         # Templates HTML du CRM
│   └── static/            # Assets (CSS, JS, images)
├── config/                # Configuration (dev/prod)
├── requirements.txt       # Dépendances Python
├── test_page.py          # Script pour tester la page web
├── run.py                # Point d'entrée du CRM
└── guides/               # Documentation
```

## 🎨 Points Forts de la Page

1. **Calculateur de Devis**
   - Calcul instantané selon : Type de projet, Surface, Qualité
   - Prix affiché en CHF avec animation

2. **Galerie de Projets**
   - 6 projets exemples avec prix
   - Filtres animés par catégorie
   - Effets hover impressionnants

3. **Prise de RDV**
   - Formulaire complet avec date/heure
   - Confirmation animée
   - Promesse de rappel sous 24h

4. **Mode Sombre**
   - Switch automatique jour/nuit
   - Sauvegarde de la préférence
   - Design adapté pour les deux modes

## 🔑 Accès CRM

- **URL** : http://localhost:5000
- **Admin** : admin@globibat.ch
- **Employé** : Via système de badge

## 📈 Résultats Attendus

- ✅ **SEO** : Top 1 Google "entreprise construction Nyon"
- ✅ **Conversions** : Augmentation des demandes de devis
- ✅ **Image** : Entreprise moderne et professionnelle
- ✅ **Efficacité** : Gestion complète via le CRM

## 🆘 Support

Pour toute question :
- 📧 info@globibat.com
- 📞 021 505 00 62

---

**Projet développé pour Globibat SA - Leader construction Nyon**