"""
Configuration de l'application Globibat CRM
"""
import os
from datetime import timedelta
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

class Config:
    """Configuration principale de l'application"""
    
    # Base de données
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///instance/globibat.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_recycle': 3600,
        'pool_pre_ping': True
    }
    
    # Sécurité
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-change-in-production-Gf8j2Kl9Mn3Qr5St7Uv1Wx4Yz6'
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None
    
    # Sessions
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'False').lower() == 'true'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    REMEMBER_COOKIE_DURATION = timedelta(days=30)
    
    # Uploads
    UPLOAD_FOLDER = 'app/static/uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx', 'xls', 'xlsx'}
    
    # Email
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True').lower() == 'true'
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL', 'False').lower() == 'true'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@globibat.com')
    
    # Entreprise
    COMPANY_NAME = "Globibat SA"
    COMPANY_EMAIL = "info@globibat.com"
    COMPANY_PHONE = "+41 79 123 45 67"
    COMPANY_ADDRESS = "Route de Lausanne 45, 1020 Renens, Suisse"
    COMPANY_WEBSITE = "https://www.globibat.ch"
    COMPANY_LOGO = "/static/images/logo.png"
    
    # Paramètres RH et Badge
    WORKING_HOURS = {
        'start_morning': '08:00',
        'end_morning': '12:00',
        'start_afternoon': '13:30',
        'end_afternoon': '17:30',
        'tolerance_minutes': 15
    }
    
    # Retards et absences
    LATE_ARRIVAL_MORNING = '09:00'
    LATE_ARRIVAL_AFTERNOON = '14:00'
    ABSENCE_THRESHOLD_HOURS = 4  # Moins de 4h = absence
    
    # Notifications
    ENABLE_EMAIL_NOTIFICATIONS = os.environ.get('ENABLE_EMAIL_NOTIFICATIONS', 'True').lower() == 'true'
    HR_EMAIL = os.environ.get('HR_EMAIL', 'rh@globibat.com')
    NOTIFICATION_RECIPIENTS = ['rh@globibat.com', 'direction@globibat.com']
    
    # API
    API_RATE_LIMIT = "100 per hour"
    API_KEY_HEADER = "X-API-Key"
    
    # Pagination
    ITEMS_PER_PAGE = 20
    MAX_ITEMS_PER_PAGE = 100
    
    # Localisation
    BABEL_DEFAULT_LOCALE = 'fr'
    BABEL_DEFAULT_TIMEZONE = 'Europe/Zurich'
    LANGUAGES = {
        'fr': 'Français',
        'en': 'English',
        'de': 'Deutsch',
        'it': 'Italiano'
    }
    
    # Cache
    CACHE_TYPE = 'simple'
    CACHE_DEFAULT_TIMEOUT = 300
    
    # Logs
    LOG_TO_STDOUT = os.environ.get('LOG_TO_STDOUT', 'False').lower() == 'true'
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    
    # Développement
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    TESTING = False
    
    # Sécurité supplémentaire
    SECURITY_PASSWORD_SALT = os.environ.get('SECURITY_PASSWORD_SALT', 'salt-change-in-production')
    SECURITY_PASSWORD_HASH = 'bcrypt'
    SECURITY_TRACKABLE = True
    SECURITY_LOGIN_WITHOUT_CONFIRMATION = True
    
    # 2FA
    ENABLE_2FA = os.environ.get('ENABLE_2FA', 'False').lower() == 'true'
    
    @staticmethod
    def init_app(app):
        """Initialisation spécifique de l'application"""
        pass

class DevelopmentConfig(Config):
    """Configuration pour le développement"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///instance/globibat_dev.db'
    
class TestingConfig(Config):
    """Configuration pour les tests"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    
class ProductionConfig(Config):
    """Configuration pour la production"""
    DEBUG = False
    SESSION_COOKIE_SECURE = True
    ENABLE_2FA = True
    
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        
        # Log vers stderr en production
        import logging
        from logging import StreamHandler
        file_handler = StreamHandler()
        file_handler.setLevel(logging.WARNING)
        app.logger.addHandler(file_handler)

# Dictionnaire de configurations
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

# Export de la configuration par défaut
Config = config[os.environ.get('FLASK_ENV', 'development')] 