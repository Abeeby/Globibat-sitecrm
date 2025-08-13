"""
Application principale Globibat CRM avec système de badgage avancé
"""

from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from flask_migrate import Migrate
from flask_cors import CORS
from flask_mail import Mail
from config import Config
import logging
from logging.handlers import RotatingFileHandler
import os
from datetime import datetime

# Extensions Flask
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
mail = Mail()

def create_app(config_class=Config):
    """Factory pattern pour créer l'application"""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialiser les extensions
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    CORS(app)
    
    # Configuration du login manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Veuillez vous connecter pour accéder à cette page.'
    login_manager.login_message_category = 'info'
    
    # Importer et enregistrer les blueprints
    from app.views import (auth_bp, main_bp, crm_bp, admin_bp, api_bp, 
                          badge_bp, website_bp, badge_advanced_bp, 
                          dashboard_bp, payroll_bp, expense_bp, 
                          leave_bp, analytics_bp)
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(crm_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(badge_bp)
    app.register_blueprint(website_bp)
    app.register_blueprint(badge_advanced_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(payroll_bp)
    app.register_blueprint(expense_bp)
    app.register_blueprint(leave_bp)
    app.register_blueprint(analytics_bp)
    
    # Créer les dossiers nécessaires
    os.makedirs(app.config.get('UPLOAD_FOLDER', 'app/static/uploads'), exist_ok=True)
    os.makedirs('app/static/uploads/attendance', exist_ok=True)
    os.makedirs('app/static/uploads/expenses', exist_ok=True)
    os.makedirs('app/static/uploads/documents', exist_ok=True)
    os.makedirs('app/static/uploads/avatars', exist_ok=True)
    os.makedirs('instance', exist_ok=True)
    os.makedirs('logs', exist_ok=True)
    
    # Configuration des logs
    if not app.debug and not app.testing:
        file_handler = RotatingFileHandler(
            'logs/globibat.log',
            maxBytes=10240000,
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        
        app.logger.setLevel(logging.INFO)
        app.logger.info('Globibat CRM startup')
    
    # Contexte global pour les templates
    @app.context_processor
    def inject_globals():
        """Injecter des variables globales dans tous les templates"""
        return dict(
            company_name='Globibat SA',
            current_year=datetime.now().year,
            site_sections={
                'main': 'Site Internet',
                'crm': 'CRM',
                'admin': 'Administration',
                'employee': 'Espace Employé',
                'badge': 'Système Badge'
            }
        )
    
    # Filtres Jinja2 personnalisés
    @app.template_filter('datetime')
    def datetime_filter(value, format='%d/%m/%Y %H:%M'):
        """Formater une datetime"""
        if value is None:
            return ''
        if isinstance(value, str):
            return value
        return value.strftime(format)
    
    @app.template_filter('date')
    def date_filter(value, format='%d/%m/%Y'):
        """Formater une date"""
        if value is None:
            return ''
        if isinstance(value, str):
            return value
        return value.strftime(format)
    
    @app.template_filter('currency')
    def currency_filter(value):
        """Formater un montant en CHF"""
        if value is None:
            return 'CHF 0.00'
        return f'CHF {value:,.2f}'
    
    @app.template_filter('percentage')
    def percentage_filter(value):
        """Formater un pourcentage"""
        if value is None:
            return '0%'
        return f'{value:.1f}%'
    
    # Gestionnaires d'erreurs
    @app.errorhandler(403)
    def forbidden(error):
        return render_template('errors/403.html'), 403
    
    @app.errorhandler(404)
    def not_found(error):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500
    
    # Commandes CLI personnalisées
    @app.cli.command()
    def init_db():
        """Initialiser la base de données"""
        db.create_all()
        print("Base de données initialisée.")
    
    @app.cli.command()
    def reset_admin():
        """Réinitialiser le mot de passe admin"""
        from app.models.user import User
        
        admin = User.query.filter_by(email='info@globibat.com').first()
        if admin:
            admin.set_password('Miser1597532684!')
            db.session.commit()
            print("Mot de passe admin réinitialisé")
        else:
            print("Admin non trouvé. Exécutez d'abord init_database.py")
    
    @app.cli.command()
    def create_test_data():
        """Créer des données de test"""
        from init_database import init_database
        init_database()
        print("Données de test créées.")
    
    return app

# Callback pour Flask-Login
@login_manager.user_loader
def load_user(user_id):
    from app.models.user import User
    return User.query.get(int(user_id))