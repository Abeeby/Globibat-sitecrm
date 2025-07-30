"""
Blueprint principal - Pages générales et dashboard
"""
from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from app.models import Project, Client, Invoice, Employee, Attendance
from app.utils.stats import get_dashboard_stats
from datetime import datetime, date, timedelta
from sqlalchemy import func

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    """Page d'accueil publique - Optimisée SEO pour construction Suisse romande"""
    # Si l'utilisateur est connecté, rediriger vers le dashboard
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    # Données SEO pour le secteur construction en Suisse romande
    seo_data = {
        'title': 'Globibat - Entreprise de Construction en Suisse Romande | Genève, Lausanne, Fribourg',
        'description': 'Globibat, votre partenaire de confiance pour tous vos projets de construction en Suisse romande. Spécialistes en construction neuve, rénovation et transformation.',
        'keywords': 'construction suisse romande, entreprise batiment geneve, renovation lausanne, construction neuve fribourg, entrepreneur general suisse',
        'services': [
            {
                'title': 'Construction Neuve',
                'description': 'Réalisation de villas, immeubles résidentiels et bâtiments commerciaux',
                'icon': 'building'
            },
            {
                'title': 'Rénovation',
                'description': 'Transformation et rénovation complète de bâtiments existants',
                'icon': 'tools'
            },
            {
                'title': 'Gros Œuvre',
                'description': 'Maçonnerie, béton armé, terrassement et fondations',
                'icon': 'foundation'
            },
            {
                'title': 'Second Œuvre',
                'description': 'Finitions, aménagements intérieurs et façades',
                'icon': 'paint-brush'
            }
        ],
        'regions': ['Genève', 'Lausanne', 'Fribourg', 'Neuchâtel', 'Sion', 'Yverdon'],
        'certifications': ['ISO 9001', 'Eco-bau', 'SQS', 'Minergie'],
        'stats': {
            'projects_completed': 150,
            'years_experience': 25,
            'satisfied_clients': 200,
            'employees': 50
        }
    }
    
    return render_template('index.html', seo_data=seo_data)

@bp.route('/dashboard')
@login_required
def dashboard():
    """Tableau de bord principal"""
    # Statistiques générales
    stats = {
        'projects': {
            'total': Project.query.count(),
            'active': Project.query.filter_by(status='in_progress').count(),
            'planning': Project.query.filter_by(status='planning').count(),
            'completed': Project.query.filter_by(status='completed').count()
        },
        'clients': {
            'total': Client.query.count(),
            'active': Client.query.filter_by(status='active').count(),
            'prospects': Client.query.filter_by(status='prospect').count()
        },
        'finance': {
            'invoices_pending': Invoice.query.filter(
                Invoice.status.in_(['sent', 'partial', 'overdue'])
            ).count(),
            'total_pending': db.session.query(
                func.sum(Invoice.total_amount - Invoice.paid_amount)
            ).filter(
                Invoice.status.in_(['sent', 'partial', 'overdue'])
            ).scalar() or 0
        },
        'employees': {
            'total': Employee.query.filter_by(is_active=True).count(),
            'present_today': Attendance.query.filter_by(
                date=date.today()
            ).count()
        }
    }
    
    # Projets récents
    recent_projects = Project.query.order_by(
        Project.created_at.desc()
    ).limit(5).all()
    
    # Factures en retard
    overdue_invoices = Invoice.query.filter_by(
        status='overdue'
    ).order_by(Invoice.due_date).limit(5).all()
    
    # Tâches à venir
    from app.models import ProjectTask
    upcoming_tasks = ProjectTask.query.filter(
        ProjectTask.status != 'completed',
        ProjectTask.due_date >= date.today(),
        ProjectTask.due_date <= date.today() + timedelta(days=7)
    ).order_by(ProjectTask.due_date).limit(10).all()
    
    # Rendez-vous du jour
    from app.models import Meeting
    today_meetings = Meeting.query.filter(
        func.date(Meeting.scheduled_at) == date.today(),
        Meeting.status != 'cancelled'
    ).order_by(Meeting.scheduled_at).all()
    
    return render_template('dashboard.html',
                         stats=stats,
                         recent_projects=recent_projects,
                         overdue_invoices=overdue_invoices,
                         upcoming_tasks=upcoming_tasks,
                         today_meetings=today_meetings)

@bp.route('/about')
def about():
    """Page À propos - SEO optimisée"""
    seo_data = {
        'title': 'À propos de Globibat - Entreprise de Construction Suisse',
        'description': 'Découvrez Globibat, entreprise de construction leader en Suisse romande depuis 25 ans. Notre expertise, nos valeurs et notre engagement qualité.'
    }
    return render_template('about.html', seo_data=seo_data)

@bp.route('/services')
def services():
    """Page Services - SEO optimisée"""
    services_data = {
        'construction': {
            'title': 'Construction Neuve',
            'description': 'Construction de villas individuelles, immeubles résidentiels et bâtiments commerciaux',
            'items': [
                'Villas clé en main',
                'Immeubles résidentiels',
                'Bâtiments industriels',
                'Locaux commerciaux'
            ]
        },
        'renovation': {
            'title': 'Rénovation & Transformation',
            'description': 'Rénovation complète ou partielle de bâtiments existants',
            'items': [
                'Rénovation énergétique',
                'Transformation de combles',
                'Agrandissement',
                'Mise aux normes'
            ]
        },
        'gros_oeuvre': {
            'title': 'Gros Œuvre',
            'description': 'Travaux de structure et fondations',
            'items': [
                'Terrassement',
                'Fondations',
                'Maçonnerie',
                'Béton armé'
            ]
        },
        'second_oeuvre': {
            'title': 'Second Œuvre',
            'description': 'Finitions et aménagements intérieurs',
            'items': [
                'Plâtrerie & Peinture',
                'Menuiserie',
                'Carrelage',
                'Façades'
            ]
        }
    }
    
    seo_data = {
        'title': 'Services de Construction - Globibat Suisse Romande',
        'description': 'Découvrez tous nos services de construction : gros œuvre, second œuvre, rénovation, transformation. Devis gratuit en Suisse romande.'
    }
    
    return render_template('services.html', services=services_data, seo_data=seo_data)

@bp.route('/contact')
def contact():
    """Page Contact - SEO optimisée"""
    contact_info = {
        'address': 'Route de Chancy 123, 1213 Petit-Lancy, Genève',
        'phone': '+41 22 792 XX XX',
        'email': 'contact@globibat.ch',
        'hours': {
            'weekdays': '7h30 - 17h30',
            'saturday': '8h00 - 12h00',
            'sunday': 'Fermé'
        },
        'regions': [
            {'name': 'Genève', 'coverage': 'Canton de Genève et France voisine'},
            {'name': 'Lausanne', 'coverage': 'Canton de Vaud'},
            {'name': 'Fribourg', 'coverage': 'Canton de Fribourg'},
            {'name': 'Neuchâtel', 'coverage': 'Canton de Neuchâtel'}
        ]
    }
    
    seo_data = {
        'title': 'Contact Globibat - Entreprise Construction Genève, Lausanne',
        'description': 'Contactez Globibat pour vos projets de construction en Suisse romande. Devis gratuit, conseil personnalisé. Bureaux à Genève.'
    }
    
    return render_template('contact.html', contact=contact_info, seo_data=seo_data)

@bp.route('/sitemap.xml')
def sitemap():
    """Sitemap XML pour SEO"""
    pages = []
    
    # Pages statiques
    for rule in current_app.url_map.iter_rules():
        if "GET" in rule.methods and not rule.endpoint.startswith('admin'):
            pages.append({
                'loc': url_for(rule.endpoint, _external=True),
                'changefreq': 'weekly',
                'priority': '0.8'
            })
    
    # Projets publics (portfolio)
    public_projects = Project.query.filter_by(
        status='completed'
    ).order_by(Project.completion_date.desc()).limit(20).all()
    
    for project in public_projects:
        pages.append({
            'loc': url_for('main.project_detail', 
                          project_id=project.id, _external=True),
            'changefreq': 'monthly',
            'priority': '0.6'
        })
    
    sitemap_xml = render_template('sitemap.xml', pages=pages)
    response = make_response(sitemap_xml)
    response.headers["Content-Type"] = "application/xml"
    
    return response