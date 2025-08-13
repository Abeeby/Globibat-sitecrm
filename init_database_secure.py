#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import Admin
from app.utils.init_data import create_initial_data
from datetime import datetime

def init_database():
    """Initialise la base de données avec les identifiants sécurisés"""
    app = create_app()
    
    with app.app_context():
        print("🔄 Création des tables...")
        db.create_all()
        print("✅ Tables créées")
        
        print("🔄 Création des données initiales...")
        create_initial_data()
        print("✅ Données initiales créées")
        
        # Récupérer les identifiants depuis les variables d'environnement
        admin_email = os.getenv('ADMIN_EMAIL', 'info@globibat.com')
        admin_username = os.getenv('ADMIN_USERNAME', 'info@globibat.com')
        admin_password = os.getenv('ADMIN_PASSWORD', 'Miser1597532684$')
        admin_firstname = os.getenv('ADMIN_FIRSTNAME', 'Admin')
        admin_lastname = os.getenv('ADMIN_LASTNAME', 'Globibat')
        
        # Vérifier si l'admin existe
        admin = Admin.query.filter_by(email=admin_email).first()
        if not admin:
            # Essayer aussi avec l'ancienne adresse
            admin = Admin.query.filter_by(email='admin@globibat.ch').first()
            if admin:
                # Mettre à jour l'ancien admin
                print("🔄 Mise à jour de l'administrateur existant...")
                admin.email = admin_email
                admin.username = admin_username
                admin.firstname = admin_firstname
                admin.lastname = admin_lastname
                admin.set_password(admin_password)
                db.session.commit()
                print("✅ Administrateur mis à jour")
            else:
                # Créer le nouvel admin
                print("🔄 Création de l'administrateur...")
                admin = Admin(
                    username=admin_username,
                    email=admin_email,
                    firstname=admin_firstname,
                    lastname=admin_lastname,
                    phone='+41 79 123 45 67',
                    role='Super Admin',
                    is_active=True,
                    created_at=datetime.utcnow()
                )
                admin.set_password(admin_password)
                db.session.add(admin)
                db.session.commit()
                print("✅ Administrateur créé")
        else:
            print("ℹ️ Administrateur existe déjà")
            # Mettre à jour le mot de passe si nécessaire
            admin.set_password(admin_password)
            db.session.commit()
            print("✅ Mot de passe mis à jour")
        
        print("\n✨ Initialisation terminée avec succès!")
        print("ℹ️ Les identifiants sont stockés de manière sécurisée dans les variables d'environnement")

if __name__ == '__main__':
    init_database()