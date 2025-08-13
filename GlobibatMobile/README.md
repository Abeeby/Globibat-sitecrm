# 📱 Globibat Mobile - Application CRM React Native

Application mobile complète pour le CRM Globibat avec gestion des employés, clients, badges par matricule et communication temps réel.

## ✨ Fonctionnalités

### 🎫 **Système de Badge par Matricule**
- ✅ Saisie du matricule employé (pas de QR code)
- ✅ Validation automatique du matricule
- ✅ Types de badge: Entrée, Sortie, Pause, Reprise
- ✅ Géolocalisation GPS automatique
- ✅ Synchronisation temps réel via WebSocket

### 💬 **Chat Temps Réel**
- Messages par chantier/projet
- Indicateur de frappe
- Notifications push
- Historique persistant

### 📊 **Dashboard**
- KPI en temps réel
- Graphiques interactifs
- Alertes et anomalies
- Activité récente

### 👥 **Gestion Employés**
- Liste complète avec recherche
- Détails et statuts
- Badges et présences
- Export des données

### 🏢 **Gestion Clients**
- Portefeuille clients
- Projets associés
- Chiffre d'affaires
- Création de devis

### 🔔 **Notifications Push**
- Alertes temps réel
- Badges et anomalies
- Messages importants
- Rappels automatiques

## 🚀 Installation

### Prérequis
- Node.js 16+
- npm ou yarn
- Expo CLI
- Smartphone avec Expo Go (pour tests)

### Étapes d'installation

1. **Cloner le projet**
```bash
cd GlobibatMobile
```

2. **Installer les dépendances**
```bash
npm install
# ou
yarn install
```

3. **Configuration**
Modifier `src/config.js` avec l'IP de votre serveur:
```javascript
export default {
  API_URL: 'http://VOTRE_IP:5001',
  SOCKET_URL: 'http://VOTRE_IP:5001',
  // ...
}
```

4. **Lancer l'application**
```bash
npm start
# ou
expo start
```

5. **Scanner le QR code avec Expo Go**
- Android: Expo Go app
- iOS: Camera app

## 📋 Structure du Projet

```
GlobibatMobile/
├── src/
│   ├── contexts/          # Contextes React (Auth, Socket, Notifications)
│   ├── screens/           # Écrans de l'application
│   │   ├── LoginScreen.js
│   │   ├── DashboardScreen.js
│   │   ├── BadgesScreen.js       # Badge par MATRICULE
│   │   ├── EmployeesScreen.js
│   │   ├── ClientsScreen.js
│   │   ├── ChatsScreen.js
│   │   └── ProfileScreen.js
│   ├── services/          # Services API
│   │   └── api.js
│   ├── components/        # Composants réutilisables
│   └── config.js         # Configuration
├── App.js                # Point d'entrée
├── package.json
└── README.md
```

## 🔑 Système de Badge par Matricule

### Fonctionnement
1. L'employé saisit son **matricule** (ex: EMP001)
2. L'app valide le matricule via l'API
3. L'employé sélectionne le type de badge
4. La position GPS est capturée automatiquement
5. Le badge est envoyé au serveur
6. Synchronisation temps réel via WebSocket

### Types de badges
- **Entrée** : Début de journée
- **Sortie** : Fin de journée
- **Pause** : Début de pause
- **Reprise** : Fin de pause

## 🌐 API Endpoints

### Badges
- `POST /api/badges/submit` - Soumettre un badge avec matricule
- `GET /api/badges/matricule/:matricule` - Récupérer badges par matricule
- `GET /api/badges/today` - Badges du jour
- `GET /api/badges/anomalies` - Anomalies détectées

### Employés
- `GET /api/employes/matricule/:matricule` - Vérifier un matricule
- `GET /api/employes` - Liste des employés
- `GET /api/employes/:id` - Détails employé

## 🔌 WebSocket Events

### Émis par le client
- `register_user` - Enregistrement utilisateur
- `new_badge` - Nouveau badge matricule
- `send_message` - Envoi message chat
- `update_presence` - Mise à jour présence

### Reçus par le client
- `badge_update` - Mise à jour badge temps réel
- `notification` - Nouvelle notification
- `new_message` - Nouveau message chat
- `alert_broadcast` - Alerte système

## 🎨 Personnalisation

### Couleurs (src/config.js)
```javascript
colors: {
  primary: '#005BBB',    // Bleu corporate
  secondary: '#FF7A00',  // Orange vif
  success: '#27AE60',    // Vert succès
  warning: '#FF7A00',    // Orange alerte
  danger: '#DC3545',     // Rouge danger
}
```

### Types de matricules
Modifier dans `src/config.js` selon votre format:
```javascript
// Exemples de formats
// EMP001, EMP002...
// MAT2024001...
// Personnalisé selon vos besoins
```

## 📱 Captures d'écran

### Écran de Badge par Matricule
- Saisie du matricule
- Validation automatique
- Sélection type de badge
- Géolocalisation
- Historique du jour

## 🐛 Dépannage

### Erreur de connexion
- Vérifier l'IP du serveur dans `config.js`
- S'assurer que le serveur est lancé (`python3 app_websocket.py`)
- Vérifier que le téléphone est sur le même réseau

### Matricule non reconnu
- Vérifier le format du matricule
- S'assurer que l'employé existe dans la base
- Vérifier la connexion API

### GPS non disponible
- Autoriser la localisation pour l'app
- Activer le GPS sur le téléphone

## 🔒 Sécurité

- Token JWT pour l'authentification
- HTTPS en production
- Validation des matricules côté serveur
- Géolocalisation optionnelle

## 📦 Build Production

### Android
```bash
expo build:android
```

### iOS
```bash
expo build:ios
```

## 🤝 Support

Pour toute question ou problème:
- Email: support@globibat.ch
- Documentation: [Wiki interne]

## 📄 Licence

© 2025 Globibat SA - Tous droits réservés

---

**Version**: 1.0.0  
**Dernière mise à jour**: Janvier 2025