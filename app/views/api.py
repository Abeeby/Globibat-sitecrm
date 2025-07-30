"""
Blueprint API - Endpoints REST
"""
from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app import db
from app.models import (
    Project, Client, Invoice, Employee, 
    Attendance, ProjectTask, Meeting
)
from app.utils.decorators import api_key_required
from datetime import datetime, date, timedelta
from sqlalchemy import func

bp = Blueprint('api', __name__, url_prefix='/api/v1')

# =======================
# AUTHENTIFICATION
# =======================

@bp.route('/auth/login', methods=['POST'])
def api_login():
    """Login API"""
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({'error': 'Email et mot de passe requis'}), 400
    
    from app.models import User
    user = User.query.filter_by(email=email).first()
    
    if user and user.check_password(password) and user.is_active:
        # Générer un token API (à implémenter)
        token = "temporary_token"  # TODO: Implémenter JWT
        
        return jsonify({
            'success': True,
            'token': token,
            'user': {
                'id': user.id,
                'email': user.email,
                'full_name': user.full_name,
                'role': user.role.name if user.role else None
            }
        })
    
    return jsonify({'error': 'Identifiants invalides'}), 401

# =======================
# DASHBOARD
# =======================

@bp.route('/dashboard/stats')
@login_required
def dashboard_stats():
    """Statistiques du dashboard"""
    stats = {
        'projects': {
            'total': Project.query.count(),
            'active': Project.query.filter_by(status='in_progress').count(),
            'completed_this_month': Project.query.filter(
                Project.status == 'completed',
                Project.actual_end_date >= date.today().replace(day=1)
            ).count()
        },
        'finance': {
            'revenue_this_month': float(db.session.query(
                func.sum(Invoice.total_amount)
            ).filter(
                Invoice.status == 'paid',
                Invoice.paid_date >= date.today().replace(day=1)
            ).scalar() or 0),
            'pending_payments': float(db.session.query(
                func.sum(Invoice.total_amount - Invoice.paid_amount)
            ).filter(
                Invoice.status.in_(['sent', 'partial', 'overdue'])
            ).scalar() or 0)
        },
        'employees': {
            'total': Employee.query.filter_by(is_active=True).count(),
            'present_today': Attendance.query.filter_by(
                date=date.today()
            ).count()
        },
        'tasks': {
            'overdue': ProjectTask.query.filter(
                ProjectTask.status != 'completed',
                ProjectTask.due_date < date.today()
            ).count(),
            'due_this_week': ProjectTask.query.filter(
                ProjectTask.status != 'completed',
                ProjectTask.due_date >= date.today(),
                ProjectTask.due_date <= date.today() + timedelta(days=7)
            ).count()
        }
    }
    
    return jsonify(stats)

@bp.route('/dashboard/charts')
@login_required
def dashboard_charts():
    """Données pour les graphiques du dashboard"""
    # Revenus des 6 derniers mois
    revenue_data = []
    for i in range(6):
        month_date = date.today() - timedelta(days=30*i)
        month_start = month_date.replace(day=1)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        
        revenue = db.session.query(
            func.sum(Invoice.total_amount)
        ).filter(
            Invoice.status == 'paid',
            Invoice.paid_date >= month_start,
            Invoice.paid_date <= month_end
        ).scalar() or 0
        
        revenue_data.append({
            'month': month_date.strftime('%B %Y'),
            'revenue': float(revenue)
        })
    
    revenue_data.reverse()
    
    # Projets par statut
    project_status = db.session.query(
        Project.status,
        func.count(Project.id)
    ).group_by(Project.status).all()
    
    # Heures travaillées cette semaine
    week_start = date.today() - timedelta(days=date.today().weekday())
    hours_data = []
    
    for i in range(7):
        day = week_start + timedelta(days=i)
        total_hours = db.session.query(
            func.sum(Attendance.total_hours)
        ).filter(
            Attendance.date == day
        ).scalar() or 0
        
        hours_data.append({
            'day': day.strftime('%A'),
            'hours': float(total_hours)
        })
    
    return jsonify({
        'revenue': revenue_data,
        'projects': [{'status': s, 'count': c} for s, c in project_status],
        'hours': hours_data
    })

# =======================
# POINTAGE / BADGEAGE
# =======================

@bp.route('/attendance/badge', methods=['POST'])
def attendance_badge():
    """Endpoint de badgeage pour application mobile"""
    data = request.get_json()
    employee_code = data.get('employee_code')
    badge_type = data.get('type')  # check_in_morning, check_out_lunch, etc.
    
    if not employee_code or not badge_type:
        return jsonify({'error': 'Code employé et type requis'}), 400
    
    employee = Employee.query.filter_by(
        employee_code=employee_code,
        is_active=True
    ).first()
    
    if not employee:
        return jsonify({'error': 'Employé non trouvé'}), 404
    
    # Obtenir ou créer le pointage du jour
    today = date.today()
    attendance = Attendance.query.filter_by(
        employee_id=employee.id,
        date=today
    ).first()
    
    if not attendance:
        attendance = Attendance(
            employee_id=employee.id,
            date=today
        )
        db.session.add(attendance)
    
    # Enregistrer le badgeage
    now = datetime.now()
    
    if badge_type == 'check_in_morning':
        if attendance.check_in_morning:
            return jsonify({'error': 'Déjà badgé ce matin'}), 400
        attendance.check_in_morning = now
        # Vérifier retard (après 8h30)
        if now.time() > datetime.strptime('08:30', '%H:%M').time():
            attendance.is_late_morning = True
    
    elif badge_type == 'check_out_lunch':
        if not attendance.check_in_morning:
            return jsonify({'error': 'Badge d\'arrivée manquant'}), 400
        if attendance.check_out_lunch:
            return jsonify({'error': 'Déjà badgé pour la pause'}), 400
        attendance.check_out_lunch = now
    
    elif badge_type == 'check_in_afternoon':
        if attendance.check_in_afternoon:
            return jsonify({'error': 'Déjà badgé cet après-midi'}), 400
        attendance.check_in_afternoon = now
        # Vérifier retard (après 14h00)
        if now.time() > datetime.strptime('14:00', '%H:%M').time():
            attendance.is_late_afternoon = True
    
    elif badge_type == 'check_out_evening':
        if attendance.check_out_evening:
            return jsonify({'error': 'Déjà badgé pour le départ'}), 400
        attendance.check_out_evening = now
        # Calculer les heures
        attendance.calculate_hours()
    
    else:
        return jsonify({'error': 'Type de badge invalide'}), 400
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'employee': employee.full_name,
        'time': now.strftime('%H:%M'),
        'total_hours': attendance.total_hours
    })

@bp.route('/attendance/employee/<int:employee_id>')
@login_required
def employee_attendance_history(employee_id):
    """Historique de pointage d'un employé"""
    employee = Employee.query.get_or_404(employee_id)
    
    # Vérifier les permissions
    if not current_user.has_permission('employees.view') and \
       (not current_user.employee or current_user.employee.id != employee_id):
        return jsonify({'error': 'Accès non autorisé'}), 403
    
    # Récupérer les pointages du mois
    month = request.args.get('month', date.today().month, type=int)
    year = request.args.get('year', date.today().year, type=int)
    
    attendances = Attendance.query.filter_by(
        employee_id=employee_id
    ).filter(
        db.extract('month', Attendance.date) == month,
        db.extract('year', Attendance.date) == year
    ).order_by(Attendance.date).all()
    
    data = []
    for att in attendances:
        data.append({
            'date': att.date.isoformat(),
            'check_in_morning': att.check_in_morning.isoformat() if att.check_in_morning else None,
            'check_out_lunch': att.check_out_lunch.isoformat() if att.check_out_lunch else None,
            'check_in_afternoon': att.check_in_afternoon.isoformat() if att.check_in_afternoon else None,
            'check_out_evening': att.check_out_evening.isoformat() if att.check_out_evening else None,
            'total_hours': att.total_hours,
            'overtime_hours': att.overtime_hours,
            'is_late': att.is_late_morning or att.is_late_afternoon
        })
    
    return jsonify({
        'employee': {
            'id': employee.id,
            'name': employee.full_name,
            'code': employee.employee_code
        },
        'month': month,
        'year': year,
        'attendances': data,
        'summary': {
            'total_days': len(attendances),
            'total_hours': sum(a.total_hours for a in attendances),
            'overtime_hours': sum(a.overtime_hours for a in attendances),
            'late_days': len([a for a in attendances if a.is_late_morning or a.is_late_afternoon])
        }
    })

# =======================
# PROJETS
# =======================

@bp.route('/projects')
@login_required
def api_projects_list():
    """Liste des projets"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    status = request.args.get('status')
    
    query = Project.query
    
    if status:
        query = query.filter_by(status=status)
    
    projects = query.order_by(Project.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    data = []
    for project in projects.items:
        data.append({
            'id': project.id,
            'code': project.project_code,
            'name': project.name,
            'client': project.client.display_name,
            'status': project.status,
            'completion': project.completion_percentage,
            'budget': {
                'approved': float(project.approved_budget or 0),
                'used': float(project.current_cost or 0),
                'status': project.budget_status
            },
            'dates': {
                'start': project.start_date.isoformat() if project.start_date else None,
                'planned_end': project.planned_end_date.isoformat() if project.planned_end_date else None,
                'is_overdue': project.is_overdue
            }
        })
    
    return jsonify({
        'projects': data,
        'pagination': {
            'page': projects.page,
            'pages': projects.pages,
            'total': projects.total,
            'per_page': per_page
        }
    })

@bp.route('/projects/<int:project_id>/tasks')
@login_required
def project_tasks(project_id):
    """Tâches d'un projet"""
    project = Project.query.get_or_404(project_id)
    
    tasks = ProjectTask.query.filter_by(
        project_id=project_id
    ).order_by(ProjectTask.due_date).all()
    
    data = []
    for task in tasks:
        data.append({
            'id': task.id,
            'title': task.title,
            'description': task.description,
            'status': task.status,
            'priority': task.priority,
            'assigned_to': task.assignee.full_name if task.assignee else None,
            'due_date': task.due_date.isoformat() if task.due_date else None,
            'is_overdue': task.is_overdue,
            'estimated_hours': task.estimated_hours,
            'actual_hours': task.actual_hours
        })
    
    return jsonify({
        'project': {
            'id': project.id,
            'name': project.name
        },
        'tasks': data
    })

# =======================
# CALENDRIER
# =======================

@bp.route('/calendar/events')
@login_required
def calendar_events():
    """Événements du calendrier"""
    start_date = request.args.get('start')
    end_date = request.args.get('end')
    
    if not start_date or not end_date:
        return jsonify({'error': 'Dates de début et fin requises'}), 400
    
    start = datetime.fromisoformat(start_date).date()
    end = datetime.fromisoformat(end_date).date()
    
    events = []
    
    # Réunions
    meetings = Meeting.query.filter(
        func.date(Meeting.scheduled_at) >= start,
        func.date(Meeting.scheduled_at) <= end,
        Meeting.status != 'cancelled'
    ).all()
    
    for meeting in meetings:
        events.append({
            'id': f'meeting_{meeting.id}',
            'title': meeting.subject,
            'start': meeting.scheduled_at.isoformat(),
            'end': (meeting.scheduled_at + timedelta(minutes=meeting.duration_minutes)).isoformat(),
            'type': 'meeting',
            'color': '#3788d8'
        })
    
    # Tâches avec échéance
    tasks = ProjectTask.query.filter(
        ProjectTask.due_date >= start,
        ProjectTask.due_date <= end,
        ProjectTask.status != 'completed'
    ).all()
    
    for task in tasks:
        events.append({
            'id': f'task_{task.id}',
            'title': task.title,
            'start': task.due_date.isoformat(),
            'allDay': True,
            'type': 'task',
            'color': '#dc3545' if task.priority == 'urgent' else '#ffc107'
        })
    
    # Congés approuvés
    from app.models import Leave
    leaves = Leave.query.filter(
        Leave.status == 'approved',
        Leave.start_date <= end,
        Leave.end_date >= start
    ).all()
    
    for leave in leaves:
        events.append({
            'id': f'leave_{leave.id}',
            'title': f'Congé: {leave.employee.full_name}',
            'start': leave.start_date.isoformat(),
            'end': (leave.end_date + timedelta(days=1)).isoformat(),
            'allDay': True,
            'type': 'leave',
            'color': '#6c757d'
        })
    
    return jsonify(events)

# =======================
# NOTIFICATIONS
# =======================

@bp.route('/notifications/unread')
@login_required
def unread_notifications():
    """Notifications non lues"""
    from app.models import Reminder
    
    reminders = Reminder.query.filter_by(
        user_id=current_user.id,
        is_read=False
    ).filter(
        Reminder.reminder_date <= datetime.utcnow()
    ).order_by(Reminder.priority.desc(), Reminder.reminder_date).all()
    
    data = []
    for reminder in reminders:
        data.append({
            'id': reminder.id,
            'title': reminder.title,
            'message': reminder.message,
            'type': reminder.reminder_type,
            'priority': reminder.priority,
            'date': reminder.reminder_date.isoformat(),
            'action_url': reminder.action_url
        })
    
    return jsonify({
        'count': len(data),
        'notifications': data
    })

@bp.route('/notifications/<int:notification_id>/read', methods=['POST'])
@login_required
def mark_notification_read(notification_id):
    """Marquer une notification comme lue"""
    from app.models import Reminder
    
    reminder = Reminder.query.filter_by(
        id=notification_id,
        user_id=current_user.id
    ).first_or_404()
    
    reminder.mark_as_read()
    db.session.commit()
    
    return jsonify({'success': True})