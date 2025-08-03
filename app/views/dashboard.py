"""
Tableaux de bord et rapports avancés
"""

from flask import Blueprint, render_template, request, jsonify, send_file, current_app
from app import db
from app.models import (Employee, Attendance, Leave, Payroll, Expense, 
                       EmployeeStatistics, CompanyDashboard, WorkTimeRegulation,
                       Project, Invoice)
from app.utils.pdf import generate_timesheet_pdf, generate_payslip_pdf
from datetime import datetime, date, timedelta
from sqlalchemy import and_, or_, func, extract
from decimal import Decimal
import pandas as pd
import io

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/api/dashboard')

@dashboard_bp.route('/overview')
def company_overview():
    """Vue d'ensemble de l'entreprise"""
    try:
        today = date.today()
        
        # Récupérer ou créer le dashboard du jour
        dashboard = CompanyDashboard.query.filter_by(date=today).first()
        
        if not dashboard or (datetime.now() - dashboard.last_updated).seconds > 300:  # Refresh toutes les 5 min
            # Calculer les stats
            total_employees = Employee.query.filter_by(is_active=True).count()
            
            # Présences du jour
            present_query = Attendance.query.filter(
                and_(
                    Attendance.date == today,
                    Attendance.check_in_morning != None
                )
            )
            present_count = present_query.count()
            
            # Absents
            all_employee_ids = [e.id for e in Employee.query.filter_by(is_active=True).all()]
            present_ids = [a.employee_id for a in present_query.all()]
            absent_ids = set(all_employee_ids) - set(present_ids)
            
            # En congé
            on_leave = Leave.query.filter(
                and_(
                    Leave.start_date <= today,
                    Leave.end_date >= today,
                    Leave.status == 'approved'
                )
            ).count()
            
            # Heures totales aujourd'hui
            total_hours = db.session.query(func.sum(Attendance.total_hours)).filter(
                Attendance.date == today
            ).scalar() or 0
            
            overtime_hours = db.session.query(func.sum(Attendance.overtime_hours)).filter(
                Attendance.date == today
            ).scalar() or 0
            
            # Coûts estimés
            labor_cost = calculate_daily_labor_cost(today)
            
            # Dépenses du jour
            expense_cost = db.session.query(func.sum(Expense.total_amount)).filter(
                Expense.expense_date == today,
                Expense.payment_status == 'approved'
            ).scalar() or 0
            
            # Projets actifs
            active_projects = Project.query.filter_by(status='active').count()
            
            # Approbations en attente
            pending_expenses = Expense.query.filter_by(payment_status='pending').count()
            pending_leaves = Leave.query.filter_by(status='pending').count()
            
            # Vérifier la conformité
            compliance_alerts = check_compliance_issues()
            
            # Mettre à jour ou créer
            if not dashboard:
                dashboard = CompanyDashboard(date=today)
                db.session.add(dashboard)
            
            dashboard.total_employees = total_employees
            dashboard.present_today = present_count
            dashboard.absent_today = len(absent_ids) - on_leave
            dashboard.on_leave = on_leave
            dashboard.total_hours_today = float(total_hours)
            dashboard.overtime_hours_today = float(overtime_hours)
            dashboard.labor_cost_today = Decimal(str(labor_cost))
            dashboard.expense_cost_today = Decimal(str(expense_cost))
            dashboard.active_projects = active_projects
            dashboard.pending_approvals = pending_expenses + pending_leaves
            dashboard.compliance_alerts = compliance_alerts
            dashboard.last_updated = datetime.now()
            
            db.session.commit()
        
        return jsonify({
            'success': True,
            'dashboard': {
                'date': dashboard.date.strftime('%d/%m/%Y'),
                'employees': {
                    'total': dashboard.total_employees,
                    'present': dashboard.present_today,
                    'absent': dashboard.absent_today,
                    'on_leave': dashboard.on_leave
                },
                'hours': {
                    'total': dashboard.total_hours_today,
                    'overtime': dashboard.overtime_hours_today
                },
                'costs': {
                    'labor': float(dashboard.labor_cost_today),
                    'expenses': float(dashboard.expense_cost_today),
                    'total': float(dashboard.labor_cost_today + dashboard.expense_cost_today)
                },
                'projects': {
                    'active': dashboard.active_projects
                },
                'alerts': {
                    'pending_approvals': dashboard.pending_approvals,
                    'compliance': dashboard.compliance_alerts
                }
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"Erreur dashboard: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@dashboard_bp.route('/attendance/report')
def attendance_report():
    """Rapport de présence avec filtres"""
    try:
        # Paramètres de filtrage
        period = request.args.get('period', 'week')  # day, week, biweek, month, custom
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        department = request.args.get('department')
        employee_id = request.args.get('employee_id')
        
        # Déterminer la période
        if period == 'day':
            start = end = date.today()
        elif period == 'week':
            start = date.today() - timedelta(days=date.today().weekday())
            end = start + timedelta(days=6)
        elif period == 'biweek':
            start = date.today() - timedelta(days=date.today().weekday() + 7)
            end = start + timedelta(days=13)
        elif period == 'month':
            start = date.today().replace(day=1)
            next_month = start.replace(day=28) + timedelta(days=4)
            end = next_month - timedelta(days=next_month.day)
        elif period == 'custom' and start_date and end_date:
            start = datetime.strptime(start_date, '%Y-%m-%d').date()
            end = datetime.strptime(end_date, '%Y-%m-%d').date()
        else:
            start = date.today() - timedelta(days=7)
            end = date.today()
        
        # Construire la requête
        query = db.session.query(
            Attendance,
            Employee,
            User
        ).join(
            Employee, Attendance.employee_id == Employee.id
        ).join(
            User, Employee.user_id == User.id
        ).filter(
            and_(
                Attendance.date >= start,
                Attendance.date <= end
            )
        )
        
        # Filtres additionnels
        if department:
            query = query.filter(Employee.department == department)
        
        if employee_id:
            query = query.filter(Employee.id == int(employee_id))
        
        attendances = query.all()
        
        # Organiser les données par employé
        employee_data = {}
        
        for att, emp, user in attendances:
            if emp.id not in employee_data:
                employee_data[emp.id] = {
                    'employee': {
                        'id': emp.id,
                        'name': user.full_name,
                        'department': emp.department,
                        'position': emp.position
                    },
                    'attendance': [],
                    'summary': {
                        'total_days': 0,
                        'present_days': 0,
                        'absent_days': 0,
                        'late_days': 0,
                        'total_hours': 0,
                        'regular_hours': 0,
                        'overtime_hours': 0
                    }
                }
            
            # Ajouter les détails de présence
            employee_data[emp.id]['attendance'].append({
                'date': att.date.strftime('%Y-%m-%d'),
                'check_in': att.check_in_morning.strftime('%H:%M') if att.check_in_morning else None,
                'check_out': att.check_out_evening.strftime('%H:%M') if att.check_out_evening else None,
                'total_hours': att.total_hours,
                'overtime_hours': att.overtime_hours,
                'is_late': att.is_late_morning or att.is_late_afternoon,
                'location': att.location_name
            })
            
            # Mettre à jour le résumé
            summary = employee_data[emp.id]['summary']
            summary['present_days'] += 1
            summary['total_hours'] += att.total_hours or 0
            summary['overtime_hours'] += att.overtime_hours or 0
            
            if att.is_late_morning or att.is_late_afternoon:
                summary['late_days'] += 1
        
        # Calculer les jours travaillés dans la période
        working_days = calculate_working_days(start, end)
        
        # Finaliser les résumés
        for emp_id, data in employee_data.items():
            summary = data['summary']
            summary['total_days'] = working_days
            summary['absent_days'] = working_days - summary['present_days']
            summary['regular_hours'] = summary['total_hours'] - summary['overtime_hours']
            summary['attendance_rate'] = round(summary['present_days'] / working_days * 100, 1)
        
        return jsonify({
            'success': True,
            'period': {
                'type': period,
                'start': start.strftime('%d/%m/%Y'),
                'end': end.strftime('%d/%m/%Y'),
                'working_days': working_days
            },
            'data': list(employee_data.values()),
            'summary': {
                'total_employees': len(employee_data),
                'total_hours': sum(d['summary']['total_hours'] for d in employee_data.values()),
                'total_overtime': sum(d['summary']['overtime_hours'] for d in employee_data.values()),
                'average_attendance_rate': round(
                    sum(d['summary']['attendance_rate'] for d in employee_data.values()) / len(employee_data) if employee_data else 0,
                    1
                )
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"Erreur rapport présence: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@dashboard_bp.route('/timesheet/generate', methods=['POST'])
def generate_timesheet():
    """Générer une feuille de temps PDF"""
    try:
        data = request.get_json()
        employee_id = data.get('employee_id')
        start_date = datetime.strptime(data.get('start_date'), '%Y-%m-%d').date()
        end_date = datetime.strptime(data.get('end_date'), '%Y-%m-%d').date()
        format_type = data.get('format', 'pdf')  # pdf ou excel
        
        employee = Employee.query.get_or_404(employee_id)
        
        # Récupérer les données de présence
        attendances = Attendance.query.filter(
            and_(
                Attendance.employee_id == employee_id,
                Attendance.date >= start_date,
                Attendance.date <= end_date
            )
        ).order_by(Attendance.date).all()
        
        if format_type == 'excel':
            # Générer Excel
            df_data = []
            for att in attendances:
                df_data.append({
                    'Date': att.date.strftime('%d/%m/%Y'),
                    'Jour': ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche'][att.date.weekday()],
                    'Arrivée Matin': att.check_in_morning.strftime('%H:%M') if att.check_in_morning else '',
                    'Départ Midi': att.check_out_lunch.strftime('%H:%M') if att.check_out_lunch else '',
                    'Arrivée Après-midi': att.check_in_afternoon.strftime('%H:%M') if att.check_in_afternoon else '',
                    'Départ Soir': att.check_out_evening.strftime('%H:%M') if att.check_out_evening else '',
                    'Heures Totales': att.total_hours or 0,
                    'Heures Supp.': att.overtime_hours or 0,
                    'Projet': att.project.name if att.project else '',
                    'Lieu': att.location_name or ''
                })
            
            df = pd.DataFrame(df_data)
            
            # Ajouter les totaux
            totals = pd.DataFrame([{
                'Date': 'TOTAL',
                'Jour': '',
                'Arrivée Matin': '',
                'Départ Midi': '',
                'Arrivée Après-midi': '',
                'Départ Soir': '',
                'Heures Totales': df['Heures Totales'].sum(),
                'Heures Supp.': df['Heures Supp.'].sum(),
                'Projet': '',
                'Lieu': ''
            }])
            
            df = pd.concat([df, totals], ignore_index=True)
            
            # Créer le fichier Excel
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, sheet_name='Feuille de temps', index=False)
                
                # Formater
                workbook = writer.book
                worksheet = writer.sheets['Feuille de temps']
                
                # Format pour les headers
                header_format = workbook.add_format({
                    'bold': True,
                    'bg_color': '#4CAF50',
                    'font_color': 'white',
                    'align': 'center',
                    'valign': 'vcenter'
                })
                
                # Appliquer le format aux headers
                for col_num, value in enumerate(df.columns.values):
                    worksheet.write(0, col_num, value, header_format)
                
                # Ajuster la largeur des colonnes
                worksheet.set_column('A:A', 12)
                worksheet.set_column('B:B', 10)
                worksheet.set_column('C:F', 15)
                worksheet.set_column('G:H', 12)
                worksheet.set_column('I:J', 20)
            
            output.seek(0)
            
            return send_file(
                output,
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                as_attachment=True,
                download_name=f'feuille_temps_{employee.employee_code}_{start_date.strftime("%Y%m%d")}_{end_date.strftime("%Y%m%d")}.xlsx'
            )
            
        else:
            # Générer PDF
            pdf_buffer = generate_timesheet_pdf(employee, attendances, start_date, end_date)
            
            return send_file(
                pdf_buffer,
                mimetype='application/pdf',
                as_attachment=True,
                download_name=f'feuille_temps_{employee.employee_code}_{start_date.strftime("%Y%m%d")}_{end_date.strftime("%Y%m%d")}.pdf'
            )
            
    except Exception as e:
        current_app.logger.error(f"Erreur génération feuille de temps: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@dashboard_bp.route('/statistics/employee/<int:employee_id>')
def employee_statistics(employee_id):
    """Statistiques détaillées d'un employé"""
    try:
        period = request.args.get('period', 'month')
        
        employee = Employee.query.get_or_404(employee_id)
        
        # Calculer les dates selon la période
        if period == 'week':
            start_date = date.today() - timedelta(days=date.today().weekday())
            end_date = start_date + timedelta(days=6)
        elif period == 'month':
            start_date = date.today().replace(day=1)
            next_month = start_date.replace(day=28) + timedelta(days=4)
            end_date = next_month - timedelta(days=next_month.day)
        elif period == 'year':
            start_date = date.today().replace(month=1, day=1)
            end_date = date.today().replace(month=12, day=31)
        else:
            start_date = date.today() - timedelta(days=30)
            end_date = date.today()
        
        # Statistiques de présence
        attendance_stats = db.session.query(
            func.count(Attendance.id).label('days_worked'),
            func.sum(Attendance.total_hours).label('total_hours'),
            func.sum(Attendance.overtime_hours).label('overtime_hours'),
            func.sum(func.cast(Attendance.is_late_morning, db.Integer)).label('late_mornings'),
            func.sum(func.cast(Attendance.is_late_afternoon, db.Integer)).label('late_afternoons')
        ).filter(
            and_(
                Attendance.employee_id == employee_id,
                Attendance.date >= start_date,
                Attendance.date <= end_date
            )
        ).first()
        
        # Congés
        leaves = Leave.query.filter(
            and_(
                Leave.employee_id == employee_id,
                Leave.status == 'approved',
                or_(
                    and_(Leave.start_date >= start_date, Leave.start_date <= end_date),
                    and_(Leave.end_date >= start_date, Leave.end_date <= end_date)
                )
            )
        ).all()
        
        leave_stats = {}
        total_leave_days = 0
        
        for leave in leaves:
            if leave.leave_type not in leave_stats:
                leave_stats[leave.leave_type] = 0
            leave_stats[leave.leave_type] += leave.total_days or 0
            total_leave_days += leave.total_days or 0
        
        # Dépenses
        expense_stats = db.session.query(
            func.count(Expense.id).label('total_expenses'),
            func.sum(Expense.total_amount).label('total_amount'),
            Expense.category
        ).filter(
            and_(
                Expense.employee_id == employee_id,
                Expense.expense_date >= start_date,
                Expense.expense_date <= end_date,
                Expense.payment_status != 'rejected'
            )
        ).group_by(Expense.category).all()
        
        expense_by_category = {
            stat.category: {
                'count': stat.total_expenses,
                'amount': float(stat.total_amount or 0)
            } for stat in expense_stats
        }
        
        # Projets travaillés
        projects = db.session.query(
            Project,
            func.count(Attendance.id).label('days_on_project')
        ).join(
            Attendance, Attendance.project_id == Project.id
        ).filter(
            and_(
                Attendance.employee_id == employee_id,
                Attendance.date >= start_date,
                Attendance.date <= end_date
            )
        ).group_by(Project.id).all()
        
        project_data = [{
            'id': proj.id,
            'name': proj.name,
            'days_worked': days,
            'status': proj.status
        } for proj, days in projects]
        
        # Calculer le taux de productivité
        working_days = calculate_working_days(start_date, end_date)
        attendance_rate = (attendance_stats.days_worked / working_days * 100) if working_days > 0 else 0
        
        # Score de productivité (basé sur plusieurs facteurs)
        productivity_score = calculate_productivity_score(
            attendance_rate,
            attendance_stats.late_mornings + attendance_stats.late_afternoons,
            attendance_stats.overtime_hours or 0,
            len(project_data)
        )
        
        return jsonify({
            'success': True,
            'employee': {
                'id': employee.id,
                'name': employee.full_name,
                'department': employee.department,
                'position': employee.position
            },
            'period': {
                'type': period,
                'start': start_date.strftime('%d/%m/%Y'),
                'end': end_date.strftime('%d/%m/%Y')
            },
            'attendance': {
                'days_worked': attendance_stats.days_worked or 0,
                'total_hours': float(attendance_stats.total_hours or 0),
                'regular_hours': float((attendance_stats.total_hours or 0) - (attendance_stats.overtime_hours or 0)),
                'overtime_hours': float(attendance_stats.overtime_hours or 0),
                'late_arrivals': (attendance_stats.late_mornings or 0) + (attendance_stats.late_afternoons or 0),
                'attendance_rate': round(attendance_rate, 1)
            },
            'leaves': {
                'total_days': total_leave_days,
                'by_type': leave_stats,
                'remaining_vacation': employee.remaining_vacation
            },
            'expenses': {
                'total_amount': sum(cat['amount'] for cat in expense_by_category.values()),
                'by_category': expense_by_category
            },
            'projects': project_data,
            'performance': {
                'productivity_score': productivity_score,
                'rating': get_performance_rating(productivity_score)
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"Erreur statistiques employé: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

# Fonctions utilitaires
def calculate_working_days(start_date, end_date):
    """Calculer le nombre de jours ouvrés dans une période"""
    days = 0
    current = start_date
    while current <= end_date:
        if current.weekday() < 5:  # Lundi à Vendredi
            days += 1
        current += timedelta(days=1)
    return days

def calculate_daily_labor_cost(date):
    """Calculer le coût de main d'œuvre pour une journée"""
    attendances = Attendance.query.filter_by(date=date).all()
    total_cost = 0
    
    for att in attendances:
        if att.employee and att.employee.hourly_rate and att.total_hours:
            regular_cost = min(att.total_hours, 8) * float(att.employee.hourly_rate)
            overtime_cost = max(0, att.total_hours - 8) * float(att.employee.hourly_rate) * 1.25
            total_cost += regular_cost + overtime_cost
    
    return total_cost

def check_compliance_issues():
    """Vérifier les problèmes de conformité"""
    alerts = []
    today = date.today()
    
    # Vérifier les heures maximales
    violations = db.session.query(Attendance).filter(
        and_(
            Attendance.date == today,
            Attendance.total_hours > 10
        )
    ).all()
    
    for v in violations:
        alerts.append({
            'type': 'overtime_violation',
            'message': f"{v.employee.full_name} a travaillé {v.total_hours}h (max: 10h)",
            'severity': 'warning'
        })
    
    # Vérifier les repos obligatoires
    # TODO: Implémenter d'autres vérifications
    
    return alerts

def calculate_productivity_score(attendance_rate, late_count, overtime_hours, projects_count):
    """Calculer un score de productivité (0-100)"""
    # Base sur le taux de présence (40%)
    attendance_score = attendance_rate * 0.4
    
    # Pénalité pour les retards (20%)
    late_penalty = max(0, 20 - late_count * 2)
    
    # Bonus pour les heures supplémentaires modérées (20%)
    overtime_bonus = min(20, overtime_hours * 2) if overtime_hours < 20 else 10
    
    # Bonus pour les projets (20%)
    project_bonus = min(20, projects_count * 5)
    
    return round(attendance_score + late_penalty + overtime_bonus + project_bonus, 1)

def get_performance_rating(score):
    """Obtenir une évaluation basée sur le score"""
    if score >= 90:
        return "Excellent"
    elif score >= 75:
        return "Très bon"
    elif score >= 60:
        return "Bon"
    elif score >= 40:
        return "À améliorer"
    else:
        return "Insuffisant"