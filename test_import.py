#!/usr/bin/env python3
import sys
import os

# Ajouter le dossier app au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

print("Test d'import des modules...")
print("="*60)

try:
    print("1. Import de app.models...")
    from app.models import db, Employe, Client, Facture, Badge
    print("   ✅ Succès!")
except ImportError as e:
    print(f"   ❌ Erreur: {e}")

try:
    print("\n2. Import de app.views.modern_views...")
    from app.views.modern_views import modern_bp
    print("   ✅ Succès!")
    print(f"   Blueprint name: {modern_bp.name}")
    print(f"   URL prefix: {modern_bp.url_prefix}")
except ImportError as e:
    print(f"   ❌ Erreur: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)
print("Test terminé.")