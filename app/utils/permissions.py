"""
Système de gestion des rôles et permissions
"""

from functools import wraps
from flask import redirect, url_for, flash, abort, request, jsonify
from flask_login import current_user
from app.models import User, Role, Employee

# Définition des rôles
ROLES = {
    'admin': {
        'name': 'Administrateur',
        'level': 100,
        'permissions': ['*']  # Toutes les permissions
    },
    'hr': {
        'name': 'Ressources Humaines',
        'level': 80,
        'permissions': [
            'employees.view', 'employees.create', 'employees.edit', 'employees.delete',
            'attendance.view', 'attendance.edit', 'attendance.reports',
            'leaves.view', 'leaves.approve', 'leaves.reports',
            'payroll.view', 'payroll.calculate', 'payroll.validate', 'payroll.export',
            'expenses.view', 'expenses.approve_final',
            'documents.view', 'documents.manage',
            'compliance.view', 'compliance.audit',
            'statistics.view', 'statistics.hr'
        ]
    },
    'finance': {
        'name': 'Finance',
        'level': 70,
        'permissions': [
            'expenses.view', 'expenses.approve_final', 'expenses.reports',
            'payroll.view', 'payroll.calculate', 'payroll.validate', 'payroll.export',
            'invoices.view', 'invoices.create', 'invoices.edit',
            'statistics.view', 'statistics.finance',
            'projects.view', 'projects.finance'
        ]
    },
    'manager': {
        'name': 'Manager',
        'level': 50,
        'permissions': [
            'employees.view_team', 'employees.edit_team',
            'attendance.view_team', 'attendance.approve_team',
            'leaves.view_team', 'leaves.approve_team',
            'expenses.view_team', 'expenses.approve_team',
            'projects.view', 'projects.manage_team',
            'statistics.view_team'
        ]
    },
    'employee': {
        'name': 'Employé',
        'level': 10,
        'permissions': [
            'profile.view', 'profile.edit',
            'attendance.view_own', 'attendance.badge',
            'leaves.view_own', 'leaves.request',
            'expenses.view_own', 'expenses.submit',
            'payroll.view_own',
            'documents.view_own'
        ]
    }
}

# Permissions spécifiques
PERMISSIONS = {
    # Employés
    'employees.view': 'Voir tous les employés',
    'employees.view_team': 'Voir les employés de son équipe',
    'employees.create': 'Créer des employés',
    'employees.edit': 'Modifier tous les employés',
    'employees.edit_team': 'Modifier les employés de son équipe',
    'employees.delete': 'Supprimer des employés',
    
    # Présences
    'attendance.view': 'Voir toutes les présences',
    'attendance.view_team': 'Voir les présences de son équipe',
    'attendance.view_own': 'Voir ses propres présences',
    'attendance.edit': 'Modifier les présences',
    'attendance.badge': 'Utiliser le système de badge',
    'attendance.reports': 'Générer des rapports de présence',
    
    # Congés
    'leaves.view': 'Voir tous les congés',
    'leaves.view_team': 'Voir les congés de son équipe',
    'leaves.view_own': 'Voir ses propres congés',
    'leaves.request': 'Demander des congés',
    'leaves.approve': 'Approuver tous les congés',
    'leaves.approve_team': 'Approuver les congés de son équipe',
    'leaves.reports': 'Générer des rapports de congés',
    
    # Paie
    'payroll.view': 'Voir toutes les fiches de paie',
    'payroll.view_own': 'Voir ses propres fiches de paie',
    'payroll.calculate': 'Calculer la paie',
    'payroll.validate': 'Valider la paie',
    'payroll.export': 'Exporter les données de paie',
    
    # Dépenses
    'expenses.view': 'Voir toutes les dépenses',
    'expenses.view_team': 'Voir les dépenses de son équipe',
    'expenses.view_own': 'Voir ses propres dépenses',
    'expenses.submit': 'Soumettre des dépenses',
    'expenses.approve_team': 'Approuver les dépenses de son équipe',
    'expenses.approve_final': 'Approuver finalement les dépenses',
    'expenses.reports': 'Générer des rapports de dépenses',
    
    # Documents
    'documents.view': 'Voir tous les documents',
    'documents.view_own': 'Voir ses propres documents',
    'documents.manage': 'Gérer tous les documents',
    
    # Projets
    'projects.view': 'Voir tous les projets',
    'projects.manage': 'Gérer tous les projets',
    'projects.manage_team': 'Gérer les projets de son équipe',
    'projects.finance': 'Voir les données financières des projets',
    
    # Statistiques
    'statistics.view': 'Voir toutes les statistiques',
    'statistics.view_team': 'Voir les statistiques de son équipe',
    'statistics.hr': 'Voir les statistiques RH',
    'statistics.finance': 'Voir les statistiques financières',
    
    # Conformité
    'compliance.view': 'Voir les données de conformité',
    'compliance.audit': 'Effectuer des audits',
    
    # Administration
    'admin.access': 'Accès à l\'administration',
    'admin.users': 'Gérer les utilisateurs',
    'admin.settings': 'Gérer les paramètres',
    'admin.backup': 'Gérer les sauvegardes'
}


class PermissionManager:
    """Gestionnaire de permissions"""
    
    @staticmethod
    def has_permission(user, permission):
        """Vérifier si un utilisateur a une permission"""
        if not user or not user.is_authenticated:
            return False
        
        # Admin a toutes les permissions
        if user.role == 'admin':
            return True
        
        # Vérifier la permission wildcard
        role_permissions = ROLES.get(user.role, {}).get('permissions', [])
        
        # Vérifier permission exacte
        if permission in role_permissions:
            return True
        
        # Vérifier permission wildcard (ex: employees.*)
        permission_parts = permission.split('.')
        for i in range(len(permission_parts)):
            wildcard = '.'.join(permission_parts[:i+1]) + '.*'
            if wildcard in role_permissions:
                return True
        
        return False
    
    @staticmethod
    def has_any_permission(user, permissions):
        """Vérifier si l'utilisateur a au moins une des permissions"""
        return any(PermissionManager.has_permission(user, p) for p in permissions)
    
    @staticmethod
    def has_all_permissions(user, permissions):
        """Vérifier si l'utilisateur a toutes les permissions"""
        return all(PermissionManager.has_permission(user, p) for p in permissions)
    
    @staticmethod
    def get_user_permissions(user):
        """Obtenir toutes les permissions d'un utilisateur"""
        if not user or not user.is_authenticated:
            return []
        
        if user.role == 'admin':
            return list(PERMISSIONS.keys())
        
        return ROLES.get(user.role, {}).get('permissions', [])
    
    @staticmethod
    def can_manage_employee(user, employee):
        """Vérifier si l'utilisateur peut gérer un employé"""
        if not user or not user.is_authenticated:
            return False
        
        # Admin et RH peuvent gérer tout le monde
        if user.role in ['admin', 'hr']:
            return True
        
        # Manager peut gérer son équipe
        if user.role == 'manager':
            # Vérifier si l'employé est dans le même département
            user_employee = Employee.query.filter_by(user_id=user.id).first()
            if user_employee and employee:
                return user_employee.department == employee.department
        
        # Employé peut voir ses propres infos
        if user.role == 'employee':
            user_employee = Employee.query.filter_by(user_id=user.id).first()
            return user_employee and user_employee.id == employee.id
        
        return False
    
    @staticmethod
    def filter_by_permission(query, model, user):
        """Filtrer une requête selon les permissions de l'utilisateur"""
        if not user or not user.is_authenticated:
            return query.filter(False)  # Aucun résultat
        
        # Admin voit tout
        if user.role == 'admin':
            return query
        
        # RH voit tout pour les modèles RH
        if user.role == 'hr' and model.__name__ in ['Employee', 'Attendance', 'Leave', 'Payroll']:
            return query
        
        # Finance voit tout pour les modèles financiers
        if user.role == 'finance' and model.__name__ in ['Expense', 'Invoice', 'Payment']:
            return query
        
        # Manager voit son département
        if user.role == 'manager':
            user_employee = Employee.query.filter_by(user_id=user.id).first()
            if user_employee and user_employee.department:
                if model.__name__ == 'Employee':
                    return query.filter_by(department=user_employee.department)
                elif hasattr(model, 'employee_id'):
                    # Joindre avec Employee pour filtrer par département
                    return query.join(Employee).filter(Employee.department == user_employee.department)
        
        # Employé voit seulement ses propres données
        if user.role == 'employee':
            user_employee = Employee.query.filter_by(user_id=user.id).first()
            if user_employee:
                if model.__name__ == 'Employee':
                    return query.filter_by(id=user_employee.id)
                elif hasattr(model, 'employee_id'):
                    return query.filter_by(employee_id=user_employee.id)
                elif hasattr(model, 'user_id'):
                    return query.filter_by(user_id=user.id)
        
        return query.filter(False)  # Aucun résultat par défaut


# Décorateurs
def require_permission(permission):
    """Décorateur pour exiger une permission"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                if request.is_json:
                    return jsonify({'error': 'Authentication required'}), 401
                flash('Veuillez vous connecter.', 'error')
                return redirect(url_for('auth.login'))
            
            if not PermissionManager.has_permission(current_user, permission):
                if request.is_json:
                    return jsonify({'error': 'Permission denied'}), 403
                flash('Vous n\'avez pas la permission d\'accéder à cette page.', 'error')
                abort(403)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def require_any_permission(*permissions):
    """Décorateur pour exiger au moins une permission parmi plusieurs"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                if request.is_json:
                    return jsonify({'error': 'Authentication required'}), 401
                flash('Veuillez vous connecter.', 'error')
                return redirect(url_for('auth.login'))
            
            if not PermissionManager.has_any_permission(current_user, permissions):
                if request.is_json:
                    return jsonify({'error': 'Permission denied'}), 403
                flash('Vous n\'avez pas la permission d\'accéder à cette page.', 'error')
                abort(403)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def require_role(role):
    """Décorateur pour exiger un rôle spécifique"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                if request.is_json:
                    return jsonify({'error': 'Authentication required'}), 401
                flash('Veuillez vous connecter.', 'error')
                return redirect(url_for('auth.login'))
            
            if current_user.role != role and current_user.role != 'admin':
                if request.is_json:
                    return jsonify({'error': 'Role required: ' + role}), 403
                flash(f'Cette page nécessite le rôle {ROLES.get(role, {}).get("name", role)}.', 'error')
                abort(403)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def require_min_role_level(min_level):
    """Décorateur pour exiger un niveau de rôle minimum"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                if request.is_json:
                    return jsonify({'error': 'Authentication required'}), 401
                flash('Veuillez vous connecter.', 'error')
                return redirect(url_for('auth.login'))
            
            user_level = ROLES.get(current_user.role, {}).get('level', 0)
            if user_level < min_level:
                if request.is_json:
                    return jsonify({'error': 'Insufficient role level'}), 403
                flash('Votre niveau d\'accès est insuffisant.', 'error')
                abort(403)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator