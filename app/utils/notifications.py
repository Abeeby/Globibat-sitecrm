"""
Système de notifications et rappels automatiques
"""

from app import db
from app.models import (Notification, Employee, Leave, Expense, Payroll, 
                       Document, WorkTimeRegulation, AuditLog)
from datetime import datetime, date, timedelta
from sqlalchemy import and_, or_
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import current_app

class NotificationService:
    """Service de gestion des notifications"""
    
    def __init__(self):
        self.smtp_server = current_app.config.get('SMTP_SERVER')
        self.smtp_port = current_app.config.get('SMTP_PORT', 587)
        self.smtp_user = current_app.config.get('SMTP_USER')
        self.smtp_password = current_app.config.get('SMTP_PASSWORD')
        self.from_email = current_app.config.get('FROM_EMAIL', 'noreply@globibat.ch')
    
    def send_notification(self, user_id, title, message, type='info', category=None, 
                         priority='normal', link_url=None, send_email=True):
        """Créer et envoyer une notification"""
        try:
            # Créer la notification en base
            notification = Notification(
                user_id=user_id,
                title=title,
                message=message,
                type=type,
                category=category,
                priority=priority,
                link_url=link_url
            )
            db.session.add(notification)
            db.session.commit()
            
            # Envoyer par email si demandé et si priorité haute
            if send_email and priority in ['high', 'urgent']:
                user = User.query.get(user_id)
                if user and user.email:
                    self.send_email_notification(user.email, title, message, link_url)
            
            return True
            
        except Exception as e:
            current_app.logger.error(f"Erreur envoi notification: {e}")
            return False
    
    def send_email_notification(self, to_email, subject, body, link_url=None):
        """Envoyer une notification par email"""
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"[Globibat] {subject}"
            msg['From'] = self.from_email
            msg['To'] = to_email
            
            # Corps du message
            text = body
            html = f"""
            <html>
            <body>
                <h2>{subject}</h2>
                <p>{body}</p>
                {f'<p><a href="{link_url}">Voir plus de détails</a></p>' if link_url else ''}
                <hr>
                <p><small>Ceci est un message automatique de Globibat CRM.</small></p>
            </body>
            </html>
            """
            
            part1 = MIMEText(text, 'plain')
            part2 = MIMEText(html, 'html')
            
            msg.attach(part1)
            msg.attach(part2)
            
            # Envoyer l'email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            
            return True
            
        except Exception as e:
            current_app.logger.error(f"Erreur envoi email: {e}")
            return False
    
    def check_and_send_reminders(self):
        """Vérifier et envoyer les rappels automatiques"""
        today = date.today()
        
        # 1. Rappels de documents expirés
        self.check_expired_documents()
        
        # 2. Rappels de congés à approuver
        self.check_pending_leaves()
        
        # 3. Rappels de dépenses à approuver
        self.check_pending_expenses()
        
        # 4. Rappels de violations de temps de travail
        self.check_work_time_violations()
        
        # 5. Rappels de fin de contrat
        self.check_contract_endings()
        
        # 6. Rappels de paie
        self.check_payroll_reminders()
        
        # 7. Rappels de formation
        self.check_training_reminders()
    
    def check_expired_documents(self):
        """Vérifier les documents expirés ou sur le point d'expirer"""
        today = date.today()
        warning_date = today + timedelta(days=30)
        
        # Documents expirés
        expired_docs = Document.query.filter(
            and_(
                Document.expiry_date <= today,
                Document.is_expired_notified == False
            )
        ).all()
        
        for doc in expired_docs:
            # Notification à l'employé
            if doc.employee.user:
                self.send_notification(
                    user_id=doc.employee.user_id,
                    title=f"Document expiré: {doc.document_type}",
                    message=f"Votre {doc.document_type} a expiré le {doc.expiry_date.strftime('%d/%m/%Y')}. Veuillez le renouveler.",
                    type='error',
                    category='document',
                    priority='high'
                )
            
            # Notification aux RH
            hr_users = User.query.filter_by(role='hr').all()
            for hr in hr_users:
                self.send_notification(
                    user_id=hr.id,
                    title=f"Document expiré - {doc.employee.full_name}",
                    message=f"Le {doc.document_type} de {doc.employee.full_name} a expiré.",
                    type='warning',
                    category='document',
                    priority='normal'
                )
            
            doc.is_expired_notified = True
        
        # Documents qui vont expirer
        expiring_docs = Document.query.filter(
            and_(
                Document.expiry_date > today,
                Document.expiry_date <= warning_date,
                Document.is_expiring_notified == False
            )
        ).all()
        
        for doc in expiring_docs:
            days_left = (doc.expiry_date - today).days
            
            if doc.employee.user:
                self.send_notification(
                    user_id=doc.employee.user_id,
                    title=f"Document bientôt expiré: {doc.document_type}",
                    message=f"Votre {doc.document_type} expire dans {days_left} jours ({doc.expiry_date.strftime('%d/%m/%Y')}).",
                    type='warning',
                    category='document',
                    priority='normal'
                )
            
            doc.is_expiring_notified = True
        
        db.session.commit()
    
    def check_pending_leaves(self):
        """Vérifier les congés en attente depuis plus de 2 jours"""
        two_days_ago = datetime.utcnow() - timedelta(days=2)
        
        pending_leaves = Leave.query.filter(
            and_(
                Leave.status == 'pending',
                Leave.requested_at < two_days_ago
            )
        ).all()
        
        for leave in pending_leaves:
            # Rappel au manager
            if leave.employee.department:
                managers = User.query.filter(
                    and_(
                        User.role == 'manager',
                        User.department == leave.employee.department
                    )
                ).all()
                
                for manager in managers:
                    self.send_notification(
                        user_id=manager.id,
                        title="Rappel: Demande de congé en attente",
                        message=f"{leave.employee.full_name} attend une réponse pour sa demande de congé du {leave.start_date.strftime('%d/%m/%Y')} au {leave.end_date.strftime('%d/%m/%Y')}",
                        type='warning',
                        category='leave',
                        priority='high',
                        link_url=f"/leaves/approve/{leave.id}"
                    )
    
    def check_pending_expenses(self):
        """Vérifier les dépenses en attente"""
        # Dépenses en attente depuis plus de 3 jours
        three_days_ago = datetime.utcnow() - timedelta(days=3)
        
        pending_expenses = Expense.query.filter(
            and_(
                Expense.payment_status.in_(['pending', 'finance_review']),
                Expense.submitted_at < three_days_ago
            )
        ).all()
        
        for expense in pending_expenses:
            # Déterminer qui doit approuver
            if expense.payment_status == 'pending':
                # Manager doit approuver
                approvers = User.query.filter(
                    and_(
                        User.role == 'manager',
                        User.department == expense.employee.department
                    )
                ).all()
            else:
                # Finance doit approuver
                approvers = User.query.filter_by(role='finance').all()
            
            for approver in approvers:
                self.send_notification(
                    user_id=approver.id,
                    title="Rappel: Dépense en attente d'approbation",
                    message=f"Dépense de {expense.total_amount} CHF soumise par {expense.employee.full_name} attend votre approbation.",
                    type='warning',
                    category='expense',
                    priority='high',
                    link_url=f"/expenses/approve/{expense.id}"
                )
    
    def check_work_time_violations(self):
        """Vérifier les violations du temps de travail"""
        today = date.today()
        yesterday = today - timedelta(days=1)
        
        # Heures excessives hier
        violations = db.session.query(Attendance).filter(
            and_(
                Attendance.date == yesterday,
                Attendance.total_hours > 10
            )
        ).all()
        
        if violations:
            # Notification aux RH
            hr_users = User.query.filter_by(role='hr').all()
            
            for hr in hr_users:
                message = f"{len(violations)} employé(s) ont dépassé 10h de travail hier:\n"
                for v in violations[:5]:  # Limiter à 5
                    message += f"- {v.employee.full_name}: {v.total_hours}h\n"
                
                self.send_notification(
                    user_id=hr.id,
                    title="Alerte: Dépassement des heures légales",
                    message=message,
                    type='error',
                    category='compliance',
                    priority='high',
                    link_url="/compliance/violations"
                )
        
        # Vérifier les heures hebdomadaires
        week_start = today - timedelta(days=today.weekday())
        
        weekly_violations = db.session.query(
            Employee,
            func.sum(Attendance.total_hours).label('weekly_hours')
        ).join(
            Attendance, Employee.id == Attendance.employee_id
        ).filter(
            and_(
                Attendance.date >= week_start,
                Attendance.date <= today
            )
        ).group_by(Employee.id).having(
            func.sum(Attendance.total_hours) > 45  # Alerte à 45h
        ).all()
        
        for emp, hours in weekly_violations:
            if emp.user:
                self.send_notification(
                    user_id=emp.user_id,
                    title="Attention: Approche de la limite hebdomadaire",
                    message=f"Vous avez travaillé {hours:.1f}h cette semaine. Limite légale: 50h.",
                    type='warning',
                    category='compliance',
                    priority='normal'
                )
    
    def check_contract_endings(self):
        """Vérifier les fins de contrat approchantes"""
        today = date.today()
        warning_date = today + timedelta(days=60)  # 2 mois avant
        
        ending_contracts = Employee.query.filter(
            and_(
                Employee.end_date != None,
                Employee.end_date > today,
                Employee.end_date <= warning_date,
                Employee.is_active == True
            )
        ).all()
        
        for emp in ending_contracts:
            days_left = (emp.end_date - today).days
            
            # Notification à l'employé
            if emp.user:
                self.send_notification(
                    user_id=emp.user_id,
                    title="Fin de contrat approchante",
                    message=f"Votre contrat se termine dans {days_left} jours ({emp.end_date.strftime('%d/%m/%Y')}).",
                    type='info',
                    category='contract',
                    priority='normal'
                )
            
            # Notification aux RH
            if days_left <= 30:  # Urgence à 1 mois
                hr_users = User.query.filter_by(role='hr').all()
                for hr in hr_users:
                    self.send_notification(
                        user_id=hr.id,
                        title=f"Fin de contrat - {emp.full_name}",
                        message=f"Le contrat de {emp.full_name} se termine dans {days_left} jours. Action requise.",
                        type='warning',
                        category='contract',
                        priority='high'
                    )
    
    def check_payroll_reminders(self):
        """Rappels pour le calcul de la paie"""
        today = date.today()
        
        # Si on est le 25 du mois, rappeler de calculer la paie
        if today.day == 25:
            finance_users = User.query.filter_by(role='finance').all()
            
            for user in finance_users:
                self.send_notification(
                    user_id=user.id,
                    title="Rappel: Calcul de la paie mensuelle",
                    message=f"N'oubliez pas de lancer le calcul de la paie pour le mois de {calendar.month_name[today.month]}.",
                    type='info',
                    category='payroll',
                    priority='high',
                    link_url="/payroll/calculate"
                )
        
        # Vérifier les paies non validées
        if today.day == 28:
            unvalidated = Payroll.query.filter(
                and_(
                    Payroll.month == today.month,
                    Payroll.year == today.year,
                    Payroll.status == 'draft'
                )
            ).count()
            
            if unvalidated > 0:
                finance_users = User.query.filter_by(role='finance').all()
                
                for user in finance_users:
                    self.send_notification(
                        user_id=user.id,
                        title="Urgent: Fiches de paie à valider",
                        message=f"{unvalidated} fiches de paie sont en attente de validation pour ce mois.",
                        type='error',
                        category='payroll',
                        priority='urgent',
                        link_url="/payroll/validation"
                    )
    
    def check_training_reminders(self):
        """Rappels de formations obligatoires"""
        # À implémenter selon les besoins spécifiques
        pass
    
    def mark_notifications_as_read(self, user_id, notification_ids=None):
        """Marquer des notifications comme lues"""
        query = Notification.query.filter_by(user_id=user_id, is_read=False)
        
        if notification_ids:
            query = query.filter(Notification.id.in_(notification_ids))
        
        query.update({'is_read': True, 'read_at': datetime.utcnow()})
        db.session.commit()
    
    def get_user_notifications(self, user_id, unread_only=False, limit=50):
        """Récupérer les notifications d'un utilisateur"""
        query = Notification.query.filter_by(user_id=user_id)
        
        if unread_only:
            query = query.filter_by(is_read=False)
        
        return query.order_by(Notification.created_at.desc()).limit(limit).all()
    
    def cleanup_old_notifications(self, days=90):
        """Nettoyer les anciennes notifications"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        old_notifications = Notification.query.filter(
            and_(
                Notification.created_at < cutoff_date,
                Notification.is_read == True
            )
        ).delete()
        
        db.session.commit()
        
        return old_notifications


# Instance globale du service
notification_service = NotificationService()