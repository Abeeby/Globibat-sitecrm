#!/usr/bin/env python3
"""
Créer un système de badgeage complet avec les 4 moments de la journée
"""

# Créer le nouveau fichier badge.py avec les 4 moments
badge_py_content = '''"""
Interface de badgeage pour les employés avec les 4 moments de la journée
"""
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from app import db
from app.models import Employee, Attendance
from datetime import datetime, date, time

bp = Blueprint('badge', __name__, url_prefix='/badge')

# Horaires de référence
HORAIRES = {
    'arrivee_matin': time(8, 0),      # 8h00
    'depart_midi': time(12, 0),       # 12h00
    'retour_midi': time(13, 30),      # 13h30
    'depart_soir': time(17, 30)       # 17h30
}

@bp.route('/')
def index():
    """Page principale de badgeage"""
    return render_template('badge/index.html')

@bp.route('/check', methods=['POST'])
def check():
    """Enregistrer un badgeage"""
    badge_number = request.form.get('badge_number')
    
    # Trouver l'employé
    employee = Employee.query.filter(
        Employee.badge_number == badge_number,
        Employee.is_active == True
    ).first()
    
    if not employee:
        flash('Badge invalide ou employé inactif!', 'danger')
        return redirect(url_for('badge.index'))
    
    # Récupérer ou créer l'attendance du jour
    today = date.today()
    attendance = Attendance.query.filter_by(
        employee_id=employee.id,
        date=today
    ).first()
    
    if not attendance:
        attendance = Attendance(
            employee_id=employee.id,
            date=today,
            check_type='normal'
        )
        db.session.add(attendance)
    
    # Déterminer quel type de badgeage
    current_time = datetime.now()
    current_hour = current_time.hour
    
    message = ""
    badge_type = ""
    
    # Logique de badgeage selon l'heure
    if current_hour < 10:  # Matin (avant 10h)
        if not attendance.clock_in:
            attendance.clock_in = current_time
            badge_type = "arrivée matin"
            message = f"Bonjour {employee.user.first_name} ! Arrivée enregistrée à {current_time.strftime('%H:%M')}"
        else:
            message = f"Vous avez déjà badgé votre arrivée à {attendance.clock_in.strftime('%H:%M')}"
            
    elif 10 <= current_hour < 14:  # Midi (10h-14h)
        if attendance.clock_in and not attendance.clock_out:
            # C'est un départ midi
            attendance.clock_out = current_time
            badge_type = "départ midi"
            message = f"Bon appétit {employee.user.first_name} ! Départ midi enregistré à {current_time.strftime('%H:%M')}"
        elif attendance.clock_out and not hasattr(attendance, 'clock_in_afternoon'):
            # C'est un retour midi
            attendance.clock_in_afternoon = current_time
            badge_type = "retour midi"
            message = f"Bon retour {employee.user.first_name} ! Retour enregistré à {current_time.strftime('%H:%M')}"
        else:
            message = "Badgeage déjà effectué pour cette période"
            
    else:  # Après-midi/Soir (après 14h)
        if not attendance.clock_out:
            # Pas encore parti le midi, c'est un départ direct
            attendance.clock_out = current_time
            badge_type = "départ soir"
        else:
            # Déjà parti le midi, c'est le départ du soir
            attendance.clock_out_final = current_time
            badge_type = "départ soir"
        
        # Calculer les heures travaillées
        if attendance.clock_in:
            morning_hours = 0
            afternoon_hours = 0
            
            if attendance.clock_out and attendance.clock_in:
                morning_delta = attendance.clock_out - attendance.clock_in
                morning_hours = morning_delta.total_seconds() / 3600
            
            if hasattr(attendance, 'clock_in_afternoon') and hasattr(attendance, 'clock_out_final'):
                if attendance.clock_in_afternoon and attendance.clock_out_final:
                    afternoon_delta = attendance.clock_out_final - attendance.clock_in_afternoon
                    afternoon_hours = afternoon_delta.total_seconds() / 3600
            elif not hasattr(attendance, 'clock_in_afternoon') and attendance.clock_out:
                # Journée continue
                total_delta = attendance.clock_out - attendance.clock_in
                attendance.hours_worked = total_delta.total_seconds() / 3600
            
            if morning_hours or afternoon_hours:
                attendance.hours_worked = morning_hours + afternoon_hours
        
        message = f"Bonne soirée {employee.user.first_name} ! Départ enregistré à {current_time.strftime('%H:%M')}"
        if hasattr(attendance, 'hours_worked') and attendance.hours_worked:
            message += f" - Total: {attendance.hours_worked:.2f}h"
    
    # Sauvegarder
    db.session.commit()
    
    # Flash le message
    if badge_type:
        flash(message, 'success')
    else:
        flash(message, 'warning')
    
    return redirect(url_for('badge.index'))

@bp.route('/status/<badge_number>')
def status(badge_number):
    """Vérifier le statut d'un employé"""
    employee = Employee.query.filter(
        Employee.badge_number == badge_number,
        Employee.is_active == True
    ).first()
    
    if not employee:
        return jsonify({'error': 'Badge invalide'}), 404
    
    # Attendance du jour
    today = date.today()
    attendance = Attendance.query.filter_by(
        employee_id=employee.id,
        date=today
    ).first()
    
    status_info = {
        'employee': f"{employee.user.first_name} {employee.user.last_name}",
        'badges_today': []
    }
    
    if attendance:
        if attendance.clock_in:
            status_info['badges_today'].append(f"Arrivée: {attendance.clock_in.strftime('%H:%M')}")
        if attendance.clock_out:
            status_info['badges_today'].append(f"Départ midi: {attendance.clock_out.strftime('%H:%M')}")
        if hasattr(attendance, 'clock_in_afternoon') and attendance.clock_in_afternoon:
            status_info['badges_today'].append(f"Retour midi: {attendance.clock_in_afternoon.strftime('%H:%M')}")
        if hasattr(attendance, 'clock_out_final') and attendance.clock_out_final:
            status_info['badges_today'].append(f"Départ soir: {attendance.clock_out_final.strftime('%H:%M')}")
    
    # Déterminer le prochain badge attendu
    current_hour = datetime.now().hour
    if not attendance or not attendance.clock_in:
        status_info['next_badge'] = "Arrivée matin"
    elif attendance.clock_in and not attendance.clock_out and current_hour < 14:
        status_info['next_badge'] = "Départ midi"
    elif attendance.clock_out and not hasattr(attendance, 'clock_in_afternoon'):
        status_info['next_badge'] = "Retour midi"
    elif (hasattr(attendance, 'clock_in_afternoon') or attendance.clock_in) and not hasattr(attendance, 'clock_out_final'):
        status_info['next_badge'] = "Départ soir"
    else:
        status_info['next_badge'] = "Journée complète"
    
    return jsonify(status_info)

@bp.route('/report')
@bp.route('/report/<int:employee_id>')
def report(employee_id=None):
    """Rapport de badgeages"""
    from datetime import timedelta
    
    # Si employee_id fourni, afficher ses badgeages
    if employee_id:
        employee = Employee.query.get_or_404(employee_id)
        
        # Récupérer les 30 derniers jours
        end_date = date.today()
        start_date = end_date - timedelta(days=30)
        
        attendances = Attendance.query.filter(
            Attendance.employee_id == employee_id,
            Attendance.date >= start_date,
            Attendance.date <= end_date
        ).order_by(Attendance.date.desc()).all()
        
        return render_template('badge/employee_report.html',
                             employee=employee,
                             attendances=attendances)
    
    # Sinon, afficher la liste des employés
    employees = Employee.query.filter_by(is_active=True).all()
    return render_template('badge/report_list.html', employees=employees)
'''

# Créer le template HTML amélioré
badge_template = '''<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Badgeage - Globibat</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/bootstrap-icons.css">
    <style>
        body {
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        }
        .badge-container {
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            padding: 40px;
            max-width: 600px;
            width: 100%;
            text-align: center;
        }
        .logo {
            font-size: 3rem;
            color: #ff6b35;
            margin-bottom: 20px;
        }
        .time-display {
            font-size: 3rem;
            font-weight: 300;
            color: #333;
            margin-bottom: 10px;
        }
        .date-display {
            font-size: 1.2rem;
            color: #666;
            margin-bottom: 30px;
        }
        .badge-input {
            font-size: 2rem;
            text-align: center;
            padding: 20px;
            border: 3px solid #e0e0e0;
            border-radius: 15px;
            margin-bottom: 20px;
            transition: all 0.3s;
        }
        .badge-input:focus {
            border-color: #ff6b35;
            box-shadow: 0 0 0 0.2rem rgba(255,107,53,0.25);
        }
        .badge-btn {
            background: #ff6b35;
            color: white;
            font-size: 1.5rem;
            padding: 15px 40px;
            border: none;
            border-radius: 50px;
            transition: all 0.3s;
            box-shadow: 0 4px 15px rgba(255,107,53,0.3);
        }
        .badge-btn:hover {
            background: #e55a2b;
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(255,107,53,0.4);
        }
        .alert {
            border-radius: 10px;
            margin-top: 20px;
        }
        .employee-status {
            margin-top: 20px;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 10px;
            display: none;
        }
        .badge-time {
            display: inline-block;
            padding: 5px 10px;
            margin: 2px;
            background: #e9ecef;
            border-radius: 5px;
            font-size: 0.9rem;
        }
        .badge-time.morning { border-left: 3px solid #28a745; }
        .badge-time.lunch-out { border-left: 3px solid #ffc107; }
        .badge-time.lunch-in { border-left: 3px solid #17a2b8; }
        .badge-time.evening { border-left: 3px solid #dc3545; }
        .next-badge {
            margin-top: 10px;
            font-size: 1.1rem;
            color: #007bff;
        }
        .time-indicator {
            position: absolute;
            top: 20px;
            right: 20px;
            padding: 10px 20px;
            background: rgba(255,255,255,0.9);
            border-radius: 10px;
            font-weight: 500;
        }
        .morning { color: #28a745; }
        .noon { color: #ffc107; }
        .afternoon { color: #17a2b8; }
        .evening { color: #dc3545; }
    </style>
</head>
<body>
    <div class="badge-container">
        <div class="logo">
            <i class="bi bi-building"></i>
        </div>
        <h1 class="h3 mb-4">Globibat - Système de Badgeage</h1>
        
        <div class="time-display" id="time"></div>
        <div class="date-display" id="date"></div>
        
        <!-- Indicateur de période -->
        <div id="period-indicator" class="mb-3"></div>
        
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert alert-{{ category }} alert-dismissible fade show" role="alert">
                        {{ message }}
                        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                    </div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        
        <form method="POST" action="{{ url_for('badge.check') }}" onsubmit="return validateBadge()">
            <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
            <input type="text" 
                   name="badge_number" 
                   id="badge_number"
                   class="form-control badge-input" 
                   placeholder="Scannez votre badge"
                   autocomplete="off"
                   autofocus
                   required>
            
            <button type="submit" class="btn badge-btn">
                <i class="bi bi-clock-history"></i> Badger
            </button>
        </form>
        
        <div id="employee-status" class="employee-status"></div>
        
        <div class="mt-4">
            <a href="/badge/report" class="text-muted me-3">
                <i class="bi bi-file-text"></i> Rapports
            </a>
            <a href="/" class="text-muted">
                <i class="bi bi-arrow-left"></i> Retour au site
            </a>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // Afficher l'heure et la période
        function updateTime() {
            const now = new Date();
            const hours = now.getHours();
            
            document.getElementById('time').textContent = now.toLocaleTimeString('fr-FR', {
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit'
            });
            
            document.getElementById('date').textContent = now.toLocaleDateString('fr-FR', {
                weekday: 'long',
                year: 'numeric',
                month: 'long',
                day: 'numeric'
            });
            
            // Indicateur de période
            let period = '';
            let periodClass = '';
            if (hours < 10) {
                period = '🌅 Période: Arrivée matin';
                periodClass = 'morning';
            } else if (hours >= 10 && hours < 14) {
                period = '🍽️ Période: Pause midi';
                periodClass = 'noon';
            } else if (hours >= 14 && hours < 17) {
                period = '☀️ Période: Après-midi';
                periodClass = 'afternoon';
            } else {
                period = '🌆 Période: Départ soir';
                periodClass = 'evening';
            }
            
            document.getElementById('period-indicator').innerHTML = 
                `<span class="badge bg-light text-dark ${periodClass}">${period}</span>`;
        }
        
        updateTime();
        setInterval(updateTime, 1000);
        
        // Validation du badge
        function validateBadge() {
            const badge = document.getElementById('badge_number').value;
            if (badge.length < 1) {
                alert('Veuillez scanner votre badge');
                return false;
            }
            return true;
        }
        
        // Vérifier le statut quand on tape
        let typingTimer;
        document.getElementById('badge_number').addEventListener('keyup', function() {
            clearTimeout(typingTimer);
            const badge = this.value;
            
            if (badge.length >= 3) {
                typingTimer = setTimeout(function() {
                    fetch('/badge/status/' + badge)
                        .then(response => response.json())
                        .then(data => {
                            const statusDiv = document.getElementById('employee-status');
                            if (data.error) {
                                statusDiv.style.display = 'none';
                            } else {
                                let badgesHtml = '';
                                if (data.badges_today && data.badges_today.length > 0) {
                                    badgesHtml = '<div class="mt-2">Badgeages aujourd\'hui:<br>';
                                    data.badges_today.forEach(badge => {
                                        let badgeClass = '';
                                        if (badge.includes('Arrivée:')) badgeClass = 'morning';
                                        else if (badge.includes('Départ midi:')) badgeClass = 'lunch-out';
                                        else if (badge.includes('Retour midi:')) badgeClass = 'lunch-in';
                                        else if (badge.includes('Départ soir:')) badgeClass = 'evening';
                                        
                                        badgesHtml += `<span class="badge-time ${badgeClass}">${badge}</span>`;
                                    });
                                    badgesHtml += '</div>';
                                }
                                
                                statusDiv.innerHTML = `
                                    <strong>${data.employee}</strong>
                                    ${badgesHtml}
                                    <div class="next-badge">
                                        <i class="bi bi-arrow-right-circle"></i> 
                                        Prochain: <strong>${data.next_badge}</strong>
                                    </div>
                                `;
                                statusDiv.style.display = 'block';
                            }
                        });
                }, 500);
            }
        });
        
        // Focus automatique
        document.getElementById('badge_number').focus();
    </script>
</body>
</html>'''

# Sauvegarder les fichiers
import os

# Créer le fichier badge.py
with open('/var/www/globibat/app/views/badge.py', 'w', encoding='utf-8') as f:
    f.write(badge_py_content)
print("✅ Fichier badge.py créé avec les 4 moments de badgeage")

# Créer le template
os.makedirs('/var/www/globibat/app/templates/badge', exist_ok=True)
with open('/var/www/globibat/app/templates/badge/index.html', 'w', encoding='utf-8') as f:
    f.write(badge_template)
print("✅ Template badge/index.html créé")

# Ajouter les colonnes manquantes à Attendance si nécessaire
print("\n🔄 Mise à jour du modèle Attendance...")

attendance_update = '''
cd /var/www/globibat
export FLASK_ENV=development
export SECRET_KEY=dev-secret-key-for-testing
export DATABASE_URL=mysql://globibat_user:Globibat2024Secure!@localhost:3306/globibat_crm

./venv/bin/python << 'EOF'
from app import create_app, db
from sqlalchemy import text

app = create_app('development')
with app.app_context():
    # Ajouter les colonnes manquantes à la table attendances
    try:
        # Vérifier si les colonnes existent
        result = db.session.execute(text("SHOW COLUMNS FROM attendances"))
        columns = [row[0] for row in result]
        
        # Ajouter clock_in_afternoon si elle n'existe pas
        if 'clock_in_afternoon' not in columns:
            db.session.execute(text("ALTER TABLE attendances ADD COLUMN clock_in_afternoon DATETIME"))
            print("✅ Colonne clock_in_afternoon ajoutée")
        
        # Ajouter clock_out_final si elle n'existe pas
        if 'clock_out_final' not in columns:
            db.session.execute(text("ALTER TABLE attendances ADD COLUMN clock_out_final DATETIME"))
            print("✅ Colonne clock_out_final ajoutée")
        
        # Ajouter date si elle n'existe pas
        if 'date' not in columns:
            db.session.execute(text("ALTER TABLE attendances ADD COLUMN date DATE"))
            db.session.execute(text("UPDATE attendances SET date = DATE(clock_in) WHERE date IS NULL"))
            print("✅ Colonne date ajoutée")
        
        db.session.commit()
        print("✅ Table attendances mise à jour")
        
    except Exception as e:
        print(f"⚠️ Erreur lors de la mise à jour: {e}")
        db.session.rollback()
EOF
'''

os.system(attendance_update)

print("\n✅ Système de badgeage avec 4 moments créé!")
print("📱 Accessible sur: http://148.230.105.25:5000/badge")
print("🔑 Badges de test: 001, 002, 003")