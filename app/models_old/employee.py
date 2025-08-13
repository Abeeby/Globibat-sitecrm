"""
Modèles pour la gestion des employés et RH
"""
from app import db
from datetime import datetime, date
from sqlalchemy import UniqueConstraint

class Employee(db.Model):
    """Modèle Employé"""
    __tablename__ = 'employees'
    
    id = db.Column(db.Integer, primary_key=True)
    employee_code = db.Column(db.String(20), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True)
    
    # Informations personnelles
    social_security = db.Column(db.String(30))
    birth_date = db.Column(db.Date)
    nationality = db.Column(db.String(50))
    marital_status = db.Column(db.String(20))
    
    # Informations professionnelles
    department = db.Column(db.String(50))
    position = db.Column(db.String(100))
    contract_type = db.Column(db.String(50))  # CDI, CDD, Intérim
    hire_date = db.Column(db.Date, default=date.today)
    end_date = db.Column(db.Date)  # Pour CDD
    
    # Salaire et avantages
    base_salary = db.Column(db.Decimal(10, 2))
    hourly_rate = db.Column(db.Decimal(10, 2))
    vacation_days = db.Column(db.Integer, default=25)  # Jours de congés annuels
    remaining_vacation = db.Column(db.Float, default=25)
    
    # Coordonnées professionnelles
    work_phone = db.Column(db.String(20))
    work_email = db.Column(db.String(120))
    emergency_contact = db.Column(db.String(200))
    emergency_phone = db.Column(db.String(20))
    
    # Adresse
    address = db.Column(db.String(200))
    postal_code = db.Column(db.String(10))
    city = db.Column(db.String(100))
    canton = db.Column(db.String(50))
    
    # Badge et authentification
    badge_number = db.Column(db.String(20), unique=True)
    qr_code = db.Column(db.String(100), unique=True)
    pin_code = db.Column(db.String(6))  # Code PIN à 6 chiffres
    face_data = db.Column(db.JSON)  # Données biométriques (future feature)
    
    # Statut
    is_active = db.Column(db.Boolean, default=True)
    
    # Relations
    attendances = db.relationship('Attendance', backref='employee', lazy='dynamic')
    leaves = db.relationship('Leave', backref='employee', lazy='dynamic')
    payrolls = db.relationship('Payroll', backref='employee', lazy='dynamic')
    assigned_projects = db.relationship('Project', secondary='project_employees', backref='employees')
    
    def __repr__(self):
        return f'<Employee {self.employee_code}>'
    
    @property
    def full_name(self):
        """Nom complet via l'utilisateur"""
        if self.user:
            return self.user.full_name
        return self.employee_code
    
    def calculate_vacation_balance(self):
        """Calculer le solde de congés"""
        approved_leaves = Leave.query.filter_by(
            employee_id=self.id,
            status='approved',
            leave_type='vacation'
        ).all()
        
        used_days = sum(leave.total_days for leave in approved_leaves)
        self.remaining_vacation = self.vacation_days - used_days
        return self.remaining_vacation


class Attendance(db.Model):
    """Modèle de pointage/présence"""
    __tablename__ = 'attendances'
    
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    date = db.Column(db.Date, nullable=False, default=date.today)
    
    # Horaires
    check_in_morning = db.Column(db.DateTime)
    check_out_lunch = db.Column(db.DateTime)
    check_in_afternoon = db.Column(db.DateTime)
    check_out_evening = db.Column(db.DateTime)
    
    # Heures travaillées
    total_hours = db.Column(db.Float, default=0)
    overtime_hours = db.Column(db.Float, default=0)
    
    # Statut
    is_late_morning = db.Column(db.Boolean, default=False)
    is_late_afternoon = db.Column(db.Boolean, default=False)
    is_absent = db.Column(db.Boolean, default=False)
    
    # Projet associé (pour facturation)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'))
    
    # Géolocalisation
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    location_name = db.Column(db.String(200))  # Ex: "Chantier Rue de la Gare"
    
    # Photos anti-fraude
    check_in_photo = db.Column(db.String(200))  # Chemin vers la photo
    check_out_photo = db.Column(db.String(200))
    
    # Méthode de pointage
    check_method = db.Column(db.String(20))  # badge, qr_code, pin, face
    device_info = db.Column(db.String(200))  # Info sur l'appareil utilisé
    
    # Notes
    notes = db.Column(db.Text)
    
    # Contrainte d'unicité
    __table_args__ = (UniqueConstraint('employee_id', 'date'),)
    
    def calculate_hours(self):
        """Calculer les heures travaillées"""
        total = 0
        
        # Matin
        if self.check_in_morning and self.check_out_lunch:
            morning = (self.check_out_lunch - self.check_in_morning).total_seconds() / 3600
            total += morning
        
        # Après-midi
        if self.check_in_afternoon and self.check_out_evening:
            afternoon = (self.check_out_evening - self.check_in_afternoon).total_seconds() / 3600
            total += afternoon
        
        self.total_hours = round(total, 2)
        
        # Heures supplémentaires (plus de 8h)
        if self.total_hours > 8:
            self.overtime_hours = round(self.total_hours - 8, 2)
        
        return self.total_hours


class Leave(db.Model):
    """Modèle de congés/absences"""
    __tablename__ = 'leaves'
    
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    
    # Type de congé
    leave_type = db.Column(db.String(50), nullable=False)  # vacation, sick, personal, maternity, etc.
    
    # Dates
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    total_days = db.Column(db.Float)
    
    # Statut
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected, cancelled
    
    # Validation
    requested_at = db.Column(db.DateTime, default=datetime.utcnow)
    approved_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    approved_at = db.Column(db.DateTime)
    
    # Justificatifs
    reason = db.Column(db.Text)
    document_path = db.Column(db.String(200))  # Certificat médical, etc.
    
    # Relations
    approved_by = db.relationship('User', foreign_keys=[approved_by_id])
    
    def __repr__(self):
        return f'<Leave {self.employee_id} - {self.leave_type}>'
    
    def calculate_days(self):
        """Calculer le nombre de jours"""
        if self.start_date and self.end_date:
            delta = (self.end_date - self.start_date).days + 1
            # Exclure les weekends
            weekdays = 0
            current = self.start_date
            while current <= self.end_date:
                if current.weekday() < 5:  # Lundi=0, Vendredi=4
                    weekdays += 1
                current += timedelta(days=1)
            self.total_days = weekdays
        return self.total_days


class Payroll(db.Model):
    """Modèle de paie"""
    __tablename__ = 'payrolls'
    
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    
    # Période
    month = db.Column(db.Integer, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    period_start = db.Column(db.Date)
    period_end = db.Column(db.Date)
    
    # Heures
    regular_hours = db.Column(db.Float, default=0)
    overtime_hours = db.Column(db.Float, default=0)
    
    # Salaire brut
    base_amount = db.Column(db.Decimal(10, 2))
    overtime_amount = db.Column(db.Decimal(10, 2))
    bonuses = db.Column(db.Decimal(10, 2), default=0)
    gross_salary = db.Column(db.Decimal(10, 2))
    
    # Déductions
    social_security = db.Column(db.Decimal(10, 2))  # AVS/AI/APG
    unemployment = db.Column(db.Decimal(10, 2))     # AC
    pension = db.Column(db.Decimal(10, 2))          # LPP
    accident_insurance = db.Column(db.Decimal(10, 2))  # LAA
    tax_deduction = db.Column(db.Decimal(10, 2))   # Impôt à la source
    other_deductions = db.Column(db.Decimal(10, 2), default=0)
    
    # Salaire net
    net_salary = db.Column(db.Decimal(10, 2))
    
    # Paiement
    payment_date = db.Column(db.Date)
    payment_method = db.Column(db.String(50))  # Virement, Chèque, etc.
    payment_reference = db.Column(db.String(100))
    
    # Statut
    status = db.Column(db.String(20), default='draft')  # draft, validated, paid
    
    # Documents
    payslip_path = db.Column(db.String(200))
    
    # Validation
    validated_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    validated_at = db.Column(db.DateTime)
    
    # Relations
    validated_by = db.relationship('User', foreign_keys=[validated_by_id])
    
    # Contrainte d'unicité
    __table_args__ = (UniqueConstraint('employee_id', 'month', 'year'),)
    
    def __repr__(self):
        return f'<Payroll {self.employee_id} - {self.month}/{self.year}>'
    
    def calculate_deductions(self):
        """Calculer les déductions sociales suisses"""
        if self.gross_salary:
            # Taux approximatifs pour la Suisse
            self.social_security = self.gross_salary * 0.0525  # AVS/AI/APG
            self.unemployment = self.gross_salary * 0.011     # AC
            self.pension = self.gross_salary * 0.075          # LPP (dépend de l'âge)
            self.accident_insurance = self.gross_salary * 0.0081  # LAA
            
            # Impôt à la source (taux variable)
            self.tax_deduction = self.gross_salary * 0.10  # Approximation
            
            total_deductions = (self.social_security + self.unemployment + 
                              self.pension + self.accident_insurance + 
                              self.tax_deduction + self.other_deductions)
            
            self.net_salary = self.gross_salary - total_deductions
        
        return self.net_salary


# Table d'association pour les employés sur les projets
project_employees = db.Table('project_employees',
    db.Column('project_id', db.Integer, db.ForeignKey('projects.id'), primary_key=True),
    db.Column('employee_id', db.Integer, db.ForeignKey('employees.id'), primary_key=True),
    db.Column('role', db.String(50)),  # Chef d'équipe, Ouvrier, etc.
    db.Column('start_date', db.Date),
    db.Column('end_date', db.Date)
)