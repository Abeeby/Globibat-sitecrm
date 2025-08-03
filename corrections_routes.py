#!/usr/bin/env python
"""
Script pour corriger les routes et redirections
dans la nouvelle structure
"""

import os
import re

def fix_routes():
    """Corrige les routes dans les fichiers"""
    
    # Corrections à appliquer
    replacements = [
        # auth.py - Correction des redirections après login
        {
            'file': 'app/views/auth.py',
            'old': "return redirect(url_for('main.dashboard'))",
            'new': "return redirect(url_for('main.dashboard'))"  # main.dashboard pointe maintenant vers /crm/dashboard
        },
        # main.py - Correction déjà faite
        
        # templates - Mise à jour des liens
        {
            'file': 'app/templates/base.html',
            'old': 'href="{{ url_for(\'main.dashboard\') }}"',
            'new': 'href="{{ url_for(\'main.dashboard\') }}"'
        },
        {
            'file': 'app/templates/base.html',
            'old': 'href="{{ url_for(\'badge.index\') }}"',
            'new': 'href="{{ url_for(\'badge.index\') }}"'
        },
        # Corriger les URLs dans intranet.html pour utiliser les bonnes routes
        {
            'file': 'app/templates/website/intranet.html',
            'old': 'href="/crm/login"',
            'new': 'href="{{ url_for(\'auth.login\') }}"'
        },
        {
            'file': 'app/templates/website/intranet.html', 
            'old': 'href="/employee/badge"',
            'new': 'href="{{ url_for(\'badge.index\') }}"'
        }
    ]
    
    # Créer le fichier run.py avec la bonne redirection
    run_py_content = '''# Ajouter cette route dans run.py après app = create_app()

@app.route('/login')
def login_redirect():
    """Redirection de l'ancienne URL login"""
    return redirect(url_for('auth.login'))

# Route pour accès rapide au CRM
@app.route('/crm')
def crm_redirect():
    """Redirection vers le login CRM"""
    return redirect(url_for('auth.login'))
'''
    
    print("Corrections à appliquer:")
    print("========================")
    print(run_py_content)
    print("\nAjouter ces routes dans run.py après 'app = create_app()'")
    
    # Créer un fichier de correction pour le formulaire de contact
    contact_fix = '''
# Dans app/templates/website/index.html
# Modifier le formulaire de contact pour ajouter les attributs name :

<form class="contact-form" action="/contact" method="POST">
    <input type="text" name="name" class="form-control" placeholder="Nom complet" required>
    <input type="email" name="email" class="form-control" placeholder="Email" required>
    <input type="tel" name="phone" class="form-control" placeholder="Téléphone">
    <select name="project_type" class="form-control">
        <option>Type de projet</option>
        ...
    </select>
    <textarea name="message" class="form-control" rows="5" placeholder="Décrivez votre projet..." required></textarea>
</form>
'''
    
    print("\nCorrection du formulaire de contact:")
    print("====================================")
    print(contact_fix)

if __name__ == "__main__":
    fix_routes()