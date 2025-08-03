#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import Admin
from app.utils.init_data import create_initial_data
from datetime import datetime

def init_database():
    app = create_app()
    with app.app_context():
        print("Creation des tables...")
        db.create_all()
        print("Tables creees")
        
        print("Creation des donnees initiales...")
        create_initial_data()
        print("Donnees initiales creees")
        
        admin = Admin.query.filter_by(email='admin@globibat.ch').first()
        if not admin:
            print("Creation de l'administrateur...")
            admin = Admin(
                username='admin',
                email='admin@globibat.ch',
                firstname='Admin',
                lastname='Globibat',
                phone='+41 79 123 45 67',
                role='Super Admin',
                is_active=True,
                created_at=datetime.utcnow()
            )
            admin.set_password('Admin2024!')
            db.session.add(admin)
            db.session.commit()
            print("Administrateur cree")
            print("Email: admin@globibat.ch")
            print("Mot de passe: Admin2024!")
        else:
            print("Administrateur existe deja")
        
        print("Initialisation terminee!")

if __name__ == '__main__':
    init_database()
