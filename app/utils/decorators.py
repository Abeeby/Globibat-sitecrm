"""
Décorateurs personnalisés pour l'application
"""
from functools import wraps
from flask import redirect, url_for, flash, request, jsonify
from flask_login import current_user

def admin_required(f):
    """Décorateur pour restreindre l'accès aux administrateurs"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login', next=request.url))
        
        if not current_user.role or current_user.role.name != 'Admin':
            flash('Accès réservé aux administrateurs.', 'error')
            return redirect(url_for('main.dashboard'))
        
        return f(*args, **kwargs)
    return decorated_function

def permission_required(permission):
    """Décorateur pour vérifier une permission spécifique"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('auth.login', next=request.url))
            
            if not current_user.has_permission(permission):
                flash('Vous n\'avez pas les permissions nécessaires.', 'error')
                return redirect(url_for('main.dashboard'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def api_key_required(f):
    """Décorateur pour l'authentification API"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        
        if not api_key:
            return jsonify({'error': 'API key required'}), 401
        
        # TODO: Vérifier l'API key dans la base de données
        # Pour l'instant, on accepte une clé de test
        if api_key != 'test-api-key':
            return jsonify({'error': 'Invalid API key'}), 401
        
        return f(*args, **kwargs)
    return decorated_function