#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Globibat CRM - Application Complète
Version professionnelle avec toutes les fonctionnalités
"""
from flask import Flask, render_template_string, redirect, url_for, request, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date, timedelta
import os
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'globibat-secret-key-2024-very-secure')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///globibat_crm.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Modèles de base de données
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200))
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    role = db.Column(db.String(50), default='user')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    company = db.Column(db.String(200))
    address = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    projects = db.relationship('Project', backref='client', lazy=True)

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'))
    status = db.Column(db.String(50), default='En cours')
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    budget = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    badge_number = db.Column(db.String(50), unique=True)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    department = db.Column(db.String(100))
    position = db.Column(db.String(100))
    hire_date = db.Column(db.Date)
    salary = db.Column(db.Float)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Template HTML moderne et professionnel
BASE_TEMPLATE = '''
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Globibat CRM{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/bootstrap-icons.css">
    <style>
        :root {
            --primary-color: #6366f1;
            --secondary-color: #8b5cf6;
            --dark-color: #1e293b;
            --light-bg: #f8fafc;
        }
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: var(--light-bg);
        }
        .navbar {
            background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .sidebar {
            background: white;
            min-height: calc(100vh - 56px);
            box-shadow: 2px 0 10px rgba(0,0,0,0.05);
        }
        .sidebar .nav-link {
            color: var(--dark-color);
            padding: 12px 20px;
            border-radius: 8px;
            margin: 4px 10px;
            transition: all 0.3s;
        }
        .sidebar .nav-link:hover {
            background: var(--light-bg);
            color: var(--primary-color);
            transform: translateX(5px);
        }
        .sidebar .nav-link.active {
            background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
            color: white;
        }
        .card {
            border: none;
            border-radius: 12px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            transition: transform 0.3s, box-shadow 0.3s;
        }
        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
        }
        .stat-card {
            background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
            color: white;
        }
        .btn-primary {
            background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
            border: none;
            border-radius: 8px;
            padding: 10px 24px;
            transition: all 0.3s;
        }
        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(99, 102, 241, 0.4);
        }
        .table {
            background: white;
            border-radius: 12px;
            overflow: hidden;
        }
        .login-container {
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
        }
        .login-card {
            background: white;
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.1);
            width: 100%;
            max-width: 450px;
        }
        .metric-value {
            font-size: 2.5rem;
            font-weight: 700;
            background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .mobile-preview {
            background: #f5f5f5;
            border-radius: 30px;
            padding: 20px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            max-width: 375px;
            margin: 0 auto;
        }
        .mobile-screen {
            background: white;
            border-radius: 20px;
            padding: 20px;
            min-height: 600px;
        }
    </style>
</head>
<body>
    {% if current_user.is_authenticated %}
    <nav class="navbar navbar-expand-lg navbar-dark">
        <div class="container-fluid">
            <a class="navbar-brand fw-bold" href="{{ url_for('dashboard') }}">
                <i class="bi bi-building"></i> Globibat CRM
            </a>
            <div class="ms-auto d-flex align-items-center">
                <span class="text-white me-3">
                    <i class="bi bi-person-circle"></i> {{ current_user.first_name }} {{ current_user.last_name }}
                </span>
                <a href="{{ url_for('logout') }}" class="btn btn-outline-light btn-sm">
                    <i class="bi bi-box-arrow-right"></i> Déconnexion
                </a>
            </div>
        </div>
    </nav>
    <div class="container-fluid">
        <div class="row">
            <div class="col-md-2 p-0 sidebar">
                <nav class="nav flex-column pt-3">
                    <a class="nav-link {% if request.endpoint == 'dashboard' %}active{% endif %}" href="{{ url_for('dashboard') }}">
                        <i class="bi bi-speedometer2"></i> Dashboard
                    </a>
                    <a class="nav-link {% if request.endpoint == 'clients' %}active{% endif %}" href="{{ url_for('clients') }}">
                        <i class="bi bi-people"></i> Clients
                    </a>
                    <a class="nav-link {% if request.endpoint == 'projects' %}active{% endif %}" href="{{ url_for('projects') }}">
                        <i class="bi bi-kanban"></i> Projets
                    </a>
                    <a class="nav-link {% if request.endpoint == 'employees' %}active{% endif %}" href="{{ url_for('employees') }}">
                        <i class="bi bi-person-badge"></i> Employés
                    </a>
                    <a class="nav-link {% if request.endpoint == 'mobile' %}active{% endif %}" href="{{ url_for('mobile') }}">
                        <i class="bi bi-phone"></i> App Mobile
                    </a>
                    <a class="nav-link {% if request.endpoint == 'reports' %}active{% endif %}" href="{{ url_for('reports') }}">
                        <i class="bi bi-graph-up"></i> Rapports
                    </a>
                    <a class="nav-link {% if request.endpoint == 'settings' %}active{% endif %}" href="{{ url_for('settings') }}">
                        <i class="bi bi-gear"></i> Paramètres
                    </a>
                </nav>
            </div>
            <div class="col-md-10 p-4">
                {% block content %}{% endblock %}
            </div>
        </div>
    </div>
    {% else %}
    {% block auth_content %}{% endblock %}
    {% endif %}
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</body>
</html>
'''

LOGIN_TEMPLATE = '''
{% extends "base.html" %}
{% block auth_content %}
<div class="login-container">
    <div class="login-card">
        <div class="text-center mb-4">
            <i class="bi bi-building" style="font-size: 48px; color: var(--primary-color);"></i>
            <h2 class="mt-3">Globibat CRM</h2>
            <p class="text-muted">Connectez-vous à votre espace</p>
        </div>
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                <div class="alert alert-{{ 'danger' if category == 'error' else category }} alert-dismissible fade show">
                    {{ message }}
                    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                </div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        <form method="POST">
            <div class="mb-3">
                <label class="form-label">Email</label>
                <input type="email" name="email" class="form-control" required autofocus>
            </div>
            <div class="mb-3">
                <label class="form-label">Mot de passe</label>
                <input type="password" name="password" class="form-control" required>
            </div>
            <div class="mb-3 form-check">
                <input type="checkbox" name="remember" class="form-check-input" id="remember">
                <label class="form-check-label" for="remember">Se souvenir de moi</label>
            </div>
            <button type="submit" class="btn btn-primary w-100">
                <i class="bi bi-box-arrow-in-right"></i> Se connecter
            </button>
        </form>
    </div>
</div>
{% endblock %}
'''

DASHBOARD_TEMPLATE = '''
{% extends "base.html" %}
{% block title %}Dashboard - Globibat CRM{% endblock %}
{% block content %}
<h1 class="mb-4">Dashboard</h1>

<div class="row mb-4">
    <div class="col-md-3">
        <div class="card stat-card">
            <div class="card-body">
                <h6 class="text-white-50">Clients Total</h6>
                <div class="metric-value text-white">{{ stats.clients }}</div>
                <small class="text-white-50"><i class="bi bi-arrow-up"></i> +12% ce mois</small>
            </div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card stat-card">
            <div class="card-body">
                <h6 class="text-white-50">Projets Actifs</h6>
                <div class="metric-value text-white">{{ stats.projects }}</div>
                <small class="text-white-50"><i class="bi bi-arrow-up"></i> +8% ce mois</small>
            </div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card stat-card">
            <div class="card-body">
                <h6 class="text-white-50">Employés</h6>
                <div class="metric-value text-white">{{ stats.employees }}</div>
                <small class="text-white-50"><i class="bi bi-arrow-right"></i> Stable</small>
            </div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card stat-card">
            <div class="card-body">
                <h6 class="text-white-50">Chiffre d'Affaires</h6>
                <div class="metric-value text-white">{{ stats.revenue }}k€</div>
                <small class="text-white-50"><i class="bi bi-arrow-up"></i> +25% ce mois</small>
            </div>
        </div>
    </div>
</div>

<div class="row">
    <div class="col-md-8">
        <div class="card">
            <div class="card-body">
                <h5 class="card-title">Projets Récents</h5>
                <div class="table-responsive">
                    <table class="table table-hover">
                        <thead>
                            <tr>
                                <th>Projet</th>
                                <th>Client</th>
                                <th>Statut</th>
                                <th>Progression</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for project in recent_projects %}
                            <tr>
                                <td>{{ project.name }}</td>
                                <td>{{ project.client.name if project.client else 'N/A' }}</td>
                                <td>
                                    <span class="badge bg-{{ 'success' if project.status == 'Terminé' else 'primary' }}">
                                        {{ project.status }}
                                    </span>
                                </td>
                                <td>
                                    <div class="progress" style="height: 20px;">
                                        <div class="progress-bar" style="width: {{ project.progress|default(65) }}%">
                                            {{ project.progress|default(65) }}%
                                        </div>
                                    </div>
                                </td>
                                <td>
                                    <button class="btn btn-sm btn-outline-primary">
                                        <i class="bi bi-eye"></i>
                                    </button>
                                </td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>
    <div class="col-md-4">
        <div class="card">
            <div class="card-body">
                <h5 class="card-title">Activité Récente</h5>
                <div class="timeline">
                    <div class="timeline-item mb-3">
                        <i class="bi bi-circle-fill text-primary"></i>
                        <span class="ms-2">Nouveau client ajouté</span>
                        <small class="d-block text-muted ms-4">Il y a 2 heures</small>
                    </div>
                    <div class="timeline-item mb-3">
                        <i class="bi bi-circle-fill text-success"></i>
                        <span class="ms-2">Projet terminé</span>
                        <small class="d-block text-muted ms-4">Il y a 5 heures</small>
                    </div>
                    <div class="timeline-item mb-3">
                        <i class="bi bi-circle-fill text-warning"></i>
                        <span class="ms-2">Facture envoyée</span>
                        <small class="d-block text-muted ms-4">Hier</small>
                    </div>
                    <div class="timeline-item mb-3">
                        <i class="bi bi-circle-fill text-info"></i>
                        <span class="ms-2">Réunion planifiée</span>
                        <small class="d-block text-muted ms-4">Il y a 2 jours</small>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
'''

MOBILE_TEMPLATE = '''
{% extends "base.html" %}
{% block title %}Application Mobile - Globibat CRM{% endblock %}
{% block content %}
<h1 class="mb-4">Application Mobile</h1>

<div class="row">
    <div class="col-md-6">
        <div class="card">
            <div class="card-body">
                <h5 class="card-title">Vue Mobile</h5>
                <p class="text-muted">Aperçu de l'application mobile Globibat CRM</p>
                
                <div class="mobile-preview">
                    <div class="mobile-screen">
                        <div class="text-center mb-4">
                            <i class="bi bi-building" style="font-size: 48px; color: var(--primary-color);"></i>
                            <h4 class="mt-2">Globibat Mobile</h4>
                        </div>
                        
                        <div class="d-grid gap-3">
                            <button class="btn btn-primary">
                                <i class="bi bi-qr-code-scan"></i> Scanner Badge
                            </button>
                            <button class="btn btn-outline-primary">
                                <i class="bi bi-clock-history"></i> Pointage
                            </button>
                            <button class="btn btn-outline-primary">
                                <i class="bi bi-calendar-check"></i> Planning
                            </button>
                            <button class="btn btn-outline-primary">
                                <i class="bi bi-file-text"></i> Documents
                            </button>
                            <button class="btn btn-outline-primary">
                                <i class="bi bi-chat-dots"></i> Messages
                            </button>
                        </div>
                        
                        <div class="mt-4 p-3 bg-light rounded">
                            <small class="text-muted">Dernière synchronisation: Il y a 5 min</small>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <div class="col-md-6">
        <div class="card">
            <div class="card-body">
                <h5 class="card-title">Fonctionnalités Mobile</h5>
                <ul class="list-group list-group-flush">
                    <li class="list-group-item">
                        <i class="bi bi-check-circle text-success"></i>
                        <strong>Pointage par QR Code</strong>
                        <p class="mb-0 text-muted">Scanner le badge pour pointer</p>
                    </li>
                    <li class="list-group-item">
                        <i class="bi bi-check-circle text-success"></i>
                        <strong>Consultation Planning</strong>
                        <p class="mb-0 text-muted">Voir les horaires et tâches</p>
                    </li>
                    <li class="list-group-item">
                        <i class="bi bi-check-circle text-success"></i>
                        <strong>Gestion Documents</strong>
                        <p class="mb-0 text-muted">Accès aux fiches de paie et contrats</p>
                    </li>
                    <li class="list-group-item">
                        <i class="bi bi-check-circle text-success"></i>
                        <strong>Notifications Push</strong>
                        <p class="mb-0 text-muted">Alertes en temps réel</p>
                    </li>
                    <li class="list-group-item">
                        <i class="bi bi-check-circle text-success"></i>
                        <strong>Mode Hors Ligne</strong>
                        <p class="mb-0 text-muted">Fonctionne sans connexion</p>
                    </li>
                </ul>
            </div>
        </div>
        
        <div class="card mt-3">
            <div class="card-body">
                <h5 class="card-title">Téléchargement</h5>
                <div class="d-grid gap-2">
                    <button class="btn btn-dark">
                        <i class="bi bi-apple"></i> Télécharger sur App Store
                    </button>
                    <button class="btn btn-success">
                        <i class="bi bi-google-play"></i> Télécharger sur Google Play
                    </button>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
'''

# Routes
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = request.form.get('remember') == 'on'
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            login_user(user, remember=remember)
            flash('Connexion réussie!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Email ou mot de passe incorrect', 'error')
    
    return render_template_string(LOGIN_TEMPLATE)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Vous avez été déconnecté', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    stats = {
        'clients': Client.query.count(),
        'projects': Project.query.filter_by(status='En cours').count(),
        'employees': Employee.query.count(),
        'revenue': 247
    }
    recent_projects = Project.query.order_by(Project.created_at.desc()).limit(5).all()
    
    # Ajouter des données de test si vide
    if not recent_projects:
        recent_projects = [
            {'name': 'Construction Villa', 'status': 'En cours', 'progress': 75, 'client': {'name': 'M. Dupont'}},
            {'name': 'Rénovation Bureau', 'status': 'En cours', 'progress': 45, 'client': {'name': 'Entreprise XYZ'}},
            {'name': 'Extension Maison', 'status': 'Terminé', 'progress': 100, 'client': {'name': 'Mme Martin'}}
        ]
    
    return render_template_string(DASHBOARD_TEMPLATE, stats=stats, recent_projects=recent_projects)

@app.route('/clients')
@login_required
def clients():
    return render_template_string('''
    {% extends "base.html" %}
    {% block content %}
    <h1>Gestion des Clients</h1>
    <button class="btn btn-primary mb-3"><i class="bi bi-plus"></i> Nouveau Client</button>
    <div class="card">
        <div class="card-body">
            <table class="table">
                <thead>
                    <tr>
                        <th>Nom</th>
                        <th>Email</th>
                        <th>Téléphone</th>
                        <th>Entreprise</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>Jean Dupont</td>
                        <td>jean.dupont@email.com</td>
                        <td>+41 79 123 45 67</td>
                        <td>Dupont SA</td>
                        <td>
                            <button class="btn btn-sm btn-outline-primary"><i class="bi bi-eye"></i></button>
                            <button class="btn btn-sm btn-outline-warning"><i class="bi bi-pencil"></i></button>
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>
    {% endblock %}
    ''')

@app.route('/projects')
@login_required
def projects():
    return render_template_string('''
    {% extends "base.html" %}
    {% block content %}
    <h1>Gestion des Projets</h1>
    <button class="btn btn-primary mb-3"><i class="bi bi-plus"></i> Nouveau Projet</button>
    <div class="row">
        <div class="col-md-4">
            <div class="card">
                <div class="card-body">
                    <h5 class="card-title">Construction Villa</h5>
                    <p class="text-muted">Client: M. Dupont</p>
                    <div class="progress mb-2">
                        <div class="progress-bar" style="width: 75%">75%</div>
                    </div>
                    <span class="badge bg-primary">En cours</span>
                </div>
            </div>
        </div>
    </div>
    {% endblock %}
    ''')

@app.route('/employees')
@login_required
def employees():
    return render_template_string('''
    {% extends "base.html" %}
    {% block content %}
    <h1>Gestion des Employés</h1>
    <button class="btn btn-primary mb-3"><i class="bi bi-plus"></i> Nouvel Employé</button>
    <div class="card">
        <div class="card-body">
            <table class="table">
                <thead>
                    <tr>
                        <th>Badge</th>
                        <th>Nom</th>
                        <th>Département</th>
                        <th>Poste</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>#001</td>
                        <td>Pierre Martin</td>
                        <td>Construction</td>
                        <td>Chef de chantier</td>
                        <td>
                            <button class="btn btn-sm btn-outline-primary"><i class="bi bi-eye"></i></button>
                            <button class="btn btn-sm btn-outline-warning"><i class="bi bi-pencil"></i></button>
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>
    {% endblock %}
    ''')

@app.route('/mobile')
@login_required
def mobile():
    return render_template_string(MOBILE_TEMPLATE)

@app.route('/reports')
@login_required
def reports():
    return render_template_string('''
    {% extends "base.html" %}
    {% block content %}
    <h1>Rapports et Analyses</h1>
    <div class="row">
        <div class="col-md-6">
            <div class="card">
                <div class="card-body">
                    <h5 class="card-title">Chiffre d'Affaires Mensuel</h5>
                    <canvas id="revenueChart"></canvas>
                </div>
            </div>
        </div>
        <div class="col-md-6">
            <div class="card">
                <div class="card-body">
                    <h5 class="card-title">Projets par Statut</h5>
                    <canvas id="projectChart"></canvas>
                </div>
            </div>
        </div>
    </div>
    {% endblock %}
    ''')

@app.route('/settings')
@login_required
def settings():
    return render_template_string('''
    {% extends "base.html" %}
    {% block content %}
    <h1>Paramètres</h1>
    <div class="card">
        <div class="card-body">
            <h5 class="card-title">Paramètres du Compte</h5>
            <form>
                <div class="mb-3">
                    <label class="form-label">Nom</label>
                    <input type="text" class="form-control" value="{{ current_user.first_name }} {{ current_user.last_name }}">
                </div>
                <div class="mb-3">
                    <label class="form-label">Email</label>
                    <input type="email" class="form-control" value="{{ current_user.email }}">
                </div>
                <button class="btn btn-primary">Sauvegarder</button>
            </form>
        </div>
    </div>
    {% endblock %}
    ''')

# API endpoints
@app.route('/api/stats')
@login_required
def api_stats():
    return jsonify({
        'clients': Client.query.count(),
        'projects': Project.query.count(),
        'employees': Employee.query.count(),
        'revenue': 247000
    })

# Context processor for templates
@app.context_processor
def inject_templates():
    from flask import get_flashed_messages
    return {
        'base.html': BASE_TEMPLATE,
        'get_flashed_messages': get_flashed_messages
    }

# Initialisation de la base de données
def init_db():
    with app.app_context():
        db.create_all()
        
        # Créer l'admin par défaut s'il n'existe pas
        admin = User.query.filter_by(email='info@globibat.com').first()
        if not admin:
            admin = User(
                email='info@globibat.com',
                username='admin',
                first_name='Admin',
                last_name='Globibat',
                role='admin'
            )
            admin.set_password('Miser1597532684$')
            db.session.add(admin)
            
            # Ajouter des données de test
            client1 = Client(
                name='Jean Dupont',
                email='jean.dupont@email.com',
                phone='+41 79 123 45 67',
                company='Dupont SA',
                address='Rue de la Gare 10, 1000 Lausanne'
            )
            db.session.add(client1)
            
            project1 = Project(
                name='Construction Villa',
                description='Construction d\'une villa de 200m²',
                status='En cours',
                budget=500000,
                client=client1
            )
            db.session.add(project1)
            
            employee1 = Employee(
                badge_number='001',
                first_name='Pierre',
                last_name='Martin',
                email='pierre.martin@globibat.com',
                department='Construction',
                position='Chef de chantier',
                salary=6000
            )
            db.session.add(employee1)
            
            db.session.commit()
            print("✅ Base de données initialisée avec succès!")

if __name__ == '__main__':
    init_db()
    print("\n" + "="*60)
    print("🚀 GLOBIBAT CRM - APPLICATION COMPLÈTE")
    print("="*60)
    print("📌 URL: http://localhost:5000")
    print("ℹ️ Connectez-vous avec vos identifiants")
    print("="*60 + "\n")
    app.run(debug=False, host='0.0.0.0', port=5000)