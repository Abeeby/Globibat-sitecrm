"""
Point d'entrée principal de l'application Globibat CRM
"""
import os
from app import create_app, db
from app.models import User, Role
from flask_migrate import Migrate, init, migrate, upgrade

# Déterminer l'environnement
env = os.environ.get('FLASK_ENV', 'production')
app = create_app(env)
migrate_instance = Migrate(app, db)

@app.cli.command()
def init_db():
    """Initialiser la base de données"""
    with app.app_context():
        # Créer toutes les tables
        db.create_all()
        
        # Insérer les rôles par défaut
        Role.insert_roles()
        
        # Créer un utilisateur admin par défaut
        admin_role = Role.query.filter_by(name='Admin').first()
        admin = User.query.filter_by(username='admin').first()
        
        if not admin:
            admin = User(
                username='admin',
                email='admin@globibat.ch',
                first_name='Admin',
                last_name='Globibat',
                role=admin_role
            )
            admin.set_password('Admin2024!')  # À changer immédiatement !
            db.session.add(admin)
            db.session.commit()
            print("Base de données initialisée avec succès!")
            print("Utilisateur admin créé: admin / Admin2024!")
            print("IMPORTANT: Changez ce mot de passe immédiatement!")
        else:
            print("La base de données existe déjà.")

@app.cli.command()
def create_admin():
    """Créer un nouvel administrateur"""
    import getpass
    
    username = input("Nom d'utilisateur: ")
    email = input("Email: ")
    password = getpass.getpass("Mot de passe: ")
    
    admin_role = Role.query.filter_by(name='Admin').first()
    
    user = User(
        username=username,
        email=email,
        role=admin_role
    )
    user.set_password(password)
    
    db.session.add(user)
    db.session.commit()
    
    print(f"Administrateur {username} créé avec succès!")

@app.cli.command()
def test():
    """Lancer les tests"""
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)

@app.shell_context_processor
def make_shell_context():
    """Contexte pour le shell Flask"""
    return {
        'db': db,
        'User': User,
        'Role': Role,
        'Client': Client,
        'Project': Project,
        'Invoice': Invoice,
        'Employee': Employee
    }

# Gestion des erreurs
@app.errorhandler(404)
def not_found(error):
    """Page 404"""
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    """Erreur serveur"""
    db.session.rollback()
    return render_template('errors/500.html'), 500

# Headers de sécurité
@app.after_request
def set_security_headers(response):
    """Ajouter les headers de sécurité"""
    if app.config.get('ENV') == 'production':
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Content-Security-Policy'] = "default-src 'self' 'unsafe-inline' 'unsafe-eval' https: data:"
    return response

# Contexte global pour les templates
@app.context_processor
def inject_globals():
    """Injecter des variables globales dans tous les templates"""
    return {
        'company_name': app.config['COMPANY_NAME'],
        'current_year': datetime.now().year,
        'seo_suffix': app.config['SEO_TITLE_SUFFIX'],
        'languages': app.config['LANGUAGES']
    }

if __name__ == '__main__':
    # En développement uniquement
    if env == 'development':
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=True
        )
    else:
        print("En production, utilisez un serveur WSGI comme Gunicorn")
        print("Exemple: gunicorn -w 4 -b 0.0.0.0:5000 run:app")