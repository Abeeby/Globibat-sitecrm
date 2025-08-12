"""
Vues modernes pour le nouveau design du CRM Globibat
"""
from flask import Blueprint, render_template, redirect, url_for, jsonify, request
from flask_login import login_required, current_user
from datetime import datetime, date, timedelta
from sqlalchemy import func

# Créer le blueprint pour les vues modernes
modern_bp = Blueprint('modern', __name__, url_prefix='/modern')

@modern_bp.route('/')
@modern_bp.route('/dashboard')
@login_required
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
@login_required
def chantiers():
    """Gestion des chantiers avec toutes les fonctionnalités BTP"""
    return render_template('chantiers_modern.html')

@modern_bp.route('/factures')
@login_required
def factures():
    """Module de gestion des factures"""
    return render_template('factures_modern.html')

@modern_bp.route('/employes')
@login_required
def employes():
    """Gestion des employés et RH"""
    return render_template('employes_modern.html')

@modern_bp.route('/clients')
@login_required
def clients():
    """Gestion des clients"""
    return render_template('clients_modern.html')

@modern_bp.route('/ressources')
@login_required
def ressources():
    """Gestion des ressources et matériel"""
    return render_template('ressources_modern.html')

@modern_bp.route('/securite')
@login_required
def securite():
    """Module sécurité et conformité"""
    return render_template('securite_modern.html')

@modern_bp.route('/communication')
@login_required
def communication():
    """Communication interne par chantier"""
    return render_template('communication_modern.html')

@modern_bp.route('/api/search')
@login_required
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
@login_required
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
@login_required
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
@login_required
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