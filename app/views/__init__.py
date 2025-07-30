"""
Blueprints pour l'organisation des vues
"""
from .auth import bp as auth_bp
from .main import bp as main_bp
from .crm import bp as crm_bp
from .admin import bp as admin_bp
from .api import bp as api_bp

__all__ = ['auth_bp', 'main_bp', 'crm_bp', 'admin_bp', 'api_bp']