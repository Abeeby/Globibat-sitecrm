"""
Routes pour le site web public de Globibat
Séparé du système interne (CRM/Badge)
"""

from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_mail import Message
from app import mail
from datetime import datetime

# Créer le blueprint pour le site web public
website_bp = Blueprint('website', __name__)

@website_bp.route('/')
def index():
    """Page d'accueil du site web public"""
    # Meta données SEO
    seo_data = {
        'title': 'Globibat SA - Entreprise Générale de Construction | Nyon, Suisse Romande',
        'description': 'Globibat SA - Votre entreprise générale de construction à Nyon. Spécialistes en rénovation, construction neuve et maçonnerie en Suisse romande. Plus de 15 ans d\'expérience.',
        'keywords': 'construction suisse romande, entreprise construction nyon, rénovation nyon, maçonnerie suisse romande, entreprise générale bâtiment, construction vaud, globibat',
        'canonical': request.url,
        'og_image': url_for('static', filename='images/globibat-og.jpg', _external=True)
    }
    
    return render_template('website/index.html', seo_data=seo_data)

@website_bp.route('/contact', methods=['POST'])
def contact():
    """Traitement du formulaire de contact"""
    try:
        # Récupérer les données du formulaire
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        project_type = request.form.get('project_type')
        message = request.form.get('message')
        
        # Créer le message email
        msg = Message(
            subject=f'Nouvelle demande de devis - {project_type}',
            sender=email,
            recipients=['info@globibat.com'],
            body=f"""
            Nouvelle demande de devis reçue via le site web:
            
            Nom: {name}
            Email: {email}
            Téléphone: {phone}
            Type de projet: {project_type}
            
            Message:
            {message}
            
            Date: {datetime.now().strftime('%d/%m/%Y %H:%M')}
            """
        )
        
        # Envoyer l'email
        mail.send(msg)
        
        flash('Votre demande a été envoyée avec succès. Nous vous contacterons dans les plus brefs délais.', 'success')
    except Exception as e:
        flash('Une erreur est survenue lors de l\'envoi de votre demande. Veuillez nous contacter par téléphone.', 'error')
        print(f"Erreur contact: {e}")
    
    return redirect(url_for('website.index') + '#contact')

@website_bp.route('/mentions-legales')
def mentions_legales():
    """Page des mentions légales"""
    return render_template('website/mentions-legales.html')

# Routes cachées pour accès interne
@website_bp.route('/intranet')
def intranet():
    """Page d'accès à l'intranet (CRM + Badge)"""
    return render_template('website/intranet.html')

@website_bp.route('/globibat-internal')
def internal_redirect():
    """Redirection cachée vers le système interne"""
    # Cette route peut être protégée par IP ou autre méthode
    return redirect(url_for('auth.login'))