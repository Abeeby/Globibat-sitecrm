"""
Module de génération de graphiques pour Globibat
Utilise Plotly pour créer des graphiques interactifs
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import json
from datetime import datetime, date, timedelta
from collections import defaultdict

def create_presence_chart(pointages_data):
    """Crée un graphique de présence par jour"""
    dates = []
    presents = []
    absents = []
    
    for data in pointages_data:
        dates.append(data['date'])
        presents.append(data['presents'])
        absents.append(data['absents'])
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        name='Présents',
        x=dates,
        y=presents,
        marker_color='#28a745'
    ))
    
    fig.add_trace(go.Bar(
        name='Absents',
        x=dates,
        y=absents,
        marker_color='#dc3545'
    ))
    
    fig.update_layout(
        title='Présence quotidienne',
        xaxis_title='Date',
        yaxis_title='Nombre d\'employés',
        barmode='stack',
        hovermode='x unified',
        template='plotly_white'
    )
    
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

def create_hours_distribution(employes_heures):
    """Crée un graphique de distribution des heures travaillées"""
    noms = [e['nom'] for e in employes_heures]
    heures = [e['heures'] for e in employes_heures]
    
    fig = go.Figure(data=[
        go.Bar(
            x=noms,
            y=heures,
            text=[f'{h:.1f}h' for h in heures],
            textposition='auto',
            marker_color='#0d6efd'
        )
    ])
    
    fig.update_layout(
        title='Heures travaillées par employé ce mois',
        xaxis_title='Employé',
        yaxis_title='Heures',
        template='plotly_white',
        xaxis_tickangle=-45
    )
    
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

def create_punctuality_gauge(taux_ponctualite):
    """Crée une jauge de ponctualité"""
    fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = taux_ponctualite,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Taux de ponctualité (%)"},
        delta = {'reference': 95},
        gauge = {
            'axis': {'range': [None, 100]},
            'bar': {'color': "#0d6efd"},
            'steps': [
                {'range': [0, 50], 'color': "#ffcccc"},
                {'range': [50, 80], 'color': "#ffffcc"},
                {'range': [80, 100], 'color': "#ccffcc"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 95
            }
        }
    ))
    
    fig.update_layout(height=300)
    
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

def create_weekly_heatmap(pointages_semaine):
    """Crée une heatmap des présences par heure de la semaine"""
    # Préparer les données
    jours = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi']
    heures = [f'{h:02d}h' for h in range(7, 19)]
    
    # Matrice de présence (exemple)
    z = []
    for jour in range(5):
        row = []
        for heure in range(7, 19):
            # Calculer le nombre d'employés présents à cette heure
            count = 0
            for p in pointages_semaine:
                if p['jour_semaine'] == jour:
                    if p['heure_arrivee'] <= heure < p['heure_depart']:
                        count += 1
            row.append(count)
        z.append(row)
    
    fig = go.Figure(data=go.Heatmap(
        z=z,
        x=heures,
        y=jours,
        colorscale='Blues',
        text=z,
        texttemplate='%{text}',
        textfont={"size": 10}
    ))
    
    fig.update_layout(
        title='Carte de présence hebdomadaire',
        xaxis_title='Heure',
        yaxis_title='Jour',
        template='plotly_white'
    )
    
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

def create_retards_timeline(retards_data):
    """Crée une timeline des retards"""
    fig = go.Figure()
    
    for employe, retards in retards_data.items():
        dates = [r['date'] for r in retards]
        minutes = [r['minutes'] for r in retards]
        
        fig.add_trace(go.Scatter(
            x=dates,
            y=minutes,
            mode='markers+lines',
            name=employe,
            text=[f"{m} min de retard" for m in minutes],
            hoverinfo='text+name'
        ))
    
    fig.update_layout(
        title='Évolution des retards',
        xaxis_title='Date',
        yaxis_title='Minutes de retard',
        template='plotly_white',
        hovermode='x unified'
    )
    
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

def create_monthly_summary_pie(stats):
    """Crée un camembert des statistiques mensuelles"""
    labels = ['Heures travaillées', 'Heures manquées', 'Pauses']
    values = [
        stats['heures_travaillees'],
        stats['heures_manquees'],
        stats['heures_pause']
    ]
    
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=.3,
        marker_colors=['#28a745', '#dc3545', '#ffc107']
    )])
    
    fig.update_layout(
        title='Répartition du temps ce mois',
        annotations=[dict(text='Heures', x=0.5, y=0.5, font_size=20, showarrow=False)]
    )
    
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

def create_dashboard_charts(db_session):
    """Génère tous les graphiques pour le tableau de bord"""
    from app import Employe, Pointage
    
    charts = {}
    
    # 1. Graphique de présence sur 30 jours
    presence_data = []
    for i in range(30):
        date_check = date.today() - timedelta(days=i)
        presents = Pointage.query.filter_by(date_pointage=date_check).filter(
            Pointage.arrivee_matin.isnot(None)
        ).count()
        
        total_employes = Employe.query.filter_by(actif=True).count()
        absents = total_employes - presents
        
        presence_data.append({
            'date': date_check.strftime('%d/%m'),
            'presents': presents,
            'absents': absents
        })
    
    charts['presence'] = create_presence_chart(presence_data[::-1])
    
    # 2. Distribution des heures ce mois
    debut_mois = date.today().replace(day=1)
    employes = Employe.query.filter_by(actif=True).all()
    employes_heures = []
    
    for emp in employes:
        pointages = Pointage.query.filter_by(employe_id=emp.id).filter(
            Pointage.date_pointage >= debut_mois
        ).all()
        
        total_heures = sum(p.heures_travaillees for p in pointages)
        employes_heures.append({
            'nom': f"{emp.nom} {emp.prenom[:1]}.",
            'heures': total_heures
        })
    
    charts['hours_distribution'] = create_hours_distribution(employes_heures)
    
    # 3. Jauge de ponctualité
    pointages_mois = Pointage.query.filter(
        Pointage.date_pointage >= debut_mois
    ).all()
    
    total_arrivees = len([p for p in pointages_mois if p.arrivee_matin or p.arrivee_apres_midi])
    retards = len([p for p in pointages_mois if p.retard_matin or p.retard_apres_midi])
    
    taux_ponctualite = ((total_arrivees - retards) / total_arrivees * 100) if total_arrivees > 0 else 100
    charts['punctuality'] = create_punctuality_gauge(taux_ponctualite)
    
    return charts 