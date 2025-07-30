"""
Configuration de base pour l'application Globibat CRM
"""
import os
from datetime import timedelta

class BaseConfig:
    """Configuration de base commune à tous les environnements"""
    
    # Chemin de base
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    
    # Clé secrète
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Base de données
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    
    # Session
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Upload
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB max
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'doc', 'docx', 'xls', 'xlsx'}
    
    # Email
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@globibat.ch')
    
    # Entreprise
    COMPANY_NAME = 'Globibat SA'
    COMPANY_ADDRESS = 'Route de Chancy 123'
    COMPANY_POSTAL_CODE = '1213'
    COMPANY_CITY = 'Petit-Lancy'
    COMPANY_CANTON = 'Genève'
    COMPANY_COUNTRY = 'Suisse'
    COMPANY_PHONE = '+41 22 792 XX XX'
    COMPANY_EMAIL = 'contact@globibat.ch'
    COMPANY_WEBSITE = 'https://www.globibat.ch'
    COMPANY_VAT = 'CHE-XXX.XXX.XXX TVA'
    COMPANY_IDE = 'CHE-XXX.XXX.XXX'
    COMPANY_IBAN = 'CH93 0076 2011 6238 5295 7'
    
    # SEO
    SEO_TITLE_SUFFIX = ' | Globibat - Construction Suisse Romande'
    SEO_DESCRIPTION = 'Globibat, entreprise de construction en Suisse romande. Spécialistes en construction neuve, rénovation et transformation à Genève, Lausanne, Fribourg.'
    SEO_KEYWORDS = 'construction suisse romande, entreprise batiment geneve, renovation lausanne, construction neuve fribourg, entrepreneur general suisse'
    
    # Horaires de travail
    WORK_HOURS = {
        'morning_start': '07:30',
        'morning_end': '12:00',
        'afternoon_start': '13:30',
        'afternoon_end': '17:30',
        'late_morning': '08:30',
        'late_afternoon': '14:00'
    }
    
    # Pagination
    ITEMS_PER_PAGE = 20
    
    # Cache
    CACHE_TYPE = 'simple'
    CACHE_DEFAULT_TIMEOUT = 300
    
    # API
    API_RATE_LIMIT = '100 per hour'
    
    # Langues supportées
    LANGUAGES = {
        'fr': 'Français',
        'de': 'Deutsch',
        'it': 'Italiano'
    }
    
    # Devise
    DEFAULT_CURRENCY = 'CHF'
    
    # TVA Suisse
    VAT_RATE = 7.7
    
    # Formats de date
    DATE_FORMAT = '%d.%m.%Y'
    DATETIME_FORMAT = '%d.%m.%Y %H:%M'