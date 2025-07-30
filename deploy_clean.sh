#!/bin/bash

# Script de déploiement de la version clean (sans 2FA ni email)

echo "🚀 Déploiement de la version simplifiée..."

# Arrêter l'application
supervisorctl stop globibat

# Sauvegarder l'ancienne version
cp app.py app_backup_$(date +%Y%m%d_%H%M%S).py

# Renommer la base de données
if [ -f badgeage.db ]; then
    mv badgeage.db badgeage_old_$(date +%Y%m%d_%H%M%S).db
    echo "✅ Ancienne base de données sauvegardée"
fi

# Si app_clean.py existe, l'utiliser
if [ -f app_clean.py ]; then
    cp app_clean.py app.py
    echo "✅ app_clean.py copié vers app.py"
fi

# Supprimer les fichiers inutiles
rm -f notifications.py
rm -f charts.py
rm -f pdf_generator.py
rm -f tasks.py

# Créer config.py minimal si nécessaire
if [ ! -f config.py ]; then
cat > config.py << 'EOF'
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'cle-secrete-globibat-2024'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///badgeage.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_COOKIE_SECURE = False
    
    # Config entreprise
    COMPANY_NAME = 'Globibat'
    HEURE_ARRIVEE_MAX = '09:00'
    HEURE_RETOUR_MAX = '14:00'
EOF
echo "✅ config.py créé"
fi

# Créer le template modifier_employe.html s'il n'existe pas
if [ ! -f templates/modifier_employe.html ]; then
cat > templates/modifier_employe.html << 'EOF'
{% extends "base.html" %}

{% block title %}Modifier Employé{% endblock %}

{% block content %}
<div class="container mt-4">
    <h2>Modifier l'employé</h2>
    
    <form method="POST" class="mt-4">
        <div class="row">
            <div class="col-md-6">
                <div class="mb-3">
                    <label for="matricule" class="form-label">Matricule</label>
                    <input type="text" class="form-control" id="matricule" name="matricule" value="{{ employe.matricule }}" required>
                </div>
                
                <div class="mb-3">
                    <label for="nom" class="form-label">Nom</label>
                    <input type="text" class="form-control" id="nom" name="nom" value="{{ employe.nom }}" required>
                </div>
                
                <div class="mb-3">
                    <label for="prenom" class="form-label">Prénom</label>
                    <input type="text" class="form-control" id="prenom" name="prenom" value="{{ employe.prenom }}" required>
                </div>
            </div>
            
            <div class="col-md-6">
                <div class="mb-3">
                    <label for="departement" class="form-label">Département</label>
                    <input type="text" class="form-control" id="departement" name="departement" value="{{ employe.departement }}">
                </div>
                
                <div class="mb-3">
                    <label for="email" class="form-label">Email</label>
                    <input type="email" class="form-control" id="email" name="email" value="{{ employe.email }}">
                </div>
                
                <div class="mb-3">
                    <label for="telephone" class="form-label">Téléphone</label>
                    <input type="tel" class="form-control" id="telephone" name="telephone" value="{{ employe.telephone }}">
                </div>
                
                <div class="form-check mb-3">
                    <input class="form-check-input" type="checkbox" id="actif" name="actif" {% if employe.actif %}checked{% endif %}>
                    <label class="form-check-label" for="actif">
                        Employé actif
                    </label>
                </div>
            </div>
        </div>
        
        <div class="mt-3">
            <button type="submit" class="btn btn-primary">Enregistrer les modifications</button>
            <a href="{{ url_for('liste_employes') }}" class="btn btn-secondary">Annuler</a>
        </div>
    </form>
</div>
{% endblock %}
EOF
echo "✅ Template modifier_employe.html créé"
fi

# Redémarrer l'application
supervisorctl start globibat

# Attendre que l'application démarre
sleep 3

# Créer l'admin automatiquement
python3 << EOF
from app import app, db, Admin
try:
    with app.app_context():
        db.create_all()
        admin = Admin.query.filter_by(username='Globibat').first()
        if not admin:
            admin = Admin(username='Globibat')
            admin.set_password('Miser1597532684$')
            db.session.add(admin)
            db.session.commit()
            print("✅ Admin Globibat créé avec succès!")
        else:
            print("ℹ️ Admin Globibat existe déjà")
except Exception as e:
    print(f"❌ Erreur: {e}")
EOF

# Vérifier le statut
echo -e "\n📊 Statut de l'application:"
supervisorctl status globibat

echo -e "\n✅ Déploiement terminé!"
echo "🌐 Accédez à http://148.230.105.25"
echo "👤 Connexion admin: http://148.230.105.25/admin-globibat"
echo "   Username: Globibat"
echo "   Password: Miser1597532684$" 