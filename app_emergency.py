from flask import Flask, render_template_string, request, redirect, url_for

app = Flask(__name__)
app.config['SECRET_KEY'] = 'cle-secrete-globibat-2024'

# Template HTML de base
BASE_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Globibat Badge System</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <nav class="navbar navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="/">Globibat Badge System</a>
        </div>
    </nav>
    <div class="container mt-4">
        {% block content %}{% endblock %}
    </div>
</body>
</html>
'''

INDEX_TEMPLATE = '''
{% extends base %}
{% block content %}
<h1>Bienvenue sur Globibat Badge System</h1>
<div class="row mt-4">
    <div class="col-md-4">
        <div class="card">
            <div class="card-body">
                <h5 class="card-title">Badgeage</h5>
                <p class="card-text">Interface de badgeage pour les employés</p>
                <a href="/badge" class="btn btn-primary">Accéder</a>
            </div>
        </div>
    </div>
    <div class="col-md-4">
        <div class="card">
            <div class="card-body">
                <h5 class="card-title">Administration</h5>
                <p class="card-text">Gestion du système</p>
                <a href="/admin-globibat" class="btn btn-warning">Connexion</a>
            </div>
        </div>
    </div>
</div>
{% endblock %}
'''

BADGE_TEMPLATE = '''
{% extends base %}
{% block content %}
<h2>Badgeage Employé</h2>
<div class="alert alert-info">
    Système temporaire - Base de données en maintenance
</div>
<form method="POST" class="mt-4">
    <div class="mb-3">
        <label for="matricule" class="form-label">Matricule</label>
        <input type="text" class="form-control" id="matricule" name="matricule" required>
    </div>
    <div class="mb-3">
        <label for="type_badge" class="form-label">Type de badgeage</label>
        <select class="form-control" id="type_badge" name="type_badge" required>
            <option value="arrivee_matin">Arrivée Matin</option>
            <option value="depart_midi">Départ Midi</option>
            <option value="arrivee_apres_midi">Arrivée Après-midi</option>
            <option value="depart_soir">Départ Soir</option>
        </select>
    </div>
    <button type="submit" class="btn btn-success">Badger</button>
</form>
{% endblock %}
'''

LOGIN_TEMPLATE = '''
{% extends base %}
{% block content %}
<h2>Connexion Administration</h2>
<form method="POST" class="mt-4">
    <div class="mb-3">
        <label for="username" class="form-label">Nom d'utilisateur</label>
        <input type="text" class="form-control" id="username" name="username" required>
    </div>
    <div class="mb-3">
        <label for="password" class="form-label">Mot de passe</label>
        <input type="password" class="form-control" id="password" name="password" required>
    </div>
    <button type="submit" class="btn btn-primary">Se connecter</button>
</form>
{% endblock %}
'''

@app.route('/')
def index():
    return render_template_string(INDEX_TEMPLATE, base=BASE_TEMPLATE)

@app.route('/badge', methods=['GET', 'POST'])
def badge():
    if request.method == 'POST':
        # Temporaire - juste afficher un message
        return '<div class="container mt-4"><div class="alert alert-success">Badgeage enregistré (mode temporaire)</div><a href="/badge">Nouveau badgeage</a></div>'
    return render_template_string(BADGE_TEMPLATE, base=BASE_TEMPLATE)

@app.route('/admin-globibat', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == 'Globibat' and password == 'Miser1597532684$':
            return '<div class="container mt-4"><div class="alert alert-success">Connexion réussie ! Interface admin en construction...</div><a href="/">Retour</a></div>'
        else:
            return '<div class="container mt-4"><div class="alert alert-danger">Identifiants incorrects</div><a href="/admin-globibat">Réessayer</a></div>'
    return render_template_string(LOGIN_TEMPLATE, base=BASE_TEMPLATE)

@app.route('/admin')
def admin():
    return '<div class="container mt-4"><h1>Interface Admin</h1><p>En construction...</p><a href="/">Retour</a></div>'

# Routes stub pour éviter les erreurs
@app.route('/employe')
def employe():
    return redirect('/')

@app.route('/employe/login')
def employe_login():
    return redirect('/badge')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 