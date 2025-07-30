"""
Modèles pour la gestion des clients
"""
from app import db
from datetime import datetime

class Client(db.Model):
    """Modèle Client"""
    __tablename__ = 'clients'
    
    id = db.Column(db.Integer, primary_key=True)
    client_code = db.Column(db.String(20), unique=True, nullable=False)
    
    # Type de client
    client_type = db.Column(db.String(20), nullable=False)  # individual, company, public
    
    # Informations entreprise
    company_name = db.Column(db.String(200))
    company_registration = db.Column(db.String(50))  # IDE/UID suisse
    vat_number = db.Column(db.String(50))
    
    # Informations individuelles
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    title = db.Column(db.String(20))  # M., Mme, Dr., etc.
    
    # Contact principal
    primary_email = db.Column(db.String(120), nullable=False)
    primary_phone = db.Column(db.String(20), nullable=False)
    secondary_phone = db.Column(db.String(20))
    website = db.Column(db.String(200))
    
    # Adresse
    address = db.Column(db.String(200))
    postal_code = db.Column(db.String(10))
    city = db.Column(db.String(100))
    canton = db.Column(db.String(50))
    country = db.Column(db.String(50), default='Suisse')
    
    # Adresse de facturation (si différente)
    billing_address = db.Column(db.String(200))
    billing_postal_code = db.Column(db.String(10))
    billing_city = db.Column(db.String(100))
    
    # Informations commerciales
    lead_source = db.Column(db.String(50))  # Site web, Recommandation, etc.
    industry = db.Column(db.String(50))
    revenue_potential = db.Column(db.Decimal(10, 2))
    credit_limit = db.Column(db.Decimal(10, 2))
    payment_terms = db.Column(db.Integer, default=30)  # Jours
    
    # Préférences
    preferred_language = db.Column(db.String(5), default='fr')  # fr, de, it
    preferred_contact_method = db.Column(db.String(20), default='email')
    
    # Statut et scoring
    status = db.Column(db.String(20), default='active')  # active, inactive, prospect
    rating = db.Column(db.Integer)  # 1-5 étoiles
    tags = db.Column(db.JSON, default=lambda: [])
    
    # Responsable commercial
    assigned_to_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Dates
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    first_contact_date = db.Column(db.Date)
    last_contact_date = db.Column(db.Date)
    
    # Notes et documents
    internal_notes = db.Column(db.Text)
    
    # Relations
    assigned_to = db.relationship('User', foreign_keys=[assigned_to_id])
    contacts = db.relationship('Contact', backref='client', lazy='dynamic', cascade='all, delete-orphan')
    projects = db.relationship('Project', backref='client', lazy='dynamic')
    quotes = db.relationship('Quote', backref='client', lazy='dynamic')
    invoices = db.relationship('Invoice', backref='client', lazy='dynamic')
    notes = db.relationship('ClientNote', backref='client', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Client {self.client_code}>'
    
    @property
    def display_name(self):
        """Nom d'affichage du client"""
        if self.client_type == 'company':
            return self.company_name
        else:
            return f"{self.title} {self.first_name} {self.last_name}".strip()
    
    @property
    def full_address(self):
        """Adresse complète"""
        parts = [self.address, f"{self.postal_code} {self.city}"]
        if self.canton:
            parts.append(self.canton)
        if self.country != 'Suisse':
            parts.append(self.country)
        return ', '.join(filter(None, parts))
    
    def calculate_outstanding_balance(self):
        """Calculer le solde dû"""
        unpaid_invoices = Invoice.query.filter_by(
            client_id=self.id,
            status='sent'
        ).all()
        return sum(invoice.total_amount - invoice.paid_amount for invoice in unpaid_invoices)


class Contact(db.Model):
    """Modèle Contact (personnes liées aux clients)"""
    __tablename__ = 'contacts'
    
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    
    # Informations personnelles
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    title = db.Column(db.String(20))
    position = db.Column(db.String(100))
    department = db.Column(db.String(100))
    
    # Contact
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    mobile = db.Column(db.String(20))
    
    # Préférences
    is_primary = db.Column(db.Boolean, default=False)
    receives_invoices = db.Column(db.Boolean, default=False)
    receives_quotes = db.Column(db.Boolean, default=False)
    receives_newsletter = db.Column(db.Boolean, default=True)
    
    # Notes
    notes = db.Column(db.Text)
    
    # Dates
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Contact {self.first_name} {self.last_name}>'
    
    @property
    def full_name(self):
        """Nom complet"""
        parts = []
        if self.title:
            parts.append(self.title)
        parts.extend([self.first_name, self.last_name])
        return ' '.join(parts)


class ClientNote(db.Model):
    """Modèle Note Client (historique des interactions)"""
    __tablename__ = 'client_notes'
    
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    
    # Type d'interaction
    note_type = db.Column(db.String(50), nullable=False)  # call, email, meeting, visit, other
    
    # Contenu
    subject = db.Column(db.String(200))
    content = db.Column(db.Text, nullable=False)
    
    # Contact associé
    contact_id = db.Column(db.Integer, db.ForeignKey('contacts.id'))
    
    # Suivi
    follow_up_date = db.Column(db.Date)
    follow_up_done = db.Column(db.Boolean, default=False)
    
    # Auteur
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relations
    contact = db.relationship('Contact')
    created_by = db.relationship('User', foreign_keys=[created_by_id])
    
    def __repr__(self):
        return f'<ClientNote {self.id} - {self.note_type}>'