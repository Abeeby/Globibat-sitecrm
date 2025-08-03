"""
Initialisation des données de base pour le système
"""

from app import db
from app.models import (Role, ExpensePolicy, WorkTimeRegulation, 
                       Department, User, Employee)
from datetime import date
import random
import string

def initialize_base_data():
    """Initialiser les données de base nécessaires au fonctionnement"""
    
    # Créer les rôles de base
    roles = [
        {'code': 'admin', 'name': 'Administrateur', 'description': 'Accès complet au système'},
        {'code': 'hr', 'name': 'Ressources Humaines', 'description': 'Gestion du personnel et paie'},
        {'code': 'finance', 'name': 'Finance', 'description': 'Gestion financière et comptabilité'},
        {'code': 'manager', 'name': 'Manager', 'description': 'Gestion d\'équipe'},
        {'code': 'employee', 'name': 'Employé', 'description': 'Employé standard'}
    ]
    
    for role_data in roles:
        if not Role.query.filter_by(code=role_data['code']).first():
            role = Role(**role_data)
            db.session.add(role)
    
    # Créer les départements
    departments = [
        'Direction',
        'Administration',
        'Chantier',
        'Maçonnerie',
        'Électricité',
        'Plomberie',
        'Peinture',
        'Menuiserie',
        'Carrelage',
        'Commercial'
    ]
    
    for dept_name in departments:
        if not Department.query.filter_by(name=dept_name).first():
            dept = Department(name=dept_name, is_active=True)
            db.session.add(dept)
    
    # Créer les politiques de dépenses
    expense_policies = [
        {
            'name': 'Transport - Général',
            'category': 'transport',
            'daily_limit': 100,
            'monthly_limit': 1500,
            'per_expense_limit': 200,
            'requires_receipt': True,
            'requires_approval': True,
            'approval_threshold': 50
        },
        {
            'name': 'Repas - Chantier',
            'category': 'meals',
            'daily_limit': 40,
            'monthly_limit': 800,
            'per_expense_limit': 30,
            'requires_receipt': True,
            'requires_approval': False,
            'approval_threshold': 30
        },
        {
            'name': 'Hébergement - Déplacement',
            'category': 'accommodation',
            'daily_limit': 200,
            'monthly_limit': 2000,
            'per_expense_limit': 250,
            'requires_receipt': True,
            'requires_approval': True,
            'approval_threshold': 100
        },
        {
            'name': 'Fournitures bureau',
            'category': 'office_supplies',
            'daily_limit': 50,
            'monthly_limit': 500,
            'per_expense_limit': 100,
            'requires_receipt': True,
            'requires_approval': False,
            'approval_threshold': 50
        }
    ]
    
    for policy_data in expense_policies:
        if not ExpensePolicy.query.filter_by(name=policy_data['name']).first():
            policy = ExpensePolicy(**policy_data)
            db.session.add(policy)
    
    # Créer les règles de temps de travail
    work_regulations = [
        {
            'name': 'Règles standard - Bureau',
            'max_daily_hours': 10,
            'standard_daily_hours': 8,
            'max_weekly_hours': 45,  # 45h pour le personnel de bureau
            'standard_weekly_hours': 42,
            'break_after_hours': 5.5,
            'min_break_duration': 30,
            'min_daily_rest': 11,
            'min_weekly_rest': 35,
            'overtime_threshold': 8,
            'max_annual_overtime': 170,
            'overtime_rate': 1.25,
            'department': 'Administration',
            'is_active': True
        },
        {
            'name': 'Règles standard - Chantier',
            'max_daily_hours': 10,
            'standard_daily_hours': 8.5,
            'max_weekly_hours': 50,  # 50h pour le personnel de chantier
            'standard_weekly_hours': 45,
            'break_after_hours': 5.5,
            'min_break_duration': 30,
            'min_daily_rest': 11,
            'min_weekly_rest': 35,
            'overtime_threshold': 8.5,
            'max_annual_overtime': 170,
            'overtime_rate': 1.25,
            'department': 'Chantier',
            'is_active': True
        }
    ]
    
    for reg_data in work_regulations:
        if not WorkTimeRegulation.query.filter_by(name=reg_data['name']).first():
            regulation = WorkTimeRegulation(**reg_data)
            db.session.add(regulation)
    
    # Créer un admin par défaut si aucun n'existe
    if not User.query.filter_by(role='admin').first():
        admin = User(
            email='admin@globibat.ch',
            first_name='Admin',
            last_name='Système',
            role='admin',
            is_active=True
        )
        admin.set_password('Globibat2024!')  # Mot de passe par défaut à changer
        db.session.add(admin)
    
    # Créer des employés de test
    create_test_employees()
    
    # Valider toutes les modifications
    db.session.commit()
    
    print("Données de base initialisées avec succès!")

def create_test_employees():
    """Créer quelques employés de test pour le développement"""
    
    # Liste d'employés de test
    test_employees = [
        {
            'first_name': 'Jean',
            'last_name': 'Dupont',
            'email': 'jean.dupont@globibat.ch',
            'department': 'Maçonnerie',
            'position': 'Chef d\'équipe',
            'role': 'manager',
            'hourly_rate': 35.00
        },
        {
            'first_name': 'Marie',
            'last_name': 'Martin',
            'email': 'marie.martin@globibat.ch',
            'department': 'Administration',
            'position': 'Responsable RH',
            'role': 'hr',
            'base_salary': 6500.00
        },
        {
            'first_name': 'Pierre',
            'last_name': 'Bernard',
            'email': 'pierre.bernard@globibat.ch',
            'department': 'Chantier',
            'position': 'Maçon',
            'role': 'employee',
            'hourly_rate': 28.00
        },
        {
            'first_name': 'Sophie',
            'last_name': 'Dubois',
            'email': 'sophie.dubois@globibat.ch',
            'department': 'Administration',
            'position': 'Comptable',
            'role': 'finance',
            'base_salary': 5800.00
        },
        {
            'first_name': 'Luc',
            'last_name': 'Moreau',
            'email': 'luc.moreau@globibat.ch',
            'department': 'Électricité',
            'position': 'Électricien',
            'role': 'employee',
            'hourly_rate': 30.00
        }
    ]
    
    for emp_data in test_employees:
        # Vérifier si l'utilisateur existe déjà
        if not User.query.filter_by(email=emp_data['email']).first():
            # Créer l'utilisateur
            user = User(
                email=emp_data['email'],
                first_name=emp_data['first_name'],
                last_name=emp_data['last_name'],
                role=emp_data['role'],
                is_active=True
            )
            user.set_password('Password123!')  # Mot de passe par défaut
            db.session.add(user)
            db.session.flush()  # Pour obtenir l'ID
            
            # Créer l'employé
            employee = Employee(
                user_id=user.id,
                employee_code=generate_employee_code(),
                department=emp_data['department'],
                position=emp_data['position'],
                hire_date=date.today(),
                badge_number=generate_badge_number(),
                pin_code=generate_pin_hash('123456'),  # PIN par défaut
                vacation_days=25,
                remaining_vacation=25,
                is_active=True
            )
            
            # Ajouter salaire
            if 'hourly_rate' in emp_data:
                employee.hourly_rate = emp_data['hourly_rate']
            if 'base_salary' in emp_data:
                employee.base_salary = emp_data['base_salary']
            
            # Informations supplémentaires
            employee.address = f"Rue Example {random.randint(1, 100)}"
            employee.postal_code = f"{random.randint(1000, 1300)}"
            employee.city = "Nyon"
            employee.canton = "VD"
            employee.work_phone = f"021 {random.randint(100, 999)} {random.randint(10, 99)} {random.randint(10, 99)}"
            employee.work_email = emp_data['email']
            
            db.session.add(employee)

def generate_employee_code():
    """Générer un code employé unique"""
    while True:
        code = f"EMP{random.randint(1000, 9999)}"
        if not Employee.query.filter_by(employee_code=code).first():
            return code

def generate_badge_number():
    """Générer un numéro de badge unique"""
    while True:
        badge = ''.join(random.choices(string.digits, k=10))
        if not Employee.query.filter_by(badge_number=badge).first():
            return badge

def generate_pin_hash(pin):
    """Générer le hash d'un code PIN"""
    import hashlib
    return hashlib.sha256(pin.encode()).hexdigest()

if __name__ == '__main__':
    from app import create_app
    app = create_app()
    with app.app_context():
        initialize_base_data()