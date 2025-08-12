"""
Application Flask avec le nouveau design moderne du CRM Globibat
"""
from flask import Flask, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_required
from datetime import datetime
import os

# Créer l'application Flask
app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-globibat-2024')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///globibat.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialiser les extensions
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

# Importer et enregistrer les blueprints
from app.views.modern_views import modern_bp
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
except ImportError:
    pass

# Route racine qui redirige vers le dashboard moderne
@app.route('/')
def index():
    return redirect(url_for('modern.dashboard'))

# Gestionnaire de connexion pour Flask-Login
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
    return render_template('errors/404_modern.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('errors/500_modern.html'), 500

# Initialisation de la base de données
def init_db():
    with app.app_context():
        db.create_all()
        print("Base de données initialisée avec succès!")

if __name__ == '__main__':
    init_db()
    print("\n" + "="*50)
    print("🚀 CRM Globibat - Design Moderne")
    print("="*50)
    print("📍 Accès local: http://localhost:5000")
    print("📍 Dashboard moderne: http://localhost:5000/modern/dashboard")
    print("📍 Gestion chantiers: http://localhost:5000/modern/chantiers")
    print("="*50 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)