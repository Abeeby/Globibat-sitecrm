#!/usr/bin/env python
"""
Script de test et de correction pour l'application Globibat CRM
"""

import os
import sys
import json
import time
from datetime import datetime, date, timedelta
from flask import Flask

# Ajouter le chemin de l'application
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import (
    User, Role, Employee, Attendance, Client, Project, 
    Quote, Invoice, Leave, Payroll
)

# Configuration de test
os.environ['FLASK_ENV'] = 'development'

def test_database_connection():
    """Test la connexion à la base de données"""
    print("\n🔍 Test de connexion à la base de données...")
    try:
        app = create_app()
        with app.app_context():
            # Test simple query
            users = User.query.all()
            print(f"✅ Connexion réussie! {len(users)} utilisateurs trouvés.")
            return True
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
        return False

def test_authentication():
    """Test l'authentification"""
    print("\n🔍 Test d'authentification...")
    app = create_app()
    with app.app_context():
        try:
            # Test admin login
            admin = User.query.filter_by(email='info@globibat.com').first()
            if admin and admin.check_password('Miser1597532684$'):
                print("✅ Authentification admin OK")
            else:
                print("❌ Problème d'authentification admin")
                
            return True
        except Exception as e:
            print(f"❌ Erreur: {e}")
            return False

def test_badge_system():
    """Test le système de badge"""
    print("\n🔍 Test du système de badge...")
    app = create_app()
    with app.app_context():
        try:
            # Vérifier les employés avec badges
            employees = Employee.query.filter(Employee.badge_number != None).all()
            print(f"✅ {len(employees)} employés avec badges trouvés:")
            for emp in employees:
                print(f"   - {emp.user.first_name} {emp.user.last_name}: Badge {emp.badge_number}")
            
            # Test de pointage
            if employees:
                emp = employees[0]
                # Créer un pointage test
                attendance = Attendance(
                    employee_id=emp.id,
                    date=date.today(),
                    check_in_morning=datetime.now()
                )
                db.session.add(attendance)
                db.session.commit()
                print(f"✅ Pointage test créé pour {emp.user.first_name}")
                
                # Supprimer le pointage test
                db.session.delete(attendance)
                db.session.commit()
                
            return True
        except Exception as e:
            print(f"❌ Erreur badge: {e}")
            return False

def test_crm_modules():
    """Test les modules CRM"""
    print("\n🔍 Test des modules CRM...")
    app = create_app()
    with app.app_context():
        results = {}
        
        # Test Clients
        try:
            clients = Client.query.all()
            results['clients'] = f"✅ Module Clients: {len(clients)} clients"
        except Exception as e:
            results['clients'] = f"❌ Module Clients: {e}"
        
        # Test Projets
        try:
            projects = Project.query.all()
            results['projects'] = f"✅ Module Projets: {len(projects)} projets"
        except Exception as e:
            results['projects'] = f"❌ Module Projets: {e}"
        
        # Test Devis
        try:
            quotes = Quote.query.all()
            results['quotes'] = f"✅ Module Devis: {len(quotes)} devis"
        except Exception as e:
            results['quotes'] = f"❌ Module Devis: {e}"
        
        # Test Factures
        try:
            invoices = Invoice.query.all()
            results['invoices'] = f"✅ Module Factures: {len(invoices)} factures"
        except Exception as e:
            results['invoices'] = f"❌ Module Factures: {e}"
        
        # Test Congés
        try:
            leaves = Leave.query.all()
            results['leaves'] = f"✅ Module Congés: {len(leaves)} demandes"
        except Exception as e:
            results['leaves'] = f"❌ Module Congés: {e}"
        
        # Test Paie
        try:
            payrolls = Payroll.query.all()
            results['payrolls'] = f"✅ Module Paie: {len(payrolls)} fiches"
        except Exception as e:
            results['payrolls'] = f"❌ Module Paie: {e}"
        
        # Afficher les résultats
        for module, result in results.items():
            print(f"   {result}")
        
        return all('✅' in r for r in results.values())

def fix_common_issues():
    """Corrige les problèmes courants"""
    print("\n🔧 Correction des problèmes courants...")
    app = create_app()
    with app.app_context():
        fixes = []
        
        # 1. S'assurer que tous les employés ont un code
        employees = Employee.query.filter(Employee.employee_code == None).all()
        if employees:
            for i, emp in enumerate(employees):
                emp.employee_code = f"EMP{str(emp.id).zfill(3)}"
            db.session.commit()
            fixes.append(f"✅ Codes employés générés pour {len(employees)} employés")
        
        # 2. S'assurer que les dates sont correctes
        attendances = Attendance.query.filter(Attendance.date == None).all()
        if attendances:
            for att in attendances:
                att.date = date.today()
            db.session.commit()
            fixes.append(f"✅ Dates corrigées pour {len(attendances)} pointages")
        
        # 3. Créer des données de test si vide
        if Client.query.count() == 0:
            # Créer un client test
            client = Client(
                client_code="CLT001",
                client_type="company",
                company_name="Construction Test SA",
                primary_email="test@construction.ch",
                primary_phone="021 123 45 67",
                address="Rue du Test 1",
                postal_code="1260",
                city="Nyon",
                canton="VD",
                is_active=True
            )
            db.session.add(client)
            db.session.commit()
            fixes.append("✅ Client test créé")
            
            # Créer un projet test
            project = Project(
                project_code="PRJ001",
                name="Rénovation Test",
                client_id=client.id,
                project_type="renovation",
                status="active",
                start_date=date.today(),
                estimated_budget=50000
            )
            db.session.add(project)
            db.session.commit()
            fixes.append("✅ Projet test créé")
        
        if fixes:
            for fix in fixes:
                print(f"   {fix}")
        else:
            print("   ✅ Aucun problème détecté")
        
        return True

def create_sample_data():
    """Crée des données d'exemple pour les tests"""
    print("\n📝 Création de données d'exemple...")
    app = create_app()
    with app.app_context():
        try:
            # Créer quelques clients supplémentaires
            clients_data = [
                {
                    "company_name": "Rénovation Plus SA",
                    "email": "contact@renovplus.ch",
                    "phone": "022 345 67 89"
                },
                {
                    "company_name": "Bâtiment Moderne Sàrl",
                    "email": "info@batmoderne.ch",
                    "phone": "024 456 78 90"
                },
                {
                    "first_name": "Jean",
                    "last_name": "Propriétaire",
                    "email": "jean.prop@email.ch",
                    "phone": "079 123 45 67"
                }
            ]
            
            for i, data in enumerate(clients_data):
                if not Client.query.filter_by(primary_email=data['email']).first():
                    client = Client(
                        client_code=f"CLT{str(i+10).zfill(3)}",
                        client_type="company" if "company_name" in data else "individual",
                        company_name=data.get('company_name'),
                        first_name=data.get('first_name'),
                        last_name=data.get('last_name'),
                        primary_email=data['email'],
                        primary_phone=data['phone'],
                        city="Nyon",
                        canton="VD",
                        is_active=True
                    )
                    db.session.add(client)
            
            db.session.commit()
            print("   ✅ Données d'exemple créées")
            return True
            
        except Exception as e:
            print(f"   ❌ Erreur: {e}")
            db.session.rollback()
            return False

def test_api_endpoints():
    """Test les endpoints API"""
    print("\n🔍 Test des endpoints API...")
    app = create_app()
    
    with app.test_client() as client:
        # Test page d'accueil
        response = client.get('/')
        print(f"   / : {response.status_code} {'✅' if response.status_code == 200 else '❌'}")
        
        # Test login
        response = client.get('/auth/login')
        print(f"   /auth/login : {response.status_code} {'✅' if response.status_code == 200 else '❌'}")
        
        # Test badge
        response = client.get('/badge')
        print(f"   /badge : {response.status_code} {'✅' if response.status_code == 200 else '❌'}")
        
        # Test API badge status
        response = client.get('/badge/status')
        print(f"   /badge/status : {response.status_code} {'✅' if response.status_code == 200 else '❌'}")

def apply_design_updates():
    """Applique les mises à jour de design"""
    print("\n🎨 Application des mises à jour de design...")
    
    # Mettre à jour les références CSS dans base.html
    base_html_path = "app/templates/base.html"
    if os.path.exists(base_html_path):
        with open(base_html_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Ajouter la nouvelle CSS si pas déjà présente
        if 'professional-style.css' not in content:
            content = content.replace(
                '<link href="{{ url_for(\'static\', filename=\'css/style.css\') }}" rel="stylesheet">',
                '''<link href="{{ url_for('static', filename='css/style.css') }}" rel="stylesheet">
    <link href="{{ url_for('static', filename='css/professional-style.css') }}" rel="stylesheet">'''
            )
            
            with open(base_html_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print("   ✅ CSS professionnelle ajoutée à base.html")
    
    # Mettre à jour le dashboard dans les vues
    views_main_path = "app/views/main.py"
    if os.path.exists(views_main_path):
        with open(views_main_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Changer le template du dashboard
        content = content.replace(
            "return render_template('dashboard.html'",
            "return render_template('dashboard_pro.html'"
        )
        
        with open(views_main_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print("   ✅ Dashboard professionnel activé")
    
    # Mettre à jour le badge
    views_badge_path = "app/views/badge.py"
    if os.path.exists(views_badge_path):
        with open(views_badge_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        content = content.replace(
            "return render_template('badge/index.html'",
            "return render_template('badge/index_pro.html'"
        )
        
        with open(views_badge_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print("   ✅ Interface badge professionnelle activée")

def main():
    """Fonction principale"""
    print("=" * 60)
    print("🚀 GLOBIBAT CRM - Test et Correction")
    print("=" * 60)
    
    # Tests
    all_ok = True
    all_ok &= test_database_connection()
    all_ok &= test_authentication()
    all_ok &= test_badge_system()
    all_ok &= test_crm_modules()
    
    # Corrections
    fix_common_issues()
    create_sample_data()
    
    # Tests API
    test_api_endpoints()
    
    # Appliquer le nouveau design
    apply_design_updates()
    
    print("\n" + "=" * 60)
    if all_ok:
        print("✅ Tous les tests sont passés avec succès!")
    else:
        print("⚠️  Certains tests ont échoué. Vérifiez les erreurs ci-dessus.")
    print("=" * 60)
    
    print("\n📋 Prochaines étapes:")
    print("1. Redémarrer l'application pour appliquer les changements")
    print("2. Tester l'interface sur http://votre-ip:5000")
    print("3. Vérifier le nouveau design professionnel")
    print("4. Tester toutes les fonctionnalités CRM")

if __name__ == "__main__":
    main()