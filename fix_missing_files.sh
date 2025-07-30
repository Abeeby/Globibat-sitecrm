#!/bin/bash

# Script pour créer les fichiers manquants sur le VPS
cd /var/www/globibat

# 1. Créer notifications.py
cat > notifications.py << 'EOF'
from flask_mail import Mail, Message
from flask import current_app
import threading

mail = Mail()

# Templates HTML pour les emails
TEMPLATE_RETARD = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; }
        .container { max-width: 600px; margin: auto; padding: 20px; }
        .header { background-color: #366092; color: white; padding: 20px; text-align: center; }
        .content { padding: 20px; background-color: #f9f9f9; }
        .footer { padding: 10px; text-align: center; color: #666; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Notification de Retard</h1>
        </div>
        <div class="content">
            <p>Bonjour,</p>
            <p><strong>{nom} {prenom}</strong> (Matricule: {matricule}) est arrivé(e) en retard.</p>
            <p><strong>Heure d'arrivée:</strong> {heure_arrivee}</p>
            <p><strong>Type:</strong> {type_retard}</p>
        </div>
        <div class="footer">
            <p>Système de Badgeage Globibat</p>
        </div>
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
        .container { max-width: 600px; margin: auto; padding: 20px; }
        .header { background-color: #d32f2f; color: white; padding: 20px; text-align: center; }
        .content { padding: 20px; background-color: #f9f9f9; }
        .footer { padding: 10px; text-align: center; color: #666; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Notification d'Absence</h1>
        </div>
        <div class="content">
            <p>Bonjour,</p>
            <p><strong>{nom} {prenom}</strong> (Matricule: {matricule}) est absent(e) aujourd'hui.</p>
            <p><strong>Date:</strong> {date}</p>
        </div>
        <div class="footer">
            <p>Système de Badgeage Globibat</p>
        </div>
    </div>
</body>
</html>
"""

def send_email_async(app, msg):
    """Envoie l'email de manière asynchrone"""
    with app.app_context():
        try:
            mail.send(msg)
        except Exception as e:
            print(f"Erreur envoi email: {e}")

def send_notification_retard(employe, heure_arrivee, type_retard="Matin"):
    """Envoie une notification de retard par email"""
    if not current_app.config.get('MAIL_USERNAME'):
        return
    
    msg = Message(
        f'Retard - {employe.nom} {employe.prenom}',
        sender=current_app.config['MAIL_USERNAME'],
        recipients=[current_app.config.get('RH_EMAIL', current_app.config['MAIL_USERNAME'])]
    )
    
    msg.html = TEMPLATE_RETARD.format(
        nom=employe.nom,
        prenom=employe.prenom,
        matricule=employe.matricule,
        heure_arrivee=heure_arrivee.strftime('%H:%M'),
        type_retard=type_retard
    )
    
    # Envoi asynchrone
    thread = threading.Thread(
        target=send_email_async,
        args=(current_app._get_current_object(), msg)
    )
    thread.start()

def send_notification_absence(employe, date_absence):
    """Envoie une notification d'absence par email"""
    if not current_app.config.get('MAIL_USERNAME'):
        return
    
    msg = Message(
        f'Absence - {employe.nom} {employe.prenom}',
        sender=current_app.config['MAIL_USERNAME'],
        recipients=[current_app.config.get('RH_EMAIL', current_app.config['MAIL_USERNAME'])]
    )
    
    msg.html = TEMPLATE_ABSENCE.format(
        nom=employe.nom,
        prenom=employe.prenom,
        matricule=employe.matricule,
        date=date_absence.strftime('%d/%m/%Y')
    )
    
    thread = threading.Thread(
        target=send_email_async,
        args=(current_app._get_current_object(), msg)
    )
    thread.start()

def send_rappel_badge(employe, type_badge):
    """Envoie un rappel de badgeage"""
    # À implémenter si nécessaire
    pass

def send_rapport_mensuel_rh(filepath):
    """Envoie le rapport mensuel aux RH"""
    # À implémenter si nécessaire
    pass
EOF

# 2. Créer charts.py (version simplifiée)
cat > charts.py << 'EOF'
import plotly.graph_objects as go
import plotly.utils
import json
from datetime import datetime, timedelta, date

def create_presence_chart(pointages_semaine):
    """Crée un graphique de présence hebdomadaire"""
    dates = []
    presents = []
    absents = []
    
    # Données simplifiées pour le test
    for i in range(7):
        jour = date.today() - timedelta(days=i)
        dates.append(jour.strftime('%d/%m'))
        presents.append(15)  # Valeur de test
        absents.append(2)    # Valeur de test
    
    fig = go.Figure()
    fig.add_trace(go.Bar(name='Présents', x=dates, y=presents, marker_color='green'))
    fig.add_trace(go.Bar(name='Absents', x=dates, y=absents, marker_color='red'))
    
    fig.update_layout(
        title='Présence Hebdomadaire',
        barmode='stack',
        height=400
    )
    
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

def create_hours_distribution(heures_data):
    """Distribution des heures travaillées"""
    fig = go.Figure(data=[
        go.Box(y=[7.5, 8, 8.5, 9, 7.8], name='Heures/Jour')
    ])
    
    fig.update_layout(title='Distribution des Heures', height=400)
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

def create_punctuality_gauge(taux_ponctualite):
    """Jauge de ponctualité"""
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=85,  # Valeur de test
        title={'text': "Ponctualité (%)"},
        gauge={'axis': {'range': [None, 100]},
               'bar': {'color': "darkgreen"},
               'steps': [
                   {'range': [0, 50], 'color': "lightgray"},
                   {'range': [50, 80], 'color': "yellow"},
                   {'range': [80, 100], 'color': "lightgreen"}],
               'threshold': {'line': {'color': "red", 'width': 4},
                           'thickness': 0.75, 'value': 90}}
    ))
    
    fig.update_layout(height=400)
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

def create_weekly_heatmap(data):
    """Heatmap des présences"""
    return create_presence_chart(data)  # Simplifié pour le test

def create_retards_timeline(retards_data):
    """Timeline des retards"""
    return create_hours_distribution(retards_data)  # Simplifié

def create_monthly_summary_pie(summary_data):
    """Camembert résumé mensuel"""
    fig = go.Figure(data=[go.Pie(
        labels=['Présents', 'Retards', 'Absences'],
        values=[300, 20, 10]
    )])
    
    fig.update_layout(title='Résumé du Mois', height=400)
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

def create_dashboard_charts(pointages, employes):
    """Génère tous les graphiques du dashboard"""
    return {
        'presence_chart': create_presence_chart(pointages),
        'hours_distribution': create_hours_distribution(None),
        'punctuality_gauge': create_punctuality_gauge(85),
        'weekly_heatmap': create_weekly_heatmap(None),
        'retards_timeline': create_retards_timeline(None),
        'monthly_summary': create_monthly_summary_pie(None)
    }
EOF

# 3. Créer pdf_generator.py (version simplifiée)
cat > pdf_generator.py << 'EOF'
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from datetime import datetime
import os

def generate_payslip(employe, month, year, output_path):
    """Génère une fiche de paie PDF simple"""
    # Pour le moment, retourner un chemin fictif
    # L'implémentation complète sera ajoutée plus tard
    return output_path
EOF

# 4. Créer tasks.py (version simplifiée)
cat > tasks.py << 'EOF'
import threading
import time
from datetime import datetime

def check_absences():
    """Vérifie les absences (simplifié)"""
    pass

def send_badge_reminders():
    """Envoie des rappels de badge (simplifié)"""
    pass

def generate_monthly_report():
    """Génère le rapport mensuel (simplifié)"""
    pass

def run_scheduler():
    """Lance les tâches planifiées"""
    while True:
        time.sleep(3600)  # Attendre 1 heure

def start_scheduler(app):
    """Démarre le scheduler dans un thread séparé"""
    # Désactivé pour le moment
    pass
EOF

# 5. Créer le dossier static s'il n'existe pas
mkdir -p static/icons

# 6. Créer manifest.json
cat > static/manifest.json << 'EOF'
{
  "name": "Globibat Badge System",
  "short_name": "Globibat",
  "description": "Système de badgeage pour les employés Globibat",
  "theme_color": "#366092",
  "background_color": "#ffffff",
  "display": "standalone",
  "start_url": "/",
  "icons": [
    {
      "src": "/static/icons/icon-192.png",
      "sizes": "192x192",
      "type": "image/png"
    },
    {
      "src": "/static/icons/icon-512.png",
      "sizes": "512x512",
      "type": "image/png"
    }
  ]
}
EOF

# 7. Créer sw.js
cat > static/sw.js << 'EOF'
const CACHE_NAME = 'globibat-v1';
const urlsToCache = [
  '/',
  '/static/css/style.css',
  '/static/js/app.js'
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(urlsToCache))
  );
});

self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request)
      .then(response => response || fetch(event.request))
  );
});
EOF

# Donner les permissions
chmod 644 *.py
chmod 644 static/manifest.json
chmod 644 static/sw.js

echo "✅ Fichiers créés avec succès !" 