"""
Module de gestion des notifications email pour Globibat
"""

from flask_mail import Mail, Message
from flask import current_app, render_template_string
from datetime import datetime, timedelta
import threading

mail = Mail()

# Templates email en HTML
TEMPLATE_RETARD = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; }
        .header { background-color: #0d6efd; color: white; padding: 20px; text-align: center; }
        .content { padding: 20px; }
        .footer { background-color: #f8f9fa; padding: 10px; text-align: center; font-size: 12px; }
        .warning { color: #dc3545; font-weight: bold; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Globibat - Notification de retard</h1>
    </div>
    <div class="content">
        <p>Bonjour {{ employe.prenom }} {{ employe.nom }},</p>
        
        <p>Nous avons constaté un <span class="warning">retard</span> dans votre badgeage aujourd'hui :</p>
        
        <ul>
            <li>Date : {{ date }}</li>
            <li>Heure d'arrivée attendue : {{ heure_attendue }}</li>
            <li>Heure d'arrivée réelle : {{ heure_arrivee }}</li>
            <li>Retard : {{ duree_retard }} minutes</li>
        </ul>
        
        <p>Merci de respecter les horaires de travail.</p>
        
        <p>Cordialement,<br>L'équipe RH de Globibat</p>
    </div>
    <div class="footer">
        <p>Cet email a été envoyé automatiquement. Ne pas répondre.</p>
    </div>
</body>
</html>
"""

TEMPLATE_ABSENCE = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; }
        .header { background-color: #dc3545; color: white; padding: 20px; text-align: center; }
        .content { padding: 20px; }
        .footer { background-color: #f8f9fa; padding: 10px; text-align: center; font-size: 12px; }
        .alert { color: #dc3545; font-weight: bold; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Globibat - Notification d'absence</h1>
    </div>
    <div class="content">
        <p>Bonjour {{ employe.prenom }} {{ employe.nom }},</p>
        
        <p>Nous avons constaté votre <span class="alert">absence</span> aujourd'hui ({{ date }}).</p>
        
        <p>Si cette absence n'est pas justifiée, merci de contacter votre responsable dans les plus brefs délais.</p>
        
        <p>Cordialement,<br>L'équipe RH de Globibat</p>
    </div>
    <div class="footer">
        <p>Cet email a été envoyé automatiquement. Ne pas répondre.</p>
    </div>
</body>
</html>
"""

TEMPLATE_RAPPEL_BADGE = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; }
        .header { background-color: #ffc107; color: #212529; padding: 20px; text-align: center; }
        .content { padding: 20px; }
        .footer { background-color: #f8f9fa; padding: 10px; text-align: center; font-size: 12px; }
        .reminder { color: #ffc107; font-weight: bold; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Globibat - Rappel de badgeage</h1>
    </div>
    <div class="content">
        <p>Bonjour {{ employe.prenom }},</p>
        
        <p><span class="reminder">N'oubliez pas de badger !</span></p>
        
        <p>Il est {{ heure }} et nous n'avons pas encore enregistré votre badgeage de {{ type_badge }}.</p>
        
        <p>Rendez-vous sur l'application pour badger : <a href="{{ url }}">Badger maintenant</a></p>
        
        <p>Bonne journée,<br>L'équipe Globibat</p>
    </div>
    <div class="footer">
        <p>Cet email a été envoyé automatiquement. Ne pas répondre.</p>
    </div>
</body>
</html>
"""

def send_email_async(app, msg):
    """Envoie un email de manière asynchrone"""
    with app.app_context():
        try:
            mail.send(msg)
        except Exception as e:
            print(f"Erreur envoi email : {str(e)}")

def send_notification_retard(employe, heure_arrivee, heure_attendue):
    """Envoie une notification de retard"""
    if not employe.email:
        return
    
    duree_retard = int((heure_arrivee - heure_attendue).total_seconds() / 60)
    
    msg = Message(
        subject="Globibat - Notification de retard",
        sender=current_app.config.get('MAIL_USERNAME'),
        recipients=[employe.email]
    )
    
    msg.html = render_template_string(
        TEMPLATE_RETARD,
        employe=employe,
        date=datetime.now().strftime('%d/%m/%Y'),
        heure_attendue=heure_attendue.strftime('%H:%M'),
        heure_arrivee=heure_arrivee.strftime('%H:%M'),
        duree_retard=duree_retard
    )
    
    # Envoi asynchrone
    thread = threading.Thread(
        target=send_email_async,
        args=(current_app._get_current_object(), msg)
    )
    thread.start()

def send_notification_absence(employe):
    """Envoie une notification d'absence"""
    if not employe.email:
        return
    
    msg = Message(
        subject="Globibat - Notification d'absence",
        sender=current_app.config.get('MAIL_USERNAME'),
        recipients=[employe.email]
    )
    
    msg.html = render_template_string(
        TEMPLATE_ABSENCE,
        employe=employe,
        date=datetime.now().strftime('%d/%m/%Y')
    )
    
    thread = threading.Thread(
        target=send_email_async,
        args=(current_app._get_current_object(), msg)
    )
    thread.start()

def send_rappel_badge(employe, type_badge):
    """Envoie un rappel de badgeage"""
    if not employe.email:
        return
    
    types_badge_texte = {
        'arrivee_matin': 'arrivée du matin',
        'depart_midi': 'départ de midi',
        'arrivee_apres_midi': 'retour de l\'après-midi',
        'depart_soir': 'départ du soir'
    }
    
    msg = Message(
        subject="Globibat - Rappel de badgeage",
        sender=current_app.config.get('MAIL_USERNAME'),
        recipients=[employe.email]
    )
    
    msg.html = render_template_string(
        TEMPLATE_RAPPEL_BADGE,
        employe=employe,
        heure=datetime.now().strftime('%H:%M'),
        type_badge=types_badge_texte.get(type_badge, 'badgeage'),
        url=current_app.config.get('COMPANY_URL', 'http://localhost:5000') + '/badge'
    )
    
    thread = threading.Thread(
        target=send_email_async,
        args=(current_app._get_current_object(), msg)
    )
    thread.start()

def send_rapport_mensuel_rh(employes_stats, mois, annee):
    """Envoie le rapport mensuel aux RH"""
    rh_email = current_app.config.get('RH_EMAIL')
    if not rh_email:
        return
    
    msg = Message(
        subject=f"Globibat - Rapport mensuel {mois}/{annee}",
        sender=current_app.config.get('MAIL_USERNAME'),
        recipients=[rh_email]
    )
    
    # Créer le contenu du rapport
    html_content = f"""
    <h1>Rapport mensuel de présence - {mois}/{annee}</h1>
    <table border="1" cellpadding="5">
        <tr>
            <th>Employé</th>
            <th>Heures travaillées</th>
            <th>Retards</th>
            <th>Absences</th>
        </tr>
    """
    
    for stats in employes_stats:
        html_content += f"""
        <tr>
            <td>{stats['nom']}</td>
            <td>{stats['heures']:.2f}h</td>
            <td>{stats['retards']}</td>
            <td>{stats['absences']}</td>
        </tr>
        """
    
    html_content += "</table>"
    msg.html = html_content
    
    thread = threading.Thread(
        target=send_email_async,
        args=(current_app._get_current_object(), msg)
    )
    thread.start() 