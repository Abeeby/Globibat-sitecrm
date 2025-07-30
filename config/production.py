"""
Configuration pour l'environnement de production
"""
import os
from .base import BaseConfig

class ProductionConfig(BaseConfig):
    """Configuration de production"""
    
    DEBUG = False
    TESTING = False
    
    # Base de données MySQL/PostgreSQL pour Hostinger
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'mysql+pymysql://user:password@localhost/globibat_db'
    )
    
    # Sécurité
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY must be set in production!")
    
    # HTTPS obligatoire
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Protection CSRF
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None
    
    # Headers de sécurité
    SECURITY_HEADERS = {
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'SAMEORIGIN',
        'X-XSS-Protection': '1; mode=block',
        'Content-Security-Policy': "default-src 'self'"
    }
    
    # Cache Redis (si disponible)
    CACHE_TYPE = 'redis' if os.environ.get('REDIS_URL') else 'simple'
    CACHE_REDIS_URL = os.environ.get('REDIS_URL')
    
    # Logs
    LOG_TO_STDOUT = os.environ.get('LOG_TO_STDOUT', 'false').lower() in ['true', 'on', '1']
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    
    # Performance
    SEND_FILE_MAX_AGE_DEFAULT = 31536000  # 1 an pour les assets statiques
    
    # Monitoring (Sentry)
    SENTRY_DSN = os.environ.get('SENTRY_DSN')
    
    # Backup
    BACKUP_ENABLED = True
    BACKUP_SCHEDULE = '0 2 * * *'  # Tous les jours à 2h du matin