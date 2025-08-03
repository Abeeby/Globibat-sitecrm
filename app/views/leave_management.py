"""
Module de gestion des absences et congés
"""

from flask import Blueprint, render_template, request, jsonify, current_app
from app import db
from app.models import (Employee, Leave, Attendance, AuditLog, 
                       Notification, User, Payroll)
from app.utils.decorators import log_action
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from sqlalchemy import and_, or_, func, extract
import calendar

leave_bp = Blueprint('leave', __name__, url_prefix='/api/leave')

# Types de congés
LEAVE_TYPES = {
    'vacation': 'Congés payés',
    'sick': 'Maladie',
    'maternity': 'Maternité',
    'paternity': 'Paternité',
    'personal': 'Personnel',
    'unpaid': 'Non payé',
    'training': 'Formation',
    'military': 'Service militaire'
}

@leave_bp.route('/request', methods=['POST'])
@log_action('leave_request')
def request_leave():
    """Soumettre une demande de congé"""
    try:
        data = request.get_json()
        
        employee_id = data.get('employee_id')
        leave_type = data.get('leave_type')
        start_date = datetime.strptime(data.get('start_date'), '%Y-%m-%d').date()
        end_date = datetime.strptime(data.get('end_date'), '%Y-%m-%d').date()
        reason = data.get('reason')
        
        # Validation
        if end_date < start_date:
            return jsonify({
                'success': False,
                'message': 'La date de fin doit être après la date de début'
            }), 400
        
        employee = Employee.query.get_or_404(employee_id)
        
        # Créer la demande
        leave = Leave(
            employee_id=employee_id,
            leave_type=leave_type,
            start_date=start_date,
            end_date=end_date,
            reason=reason,
            status='pending',
            requested_at=datetime.utcnow()
        )
        
        # Calculer les jours (exclure weekends)
        leave.calculate_days()
        
        # Vérifier le solde de congés pour les congés payés
        if leave_type == 'vacation':
            employee.calculate_vacation_balance()
            
            if leave.total_days > employee.remaining_vacation:
                return jsonify({
                    'success': False,
                    'message': f'Solde de congés insuffisant. Disponible: {employee.remaining_vacation} jours'
                }), 400
        
        # Vérifier les conflits
        conflicts = check_leave_conflicts(employee_id, start_date, end_date)
        if conflicts:
            return jsonify({
                'success': False,
                'message': 'Conflit avec une autre absence ou congé',
                'conflicts': conflicts
            }), 400
        
        db.session.add(leave)
        db.session.commit()
        
        # Notification au manager
        if employee.department:
            manager = User.query.filter_by(
                role='manager',
                department=employee.department
            ).first()
            
            if manager:
                notification = Notification(
                    user_id=manager.id,
                    title="Nouvelle demande de congé",
                    message=f"{employee.full_name} demande {leave.total_days} jours de {LEAVE_TYPES.get(leave_type, leave_type)}",
                    type='info',
                    category='leave',
                    link_url=f"/leaves/approve/{leave.id}",
                    priority='normal'
                )
                db.session.add(notification)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Demande de congé soumise',
            'leave': {
                'id': leave.id,
                'total_days': leave.total_days,
                'status': leave.status
            }
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Erreur demande congé: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@leave_bp.route('/approve', methods=['POST'])
@log_action('leave_approve')
def approve_leave():
    """Approuver ou rejeter une demande de congé"""
    try:
        data = request.get_json()
        
        leave_id = data.get('leave_id')
        action = data.get('action')  # approve, reject
        approver_id = data.get('approver_id')
        comments = data.get('comments')
        
        if action not in ['approve', 'reject']:
            return jsonify({
                'success': False,
                'message': 'Action invalide'
            }), 400
        
        leave = Leave.query.get_or_404(leave_id)
        
        if leave.status != 'pending':
            return jsonify({
                'success': False,
                'message': 'Cette demande a déjà été traitée'
            }), 400
        
        if action == 'approve':
            leave.status = 'approved'
            leave.approved_by_id = approver_id
            leave.approved_at = datetime.utcnow()
            
            # Mettre à jour le solde de congés
            if leave.leave_type == 'vacation':
                leave.employee.remaining_vacation -= leave.total_days
            
            # Marquer les jours comme absents dans le calendrier
            create_absence_records(leave)
            
            message = "Demande de congé approuvée"
            notification_type = 'success'
            
        else:  # reject
            leave.status = 'rejected'
            leave.approved_by_id = approver_id
            leave.approved_at = datetime.utcnow()
            leave.reason = comments or "Demande rejetée"
            
            message = "Demande de congé rejetée"
            notification_type = 'error'
        
        # Notification à l'employé
        if leave.employee.user:
            notification = Notification(
                user_id=leave.employee.user_id,
                title=f"Demande de congé {leave.status == 'approved' ? 'approuvée' : 'rejetée'}",
                message=f"Votre demande du {leave.start_date.strftime('%d/%m/%Y')} au {leave.end_date.strftime('%d/%m/%Y')} a été {leave.status == 'approved' ? 'approuvée' : 'rejetée'}",
                type=notification_type,
                category='leave'
            )
            db.session.add(notification)
        
        # Log d'audit
        audit = AuditLog(
            user_id=approver_id,
            action=action,
            model='Leave',
            model_id=leave_id,
            description=f"{action} leave request for {leave.employee.full_name}",
            category='hr',
            severity='info'
        )
        db.session.add(audit)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': message
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Erreur approbation congé: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@leave_bp.route('/balance/<int:employee_id>')
def get_leave_balance(employee_id):
    """Obtenir le solde de congés d'un employé"""
    try:
        employee = Employee.query.get_or_404(employee_id)
        
        # Calculer le solde actuel
        employee.calculate_vacation_balance()
        
        # Congés pris cette année
        year_start = date.today().replace(month=1, day=1)
        year_end = date.today().replace(month=12, day=31)
        
        leaves_taken = db.session.query(
            Leave.leave_type,
            func.sum(Leave.total_days).label('days')
        ).filter(
            and_(
                Leave.employee_id == employee_id,
                Leave.status == 'approved',
                Leave.start_date >= year_start,
                Leave.end_date <= year_end
            )
        ).group_by(Leave.leave_type).all()
        
        # Formater les données
        leave_summary = {lt: 0 for lt in LEAVE_TYPES.keys()}
        for leave_type, days in leaves_taken:
            leave_summary[leave_type] = float(days or 0)
        
        # Congés en attente
        pending_leaves = Leave.query.filter(
            and_(
                Leave.employee_id == employee_id,
                Leave.status == 'pending'
            )
        ).all()
        
        pending_data = [{
            'id': leave.id,
            'type': leave.leave_type,
            'start_date': leave.start_date.strftime('%d/%m/%Y'),
            'end_date': leave.end_date.strftime('%d/%m/%Y'),
            'days': leave.total_days,
            'reason': leave.reason
        } for leave in pending_leaves]
        
        # Prochain congé approuvé
        next_leave = Leave.query.filter(
            and_(
                Leave.employee_id == employee_id,
                Leave.status == 'approved',
                Leave.start_date > date.today()
            )
        ).order_by(Leave.start_date).first()
        
        next_leave_data = None
        if next_leave:
            next_leave_data = {
                'type': next_leave.leave_type,
                'start_date': next_leave.start_date.strftime('%d/%m/%Y'),
                'end_date': next_leave.end_date.strftime('%d/%m/%Y'),
                'days': next_leave.total_days
            }
        
        return jsonify({
            'success': True,
            'employee': {
                'id': employee.id,
                'name': employee.full_name,
                'department': employee.department
            },
            'balance': {
                'annual_allowance': employee.vacation_days,
                'remaining': employee.remaining_vacation,
                'used': employee.vacation_days - employee.remaining_vacation
            },
            'leaves_taken': leave_summary,
            'pending_leaves': pending_data,
            'next_leave': next_leave_data
        })
        
    except Exception as e:
        current_app.logger.error(f"Erreur solde congés: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@leave_bp.route('/calendar')
def leave_calendar():
    """Calendrier des absences"""
    try:
        month = request.args.get('month', type=int, default=date.today().month)
        year = request.args.get('year', type=int, default=date.today().year)
        department = request.args.get('department')
        
        # Dates du mois
        month_start = date(year, month, 1)
        month_end = (month_start + relativedelta(months=1)) - timedelta(days=1)
        
        # Requête des congés
        query = db.session.query(
            Leave,
            Employee,
            User
        ).join(
            Employee, Leave.employee_id == Employee.id
        ).join(
            User, Employee.user_id == User.id
        ).filter(
            and_(
                Leave.status == 'approved',
                or_(
                    and_(Leave.start_date >= month_start, Leave.start_date <= month_end),
                    and_(Leave.end_date >= month_start, Leave.end_date <= month_end),
                    and_(Leave.start_date < month_start, Leave.end_date > month_end)
                )
            )
        )
        
        if department:
            query = query.filter(Employee.department == department)
        
        leaves = query.all()
        
        # Organiser par jour
        calendar_data = {}
        current = month_start
        
        while current <= month_end:
            day_key = current.strftime('%Y-%m-%d')
            calendar_data[day_key] = {
                'date': current.strftime('%d/%m/%Y'),
                'day_name': ['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim'][current.weekday()],
                'is_weekend': current.weekday() >= 5,
                'employees_absent': []
            }
            
            # Vérifier qui est absent ce jour
            for leave, employee, user in leaves:
                if leave.start_date <= current <= leave.end_date:
                    calendar_data[day_key]['employees_absent'].append({
                        'employee_id': employee.id,
                        'name': user.full_name,
                        'department': employee.department,
                        'leave_type': leave.leave_type,
                        'leave_type_label': LEAVE_TYPES.get(leave.leave_type, leave.leave_type)
                    })
            
            current += timedelta(days=1)
        
        # Statistiques du mois
        total_employees = Employee.query.filter_by(is_active=True)
        if department:
            total_employees = total_employees.filter_by(department=department)
        total_employees = total_employees.count()
        
        # Jours avec le plus d'absences
        max_absences = 0
        critical_days = []
        
        for day, data in calendar_data.items():
            if not data['is_weekend']:
                absence_count = len(data['employees_absent'])
                if absence_count > max_absences:
                    max_absences = absence_count
                    critical_days = [day]
                elif absence_count == max_absences and absence_count > 0:
                    critical_days.append(day)
        
        return jsonify({
            'success': True,
            'month': {
                'number': month,
                'name': calendar.month_name[month],
                'year': year
            },
            'calendar': calendar_data,
            'statistics': {
                'total_employees': total_employees,
                'max_absences_per_day': max_absences,
                'critical_days': critical_days
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"Erreur calendrier congés: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@leave_bp.route('/report')
def leave_report():
    """Rapport détaillé des absences"""
    try:
        # Paramètres
        year = request.args.get('year', type=int, default=date.today().year)
        department = request.args.get('department')
        leave_type = request.args.get('leave_type')
        
        # Statistiques par type de congé
        type_stats = db.session.query(
            Leave.leave_type,
            func.count(Leave.id).label('count'),
            func.sum(Leave.total_days).label('total_days')
        ).filter(
            and_(
                Leave.status == 'approved',
                extract('year', Leave.start_date) == year
            )
        )
        
        if department:
            type_stats = type_stats.join(
                Employee, Leave.employee_id == Employee.id
            ).filter(Employee.department == department)
        
        if leave_type:
            type_stats = type_stats.filter(Leave.leave_type == leave_type)
        
        type_stats = type_stats.group_by(Leave.leave_type).all()
        
        # Formater les statistiques par type
        leave_by_type = []
        total_leave_days = 0
        
        for lt, count, days in type_stats:
            leave_by_type.append({
                'type': lt,
                'label': LEAVE_TYPES.get(lt, lt),
                'count': count,
                'total_days': float(days or 0)
            })
            total_leave_days += days or 0
        
        # Statistiques par employé
        employee_stats = db.session.query(
            Employee,
            func.count(Leave.id).label('leave_count'),
            func.sum(Leave.total_days).label('total_days')
        ).join(
            Leave, Employee.id == Leave.employee_id
        ).filter(
            and_(
                Leave.status == 'approved',
                extract('year', Leave.start_date) == year
            )
        )
        
        if department:
            employee_stats = employee_stats.filter(Employee.department == department)
        
        if leave_type:
            employee_stats = employee_stats.filter(Leave.leave_type == leave_type)
        
        employee_stats = employee_stats.group_by(Employee.id).order_by(
            func.sum(Leave.total_days).desc()
        ).limit(10).all()
        
        # Top 10 employés avec le plus d'absences
        top_employees = []
        for emp, count, days in employee_stats:
            emp.calculate_vacation_balance()
            top_employees.append({
                'employee_id': emp.id,
                'name': emp.full_name,
                'department': emp.department,
                'leave_count': count,
                'total_days': float(days or 0),
                'remaining_vacation': emp.remaining_vacation
            })
        
        # Tendances mensuelles
        monthly_trends = db.session.query(
            extract('month', Leave.start_date).label('month'),
            func.count(Leave.id).label('count'),
            func.sum(Leave.total_days).label('days')
        ).filter(
            and_(
                Leave.status == 'approved',
                extract('year', Leave.start_date) == year
            )
        )
        
        if department:
            monthly_trends = monthly_trends.join(
                Employee, Leave.employee_id == Employee.id
            ).filter(Employee.department == department)
        
        monthly_trends = monthly_trends.group_by('month').all()
        
        # Formater les tendances
        trends = []
        for month_num, count, days in monthly_trends:
            trends.append({
                'month': int(month_num),
                'month_name': calendar.month_name[int(month_num)],
                'leave_count': count,
                'total_days': float(days or 0)
            })
        
        # Taux d'absentéisme
        total_employees = Employee.query.filter_by(is_active=True)
        if department:
            total_employees = total_employees.filter_by(department=department)
        total_employees = total_employees.count()
        
        working_days_year = calculate_working_days(date(year, 1, 1), date(year, 12, 31))
        potential_days = total_employees * working_days_year
        
        absenteeism_rate = (total_leave_days / potential_days * 100) if potential_days > 0 else 0
        
        return jsonify({
            'success': True,
            'year': year,
            'filters': {
                'department': department,
                'leave_type': leave_type
            },
            'summary': {
                'total_leave_days': total_leave_days,
                'absenteeism_rate': round(absenteeism_rate, 2),
                'average_days_per_employee': round(total_leave_days / total_employees, 1) if total_employees > 0 else 0
            },
            'by_type': leave_by_type,
            'top_employees': top_employees,
            'monthly_trends': trends
        })
        
    except Exception as e:
        current_app.logger.error(f"Erreur rapport congés: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

# Fonctions utilitaires
def check_leave_conflicts(employee_id, start_date, end_date):
    """Vérifier les conflits avec d'autres absences"""
    conflicts = []
    
    # Vérifier les congés existants
    existing_leaves = Leave.query.filter(
        and_(
            Leave.employee_id == employee_id,
            Leave.status.in_(['pending', 'approved']),
            or_(
                and_(Leave.start_date >= start_date, Leave.start_date <= end_date),
                and_(Leave.end_date >= start_date, Leave.end_date <= end_date),
                and_(Leave.start_date < start_date, Leave.end_date > end_date)
            )
        )
    ).all()
    
    for leave in existing_leaves:
        conflicts.append({
            'type': 'leave',
            'id': leave.id,
            'dates': f"{leave.start_date.strftime('%d/%m/%Y')} - {leave.end_date.strftime('%d/%m/%Y')}",
            'status': leave.status
        })
    
    return conflicts

def create_absence_records(leave):
    """Créer des enregistrements d'absence pour les jours de congé approuvés"""
    current = leave.start_date
    
    while current <= leave.end_date:
        # Ne pas créer pour les weekends
        if current.weekday() < 5:
            # Vérifier s'il n'y a pas déjà un pointage
            existing = Attendance.query.filter(
                and_(
                    Attendance.employee_id == leave.employee_id,
                    Attendance.date == current
                )
            ).first()
            
            if not existing:
                attendance = Attendance(
                    employee_id=leave.employee_id,
                    date=current,
                    is_absent=True,
                    notes=f"Congé: {LEAVE_TYPES.get(leave.leave_type, leave.leave_type)}"
                )
                db.session.add(attendance)
        
        current += timedelta(days=1)

def calculate_working_days(start_date, end_date):
    """Calculer le nombre de jours ouvrés dans une période"""
    days = 0
    current = start_date
    while current <= end_date:
        if current.weekday() < 5:  # Lundi à Vendredi
            days += 1
        current += timedelta(days=1)
    return days