"""
Configuration pour l'environnement de développement
"""
from .base import BaseConfig

class DevelopmentConfig(BaseConfig):
    """Configuration de développement"""
    
    DEBUG = True
    TESTING = False
    
    # Base de données SQLite locale
    SQLALCHEMY_DATABASE_URI = 'sqlite:///globibat_dev.db'
    SQLALCHEMY_ECHO = True  # Afficher les requêtes SQL
    
    # Session
    SESSION_COOKIE_SECURE = False  # Pas de HTTPS en dev
    
    # Cache
    CACHE_TYPE = 'simple'
    
    # Email (mode debug)
    MAIL_DEBUG = True
    MAIL_SUPPRESS_SEND = True  # Ne pas envoyer réellement les emails
    
    # Assets
    ASSETS_DEBUG = True