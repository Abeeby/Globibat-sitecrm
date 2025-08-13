"""
Application Flask avec le nouveau design moderne du CRM Globibat
"""
from flask import Flask, render_template, redirect, url_for, Blueprint
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
import sys

# Flask-Login est optionnel
try:
    from flask_login import LoginManager, login_required
    HAS_LOGIN = True
except ImportError:
    HAS_LOGIN = False
    print("ℹ️ Flask-Login non installé, authentification désactivée")

# Ajouter le répertoire app au path Python
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

# Créer l'application Flask avec les bons chemins
app = Flask(__name__, 
            template_folder='app/templates',
            static_folder='app/static')

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-globibat-2024')
# Chemin absolu pour la base de données
db_path = os.path.join(os.path.dirname(__file__), 'instance', 'globibat.db')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', f'sqlite:///{db_path}')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Import et initialisation de la base de données
try:
    # Essayer d'importer les nouveaux modèles
    from app.models import db as models_db
    if hasattr(models_db, 'init_app'):
        models_db.init_app(app)
        db = models_db
    else:
        db = SQLAlchemy(app)
except (ImportError, AttributeError) as e:
    # Fallback si models.py n'existe pas ou a des erreurs
    db = SQLAlchemy(app)
    print(f"ℹ️ Utilisation de SQLAlchemy par défaut: {e}")

# Configurer Flask-Login si disponible
if HAS_LOGIN:
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

# Importer et enregistrer les blueprints
try:
    from app.views.modern_views import modern_bp
    app.register_blueprint(modern_bp)
except ImportError as e:
    print(f"⚠️ Erreur d'import des vues modernes: {e}")
    # Créer un blueprint minimal si l'import échoue
    from flask import Blueprint
    modern_bp = Blueprint('modern', __name__, url_prefix='/modern')
    
    @modern_bp.route('/')
    @modern_bp.route('/dashboard')
    def dashboard():
        return render_template('dashboard_modern.html', stats={}, recent_badges=[])
    
    @modern_bp.route('/chantiers')
    def chantiers():
        return render_template('chantiers_modern.html')
    
    app.register_blueprint(modern_bp)

# Importer les vues existantes si nécessaire
try:
    from app.views import auth, main, admin, crm, badge, website
    app.register_blueprint(auth.bp)
    app.register_blueprint(main.bp)
    app.register_blueprint(admin.bp)
    app.register_blueprint(crm.bp)
    app.register_blueprint(badge.bp)
    app.register_blueprint(website.bp)
except ImportError as e:
    print(f"ℹ️ Modules existants non trouvés (normal pour une nouvelle installation): {e}")

# Route racine qui redirige vers le dashboard moderne
@app.route('/')
def index():
    return redirect(url_for('modern.dashboard'))

# Gestionnaire de connexion pour Flask-Login
if HAS_LOGIN:
    @login_manager.user_loader
    def load_user(user_id):
        try:
            from app.models.user import User
            return User.query.get(int(user_id))
        except:
            # Si les modèles ne sont pas disponibles, utiliser un utilisateur factice
            class DummyUser:
                def __init__(self):
                    self.id = 1
                    self.username = 'admin'
                    self.is_authenticated = True
                    self.is_active = True
                    self.is_anonymous = False
                    self.role = 'admin'
                
                def get_id(self):
                    return str(self.id)
                
                def has_permission(self, permission):
                    return True
            
            return DummyUser()

# Contexte global pour tous les templates
@app.context_processor
def inject_global_context():
    """Injecte les variables globales dans tous les templates"""
    return {
        'current_year': datetime.now().year,
        'company_name': 'Globibat SA',
        'current_user': {
            'is_authenticated': True,
            'username': 'Admin',
            'role': 'admin'
        }
    }

# Pages d'erreur personnalisées
@app.errorhandler(404)
def not_found_error(error):
    from flask import render_template_string
    return render_template_string("""
    {% extends "base_modern.html" %}
    {% block title %}Page non trouvée{% endblock %}
    {% block page_title %}Erreur 404{% endblock %}
    {% block page_description %}La page que vous recherchez n'existe pas{% endblock %}
    {% block content %}
    <div class="card text-center">
        <div class="card-body py-5">
            <i class="ri-error-warning-line" style="font-size: 4rem; color: var(--warning);"></i>
            <h2 class="mt-3">Page non trouvée</h2>
            <p class="text-muted">La page que vous recherchez n'existe pas ou a été déplacée.</p>
            <a href="/modern/dashboard" class="btn btn-primary mt-3">
                <i class="ri-home-line"></i> Retour au tableau de bord
            </a>
        </div>
    </div>
    {% endblock %}
    """), 404

@app.errorhandler(500)
def internal_error(error):
    from flask import render_template_string
    return render_template_string("""
    {% extends "base_modern.html" %}
    {% block title %}Erreur serveur{% endblock %}
    {% block page_title %}Erreur 500{% endblock %}
    {% block page_description %}Une erreur est survenue{% endblock %}
    {% block content %}
    <div class="card text-center">
        <div class="card-body py-5">
            <i class="ri-error-warning-fill" style="font-size: 4rem; color: var(--danger);"></i>
            <h2 class="mt-3">Erreur serveur</h2>
            <p class="text-muted">Une erreur inattendue s'est produite. Veuillez réessayer plus tard.</p>
            <a href="/modern/dashboard" class="btn btn-primary mt-3">
                <i class="ri-home-line"></i> Retour au tableau de bord
            </a>
        </div>
    </div>
    {% endblock %}
    """), 500

# Initialisation de la base de données
def initialize_database():
    """Initialise la base de données et charge les données de démonstration"""
    with app.app_context():
        # Créer le dossier instance s'il n'existe pas
        instance_path = os.path.join(os.path.dirname(__file__), 'instance')
        if not os.path.exists(instance_path):
            os.makedirs(instance_path)
        
        # Créer les tables
        db.create_all()
        print("✅ Tables de base de données créées!")
        
        # Charger les données de démonstration
        try:
            from app.models import seed_demo_data
            seed_demo_data(app)
        except Exception as e:
            print(f"⚠️ Erreur lors du chargement des données de démonstration: {e}")

if __name__ == '__main__':
    initialize_database()
    print("\n" + "="*50)
    print("🚀 CRM Globibat - Design Moderne")
    print("="*50)
    print("📍 Accès local: http://localhost:5000")
    print("📍 Dashboard moderne: http://localhost:5000/modern/dashboard")
    print("📍 Gestion chantiers: http://localhost:5000/modern/chantiers")
    print("="*50 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)