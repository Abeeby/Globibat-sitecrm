#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour lancer Globibat CRM en local
Identifiants admin: info@globibat.com / Miser1597532684$
"""
import os
import sys
import time
import webbrowser
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

def print_header():
    print(f"\n{Colors.BLUE}{'=' * 60}{Colors.END}")
    print(f"{Colors.BLUE}{'GLOBIBAT CRM - LANCEMENT LOCAL'.center(60)}{Colors.END}")
    print(f"{Colors.BLUE}{'=' * 60}{Colors.END}\n")

def print_success(message):
    print(f"{Colors.GREEN}✅ {message}{Colors.END}")

def print_info(message):
    print(f"{Colors.YELLOW}ℹ️ {message}{Colors.END}")

def print_error(message):
    print(f"{Colors.RED}❌ {message}{Colors.END}")

def main():
    print_header()
    
    # Vérifier que .env existe
    if not os.path.exists('.env'):
        print_error("Fichier .env non trouvé!")
        print_info("Création du fichier .env avec les identifiants par défaut...")
        with open('.env', 'w') as f:
            f.write("""# Configuration de l'application
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=globibat_secret_key_2024_very_secure_and_long

# Configuration de la base de données
DATABASE_URL=sqlite:///instance/globibat.db

# Configuration de l'admin par défaut
ADMIN_EMAIL=info@globibat.com
ADMIN_USERNAME=info@globibat.com
ADMIN_PASSWORD=Miser1597532684$
ADMIN_FIRSTNAME=Admin
ADMIN_LASTNAME=Globibat

# Configuration Email (SMTP)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=info@globibat.com
MAIL_PASSWORD=your_email_password_here
MAIL_DEFAULT_SENDER=info@globibat.com

# URL de l'application
APP_URL=http://localhost:5000
""")
        print_success("Fichier .env créé!")
    
    # Créer les dossiers nécessaires
    print_info("Création des dossiers...")
    dirs = [
        "instance",
        "instance/logs",
        "app/static/uploads",
        "app/static/uploads/receipts",
        "app/static/uploads/photos",
        "app/static/uploads/documents"
    ]
    for dir_path in dirs:
        os.makedirs(dir_path, exist_ok=True)
    print_success("Dossiers créés")
    
    # Initialiser la base de données
    print_info("Initialisation de la base de données...")
    if os.path.exists('init_database_secure.py'):
        os.system('python3 init_database_secure.py')
    else:
        # Créer un script d'init simple si le secure n'existe pas
        print_info("Utilisation du script d'init standard...")
        os.system('python3 init_database.py')
    print_success("Base de données initialisée")
    
    # Lancer l'application
    print_info("Démarrage de l'application...")
    print(f"\n{Colors.PURPLE}{'=' * 60}{Colors.END}")
    print(f"{Colors.PURPLE}L'APPLICATION VA DÉMARRER{Colors.END}")
    print(f"{Colors.PURPLE}{'=' * 60}{Colors.END}\n")
    
    print(f"{Colors.GREEN}📌 INFORMATIONS DE CONNEXION:{Colors.END}")
    print(f"{Colors.BLUE}   URL: http://localhost:5000{Colors.END}")
    print(f"{Colors.BLUE}   Email: info@globibat.com{Colors.END}")
    print(f"{Colors.BLUE}   Mot de passe: Miser1597532684${Colors.END}")
    print()
    print(f"{Colors.YELLOW}L'application va s'ouvrir dans votre navigateur...{Colors.END}")
    print(f"{Colors.YELLOW}Appuyez sur Ctrl+C pour arrêter le serveur{Colors.END}")
    print(f"\n{Colors.PURPLE}{'=' * 60}{Colors.END}\n")
    
    # Ouvrir le navigateur après 3 secondes
    def open_browser():
        time.sleep(3)
        webbrowser.open('http://localhost:5000')
    
    import threading
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    # Lancer Flask
    try:
        os.system('python3 run.py')
    except KeyboardInterrupt:
        print(f"\n{Colors.GREEN}✅ Application arrêtée{Colors.END}")

if __name__ == "__main__":
    main()