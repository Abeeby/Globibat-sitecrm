#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys

# Configuration de l'environnement
os.environ['FLASK_ENV'] = 'development'
os.environ['SECRET_KEY'] = 'globibat_secret_key_2024'
os.environ['FLASK_DEBUG'] = '0'

# Ajouter le chemin au sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 60)
print("🚀 DÉMARRAGE DE GLOBIBAT CRM - VERSION COMPLÈTE")
print("=" * 60)
print()
print("📌 Accès: http://localhost:5000")
print("📧 Connexion avec vos identifiants admin")
print()
print("=" * 60)
print()

# Essayer de lancer l'application
try:
    # Vérifier si on utilise app.py ou run.py
    if os.path.exists('app.py'):
        # Charger et lancer app.py
        with open('app.py', 'r', encoding='utf-8') as f:
            code = f.read()
            # Ajouter le code pour lancer l'application
            code += "\n\nif __name__ == '__main__':\n    app.run(host='0.0.0.0', port=5000, debug=False)"
            exec(code)
    else:
        print("❌ Fichier app.py non trouvé")
        
except Exception as e:
    print(f"❌ Erreur: {e}")
    print("\nVérifiez que toutes les dépendances sont installées:")