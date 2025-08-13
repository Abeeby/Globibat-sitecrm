#!/usr/bin/env python3
"""Script pour initialiser la base de données avec des données de démonstration"""

import os
import sys

# Ajouter le répertoire au path
sys.path.insert(0, os.path.dirname(__file__))

# Importer l'application et les modèles
from app_modern import app, db, initialize_database

# Initialiser la base
if __name__ == '__main__':
    print("🔄 Initialisation de la base de données...")
    initialize_database()
    print("✅ Base de données prête!")
