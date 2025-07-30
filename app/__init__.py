"""
Application principale Globibat CRM
CRM moderne pour entreprises de construction en Suisse romande
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_mail import Mail
from flask_wtf.csrf import CSRFProtect
import os

# Extensions Flask
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
mail = Mail()
csrf = CSRFProtect()

def create_app(config_name='production'):
    """Factory pattern pour créer l'application"""
    app = Flask(__name__)
    
    # Configuration
    if config_name == 'development':
        app.config.from_object('config.development.DevelopmentConfig')
    else:
        app.config.from_object('config.production.ProductionConfig')
    
    # Initialiser les extensions
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    csrf.init_app(app)
    
    # Configuration Login Manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Veuillez vous connecter pour accéder à cette page.'
    
    # Enregistrer les blueprints
    from app.views import auth, main, crm, admin, api
    app.register_blueprint(auth.bp)
    app.register_blueprint(main.bp)
    app.register_blueprint(crm.bp)
    app.register_blueprint(admin.bp)
    app.register_blueprint(api.bp)
    
    # Créer les dossiers nécessaires
    os.makedirs(app.instance_path, exist_ok=True)
    os.makedirs(os.path.join(app.static_folder, 'uploads'), exist_ok=True)
    
    return app