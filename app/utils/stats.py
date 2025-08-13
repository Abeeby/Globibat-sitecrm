"""
Module de statistiques pour les tableaux de bord
"""
from datetime import datetime, date, timedelta
from app import db

def get_dashboard_stats():
    """Récupérer les statistiques pour le tableau de bord principal"""
    from app.models.employee import Employee
    from app.models.client import Client
    from app.models.project import Project
    
    today = date.today()
    month_start = today.replace(day=1)
    
    stats = {
        'total_employees': Employee.query.filter_by(is_active=True).count(),
        'total_clients': Client.query.filter_by(is_active=True).count(),
        'active_projects': Project.query.filter_by(status='En cours').count(),
        'month': today.strftime('%B %Y'),
        'today': today.strftime('%d/%m/%Y'),
        'alerts': [],
        'recent_activities': []
    }
    
    return stats

def get_employee_stats(employee_id):
    """Récupérer les statistiques d'un employé"""
    from app.models.employee import Employee, Attendance
    
    employee = Employee.query.get(employee_id)
    if not employee:
        return None
    
    today = date.today()
    month_start = today.replace(day=1)
    
    # Statistiques du mois
    attendances = Attendance.query.filter(
        Attendance.employee_id == employee_id,
        Attendance.date >= month_start
    ).all()
    
    total_hours = sum(a.hours_worked or 0 for a in attendances)
    total_days = len(attendances)
    
    return {
        'employee': employee,
        'total_hours_month': total_hours,
        'total_days_month': total_days,
        'average_hours': total_hours / total_days if total_days > 0 else 0
    }

def get_financial_stats(start_date=None, end_date=None):
    """Récupérer les statistiques financières"""
    from app.models.finance import Invoice, Payment
    
    if not start_date:
        start_date = date.today().replace(day=1)
    if not end_date:
        end_date = date.today()
    
    # Factures
    invoices = Invoice.query.filter(
        Invoice.date >= start_date,
        Invoice.date <= end_date
    ).all()
    
    total_invoiced = sum(i.total_amount or 0 for i in invoices)
    total_paid = sum(i.paid_amount or 0 for i in invoices)
    total_pending = total_invoiced - total_paid
    
    return {
        'total_invoiced': total_invoiced,
        'total_paid': total_paid,
        'total_pending': total_pending,
        'invoice_count': len(invoices),
        'payment_rate': (total_paid / total_invoiced * 100) if total_invoiced > 0 else 0
    }

def get_project_stats():
    """Récupérer les statistiques des projets"""
    from app.models.project import Project
    
    stats = {
        'total': Project.query.count(),
        'active': Project.query.filter_by(status='En cours').count(),
        'completed': Project.query.filter_by(status='Terminé').count(),
        'pending': Project.query.filter_by(status='En attente').count(),
        'cancelled': Project.query.filter_by(status='Annulé').count()
    }
    
    return stats