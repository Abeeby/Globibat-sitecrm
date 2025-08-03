"""
Système de conformité et audit pour les règles suisses du travail
"""

from app import db
from app.models import (Employee, Attendance, Leave, Payroll, WorkTimeRegulation,
                       AuditLog, CompanyDashboard, Notification)
from datetime import datetime, date, timedelta
from sqlalchemy import and_, or_, func
import calendar
from decimal import Decimal

class ComplianceChecker:
    """Vérificateur de conformité aux règles suisses"""
    
    # Règles légales suisses (Loi sur le travail - LTr)
    SWISS_LABOR_LAWS = {
        'max_daily_hours': 10,           # Maximum 10h par jour (art. 9 LTr)
        'max_weekly_hours': 50,          # Maximum 50h par semaine (45h pour bureaux)
        'max_overtime_annual': 170,      # Maximum 170h supplémentaires par an
        'min_daily_rest': 11,            # Minimum 11h de repos entre deux jours
        'min_weekly_rest': 35,           # Minimum 35h consécutives par semaine
        'break_after_hours': 5.5,        # Pause obligatoire après 5h30
        'min_break_duration': 30,        # Minimum 30 min de pause
        'night_work_hours': (23, 6),     # Travail de nuit: 23h-6h
        'sunday_work_allowed': False,    # Travail du dimanche interdit sauf exceptions
        'vacation_min_days': 20,         # Minimum 20 jours de vacances (25 pour <20 ans)
        'maternity_leave_weeks': 14,    # 14 semaines de congé maternité
        'paternity_leave_days': 10,      # 10 jours de congé paternité (depuis 2021)
    }
    
    def __init__(self):
        self.violations = []
        self.warnings = []
        self.audit_entries = []
    
    def check_daily_compliance(self, date_to_check=None):
        """Vérifier la conformité journalière"""
        if not date_to_check:
            date_to_check = date.today()
        
        self.violations = []
        self.warnings = []
        
        # Vérifier les heures maximales journalières
        overtime_attendances = Attendance.query.filter(
            and_(
                Attendance.date == date_to_check,
                Attendance.total_hours > self.SWISS_LABOR_LAWS['max_daily_hours']
            )
        ).all()
        
        for att in overtime_attendances:
            self.violations.append({
                'type': 'daily_overtime',
                'employee_id': att.employee_id,
                'employee_name': att.employee.full_name,
                'date': att.date,
                'hours': att.total_hours,
                'limit': self.SWISS_LABOR_LAWS['max_daily_hours'],
                'severity': 'high',
                'message': f"{att.employee.full_name} a travaillé {att.total_hours}h le {att.date.strftime('%d/%m/%Y')} (max: {self.SWISS_LABOR_LAWS['max_daily_hours']}h)"
            })
        
        # Vérifier les pauses obligatoires
        long_shifts = Attendance.query.filter(
            and_(
                Attendance.date == date_to_check,
                Attendance.total_hours > self.SWISS_LABOR_LAWS['break_after_hours']
            )
        ).all()
        
        for att in long_shifts:
            if att.check_out_lunch and att.check_in_afternoon:
                break_duration = (att.check_in_afternoon - att.check_out_lunch).total_seconds() / 60
                if break_duration < self.SWISS_LABOR_LAWS['min_break_duration']:
                    self.warnings.append({
                        'type': 'insufficient_break',
                        'employee_id': att.employee_id,
                        'employee_name': att.employee.full_name,
                        'date': att.date,
                        'break_duration': break_duration,
                        'required': self.SWISS_LABOR_LAWS['min_break_duration'],
                        'severity': 'medium',
                        'message': f"{att.employee.full_name} n'a pris que {break_duration:.0f} min de pause (min: {self.SWISS_LABOR_LAWS['min_break_duration']} min)"
                    })
        
        # Vérifier le travail de nuit
        night_start, night_end = self.SWISS_LABOR_LAWS['night_work_hours']
        night_work = Attendance.query.filter(
            and_(
                Attendance.date == date_to_check,
                or_(
                    func.extract('hour', Attendance.check_in_morning) < night_end,
                    func.extract('hour', Attendance.check_out_evening) >= night_start
                )
            )
        ).all()
        
        for att in night_work:
            self.warnings.append({
                'type': 'night_work',
                'employee_id': att.employee_id,
                'employee_name': att.employee.full_name,
                'date': att.date,
                'severity': 'low',
                'message': f"{att.employee.full_name} a effectué du travail de nuit le {att.date.strftime('%d/%m/%Y')}"
            })
        
        # Vérifier le repos minimum entre deux jours
        self._check_daily_rest(date_to_check)
        
        return {
            'violations': self.violations,
            'warnings': self.warnings,
            'compliant': len(self.violations) == 0
        }
    
    def check_weekly_compliance(self, week_start=None):
        """Vérifier la conformité hebdomadaire"""
        if not week_start:
            today = date.today()
            week_start = today - timedelta(days=today.weekday())
        
        week_end = week_start + timedelta(days=6)
        
        # Heures hebdomadaires
        weekly_hours = db.session.query(
            Employee,
            func.sum(Attendance.total_hours).label('weekly_hours')
        ).join(
            Attendance, Employee.id == Attendance.employee_id
        ).filter(
            and_(
                Attendance.date >= week_start,
                Attendance.date <= week_end
            )
        ).group_by(Employee.id).all()
        
        for emp, hours in weekly_hours:
            if hours and hours > self.SWISS_LABOR_LAWS['max_weekly_hours']:
                self.violations.append({
                    'type': 'weekly_overtime',
                    'employee_id': emp.id,
                    'employee_name': emp.full_name,
                    'week': week_start.strftime('%d/%m/%Y'),
                    'hours': float(hours),
                    'limit': self.SWISS_LABOR_LAWS['max_weekly_hours'],
                    'severity': 'high',
                    'message': f"{emp.full_name} a travaillé {hours:.1f}h cette semaine (max: {self.SWISS_LABOR_LAWS['max_weekly_hours']}h)"
                })
        
        # Vérifier le repos hebdomadaire
        self._check_weekly_rest(week_start, week_end)
        
        # Travail du dimanche
        sunday_work = Attendance.query.filter(
            and_(
                Attendance.date >= week_start,
                Attendance.date <= week_end,
                func.extract('dow', Attendance.date) == 0  # Dimanche
            )
        ).all()
        
        if sunday_work and not self.SWISS_LABOR_LAWS['sunday_work_allowed']:
            for att in sunday_work:
                self.warnings.append({
                    'type': 'sunday_work',
                    'employee_id': att.employee_id,
                    'employee_name': att.employee.full_name,
                    'date': att.date,
                    'severity': 'medium',
                    'message': f"{att.employee.full_name} a travaillé le dimanche {att.date.strftime('%d/%m/%Y')}"
                })
        
        return {
            'violations': self.violations,
            'warnings': self.warnings,
            'compliant': len(self.violations) == 0
        }
    
    def check_annual_compliance(self, year=None):
        """Vérifier la conformité annuelle"""
        if not year:
            year = date.today().year
        
        year_start = date(year, 1, 1)
        year_end = date(year, 12, 31)
        
        # Heures supplémentaires annuelles
        annual_overtime = db.session.query(
            Employee,
            func.sum(Attendance.overtime_hours).label('annual_overtime')
        ).join(
            Attendance, Employee.id == Attendance.employee_id
        ).filter(
            and_(
                Attendance.date >= year_start,
                Attendance.date <= year_end
            )
        ).group_by(Employee.id).all()
        
        for emp, overtime in annual_overtime:
            if overtime and overtime > self.SWISS_LABOR_LAWS['max_overtime_annual']:
                self.violations.append({
                    'type': 'annual_overtime',
                    'employee_id': emp.id,
                    'employee_name': emp.full_name,
                    'year': year,
                    'hours': float(overtime),
                    'limit': self.SWISS_LABOR_LAWS['max_overtime_annual'],
                    'severity': 'high',
                    'message': f"{emp.full_name} a accumulé {overtime:.1f}h supplémentaires en {year} (max: {self.SWISS_LABOR_LAWS['max_overtime_annual']}h)"
                })
        
        # Vérifier les congés minimums
        self._check_vacation_compliance(year)
        
        return {
            'violations': self.violations,
            'warnings': self.warnings,
            'compliant': len(self.violations) == 0
        }
    
    def check_payroll_compliance(self, payroll):
        """Vérifier la conformité d'une fiche de paie"""
        violations = []
        
        # Vérifier le salaire minimum (selon CCT du secteur)
        # Note: Le salaire minimum varie selon le canton et le secteur
        MIN_HOURLY_RATE = Decimal('23.00')  # Exemple pour Genève
        
        if payroll.employee.hourly_rate and payroll.employee.hourly_rate < MIN_HOURLY_RATE:
            violations.append({
                'type': 'minimum_wage',
                'message': f"Taux horaire inférieur au minimum légal ({payroll.employee.hourly_rate} < {MIN_HOURLY_RATE} CHF)",
                'severity': 'high'
            })
        
        # Vérifier les déductions sociales
        expected_social_rate = Decimal('0.0525')  # AVS/AI/APG
        actual_social_rate = payroll.social_security / payroll.gross_salary if payroll.gross_salary > 0 else 0
        
        if abs(actual_social_rate - expected_social_rate) > Decimal('0.001'):
            violations.append({
                'type': 'social_deduction',
                'message': f"Taux de cotisation AVS/AI/APG incorrect ({actual_social_rate:.4f} au lieu de {expected_social_rate:.4f})",
                'severity': 'medium'
            })
        
        # Vérifier le paiement des heures supplémentaires
        if payroll.overtime_hours > 0 and payroll.overtime_amount == 0:
            violations.append({
                'type': 'unpaid_overtime',
                'message': f"{payroll.overtime_hours:.1f}h supplémentaires non payées",
                'severity': 'high'
            })
        
        return violations
    
    def generate_compliance_report(self, start_date, end_date):
        """Générer un rapport de conformité complet"""
        report = {
            'period': {
                'start': start_date.strftime('%d/%m/%Y'),
                'end': end_date.strftime('%d/%m/%Y')
            },
            'summary': {
                'total_violations': 0,
                'total_warnings': 0,
                'compliance_rate': 0
            },
            'violations_by_type': {},
            'employees_at_risk': [],
            'recommendations': []
        }
        
        # Analyser toutes les violations sur la période
        current = start_date
        all_violations = []
        all_warnings = []
        
        while current <= end_date:
            daily_check = self.check_daily_compliance(current)
            all_violations.extend(daily_check['violations'])
            all_warnings.extend(daily_check['warnings'])
            current += timedelta(days=1)
        
        # Résumer par type
        for violation in all_violations:
            vtype = violation['type']
            if vtype not in report['violations_by_type']:
                report['violations_by_type'][vtype] = {
                    'count': 0,
                    'employees': set()
                }
            report['violations_by_type'][vtype]['count'] += 1
            report['violations_by_type'][vtype]['employees'].add(violation['employee_id'])
        
        # Convertir les sets en listes pour la sérialisation
        for vtype in report['violations_by_type']:
            report['violations_by_type'][vtype]['employees'] = list(
                report['violations_by_type'][vtype]['employees']
            )
        
        # Identifier les employés à risque
        employee_violations = {}
        for violation in all_violations:
            emp_id = violation['employee_id']
            if emp_id not in employee_violations:
                employee_violations[emp_id] = 0
            employee_violations[emp_id] += 1
        
        # Top 5 des employés avec le plus de violations
        sorted_employees = sorted(employee_violations.items(), key=lambda x: x[1], reverse=True)[:5]
        
        for emp_id, count in sorted_employees:
            employee = Employee.query.get(emp_id)
            if employee:
                report['employees_at_risk'].append({
                    'employee_id': emp_id,
                    'name': employee.full_name,
                    'violations': count
                })
        
        # Calculer le taux de conformité
        total_days = (end_date - start_date).days + 1
        total_employees = Employee.query.filter_by(is_active=True).count()
        potential_violations = total_days * total_employees
        
        report['summary']['total_violations'] = len(all_violations)
        report['summary']['total_warnings'] = len(all_warnings)
        report['summary']['compliance_rate'] = round(
            (1 - len(all_violations) / potential_violations) * 100 if potential_violations > 0 else 100,
            2
        )
        
        # Générer des recommandations
        report['recommendations'] = self._generate_recommendations(report)
        
        return report
    
    def audit_action(self, user, action, model, model_id, description, old_values=None, new_values=None):
        """Enregistrer une action dans le journal d'audit"""
        try:
            # Déterminer la catégorie et la sévérité
            category = self._determine_audit_category(model)
            severity = self._determine_audit_severity(action)
            
            # Créer l'entrée d'audit
            audit = AuditLog(
                user_id=user.id if user else None,
                action=action,
                model=model,
                model_id=model_id,
                description=description,
                old_values=old_values,
                new_values=new_values,
                category=category,
                severity=severity,
                user_ip=self._get_user_ip(),
                user_agent=self._get_user_agent()
            )
            
            db.session.add(audit)
            db.session.commit()
            
            # Pour les actions critiques, envoyer une notification
            if severity == 'critical':
                self._notify_critical_action(audit)
            
            return True
            
        except Exception as e:
            current_app.logger.error(f"Erreur audit: {e}")
            return False
    
    def _check_daily_rest(self, check_date):
        """Vérifier le repos minimum entre deux jours de travail"""
        next_day = check_date + timedelta(days=1)
        
        # Trouver les employés qui ont travaillé deux jours consécutifs
        today_attendance = Attendance.query.filter_by(date=check_date).all()
        
        for att in today_attendance:
            if att.check_out_evening:
                # Vérifier s'il y a un pointage le lendemain
                next_attendance = Attendance.query.filter_by(
                    employee_id=att.employee_id,
                    date=next_day
                ).first()
                
                if next_attendance and next_attendance.check_in_morning:
                    # Calculer le temps de repos
                    rest_hours = (next_attendance.check_in_morning - att.check_out_evening).total_seconds() / 3600
                    
                    if rest_hours < self.SWISS_LABOR_LAWS['min_daily_rest']:
                        self.violations.append({
                            'type': 'insufficient_daily_rest',
                            'employee_id': att.employee_id,
                            'employee_name': att.employee.full_name,
                            'date': check_date,
                            'rest_hours': rest_hours,
                            'required': self.SWISS_LABOR_LAWS['min_daily_rest'],
                            'severity': 'high',
                            'message': f"{att.employee.full_name} n'a eu que {rest_hours:.1f}h de repos entre deux jours (min: {self.SWISS_LABOR_LAWS['min_daily_rest']}h)"
                        })
    
    def _check_weekly_rest(self, week_start, week_end):
        """Vérifier le repos hebdomadaire minimum"""
        # Pour chaque employé, vérifier s'il a eu 35h consécutives de repos
        employees = Employee.query.filter_by(is_active=True).all()
        
        for emp in employees:
            attendances = Attendance.query.filter(
                and_(
                    Attendance.employee_id == emp.id,
                    Attendance.date >= week_start,
                    Attendance.date <= week_end
                )
            ).order_by(Attendance.date).all()
            
            if len(attendances) >= 6:  # Travaillé au moins 6 jours
                self.warnings.append({
                    'type': 'insufficient_weekly_rest',
                    'employee_id': emp.id,
                    'employee_name': emp.full_name,
                    'week': week_start.strftime('%d/%m/%Y'),
                    'severity': 'medium',
                    'message': f"{emp.full_name} pourrait ne pas avoir eu 35h de repos consécutives cette semaine"
                })
    
    def _check_vacation_compliance(self, year):
        """Vérifier le respect des congés minimums"""
        employees = Employee.query.filter_by(is_active=True).all()
        
        for emp in employees:
            # Calculer l'âge de l'employé
            if emp.birth_date:
                age = year - emp.birth_date.year
                min_vacation = 25 if age < 20 else self.SWISS_LABOR_LAWS['vacation_min_days']
            else:
                min_vacation = self.SWISS_LABOR_LAWS['vacation_min_days']
            
            # Vérifier les jours de vacances
            if emp.vacation_days < min_vacation:
                self.warnings.append({
                    'type': 'insufficient_vacation',
                    'employee_id': emp.id,
                    'employee_name': emp.full_name,
                    'year': year,
                    'allocated': emp.vacation_days,
                    'required': min_vacation,
                    'severity': 'medium',
                    'message': f"{emp.full_name} n'a que {emp.vacation_days} jours de congés alloués (min: {min_vacation})"
                })
    
    def _generate_recommendations(self, report):
        """Générer des recommandations basées sur le rapport"""
        recommendations = []
        
        if report['summary']['total_violations'] > 0:
            recommendations.append({
                'priority': 'high',
                'category': 'general',
                'recommendation': "Mettre en place des alertes automatiques pour prévenir les dépassements d'heures"
            })
        
        if 'daily_overtime' in report['violations_by_type']:
            recommendations.append({
                'priority': 'high',
                'category': 'hours',
                'recommendation': "Revoir la planification des équipes pour éviter les journées de plus de 10h"
            })
        
        if 'insufficient_break' in report['violations_by_type']:
            recommendations.append({
                'priority': 'medium',
                'category': 'breaks',
                'recommendation': "Sensibiliser les employés sur l'importance des pauses obligatoires"
            })
        
        if report['summary']['compliance_rate'] < 95:
            recommendations.append({
                'priority': 'high',
                'category': 'compliance',
                'recommendation': "Organiser une formation sur la législation du travail suisse"
            })
        
        return recommendations
    
    def _determine_audit_category(self, model):
        """Déterminer la catégorie d'audit selon le modèle"""
        categories = {
            'Employee': 'hr',
            'Attendance': 'hr',
            'Leave': 'hr',
            'Payroll': 'finance',
            'Expense': 'finance',
            'User': 'security',
            'Invoice': 'finance',
            'Project': 'operations'
        }
        return categories.get(model, 'other')
    
    def _determine_audit_severity(self, action):
        """Déterminer la sévérité d'une action"""
        critical_actions = ['delete', 'approve_payroll', 'modify_salary', 'grant_admin']
        warning_actions = ['edit', 'approve', 'reject']
        
        if action in critical_actions:
            return 'critical'
        elif action in warning_actions:
            return 'warning'
        return 'info'
    
    def _get_user_ip(self):
        """Obtenir l'IP de l'utilisateur"""
        from flask import request
        return request.remote_addr if request else None
    
    def _get_user_agent(self):
        """Obtenir le user agent"""
        from flask import request
        return request.headers.get('User-Agent') if request else None
    
    def _notify_critical_action(self, audit):
        """Notifier les admins des actions critiques"""
        from app.utils.notifications import notification_service
        
        admins = User.query.filter_by(role='admin').all()
        for admin in admins:
            notification_service.send_notification(
                user_id=admin.id,
                title="Action critique détectée",
                message=f"{audit.user.full_name if audit.user else 'Système'} a effectué: {audit.description}",
                type='error',
                category='security',
                priority='urgent'
            )


# Instance globale
compliance_checker = ComplianceChecker()