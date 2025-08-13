"""
Vues modernes pour le nouveau design du CRM Globibat
"""
from flask import Blueprint, render_template, render_template_string, redirect, url_for, jsonify, request
from datetime import datetime, date, timedelta

# Flask-Login est optionnel
try:
    from flask_login import current_user
except ImportError:
    current_user = None

try:
    from sqlalchemy import func
except ImportError:
    func = None

# Créer le blueprint pour les vues modernes
modern_bp = Blueprint('modern', __name__, url_prefix='/modern')

@modern_bp.route('/')
@modern_bp.route('/dashboard')
def dashboard():
    """Dashboard moderne avec KPI et widgets"""
    # Statistiques pour le dashboard
    stats = {
        'active_employees': 42,
        'present_today': 38,
        'badges_today': 76,
        'anomalies': 3,
        'active_projects': 8,
        'unpaid_amount': 125430
    }
    
    # Badges récents (données de démonstration)
    recent_badges = []
    
    return render_template('dashboard_modern.html', stats=stats, recent_badges=recent_badges)

@modern_bp.route('/chantiers')
def chantiers():
    """Gestion des chantiers avec toutes les fonctionnalités BTP"""
    return render_template('chantiers_modern.html')

@modern_bp.route('/factures')
def factures():
    """Module de gestion des factures"""
    try:
        from app.models import Facture, Client, Chantier, db
        from datetime import datetime, timedelta
        
        # Récupérer toutes les factures
        factures = Facture.query.all()
        clients = Client.query.filter_by(actif=True).all()
        
        # Calculer les statistiques
        total_factures = len(factures)
        montant_total = sum(f.montant_ttc for f in factures)
        
        # Factures en attente et en retard
        today = datetime.now().date()
        en_attente = sum(f.montant_ttc for f in factures if f.statut == 'Envoyée')
        factures_retard = [f for f in factures if f.date_echeance and f.date_echeance < today and f.statut != 'Payée']
        en_retard = len(factures_retard)
        relances_count = len(factures_retard)
        
        # Ajouter le nombre de jours de retard pour chaque facture
        for facture in factures:
            if facture.date_echeance and facture.date_echeance < today and facture.statut != 'Payée':
                facture.jours_retard = (today - facture.date_echeance).days
            else:
                facture.jours_retard = 0
        
        # Filtre pour formater les montants
        def format_currency(value):
            if value is None:
                return "0.00 €"
            return f"{value:,.2f} €".replace(",", " ").replace(".", ",")
        
        # Filtre pour formater les dates
        def date_filter(value, format='%d/%m/%Y'):
            if value:
                return value.strftime(format)
            return '-'
        
        return render_template('factures_modern.html',
                             factures=factures,
                             clients=clients,
                             total_factures=total_factures,
                             montant_total=montant_total,
                             en_attente=en_attente,
                             en_retard=en_retard,
                             relances_count=relances_count,
                             format_currency=format_currency,
                             date=date_filter)
    except Exception as e:
        print(f"Erreur dans la vue factures: {e}")
        return render_template_string("""
        {% extends "base_modern.html" %}
        {% block title %}Factures{% endblock %}
        {% block page_title %}Gestion des Factures{% endblock %}
        {% block content %}
        <div class="alert alert-warning">
            <i class="ri-error-warning-line"></i> Module en cours de chargement...
        </div>
        {% endblock %}
        """)

@modern_bp.route('/employes')
def employes():
    """Gestion des employés et RH"""
    try:
        # Importer les modèles
        from app.models import Employe, StatutEmploye, Badge, TypeBadge
        
        # Récupérer tous les employés
        employes = Employe.query.all()
        
        # Calculer les statistiques
        total_employees = len(employes)
        active_employees = Employe.query.filter_by(statut=StatutEmploye.ACTIF).count()
        
        # Compter les présents aujourd'hui (ceux qui ont badgé en entrée)
        from datetime import datetime, date
        today = date.today()
        present_today = 0
        on_site = 0
        
        for emp in employes:
            # Vérifier le dernier badge de l'employé
            last_badge = emp.badges.order_by(Badge.timestamp.desc()).first()
            if last_badge and last_badge.timestamp.date() == today:
                if last_badge.type_badge == TypeBadge.ENTREE:
                    present_today += 1
                    if last_badge.chantier_id:
                        on_site += 1
        
        return render_template('employes_modern.html',
                             employes=employes,
                             total_employees=total_employees,
                             active_employees=active_employees,
                             present_today=present_today,
                             on_site=on_site)
    except Exception as e:
        print(f"Erreur dans la vue employés: {e}")
        # Fallback si pas de base de données
        return render_template_string("""
        {% extends "base_modern.html" %}
        {% block title %}Employés{% endblock %}
        {% block page_title %}Gestion des Employés{% endblock %}
        {% block page_description %}Gérez vos équipes et ressources humaines{% endblock %}
        {% block content %}
        <div class="alert alert-warning">
            <i class="ri-error-warning-line"></i> La base de données n'est pas encore configurée.
        </div>
        {% endblock %}
        """)

@modern_bp.route('/clients')
def clients():
    """Gestion des clients"""
    try:
        from app.models import Client, Chantier, Devis, StatutChantier
        
        # Récupérer tous les clients
        clients = Client.query.all()
        
        # Calculer les statistiques
        total_clients = len(clients)
        active_projects = Chantier.query.filter_by(statut=StatutChantier.EN_COURS).count()
        pending_quotes = Devis.query.filter_by(accepte=False).count()
        
        # Calculer le CA total
        total_ca = sum(client.chiffre_affaires for client in clients)
        
        # Créer un filtre pour formater les montants
        def format_currency(value):
            if value is None:
                return "0 €"
            return f"{value:,.2f} €".replace(",", " ").replace(".", ",")
        
        return render_template('clients_modern.html',
                             clients=clients,
                             total_clients=total_clients,
                             active_projects=active_projects,
                             pending_quotes=pending_quotes,
                             total_ca=total_ca,
                             format_currency=format_currency)
    except Exception as e:
        print(f"Erreur dans la vue clients: {e}")
        return render_template_string("""
        {% extends "base_modern.html" %}
        {% block title %}Clients{% endblock %}
        {% block page_title %}Gestion des Clients{% endblock %}
        {% block content %}
        <div class="alert alert-warning">
            <i class="ri-error-warning-line"></i> Erreur: {{ error }}
        </div>
        {% endblock %}
        """, error=str(e))

@modern_bp.route('/ressources')
def ressources():
    """Gestion des ressources et matériel"""
    return render_template_string("""
    {% extends "base_modern.html" %}
    {% block title %}Ressources{% endblock %}
    {% block page_title %}Gestion des Ressources{% endblock %}
    {% block page_description %}Gérez vos machines, outils et matériaux{% endblock %}
    {% block content %}
    <div class="card">
        <div class="card-header">
            <h3 class="card-title">Inventaire des ressources</h3>
            <button class="btn btn-primary">
                <i class="ri-add-line"></i> Ajouter ressource
            </button>
        </div>
        <div class="card-body">
            <p>Module de gestion des ressources en cours de développement...</p>
        </div>
    </div>
    {% endblock %}
    """)

@modern_bp.route('/securite')
def securite():
    """Module sécurité et conformité"""
    return render_template_string("""
    {% extends "base_modern.html" %}
    {% block title %}Sécurité{% endblock %}
    {% block page_title %}Sécurité & Conformité{% endblock %}
    {% block page_description %}Gérez la sécurité sur vos chantiers{% endblock %}
    {% block content %}
    <div class="card">
        <div class="card-header">
            <h3 class="card-title">Rapports de sécurité</h3>
            <button class="btn btn-primary">
                <i class="ri-shield-check-line"></i> Nouveau rapport
            </button>
        </div>
        <div class="card-body">
            <p>Module de sécurité en cours de développement...</p>
        </div>
    </div>
    {% endblock %}
    """)

@modern_bp.route('/communication')
def communication():
    """Communication interne par chantier"""
    return render_template_string("""
    {% extends "base_modern.html" %}
    {% block title %}Communication{% endblock %}
    {% block page_title %}Communication Interne{% endblock %}
    {% block page_description %}Chat et messages par chantier{% endblock %}
    {% block content %}
    <div class="card">
        <div class="card-header">
            <h3 class="card-title">Messages récents</h3>
            <button class="btn btn-primary">
                <i class="ri-message-3-line"></i> Nouveau message
            </button>
        </div>
        <div class="card-body">
            <p>Module de communication en cours de développement...</p>
        </div>
    </div>
    {% endblock %}
    """)

# Nouvelles routes pour rendre tous les liens fonctionnels
@modern_bp.route('/devis')
def devis():
    """Module de gestion des devis"""
    return render_template_string("""
    {% extends "base_modern.html" %}
    {% block title %}Devis{% endblock %}
    {% block page_title %}Gestion des Devis{% endblock %}
    {% block page_description %}Créer et gérer vos devis{% endblock %}
    {% block content %}
    <div class="card">
        <div class="card-header">
            <h3 class="card-title">Devis</h3>
            <button class="btn btn-primary">
                <i class="ri-add-line"></i> Nouveau devis
            </button>
        </div>
        <div class="card-body">
            <p>Module de gestion des devis en cours de développement...</p>
        </div>
    </div>
    {% endblock %}
    """)

@modern_bp.route('/leads')
def leads():
    """Gestion des leads/prospects"""
    return render_template_string("""
    {% extends "base_modern.html" %}
    {% block title %}Leads{% endblock %}
    {% block page_title %}Gestion des Leads{% endblock %}
    {% block page_description %}Suivez vos prospects et opportunités{% endblock %}
    {% block content %}
    <div class="card">
        <div class="card-header">
            <h3 class="card-title">Leads & Prospects</h3>
            <button class="btn btn-primary">
                <i class="ri-user-add-line"></i> Nouveau lead
            </button>
        </div>
        <div class="card-body">
            <p>Module de gestion des leads en cours de développement...</p>
        </div>
    </div>
    {% endblock %}
    """)

@modern_bp.route('/badges')
def badges():
    """Module de gestion des badges"""
    return render_template_string("""
    {% extends "base_modern.html" %}
    {% block title %}Badges{% endblock %}
    {% block page_title %}Gestion des Badges{% endblock %}
    {% block page_description %}Suivi des badges et présences{% endblock %}
    {% block content %}
    <div class="card">
        <div class="card-header">
            <h3 class="card-title">Badges du jour</h3>
            <button class="btn btn-primary">
                <i class="ri-qr-code-line"></i> Scanner badge
            </button>
        </div>
        <div class="card-body">
            <p>Module de gestion des badges en cours de développement...</p>
        </div>
    </div>
    {% endblock %}
    """)

@modern_bp.route('/carte')
def carte():
    """Carte des chantiers"""
    return render_template_string("""
    {% extends "base_modern.html" %}
    {% block title %}Carte{% endblock %}
    {% block page_title %}Carte des Chantiers{% endblock %}
    {% block page_description %}Visualisez tous vos chantiers sur la carte{% endblock %}
    {% block content %}
    <div class="card">
        <div class="card-body p-0">
            <div id="map" style="height: 600px; background: #f0f0f0; display: flex; align-items: center; justify-content: center;">
                <p>Carte interactive en cours de chargement...</p>
            </div>
        </div>
    </div>
    {% endblock %}
    """)

@modern_bp.route('/paie')
def paie():
    """Module de gestion de la paie"""
    return render_template_string("""
    {% extends "base_modern.html" %}
    {% block title %}Paie{% endblock %}
    {% block page_title %}Gestion de la Paie{% endblock %}
    {% block page_description %}Gérez les salaires et fiches de paie{% endblock %}
    {% block content %}
    <div class="card">
        <div class="card-header">
            <h3 class="card-title">Fiches de paie</h3>
            <button class="btn btn-primary">
                <i class="ri-file-add-line"></i> Générer fiches de paie
            </button>
        </div>
        <div class="card-body">
            <p>Module de gestion de la paie en cours de développement...</p>
        </div>
    </div>
    {% endblock %}
    """)

@modern_bp.route('/rapports')
def rapports():
    """Module de rapports et analyses"""
    return render_template_string("""
    {% extends "base_modern.html" %}
    {% block title %}Rapports{% endblock %}
    {% block page_title %}Rapports & Analyses{% endblock %}
    {% block page_description %}Tableaux de bord et analyses détaillées{% endblock %}
    {% block content %}
    <div class="card">
        <div class="card-header">
            <h3 class="card-title">Rapports disponibles</h3>
            <button class="btn btn-primary">
                <i class="ri-download-line"></i> Exporter
            </button>
        </div>
        <div class="card-body">
            <p>Module de rapports en cours de développement...</p>
        </div>
    </div>
    {% endblock %}
    """)

@modern_bp.route('/budgets')
def budgets():
    """Module de gestion des budgets"""
    return render_template_string("""
    {% extends "base_modern.html" %}
    {% block title %}Budgets{% endblock %}
    {% block page_title %}Gestion des Budgets{% endblock %}
    {% block page_description %}Suivez et gérez vos budgets par chantier{% endblock %}
    {% block content %}
    <div class="card">
        <div class="card-header">
            <h3 class="card-title">Budgets par chantier</h3>
            <button class="btn btn-primary">
                <i class="ri-add-line"></i> Nouveau budget
            </button>
        </div>
        <div class="card-body">
            <p>Module de gestion des budgets en cours de développement...</p>
        </div>
    </div>
    {% endblock %}
    """)

@modern_bp.route('/parametres')
def parametres():
    """Paramètres de l'application"""
    return render_template_string("""
    {% extends "base_modern.html" %}
    {% block title %}Paramètres{% endblock %}
    {% block page_title %}Paramètres{% endblock %}
    {% block page_description %}Configuration de l'application{% endblock %}
    {% block content %}
    <div class="card">
        <div class="card-header">
            <h3 class="card-title">Paramètres généraux</h3>
        </div>
        <div class="card-body">
            <p>Configuration en cours de développement...</p>
        </div>
    </div>
    {% endblock %}
    """)

@modern_bp.route('/utilisateurs')
def utilisateurs():
    """Gestion des utilisateurs"""
    return render_template_string("""
    {% extends "base_modern.html" %}
    {% block title %}Utilisateurs{% endblock %}
    {% block page_title %}Gestion des Utilisateurs{% endblock %}
    {% block page_description %}Gérez les comptes et permissions{% endblock %}
    {% block content %}
    <div class="card">
        <div class="card-header">
            <h3 class="card-title">Utilisateurs</h3>
            <button class="btn btn-primary">
                <i class="ri-user-add-line"></i> Nouvel utilisateur
            </button>
        </div>
        <div class="card-body">
            <p>Module de gestion des utilisateurs en cours de développement...</p>
        </div>
    </div>
    {% endblock %}
    """)

@modern_bp.route('/sauvegarde')
def sauvegarde():
    """Module de sauvegarde"""
    return render_template_string("""
    {% extends "base_modern.html" %}
    {% block title %}Sauvegarde{% endblock %}
    {% block page_title %}Sauvegarde & Restauration{% endblock %}
    {% block page_description %}Gérez vos sauvegardes{% endblock %}
    {% block content %}
    <div class="card">
        <div class="card-header">
            <h3 class="card-title">Sauvegardes</h3>
            <button class="btn btn-primary">
                <i class="ri-database-2-line"></i> Nouvelle sauvegarde
            </button>
        </div>
        <div class="card-body">
            <p>Module de sauvegarde en cours de développement...</p>
        </div>
    </div>
    {% endblock %}
    """)

@modern_bp.route('/api/search')
def search():
    """API de recherche globale"""
    query = request.args.get('q', '')
    results = {
        'chantiers': [],
        'clients': [],
        'employes': [],
        'factures': []
    }
    
    if len(query) > 2:
        # Ici vous pouvez implémenter la recherche dans la base de données
        # Pour la démo, on retourne des résultats statiques
        results = {
            'chantiers': [
                {'id': 1, 'name': 'Immeuble Les Jardins', 'location': 'Genève'},
                {'id': 2, 'name': 'Centre Commercial', 'location': 'Lausanne'}
            ],
            'clients': [
                {'id': 1, 'name': 'Client ABC SA', 'type': 'Entreprise'},
                {'id': 2, 'name': 'Immobilier XYZ', 'type': 'Promoteur'}
            ],
            'employes': [
                {'id': 1, 'name': 'Jean Dupont', 'role': 'Maçon'},
                {'id': 2, 'name': 'Pierre Martin', 'role': 'Chef de chantier'}
            ],
            'factures': [
                {'id': 1, 'number': 'FAC-2024-001', 'amount': 15430, 'status': 'paid'},
                {'id': 2, 'number': 'FAC-2024-002', 'amount': 42750, 'status': 'pending'}
            ]
        }
    
    return jsonify(results)

@modern_bp.route('/api/stats')
def api_stats():
    """API pour récupérer les statistiques en temps réel"""
    stats = {
        'timestamp': datetime.now().isoformat(),
        'kpi': {
            'active_employees': 42,
            'present_today': 38,
            'badges_today': 76,
            'anomalies': 3,
            'active_projects': 8,
            'unpaid_amount': 125430
        },
        'charts': {
            'project_activity': {
                'labels': ['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim'],
                'datasets': [
                    {
                        'label': 'Heures travaillées',
                        'data': [420, 450, 480, 460, 490, 200, 0]
                    },
                    {
                        'label': 'Employés présents',
                        'data': [38, 40, 42, 39, 41, 15, 0]
                    }
                ]
            },
            'budget_tracking': {
                'labels': ['Jan', 'Fév', 'Mars', 'Avril', 'Mai', 'Juin'],
                'planned': [200000, 400000, 800000, 1200000, 1800000, 2300000],
                'actual': [180000, 380000, 750000, 1100000, 1495000, None]
            }
        }
    }
    
    return jsonify(stats)

@modern_bp.route('/api/notifications')
def api_notifications():
    """API pour récupérer les notifications"""
    notifications = [
        {
            'id': 1,
            'type': 'success',
            'title': 'Nouveau badge enregistré',
            'message': 'Jean Dupont a badgé à 08:15',
            'time': 'Il y a 5 min',
            'read': False
        },
        {
            'id': 2,
            'type': 'warning',
            'title': 'Maintenance requise',
            'message': 'La pelleteuse #3 nécessite une révision',
            'time': 'Il y a 2h',
            'read': False
        },
        {
            'id': 3,
            'type': 'info',
            'title': 'Nouvelle facture',
            'message': 'Facture #2024-001 créée pour Client ABC',
            'time': 'Hier',
            'read': True
        }
    ]
    
    return jsonify(notifications)

@modern_bp.route('/api/chantiers/<int:id>')
def api_chantier_detail(id):
    """API pour récupérer les détails d'un chantier"""
    chantier = {
        'id': id,
        'name': 'Immeuble résidentiel Les Jardins',
        'location': 'Genève Centre',
        'status': 'active',
        'progress': 65,
        'budget': {
            'total': 2300000,
            'spent': 1495000,
            'remaining': 805000
        },
        'timeline': [
            {
                'date': '2024-02-15 14:30',
                'title': 'Coulage dalle 3ème étage terminé',
                'description': 'La dalle du 3ème étage a été coulée avec succès.',
                'images': ['image1.jpg', 'image2.jpg']
            },
            {
                'date': '2024-02-14 09:15',
                'title': 'Livraison matériaux',
                'description': 'Réception de 50 sacs de ciment et 200 parpaings.',
                'images': []
            }
        ],
        'checklist': {
            'phase1': {
                'name': 'Fondations',
                'progress': 100,
                'items': [
                    {'id': 1, 'label': 'Terrassement', 'completed': True},
                    {'id': 2, 'label': 'Coulage fondations', 'completed': True},
                    {'id': 3, 'label': 'Imperméabilisation', 'completed': True}
                ]
            },
            'phase2': {
                'name': 'Gros œuvre',
                'progress': 60,
                'items': [
                    {'id': 4, 'label': 'Murs porteurs RDC', 'completed': True},
                    {'id': 5, 'label': 'Dalle 1er étage', 'completed': True},
                    {'id': 6, 'label': 'Murs porteurs 1er étage', 'completed': False},
                    {'id': 7, 'label': 'Dalle 2ème étage', 'completed': False}
                ]
            }
        }
    }
    
    return jsonify(chantier)

# API Routes pour les Clients
@modern_bp.route('/api/clients', methods=['GET', 'POST'])
def api_clients():
    """API pour gérer les clients"""
    try:
        from app.models import Client, db
        
        if request.method == 'POST':
            data = request.get_json()
            
            # Créer un nouveau client
            client = Client(
                code_client=data.get('code_client'),
                raison_sociale=data.get('raison_sociale'),
                type_client=data.get('type_client'),
                siret=data.get('siret'),
                tva_intracommunautaire=data.get('tva_intracommunautaire'),
                adresse=data.get('adresse'),
                code_postal=data.get('code_postal'),
                ville=data.get('ville'),
                pays=data.get('pays', 'France'),
                telephone=data.get('telephone'),
                email=data.get('email'),
                contact_principal=data.get('contact_principal'),
                credit_limite=data.get('credit_limite'),
                conditions_paiement=data.get('conditions_paiement'),
                notes=data.get('notes'),
                actif=data.get('actif', True)
            )
            
            db.session.add(client)
            db.session.commit()
            
            return jsonify({'success': True, 'id': client.id})
        
        # GET - Récupérer tous les clients
        clients = Client.query.all()
        return jsonify([{
            'id': c.id,
            'code_client': c.code_client,
            'raison_sociale': c.raison_sociale,
            'type_client': c.type_client,
            'email': c.email,
            'telephone': c.telephone,
            'ville': c.ville,
            'actif': c.actif
        } for c in clients])
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

@modern_bp.route('/api/clients/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def api_client_detail(id):
    """API pour un client spécifique"""
    try:
        from app.models import Client, db
        
        client = Client.query.get_or_404(id)
        
        if request.method == 'GET':
            return jsonify({
                'id': client.id,
                'code_client': client.code_client,
                'raison_sociale': client.raison_sociale,
                'type_client': client.type_client,
                'siret': client.siret,
                'tva_intracommunautaire': client.tva_intracommunautaire,
                'adresse': client.adresse,
                'code_postal': client.code_postal,
                'ville': client.ville,
                'pays': client.pays,
                'telephone': client.telephone,
                'email': client.email,
                'contact_principal': client.contact_principal,
                'credit_limite': client.credit_limite,
                'conditions_paiement': client.conditions_paiement,
                'notes': client.notes,
                'actif': client.actif
            })
        
        elif request.method == 'PUT':
            data = request.get_json()
            
            # Mettre à jour les champs
            client.code_client = data.get('code_client', client.code_client)
            client.raison_sociale = data.get('raison_sociale', client.raison_sociale)
            client.type_client = data.get('type_client', client.type_client)
            client.siret = data.get('siret', client.siret)
            client.tva_intracommunautaire = data.get('tva_intracommunautaire', client.tva_intracommunautaire)
            client.adresse = data.get('adresse', client.adresse)
            client.code_postal = data.get('code_postal', client.code_postal)
            client.ville = data.get('ville', client.ville)
            client.pays = data.get('pays', client.pays)
            client.telephone = data.get('telephone', client.telephone)
            client.email = data.get('email', client.email)
            client.contact_principal = data.get('contact_principal', client.contact_principal)
            client.credit_limite = data.get('credit_limite', client.credit_limite)
            client.conditions_paiement = data.get('conditions_paiement', client.conditions_paiement)
            client.notes = data.get('notes', client.notes)
            client.actif = data.get('actif', client.actif)
            
            db.session.commit()
            return jsonify({'success': True})
        
        elif request.method == 'DELETE':
            # Vérifier s'il y a des chantiers liés
            if client.chantiers.count() > 0:
                return jsonify({
                    'success': False, 
                    'message': 'Impossible de supprimer ce client car il a des chantiers associés'
                }), 400
            
            db.session.delete(client)
            db.session.commit()
            return jsonify({'success': True})
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

@modern_bp.route('/api/clients/export')
def export_clients():
    """Exporter les clients en CSV"""
    try:
        from app.models import Client
        import csv
        from io import StringIO
        from flask import make_response
        
        # Créer le CSV
        si = StringIO()
        writer = csv.writer(si)
        
        # En-têtes
        writer.writerow(['Code', 'Raison sociale', 'Type', 'Contact', 'Téléphone', 'Email', 'Ville', 'CA'])
        
        # Données
        clients = Client.query.all()
        for client in clients:
            writer.writerow([
                client.code_client,
                client.raison_sociale,
                client.type_client,
                client.contact_principal,
                client.telephone,
                client.email,
                client.ville,
                client.chiffre_affaires
            ])
        
        # Créer la réponse
        output = make_response(si.getvalue())
        output.headers["Content-Disposition"] = "attachment; filename=clients.csv"
        output.headers["Content-type"] = "text/csv"
        return output
    
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# API Routes pour les Employés
@modern_bp.route('/api/employes', methods=['GET', 'POST'])
def api_employes():
    """API pour gérer les employés"""
    try:
        from app.models import Employe, StatutEmploye, db
        
        if request.method == 'POST':
            data = request.get_json() if request.is_json else request.form
            
            # Créer un nouvel employé
            employe = Employe(
                matricule=data.get('matricule'),
                nom=data.get('nom'),
                prenom=data.get('prenom'),
                telephone=data.get('telephone'),
                email=data.get('email'),
                adresse=data.get('adresse'),
                poste=data.get('poste'),
                departement=data.get('departement'),
                salaire_base=float(data.get('salaire_base', 0)),
                statut=StatutEmploye[data.get('statut', 'ACTIF').upper().replace(' ', '_')],
                permis_conduire=data.get('permis_conduire'),
                caces=data.get('caces')
            )
            
            db.session.add(employe)
            db.session.commit()
            
            return jsonify({'success': True, 'id': employe.id})
        
        # GET - Récupérer tous les employés
        employes = Employe.query.all()
        return jsonify([{
            'id': e.id,
            'matricule': e.matricule,
            'nom_complet': e.nom_complet,
            'poste': e.poste,
            'departement': e.departement,
            'statut': e.statut.value if e.statut else 'Actif'
        } for e in employes])
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

@modern_bp.route('/api/employes/<int:id>', methods=['GET', 'DELETE'])
def api_employe_detail(id):
    """API pour un employé spécifique"""
    try:
        from app.models import Employe, db
        
        employe = Employe.query.get_or_404(id)
        
        if request.method == 'GET':
            return jsonify({
                'id': employe.id,
                'matricule': employe.matricule,
                'nom': employe.nom,
                'prenom': employe.prenom,
                'telephone': employe.telephone,
                'email': employe.email,
                'poste': employe.poste,
                'departement': employe.departement,
                'statut': employe.statut.value if employe.statut else 'Actif'
            })
        
        elif request.method == 'DELETE':
            db.session.delete(employe)
            db.session.commit()
            return jsonify({'success': True})
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

# API Routes pour les Factures
@modern_bp.route('/api/factures', methods=['GET', 'POST'])
def api_factures():
    """API pour gérer les factures"""
    try:
        from app.models import Facture, Client, Chantier, db
        
        if request.method == 'POST':
            data = request.get_json()
            
            # Créer une nouvelle facture
            facture = Facture(
                numero_facture=data.get('numero_facture'),
                date_emission=datetime.strptime(data.get('date_emission'), '%Y-%m-%d').date(),
                date_echeance=datetime.strptime(data.get('date_echeance'), '%Y-%m-%d').date(),
                statut=data.get('statut', 'Brouillon'),
                client_id=data.get('client_id'),
                chantier_id=data.get('chantier_id'),
                conditions_paiement=data.get('conditions_paiement'),
                notes=data.get('notes')
            )
            
            # Calculer les montants à partir des lignes
            montant_ht = 0
            montant_tva = 0
            
            for ligne in data.get('lignes', []):
                quantite = float(ligne.get('quantite', 0))
                prix_unitaire = float(ligne.get('prix_unitaire', 0))
                taux_tva = float(ligne.get('taux_tva', 20))
                
                ligne_ht = quantite * prix_unitaire
                ligne_tva = ligne_ht * (taux_tva / 100)
                
                montant_ht += ligne_ht
                montant_tva += ligne_tva
            
            facture.montant_ht = montant_ht
            facture.montant_tva = montant_tva
            facture.montant_ttc = montant_ht + montant_tva
            
            db.session.add(facture)
            db.session.commit()
            
            return jsonify({'success': True, 'id': facture.id})
        
        # GET - Récupérer toutes les factures
        factures = Facture.query.all()
        return jsonify([{
            'id': f.id,
            'numero_facture': f.numero_facture,
            'date_emission': f.date_emission.isoformat() if f.date_emission else None,
            'client': f.client.raison_sociale if f.client else '',
            'montant_ttc': f.montant_ttc,
            'statut': f.statut
        } for f in factures])
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

@modern_bp.route('/api/factures/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def api_facture_detail(id):
    """API pour une facture spécifique"""
    try:
        from app.models import Facture, db
        
        facture = Facture.query.get_or_404(id)
        
        if request.method == 'GET':
            return jsonify({
                'id': facture.id,
                'numero_facture': facture.numero_facture,
                'date_emission': facture.date_emission.isoformat() if facture.date_emission else None,
                'date_echeance': facture.date_echeance.isoformat() if facture.date_echeance else None,
                'statut': facture.statut,
                'client_id': facture.client_id,
                'chantier_id': facture.chantier_id,
                'montant_ht': facture.montant_ht,
                'montant_tva': facture.montant_tva,
                'montant_ttc': facture.montant_ttc,
                'conditions_paiement': facture.conditions_paiement,
                'notes': facture.notes
            })
        
        elif request.method == 'PUT':
            data = request.get_json()
            
            # Mettre à jour les champs
            facture.numero_facture = data.get('numero_facture', facture.numero_facture)
            facture.statut = data.get('statut', facture.statut)
            facture.conditions_paiement = data.get('conditions_paiement', facture.conditions_paiement)
            facture.notes = data.get('notes', facture.notes)
            
            if data.get('date_emission'):
                facture.date_emission = datetime.strptime(data.get('date_emission'), '%Y-%m-%d').date()
            if data.get('date_echeance'):
                facture.date_echeance = datetime.strptime(data.get('date_echeance'), '%Y-%m-%d').date()
            
            db.session.commit()
            return jsonify({'success': True})
        
        elif request.method == 'DELETE':
            db.session.delete(facture)
            db.session.commit()
            return jsonify({'success': True})
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

@modern_bp.route('/api/factures/<int:id>/pdf')
def api_facture_pdf(id):
    """Générer le PDF d'une facture"""
    try:
        from app.models import Facture
        from io import BytesIO
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib import colors
        from reportlab.lib.units import inch
        from flask import send_file
        
        facture = Facture.query.get_or_404(id)
        
        # Créer le PDF
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        elements = []
        styles = getSampleStyleSheet()
        
        # En-tête
        elements.append(Paragraph(f"<b>FACTURE N° {facture.numero_facture}</b>", styles['Title']))
        elements.append(Spacer(1, 12))
        
        # Informations client
        if facture.client:
            client_info = f"""
            <b>Client:</b> {facture.client.raison_sociale}<br/>
            {facture.client.adresse}<br/>
            {facture.client.code_postal} {facture.client.ville}<br/>
            """
            elements.append(Paragraph(client_info, styles['Normal']))
            elements.append(Spacer(1, 12))
        
        # Dates
        date_info = f"""
        <b>Date d'émission:</b> {facture.date_emission.strftime('%d/%m/%Y') if facture.date_emission else '-'}<br/>
        <b>Date d'échéance:</b> {facture.date_echeance.strftime('%d/%m/%Y') if facture.date_echeance else '-'}<br/>
        """
        elements.append(Paragraph(date_info, styles['Normal']))
        elements.append(Spacer(1, 20))
        
        # Tableau des prestations (simplifié)
        data = [['Description', 'Montant HT', 'TVA', 'Montant TTC']]
        if facture.chantier:
            data.append([facture.chantier.nom, 
                        f"{facture.montant_ht:.2f} €",
                        f"{facture.montant_tva:.2f} €",
                        f"{facture.montant_ttc:.2f} €"])
        else:
            data.append(['Prestation', 
                        f"{facture.montant_ht:.2f} €",
                        f"{facture.montant_tva:.2f} €",
                        f"{facture.montant_ttc:.2f} €"])
        
        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 20))
        
        # Total
        total_text = f"<b>TOTAL TTC: {facture.montant_ttc:.2f} €</b>"
        elements.append(Paragraph(total_text, styles['Heading2']))
        
        # Conditions
        if facture.conditions_paiement:
            elements.append(Spacer(1, 20))
            elements.append(Paragraph(f"<b>Conditions de paiement:</b> {facture.conditions_paiement}", styles['Normal']))
        
        # Construire le PDF
        doc.build(elements)
        
        buffer.seek(0)
        return send_file(buffer, as_attachment=True, download_name=f"facture_{facture.numero_facture}.pdf", mimetype='application/pdf')
    
    except ImportError:
        # Si reportlab n'est pas installé, retourner une erreur
        return jsonify({'error': 'Génération PDF non disponible. Installez reportlab: pip install reportlab'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@modern_bp.route('/api/factures/<int:id>/paid', methods=['POST'])
def api_facture_mark_paid(id):
    """Marquer une facture comme payée"""
    try:
        from app.models import Facture, db
        
        facture = Facture.query.get_or_404(id)
        facture.statut = 'Payée'
        facture.date_paiement = datetime.now().date()
        
        db.session.commit()
        return jsonify({'success': True})
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

@modern_bp.route('/api/factures/<int:id>/send', methods=['POST'])
def api_facture_send(id):
    """Envoyer une facture par email"""
    try:
        from app.models import Facture
        
        facture = Facture.query.get_or_404(id)
        
        # Ici, vous pouvez implémenter l'envoi d'email
        # Pour l'instant, on simule juste
        facture.statut = 'Envoyée'
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Facture envoyée avec succès'})
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

@modern_bp.route('/api/factures/<int:id>/relance', methods=['POST'])
def api_facture_relance(id):
    """Envoyer une relance pour une facture"""
    try:
        from app.models import Facture, RelanceFacture, db
        
        facture = Facture.query.get_or_404(id)
        
        # Créer une relance
        relance = RelanceFacture(
            facture_id=facture.id,
            date_relance=datetime.now(),
            type_relance='Email',
            statut='Envoyée',
            notes=f'Relance automatique pour facture {facture.numero_facture}'
        )
        
        db.session.add(relance)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Relance envoyée avec succès'})
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

@modern_bp.route('/api/clients/<int:client_id>/chantiers')
def api_client_chantiers(client_id):
    """Récupérer les chantiers d'un client"""
    try:
        from app.models import Chantier
        
        chantiers = Chantier.query.filter_by(client_id=client_id).all()
        
        return jsonify([{
            'id': c.id,
            'nom': c.nom
        } for c in chantiers])
    
    except Exception as e:
        return jsonify([])

# Contexte global pour tous les templates
@modern_bp.context_processor
def inject_global_context():
    """Injecte les variables globales dans tous les templates"""
    return {
        'current_year': datetime.now().year,
        'company_name': 'Globibat SA',
        'employee_count': 42,
        'notification_count': 3
    }

# Gestion des erreurs
@modern_bp.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404_modern.html'), 404

@modern_bp.errorhandler(500)
def internal_error(error):
    return render_template('errors/500_modern.html'), 500