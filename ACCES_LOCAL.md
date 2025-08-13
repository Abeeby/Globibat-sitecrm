# 🚀 ACCÈS LOCAL - GLOBIBAT CRM

## ✅ SERVICES ACTIFS

### 1️⃣ **Backend Flask + WebSockets**
- ✅ **Status**: ACTIF sur port 5001
- 🌐 **URL**: http://localhost:5001
- 🔌 **WebSocket**: ws://localhost:5001/socket.io/

### 2️⃣ **Application Web**
- 📊 **Dashboard**: http://localhost:5001/modern/dashboard
- 🧪 **Test WebSocket**: http://localhost:5001/
- 📱 **Toutes les pages**:
  - Employés: http://localhost:5001/modern/employes
  - Clients: http://localhost:5001/modern/clients
  - Projets: http://localhost:5001/modern/chantiers
  - Factures: http://localhost:5001/modern/factures
  - Badges: http://localhost:5001/modern/badges
  - Ressources: http://localhost:5001/modern/ressources
  - Communication: http://localhost:5001/modern/communication

### 3️⃣ **Application Mobile React Native**
- ✅ **Status**: En cours de démarrage avec Expo
- 📱 **Pour tester sur votre téléphone**:
  1. Installer l'app "Expo Go" (App Store / Google Play)
  2. Scanner le QR code qui s'affiche dans le terminal
  3. L'app se lance automatiquement

## 🔑 CONNEXION TEST

### Web
- **Email**: admin@globibat.ch
- **Mot de passe**: admin123

### Mobile
- Même identifiants ou utiliser le bouton "Connexion rapide (Dev)"

## 🎫 SYSTÈME DE BADGE PAR MATRICULE

### Matricules de test disponibles:
- **EMP001** - Jean Dupont
- **EMP002** - Marie Martin  
- **EMP003** - Pierre Durand
- **EMP004** - Sophie Lefebvre
- **EMP005** - Lucas Bernard

### Types de badges:
- **Entrée**: Début de journée
- **Sortie**: Fin de journée
- **Pause**: Début de pause
- **Reprise**: Fin de pause

## 📱 CONFIGURATION MOBILE

Si l'app mobile ne se connecte pas, modifier `GlobibatMobile/src/config.js`:
```javascript
// Remplacer localhost par votre IP locale
API_URL: 'http://VOTRE_IP:5001',
SOCKET_URL: 'http://VOTRE_IP:5001',
```

Pour trouver votre IP:
- Windows: `ipconfig` → IPv4
- Mac/Linux: `ifconfig` → inet

## 🧪 TESTS WEBSOCKET

1. **Page de test**: http://localhost:5001/
2. **Fonctionnalités à tester**:
   - Chat temps réel
   - Notifications push
   - Badges avec matricule
   - Alertes système

## 📊 MONITORING

- **Stats WebSocket**: http://localhost:5001/api/websocket/stats
- **Logs**: Visibles dans le terminal

## 🛠 COMMANDES UTILES

```bash
# Arrêter tous les services
pkill -f "python3 app_websocket.py"
pkill -f "expo"

# Relancer le backend
cd /workspace && python3 app_websocket.py

# Relancer l'app mobile
cd /workspace/GlobibatMobile && npx expo start --tunnel
```

## ⚠️ TROUBLESHOOTING

### Backend ne répond pas
- Vérifier le port 5001: `lsof -i :5001`
- Relancer: `python3 app_websocket.py`

### App mobile ne se connecte pas
- Vérifier l'IP dans `config.js`
- S'assurer d'être sur le même réseau WiFi
- Désactiver le firewall temporairement

### WebSocket déconnecté
- Rafraîchir la page
- Vérifier la console du navigateur (F12)

---

**Support**: Pour toute question, consulter `/workspace/DOCUMENTATION_UI_MODERNE.md`