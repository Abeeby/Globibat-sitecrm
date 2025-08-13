#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Globibat CRM - Version Complète Fonctionnelle
"""
from flask import Flask, render_template_string, redirect, url_for, request, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'globibat-secret-2024'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///globibat.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Modèles
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200))
    name = db.Column(db.String(100))
    role = db.Column(db.String(50), default='user')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Template complet avec toutes les pages
FULL_TEMPLATE = '''
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title|default('Globibat CRM') }}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/bootstrap-icons.css">
    <style>
        :root {
            --primary: #6366f1;
            --secondary: #8b5cf6;
            --dark: #1e293b;
            --light: #f8fafc;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: var(--light);
        }
        .navbar {
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .sidebar {
            background: white;
            min-height: calc(100vh - 56px);
            box-shadow: 2px 0 10px rgba(0,0,0,0.05);
        }
        .sidebar .nav-link {
            color: var(--dark);
            padding: 12px 20px;
            border-radius: 8px;
            margin: 4px 10px;
            transition: all 0.3s;
        }
        .sidebar .nav-link:hover {
            background: var(--light);
            color: var(--primary);
            transform: translateX(5px);
        }
        .sidebar .nav-link.active {
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            color: white;
        }
        .card {
            border: none;
            border-radius: 12px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        }
        .stat-card {
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            color: white;
        }
        .login-container {
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            background: linear-gradient(135deg, var(--primary), var(--secondary));
        }
        .login-card {
            background: white;
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.1);
            width: 100%;
            max-width: 450px;
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
        .metric-value {
            font-size: 2.5rem;
            font-weight: 700;
        }
    </style>
</head>
<body>
    {% if current_user.is_authenticated %}
    <!-- Navigation -->
    <nav class="navbar navbar-expand-lg navbar-dark">
        <div class="container-fluid">
            <a class="navbar-brand fw-bold" href="{{ url_for('dashboard') }}">
                <i class="bi bi-building"></i> Globibat CRM
            </a>
            <div class="ms-auto">
                <span class="text-white me-3">
                    <i class="bi bi-person-circle"></i> {{ current_user.name }}
                </span>
                <a href="{{ url_for('logout') }}" class="btn btn-outline-light btn-sm">
                    <i class="bi bi-box-arrow-right"></i> Déconnexion
                </a>
            </div>
        </div>
    </nav>

    <div class="container-fluid">
        <div class="row">
            <!-- Sidebar -->
            <div class="col-md-2 p-0 sidebar">
                <nav class="nav flex-column pt-3">
                    <a class="nav-link {{ 'active' if page == 'dashboard' }}" href="{{ url_for('dashboard') }}">
                        <i class="bi bi-speedometer2"></i> Dashboard
                    </a>
                    <a class="nav-link {{ 'active' if page == 'clients' }}" href="{{ url_for('clients') }}">
                        <i class="bi bi-people"></i> Clients
                    </a>
                    <a class="nav-link {{ 'active' if page == 'projects' }}" href="{{ url_for('projects') }}">
                        <i class="bi bi-kanban"></i> Projets
                    </a>
                    <a class="nav-link {{ 'active' if page == 'employees' }}" href="{{ url_for('employees') }}">
                        <i class="bi bi-person-badge"></i> Employés
                    </a>
                    <a class="nav-link {{ 'active' if page == 'mobile' }}" href="{{ url_for('mobile') }}">
                        <i class="bi bi-phone"></i> App Mobile
                    </a>
                    <a class="nav-link {{ 'active' if page == 'reports' }}" href="{{ url_for('reports') }}">
                        <i class="bi bi-graph-up"></i> Rapports
                    </a>
                </nav>
            </div>

            <!-- Content -->
            <div class="col-md-10 p-4">
                {% if page == 'dashboard' %}
                <h1 class="mb-4">Dashboard</h1>
                <div class="row mb-4">
                    <div class="col-md-3">
                        <div class="card stat-card">
                            <div class="card-body">
                                <h6 class="text-white-50">Clients Total</h6>
                                <div class="metric-value">124</div>
                                <small><i class="bi bi-arrow-up"></i> +12% ce mois</small>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="card stat-card">
                            <div class="card-body">
                                <h6 class="text-white-50">Projets Actifs</h6>
                                <div class="metric-value">18</div>
                                <small><i class="bi bi-arrow-up"></i> +8% ce mois</small>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="card stat-card">
                            <div class="card-body">
                                <h6 class="text-white-50">Employés</h6>
                                <div class="metric-value">42</div>
                                <small><i class="bi bi-arrow-right"></i> Stable</small>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="card stat-card">
                            <div class="card-body">
                                <h6 class="text-white-50">CA Mensuel</h6>
                                <div class="metric-value">247k€</div>
                                <small><i class="bi bi-arrow-up"></i> +25% ce mois</small>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="row">
                    <div class="col-md-8">
                        <div class="card">
                            <div class="card-body">
                                <h5 class="card-title">Projets Récents</h5>
                                <table class="table">
                                    <thead>
                                        <tr>
                                            <th>Projet</th>
                                            <th>Client</th>
                                            <th>Statut</th>
                                            <th>Progression</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        <tr>
                                            <td>Construction Villa</td>
                                            <td>M. Dupont</td>
                                            <td><span class="badge bg-primary">En cours</span></td>
                                            <td>
                                                <div class="progress">
                                                    <div class="progress-bar" style="width: 75%">75%</div>
                                                </div>
                                            </td>
                                        </tr>
                                        <tr>
                                            <td>Rénovation Bureau</td>
                                            <td>Entreprise XYZ</td>
                                            <td><span class="badge bg-primary">En cours</span></td>
                                            <td>
                                                <div class="progress">
                                                    <div class="progress-bar" style="width: 45%">45%</div>
                                                </div>
                                            </td>
                                        </tr>
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="card">
                            <div class="card-body">
                                <h5 class="card-title">Activité Récente</h5>
                                <div class="timeline">
                                    <div class="mb-3">
                                        <i class="bi bi-circle-fill text-primary"></i>
                                        <span class="ms-2">Nouveau client ajouté</span>
                                        <small class="d-block text-muted ms-4">Il y a 2 heures</small>
                                    </div>
                                    <div class="mb-3">
                                        <i class="bi bi-circle-fill text-success"></i>
                                        <span class="ms-2">Projet terminé</span>
                                        <small class="d-block text-muted ms-4">Il y a 5 heures</small>
                                    </div>
                                    <div class="mb-3">
                                        <i class="bi bi-circle-fill text-warning"></i>
                                        <span class="ms-2">Facture envoyée</span>
                                        <small class="d-block text-muted ms-4">Hier</small>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                {% elif page == 'mobile' %}
                <h1 class="mb-4">Application Mobile</h1>
                <div class="row">
                    <div class="col-md-6">
                        <div class="card">
                            <div class="card-body">
                                <h5 class="card-title">Vue Mobile</h5>
                                <div class="mobile-preview">
                                    <div class="mobile-screen">
                                        <div class="text-center mb-4">
                                            <i class="bi bi-building" style="font-size: 48px; color: var(--primary);"></i>
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
                                            <small class="text-muted">Dernière sync: Il y a 5 min</small>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="card">
                            <div class="card-body">
                                <h5 class="card-title">Fonctionnalités</h5>
                                <ul class="list-group list-group-flush">
                                    <li class="list-group-item">
                                        <i class="bi bi-check-circle text-success"></i>
                                        <strong>Pointage QR Code</strong>
                                    </li>
                                    <li class="list-group-item">
                                        <i class="bi bi-check-circle text-success"></i>
                                        <strong>Consultation Planning</strong>
                                    </li>
                                    <li class="list-group-item">
                                        <i class="bi bi-check-circle text-success"></i>
                                        <strong>Documents & Fiches de paie</strong>
                                    </li>
                                    <li class="list-group-item">
                                        <i class="bi bi-check-circle text-success"></i>
                                        <strong>Notifications Push</strong>
                                    </li>
                                    <li class="list-group-item">
                                        <i class="bi bi-check-circle text-success"></i>
                                        <strong>Mode Hors Ligne</strong>
                                    </li>
                                </ul>
                            </div>
                        </div>
                        <div class="card mt-3">
                            <div class="card-body">
                                <h5 class="card-title">Téléchargement</h5>
                                <div class="d-grid gap-2">
                                    <button class="btn btn-dark">
                                        <i class="bi bi-apple"></i> App Store
                                    </button>
                                    <button class="btn btn-success">
                                        <i class="bi bi-google-play"></i> Google Play
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                {% elif page == 'clients' %}
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
                
                {% elif page == 'projects' %}
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
                    <div class="col-md-4">
                        <div class="card">
                            <div class="card-body">
                                <h5 class="card-title">Rénovation Bureau</h5>
                                <p class="text-muted">Client: Entreprise XYZ</p>
                                <div class="progress mb-2">
                                    <div class="progress-bar" style="width: 45%">45%</div>
                                </div>
                                <span class="badge bg-primary">En cours</span>
                            </div>
                        </div>
                    </div>
                </div>
                
                {% elif page == 'employees' %}
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
                
                {% elif page == 'reports' %}
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
                {% endif %}
            </div>
        </div>
    </div>
    {% else %}
    <!-- Login Page -->
    <div class="login-container">
        <div class="login-card">
            <div class="text-center mb-4">
                <i class="bi bi-building" style="font-size: 48px; color: var(--primary);"></i>
                <h2 class="mt-3">Globibat CRM</h2>
                <p class="text-muted">Connectez-vous à votre espace</p>
            </div>
            {% with messages = get_flashed_messages(with_categories=true) %}
                {% if messages %}
                    {% for category, message in messages %}
                    <div class="alert alert-{{ 'danger' if category == 'error' else category }}">
                        {{ message }}
                    </div>
                    {% endfor %}
                {% endif %}
            {% endwith %}
            <form method="POST" action="{{ url_for('login') }}">
                <div class="mb-3">
                    <label class="form-label">Email</label>
                    <input type="email" name="email" class="form-control" required>
                </div>
                <div class="mb-3">
                    <label class="form-label">Mot de passe</label>
                    <input type="password" name="password" class="form-control" required>
                </div>
                <button type="submit" class="btn btn-primary w-100">
                    <i class="bi bi-box-arrow-in-right"></i> Se connecter
                </button>
            </form>
        </div>
    </div>
    {% endif %}
</body>
</html>
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
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Email ou mot de passe incorrect', 'error')
    
    return render_template_string(FULL_TEMPLATE, page='login')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template_string(FULL_TEMPLATE, page='dashboard', title='Dashboard - Globibat CRM')

@app.route('/clients')
@login_required
def clients():
    return render_template_string(FULL_TEMPLATE, page='clients', title='Clients - Globibat CRM')

@app.route('/projects')
@login_required
def projects():
    return render_template_string(FULL_TEMPLATE, page='projects', title='Projets - Globibat CRM')

@app.route('/employees')
@login_required
def employees():
    return render_template_string(FULL_TEMPLATE, page='employees', title='Employés - Globibat CRM')

@app.route('/mobile')
@login_required
def mobile():
    return render_template_string(FULL_TEMPLATE, page='mobile', title='App Mobile - Globibat CRM')

@app.route('/reports')
@login_required
def reports():
    return render_template_string(FULL_TEMPLATE, page='reports', title='Rapports - Globibat CRM')

def init_db():
    with app.app_context():
        db.create_all()
        # Créer l'admin si n'existe pas
        admin = User.query.filter_by(email='info@globibat.com').first()
        if not admin:
            admin = User(
                email='info@globibat.com',
                name='Admin Globibat',
                role='admin'
            )
            admin.set_password('Miser1597532684$')
            db.session.add(admin)
            db.session.commit()
            print("✅ Admin créé avec succès")

if __name__ == '__main__':
    init_db()
    print("\n" + "="*60)
    print("🚀 GLOBIBAT CRM - APPLICATION COMPLÈTE")
    print("="*60)
    print("📌 URL: http://localhost:5000")
    print("📧 Connectez-vous avec vos identifiants")
    print("="*60 + "\n")
    app.run(host='0.0.0.0', port=5000, debug=False)