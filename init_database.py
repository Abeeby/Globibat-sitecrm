#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script d'initialisation de la base de données Globibat CRM
NE PAS AFFICHER LES IDENTIFIANTS EN PRODUCTION
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.user import User, Role
from app.models.employee import Employee, Department, Attendance
from app.models.client import Client, Contact
from datetime import datetime, date, timedelta
import random

def init_database():
    """Initialiser la base de données avec les données de base"""
    app = create_app()
    with app.app_context():
        print("=" * 50)
        print("INITIALISATION DE LA BASE DE DONNÉES GLOBIBAT")
        print("=" * 50)
        
        # Supprimer et recréer les tables
        print("\n[1/5] Création des tables...")
        db.drop_all()
        db.create_all()
        print("✓ Tables créées avec succès")
        
        # Créer les rôles
        print("\n[2/5] Création des rôles...")
        Role.insert_roles()
        print("✓ Rôles créés")
        
        # Créer l'administrateur principal
        print("\n[3/5] Création du compte administrateur...")
        admin_role = Role.query.filter_by(name='Admin').first()
        
        # Vérifier si l'admin existe déjà
        admin = User.query.filter_by(email='info@globibat.com').first()
        if not admin:
            admin = User(
                username='admin',
                email='info@globibat.com',
                first_name='Admin',
                last_name='Globibat',
                phone='+41 79 123 45 67',
                role_id=admin_role.id,
                is_active=True,
                is_verified=True,
                created_at=datetime.utcnow()
            )
            # Utiliser le mot de passe spécifié
            admin.set_password('Miser1597532684!')
            db.session.add(admin)
            db.session.commit()
            print("✓ Administrateur créé")
        else:
            # Mettre à jour le mot de passe si l'admin existe
            admin.set_password('Miser1597532684!')
            db.session.commit()
            print("✓ Mot de passe administrateur mis à jour")
        
        # Créer les départements
        print("\n[4/5] Création des départements...")
        departments_data = [
            {'name': 'Direction', 'code': 'DIR', 'description': 'Direction générale'},
            {'name': 'Commercial', 'code': 'COM', 'description': 'Service commercial et ventes'},
            {'name': 'Technique', 'code': 'TEC', 'description': 'Service technique et production'},
            {'name': 'Administratif', 'code': 'ADM', 'description': 'Service administratif'},
            {'name': 'Comptabilité', 'code': 'CPT', 'description': 'Service comptabilité'},
            {'name': 'Ressources Humaines', 'code': 'RH', 'description': 'Service RH'}
        ]
        
        for dept_data in departments_data:
            dept = Department.query.filter_by(code=dept_data['code']).first()
            if not dept:
                dept = Department(**dept_data)
                db.session.add(dept)
        
        db.session.commit()
        print("✓ Départements créés")
        
        # Créer des employés de test
        print("\n[5/5] Création des employés de test...")
        employee_role = Role.query.filter_by(name='Employee').first()
        manager_role = Role.query.filter_by(name='Manager').first()
        
        employees_data = [
            {
                'employee_code': 'EMP001',
                'first_name': 'Jean',
                'last_name': 'Dupont',
                'email': 'jean.dupont@globibat.com',
                'phone': '+41 79 234 56 78',
                'department': 'TEC',
                'role': manager_role.id,
                'position': 'Chef de chantier'
            },
            {
                'employee_code': 'EMP002',
                'first_name': 'Marie',
                'last_name': 'Martin',
                'email': 'marie.martin@globibat.com',
                'phone': '+41 79 345 67 89',
                'department': 'COM',
                'role': employee_role.id,
                'position': 'Commerciale'
            },
            {
                'employee_code': 'EMP003',
                'first_name': 'Pierre',
                'last_name': 'Bernard',
                'email': 'pierre.bernard@globibat.com',
                'phone': '+41 79 456 78 90',
                'department': 'TEC',
                'role': employee_role.id,
                'position': 'Ouvrier qualifié'
            },
            {
                'employee_code': 'EMP004',
                'first_name': 'Sophie',
                'last_name': 'Durand',
                'email': 'sophie.durand@globibat.com',
                'phone': '+41 79 567 89 01',
                'department': 'CPT',
                'role': employee_role.id,
                'position': 'Comptable'
            },
            {
                'employee_code': 'EMP005',
                'first_name': 'Lucas',
                'last_name': 'Moreau',
                'email': 'lucas.moreau@globibat.com',
                'phone': '+41 79 678 90 12',
                'department': 'TEC',
                'role': employee_role.id,
                'position': 'Maçon'
            }
        ]
        
        for emp_data in employees_data:
            # Créer l'utilisateur
            user = User.query.filter_by(email=emp_data['email']).first()
            if not user:
                user = User(
                    username=emp_data['email'].split('@')[0],
                    email=emp_data['email'],
                    first_name=emp_data['first_name'],
                    last_name=emp_data['last_name'],
                    phone=emp_data['phone'],
                    role_id=emp_data['role'],
                    is_active=True,
                    is_verified=True
                )
                user.set_password('Employee2024!')  # Mot de passe par défaut pour les tests
                db.session.add(user)
                db.session.flush()
                
                # Créer l'employé
                dept = Department.query.filter_by(code=emp_data['department']).first()
                employee = Employee(
                    employee_code=emp_data['employee_code'],
                    user_id=user.id,
                    department_id=dept.id if dept else None,
                    position=emp_data['position'],
                    hire_date=date.today() - timedelta(days=random.randint(30, 365)),
                    base_salary=random.randint(4000, 8000),
                    contract_type='CDI'
                )
                db.session.add(employee)
        
        # Créer quelques pointages de test pour aujourd'hui
        employees = Employee.query.all()
        today = date.today()
        
        for emp in employees:
            # Créer des pointages pour les 7 derniers jours
            for i in range(7):
                attendance_date = today - timedelta(days=i)
                if attendance_date.weekday() < 5:  # Jours de semaine uniquement
                    attendance = Attendance(
                        employee_id=emp.id,
                        date=attendance_date,
                        check_in=datetime.combine(attendance_date, datetime.min.time()).replace(
                            hour=random.randint(7, 9), 
                            minute=random.randint(0, 59)
                        ),
                        check_out=datetime.combine(attendance_date, datetime.min.time()).replace(
                            hour=random.randint(17, 19), 
                            minute=random.randint(0, 59)
                        ) if i > 0 else None  # Pas de check_out pour aujourd'hui
                    )
                    db.session.add(attendance)
        
        # Créer quelques clients de test
        clients_data = [
            {
                'name': 'Construction Moderne SA',
                'email': 'contact@construction-moderne.ch',
                'phone': '+41 21 123 45 67',
                'address': 'Route de Lausanne 45, 1020 Renens',
                'city': 'Renens',
                'postal_code': '1020',
                'country': 'Suisse'
            },
            {
                'name': 'Immobilier Plus Sàrl',
                'email': 'info@immobilier-plus.ch',
                'phone': '+41 22 234 56 78',
                'address': 'Avenue de la Gare 12, 1003 Lausanne',
                'city': 'Lausanne',
                'postal_code': '1003',
                'country': 'Suisse'
            },
            {
                'name': 'Rénovation Express',
                'email': 'contact@renovation-express.ch',
                'phone': '+41 24 345 67 89',
                'address': 'Rue du Commerce 8, 1400 Yverdon',
                'city': 'Yverdon-les-Bains',
                'postal_code': '1400',
                'country': 'Suisse'
            }
        ]
        
        for client_data in clients_data:
            client = Client.query.filter_by(email=client_data['email']).first()
            if not client:
                client = Client(**client_data)
                db.session.add(client)
        
        db.session.commit()
        print("✓ Employés et données de test créés")
        
        print("\n" + "=" * 50)
        print("INITIALISATION TERMINÉE AVEC SUCCÈS")
        print("=" * 50)
        print("\nINFORMATIONS DE CONNEXION:")
        print("-" * 30)
        print("Admin CRM:")
        print("  URL: http://localhost:5000/admin")
        print("  (Identifiants sécurisés - non affichés)")
        print("\nEspace Employé:")
        print("  URL: http://localhost:5000/employee")
        print("  Email: jean.dupont@globibat.com")
        print("  Mot de passe: Employee2024!")
        print("\nSystème de Badge:")
        print("  URL: http://localhost:5000/badge")
        print("  Matricules: EMP001 à EMP005")
        print("\nSite Internet:")
        print("  URL: http://localhost:5000")
        print("=" * 50)

if __name__ == '__main__':
    init_database()
