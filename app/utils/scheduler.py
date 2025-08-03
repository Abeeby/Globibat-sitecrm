"""
Planificateur de tâches automatiques
"""

from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, date
import logging

logger = logging.getLogger(__name__)

def start_scheduler(app):
    """Démarrer le planificateur de tâches"""
    scheduler = BackgroundScheduler()
    
    # Tâche 1: Vérifier la conformité quotidienne (tous les jours à 22h)
    @scheduler.scheduled_job('cron', hour=22)
    def daily_compliance_check():
        with app.app_context():
            try:
                from app.utils.compliance import compliance_checker
                from app.models import CompanyDashboard
                
                result = compliance_checker.check_daily_compliance()
                
                # Mettre à jour le dashboard
                dashboard = CompanyDashboard.query.filter_by(date=date.today()).first()
                if dashboard:
                    dashboard.compliance_alerts = result['violations'] + result['warnings']
                    db.session.commit()
                
                logger.info(f"Vérification de conformité effectuée: {len(result['violations'])} violations")
                
            except Exception as e:
                logger.error(f"Erreur vérification conformité: {e}")
    
    # Tâche 2: Envoyer les rappels (tous les jours à 9h et 16h)
    @scheduler.scheduled_job('cron', hour='9,16')
    def send_daily_reminders():
        with app.app_context():
            try:
                from app.utils.notifications import notification_service
                notification_service.check_and_send_reminders()
                logger.info("Rappels automatiques envoyés")
                
            except Exception as e:
                logger.error(f"Erreur envoi rappels: {e}")
    
    # Tâche 3: Calculer les statistiques (tous les jours à 2h du matin)
    @scheduler.scheduled_job('cron', hour=2)
    def calculate_statistics():
        with app.app_context():
            try:
                from app.models import Employee, EmployeeStatistics, Attendance, Expense
                from sqlalchemy import func
                
                # Calculer les stats de la veille
                yesterday = date.today() - timedelta(days=1)
                
                # Pour chaque employé actif
                employees = Employee.query.filter_by(is_active=True).all()
                
                for emp in employees:
                    # Vérifier si les stats existent déjà
                    existing = EmployeeStatistics.query.filter_by(
                        employee_id=emp.id,
                        period_type='daily',
                        period_start=yesterday
                    ).first()
                    
                    if not existing:
                        # Calculer les heures
                        attendance = Attendance.query.filter_by(
                            employee_id=emp.id,
                            date=yesterday
                        ).first()
                        
                        # Calculer les dépenses
                        expenses = db.session.query(
                            func.sum(Expense.total_amount)
                        ).filter(
                            Expense.employee_id == emp.id,
                            Expense.expense_date == yesterday
                        ).scalar() or 0
                        
                        # Créer les stats
                        stats = EmployeeStatistics(
                            employee_id=emp.id,
                            period_type='daily',
                            period_start=yesterday,
                            period_end=yesterday,
                            total_hours=attendance.total_hours if attendance else 0,
                            regular_hours=(attendance.total_hours - attendance.overtime_hours) if attendance else 0,
                            overtime_hours=attendance.overtime_hours if attendance else 0,
                            days_present=1 if attendance else 0,
                            days_absent=0 if attendance else 1,
                            late_arrivals=1 if attendance and (attendance.is_late_morning or attendance.is_late_afternoon) else 0,
                            total_expenses=expenses
                        )
                        
                        db.session.add(stats)
                
                db.session.commit()
                logger.info("Statistiques quotidiennes calculées")
                
            except Exception as e:
                logger.error(f"Erreur calcul statistiques: {e}")
    
    # Tâche 4: Nettoyer les anciennes notifications (tous les dimanches à 3h)
    @scheduler.scheduled_job('cron', day_of_week=6, hour=3)
    def cleanup_old_data():
        with app.app_context():
            try:
                from app.utils.notifications import notification_service
                
                # Nettoyer les notifications de plus de 90 jours
                deleted = notification_service.cleanup_old_notifications(90)
                logger.info(f"Nettoyage: {deleted} notifications supprimées")
                
                # Nettoyer les logs d'audit de plus de 1 an
                from app.models import AuditLog
                one_year_ago = datetime.utcnow() - timedelta(days=365)
                
                old_logs = AuditLog.query.filter(
                    AuditLog.timestamp < one_year_ago
                ).delete()
                
                db.session.commit()
                logger.info(f"Nettoyage: {old_logs} logs d'audit supprimés")
                
            except Exception as e:
                logger.error(f"Erreur nettoyage: {e}")
    
    # Tâche 5: Vérifier les documents expirés (tous les jours à 8h)
    @scheduler.scheduled_job('cron', hour=8)
    def check_expiring_documents():
        with app.app_context():
            try:
                from app.utils.notifications import notification_service
                notification_service.check_expired_documents()
                logger.info("Vérification des documents expirés effectuée")
                
            except Exception as e:
                logger.error(f"Erreur vérification documents: {e}")
    
    # Tâche 6: Générer le rapport hebdomadaire (tous les lundis à 7h)
    @scheduler.scheduled_job('cron', day_of_week=0, hour=7)
    def generate_weekly_report():
        with app.app_context():
            try:
                from app.utils.reports import generate_weekly_management_report
                
                # Générer le rapport de la semaine précédente
                report_path = generate_weekly_management_report()
                
                # Envoyer aux managers et RH
                from app.models import User
                from app.utils.notifications import notification_service
                
                recipients = User.query.filter(
                    User.role.in_(['admin', 'hr', 'manager'])
                ).all()
                
                for user in recipients:
                    notification_service.send_notification(
                        user_id=user.id,
                        title="Rapport hebdomadaire disponible",
                        message="Le rapport de gestion hebdomadaire est prêt.",
                        type='info',
                        category='report',
                        link_url=f"/reports/download/{report_path}"
                    )
                
                logger.info("Rapport hebdomadaire généré et distribué")
                
            except Exception as e:
                logger.error(f"Erreur génération rapport: {e}")
    
    # Tâche 7: Mise à jour du dashboard (toutes les 5 minutes)
    @scheduler.scheduled_job('interval', minutes=5)
    def update_dashboard():
        with app.app_context():
            try:
                from app.views.dashboard import calculate_daily_labor_cost
                from app.models import CompanyDashboard, Employee, Attendance, Expense, Leave, Project
                
                today = date.today()
                dashboard = CompanyDashboard.query.filter_by(date=today).first()
                
                if not dashboard:
                    dashboard = CompanyDashboard(date=today)
                    db.session.add(dashboard)
                
                # Mettre à jour les métriques
                dashboard.total_employees = Employee.query.filter_by(is_active=True).count()
                
                present_query = Attendance.query.filter(
                    Attendance.date == today,
                    Attendance.check_in_morning != None
                )
                dashboard.present_today = present_query.count()
                
                dashboard.total_hours_today = db.session.query(
                    func.sum(Attendance.total_hours)
                ).filter(Attendance.date == today).scalar() or 0
                
                dashboard.overtime_hours_today = db.session.query(
                    func.sum(Attendance.overtime_hours)
                ).filter(Attendance.date == today).scalar() or 0
                
                dashboard.labor_cost_today = calculate_daily_labor_cost(today)
                
                dashboard.expense_cost_today = db.session.query(
                    func.sum(Expense.total_amount)
                ).filter(
                    Expense.expense_date == today,
                    Expense.payment_status == 'approved'
                ).scalar() or 0
                
                dashboard.active_projects = Project.query.filter_by(status='active').count()
                
                pending_expenses = Expense.query.filter_by(payment_status='pending').count()
                pending_leaves = Leave.query.filter_by(status='pending').count()
                dashboard.pending_approvals = pending_expenses + pending_leaves
                
                dashboard.last_updated = datetime.utcnow()
                
                db.session.commit()
                
            except Exception as e:
                logger.error(f"Erreur mise à jour dashboard: {e}")
    
    # Démarrer le planificateur
    scheduler.start()
    logger.info("Planificateur de tâches démarré")
    
    # S'assurer que le planificateur s'arrête proprement
    import atexit
    atexit.register(lambda: scheduler.shutdown())
    
    return scheduler