#!/usr/bin/env python3
"""Script pour tester les routes de l'application moderne"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app_modern import app

print("\n" + "="*60)
print("🔍 ROUTES ENREGISTRÉES DANS L'APPLICATION")
print("="*60)

routes = []
for rule in app.url_map.iter_rules():
    routes.append((rule.endpoint, list(rule.methods - {'HEAD', 'OPTIONS'}), str(rule)))

# Trier par URL
routes.sort(key=lambda x: x[2])

# Afficher les routes modern
print("\n📌 Routes Modern (/modern/*):")
print("-"*40)
modern_routes = [r for r in routes if '/modern/' in r[2]]
if modern_routes:
    for endpoint, methods, rule in modern_routes:
        print(f"  {rule:40} {methods} -> {endpoint}")
else:
    print("  ❌ Aucune route modern trouvée!")

# Afficher les autres routes
print("\n📌 Autres routes:")
print("-"*40)
other_routes = [r for r in routes if '/modern/' not in r[2] and not rule.startswith('/static')]
for endpoint, methods, rule in other_routes[:10]:  # Limiter à 10
    print(f"  {rule:40} {methods} -> {endpoint}")

print("\n" + "="*60)
print(f"Total: {len(routes)} routes enregistrées")
print(f"Routes modern: {len(modern_routes)}")
print("="*60)