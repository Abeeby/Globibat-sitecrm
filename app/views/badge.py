"""
Blueprint pour le système de badge des employés
Séparé du site public
"""

from flask import Blueprint, render_template, request, jsonify
from app import db
from app.models import Employee, Attendance
from datetime import datetime, date
from sqlalchemy import and_

# Créer le blueprint avec un préfixe pour séparer du site public
badge_bp = Blueprint('badge', __name__, url_prefix='/employee')

@badge_bp.route('/badge')
def index():
    """Interface principale de badge pour les employés"""
    return render_template('badge/index_pro.html')

@badge_bp.route('/badge/check', methods=['POST'])
def check():
    """Enregistrer un pointage (entrée/sortie)"""
    try:
        badge_number = request.json.get('badge_number')
        
        if not badge_number:
            return jsonify({
                'success': False,
                'message': 'Numéro de badge requis'
            }), 400
        
        # Trouver l'employé
        employee = Employee.query.filter_by(badge_number=badge_number, is_active=True).first()
        
        if not employee:
            return jsonify({
                'success': False,
                'message': 'Badge invalide ou employé inactif'
            }), 404
        
        # Vérifier s'il y a déjà un pointage aujourd'hui
        today = date.today()
        attendance = Attendance.query.filter(
            and_(
                Attendance.employee_id == employee.id,
                Attendance.date == today
            )
        ).first()
        
        current_time = datetime.now()
        action_type = None
        message = ""
        
        if not attendance:
            # Premier pointage du jour - Arrivée matin
            attendance = Attendance(
                employee_id=employee.id,
                date=today,
                check_in_morning=current_time
            )
            db.session.add(attendance)
            action_type = "check_in"
            message = f"Bonjour {employee.user.first_name}! Arrivée enregistrée à {current_time.strftime('%H:%M')}"
            
        elif not attendance.check_out_lunch:
            # Départ midi
            attendance.check_out_lunch = current_time
            action_type = "check_out"
            message = f"Bon appétit {employee.user.first_name}! Départ midi enregistré à {current_time.strftime('%H:%M')}"
            
        elif not attendance.check_in_afternoon:
            # Retour après-midi
            attendance.check_in_afternoon = current_time
            action_type = "check_in"
            message = f"Bon retour {employee.user.first_name}! Retour enregistré à {current_time.strftime('%H:%M')}"
            
        elif not attendance.check_out_evening:
            # Départ soir
            attendance.check_out_evening = current_time
            action_type = "check_out"
            
            # Calculer les heures totales
            morning_hours = 0
            afternoon_hours = 0
            
            if attendance.check_in_morning and attendance.check_out_lunch:
                morning_delta = attendance.check_out_lunch - attendance.check_in_morning
                morning_hours = morning_delta.total_seconds() / 3600
            
            if attendance.check_in_afternoon and attendance.check_out_evening:
                afternoon_delta = attendance.check_out_evening - attendance.check_in_afternoon
                afternoon_hours = afternoon_delta.total_seconds() / 3600
            
            total_hours = round(morning_hours + afternoon_hours, 2)
            attendance.total_hours = total_hours
            
            # Calculer les heures supplémentaires (> 8h)
            if total_hours > 8:
                attendance.overtime_hours = round(total_hours - 8, 2)
            
            message = f"Bonne soirée {employee.user.first_name}! Départ enregistré à {current_time.strftime('%H:%M')}. Total: {total_hours}h"
        else:
            return jsonify({
                'success': False,
                'message': 'Tous les pointages du jour sont déjà enregistrés'
            }), 400
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': message,
            'action_type': action_type,
            'employee': {
                'name': f"{employee.user.first_name} {employee.user.last_name}",
                'position': employee.position,
                'department': employee.department
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Erreur lors du pointage: {str(e)}'
        }), 500

@badge_bp.route('/badge/status')
def status():
    """Obtenir le statut actuel du système de badge"""
    try:
        # Compter les employés présents aujourd'hui
        today = date.today()
        present_count = Attendance.query.filter(
            and_(
                Attendance.date == today,
                Attendance.check_in_morning != None,
                Attendance.check_out_evening == None
            )
        ).count()
        
        # Total des employés actifs
        total_employees = Employee.query.filter_by(is_active=True).count()
        
        return jsonify({
            'success': True,
            'present': present_count,
            'total': total_employees,
            'date': today.strftime('%d/%m/%Y'),
            'time': datetime.now().strftime('%H:%M:%S')
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500