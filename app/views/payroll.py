"""
Module de paie avec génération automatique de fiches de paie
"""

from flask import Blueprint, render_template, request, jsonify, send_file, current_app
from app import db
from app.models import (Employee, Payroll, Attendance, Leave, Expense, 
                       AuditLog, Notification)
from app.utils.pdf import generate_payslip_pdf
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from sqlalchemy import and_, or_, func, extract
from decimal import Decimal
import calendar

payroll_bp = Blueprint('payroll', __name__, url_prefix='/api/payroll')

@payroll_bp.route('/calculate', methods=['POST'])
def calculate_payroll():
    """Calculer la paie pour un ou plusieurs employés"""
    try:
        data = request.get_json()
        month = data.get('month', date.today().month)
        year = data.get('year', date.today().year)
        employee_ids = data.get('employee_ids', [])  # Liste vide = tous les employés
        
        # Si pas d'employés spécifiés, prendre tous les actifs
        if not employee_ids:
            employees = Employee.query.filter_by(is_active=True).all()
        else:
            employees = Employee.query.filter(
                and_(
                    Employee.id.in_(employee_ids),
                    Employee.is_active == True
                )
            ).all()
        
        # Dates de la période
        period_start = date(year, month, 1)
        period_end = date(year, month, calendar.monthrange(year, month)[1])
        
        results = []
        
        for employee in employees:
            # Vérifier si la paie existe déjà
            existing_payroll = Payroll.query.filter_by(
                employee_id=employee.id,
                month=month,
                year=year
            ).first()
            
            if existing_payroll and existing_payroll.status == 'paid':
                results.append({
                    'employee_id': employee.id,
                    'status': 'already_paid',
                    'message': f"Paie déjà versée pour {employee.full_name}"
                })
                continue
            
            # Calculer les heures travaillées
            attendance_data = db.session.query(
                func.sum(Attendance.total_hours).label('total_hours'),
                func.sum(Attendance.overtime_hours).label('overtime_hours')
            ).filter(
                and_(
                    Attendance.employee_id == employee.id,
                    Attendance.date >= period_start,
                    Attendance.date <= period_end
                )
            ).first()
            
            total_hours = attendance_data.total_hours or 0
            overtime_hours = attendance_data.overtime_hours or 0
            regular_hours = total_hours - overtime_hours
            
            # Calculer le salaire de base
            if employee.base_salary:
                # Salaire mensuel fixe
                base_amount = employee.base_salary
                overtime_rate = (employee.base_salary / 160) * Decimal('1.25')  # Base sur 160h/mois
                overtime_amount = overtime_rate * Decimal(str(overtime_hours))
            elif employee.hourly_rate:
                # Salaire horaire
                base_amount = employee.hourly_rate * Decimal(str(regular_hours))
                overtime_amount = employee.hourly_rate * Decimal('1.25') * Decimal(str(overtime_hours))
            else:
                results.append({
                    'employee_id': employee.id,
                    'status': 'error',
                    'message': f"Pas de salaire défini pour {employee.full_name}"
                })
                continue
            
            # Ajouter les bonus éventuels
            bonuses = Decimal('0')  # TODO: Implémenter la logique des bonus
            
            # Salaire brut
            gross_salary = base_amount + overtime_amount + bonuses
            
            # Créer ou mettre à jour la paie
            if existing_payroll:
                payroll = existing_payroll
            else:
                payroll = Payroll(
                    employee_id=employee.id,
                    month=month,
                    year=year,
                    period_start=period_start,
                    period_end=period_end
                )
                db.session.add(payroll)
            
            # Mettre à jour les valeurs
            payroll.regular_hours = float(regular_hours)
            payroll.overtime_hours = float(overtime_hours)
            payroll.base_amount = base_amount
            payroll.overtime_amount = overtime_amount
            payroll.bonuses = bonuses
            payroll.gross_salary = gross_salary
            
            # Calculer les déductions
            payroll.calculate_deductions()
            
            # Statut
            payroll.status = 'draft'
            
            db.session.commit()
            
            results.append({
                'employee_id': employee.id,
                'employee_name': employee.full_name,
                'status': 'calculated',
                'payroll_id': payroll.id,
                'gross_salary': float(payroll.gross_salary),
                'net_salary': float(payroll.net_salary),
                'hours': {
                    'regular': payroll.regular_hours,
                    'overtime': payroll.overtime_hours
                }
            })
        
        # Créer une notification pour les RH
        notification = Notification(
            user_id=1,  # TODO: Obtenir l'ID du responsable RH
            title=f"Calcul de paie terminé - {month}/{year}",
            message=f"{len(results)} fiches de paie calculées pour validation",
            type='info',
            category='payroll',
            link_url=f"/payroll/validation?month={month}&year={year}"
        )
        db.session.add(notification)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f"{len(results)} fiches de paie calculées",
            'results': results
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Erreur calcul paie: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@payroll_bp.route('/validate', methods=['POST'])
def validate_payroll():
    """Valider une ou plusieurs fiches de paie"""
    try:
        data = request.get_json()
        payroll_ids = data.get('payroll_ids', [])
        validated_by = data.get('validated_by_id')  # ID du validateur
        
        if not payroll_ids:
            return jsonify({
                'success': False,
                'message': 'Aucune fiche de paie sélectionnée'
            }), 400
        
        payrolls = Payroll.query.filter(
            and_(
                Payroll.id.in_(payroll_ids),
                Payroll.status == 'draft'
            )
        ).all()
        
        validated_count = 0
        
        for payroll in payrolls:
            payroll.status = 'validated'
            payroll.validated_by_id = validated_by
            payroll.validated_at = datetime.utcnow()
            validated_count += 1
            
            # Log d'audit
            audit = AuditLog(
                user_id=validated_by,
                action='validate',
                model='Payroll',
                model_id=payroll.id,
                description=f"Validation fiche de paie {payroll.employee.full_name} - {payroll.month}/{payroll.year}",
                category='finance',
                severity='info'
            )
            db.session.add(audit)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f"{validated_count} fiches de paie validées"
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Erreur validation paie: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@payroll_bp.route('/generate-payslips', methods=['POST'])
def generate_payslips():
    """Générer les fiches de paie PDF"""
    try:
        data = request.get_json()
        payroll_ids = data.get('payroll_ids', [])
        send_email = data.get('send_email', False)
        
        payrolls = Payroll.query.filter(
            and_(
                Payroll.id.in_(payroll_ids),
                Payroll.status.in_(['validated', 'paid'])
            )
        ).all()
        
        generated = []
        
        for payroll in payrolls:
            # Générer le PDF
            pdf_path = generate_payslip_pdf(payroll)
            payroll.payslip_path = pdf_path
            
            # Envoyer par email si demandé
            if send_email and payroll.employee.user and payroll.employee.user.email:
                # TODO: Implémenter l'envoi d'email
                pass
            
            generated.append({
                'payroll_id': payroll.id,
                'employee_name': payroll.employee.full_name,
                'pdf_path': pdf_path
            })
            
            # Notification à l'employé
            if payroll.employee.user:
                notification = Notification(
                    user_id=payroll.employee.user.id,
                    title=f"Fiche de paie disponible - {payroll.month}/{payroll.year}",
                    message="Votre fiche de paie est disponible dans votre espace personnel",
                    type='info',
                    category='payroll',
                    link_url=f"/employee/payslips/{payroll.id}"
                )
                db.session.add(notification)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f"{len(generated)} fiches de paie générées",
            'payslips': generated
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Erreur génération fiches de paie: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@payroll_bp.route('/list')
def list_payrolls():
    """Lister les fiches de paie avec filtres"""
    try:
        # Paramètres
        month = request.args.get('month', type=int)
        year = request.args.get('year', type=int)
        employee_id = request.args.get('employee_id', type=int)
        department = request.args.get('department')
        status = request.args.get('status')
        
        # Construire la requête
        query = db.session.query(
            Payroll,
            Employee,
            User
        ).join(
            Employee, Payroll.employee_id == Employee.id
        ).join(
            User, Employee.user_id == User.id
        )
        
        # Appliquer les filtres
        if month:
            query = query.filter(Payroll.month == month)
        
        if year:
            query = query.filter(Payroll.year == year)
        
        if employee_id:
            query = query.filter(Payroll.employee_id == employee_id)
        
        if department:
            query = query.filter(Employee.department == department)
        
        if status:
            query = query.filter(Payroll.status == status)
        
        payrolls = query.order_by(
            Payroll.year.desc(),
            Payroll.month.desc(),
            User.last_name
        ).all()
        
        # Formater les résultats
        result = []
        total_gross = Decimal('0')
        total_net = Decimal('0')
        
        for payroll, employee, user in payrolls:
            result.append({
                'id': payroll.id,
                'employee': {
                    'id': employee.id,
                    'name': user.full_name,
                    'department': employee.department,
                    'position': employee.position
                },
                'period': f"{payroll.month:02d}/{payroll.year}",
                'hours': {
                    'regular': payroll.regular_hours,
                    'overtime': payroll.overtime_hours
                },
                'amounts': {
                    'gross': float(payroll.gross_salary),
                    'net': float(payroll.net_salary),
                    'deductions': float(payroll.gross_salary - payroll.net_salary)
                },
                'status': payroll.status,
                'payment_date': payroll.payment_date.strftime('%d/%m/%Y') if payroll.payment_date else None,
                'has_payslip': bool(payroll.payslip_path)
            })
            
            total_gross += payroll.gross_salary
            total_net += payroll.net_salary
        
        return jsonify({
            'success': True,
            'payrolls': result,
            'summary': {
                'count': len(result),
                'total_gross': float(total_gross),
                'total_net': float(total_net),
                'total_charges': float(total_gross - total_net)
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"Erreur liste paie: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@payroll_bp.route('/payslip/<int:payroll_id>')
def download_payslip(payroll_id):
    """Télécharger une fiche de paie"""
    try:
        payroll = Payroll.query.get_or_404(payroll_id)
        
        # Vérifier les permissions
        # TODO: Implémenter la vérification des permissions
        
        if not payroll.payslip_path:
            # Générer la fiche si elle n'existe pas
            pdf_buffer = generate_payslip_pdf(payroll)
        else:
            # Lire le fichier existant
            with open(payroll.payslip_path, 'rb') as f:
                pdf_buffer = io.BytesIO(f.read())
        
        filename = f"fiche_paie_{payroll.employee.employee_code}_{payroll.year}_{payroll.month:02d}.pdf"
        
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        current_app.logger.error(f"Erreur téléchargement fiche de paie: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@payroll_bp.route('/summary/<int:year>')
def annual_summary(year):
    """Résumé annuel des paies"""
    try:
        # Récupérer toutes les paies de l'année
        payrolls = db.session.query(
            Payroll.month,
            func.count(Payroll.id).label('count'),
            func.sum(Payroll.gross_salary).label('total_gross'),
            func.sum(Payroll.net_salary).label('total_net'),
            func.sum(Payroll.social_security).label('total_social'),
            func.sum(Payroll.tax_deduction).label('total_tax')
        ).filter(
            Payroll.year == year
        ).group_by(
            Payroll.month
        ).order_by(
            Payroll.month
        ).all()
        
        # Formater par mois
        monthly_data = []
        yearly_totals = {
            'gross': Decimal('0'),
            'net': Decimal('0'),
            'social': Decimal('0'),
            'tax': Decimal('0')
        }
        
        for month_data in payrolls:
            monthly_data.append({
                'month': month_data.month,
                'month_name': calendar.month_name[month_data.month],
                'employee_count': month_data.count,
                'amounts': {
                    'gross': float(month_data.total_gross or 0),
                    'net': float(month_data.total_net or 0),
                    'social_charges': float(month_data.total_social or 0),
                    'tax': float(month_data.total_tax or 0)
                }
            })
            
            yearly_totals['gross'] += month_data.total_gross or 0
            yearly_totals['net'] += month_data.total_net or 0
            yearly_totals['social'] += month_data.total_social or 0
            yearly_totals['tax'] += month_data.total_tax or 0
        
        # Statistiques par département
        dept_stats = db.session.query(
            Employee.department,
            func.count(distinct(Payroll.employee_id)).label('employees'),
            func.sum(Payroll.gross_salary).label('total_gross')
        ).join(
            Employee, Payroll.employee_id == Employee.id
        ).filter(
            Payroll.year == year
        ).group_by(
            Employee.department
        ).all()
        
        department_data = [{
            'department': dept.department,
            'employee_count': dept.employees,
            'total_cost': float(dept.total_gross or 0),
            'average_cost': float(dept.total_gross / dept.employees) if dept.employees > 0 else 0
        } for dept in dept_stats]
        
        return jsonify({
            'success': True,
            'year': year,
            'monthly_data': monthly_data,
            'yearly_totals': {
                'gross': float(yearly_totals['gross']),
                'net': float(yearly_totals['net']),
                'social_charges': float(yearly_totals['social']),
                'tax': float(yearly_totals['tax']),
                'total_charges': float(yearly_totals['gross'] - yearly_totals['net'])
            },
            'department_breakdown': department_data,
            'average_monthly_cost': float(yearly_totals['gross'] / 12) if yearly_totals['gross'] > 0 else 0
        })
        
    except Exception as e:
        current_app.logger.error(f"Erreur résumé annuel: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@payroll_bp.route('/process-payment', methods=['POST'])
def process_payment():
    """Marquer les fiches de paie comme payées"""
    try:
        data = request.get_json()
        payroll_ids = data.get('payroll_ids', [])
        payment_date = data.get('payment_date', date.today().isoformat())
        payment_method = data.get('payment_method', 'Virement')
        
        payment_date = datetime.strptime(payment_date, '%Y-%m-%d').date()
        
        payrolls = Payroll.query.filter(
            and_(
                Payroll.id.in_(payroll_ids),
                Payroll.status == 'validated'
            )
        ).all()
        
        paid_count = 0
        total_amount = Decimal('0')
        
        for payroll in payrolls:
            payroll.status = 'paid'
            payroll.payment_date = payment_date
            payroll.payment_method = payment_method
            payroll.payment_reference = f"PAY-{payroll.year}{payroll.month:02d}-{payroll.employee.employee_code}"
            
            paid_count += 1
            total_amount += payroll.net_salary
            
            # Notification à l'employé
            if payroll.employee.user:
                notification = Notification(
                    user_id=payroll.employee.user.id,
                    title="Salaire versé",
                    message=f"Votre salaire de {calendar.month_name[payroll.month]} {payroll.year} a été versé. Montant: {payroll.net_salary:.2f} CHF",
                    type='success',
                    category='payroll',
                    priority='high'
                )
                db.session.add(notification)
            
            # Traiter les remboursements de dépenses du mois
            expenses = Expense.query.filter(
                and_(
                    Expense.employee_id == payroll.employee_id,
                    Expense.payment_status == 'approved',
                    extract('month', Expense.expense_date) == payroll.month,
                    extract('year', Expense.expense_date) == payroll.year
                )
            ).all()
            
            for expense in expenses:
                expense.payment_status = 'reimbursed'
                expense.reimbursed_date = payment_date
                expense.reimbursement_amount = expense.total_amount
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f"{paid_count} salaires versés",
            'summary': {
                'count': paid_count,
                'total_amount': float(total_amount),
                'payment_date': payment_date.strftime('%d/%m/%Y'),
                'payment_method': payment_method
            }
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Erreur traitement paiement: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500