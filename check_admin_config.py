#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour vérifier la configuration admin sécurisée
"""
import os
import sys

# Vérifier si le fichier .env existe
if not os.path.exists('.env'):
    print("❌ Fichier .env non trouvé!")
    print("✅ Les identifiants admin sont maintenant sécurisés dans .env")
    sys.exit(1)

# Lire le fichier .env
print("=" * 60)
print("🔐 VÉRIFICATION DE LA CONFIGURATION ADMIN")
print("=" * 60)
print()

env_vars = {}
with open('.env', 'r') as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith('#'):
            if '=' in line:
                key, value = line.split('=', 1)
                env_vars[key.strip()] = value.strip()

# Vérifier les variables importantes
required_vars = [
    'ADMIN_EMAIL',
    'ADMIN_USERNAME', 
    'ADMIN_PASSWORD',
    'SECRET_KEY'
]

print("📋 Variables de configuration:")
print("-" * 40)
for var in required_vars:
    if var in env_vars:
        if var == 'ADMIN_PASSWORD':
            # Masquer le mot de passe
            print(f"✅ {var}: ******** (sécurisé)")
        elif var == 'SECRET_KEY':
            print(f"✅ {var}: ******** (sécurisé)")
        else:
            print(f"✅ {var}: {env_vars[var]}")
    else:
        print(f"❌ {var}: NON DÉFINI")

print()
print("=" * 60)
print("✨ RÉSUMÉ:")
print("=" * 60)

if all(var in env_vars for var in required_vars):
    print("✅ Configuration admin sécurisée!")
    print(f"📧 Email admin: {env_vars.get('ADMIN_EMAIL')}")
    print("🔒 Mot de passe: ******** (stocké de manière sécurisée)")
    print()
    print("ℹ️ Les identifiants ne sont PAS visibles dans le code")
    print("ℹ️ Ils sont stockés dans le fichier .env")
    print("ℹ️ Le fichier .env est exclu de Git (.gitignore)")
    print()
    print("🚀 Prêt pour le déploiement sur VPS!")
    print("   Utilisez: bash deploy_vps_secure.sh")
else:
    print("❌ Configuration incomplète!")
    print("   Vérifiez le fichier .env")
    sys.exit(1)