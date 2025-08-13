"""
Configuration de l'application Globibat CRM
"""
import os
from datetime import timedelta

class Config:
    """Configuration principale de l'application"""
    
    # Base de données
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///instance/globibat.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Sécurité
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-change-in-production-Gf8j2Kl9Mn3Qr5St7Uv1Wx4Yz6'
    WTF_CSRF_ENABLED = True
    
    # Sessions
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Uploads
    UPLOAD_FOLDER = 'app/static/uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max
    
    # Email
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@globibat.com')
    
    # Entreprise
    COMPANY_NAME = "Globibat SA"
    COMPANY_EMAIL = "info@globibat.com"
    COMPANY_PHONE = "+41 79 123 45 67"
    
    # Debug
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'