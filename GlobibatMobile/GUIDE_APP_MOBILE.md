# 📱 GUIDE APPLICATION MOBILE GLOBIBAT CRM

## 🎯 VUE D'ENSEMBLE

Application mobile **React Native** complète pour la gestion du CRM Globibat avec système de **badge par MATRICULE** (pas de QR Code).

## 📱 ÉCRANS DISPONIBLES

### 1️⃣ **LoginScreen** (`src/screens/LoginScreen.js`)
- Connexion sécurisée avec email/mot de passe
- Bouton "Connexion rapide" en mode développement
- Design moderne avec le logo Globibat
- Validation des champs

### 2️⃣ **DashboardScreen** (`src/screens/DashboardScreen.js`)
- 📊 **KPI en temps réel**:
  - Employés actifs/présents
  - Chantiers actifs
  - Factures impayées
  - Chiffre d'affaires mensuel
- 📈 **Graphiques interactifs** (LineChart)
- 🔔 **Activité récente**
- 🎫 **Derniers badges** en temps réel
- 🔘 **FAB** pour accès rapide aux badges

### 3️⃣ **BadgesScreen** (`src/screens/BadgesScreen.js`) ⭐ IMPORTANT
- 🎫 **Saisie du MATRICULE** (pas de QR!)
- ✅ **Validation automatique** du matricule
- 👤 **Affichage infos employé** après validation
- 📍 **Géolocalisation GPS** automatique
- 🔄 **Types de badge**:
  - Entrée (début journée)
  - Sortie (fin journée)  
  - Pause (début pause)
  - Reprise (fin pause)
- 📊 **Historique du jour**
- ⚠️ **Anomalies détectées**
- 🔌 **Synchronisation WebSocket** temps réel

### 4️⃣ **EmployeesScreen** (`src/screens/EmployeesScreen.js`)
- 📋 **Liste complète** des employés
- 🔍 **Recherche** par nom/matricule
- 📊 **Statistiques** (total, actifs, congés)
- 🏷️ **Statuts visuels** (badges colorés)
- 👤 **Avatars** avec initiales
- ➕ **FAB** pour ajouter un employé

### 5️⃣ **ClientsScreen** (`src/screens/ClientsScreen.js`)
- 🏢 **Portefeuille clients**
- 🔍 **Recherche** par nom/email/ville
- 📊 **KPI** (clients actifs, projets, CA)
- 🏷️ **Types** (Entreprise, Particulier, Public)
- 💰 **Chiffre d'affaires** par client
- ➕ **FAB** pour nouveau client

### 6️⃣ **ChatsScreen** (`src/screens/ChatsScreen.js`)
- 💬 **Chat temps réel** via WebSocket
- 🏗️ **Salles par projet/chantier**
- ⌨️ **Indicateur de frappe**
- 📅 **Horodatage** des messages
- 🔌 **Statut connexion** visible
- 📨 **Envoi/réception** instantané

### 7️⃣ **ProfileScreen** (`src/screens/ProfileScreen.js`)
- 👤 **Informations utilisateur**
- 🎫 **Matricule** affiché
- ⚙️ **Paramètres**:
  - Notifications ON/OFF
  - Mode sombre
- 🔧 **Actions**:
  - Modifier profil
  - Changer mot de passe
  - Support
- 🚪 **Déconnexion sécurisée**

### 8️⃣ **NotificationsScreen** (`src/screens/NotificationsScreen.js`)
- 🔔 **Centre de notifications**
- 🎨 **Icônes et couleurs** par type
- ⏰ **Temps relatif** (il y a X minutes)
- ❌ **Suppression individuelle**
- 🗑️ **Effacer tout**
- 📭 **État vide** stylisé

## 🎨 DESIGN & THÈME

### Couleurs Globibat
```javascript
primary: '#005BBB'    // Bleu corporate
secondary: '#FF7A00'  // Orange vif
success: '#27AE60'    // Vert
warning: '#FF7A00'    // Orange
danger: '#DC3545'     // Rouge
light: '#F4F6F8'      // Gris clair
dark: '#2C3E50'       // Gris foncé
```

### Composants utilisés
- **React Native Paper** (Material Design)
- **React Navigation** (Bottom Tabs)
- **React Native Chart Kit** (Graphiques)
- **Moment.js** (Dates en français)

## 🔧 CONFIGURATION

### Fichier principal: `src/config.js`
```javascript
// IMPORTANT: Remplacer par votre IP locale
API_URL: 'http://VOTRE_IP:5001',
SOCKET_URL: 'http://VOTRE_IP:5001',
```

### Trouver votre IP:
- **Windows**: `ipconfig` → IPv4 Address
- **Mac/Linux**: `ifconfig` → inet

## 🎫 SYSTÈME DE BADGE PAR MATRICULE

### Workflow
1. **Employé saisit son matricule** (ex: EMP001)
2. **App valide** le matricule via API
3. **Affichage** nom et poste de l'employé
4. **Sélection** du type de badge
5. **Capture GPS** automatique
6. **Envoi** au serveur
7. **Sync WebSocket** pour temps réel

### Matricules de test
- `EMP001` - Jean Dupont
- `EMP002` - Marie Martin
- `EMP003` - Pierre Durand
- `EMP004` - Sophie Lefebvre
- `EMP005` - Lucas Bernard

## 🚀 LANCEMENT

### 1. Backend (obligatoire)
```bash
cd /workspace
python3 app_websocket.py
```

### 2. Application Mobile
```bash
cd /workspace/GlobibatMobile
npm install
npx expo start
```

### 3. Sur votre téléphone
1. Installer **Expo Go** (App Store/Play Store)
2. Scanner le **QR code** affiché
3. L'app se lance !

## 📱 NAVIGATION

```
┌─────────────────────────────────┐
│         LoginScreen             │
└────────────┬────────────────────┘
             ▼
┌─────────────────────────────────┐
│      Bottom Tab Navigator       │
├─────────────────────────────────┤
│ 📊 Dashboard │ 👥 Employés     │
│ 🏢 Clients  │ 🎫 Badges       │
│ 💬 Chat     │ 👤 Profil        │
└─────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│    NotificationsScreen          │
│    (Stack Navigator)            │
└─────────────────────────────────┘
```

## ✨ FONCTIONNALITÉS TEMPS RÉEL

### WebSocket Events
- ✅ **Chat messages** - Messages instantanés
- ✅ **Badge updates** - Nouveaux badges
- ✅ **Notifications** - Alertes push
- ✅ **Typing indicator** - Qui écrit
- ✅ **Presence** - Statut en ligne

### Contexts React
- **AuthContext** - Gestion authentification
- **SocketContext** - WebSocket management
- **NotificationContext** - Push notifications

## 🐛 TROUBLESHOOTING

### Erreur connexion
- Vérifier l'IP dans `config.js`
- Backend lancé sur port 5001?
- Même réseau WiFi?

### Matricule invalide
- Format correct? (EMP001)
- Employé existe dans DB?
- API accessible?

### GPS non disponible
- Permissions accordées?
- GPS activé sur téléphone?

### WebSocket déconnecté
- Vérifier connexion WiFi
- Backend actif?
- Firewall bloque port 5001?

## 📊 MONITORING

- **Stats API**: http://localhost:5001/api/websocket/stats
- **Logs Backend**: Terminal Python
- **Logs Mobile**: Terminal Expo

## 🎯 PROCHAINES ÉTAPES

- [ ] Mode hors ligne avec cache
- [ ] Synchronisation différée
- [ ] Photos pour badges
- [ ] Signature digitale
- [ ] Export PDF rapports
- [ ] Push notifications natives
- [ ] Biométrie (Face ID/Touch ID)

---

**Version**: 1.0.0  
**Dernière MAJ**: Janvier 2025  
**Support**: support@globibat.ch