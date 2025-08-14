#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys

# Ajouter le répertoire au path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configuration basique
os.environ['FLASK_ENV'] = 'development'
os.environ['FLASK_DEBUG'] = '1'

print("🚀 Démarrage de Globibat CRM...")
print("=" * 50)
print("📌 Accès: http://localhost:5000")
print("📧 Email: info@globibat.com")
print("🔐 Mot de passe: Miser1597532684$")
print("=" * 50)
print("\nAppuyez sur Ctrl+C pour arrêter\n")

try:
    from app import create_app
    app = create_app()
    
    # Lancer l'application
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=False,
        use_reloader=False
    )
except ImportError as e:
    print(f"❌ Erreur d'import: {e}")
    print("Vérifiez que les dépendances sont installées:")
    print("  pip install flask flask-sqlalchemy flask-login")
except Exception as e:
    print(f"❌ Erreur: {e}")