#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de test local pour l'application Globibat
"""

import os
import sys
import subprocess
from pathlib import Path

# Couleurs pour l'affichage
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_step(message):
    print(f"\n{Colors.BLUE}➤ {message}{Colors.END}")

def print_success(message):
    print(f"{Colors.GREEN}✓ {message}{Colors.END}")

def print_error(message):
    print(f"{Colors.RED}✗ {message}{Colors.END}")

def print_warning(message):
    print(f"{Colors.YELLOW}⚠ {message}{Colors.END}")

def test_application():
    """Lance les tests de l'application"""
    
    print(f"{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}     TEST LOCAL - SYSTÈME GLOBIBAT{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}")
    
    # Vérifier l'environnement Python
    print_step("Vérification de l'environnement Python")
    python_version = sys.version_info
    if python_version.major >= 3 and python_version.minor >= 7:
        print_success(f"Python {python_version.major}.{python_version.minor} détecté")
    else:
        print_error("Python 3.7+ requis")
        return False
    
    # Créer l'environnement virtuel si nécessaire
    venv_path = Path("venv")
    if not venv_path.exists():
        print_step("Création de l'environnement virtuel")
        subprocess.run([sys.executable, "-m", "venv", "venv"])
        print_success("Environnement virtuel créé")
    
    # Activer l'environnement et installer les dépendances
    print_step("Installation des dépendances")
    pip_path = "venv\\Scripts\\pip.exe" if os.name == 'nt' else "venv/bin/pip"
    subprocess.run([pip_path, "install", "-r", "requirements.txt", "-q"])
    print_success("Dépendances installées")
    
    # Créer la base de données
    print_step("Initialisation de la base de données")
    python_path = "venv\\Scripts\\python.exe" if os.name == 'nt' else "venv/bin/python"
    
    # Script pour créer la DB et l'admin
    init_script = """
import sys
sys.path.insert(0, '.')
from app import app, db, Admin
from werkzeug.security import generate_password_hash

with app.app_context():
    db.create_all()
    
    # Créer l'admin si n'existe pas
    admin = Admin.query.filter_by(username='Globibat').first()
    if not admin:
        admin = Admin(username='Globibat')
        admin.set_password('Miser1597532684$')
        db.session.add(admin)
        db.session.commit()
        print("Admin créé avec succès")
    else:
        print("Admin existe déjà")
"""
    
    subprocess.run([python_path, "-c", init_script])
    print_success("Base de données initialisée")
    
    # Afficher les URLs importantes
    print(f"\n{Colors.GREEN}{'='*60}{Colors.END}")
    print(f"{Colors.GREEN}✓ APPLICATION PRÊTE !{Colors.END}")
    print(f"{Colors.GREEN}{'='*60}{Colors.END}")
    
    print(f"\n{Colors.YELLOW}URLs disponibles :{Colors.END}")
    print(f"  • Page d'accueil : http://localhost:5000")
    print(f"  • Badgeage : http://localhost:5000/badge")
    print(f"  • Portail employé : http://localhost:5000/employe")
    print(f"  • Admin (caché) : http://localhost:5000/admin-globibat")
    
    print(f"\n{Colors.YELLOW}Identifiants admin :{Colors.END}")
    print(f"  • Utilisateur : Globibat")
    print(f"  • Mot de passe : Miser1597532684$")
    
    print(f"\n{Colors.BLUE}Pour lancer l'application :{Colors.END}")
    if os.name == 'nt':
        print(f"  {python_path} app.py")
    else:
        print(f"  source venv/bin/activate && python app.py")
    
    return True

if __name__ == "__main__":
    try:
        test_application()
    except Exception as e:
        print_error(f"Erreur : {str(e)}")
        sys.exit(1) 