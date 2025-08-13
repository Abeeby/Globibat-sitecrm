# 🚀 LANCER L'APPLICATION EN LOCAL

## ✅ Méthode Rapide (Recommandée)

### Sur Windows
Double-cliquez sur : **`LANCER_LOCAL.bat`**

### Sur Linux/Mac
```bash
./lancer_local.sh
```

## 📌 Identifiants de Connexion

- **URL**: http://localhost:5000
- **Email**: `info@globibat.com`
- **Mot de passe**: `Miser1597532684$`

## 🔧 Méthode Manuelle

Si les scripts automatiques ne fonctionnent pas :

### 1. Installer les dépendances
```bash
pip install -r requirements.txt
```

### 2. Initialiser la base de données
```bash
python init_database_secure.py
```

### 3. Lancer l'application
```bash
python run.py
```

### 4. Ouvrir dans le navigateur
Allez à : http://localhost:5000

## ⚠️ Résolution de Problèmes

### Erreur "Python non trouvé"
- **Windows**: Téléchargez Python depuis [python.org](https://www.python.org/downloads/)
- **Linux**: `sudo apt install python3 python3-pip`
- **Mac**: `brew install python3`

### Erreur "Module not found"
```bash
pip install -r requirements.txt
```

### Port 5000 déjà utilisé
Modifier le port dans `run.py` :
```python
app.run(port=8000)  # Changer 5000 par 8000
```

## 🎯 Test Rapide

Une fois l'application lancée :
1. Ouvrez http://localhost:5000
2. Connectez-vous avec les identifiants ci-dessus
3. Vous devriez voir le dashboard admin

## 💡 Conseils

- **Gardez le terminal ouvert** pendant l'utilisation
- **Ctrl+C** pour arrêter le serveur
- Les données sont sauvegardées dans `instance/globibat.db`

## 🔐 Sécurité

Les identifiants sont stockés de manière sécurisée dans `.env`
Ne partagez jamais ce fichier !

---

**Besoin d'aide ?** Vérifiez que tous les fichiers sont présents et que Python est installé.