"""
Système de badgage avancé avec QR codes, PIN, photos et géolocalisation
"""

from flask import Blueprint, render_template, request, jsonify, current_app
from werkzeug.utils import secure_filename
from app import db
from app.models import Employee, Attendance, AuditLog
from app.utils.decorators import log_action
from datetime import datetime, date, timedelta
from sqlalchemy import and_, or_, func
import os
import qrcode
import io
import base64
from PIL import Image
import hashlib

# Blueprint pour le badge avancé
badge_advanced_bp = Blueprint('badge_advanced', __name__, url_prefix='/api/badge')

# Configuration
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
UPLOAD_FOLDER = 'app/static/uploads/attendance'

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_qr_code(employee_id, badge_number):
    """Générer un QR code unique pour un employé"""
    # Créer un hash unique
    data = f"GLOBIBAT-{employee_id}-{badge_number}-{datetime.now().strftime('%Y%m%d')}"
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convertir en base64
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    
    return base64.b64encode(buffer.getvalue()).decode()

@badge_advanced_bp.route('/generate-qr/<int:employee_id>')
def generate_employee_qr(employee_id):
    """Générer et retourner le QR code d'un employé"""
    employee = Employee.query.get_or_404(employee_id)
    
    if not employee.qr_code:
        # Générer un nouveau QR code
        qr_data = f"GB-{employee.employee_code}-{hashlib.md5(str(employee.id).encode()).hexdigest()[:8]}"
        employee.qr_code = qr_data
        db.session.commit()
    
    qr_image = generate_qr_code(employee.id, employee.badge_number)
    
    return jsonify({
        'success': True,
        'qr_code': employee.qr_code,
        'qr_image': f"data:image/png;base64,{qr_image}",
        'employee': {
            'name': employee.full_name,
            'code': employee.employee_code
        }
    })

@badge_advanced_bp.route('/check-in', methods=['POST'])
@log_action('badge_checkin')
def check_in_advanced():
    """Pointage avancé avec multiple méthodes d'authentification"""
    try:
        data = request.get_json()
        
        # Méthode d'authentification
        auth_method = data.get('method')  # badge, qr_code, pin, face
        auth_value = data.get('value')
        
        # Géolocalisation
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        location_name = data.get('location_name')
        
        # Photo (optionnelle)
        photo_data = data.get('photo')
        
        # Info appareil
        device_info = data.get('device_info', request.headers.get('User-Agent'))
        
        # Trouver l'employé selon la méthode
        employee = None
        
        if auth_method == 'badge':
            employee = Employee.query.filter_by(badge_number=auth_value, is_active=True).first()
        elif auth_method == 'qr_code':
            employee = Employee.query.filter_by(qr_code=auth_value, is_active=True).first()
        elif auth_method == 'pin':
            # Vérifier le PIN (haché pour la sécurité)
            pin_hash = hashlib.sha256(auth_value.encode()).hexdigest()
            employee = Employee.query.filter_by(pin_code=pin_hash, is_active=True).first()
        
        if not employee:
            return jsonify({
                'success': False,
                'message': 'Authentification échouée. Vérifiez vos identifiants.'
            }), 401
        
        # Vérifier la géolocalisation si requise
        if current_app.config.get('REQUIRE_GEOLOCATION', False):
            if not latitude or not longitude:
                return jsonify({
                    'success': False,
                    'message': 'La géolocalisation est requise pour le pointage.'
                }), 400
            
            # Vérifier si l'employé est dans un rayon autorisé
            # TODO: Implémenter la vérification du périmètre
        
        # Obtenir ou créer l'attendance du jour
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
        photo_path = None
        
        # Sauvegarder la photo si fournie
        if photo_data:
            try:
                # Décoder la photo base64
                photo_binary = base64.b64decode(photo_data.split(',')[1])
                
                # Créer le nom de fichier
                timestamp = current_time.strftime('%Y%m%d_%H%M%S')
                filename = f"{employee.employee_code}_{timestamp}.jpg"
                
                # Créer le dossier si nécessaire
                os.makedirs(UPLOAD_FOLDER, exist_ok=True)
                
                # Sauvegarder la photo
                photo_path = os.path.join(UPLOAD_FOLDER, filename)
                with open(photo_path, 'wb') as f:
                    f.write(photo_binary)
                    
                # Chemin relatif pour la DB
                photo_path = f"uploads/attendance/{filename}"
                
            except Exception as e:
                current_app.logger.error(f"Erreur sauvegarde photo: {e}")
        
        # Déterminer l'action et mettre à jour
        if not attendance:
            # Premier pointage - Arrivée
            attendance = Attendance(
                employee_id=employee.id,
                date=today,
                check_in_morning=current_time,
                check_method=auth_method,
                device_info=device_info,
                latitude=latitude,
                longitude=longitude,
                location_name=location_name,
                check_in_photo=photo_path
            )
            
            # Vérifier si en retard (après 8h30)
            if current_time.time() > datetime.strptime("08:30", "%H:%M").time():
                attendance.is_late_morning = True
            
            db.session.add(attendance)
            action_type = "check_in"
            message = f"Bonjour {employee.full_name}! Arrivée enregistrée à {current_time.strftime('%H:%M')}"
            
        elif not attendance.check_out_lunch and current_time.hour < 14:
            # Départ midi
            attendance.check_out_lunch = current_time
            action_type = "check_out"
            message = f"Bon appétit {employee.full_name}! Pause déjeuner à {current_time.strftime('%H:%M')}"
            
        elif not attendance.check_in_afternoon and current_time.hour >= 12:
            # Retour après-midi
            attendance.check_in_afternoon = current_time
            
            # Vérifier si en retard (après 14h00)
            if current_time.time() > datetime.strptime("14:00", "%H:%M").time():
                attendance.is_late_afternoon = True
                
            action_type = "check_in"
            message = f"Bon retour {employee.full_name}! Reprise à {current_time.strftime('%H:%M')}"
            
        elif not attendance.check_out_evening:
            # Départ final
            attendance.check_out_evening = current_time
            attendance.check_out_photo = photo_path
            
            # Calculer les heures totales
            attendance.calculate_hours()
            
            action_type = "check_out"
            message = f"Bonne soirée {employee.full_name}! Journée terminée à {current_time.strftime('%H:%M')}. Total: {attendance.total_hours}h"
            
            # Vérifier la conformité
            if attendance.total_hours > 10:
                message += " ⚠️ Attention: dépassement des heures maximales journalières!"
                
        else:
            return jsonify({
                'success': False,
                'message': 'Tous les pointages du jour sont déjà enregistrés.'
            }), 400
        
        # Mettre à jour les infos de localisation
        attendance.latitude = latitude
        attendance.longitude = longitude
        attendance.location_name = location_name
        attendance.device_info = device_info
        
        db.session.commit()
        
        # Log d'audit
        AuditLog(
            user_id=employee.user_id if employee.user else None,
            action='attendance_check',
            model='Attendance',
            model_id=attendance.id,
            description=f"{action_type} via {auth_method}",
            category='hr',
            user_ip=request.remote_addr
        )
        
        return jsonify({
            'success': True,
            'message': message,
            'action_type': action_type,
            'attendance': {
                'id': attendance.id,
                'total_hours': attendance.total_hours,
                'overtime_hours': attendance.overtime_hours
            },
            'employee': {
                'id': employee.id,
                'name': employee.full_name,
                'position': employee.position,
                'department': employee.department,
                'photo': employee.user.photo_url if employee.user else None
            }
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Erreur pointage: {e}")
        return jsonify({
            'success': False,
            'message': 'Erreur lors du pointage. Veuillez réessayer.'
        }), 500

@badge_advanced_bp.route('/attendance/today')
def get_today_attendance():
    """Obtenir la liste des présences du jour"""
    try:
        today = date.today()
        
        # Requête avec jointure pour obtenir les infos employés
        attendances = db.session.query(
            Attendance,
            Employee,
            User
        ).join(
            Employee, Attendance.employee_id == Employee.id
        ).join(
            User, Employee.user_id == User.id
        ).filter(
            Attendance.date == today
        ).all()
        
        present = []
        absent = []
        late = []
        
        # Tous les employés actifs
        all_employees = Employee.query.filter_by(is_active=True).all()
        attended_ids = [att[0].employee_id for att in attendances]
        
        for att, emp, user in attendances:
            data = {
                'employee_id': emp.id,
                'name': user.full_name,
                'department': emp.department,
                'position': emp.position,
                'check_in': att.check_in_morning.strftime('%H:%M') if att.check_in_morning else None,
                'check_out': att.check_out_evening.strftime('%H:%M') if att.check_out_evening else None,
                'total_hours': att.total_hours,
                'is_late': att.is_late_morning or att.is_late_afternoon,
                'location': att.location_name
            }
            
            if att.check_in_morning and not att.check_out_evening:
                present.append(data)
            
            if att.is_late_morning or att.is_late_afternoon:
                late.append(data)
        
        # Employés absents
        for emp in all_employees:
            if emp.id not in attended_ids:
                # Vérifier s'ils sont en congé
                leave = Leave.query.filter(
                    and_(
                        Leave.employee_id == emp.id,
                        Leave.start_date <= today,
                        Leave.end_date >= today,
                        Leave.status == 'approved'
                    )
                ).first()
                
                absent.append({
                    'employee_id': emp.id,
                    'name': emp.full_name,
                    'department': emp.department,
                    'reason': leave.leave_type if leave else 'Non justifié'
                })
        
        return jsonify({
            'success': True,
            'date': today.strftime('%d/%m/%Y'),
            'stats': {
                'present': len(present),
                'absent': len(absent),
                'late': len(late),
                'total': len(all_employees)
            },
            'present_employees': present,
            'absent_employees': absent,
            'late_employees': late
        })
        
    except Exception as e:
        current_app.logger.error(f"Erreur récupération présences: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@badge_advanced_bp.route('/set-pin', methods=['POST'])
def set_employee_pin():
    """Définir ou modifier le code PIN d'un employé"""
    try:
        data = request.get_json()
        employee_id = data.get('employee_id')
        new_pin = data.get('pin')
        
        # Validation du PIN
        if not new_pin or len(new_pin) != 6 or not new_pin.isdigit():
            return jsonify({
                'success': False,
                'message': 'Le code PIN doit contenir exactement 6 chiffres.'
            }), 400
        
        employee = Employee.query.get_or_404(employee_id)
        
        # Hasher le PIN pour la sécurité
        employee.pin_code = hashlib.sha256(new_pin.encode()).hexdigest()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Code PIN défini avec succès.'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500