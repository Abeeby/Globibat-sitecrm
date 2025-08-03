#!/usr/bin/env python3
"""
Script pour corriger les problèmes de modèles dans le CRM Globibat
"""

import os
import sys

def fix_crm_py():
    """Corriger les erreurs dans crm.py"""
    crm_file = '/var/www/globibat/app/views/crm.py'
    
    if not os.path.exists(crm_file):
        print(f"❌ Fichier {crm_file} non trouvé")
        return
    
    with open(crm_file, 'r') as f:
        content = f.read()
    
    # Remplacements nécessaires
    replacements = [
        # Remplacer created_at par issue_date pour Quote
        ('Quote.created_at.desc()', 'Quote.issue_date.desc()'),
        ('Quote.created_at', 'Quote.issue_date'),
        
        # Remplacer created_at par issue_date pour Invoice
        ('Invoice.created_at.desc()', 'Invoice.issue_date.desc()'),
        ('Invoice.created_at', 'Invoice.issue_date'),
        
        # Retirer is_active pour Client (on va lister tous les clients)
        ('Client.query.filter_by(is_active=True)', 'Client.query'),
        ('filter_by(is_active=True)', ''),  # Pour les cas restants
    ]
    
    modified = False
    for old, new in replacements:
        if old in content:
            content = content.replace(old, new)
            modified = True
            print(f"✅ Remplacé: {old} → {new}")
    
    if modified:
        with open(crm_file, 'w') as f:
            f.write(content)
        print(f"✅ Fichier {crm_file} corrigé")
    else:
        print(f"ℹ️ Aucune modification nécessaire dans {crm_file}")

def add_badge_number_to_employee():
    """Ajouter badge_number au modèle Employee"""
    employee_file = '/var/www/globibat/app/models/employee.py'
    
    if not os.path.exists(employee_file):
        print(f"❌ Fichier {employee_file} non trouvé")
        return
    
    with open(employee_file, 'r') as f:
        content = f.read()
    
    # Vérifier si badge_number existe déjà
    if 'badge_number' in content:
        print("ℹ️ badge_number existe déjà dans Employee")
        return
    
    # Ajouter badge_number après canton
    old_text = """    canton = db.Column(db.String(50))
    
    # Statut
    is_active = db.Column(db.Boolean, default=True)"""
    
    new_text = """    canton = db.Column(db.String(50))
    
    # Badge
    badge_number = db.Column(db.String(20), unique=True)
    
    # Statut
    is_active = db.Column(db.Boolean, default=True)"""
    
    if old_text in content:
        content = content.replace(old_text, new_text)
        with open(employee_file, 'w') as f:
            f.write(content)
        print("✅ badge_number ajouté au modèle Employee")
    else:
        print("⚠️ Structure du fichier Employee différente, ajout manuel nécessaire")

def add_is_active_to_client():
    """Ajouter is_active au modèle Client"""
    client_file = '/var/www/globibat/app/models/client.py'
    
    if not os.path.exists(client_file):
        print(f"❌ Fichier {client_file} non trouvé")
        return
    
    with open(client_file, 'r') as f:
        content = f.read()
    
    # Vérifier si is_active existe déjà
    if 'is_active' in content:
        print("ℹ️ is_active existe déjà dans Client")
        return
    
    # Ajouter is_active avant # Relations
    old_text = """    internal_notes = db.Column(db.Text)
    
    # Relations"""
    
    new_text = """    internal_notes = db.Column(db.Text)
    
    # Statut
    is_active = db.Column(db.Boolean, default=True)
    
    # Relations"""
    
    if old_text in content:
        content = content.replace(old_text, new_text)
        with open(client_file, 'w') as f:
            f.write(content)
        print("✅ is_active ajouté au modèle Client")
    else:
        print("⚠️ Structure du fichier Client différente, ajout manuel nécessaire")

def update_database():
    """Mettre à jour la base de données avec les nouveaux champs"""
    print("\n🔄 Mise à jour de la base de données...")
    
    commands = [
        'cd /var/www/globibat',
        'export FLASK_ENV=development',
        'export SECRET_KEY=dev-secret-key-for-testing',
        'export DATABASE_URL=mysql://globibat_user:Globibat2024Secure!@localhost:3306/globibat_crm',
        './venv/bin/python -c "from app import create_app, db; app = create_app(\'development\'); app.app_context().push(); db.create_all(); print(\'✅ Tables mises à jour\')"'
    ]
    
    full_command = ' && '.join(commands)
    os.system(full_command)

def create_test_employees():
    """Créer des employés de test avec badges"""
    print("\n🧑‍💼 Création des employés de test...")
    
    script = '''
cd /var/www/globibat
export FLASK_ENV=development
export SECRET_KEY=dev-secret-key-for-testing
export DATABASE_URL=mysql://globibat_user:Globibat2024Secure!@localhost:3306/globibat_crm

./venv/bin/python << 'EOF'
from app import create_app, db
from app.models import Employee, User
from datetime import date

app = create_app('development')
with app.app_context():
    # Créer des employés de test
    employees_data = [
        {
            'employee_code': 'EMP001',
            'badge_number': '001',
            'first_name': 'Jean',
            'last_name': 'Dupont',
            'position': 'Maçon',
            'department': 'Construction',
            'hourly_rate': 35.0,
            'hire_date': date(2020, 1, 15)
        },
        {
            'employee_code': 'EMP002',
            'badge_number': '002',
            'first_name': 'Marie',
            'last_name': 'Martin',
            'position': 'Chef de chantier',
            'department': 'Construction',
            'hourly_rate': 45.0,
            'hire_date': date(2019, 6, 1)
        },
        {
            'employee_code': 'EMP003',
            'badge_number': '003',
            'first_name': 'Pierre',
            'last_name': 'Bernard',
            'position': 'Électricien',
            'department': 'Électricité',
            'hourly_rate': 40.0,
            'hire_date': date(2021, 3, 10)
        }
    ]
    
    for emp_data in employees_data:
        # Vérifier si l'employé existe déjà
        employee = Employee.query.filter_by(employee_code=emp_data['employee_code']).first()
        if not employee:
            # Créer le User associé
            user = User(
                username=emp_data['first_name'].lower() + '.' + emp_data['last_name'].lower(),
                email=emp_data['first_name'].lower() + '.' + emp_data['last_name'].lower() + '@globibat.com',
                first_name=emp_data['first_name'],
                last_name=emp_data['last_name'],
                is_active=True
            )
            user.set_password('password123')  # Mot de passe par défaut
            db.session.add(user)
            db.session.flush()
            
            # Créer l'employé
            emp_data['user_id'] = user.id
            employee = Employee(**emp_data)
            db.session.add(employee)
            print(f"✅ Employé créé: {emp_data['first_name']} {emp_data['last_name']} (Badge: {emp_data['badge_number']})")
        else:
            # Mettre à jour le badge_number si nécessaire
            if not employee.badge_number:
                employee.badge_number = emp_data['badge_number']
                print(f"✅ Badge ajouté pour: {employee.user.first_name} {employee.user.last_name}")
    
    db.session.commit()
    print("✅ Employés de test créés/mis à jour")
EOF
'''
    os.system(script)

if __name__ == '__main__':
    print("🔧 Correction des modèles Globibat CRM\n")
    
    # Corriger les fichiers
    add_badge_number_to_employee()
    add_is_active_to_client()
    fix_crm_py()
    
    # Mettre à jour la base de données
    update_database()
    
    # Créer les employés de test
    create_test_employees()
    
    print("\n✅ Corrections terminées!")
    print("\n📱 Interface de badgeage disponible sur: http://148.230.105.25:5000/badge")
    print("🔑 Badges disponibles: 001, 002, 003")