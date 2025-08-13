"""
Modèles pour la gestion de la planification et des rendez-vous
"""
from app import db
from datetime import datetime, date

class Schedule(db.Model):
    """Modèle Planning/Calendrier"""
    __tablename__ = 'schedules'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Type d'événement
    event_type = db.Column(db.String(50), nullable=False)  # meeting, task, project_milestone, leave, training
    
    # Informations générales
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    location = db.Column(db.String(200))
    
    # Dates et heures
    start_datetime = db.Column(db.DateTime, nullable=False)
    end_datetime = db.Column(db.DateTime, nullable=False)
    all_day = db.Column(db.Boolean, default=False)
    
    # Récurrence
    is_recurring = db.Column(db.Boolean, default=False)
    recurrence_pattern = db.Column(db.String(50))  # daily, weekly, monthly, yearly
    recurrence_end_date = db.Column(db.Date)
    
    # Associations
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'))
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'))
    
    # Participants
    organizer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    attendees = db.Column(db.JSON, default=lambda: [])  # Liste des IDs utilisateurs
    
    # Rappels
    reminder_minutes = db.Column(db.Integer, default=15)
    reminder_sent = db.Column(db.Boolean, default=False)
    
    # Statut
    status = db.Column(db.String(20), default='scheduled')  # scheduled, in_progress, completed, cancelled
    
    # Couleur (pour l'affichage calendrier)
    color = db.Column(db.String(7), default='#3788d8')
    
    # Notes
    notes = db.Column(db.Text)
    
    # Relations
    organizer = db.relationship('User', foreign_keys=[organizer_id])
    
    def __repr__(self):
        return f'<Schedule {self.title}>'
    
    @property
    def duration_hours(self):
        """Durée en heures"""
        if self.start_datetime and self.end_datetime:
            delta = self.end_datetime - self.start_datetime
            return delta.total_seconds() / 3600
        return 0


class Meeting(db.Model):
    """Modèle Réunion/Rendez-vous"""
    __tablename__ = 'meetings'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Type de réunion
    meeting_type = db.Column(db.String(50))  # client, internal, supplier, site_visit, inspection
    
    # Informations
    subject = db.Column(db.String(200), nullable=False)
    agenda = db.Column(db.Text)
    location = db.Column(db.String(200))
    is_virtual = db.Column(db.Boolean, default=False)
    virtual_link = db.Column(db.String(500))
    
    # Dates
    scheduled_at = db.Column(db.DateTime, nullable=False)
    duration_minutes = db.Column(db.Integer, default=60)
    actual_start = db.Column(db.DateTime)
    actual_end = db.Column(db.DateTime)
    
    # Associations
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'))
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'))
    
    # Participants
    organizer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Résultats
    minutes = db.Column(db.Text)  # Compte-rendu
    decisions = db.Column(db.Text)
    action_items = db.Column(db.JSON, default=lambda: [])
    
    # Statut
    status = db.Column(db.String(20), default='scheduled')  # scheduled, in_progress, completed, cancelled
    
    # Documents
    attachments = db.Column(db.JSON, default=lambda: [])
    
    # Relations
    organizer = db.relationship('User', foreign_keys=[organizer_id])
    participants = db.relationship('MeetingParticipant', backref='meeting', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Meeting {self.subject}>'


class MeetingParticipant(db.Model):
    """Modèle Participant de réunion"""
    __tablename__ = 'meeting_participants'
    
    id = db.Column(db.Integer, primary_key=True)
    meeting_id = db.Column(db.Integer, db.ForeignKey('meetings.id'), nullable=False)
    
    # Participant interne ou externe
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    external_name = db.Column(db.String(100))
    external_email = db.Column(db.String(120))
    external_company = db.Column(db.String(100))
    
    # Statut
    is_required = db.Column(db.Boolean, default=True)
    response_status = db.Column(db.String(20), default='pending')  # pending, accepted, declined, tentative
    attended = db.Column(db.Boolean, default=False)
    
    # Notes
    notes = db.Column(db.Text)
    
    # Relations
    user = db.relationship('User', foreign_keys=[user_id])
    
    def __repr__(self):
        if self.user:
            return f'<MeetingParticipant {self.user.full_name}>'
        return f'<MeetingParticipant {self.external_name}>'


class Reminder(db.Model):
    """Modèle Rappel/Notification"""
    __tablename__ = 'reminders'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Type de rappel
    reminder_type = db.Column(db.String(50))  # task, meeting, payment, maintenance, document_expiry
    
    # Informations
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text)
    
    # Date du rappel
    reminder_date = db.Column(db.DateTime, nullable=False)
    
    # Destinataire
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Association avec d'autres entités
    entity_type = db.Column(db.String(50))  # project, task, invoice, equipment, etc.
    entity_id = db.Column(db.Integer)
    
    # Statut
    is_sent = db.Column(db.Boolean, default=False)
    sent_at = db.Column(db.DateTime)
    is_read = db.Column(db.Boolean, default=False)
    read_at = db.Column(db.DateTime)
    
    # Priorité
    priority = db.Column(db.String(20), default='normal')  # low, normal, high, urgent
    
    # Actions
    action_url = db.Column(db.String(200))  # Lien vers l'action à effectuer
    
    # Relations
    user = db.relationship('User', foreign_keys=[user_id])
    
    def __repr__(self):
        return f'<Reminder {self.title}>'
    
    def mark_as_sent(self):
        """Marquer comme envoyé"""
        self.is_sent = True
        self.sent_at = datetime.utcnow()
    
    def mark_as_read(self):
        """Marquer comme lu"""
        self.is_read = True
        self.read_at = datetime.utcnow()


class Holiday(db.Model):
    """Modèle Jours fériés"""
    __tablename__ = 'holidays'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Informations
    name = db.Column(db.String(100), nullable=False)
    date = db.Column(db.Date, nullable=False, unique=True)
    
    # Type
    holiday_type = db.Column(db.String(50))  # national, cantonal, company
    
    # Applicable à
    canton = db.Column(db.String(50))  # Si cantonal
    is_paid = db.Column(db.Boolean, default=True)
    
    # Récurrence annuelle
    is_recurring = db.Column(db.Boolean, default=True)
    
    def __repr__(self):
        return f'<Holiday {self.name} - {self.date}>'