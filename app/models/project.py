"""
Modèles pour la gestion des projets de construction
"""
from app import db
from datetime import datetime, date
from sqlalchemy import event

class Project(db.Model):
    """Modèle Projet de construction"""
    __tablename__ = 'projects'
    
    id = db.Column(db.Integer, primary_key=True)
    project_code = db.Column(db.String(20), unique=True, nullable=False)
    
    # Informations générales
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    project_type = db.Column(db.String(50))  # Construction, Rénovation, Extension, etc.
    building_type = db.Column(db.String(50))  # Villa, Immeuble, Commercial, Industriel
    
    # Client
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    
    # Adresse du chantier
    site_address = db.Column(db.String(200))
    site_postal_code = db.Column(db.String(10))
    site_city = db.Column(db.String(100))
    site_canton = db.Column(db.String(50))
    coordinates_lat = db.Column(db.Float)  # Pour géolocalisation
    coordinates_lng = db.Column(db.Float)
    
    # Dates
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    start_date = db.Column(db.Date)
    planned_end_date = db.Column(db.Date)
    actual_end_date = db.Column(db.Date)
    
    # Budget et finances
    estimated_budget = db.Column(db.Float)
    approved_budget = db.Column(db.Float)
    current_cost = db.Column(db.Float, default=0)
    margin_percentage = db.Column(db.Float)
    
    # Statut et progression
    status = db.Column(db.String(20), default='planning')  # planning, approved, in_progress, on_hold, completed, cancelled
    completion_percentage = db.Column(db.Integer, default=0)
    priority = db.Column(db.String(20), default='normal')  # low, normal, high, urgent
    
    # Responsables
    project_manager_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    site_supervisor_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Informations techniques
    surface_area = db.Column(db.Float)  # m²
    floors_count = db.Column(db.Integer)
    building_permit_number = db.Column(db.String(50))
    building_permit_date = db.Column(db.Date)
    
    # Documents et notes
    internal_notes = db.Column(db.Text)
    client_notes = db.Column(db.Text)
    
    # Relations
    project_manager = db.relationship('User', foreign_keys=[project_manager_id])
    site_supervisor = db.relationship('User', foreign_keys=[site_supervisor_id])
    phases = db.relationship('ProjectPhase', backref='project', lazy='dynamic', cascade='all, delete-orphan')
    tasks = db.relationship('ProjectTask', backref='project', lazy='dynamic', cascade='all, delete-orphan')
    documents = db.relationship('ProjectDocument', backref='project', lazy='dynamic', cascade='all, delete-orphan')
    attendances = db.relationship('Attendance', backref='project', lazy='dynamic')
    
    def __repr__(self):
        return f'<Project {self.project_code} - {self.name}>'
    
    @property
    def is_overdue(self):
        """Vérifier si le projet est en retard"""
        if self.planned_end_date and self.status == 'in_progress':
            return date.today() > self.planned_end_date
        return False
    
    @property
    def budget_status(self):
        """Statut du budget"""
        if self.approved_budget and self.current_cost:
            percentage = (self.current_cost / self.approved_budget) * 100
            if percentage > 100:
                return 'over_budget'
            elif percentage > 90:
                return 'warning'
            else:
                return 'on_track'
        return 'unknown'
    
    def update_completion(self):
        """Mettre à jour le pourcentage d'achèvement basé sur les phases"""
        if self.phases.count() > 0:
            completed_phases = self.phases.filter_by(status='completed').count()
            self.completion_percentage = int((completed_phases / self.phases.count()) * 100)
        return self.completion_percentage


class ProjectPhase(db.Model):
    """Modèle Phase de projet"""
    __tablename__ = 'project_phases'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    
    # Informations
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    phase_order = db.Column(db.Integer, default=0)
    
    # Dates
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    actual_start = db.Column(db.Date)
    actual_end = db.Column(db.Date)
    
    # Budget
    estimated_cost = db.Column(db.Float)
    actual_cost = db.Column(db.Float, default=0)
    
    # Statut
    status = db.Column(db.String(20), default='pending')  # pending, in_progress, completed, cancelled
    completion_percentage = db.Column(db.Integer, default=0)
    
    # Responsable
    responsible_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relations
    responsible = db.relationship('User', foreign_keys=[responsible_id])
    
    def __repr__(self):
        return f'<ProjectPhase {self.name}>'


class ProjectTask(db.Model):
    """Modèle Tâche de projet"""
    __tablename__ = 'project_tasks'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    phase_id = db.Column(db.Integer, db.ForeignKey('project_phases.id'))
    
    # Informations
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    task_type = db.Column(db.String(50))  # Maçonnerie, Électricité, Plomberie, etc.
    
    # Dates et durée
    start_date = db.Column(db.Date)
    due_date = db.Column(db.Date)
    completed_date = db.Column(db.Date)
    estimated_hours = db.Column(db.Float)
    actual_hours = db.Column(db.Float, default=0)
    
    # Assignation
    assigned_to_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    team_size = db.Column(db.Integer, default=1)
    
    # Statut et priorité
    status = db.Column(db.String(20), default='todo')  # todo, in_progress, completed, blocked
    priority = db.Column(db.String(20), default='normal')  # low, normal, high, urgent
    
    # Dépendances
    depends_on_task_id = db.Column(db.Integer, db.ForeignKey('project_tasks.id'))
    
    # Matériaux requis
    materials_needed = db.Column(db.Text)
    equipment_needed = db.Column(db.Text)
    
    # Validation
    requires_validation = db.Column(db.Boolean, default=False)
    validated_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    validated_at = db.Column(db.DateTime)
    
    # Relations
    phase = db.relationship('ProjectPhase')
    depends_on = db.relationship('ProjectTask', remote_side=[id])
    validated_by = db.relationship('User', foreign_keys=[validated_by_id])
    
    def __repr__(self):
        return f'<ProjectTask {self.title}>'
    
    @property
    def is_overdue(self):
        """Vérifier si la tâche est en retard"""
        if self.due_date and self.status != 'completed':
            return date.today() > self.due_date
        return False


class ProjectDocument(db.Model):
    """Modèle Document de projet"""
    __tablename__ = 'project_documents'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    
    # Informations
    name = db.Column(db.String(200), nullable=False)
    document_type = db.Column(db.String(50))  # plan, permit, contract, photo, report
    description = db.Column(db.Text)
    
    # Fichier
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer)  # en octets
    file_type = db.Column(db.String(50))  # MIME type
    
    # Versioning
    version = db.Column(db.String(20), default='1.0')
    is_latest = db.Column(db.Boolean, default=True)
    
    # Métadonnées
    uploaded_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Sécurité
    is_confidential = db.Column(db.Boolean, default=False)
    access_level = db.Column(db.String(20), default='internal')  # internal, client, public
    
    # Relations
    uploaded_by = db.relationship('User', foreign_keys=[uploaded_by_id])
    
    def __repr__(self):
        return f'<ProjectDocument {self.name}>'


# Event listener pour générer automatiquement les codes projet
@event.listens_for(Project, 'before_insert')
def generate_project_code(mapper, connection, target):
    """Générer automatiquement un code projet"""
    if not target.project_code:
        # Format: PRJ-YYYY-XXXX
        year = datetime.now().year
        
        # Obtenir le dernier numéro
        result = connection.execute(
            f"SELECT MAX(CAST(SUBSTR(project_code, -4) AS INTEGER)) FROM projects WHERE project_code LIKE 'PRJ-{year}-%'"
        ).scalar()
        
        next_number = (result or 0) + 1
        target.project_code = f"PRJ-{year}-{next_number:04d}"