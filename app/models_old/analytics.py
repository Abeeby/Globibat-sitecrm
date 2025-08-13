"""
Modèles pour les statistiques et analyses
"""
from app import db
from datetime import datetime, date
from sqlalchemy import func

class ExpensePolicy(db.Model):
    """Modèle pour les politiques de dépenses"""
    __tablename__ = 'expense_policies'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    
    # Limites
    daily_limit = db.Column(db.Decimal(10, 2))
    monthly_limit = db.Column(db.Decimal(10, 2))
    per_expense_limit = db.Column(db.Decimal(10, 2))
    
    # Règles
    requires_receipt = db.Column(db.Boolean, default=True)
    requires_approval = db.Column(db.Boolean, default=True)
    approval_threshold = db.Column(db.Decimal(10, 2))  # Montant nécessitant approbation
    
    # Employés concernés
    applies_to_all = db.Column(db.Boolean, default=True)
    department = db.Column(db.String(50))  # Si pas tous
    
    # Statut
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<ExpensePolicy {self.name}>'


class WorkTimeRegulation(db.Model):
    """Modèle pour les réglementations du temps de travail (Suisse)"""
    __tablename__ = 'work_time_regulations'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    
    # Limites journalières
    max_daily_hours = db.Column(db.Float, default=10)  # Max heures/jour
    standard_daily_hours = db.Column(db.Float, default=8)
    
    # Limites hebdomadaires
    max_weekly_hours = db.Column(db.Float, default=50)  # Max heures/semaine
    standard_weekly_hours = db.Column(db.Float, default=42)
    
    # Pauses obligatoires
    break_after_hours = db.Column(db.Float, default=5.5)  # Pause après X heures
    min_break_duration = db.Column(db.Integer, default=30)  # Minutes
    
    # Repos
    min_daily_rest = db.Column(db.Integer, default=11)  # Heures entre deux jours
    min_weekly_rest = db.Column(db.Integer, default=35)  # Heures consécutives/semaine
    
    # Heures supplémentaires
    overtime_threshold = db.Column(db.Float, default=8)
    max_annual_overtime = db.Column(db.Float, default=170)
    overtime_rate = db.Column(db.Float, default=1.25)  # Taux horaire x1.25
    
    # Application
    department = db.Column(db.String(50))
    is_active = db.Column(db.Boolean, default=True)
    
    def __repr__(self):
        return f'<WorkTimeRegulation {self.name}>'


class EmployeeStatistics(db.Model):
    """Modèle pour les statistiques employés (calculées périodiquement)"""
    __tablename__ = 'employee_statistics'
    
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    
    # Période
    period_type = db.Column(db.String(20))  # daily, weekly, monthly, yearly
    period_start = db.Column(db.Date, nullable=False)
    period_end = db.Column(db.Date, nullable=False)
    
    # Temps de travail
    total_hours = db.Column(db.Float, default=0)
    regular_hours = db.Column(db.Float, default=0)
    overtime_hours = db.Column(db.Float, default=0)
    
    # Présence
    days_present = db.Column(db.Integer, default=0)
    days_absent = db.Column(db.Integer, default=0)
    late_arrivals = db.Column(db.Integer, default=0)
    
    # Congés
    vacation_taken = db.Column(db.Float, default=0)
    sick_days = db.Column(db.Float, default=0)
    
    # Dépenses
    total_expenses = db.Column(db.Decimal(10, 2), default=0)
    expenses_by_category = db.Column(db.JSON)  # {"Transport": 150.50, "Repas": 75.00}
    
    # Performance
    projects_worked = db.Column(db.Integer, default=0)
    productivity_score = db.Column(db.Float)  # Calculé selon critères
    
    # Calculs
    calculated_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relations
    employee = db.relationship('Employee', backref='statistics')
    
    def __repr__(self):
        return f'<EmployeeStatistics {self.employee_id} - {self.period_type}>'


class CompanyDashboard(db.Model):
    """Modèle pour le tableau de bord global de l'entreprise"""
    __tablename__ = 'company_dashboard'
    
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, unique=True)
    
    # Effectifs
    total_employees = db.Column(db.Integer, default=0)
    present_today = db.Column(db.Integer, default=0)
    absent_today = db.Column(db.Integer, default=0)
    on_leave = db.Column(db.Integer, default=0)
    
    # Heures
    total_hours_today = db.Column(db.Float, default=0)
    overtime_hours_today = db.Column(db.Float, default=0)
    
    # Coûts
    labor_cost_today = db.Column(db.Decimal(10, 2), default=0)
    expense_cost_today = db.Column(db.Decimal(10, 2), default=0)
    
    # Projets
    active_projects = db.Column(db.Integer, default=0)
    
    # Alertes
    compliance_alerts = db.Column(db.JSON)  # Liste des violations
    pending_approvals = db.Column(db.Integer, default=0)
    
    # Mise à jour
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<CompanyDashboard {self.date}>'


class AuditLog(db.Model):
    """Modèle pour l'audit trail"""
    __tablename__ = 'audit_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Utilisateur
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user_ip = db.Column(db.String(50))
    user_agent = db.Column(db.String(200))
    
    # Action
    action = db.Column(db.String(50), nullable=False)  # create, update, delete, approve, etc.
    model = db.Column(db.String(50))  # Employee, Expense, etc.
    model_id = db.Column(db.Integer)
    
    # Détails
    old_values = db.Column(db.JSON)
    new_values = db.Column(db.JSON)
    changes = db.Column(db.JSON)
    
    # Contexte
    description = db.Column(db.Text)
    category = db.Column(db.String(50))  # security, hr, finance, etc.
    severity = db.Column(db.String(20))  # info, warning, critical
    
    # Relations
    user = db.relationship('User', backref='audit_logs')
    
    def __repr__(self):
        return f'<AuditLog {self.action} - {self.timestamp}>'


class Notification(db.Model):
    """Modèle pour les notifications"""
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Destinataire
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Contenu
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(50))  # info, warning, error, success
    category = db.Column(db.String(50))  # expense, leave, payroll, etc.
    
    # Lien
    link_url = db.Column(db.String(200))
    link_text = db.Column(db.String(100))
    
    # Statut
    is_read = db.Column(db.Boolean, default=False)
    is_archived = db.Column(db.Boolean, default=False)
    
    # Dates
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    read_at = db.Column(db.DateTime)
    expires_at = db.Column(db.DateTime)
    
    # Priorité
    priority = db.Column(db.String(20), default='normal')  # low, normal, high, urgent
    
    # Relations
    user = db.relationship('User', backref='notifications')
    
    def __repr__(self):
        return f'<Notification {self.title} - {self.user_id}>'