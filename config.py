import os
from datetime import timedelta

class Config:
    # Clé secrète - À changer en production !
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'votre-cle-secrete-tres-securisee-a-changer-en-production-2024'
    
    # Base de données
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///badgeage.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configuration des sessions
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)
    SESSION_COOKIE_SECURE = False  # Désactivé car pas de HTTPS pour l'instant
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Configuration de l'application
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max pour les uploads
    
    # Paramètres métier
    HEURE_ARRIVEE_MAX = "09:00"  # Après cette heure = retard matin
    HEURE_RETOUR_MAX = "14:00"   # Après cette heure = retard après-midi
    
    # Email (pour notifications futures)
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    
    # Paramètres de l'entreprise
    COMPANY_NAME = "Globibat"
    COMPANY_EMAIL = "contact@globibat.com"
    COMPANY_PHONE = "+33 1 23 45 67 89"
    COMPANY_URL = os.environ.get('COMPANY_URL', 'https://globibat.com')
    
    # Email RH pour rapports
    RH_EMAIL = os.environ.get('RH_EMAIL', 'rh@globibat.com') 