#!/bin/bash

# Script de déploiement corrigé pour Ubuntu (python3)

echo "🚀 Déploiement de la version simplifiée..."

cd /var/www/globibat

# Activer l'environnement virtuel
source venv/bin/activate

# Arrêter l'application
supervisorctl stop globibat

# Sauvegarder l'ancienne version
cp app.py app_backup_$(date +%Y%m%d_%H%M%S).py 2>/dev/null || echo "Pas de app.py à sauvegarder"

# Renommer la base de données
if [ -f badgeage.db ]; then
    mv badgeage.db badgeage_old_$(date +%Y%m%d_%H%M%S).db
    echo "✅ Ancienne base de données sauvegardée"
fi

# Copier la version clean si elle existe
if [ -f app_clean.py ]; then
    cp app_clean.py app.py
    echo "✅ app_clean.py copié vers app.py"
else
    echo "⚠️  app_clean.py non trouvé, utilisez FileZilla pour le transférer"
fi

# Créer config.py si nécessaire
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

# Créer le template modifier_employe.html
mkdir -p templates
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

# Supprimer les fichiers inutiles
rm -f notifications.py charts.py pdf_generator.py tasks.py 2>/dev/null

# Redémarrer l'application
supervisorctl start globibat

# Attendre un peu
sleep 3

# Créer l'admin avec python3
echo "🔄 Création du compte admin..."
python3 << 'PYTHON_SCRIPT'
try:
    from app import app, db, Admin
    with app.app_context():
        db.create_all()
        
        # Vérifier si l'admin existe déjà
        admin = Admin.query.filter_by(username='Globibat').first()
        if not admin:
            admin = Admin(username='Globibat')
            admin.set_password('Miser1597532684$')
            db.session.add(admin)
            db.session.commit()
            print("✅ Admin Globibat créé avec succès!")
        else:
            print("ℹ️  Admin Globibat existe déjà")
except Exception as e:
    print(f"❌ Erreur lors de la création de l'admin: {e}")
    print("   Vous devrez le créer manuellement")
PYTHON_SCRIPT

# Vérifier le statut
echo -e "\n📊 Statut de l'application:"
supervisorctl status globibat

echo -e "\n✅ Déploiement terminé!"
echo "🌐 Accédez à http://148.230.105.25"
echo "👤 Connexion admin: http://148.230.105.25/admin-globibat"
echo "   Username: Globibat"
echo "   Password: Miser1597532684$" 