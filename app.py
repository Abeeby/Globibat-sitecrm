#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Point d'entrée principal de l'application Globibat CRM
"""

import os
import sys
from app import create_app, db
from app.models.user import User, Role
from app.models.employee import Employee, Department, Attendance
from flask_migrate import Migrate

# Créer l'application Flask
app = create_app()
migrate = Migrate(app, db)

# Shell context pour le débogage
@app.shell_context_processor
def make_shell_context():
    """Contexte pour flask shell"""
    return {
        'db': db,
        'User': User,
        'Role': Role,
        'Employee': Employee,
        'Department': Department,
        'Attendance': Attendance
    }

# Point d'entrée principal
if __name__ == '__main__':
    # S'assurer que les dossiers nécessaires existent
    os.makedirs('instance', exist_ok=True)
    os.makedirs('logs', exist_ok=True)
    os.makedirs('app/static/uploads', exist_ok=True)
    
    # Mode de lancement
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    # Message de démarrage
    print("=" * 60)
    print("GLOBIBAT CRM - SYSTÈME INTÉGRÉ")
    print("=" * 60)
    print(f"🚀 Démarrage du serveur sur http://localhost:{port}")
    print("-" * 60)
    print("📌 Points d'accès disponibles:")
    print(f"   • Site Internet: http://localhost:{port}/")
    print(f"   • CRM Admin: http://localhost:{port}/admin")
    print(f"   • Espace Employé: http://localhost:{port}/employee")
    print(f"   • Système Badge: http://localhost:{port}/badge")
    print(f"   • API: http://localhost:{port}/api/v1/")
    print("-" * 60)
    
    # Instructions de connexion
    if debug:
        print("⚠️  Mode DEBUG activé - Ne pas utiliser en production!")
        print("-" * 60)
    
    print("💡 Pour initialiser la base de données:")
    print("   python init_database.py")
    print("-" * 60)
    print("Appuyez sur Ctrl+C pour arrêter le serveur")
    print("=" * 60)
    
    # Lancer l'application
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug,
        use_reloader=debug
    ) 