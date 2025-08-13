"""
Modèles de base de données pour Globibat CRM
"""
from datetime import datetime, date
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import event
import enum

db = SQLAlchemy()

# Enums pour les statuts
class StatutEmploye(enum.Enum):
    ACTIF = "Actif"
    CONGE = "En congé"
    MALADIE = "Maladie"
    FORMATION = "Formation"
    INACTIF = "Inactif"

class StatutChantier(enum.Enum):
    PLANIFIE = "Planifié"
    EN_COURS = "En cours"
    PAUSE = "En pause"
    TERMINE = "Terminé"
    ANNULE = "Annulé"

class StatutFacture(enum.Enum):
    BROUILLON = "Brouillon"
    ENVOYEE = "Envoyée"
    PAYEE = "Payée"
    EN_RETARD = "En retard"
    ANNULEE = "Annulée"

class TypeBadge(enum.Enum):
    ENTREE = "Entrée"
    SORTIE = "Sortie"
    PAUSE_DEBUT = "Début pause"
    PAUSE_FIN = "Fin pause"

class PrioriteAnomalie(enum.Enum):
    BASSE = "Basse"
    MOYENNE = "Moyenne"
    HAUTE = "Haute"
    CRITIQUE = "Critique"

# Table d'association pour les employés sur les chantiers
chantier_employes = db.Table('chantier_employes',
    db.Column('chantier_id', db.Integer, db.ForeignKey('chantier.id'), primary_key=True),
    db.Column('employe_id', db.Integer, db.ForeignKey('employe.id'), primary_key=True),
    db.Column('date_affectation', db.DateTime, default=datetime.utcnow),
    db.Column('role_chantier', db.String(100))
)

# Modèle Utilisateur (pour l'authentification)
class User(UserMixin, db.Model):
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256))
    role = db.Column(db.String(50), default='user')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relations
    employe = db.relationship('Employe', backref='user_account', uselist=False)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def has_permission(self, permission):
        return self.role in ['admin', 'manager']

# Modèle Employé
class Employe(db.Model):
    __tablename__ = 'employe'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True)
    matricule = db.Column(db.String(20), unique=True, nullable=False)
    nom = db.Column(db.String(100), nullable=False)
    prenom = db.Column(db.String(100), nullable=False)
    date_naissance = db.Column(db.Date)
    telephone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    adresse = db.Column(db.Text)
    poste = db.Column(db.String(100))
    departement = db.Column(db.String(100))
    date_embauche = db.Column(db.Date, default=date.today)
    salaire_base = db.Column(db.Float)
    statut = db.Column(db.Enum(StatutEmploye), default=StatutEmploye.ACTIF)
    photo = db.Column(db.String(200))
    qr_code = db.Column(db.String(200), unique=True)
    
    # Certifications et documents
    permis_conduire = db.Column(db.String(50))
    caces = db.Column(db.String(200))
    certifications = db.Column(db.Text)
    
    # Relations
    badges = db.relationship('Badge', backref='employe', lazy='dynamic')
    chantiers = db.relationship('Chantier', secondary=chantier_employes, backref='employes')
    fiches_paie = db.relationship('FichePaie', backref='employe', lazy='dynamic')
    incidents = db.relationship('IncidentSecurite', backref='employe_declarant', lazy='dynamic')
    
    @property
    def nom_complet(self):
        return f"{self.prenom} {self.nom}"
    
    @property
    def est_present(self):
        dernier_badge = self.badges.order_by(Badge.timestamp.desc()).first()
        if dernier_badge:
            return dernier_badge.type_badge == TypeBadge.ENTREE
        return False

# Modèle Client
class Client(db.Model):
    __tablename__ = 'client'
    
    id = db.Column(db.Integer, primary_key=True)
    code_client = db.Column(db.String(20), unique=True, nullable=False)
    raison_sociale = db.Column(db.String(200), nullable=False)
    type_client = db.Column(db.String(50))  # Particulier, Entreprise, Public
    siret = db.Column(db.String(20))
    tva_intracommunautaire = db.Column(db.String(50))
    adresse = db.Column(db.Text)
    code_postal = db.Column(db.String(10))
    ville = db.Column(db.String(100))
    pays = db.Column(db.String(100), default='France')
    telephone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    contact_principal = db.Column(db.String(200))
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    credit_limite = db.Column(db.Float)
    conditions_paiement = db.Column(db.String(100))
    notes = db.Column(db.Text)
    actif = db.Column(db.Boolean, default=True)
    
    # Relations
    chantiers = db.relationship('Chantier', backref='client', lazy='dynamic')
    devis = db.relationship('Devis', backref='client', lazy='dynamic')
    factures = db.relationship('Facture', backref='client', lazy='dynamic')
    
    @property
    def chiffre_affaires(self):
        return sum(f.montant_ttc for f in self.factures.filter_by(statut=StatutFacture.PAYEE))

# Modèle Chantier
class Chantier(db.Model):
    __tablename__ = 'chantier'
    
    id = db.Column(db.Integer, primary_key=True)
    code_chantier = db.Column(db.String(20), unique=True, nullable=False)
    nom = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    adresse = db.Column(db.Text)
    code_postal = db.Column(db.String(10))
    ville = db.Column(db.String(100))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    date_debut = db.Column(db.Date)
    date_fin_prevue = db.Column(db.Date)
    date_fin_reelle = db.Column(db.Date)
    budget_initial = db.Column(db.Float)
    budget_consomme = db.Column(db.Float, default=0)
    statut = db.Column(db.Enum(StatutChantier), default=StatutChantier.PLANIFIE)
    chef_chantier_id = db.Column(db.Integer, db.ForeignKey('employe.id'))
    avancement = db.Column(db.Integer, default=0)  # Pourcentage
    image = db.Column(db.String(200))
    
    # Relations
    chef_chantier = db.relationship('Employe', foreign_keys=[chef_chantier_id])
    phases = db.relationship('PhaseChantier', backref='chantier', lazy='dynamic', cascade='all, delete-orphan')
    photos = db.relationship('PhotoChantier', backref='chantier', lazy='dynamic', cascade='all, delete-orphan')
    documents = db.relationship('DocumentChantier', backref='chantier', lazy='dynamic', cascade='all, delete-orphan')
    incidents = db.relationship('IncidentSecurite', backref='chantier', lazy='dynamic')
    materiels = db.relationship('AffectationMateriel', backref='chantier', lazy='dynamic')
    
    @property
    def jours_restants(self):
        if self.date_fin_prevue:
            delta = self.date_fin_prevue - date.today()
            return delta.days
        return None
    
    @property
    def budget_restant(self):
        if self.budget_initial:
            return self.budget_initial - self.budget_consomme
        return None

# Modèle Phase de Chantier
class PhaseChantier(db.Model):
    __tablename__ = 'phase_chantier'
    
    id = db.Column(db.Integer, primary_key=True)
    chantier_id = db.Column(db.Integer, db.ForeignKey('chantier.id'), nullable=False)
    nom = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    ordre = db.Column(db.Integer)
    date_debut = db.Column(db.Date)
    date_fin = db.Column(db.Date)
    completee = db.Column(db.Boolean, default=False)
    
    # Relations
    taches = db.relationship('TacheChantier', backref='phase', lazy='dynamic', cascade='all, delete-orphan')

# Modèle Tâche de Chantier
class TacheChantier(db.Model):
    __tablename__ = 'tache_chantier'
    
    id = db.Column(db.Integer, primary_key=True)
    phase_id = db.Column(db.Integer, db.ForeignKey('phase_chantier.id'), nullable=False)
    nom = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    assignee_id = db.Column(db.Integer, db.ForeignKey('employe.id'))
    date_debut = db.Column(db.DateTime)
    date_fin = db.Column(db.DateTime)
    completee = db.Column(db.Boolean, default=False)
    priorite = db.Column(db.String(20))
    
    # Relations
    assignee = db.relationship('Employe', foreign_keys=[assignee_id])

# Modèle Badge
class Badge(db.Model):
    __tablename__ = 'badge'
    
    id = db.Column(db.Integer, primary_key=True)
    employe_id = db.Column(db.Integer, db.ForeignKey('employe.id'), nullable=False)
    chantier_id = db.Column(db.Integer, db.ForeignKey('chantier.id'))
    type_badge = db.Column(db.Enum(TypeBadge), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    localisation = db.Column(db.String(200))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    photo = db.Column(db.String(200))
    anomalie = db.Column(db.Boolean, default=False)
    commentaire = db.Column(db.Text)
    
    # Relations
    chantier = db.relationship('Chantier', backref='badges')

# Modèle Anomalie
class Anomalie(db.Model):
    __tablename__ = 'anomalie'
    
    id = db.Column(db.Integer, primary_key=True)
    badge_id = db.Column(db.Integer, db.ForeignKey('badge.id'))
    type_anomalie = db.Column(db.String(100))
    description = db.Column(db.Text)
    priorite = db.Column(db.Enum(PrioriteAnomalie), default=PrioriteAnomalie.MOYENNE)
    resolue = db.Column(db.Boolean, default=False)
    date_resolution = db.Column(db.DateTime)
    commentaire_resolution = db.Column(db.Text)
    
    # Relations
    badge = db.relationship('Badge', backref='anomalies')

# Modèle Devis
class Devis(db.Model):
    __tablename__ = 'devis'
    
    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.String(20), unique=True, nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    chantier_id = db.Column(db.Integer, db.ForeignKey('chantier.id'))
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    date_validite = db.Column(db.Date)
    montant_ht = db.Column(db.Float, nullable=False)
    taux_tva = db.Column(db.Float, default=20.0)
    montant_ttc = db.Column(db.Float, nullable=False)
    statut = db.Column(db.String(50), default='En attente')
    accepte = db.Column(db.Boolean, default=False)
    date_acceptation = db.Column(db.DateTime)
    conditions = db.Column(db.Text)
    
    # Relations
    chantier = db.relationship('Chantier', backref='devis_associes')
    lignes = db.relationship('LigneDevis', backref='devis', lazy='dynamic', cascade='all, delete-orphan')
    facture = db.relationship('Facture', backref='devis_origine', uselist=False)

# Modèle Ligne de Devis
class LigneDevis(db.Model):
    __tablename__ = 'ligne_devis'
    
    id = db.Column(db.Integer, primary_key=True)
    devis_id = db.Column(db.Integer, db.ForeignKey('devis.id'), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    quantite = db.Column(db.Float, nullable=False)
    unite = db.Column(db.String(20))
    prix_unitaire = db.Column(db.Float, nullable=False)
    montant = db.Column(db.Float, nullable=False)
    ordre = db.Column(db.Integer)

# Modèle Facture
class Facture(db.Model):
    __tablename__ = 'facture'
    
    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.String(20), unique=True, nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    chantier_id = db.Column(db.Integer, db.ForeignKey('chantier.id'))
    devis_id = db.Column(db.Integer, db.ForeignKey('devis.id'), unique=True)
    date_emission = db.Column(db.DateTime, default=datetime.utcnow)
    date_echeance = db.Column(db.Date)
    montant_ht = db.Column(db.Float, nullable=False)
    taux_tva = db.Column(db.Float, default=20.0)
    montant_ttc = db.Column(db.Float, nullable=False)
    statut = db.Column(db.Enum(StatutFacture), default=StatutFacture.BROUILLON)
    date_paiement = db.Column(db.DateTime)
    mode_paiement = db.Column(db.String(50))
    reference_paiement = db.Column(db.String(100))
    
    # Relations
    chantier = db.relationship('Chantier', backref='factures')
    lignes = db.relationship('LigneFacture', backref='facture', lazy='dynamic', cascade='all, delete-orphan')
    relances = db.relationship('RelanceFacture', backref='facture', lazy='dynamic')

# Modèle Ligne de Facture
class LigneFacture(db.Model):
    __tablename__ = 'ligne_facture'
    
    id = db.Column(db.Integer, primary_key=True)
    facture_id = db.Column(db.Integer, db.ForeignKey('facture.id'), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    quantite = db.Column(db.Float, nullable=False)
    unite = db.Column(db.String(20))
    prix_unitaire = db.Column(db.Float, nullable=False)
    montant = db.Column(db.Float, nullable=False)
    ordre = db.Column(db.Integer)

# Modèle Lead/Prospect
class Lead(db.Model):
    __tablename__ = 'lead'
    
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(200), nullable=False)
    entreprise = db.Column(db.String(200))
    email = db.Column(db.String(120))
    telephone = db.Column(db.String(20))
    source = db.Column(db.String(100))  # Site web, Salon, Recommandation, etc.
    projet = db.Column(db.Text)
    budget_estime = db.Column(db.Float)
    date_contact = db.Column(db.DateTime, default=datetime.utcnow)
    statut = db.Column(db.String(50), default='Nouveau')  # Nouveau, Contacté, Qualifié, Proposition, Gagné, Perdu
    commercial_id = db.Column(db.Integer, db.ForeignKey('employe.id'))
    date_relance = db.Column(db.Date)
    notes = db.Column(db.Text)
    converti_client = db.Column(db.Boolean, default=False)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'))
    
    # Relations
    commercial = db.relationship('Employe', foreign_keys=[commercial_id])
    client_converti = db.relationship('Client', foreign_keys=[client_id])

# Modèle Matériel/Ressource
class Materiel(db.Model):
    __tablename__ = 'materiel'
    
    id = db.Column(db.Integer, primary_key=True)
    code_materiel = db.Column(db.String(20), unique=True, nullable=False)
    nom = db.Column(db.String(200), nullable=False)
    categorie = db.Column(db.String(100))  # Véhicule, Outil, Machine, etc.
    marque = db.Column(db.String(100))
    modele = db.Column(db.String(100))
    numero_serie = db.Column(db.String(100))
    date_achat = db.Column(db.Date)
    valeur_achat = db.Column(db.Float)
    statut = db.Column(db.String(50), default='Disponible')  # Disponible, En service, Maintenance, Hors service
    localisation = db.Column(db.String(200))
    date_derniere_maintenance = db.Column(db.Date)
    date_prochaine_maintenance = db.Column(db.Date)
    kilometrage = db.Column(db.Integer)  # Pour les véhicules
    heures_utilisation = db.Column(db.Integer)  # Pour les machines
    photo = db.Column(db.String(200))
    
    # Relations
    affectations = db.relationship('AffectationMateriel', backref='materiel', lazy='dynamic')
    maintenances = db.relationship('MaintenanceMateriel', backref='materiel', lazy='dynamic')

# Modèle Affectation Matériel
class AffectationMateriel(db.Model):
    __tablename__ = 'affectation_materiel'
    
    id = db.Column(db.Integer, primary_key=True)
    materiel_id = db.Column(db.Integer, db.ForeignKey('materiel.id'), nullable=False)
    chantier_id = db.Column(db.Integer, db.ForeignKey('chantier.id'))
    employe_id = db.Column(db.Integer, db.ForeignKey('employe.id'))
    date_debut = db.Column(db.DateTime, default=datetime.utcnow)
    date_fin = db.Column(db.DateTime)
    retour_prevu = db.Column(db.Date)
    notes = db.Column(db.Text)
    
    # Relations
    employe = db.relationship('Employe', backref='materiels_affectes')

# Modèle Incident Sécurité
class IncidentSecurite(db.Model):
    __tablename__ = 'incident_securite'
    
    id = db.Column(db.Integer, primary_key=True)
    chantier_id = db.Column(db.Integer, db.ForeignKey('chantier.id'))
    employe_id = db.Column(db.Integer, db.ForeignKey('employe.id'))
    date_incident = db.Column(db.DateTime, default=datetime.utcnow)
    type_incident = db.Column(db.String(100))  # Accident, Presque accident, Danger identifié
    gravite = db.Column(db.String(50))  # Mineure, Modérée, Grave, Critique
    description = db.Column(db.Text, nullable=False)
    blessures = db.Column(db.Boolean, default=False)
    arret_travail = db.Column(db.Integer, default=0)  # Nombre de jours
    mesures_prises = db.Column(db.Text)
    photos = db.Column(db.Text)  # JSON des URLs des photos
    temoin = db.Column(db.String(200))
    rapport_externe = db.Column(db.Boolean, default=False)  # Déclaration autorités
    cloture = db.Column(db.Boolean, default=False)
    date_cloture = db.Column(db.DateTime)

# Modèle Fiche de Paie
class FichePaie(db.Model):
    __tablename__ = 'fiche_paie'
    
    id = db.Column(db.Integer, primary_key=True)
    employe_id = db.Column(db.Integer, db.ForeignKey('employe.id'), nullable=False)
    periode_debut = db.Column(db.Date, nullable=False)
    periode_fin = db.Column(db.Date, nullable=False)
    salaire_base = db.Column(db.Float, nullable=False)
    heures_travaillees = db.Column(db.Float)
    heures_supplementaires = db.Column(db.Float, default=0)
    primes = db.Column(db.Float, default=0)
    cotisations_salariales = db.Column(db.Float)
    cotisations_patronales = db.Column(db.Float)
    net_payer = db.Column(db.Float, nullable=False)
    date_paiement = db.Column(db.Date)
    mode_paiement = db.Column(db.String(50))
    fichier_pdf = db.Column(db.String(200))
    
# Modèle Photo Chantier
class PhotoChantier(db.Model):
    __tablename__ = 'photo_chantier'
    
    id = db.Column(db.Integer, primary_key=True)
    chantier_id = db.Column(db.Integer, db.ForeignKey('chantier.id'), nullable=False)
    titre = db.Column(db.String(200))
    description = db.Column(db.Text)
    fichier = db.Column(db.String(200), nullable=False)
    type_photo = db.Column(db.String(50))  # Avant, Pendant, Après
    date_prise = db.Column(db.DateTime, default=datetime.utcnow)
    uploade_par_id = db.Column(db.Integer, db.ForeignKey('employe.id'))
    
    # Relations
    uploade_par = db.relationship('Employe', foreign_keys=[uploade_par_id])

# Modèle Document Chantier
class DocumentChantier(db.Model):
    __tablename__ = 'document_chantier'
    
    id = db.Column(db.Integer, primary_key=True)
    chantier_id = db.Column(db.Integer, db.ForeignKey('chantier.id'), nullable=False)
    nom = db.Column(db.String(200), nullable=False)
    type_document = db.Column(db.String(100))  # Plan, Permis, Contrat, etc.
    fichier = db.Column(db.String(200), nullable=False)
    date_upload = db.Column(db.DateTime, default=datetime.utcnow)
    uploade_par_id = db.Column(db.Integer, db.ForeignKey('employe.id'))
    
    # Relations
    uploade_par = db.relationship('Employe', foreign_keys=[uploade_par_id])

# Modèle Maintenance Matériel
class MaintenanceMateriel(db.Model):
    __tablename__ = 'maintenance_materiel'
    
    id = db.Column(db.Integer, primary_key=True)
    materiel_id = db.Column(db.Integer, db.ForeignKey('materiel.id'), nullable=False)
    date_maintenance = db.Column(db.Date, nullable=False)
    type_maintenance = db.Column(db.String(100))  # Préventive, Curative
    description = db.Column(db.Text)
    cout = db.Column(db.Float)
    effectuee_par = db.Column(db.String(200))
    prochaine_maintenance = db.Column(db.Date)

# Modèle Relance Facture
class RelanceFacture(db.Model):
    __tablename__ = 'relance_facture'
    
    id = db.Column(db.Integer, primary_key=True)
    facture_id = db.Column(db.Integer, db.ForeignKey('facture.id'), nullable=False)
    date_relance = db.Column(db.DateTime, default=datetime.utcnow)
    type_relance = db.Column(db.String(50))  # Email, Courrier, Téléphone
    message = db.Column(db.Text)
    effectuee_par_id = db.Column(db.Integer, db.ForeignKey('employe.id'))
    
    # Relations
    effectuee_par = db.relationship('Employe', foreign_keys=[effectuee_par_id])

# Modèle Message Communication
class Message(db.Model):
    __tablename__ = 'message'
    
    id = db.Column(db.Integer, primary_key=True)
    chantier_id = db.Column(db.Integer, db.ForeignKey('chantier.id'))
    expediteur_id = db.Column(db.Integer, db.ForeignKey('employe.id'), nullable=False)
    contenu = db.Column(db.Text, nullable=False)
    date_envoi = db.Column(db.DateTime, default=datetime.utcnow)
    lu = db.Column(db.Boolean, default=False)
    important = db.Column(db.Boolean, default=False)
    
    # Relations
    chantier = db.relationship('Chantier', backref='messages')
    expediteur = db.relationship('Employe', foreign_keys=[expediteur_id])

# Modèle Paramètres
class Parametre(db.Model):
    __tablename__ = 'parametre'
    
    id = db.Column(db.Integer, primary_key=True)
    cle = db.Column(db.String(100), unique=True, nullable=False)
    valeur = db.Column(db.Text)
    description = db.Column(db.String(500))
    type_parametre = db.Column(db.String(50))  # Système, Entreprise, Module
    modifiable = db.Column(db.Boolean, default=True)
    
# Fonction pour créer les tables
def init_db(app):
    with app.app_context():
        db.create_all()
        print("✅ Base de données initialisée avec succès!")
        
# Fonction pour créer des données de démonstration
def seed_demo_data(app):
    with app.app_context():
        # Vérifier si des données existent déjà
        if User.query.first():
            print("ℹ️ Des données existent déjà dans la base")
            return
        
        # Créer un administrateur
        admin = User(
            username='admin',
            email='admin@globibat.ch',
            role='admin'
        )
        admin.set_password('admin123')
        db.session.add(admin)
        
        # Créer des employés
        employes_data = [
            {'nom': 'Dupont', 'prenom': 'Jean', 'poste': 'Chef de chantier', 'matricule': 'EMP001'},
            {'nom': 'Martin', 'prenom': 'Marie', 'poste': 'Conducteur de travaux', 'matricule': 'EMP002'},
            {'nom': 'Bernard', 'prenom': 'Pierre', 'poste': 'Maçon', 'matricule': 'EMP003'},
            {'nom': 'Dubois', 'prenom': 'Sophie', 'poste': 'Électricien', 'matricule': 'EMP004'},
            {'nom': 'Thomas', 'prenom': 'Luc', 'poste': 'Plombier', 'matricule': 'EMP005'},
        ]
        
        employes = []
        for emp_data in employes_data:
            emp = Employe(
                nom=emp_data['nom'],
                prenom=emp_data['prenom'],
                poste=emp_data['poste'],
                matricule=emp_data['matricule'],
                email=f"{emp_data['prenom'].lower()}.{emp_data['nom'].lower()}@globibat.ch",
                telephone='0123456789',
                departement='Construction',
                salaire_base=3500.00,
                statut=StatutEmploye.ACTIF
            )
            employes.append(emp)
            db.session.add(emp)
        
        # Créer des clients
        clients_data = [
            {'raison_sociale': 'Mairie de Genève', 'type_client': 'Public', 'code_client': 'CLI001'},
            {'raison_sociale': 'SCI Les Acacias', 'type_client': 'Entreprise', 'code_client': 'CLI002'},
            {'raison_sociale': 'M. Durand', 'type_client': 'Particulier', 'code_client': 'CLI003'},
        ]
        
        clients = []
        for cli_data in clients_data:
            client = Client(
                raison_sociale=cli_data['raison_sociale'],
                type_client=cli_data['type_client'],
                code_client=cli_data['code_client'],
                email='contact@client.ch',
                telephone='0123456789',
                ville='Genève',
                code_postal='1200'
            )
            clients.append(client)
            db.session.add(client)
        
        db.session.commit()
        
        # Créer des chantiers
        chantiers_data = [
            {
                'nom': 'Rénovation École Primaire',
                'code_chantier': 'CH001',
                'client': clients[0],
                'budget_initial': 250000,
                'statut': StatutChantier.EN_COURS,
                'avancement': 65
            },
            {
                'nom': 'Construction Villa',
                'code_chantier': 'CH002',
                'client': clients[2],
                'budget_initial': 450000,
                'statut': StatutChantier.EN_COURS,
                'avancement': 30
            },
            {
                'nom': 'Extension Bureaux',
                'code_chantier': 'CH003',
                'client': clients[1],
                'budget_initial': 180000,
                'statut': StatutChantier.PLANIFIE,
                'avancement': 0
            },
        ]
        
        for ch_data in chantiers_data:
            chantier = Chantier(
                nom=ch_data['nom'],
                code_chantier=ch_data['code_chantier'],
                client=ch_data['client'],
                budget_initial=ch_data['budget_initial'],
                statut=ch_data['statut'],
                avancement=ch_data['avancement'],
                chef_chantier=employes[0],
                date_debut=date.today(),
                date_fin_prevue=date(2025, 12, 31),
                ville='Genève',
                adresse='123 Rue du Chantier'
            )
            
            # Affecter des employés
            chantier.employes.extend(employes[:3])
            db.session.add(chantier)
        
        # Créer des badges
        for emp in employes[:3]:
            badge = Badge(
                employe=emp,
                type_badge=TypeBadge.ENTREE,
                timestamp=datetime.utcnow(),
                localisation='Chantier principal'
            )
            db.session.add(badge)
        
        # Créer quelques factures
        facture1 = Facture(
            numero='FAC2025001',
            client=clients[0],
            montant_ht=50000,
            montant_ttc=60000,
            statut=StatutFacture.ENVOYEE,
            date_echeance=date(2025, 1, 31)
        )
        db.session.add(facture1)
        
        facture2 = Facture(
            numero='FAC2025002',
            client=clients[1],
            montant_ht=25000,
            montant_ttc=30000,
            statut=StatutFacture.PAYEE,
            date_paiement=datetime.utcnow()
        )
        db.session.add(facture2)
        
        # Créer des leads
        lead1 = Lead(
            nom='Prospect Important',
            entreprise='Grande Entreprise SA',
            email='contact@entreprise.ch',
            telephone='0123456789',
            source='Site web',
            projet='Construction nouveau siège',
            budget_estime=1500000,
            statut='Qualifié'
        )
        db.session.add(lead1)
        
        # Créer du matériel
        materiels_data = [
            {'nom': 'Camion Benne', 'code_materiel': 'MAT001', 'categorie': 'Véhicule'},
            {'nom': 'Pelleteuse', 'code_materiel': 'MAT002', 'categorie': 'Machine'},
            {'nom': 'Bétonnière', 'code_materiel': 'MAT003', 'categorie': 'Machine'},
        ]
        
        for mat_data in materiels_data:
            materiel = Materiel(
                nom=mat_data['nom'],
                code_materiel=mat_data['code_materiel'],
                categorie=mat_data['categorie'],
                statut='Disponible',
                valeur_achat=50000
            )
            db.session.add(materiel)
        
        # Sauvegarder toutes les données
        db.session.commit()
        print("✅ Données de démonstration créées avec succès!")
        return True

# Exporter tous les modèles pour faciliter les imports
__all__ = [
    'db',
    'init_db',
    'seed_demo_data',
    'User',
    'Employe',
    'Client',
    'Chantier',
    'Devis',
    'Facture',
    'LigneFacture',
    'Badge',
    'Lead',
    'Materiel',
    'MaintenanceMateriel',
    'Consommable',
    'IncidentSecurite',
    'FichePaie',
    'PhotoChantier',
    'DocumentChantier',
    'RelanceFacture',
    'Message',
    'Parametre',
    'StatutEmploye',
    'StatutChantier',
    'StatutFacture',
    'TypeBadge',
    'PrioriteAnomalie'
]