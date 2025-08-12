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
    return render_template_string("""
    {% extends "base_modern.html" %}
    {% block title %}Factures{% endblock %}
    {% block page_title %}Gestion des Factures{% endblock %}
    {% block page_description %}Gérez vos factures et paiements{% endblock %}
    {% block content %}
    <div class="card">
        <div class="card-header">
            <h3 class="card-title">Liste des factures</h3>
            <button class="btn btn-primary">
                <i class="ri-file-add-line"></i> Nouvelle facture
            </button>
        </div>
        <div class="card-body">
            <p>Module de gestion des factures en cours de développement...</p>
        </div>
    </div>
    {% endblock %}
    """)

@modern_bp.route('/employes')
def employes():
    """Gestion des employés et RH"""
    return render_template_string("""
    {% extends "base_modern.html" %}
    {% block title %}Employés{% endblock %}
    {% block page_title %}Gestion des Employés{% endblock %}
    {% block page_description %}Gérez vos équipes et ressources humaines{% endblock %}
    {% block content %}
    <div class="card">
        <div class="card-header">
            <h3 class="card-title">Liste des employés</h3>
            <button class="btn btn-primary">
                <i class="ri-user-add-line"></i> Nouvel employé
            </button>
        </div>
        <div class="card-body">
            <p>Module de gestion des employés en cours de développement...</p>
        </div>
    </div>
    {% endblock %}
    """)

@modern_bp.route('/clients')
def clients():
    """Gestion des clients"""
    return render_template_string("""
    {% extends "base_modern.html" %}
    {% block title %}Clients{% endblock %}
    {% block page_title %}Gestion des Clients{% endblock %}
    {% block page_description %}Gérez votre portefeuille clients{% endblock %}
    {% block content %}
    <div class="card">
        <div class="card-header">
            <h3 class="card-title">Liste des clients</h3>
            <button class="btn btn-primary">
                <i class="ri-user-add-line"></i> Nouveau client
            </button>
        </div>
        <div class="card-body">
            <p>Module de gestion des clients en cours de développement...</p>
        </div>
    </div>
    {% endblock %}
    """)

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