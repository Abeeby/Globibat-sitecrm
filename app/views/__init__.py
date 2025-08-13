"""
Blueprints pour l'organisation des vues
"""
# Temporairement désactivé - modules manquants
# from .auth import bp as auth_bp
# from .main import bp as main_bp
# from .crm import bp as crm_bp
# from .admin import bp as admin_bp
# from .api import bp as api_bp
# from .badge import badge_bp
# from .website import website_bp
# from .badge_advanced import badge_advanced_bp
# from .dashboard import dashboard_bp
# from .payroll import payroll_bp
# from .expense_management import expense_bp
# from .leave_management import leave_bp
# from .analytics import analytics_bp

# Import seulement modern_views qui fonctionne
try:
    from .modern_views import modern_bp
except ImportError:
    modern_bp = None

__all__ = ['modern_bp']