"""
Module de statistiques et analyses avancées
"""

from flask import Blueprint, render_template, request, jsonify, current_app
from app import db
from app.models import (Employee, Attendance, Leave, Payroll, Expense, 
                       Project, Invoice, EmployeeStatistics, CompanyDashboard,
                       WorkTimeRegulation)
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from sqlalchemy import and_, or_, func, extract, distinct
from decimal import Decimal
import calendar
import json

analytics_bp = Blueprint('analytics', __name__, url_prefix='/api/analytics')

@analytics_bp.route('/overview')
def company_analytics():
    """Vue d'ensemble analytique de l'entreprise"""
    try:
        # Période par défaut: 12 derniers mois
        end_date = date.today()
        start_date = end_date - relativedelta(months=12)
        
        # KPIs principaux
        kpis = calculate_company_kpis(start_date, end_date)
        
        # Tendances mensuelles
        monthly_trends = get_monthly_trends(start_date, end_date)
        
        # Répartition par département
        department_stats = get_department_statistics()
        
        # Performance des projets
        project_performance = get_project_performance()
        
        # Prévisions
        forecasts = calculate_forecasts()
        
        return jsonify({
            'success': True,
            'period': {
                'start': start_date.strftime('%d/%m/%Y'),
                'end': end_date.strftime('%d/%m/%Y')
            },
            'kpis': kpis,
            'trends': monthly_trends,
            'departments': department_stats,
            'projects': project_performance,
            'forecasts': forecasts
        })
        
    except Exception as e:
        current_app.logger.error(f"Erreur analytics overview: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@analytics_bp.route('/hr-metrics')
def hr_metrics():
    """Métriques RH détaillées"""
    try:
        year = request.args.get('year', type=int, default=date.today().year)
        
        # Effectifs
        headcount_evolution = db.session.query(
            extract('month', Employee.hire_date).label('month'),
            func.count(Employee.id).label('hires')
        ).filter(
            extract('year', Employee.hire_date) == year
        ).group_by('month').all()
        
        # Turnover
        turnover_data = calculate_turnover_rate(year)
        
        # Absentéisme
        absenteeism_data = calculate_absenteeism_metrics(year)
        
        # Heures supplémentaires
        overtime_metrics = db.session.query(
            extract('month', Attendance.date).label('month'),
            func.sum(Attendance.overtime_hours).label('total_overtime'),
            func.count(distinct(Attendance.employee_id)).label('employees_with_overtime')
        ).filter(
            and_(
                extract('year', Attendance.date) == year,
                Attendance.overtime_hours > 0
            )
        ).group_by('month').all()
        
        # Formation et développement
        training_stats = db.session.query(
            func.count(Leave.id).label('training_leaves'),
            func.sum(Leave.total_days).label('training_days')
        ).filter(
            and_(
                Leave.leave_type == 'training',
                Leave.status == 'approved',
                extract('year', Leave.start_date) == year
            )
        ).first()
        
        # Score de satisfaction (basé sur différents facteurs)
        satisfaction_score = calculate_employee_satisfaction()
        
        # Top performers
        top_performers = identify_top_performers(year)
        
        return jsonify({
            'success': True,
            'year': year,
            'headcount': {
                'evolution': [{
                    'month': int(month),
                    'hires': hires
                } for month, hires in headcount_evolution],
                'current': Employee.query.filter_by(is_active=True).count()
            },
            'turnover': turnover_data,
            'absenteeism': absenteeism_data,
            'overtime': [{
                'month': int(month),
                'total_hours': float(hours or 0),
                'employees_affected': count
            } for month, hours, count in overtime_metrics],
            'training': {
                'sessions': training_stats.training_leaves or 0,
                'total_days': float(training_stats.training_days or 0)
            },
            'satisfaction': satisfaction_score,
            'top_performers': top_performers
        })
        
    except Exception as e:
        current_app.logger.error(f"Erreur HR metrics: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@analytics_bp.route('/financial-analysis')
def financial_analysis():
    """Analyse financière approfondie"""
    try:
        period = request.args.get('period', 'year')
        year = request.args.get('year', type=int, default=date.today().year)
        
        if period == 'year':
            start_date = date(year, 1, 1)
            end_date = date(year, 12, 31)
        elif period == 'quarter':
            quarter = request.args.get('quarter', type=int, default=1)
            start_month = (quarter - 1) * 3 + 1
            start_date = date(year, start_month, 1)
            end_date = (start_date + relativedelta(months=3)) - timedelta(days=1)
        else:
            start_date = date.today() - relativedelta(months=1)
            end_date = date.today()
        
        # Coûts salariaux
        payroll_costs = db.session.query(
            extract('month', Payroll.period_start).label('month'),
            func.sum(Payroll.gross_salary).label('gross'),
            func.sum(Payroll.net_salary).label('net'),
            func.sum(Payroll.social_security + Payroll.unemployment + 
                    Payroll.pension + Payroll.accident_insurance).label('social_charges')
        ).filter(
            and_(
                Payroll.period_start >= start_date,
                Payroll.period_end <= end_date,
                Payroll.status == 'paid'
            )
        ).group_by('month').all()
        
        # Dépenses par catégorie
        expense_breakdown = db.session.query(
            Expense.category,
            func.count(Expense.id).label('count'),
            func.sum(Expense.total_amount).label('total')
        ).filter(
            and_(
                Expense.expense_date >= start_date,
                Expense.expense_date <= end_date,
                Expense.payment_status.in_(['approved', 'reimbursed'])
            )
        ).group_by(Expense.category).all()
        
        # Revenus (factures)
        revenue_data = db.session.query(
            extract('month', Invoice.issue_date).label('month'),
            func.sum(Invoice.total_amount).label('invoiced'),
            func.sum(Invoice.paid_amount).label('collected')
        ).filter(
            and_(
                Invoice.issue_date >= start_date,
                Invoice.issue_date <= end_date,
                Invoice.status != 'cancelled'
            )
        ).group_by('month').all()
        
        # Rentabilité par projet
        project_profitability = calculate_project_profitability(start_date, end_date)
        
        # Cash flow
        cash_flow = calculate_cash_flow(start_date, end_date)
        
        # Ratios financiers
        financial_ratios = calculate_financial_ratios(start_date, end_date)
        
        return jsonify({
            'success': True,
            'period': {
                'type': period,
                'start': start_date.strftime('%d/%m/%Y'),
                'end': end_date.strftime('%d/%m/%Y')
            },
            'payroll': [{
                'month': int(month),
                'gross': float(gross or 0),
                'net': float(net or 0),
                'charges': float(charges or 0)
            } for month, gross, net, charges in payroll_costs],
            'expenses': [{
                'category': cat,
                'count': count,
                'total': float(total or 0)
            } for cat, count, total in expense_breakdown],
            'revenue': [{
                'month': int(month),
                'invoiced': float(invoiced or 0),
                'collected': float(collected or 0)
            } for month, invoiced, collected in revenue_data],
            'project_profitability': project_profitability,
            'cash_flow': cash_flow,
            'ratios': financial_ratios
        })
        
    except Exception as e:
        current_app.logger.error(f"Erreur analyse financière: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@analytics_bp.route('/productivity-analysis')
def productivity_analysis():
    """Analyse de productivité"""
    try:
        department = request.args.get('department')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if not start_date:
            start_date = date.today() - relativedelta(months=3)
        else:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        
        if not end_date:
            end_date = date.today()
        else:
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        # Heures travaillées vs heures facturées
        productivity_data = db.session.query(
            Employee,
            func.sum(Attendance.total_hours).label('worked_hours'),
            func.sum(case([(Attendance.project_id != None, Attendance.total_hours)], else_=0)).label('billable_hours')
        ).join(
            Attendance, Employee.id == Attendance.employee_id
        ).filter(
            and_(
                Attendance.date >= start_date,
                Attendance.date <= end_date,
                Employee.is_active == True
            )
        )
        
        if department:
            productivity_data = productivity_data.filter(Employee.department == department)
        
        productivity_data = productivity_data.group_by(Employee.id).all()
        
        # Calculer les métriques
        employee_productivity = []
        total_worked = 0
        total_billable = 0
        
        for emp, worked, billable in productivity_data:
            worked = float(worked or 0)
            billable = float(billable or 0)
            utilization_rate = (billable / worked * 100) if worked > 0 else 0
            
            employee_productivity.append({
                'employee_id': emp.id,
                'name': emp.full_name,
                'department': emp.department,
                'worked_hours': worked,
                'billable_hours': billable,
                'utilization_rate': round(utilization_rate, 1)
            })
            
            total_worked += worked
            total_billable += billable
        
        # Trier par taux d'utilisation
        employee_productivity.sort(key=lambda x: x['utilization_rate'], reverse=True)
        
        # Productivité par jour de la semaine
        daily_productivity = db.session.query(
            func.extract('dow', Attendance.date).label('day_of_week'),
            func.avg(Attendance.total_hours).label('avg_hours')
        ).filter(
            and_(
                Attendance.date >= start_date,
                Attendance.date <= end_date
            )
        ).group_by('day_of_week').all()
        
        # Tendances de productivité
        weekly_trends = db.session.query(
            func.date_trunc('week', Attendance.date).label('week'),
            func.sum(Attendance.total_hours).label('total_hours'),
            func.count(distinct(Attendance.employee_id)).label('active_employees')
        ).filter(
            and_(
                Attendance.date >= start_date,
                Attendance.date <= end_date
            )
        ).group_by('week').order_by('week').all()
        
        return jsonify({
            'success': True,
            'period': {
                'start': start_date.strftime('%d/%m/%Y'),
                'end': end_date.strftime('%d/%m/%Y')
            },
            'summary': {
                'total_worked_hours': total_worked,
                'total_billable_hours': total_billable,
                'overall_utilization': round(total_billable / total_worked * 100, 1) if total_worked > 0 else 0
            },
            'employee_productivity': employee_productivity[:20],  # Top 20
            'daily_patterns': [{
                'day': ['Dim', 'Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam'][int(day)],
                'avg_hours': float(hours or 0)
            } for day, hours in daily_productivity],
            'weekly_trends': [{
                'week': week.strftime('%d/%m'),
                'total_hours': float(hours or 0),
                'avg_per_employee': float(hours / employees) if employees > 0 else 0
            } for week, hours, employees in weekly_trends]
        })
        
    except Exception as e:
        current_app.logger.error(f"Erreur analyse productivité: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@analytics_bp.route('/compliance-dashboard')
def compliance_dashboard():
    """Tableau de bord de conformité"""
    try:
        # Vérifier les violations des règles de temps de travail
        today = date.today()
        week_start = today - timedelta(days=today.weekday())
        
        # Violations journalières (>10h)
        daily_violations = db.session.query(
            Attendance,
            Employee
        ).join(
            Employee, Attendance.employee_id == Employee.id
        ).filter(
            and_(
                Attendance.date >= week_start,
                Attendance.total_hours > 10
            )
        ).all()
        
        # Violations hebdomadaires (>50h)
        weekly_violations = db.session.query(
            Employee,
            func.sum(Attendance.total_hours).label('weekly_hours')
        ).join(
            Attendance, Employee.id == Attendance.employee_id
        ).filter(
            Attendance.date >= week_start
        ).group_by(Employee.id).having(
            func.sum(Attendance.total_hours) > 50
        ).all()
        
        # Pauses manquantes
        break_violations = check_break_violations()
        
        # Documents expirés
        expired_documents = check_expired_documents()
        
        # Formations obligatoires manquantes
        missing_trainings = check_missing_trainings()
        
        # Score de conformité global
        compliance_score = calculate_compliance_score()
        
        return jsonify({
            'success': True,
            'violations': {
                'daily_overtime': [{
                    'employee': att.employee.full_name,
                    'date': att.date.strftime('%d/%m/%Y'),
                    'hours': att.total_hours
                } for att, emp in daily_violations],
                'weekly_overtime': [{
                    'employee': emp.full_name,
                    'hours': float(hours)
                } for emp, hours in weekly_violations],
                'break_violations': break_violations,
                'total_violations': len(daily_violations) + len(weekly_violations) + len(break_violations)
            },
            'documents': {
                'expired': expired_documents,
                'expiring_soon': []  # TODO: Implémenter
            },
            'trainings': {
                'missing': missing_trainings
            },
            'compliance_score': compliance_score,
            'recommendations': generate_compliance_recommendations()
        })
        
    except Exception as e:
        current_app.logger.error(f"Erreur compliance dashboard: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

# Fonctions utilitaires
def calculate_company_kpis(start_date, end_date):
    """Calculer les KPIs principaux de l'entreprise"""
    # Effectif moyen
    avg_headcount = Employee.query.filter_by(is_active=True).count()
    
    # Chiffre d'affaires
    revenue = db.session.query(func.sum(Invoice.paid_amount)).filter(
        and_(
            Invoice.paid_date >= start_date,
            Invoice.paid_date <= end_date
        )
    ).scalar() or 0
    
    # Coûts totaux
    payroll_costs = db.session.query(func.sum(Payroll.gross_salary)).filter(
        and_(
            Payroll.period_start >= start_date,
            Payroll.period_end <= end_date,
            Payroll.status == 'paid'
        )
    ).scalar() or 0
    
    expense_costs = db.session.query(func.sum(Expense.total_amount)).filter(
        and_(
            Expense.expense_date >= start_date,
            Expense.expense_date <= end_date,
            Expense.payment_status == 'reimbursed'
        )
    ).scalar() or 0
    
    # Marge
    margin = float(revenue) - float(payroll_costs) - float(expense_costs)
    margin_rate = (margin / float(revenue) * 100) if revenue > 0 else 0
    
    return {
        'headcount': avg_headcount,
        'revenue': float(revenue),
        'payroll_costs': float(payroll_costs),
        'expense_costs': float(expense_costs),
        'total_costs': float(payroll_costs) + float(expense_costs),
        'margin': margin,
        'margin_rate': round(margin_rate, 1)
    }

def get_monthly_trends(start_date, end_date):
    """Obtenir les tendances mensuelles"""
    trends = []
    current = start_date.replace(day=1)
    
    while current <= end_date:
        month_end = (current + relativedelta(months=1)) - timedelta(days=1)
        
        # Métriques du mois
        revenue = db.session.query(func.sum(Invoice.total_amount)).filter(
            and_(
                Invoice.issue_date >= current,
                Invoice.issue_date <= month_end,
                Invoice.status != 'cancelled'
            )
        ).scalar() or 0
        
        costs = db.session.query(func.sum(Payroll.gross_salary)).filter(
            and_(
                Payroll.month == current.month,
                Payroll.year == current.year,
                Payroll.status == 'paid'
            )
        ).scalar() or 0
        
        hours = db.session.query(func.sum(Attendance.total_hours)).filter(
            and_(
                Attendance.date >= current,
                Attendance.date <= month_end
            )
        ).scalar() or 0
        
        trends.append({
            'month': current.strftime('%Y-%m'),
            'month_name': f"{calendar.month_name[current.month]} {current.year}",
            'revenue': float(revenue),
            'costs': float(costs),
            'hours': float(hours or 0)
        })
        
        current += relativedelta(months=1)
    
    return trends

def calculate_turnover_rate(year):
    """Calculer le taux de turnover"""
    # Employés au début de l'année
    start_count = Employee.query.filter(
        Employee.hire_date < date(year, 1, 1)
    ).count()
    
    # Départs durant l'année
    departures = Employee.query.filter(
        and_(
            Employee.end_date != None,
            extract('year', Employee.end_date) == year
        )
    ).count()
    
    # Nouvelles embauches
    hires = Employee.query.filter(
        extract('year', Employee.hire_date) == year
    ).count()
    
    # Taux de turnover
    avg_headcount = (start_count + Employee.query.filter_by(is_active=True).count()) / 2
    turnover_rate = (departures / avg_headcount * 100) if avg_headcount > 0 else 0
    
    return {
        'departures': departures,
        'hires': hires,
        'turnover_rate': round(turnover_rate, 1),
        'net_change': hires - departures
    }

def calculate_absenteeism_metrics(year):
    """Calculer les métriques d'absentéisme"""
    # Total jours d'absence (hors congés payés)
    absences = db.session.query(
        func.sum(Leave.total_days)
    ).filter(
        and_(
            Leave.status == 'approved',
            Leave.leave_type != 'vacation',
            extract('year', Leave.start_date) == year
        )
    ).scalar() or 0
    
    # Jours ouvrés théoriques
    working_days = calculate_working_days(date(year, 1, 1), date(year, 12, 31))
    active_employees = Employee.query.filter_by(is_active=True).count()
    theoretical_days = working_days * active_employees
    
    # Taux d'absentéisme
    absenteeism_rate = (float(absences) / theoretical_days * 100) if theoretical_days > 0 else 0
    
    return {
        'total_absence_days': float(absences),
        'absenteeism_rate': round(absenteeism_rate, 2),
        'avg_days_per_employee': round(float(absences) / active_employees, 1) if active_employees > 0 else 0
    }

def identify_top_performers(year):
    """Identifier les top performers"""
    # Basé sur plusieurs critères
    employees = Employee.query.filter_by(is_active=True).all()
    
    performers = []
    for emp in employees:
        # Taux de présence
        worked_days = Attendance.query.filter(
            and_(
                Attendance.employee_id == emp.id,
                extract('year', Attendance.date) == year
            )
        ).count()
        
        # Heures supplémentaires (modérées)
        overtime = db.session.query(
            func.sum(Attendance.overtime_hours)
        ).filter(
            and_(
                Attendance.employee_id == emp.id,
                extract('year', Attendance.date) == year
            )
        ).scalar() or 0
        
        # Projets
        projects = db.session.query(
            func.count(distinct(Attendance.project_id))
        ).filter(
            and_(
                Attendance.employee_id == emp.id,
                Attendance.project_id != None,
                extract('year', Attendance.date) == year
            )
        ).scalar() or 0
        
        # Score composite
        score = (worked_days * 0.4) + (min(float(overtime), 100) * 0.3) + (projects * 10)
        
        performers.append({
            'employee_id': emp.id,
            'name': emp.full_name,
            'department': emp.department,
            'score': round(score, 1),
            'metrics': {
                'attendance_days': worked_days,
                'overtime_hours': float(overtime),
                'projects': projects
            }
        })
    
    # Trier par score
    performers.sort(key=lambda x: x['score'], reverse=True)
    
    return performers[:10]  # Top 10

def calculate_working_days(start_date, end_date):
    """Calculer le nombre de jours ouvrés"""
    days = 0
    current = start_date
    while current <= end_date:
        if current.weekday() < 5:
            days += 1
        current += timedelta(days=1)
    return days