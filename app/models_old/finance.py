"""
Modèles pour la gestion financière
"""
from app import db
from datetime import datetime, date, timedelta
from decimal import Decimal
from sqlalchemy import event

class Invoice(db.Model):
    """Modèle Facture"""
    __tablename__ = 'invoices'
    
    id = db.Column(db.Integer, primary_key=True)
    invoice_number = db.Column(db.String(20), unique=True, nullable=False)
    
    # Type de facture
    invoice_type = db.Column(db.String(20), default='standard')  # standard, credit_note, proforma
    
    # Client et projet
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'))
    
    # Dates
    issue_date = db.Column(db.Date, default=date.today)
    due_date = db.Column(db.Date)
    paid_date = db.Column(db.Date)
    
    # Montants
    subtotal = db.Column(db.Decimal(10, 2), default=0)
    tax_rate = db.Column(db.Float, default=7.7)  # TVA suisse standard
    tax_amount = db.Column(db.Decimal(10, 2), default=0)
    discount_percentage = db.Column(db.Float, default=0)
    discount_amount = db.Column(db.Decimal(10, 2), default=0)
    total_amount = db.Column(db.Decimal(10, 2), nullable=False)
    paid_amount = db.Column(db.Decimal(10, 2), default=0)
    
    # Devise
    currency = db.Column(db.String(3), default='CHF')
    
    # Statut
    status = db.Column(db.String(20), default='draft')  # draft, sent, paid, partial, overdue, cancelled
    
    # Références
    reference_number = db.Column(db.String(50))  # Référence QR-facture
    quote_id = db.Column(db.Integer, db.ForeignKey('quotes.id'))
    
    # Notes
    header_text = db.Column(db.Text)
    footer_text = db.Column(db.Text)
    internal_notes = db.Column(db.Text)
    
    # Validation
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    validated_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    validated_at = db.Column(db.DateTime)
    
    # Envoi
    sent_at = db.Column(db.DateTime)
    sent_to_emails = db.Column(db.JSON, default=lambda: [])
    
    # Documents
    pdf_path = db.Column(db.String(200))
    
    # Relations
    created_by = db.relationship('User', foreign_keys=[created_by_id])
    validated_by = db.relationship('User', foreign_keys=[validated_by_id])
    items = db.relationship('InvoiceItem', backref='invoice', lazy='dynamic', cascade='all, delete-orphan')
    payments = db.relationship('Payment', backref='invoice', lazy='dynamic')
    
    def __repr__(self):
        return f'<Invoice {self.invoice_number}>'
    
    def calculate_totals(self):
        """Calculer les totaux"""
        self.subtotal = sum(item.total for item in self.items)
        
        if self.discount_percentage:
            self.discount_amount = self.subtotal * (self.discount_percentage / 100)
        
        taxable_amount = self.subtotal - self.discount_amount
        self.tax_amount = taxable_amount * (self.tax_rate / 100)
        self.total_amount = taxable_amount + self.tax_amount
        
        return self.total_amount
    
    def update_status(self):
        """Mettre à jour le statut basé sur les paiements"""
        if self.status == 'cancelled':
            return
        
        if self.paid_amount >= self.total_amount:
            self.status = 'paid'
            if not self.paid_date:
                self.paid_date = date.today()
        elif self.paid_amount > 0:
            self.status = 'partial'
        elif self.due_date and date.today() > self.due_date:
            self.status = 'overdue'
        elif self.sent_at:
            self.status = 'sent'
        else:
            self.status = 'draft'


class InvoiceItem(db.Model):
    """Modèle Ligne de facture"""
    __tablename__ = 'invoice_items'
    
    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoices.id'), nullable=False)
    
    # Description
    description = db.Column(db.Text, nullable=False)
    item_code = db.Column(db.String(50))
    
    # Quantité et prix
    quantity = db.Column(db.Float, default=1)
    unit = db.Column(db.String(20))  # Heures, m², pièces, etc.
    unit_price = db.Column(db.Decimal(10, 2), nullable=False)
    total = db.Column(db.Decimal(10, 2), nullable=False)
    
    # Ordre d'affichage
    position = db.Column(db.Integer, default=0)
    
    # Catégorie (pour regroupement)
    category = db.Column(db.String(50))
    
    def __repr__(self):
        return f'<InvoiceItem {self.description[:30]}>'
    
    def calculate_total(self):
        """Calculer le total de la ligne"""
        self.total = Decimal(str(self.quantity)) * self.unit_price
        return self.total


class Quote(db.Model):
    """Modèle Devis"""
    __tablename__ = 'quotes'
    
    id = db.Column(db.Integer, primary_key=True)
    quote_number = db.Column(db.String(20), unique=True, nullable=False)
    
    # Client et projet potentiel
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    project_name = db.Column(db.String(200))
    project_description = db.Column(db.Text)
    
    # Dates
    issue_date = db.Column(db.Date, default=date.today)
    valid_until = db.Column(db.Date)
    
    # Montants
    subtotal = db.Column(db.Decimal(10, 2), default=0)
    tax_rate = db.Column(db.Float, default=7.7)
    tax_amount = db.Column(db.Decimal(10, 2), default=0)
    discount_percentage = db.Column(db.Float, default=0)
    discount_amount = db.Column(db.Decimal(10, 2), default=0)
    total_amount = db.Column(db.Decimal(10, 2), nullable=False)
    
    # Statut
    status = db.Column(db.String(20), default='draft')  # draft, sent, accepted, rejected, expired
    
    # Conditions
    payment_terms = db.Column(db.Text)
    delivery_terms = db.Column(db.Text)
    validity_terms = db.Column(db.Text)
    
    # Notes
    introduction_text = db.Column(db.Text)
    conclusion_text = db.Column(db.Text)
    internal_notes = db.Column(db.Text)
    
    # Validation et acceptation
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    accepted_at = db.Column(db.DateTime)
    accepted_by_name = db.Column(db.String(100))
    rejection_reason = db.Column(db.Text)
    
    # Conversion
    converted_to_project_id = db.Column(db.Integer, db.ForeignKey('projects.id'))
    
    # Documents
    pdf_path = db.Column(db.String(200))
    
    # Relations
    created_by = db.relationship('User', foreign_keys=[created_by_id])
    converted_to_project = db.relationship('Project', foreign_keys=[converted_to_project_id])
    items = db.relationship('QuoteItem', backref='quote', lazy='dynamic', cascade='all, delete-orphan')
    invoices = db.relationship('Invoice', backref='quote', lazy='dynamic')
    
    def __repr__(self):
        return f'<Quote {self.quote_number}>'
    
    def calculate_totals(self):
        """Calculer les totaux"""
        self.subtotal = sum(item.total for item in self.items)
        
        if self.discount_percentage:
            self.discount_amount = self.subtotal * (self.discount_percentage / 100)
        
        taxable_amount = self.subtotal - self.discount_amount
        self.tax_amount = taxable_amount * (self.tax_rate / 100)
        self.total_amount = taxable_amount + self.tax_amount
        
        return self.total_amount
    
    def check_expiry(self):
        """Vérifier si le devis est expiré"""
        if self.status in ['accepted', 'rejected', 'expired']:
            return
        
        if self.valid_until and date.today() > self.valid_until:
            self.status = 'expired'


class QuoteItem(db.Model):
    """Modèle Ligne de devis"""
    __tablename__ = 'quote_items'
    
    id = db.Column(db.Integer, primary_key=True)
    quote_id = db.Column(db.Integer, db.ForeignKey('quotes.id'), nullable=False)
    
    # Description
    description = db.Column(db.Text, nullable=False)
    detailed_description = db.Column(db.Text)  # Description technique détaillée
    item_code = db.Column(db.String(50))
    
    # Quantité et prix
    quantity = db.Column(db.Float, default=1)
    unit = db.Column(db.String(20))
    unit_price = db.Column(db.Decimal(10, 2), nullable=False)
    total = db.Column(db.Decimal(10, 2), nullable=False)
    
    # Options
    is_optional = db.Column(db.Boolean, default=False)
    option_group = db.Column(db.String(50))  # Pour grouper les options
    
    # Ordre d'affichage
    position = db.Column(db.Integer, default=0)
    category = db.Column(db.String(50))
    
    def __repr__(self):
        return f'<QuoteItem {self.description[:30]}>'
    
    def calculate_total(self):
        """Calculer le total de la ligne"""
        self.total = Decimal(str(self.quantity)) * self.unit_price
        return self.total


class Expense(db.Model):
    """Modèle Dépense"""
    __tablename__ = 'expenses'
    
    id = db.Column(db.Integer, primary_key=True)
    expense_number = db.Column(db.String(20), unique=True)
    
    # Employé concerné
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    
    # Type et catégorie
    expense_type = db.Column(db.String(50))  # Matériaux, Transport, Sous-traitance, etc.
    category = db.Column(db.String(50))  # Transport, Repas, Fournitures, Hébergement, etc.
    
    # Projet associé
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'))
    
    # Fournisseur
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'))
    supplier_name = db.Column(db.String(200))  # Si pas dans la base
    
    # Informations
    description = db.Column(db.Text, nullable=False)
    expense_date = db.Column(db.Date, default=date.today)
    
    # Montants
    amount = db.Column(db.Decimal(10, 2), nullable=False)
    tax_amount = db.Column(db.Decimal(10, 2), default=0)
    total_amount = db.Column(db.Decimal(10, 2), nullable=False)
    currency = db.Column(db.String(3), default='CHF')
    exchange_rate = db.Column(db.Float, default=1.0)  # Si devise étrangère
    
    # Paiement
    payment_method = db.Column(db.String(50))  # Carte entreprise, Personnel, Espèces
    payment_status = db.Column(db.String(20), default='pending')  # pending, approved, rejected, paid, reimbursed
    paid_date = db.Column(db.Date)
    reimbursed_date = db.Column(db.Date)
    reimbursement_amount = db.Column(db.Decimal(10, 2))
    
    # Documents
    receipt_path = db.Column(db.String(200))
    receipt_photo = db.Column(db.String(200))  # Photo du reçu
    invoice_reference = db.Column(db.String(100))
    
    # Workflow de validation
    submitted_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Approbation niveau 1 (Manager)
    manager_approved_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    manager_approved_at = db.Column(db.DateTime)
    manager_comments = db.Column(db.Text)
    
    # Approbation niveau 2 (Finance/RH)
    final_approved_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    final_approved_at = db.Column(db.DateTime)
    final_comments = db.Column(db.Text)
    
    # Raison de rejet
    rejection_reason = db.Column(db.Text)
    rejected_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    rejected_at = db.Column(db.DateTime)
    
    # Politiques
    policy_violation = db.Column(db.Boolean, default=False)
    policy_violation_reason = db.Column(db.Text)
    
    # Notes
    notes = db.Column(db.Text)
    
    # Relations
    employee = db.relationship('Employee', backref='expenses')
    submitted_by = db.relationship('User', foreign_keys=[submitted_by_id])
    manager_approved_by = db.relationship('User', foreign_keys=[manager_approved_by_id])
    final_approved_by = db.relationship('User', foreign_keys=[final_approved_by_id])
    rejected_by = db.relationship('User', foreign_keys=[rejected_by_id])
    
    def __repr__(self):
        return f'<Expense {self.expense_number or self.id}>'


class Payment(db.Model):
    """Modèle Paiement"""
    __tablename__ = 'payments'
    
    id = db.Column(db.Integer, primary_key=True)
    payment_number = db.Column(db.String(20), unique=True)
    
    # Facture associée
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoices.id'), nullable=False)
    
    # Informations de paiement
    payment_date = db.Column(db.Date, default=date.today)
    amount = db.Column(db.Decimal(10, 2), nullable=False)
    payment_method = db.Column(db.String(50))  # Virement, Carte, Espèces, Chèque
    
    # Référence bancaire
    bank_reference = db.Column(db.String(100))
    transaction_id = db.Column(db.String(100))
    
    # Validation
    recorded_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Notes
    notes = db.Column(db.Text)
    
    # Relations
    recorded_by = db.relationship('User', foreign_keys=[recorded_by_id])
    
    def __repr__(self):
        return f'<Payment {self.payment_number or self.id}>'


# Event listeners pour générer les numéros automatiquement
@event.listens_for(Invoice, 'before_insert')
def generate_invoice_number(mapper, connection, target):
    """Générer automatiquement un numéro de facture"""
    if not target.invoice_number:
        year = datetime.now().year
        result = connection.execute(
            f"SELECT MAX(CAST(SUBSTR(invoice_number, -4) AS INTEGER)) FROM invoices WHERE invoice_number LIKE 'F-{year}-%'"
        ).scalar()
        next_number = (result or 0) + 1
        target.invoice_number = f"F-{year}-{next_number:04d}"


@event.listens_for(Quote, 'before_insert')
def generate_quote_number(mapper, connection, target):
    """Générer automatiquement un numéro de devis"""
    if not target.quote_number:
        year = datetime.now().year
        result = connection.execute(
            f"SELECT MAX(CAST(SUBSTR(quote_number, -4) AS INTEGER)) FROM quotes WHERE quote_number LIKE 'D-{year}-%'"
        ).scalar()
        next_number = (result or 0) + 1
        target.quote_number = f"D-{year}-{next_number:04d}"