#!/bin/bash
# Script pour appliquer toutes les corrections sur le serveur

echo "🚀 Application des corrections Globibat CRM"
echo "========================================="

# Se connecter au serveur et exécuter les corrections
ssh root@148.230.105.25 << 'ENDSSH'

# 1. Télécharger et exécuter le script de correction des modèles
echo "📥 Téléchargement du script de correction..."
cat > /tmp/fix_models.py << 'EOF'
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

if __name__ == '__main__':
    print("🔧 Correction des modèles Globibat CRM\n")
    
    # Corriger les fichiers
    add_badge_number_to_employee()
    add_is_active_to_client()
    fix_crm_py()
    
    print("\n✅ Corrections des fichiers terminées!")
EOF

# Exécuter le script de correction
python3 /tmp/fix_models.py

# 2. Mettre à jour la base de données
echo -e "\n🔄 Mise à jour de la base de données..."
cd /var/www/globibat
export FLASK_ENV=development
export SECRET_KEY=dev-secret-key-for-testing
export DATABASE_URL=mysql://globibat_user:Globibat2024Secure!@localhost:3306/globibat_crm

# Ajouter les colonnes manquantes
./venv/bin/python << 'EOFPY'
from app import create_app, db
from sqlalchemy import text

app = create_app('development')
with app.app_context():
    try:
        # Ajouter badge_number à employees si nécessaire
        result = db.session.execute(text("SHOW COLUMNS FROM employees LIKE 'badge_number'"))
        if not result.fetchone():
            db.session.execute(text("ALTER TABLE employees ADD COLUMN badge_number VARCHAR(20) UNIQUE"))
            print("✅ Colonne badge_number ajoutée à employees")
        
        # Ajouter is_active à clients si nécessaire
        result = db.session.execute(text("SHOW COLUMNS FROM clients LIKE 'is_active'"))
        if not result.fetchone():
            db.session.execute(text("ALTER TABLE clients ADD COLUMN is_active BOOLEAN DEFAULT TRUE"))
            print("✅ Colonne is_active ajoutée à clients")
        
        # Ajouter les colonnes pour les 4 moments de badgeage
        result = db.session.execute(text("SHOW COLUMNS FROM attendances"))
        columns = [row[0] for row in result]
        
        if 'clock_in_afternoon' not in columns:
            db.session.execute(text("ALTER TABLE attendances ADD COLUMN clock_in_afternoon DATETIME"))
            print("✅ Colonne clock_in_afternoon ajoutée")
        
        if 'clock_out_final' not in columns:
            db.session.execute(text("ALTER TABLE attendances ADD COLUMN clock_out_final DATETIME"))
            print("✅ Colonne clock_out_final ajoutée")
        
        if 'date' not in columns:
            db.session.execute(text("ALTER TABLE attendances ADD COLUMN date DATE"))
            db.session.execute(text("UPDATE attendances SET date = DATE(clock_in) WHERE date IS NULL"))
            print("✅ Colonne date ajoutée")
        
        db.session.commit()
        print("✅ Base de données mise à jour")
    except Exception as e:
        print(f"⚠️ Erreur: {e}")
        db.session.rollback()
EOFPY

# 3. Créer les employés de test
echo -e "\n👥 Création des employés de test..."
./venv/bin/python << 'EOFPY2'
from app import create_app, db
from app.models import Employee, User
from datetime import date

app = create_app('development')
with app.app_context():
    # Données des employés
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
        # Vérifier si l'employé existe
        employee = Employee.query.filter_by(employee_code=emp_data['employee_code']).first()
        if not employee:
            # Créer le User
            user = User(
                username=emp_data['first_name'].lower() + '.' + emp_data['last_name'].lower(),
                email=emp_data['first_name'].lower() + '.' + emp_data['last_name'].lower() + '@globibat.com',
                first_name=emp_data['first_name'],
                last_name=emp_data['last_name'],
                is_active=True
            )
            user.set_password('password123')
            db.session.add(user)
            db.session.flush()
            
            # Créer l'employé
            emp_data['user_id'] = user.id
            employee = Employee(**emp_data)
            db.session.add(employee)
            print(f"✅ Employé créé: {emp_data['first_name']} {emp_data['last_name']} (Badge: {emp_data['badge_number']})")
        else:
            # Mettre à jour le badge si nécessaire
            if not employee.badge_number:
                employee.badge_number = emp_data['badge_number']
                print(f"✅ Badge ajouté pour: {employee.user.first_name} {employee.user.last_name}")
    
    db.session.commit()
    print("✅ Employés de test créés/mis à jour")
EOFPY2

# 4. Redémarrer l'application
echo -e "\n🔄 Redémarrage de l'application..."
pkill -f "python.*run.py" || true
cd /var/www/globibat
nohup ./venv/bin/python run.py > app.log 2>&1 &

echo -e "\n✅ Toutes les corrections ont été appliquées!"
echo "📱 Interface de badgeage : http://148.230.105.25:5000/badge"
echo "🔑 Badges de test : 001, 002, 003"
echo ""
echo "🕐 Système de badgeage avec 4 moments :"
echo "   - Arrivée matin (avant 10h)"
echo "   - Départ midi (10h-14h)"
echo "   - Retour midi (10h-14h)"
echo "   - Départ soir (après 14h)"

ENDSSH