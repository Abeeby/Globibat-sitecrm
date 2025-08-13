"""
Modèles pour la gestion d'inventaire et fournisseurs
"""
from app import db
from datetime import datetime, date

class Supplier(db.Model):
    """Modèle Fournisseur"""
    __tablename__ = 'suppliers'
    
    id = db.Column(db.Integer, primary_key=True)
    supplier_code = db.Column(db.String(20), unique=True, nullable=False)
    
    # Informations entreprise
    company_name = db.Column(db.String(200), nullable=False)
    registration_number = db.Column(db.String(50))
    vat_number = db.Column(db.String(50))
    
    # Contact
    contact_name = db.Column(db.String(100))
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    fax = db.Column(db.String(20))
    website = db.Column(db.String(200))
    
    # Adresse
    address = db.Column(db.String(200))
    postal_code = db.Column(db.String(10))
    city = db.Column(db.String(100))
    canton = db.Column(db.String(50))
    country = db.Column(db.String(50), default='Suisse')
    
    # Informations commerciales
    supplier_type = db.Column(db.String(50))  # Matériaux, Équipement, Services
    categories = db.Column(db.JSON, default=lambda: [])  # Catégories de produits
    payment_terms = db.Column(db.Integer, default=30)  # Jours
    discount_percentage = db.Column(db.Float, default=0)
    credit_limit = db.Column(db.Float)
    
    # Évaluation
    rating = db.Column(db.Integer)  # 1-5 étoiles
    quality_score = db.Column(db.Float)
    delivery_score = db.Column(db.Float)
    price_score = db.Column(db.Float)
    
    # Statut
    is_active = db.Column(db.Boolean, default=True)
    is_preferred = db.Column(db.Boolean, default=False)
    
    # Notes
    notes = db.Column(db.Text)
    
    # Dates
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_order_date = db.Column(db.Date)
    
    # Relations
    materials = db.relationship('Material', backref='supplier', lazy='dynamic')
    purchase_orders = db.relationship('PurchaseOrder', backref='supplier', lazy='dynamic')
    expenses = db.relationship('Expense', backref='supplier', lazy='dynamic')
    
    def __repr__(self):
        return f'<Supplier {self.company_name}>'


class Material(db.Model):
    """Modèle Matériau/Produit"""
    __tablename__ = 'materials'
    
    id = db.Column(db.Integer, primary_key=True)
    material_code = db.Column(db.String(50), unique=True, nullable=False)
    
    # Informations produit
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50))  # Gros œuvre, Second œuvre, etc.
    subcategory = db.Column(db.String(50))
    
    # Fournisseur principal
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'))
    supplier_ref = db.Column(db.String(100))  # Référence fournisseur
    
    # Unités et prix
    unit = db.Column(db.String(20))  # m², m³, kg, pièce, etc.
    purchase_price = db.Column(db.Float)
    selling_price = db.Column(db.Float)
    
    # Stock
    current_stock = db.Column(db.Float, default=0)
    minimum_stock = db.Column(db.Float, default=0)
    maximum_stock = db.Column(db.Float)
    location = db.Column(db.String(100))  # Emplacement dans l'entrepôt
    
    # Caractéristiques techniques
    specifications = db.Column(db.JSON, default=lambda: {})
    weight_per_unit = db.Column(db.Float)  # kg
    volume_per_unit = db.Column(db.Float)  # m³
    
    # Statut
    is_active = db.Column(db.Boolean, default=True)
    is_stockable = db.Column(db.Boolean, default=True)
    
    # Images et documents
    image_path = db.Column(db.String(200))
    datasheet_path = db.Column(db.String(200))
    
    # Dates
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_purchase_date = db.Column(db.Date)
    
    def __repr__(self):
        return f'<Material {self.name}>'
    
    @property
    def needs_reorder(self):
        """Vérifier si le matériau doit être réapprovisionné"""
        return self.current_stock <= self.minimum_stock
    
    @property
    def stock_value(self):
        """Calculer la valeur du stock"""
        if self.current_stock and self.purchase_price:
            return self.current_stock * self.purchase_price
        return 0


class Equipment(db.Model):
    """Modèle Équipement/Outillage"""
    __tablename__ = 'equipment'
    
    id = db.Column(db.Integer, primary_key=True)
    equipment_code = db.Column(db.String(20), unique=True, nullable=False)
    
    # Informations
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50))  # Outillage, Véhicule, Machine, etc.
    brand = db.Column(db.String(100))
    model = db.Column(db.String(100))
    serial_number = db.Column(db.String(100))
    
    # Acquisition
    purchase_date = db.Column(db.Date)
    purchase_price = db.Column(db.Float)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'))
    
    # Localisation et responsable
    current_location = db.Column(db.String(100))
    assigned_to_id = db.Column(db.Integer, db.ForeignKey('employees.id'))
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'))
    
    # Maintenance
    last_maintenance = db.Column(db.Date)
    next_maintenance = db.Column(db.Date)
    maintenance_interval_days = db.Column(db.Integer)
    
    # Statut
    status = db.Column(db.String(20), default='available')  # available, in_use, maintenance, broken
    condition = db.Column(db.String(20), default='good')  # excellent, good, fair, poor
    
    # Amortissement
    depreciation_years = db.Column(db.Integer)
    residual_value = db.Column(db.Float)
    
    # Documents
    image_path = db.Column(db.String(200))
    manual_path = db.Column(db.String(200))
    
    # Notes
    notes = db.Column(db.Text)
    
    # Relations
    assigned_to = db.relationship('Employee', foreign_keys=[assigned_to_id])
    maintenance_logs = db.relationship('EquipmentMaintenance', backref='equipment', lazy='dynamic')
    
    def __repr__(self):
        return f'<Equipment {self.name}>'
    
    @property
    def needs_maintenance(self):
        """Vérifier si l'équipement nécessite une maintenance"""
        if self.next_maintenance:
            return date.today() >= self.next_maintenance
        return False
    
    @property
    def current_value(self):
        """Calculer la valeur actuelle (avec amortissement)"""
        if not self.purchase_price or not self.purchase_date:
            return self.purchase_price
        
        if self.depreciation_years:
            years_owned = (date.today() - self.purchase_date).days / 365.25
            if years_owned >= self.depreciation_years:
                return self.residual_value or 0
            
            total_depreciation = self.purchase_price - (self.residual_value or 0)
            annual_depreciation = total_depreciation / self.depreciation_years
            current_depreciation = annual_depreciation * years_owned
            
            return self.purchase_price - current_depreciation
        
        return self.purchase_price


class PurchaseOrder(db.Model):
    """Modèle Bon de commande"""
    __tablename__ = 'purchase_orders'
    
    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(20), unique=True, nullable=False)
    
    # Fournisseur
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=False)
    
    # Projet associé
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'))
    
    # Dates
    order_date = db.Column(db.Date, default=date.today)
    expected_delivery = db.Column(db.Date)
    actual_delivery = db.Column(db.Date)
    
    # Montants
    subtotal = db.Column(db.Float, default=0)
    tax_amount = db.Column(db.Float, default=0)
    shipping_cost = db.Column(db.Float, default=0)
    total_amount = db.Column(db.Float, nullable=False)
    
    # Statut
    status = db.Column(db.String(20), default='draft')  # draft, sent, confirmed, delivered, cancelled
    
    # Livraison
    delivery_address = db.Column(db.Text)
    delivery_notes = db.Column(db.Text)
    
    # Validation
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    approved_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    approved_at = db.Column(db.DateTime)
    
    # Documents
    pdf_path = db.Column(db.String(200))
    
    # Relations
    created_by = db.relationship('User', foreign_keys=[created_by_id])
    approved_by = db.relationship('User', foreign_keys=[approved_by_id])
    items = db.relationship('PurchaseOrderItem', backref='purchase_order', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<PurchaseOrder {self.order_number}>'


class PurchaseOrderItem(db.Model):
    """Modèle Ligne de commande"""
    __tablename__ = 'purchase_order_items'
    
    id = db.Column(db.Integer, primary_key=True)
    purchase_order_id = db.Column(db.Integer, db.ForeignKey('purchase_orders.id'), nullable=False)
    
    # Matériau
    material_id = db.Column(db.Integer, db.ForeignKey('materials.id'))
    description = db.Column(db.Text, nullable=False)
    
    # Quantité et prix
    quantity = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(20))
    unit_price = db.Column(db.Float, nullable=False)
    total = db.Column(db.Float, nullable=False)
    
    # Réception
    received_quantity = db.Column(db.Float, default=0)
    received_date = db.Column(db.Date)
    
    def __repr__(self):
        return f'<PurchaseOrderItem {self.description[:30]}>'


class EquipmentMaintenance(db.Model):
    """Modèle Maintenance équipement"""
    __tablename__ = 'equipment_maintenance'
    
    id = db.Column(db.Integer, primary_key=True)
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id'), nullable=False)
    
    # Type de maintenance
    maintenance_type = db.Column(db.String(50))  # preventive, corrective, inspection
    
    # Dates
    scheduled_date = db.Column(db.Date)
    performed_date = db.Column(db.Date, nullable=False)
    next_due_date = db.Column(db.Date)
    
    # Détails
    description = db.Column(db.Text, nullable=False)
    performed_by = db.Column(db.String(100))
    cost = db.Column(db.Float)
    
    # Documents
    report_path = db.Column(db.String(200))
    
    # Validation
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relations
    created_by = db.relationship('User', foreign_keys=[created_by_id])
    
    def __repr__(self):
        return f'<EquipmentMaintenance {self.equipment_id} - {self.performed_date}>'