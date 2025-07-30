#!/bin/bash

cd /var/www/globibat/templates

# 1. statistiques.html
cat > statistiques.html << 'EOF'
{% extends "base.html" %}

{% block title %}Statistiques Avancées{% endblock %}

{% block content %}
<div class="container mt-4">
    <h2>Statistiques Avancées</h2>
    
    <div class="row mt-4">
        <div class="col-md-6">
            <div id="presence_chart"></div>
        </div>
        <div class="col-md-6">
            <div id="hours_distribution"></div>
        </div>
    </div>
    
    <div class="row mt-4">
        <div class="col-md-4">
            <div id="punctuality_gauge"></div>
        </div>
        <div class="col-md-8">
            <div id="monthly_summary"></div>
        </div>
    </div>
</div>

<script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
<script>
    // Charger les graphiques
    const charts = {{ charts | tojson }};
    
    if (charts.presence_chart) {
        Plotly.newPlot('presence_chart', JSON.parse(charts.presence_chart));
    }
    if (charts.hours_distribution) {
        Plotly.newPlot('hours_distribution', JSON.parse(charts.hours_distribution));
    }
    if (charts.punctuality_gauge) {
        Plotly.newPlot('punctuality_gauge', JSON.parse(charts.punctuality_gauge));
    }
    if (charts.monthly_summary) {
        Plotly.newPlot('monthly_summary', JSON.parse(charts.monthly_summary));
    }
</script>
{% endblock %}
EOF

# 2. employe_home.html
cat > employe_home.html << 'EOF'
{% extends "base.html" %}

{% block title %}Espace Employé{% endblock %}

{% block content %}
<div class="container mt-5">
    <div class="row justify-content-center">
        <div class="col-md-8">
            <h2 class="text-center mb-4">Espace Employé</h2>
            
            <div class="row">
                <div class="col-md-6 mb-3">
                    <div class="card h-100">
                        <div class="card-body text-center">
                            <i class="fas fa-sign-in-alt fa-3x text-primary mb-3"></i>
                            <h5 class="card-title">Se connecter</h5>
                            <p class="card-text">Accédez à votre espace personnel</p>
                            <a href="/employe/login" class="btn btn-primary">Connexion</a>
                        </div>
                    </div>
                </div>
                
                <div class="col-md-6 mb-3">
                    <div class="card h-100">
                        <div class="card-body text-center">
                            <i class="fas fa-id-badge fa-3x text-success mb-3"></i>
                            <h5 class="card-title">Badge Rapide</h5>
                            <p class="card-text">Badgez directement sans connexion</p>
                            <a href="/badge" class="btn btn-success">Badger</a>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
EOF

# 3. employe_login.html
cat > employe_login.html << 'EOF'
{% extends "base.html" %}

{% block title %}Connexion Employé{% endblock %}

{% block content %}
<div class="container mt-5">
    <div class="row justify-content-center">
        <div class="col-md-6">
            <div class="card">
                <div class="card-header">
                    <h4>Connexion Employé</h4>
                </div>
                <div class="card-body">
                    <form method="POST">
                        <div class="mb-3">
                            <label for="matricule" class="form-label">Matricule</label>
                            <input type="text" class="form-control" id="matricule" name="matricule" required>
                        </div>
                        <button type="submit" class="btn btn-primary">Se connecter</button>
                    </form>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
EOF

# 4. employe_dashboard.html
cat > employe_dashboard.html << 'EOF'
{% extends "base.html" %}

{% block title %}Mon Tableau de Bord{% endblock %}

{% block content %}
<div class="container mt-4">
    <h2>Bienvenue {{ employe.prenom }} {{ employe.nom }}</h2>
    <p class="text-muted">Matricule: {{ employe.matricule }}</p>
    
    <div class="row mt-4">
        <div class="col-md-4">
            <div class="card">
                <div class="card-body">
                    <h5 class="card-title">Heures ce mois</h5>
                    <h3>{{ stats.heures_mois|default(0) }}h</h3>
                </div>
            </div>
        </div>
        <div class="col-md-4">
            <div class="card">
                <div class="card-body">
                    <h5 class="card-title">Retards</h5>
                    <h3>{{ stats.retards|default(0) }}</h3>
                </div>
            </div>
        </div>
        <div class="col-md-4">
            <div class="card">
                <div class="card-body">
                    <h5 class="card-title">Jours travaillés</h5>
                    <h3>{{ stats.jours_travailles|default(0) }}</h3>
                </div>
            </div>
        </div>
    </div>
    
    <div class="mt-4">
        <h4>Historique récent</h4>
        <table class="table">
            <thead>
                <tr>
                    <th>Date</th>
                    <th>Arrivée Matin</th>
                    <th>Départ Midi</th>
                    <th>Arrivée Après-midi</th>
                    <th>Départ Soir</th>
                    <th>Heures</th>
                </tr>
            </thead>
            <tbody>
                {% for p in pointages %}
                <tr>
                    <td>{{ p.date_pointage.strftime('%d/%m/%Y') }}</td>
                    <td>{{ p.arrivee_matin.strftime('%H:%M') if p.arrivee_matin else '-' }}</td>
                    <td>{{ p.depart_midi.strftime('%H:%M') if p.depart_midi else '-' }}</td>
                    <td>{{ p.arrivee_apres_midi.strftime('%H:%M') if p.arrivee_apres_midi else '-' }}</td>
                    <td>{{ p.depart_soir.strftime('%H:%M') if p.depart_soir else '-' }}</td>
                    <td>{{ p.heures_travaillees }}h</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</div>
{% endblock %}
EOF

# 5. verify_2fa.html
cat > verify_2fa.html << 'EOF'
{% extends "base.html" %}

{% block title %}Vérification 2FA{% endblock %}

{% block content %}
<div class="container mt-5">
    <div class="row justify-content-center">
        <div class="col-md-6">
            <div class="card">
                <div class="card-header">
                    <h4>Vérification en deux étapes</h4>
                </div>
                <div class="card-body">
                    <form method="POST">
                        <div class="mb-3">
                            <label for="token" class="form-label">Code à 6 chiffres</label>
                            <input type="text" class="form-control" id="token" name="token" 
                                   maxlength="6" pattern="[0-9]{6}" required autofocus>
                            <div class="form-text">Entrez le code de votre application d'authentification</div>
                        </div>
                        <button type="submit" class="btn btn-primary">Vérifier</button>
                    </form>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
EOF

# 6. setup_2fa.html
cat > setup_2fa.html << 'EOF'
{% extends "base.html" %}

{% block title %}Configuration 2FA{% endblock %}

{% block content %}
<div class="container mt-5">
    <div class="row justify-content-center">
        <div class="col-md-8">
            <div class="card">
                <div class="card-header">
                    <h4>Configurer l'authentification à deux facteurs</h4>
                </div>
                <div class="card-body">
                    <div class="text-center mb-4">
                        <img src="data:image/png;base64,{{ qr_code }}" alt="QR Code 2FA">
                    </div>
                    
                    <p>Scannez ce QR code avec votre application d'authentification (Google Authenticator, Authy, etc.)</p>
                    
                    <div class="alert alert-info">
                        <strong>Clé secrète:</strong> <code>{{ secret }}</code>
                        <br>
                        <small>Conservez cette clé en lieu sûr</small>
                    </div>
                    
                    <form method="POST" action="/admin/confirm-2fa">
                        <div class="mb-3">
                            <label for="token" class="form-label">Code de vérification</label>
                            <input type="text" class="form-control" id="token" name="token" 
                                   maxlength="6" pattern="[0-9]{6}" required>
                            <div class="form-text">Entrez le code à 6 chiffres de votre application</div>
                        </div>
                        <button type="submit" class="btn btn-success">Activer 2FA</button>
                        <a href="/admin" class="btn btn-secondary">Annuler</a>
                    </form>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
EOF

# 7. fiches_paie.html
cat > fiches_paie.html << 'EOF'
{% extends "base.html" %}

{% block title %}Fiches de Paie{% endblock %}

{% block content %}
<div class="container mt-4">
    <h2>Génération des Fiches de Paie</h2>
    <p>Mois en cours: {{ mois }}/{{ annee }}</p>
    
    <table class="table">
        <thead>
            <tr>
                <th>Employé</th>
                <th>Heures Travaillées</th>
                <th>Salaire Net (Approx.)</th>
                <th>Action</th>
            </tr>
        </thead>
        <tbody>
            {% for e in employes %}
            <tr>
                <td>{{ e.nom }} {{ e.prenom }}</td>
                <td>{{ e.heures_mois|default(0) }}h</td>
                <td>{{ "%.2f"|format(e.salaire_net|default(0)) }} €</td>
                <td>
                    <a href="/admin/fiche-paie/{{ e.id }}" class="btn btn-sm btn-primary">
                        <i class="fas fa-file-pdf"></i> Générer PDF
                    </a>
                </td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>
{% endblock %}
EOF

echo "✅ Templates créés avec succès !" 