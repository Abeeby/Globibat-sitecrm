"""
Point d'entrée WSGI pour le déploiement en production
"""
import os
import sys

# Ajouter le répertoire racine au path Python
sys.path.insert(0, os.path.dirname(__file__))

from run import app

# Configuration pour Hostinger
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000) 