"""
Modèle User et système de rôles
"""
from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import pyotp

class Role(db.Model):
    """Rôles utilisateur"""
    __tablename__ = 'roles'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(200))
    permissions = db.Column(db.JSON, default=lambda: {})
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relations
    users = db.relationship('User', backref='role', lazy='dynamic')
    
    def __repr__(self):
        return f'<Role {self.name}>'
    
    @staticmethod
    def insert_roles():
        """Insérer les rôles par défaut"""
        roles = {
            'Admin': {
                'description': 'Administrateur système avec tous les droits',
                'permissions': ['all']
            },
            'Manager': {
                'description': 'Gestionnaire avec accès complet au CRM',
                'permissions': ['crm.view', 'crm.edit', 'crm.delete', 'reports.view', 'employees.manage']
            },
            'Employee': {
                'description': 'Employé avec accès limité',
                'permissions': ['crm.view', 'projects.view', 'attendance.self']
            },
            'Accountant': {
                'description': 'Comptable avec accès financier',
                'permissions': ['finance.view', 'finance.edit', 'reports.financial']
            }
        }
        
        for role_name, details in roles.items():
            role = Role.query.filter_by(name=role_name).first()
            if not role:
                role = Role(
                    name=role_name,
                    description=details['description'],
                    permissions=details['permissions']
                )
                db.session.add(role)
        db.session.commit()

class User(UserMixin, db.Model):
    """Modèle utilisateur principal"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256))
    
    # Informations personnelles
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    phone = db.Column(db.String(20))
    avatar = db.Column(db.String(200))
    
    # Sécurité
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)
    totp_secret = db.Column(db.String(32))
    is_2fa_enabled = db.Column(db.Boolean, default=False)
    
    # Rôle et permissions
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    
    # Dates
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Préférences
    language = db.Column(db.String(5), default='fr')
    timezone = db.Column(db.String(50), default='Europe/Zurich')
    notifications_enabled = db.Column(db.Boolean, default=True)
    
    # Relations
    employee = db.relationship('Employee', backref='user', uselist=False)
    created_projects = db.relationship('Project', foreign_keys='Project.created_by_id', backref='creator')
    assigned_tasks = db.relationship('ProjectTask', foreign_keys='ProjectTask.assigned_to_id', backref='assignee')
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    @property
    def full_name(self):
        """Nom complet de l'utilisateur"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username
    
    def set_password(self, password):
        """Définir le mot de passe"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Vérifier le mot de passe"""
        return check_password_hash(self.password_hash, password)
    
    def generate_totp_secret(self):
        """Générer un secret TOTP pour 2FA"""
        self.totp_secret = pyotp.random_base32()
        return self.totp_secret
    
    def get_totp_uri(self):
        """Obtenir l'URI pour le QR code 2FA"""
        return pyotp.totp.TOTP(self.totp_secret).provisioning_uri(
            name=self.email,
            issuer_name='Globibat CRM'
        )
    
    def verify_totp(self, token):
        """Vérifier le code TOTP"""
        if not self.totp_secret:
            return False
        totp = pyotp.TOTP(self.totp_secret)
        return totp.verify(token, valid_window=1)
    
    def has_permission(self, permission):
        """Vérifier si l'utilisateur a une permission"""
        if not self.role:
            return False
        if 'all' in self.role.permissions:
            return True
        return permission in self.role.permissions
    
    def update_last_login(self):
        """Mettre à jour la dernière connexion"""
        self.last_login = datetime.utcnow()
        db.session.commit()

@login_manager.user_loader
def load_user(user_id):
    """Charger l'utilisateur pour Flask-Login"""
    return User.query.get(int(user_id))