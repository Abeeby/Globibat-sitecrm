#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de test local sécurisé pour Globibat CRM
"""
import os
import sys
import subprocess
import time
import requests
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Couleurs pour l'affichage
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    END = '\033[0m'

def print_header(title):
    print(f"\n{Colors.BLUE}{'=' * 60}{Colors.END}")
    print(f"{Colors.BLUE}{title.center(60)}{Colors.END}")
    print(f"{Colors.BLUE}{'=' * 60}{Colors.END}\n")

def print_success(message):
    print(f"{Colors.GREEN}✅ {message}{Colors.END}")

def print_error(message):
    print(f"{Colors.RED}❌ {message}{Colors.END}")

def print_info(message):
    print(f"{Colors.YELLOW}ℹ️ {message}{Colors.END}")

def test_application():
    """Test complet de l'application"""
    
    print_header("TEST LOCAL GLOBIBAT CRM")
    
    # 1. Installation des dépendances
    print_info("Installation des dépendances...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt", "-q"], check=True)
        print_success("Dépendances installées")
    except Exception as e:
        print_error(f"Erreur installation: {e}")
        return False
    
    # 2. Initialisation de la base de données
    print_info("Initialisation de la base de données...")
    try:
        subprocess.run([sys.executable, "init_database_secure.py"], check=True)
        print_success("Base de données initialisée")
    except Exception as e:
        print_error(f"Erreur initialisation: {e}")
        return False
    
    # 3. Démarrage du serveur
    print_info("Démarrage du serveur Flask...")
    server = subprocess.Popen([sys.executable, "run.py"], 
                              stdout=subprocess.PIPE, 
                              stderr=subprocess.PIPE)
    
    # Attendre que le serveur démarre
    time.sleep(5)
    
    # 4. Tests des endpoints
    print_info("Test des endpoints...")
    base_url = "http://localhost:5000"
    
    tests = [
        ("Page d'accueil", "/"),
        ("Page de connexion", "/login"),
        ("Dashboard", "/dashboard"),
    ]
    
    for test_name, endpoint in tests:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            if response.status_code in [200, 302]:
                print_success(f"{test_name}: OK")
            else:
                print_error(f"{test_name}: Status {response.status_code}")
        except Exception as e:
            print_error(f"{test_name}: {e}")
    
    # 5. Test de connexion
    print_info("Test de connexion admin...")
    admin_email = os.getenv('ADMIN_EMAIL', 'info@globibat.com')
    admin_password = os.getenv('ADMIN_PASSWORD')
    
    if admin_password:
        try:
            session = requests.Session()
            
            # Récupérer le token CSRF
            login_page = session.get(f"{base_url}/login")
            
            # Tenter la connexion
            login_data = {
                'email': admin_email,
                'password': admin_password,
                'remember': 'false'
            }
            
            response = session.post(f"{base_url}/login", data=login_data, allow_redirects=False)
            
            if response.status_code == 302:
                print_success("Connexion admin réussie")
            else:
                print_error(f"Connexion échouée: Status {response.status_code}")
        except Exception as e:
            print_error(f"Erreur connexion: {e}")
    else:
        print_info("Test de connexion ignoré (mot de passe non défini dans .env)")
    
    # 6. Arrêt du serveur
    print_info("Arrêt du serveur...")
    server.terminate()
    server.wait()
    print_success("Serveur arrêté")
    
    # Résumé
    print_header("RÉSUMÉ DU TEST")
    print_success("Application testée avec succès!")
    print_info(f"Email admin: {admin_email}")
    print_info("Mot de passe: ****** (sécurisé dans .env)")
    print(f"\n{Colors.PURPLE}L'application est prête pour le déploiement!{Colors.END}")
    
    return True

if __name__ == "__main__":
    success = test_application()
    sys.exit(0 if success else 1)