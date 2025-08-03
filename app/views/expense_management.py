"""
Module de gestion des dépenses avec workflow d'approbation
"""

from flask import Blueprint, render_template, request, jsonify, send_file, current_app
from werkzeug.utils import secure_filename
from app import db
from app.models import (Employee, Expense, ExpensePolicy, AuditLog, 
                       Notification, User, Project)
from app.utils.decorators import log_action
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from sqlalchemy import and_, or_, func, extract
from decimal import Decimal
import os
import base64
from PIL import Image
import io

expense_bp = Blueprint('expense', __name__, url_prefix='/api/expense')

# Configuration
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf', 'gif'}
UPLOAD_FOLDER = 'app/static/uploads/expenses'

# Catégories de dépenses
EXPENSE_CATEGORIES = {
    'transport': 'Transport',
    'meals': 'Repas',
    'accommodation': 'Hébergement',
    'office_supplies': 'Fournitures bureau',
    'tools_equipment': 'Outils et équipement',
    'training': 'Formation',
    'client_entertainment': 'Frais de représentation',
    'communication': 'Communication',
    'other': 'Autres'
}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def check_expense_policy(expense):
    """Vérifier si une dépense respecte les politiques"""
    violations = []
    
    # Récupérer les politiques applicables
    policies = ExpensePolicy.query.filter(
        and_(
            ExpensePolicy.is_active == True,
            or_(
                ExpensePolicy.category == expense.category,
                ExpensePolicy.category == 'all'
            )
        )
    ).all()
    
    for policy in policies:
        # Vérifier la limite par dépense
        if policy.per_expense_limit and expense.total_amount > policy.per_expense_limit:
            violations.append({
                'policy': policy.name,
                'violation': f"Montant dépasse la limite ({policy.per_expense_limit} CHF)",
                'severity': 'warning'
            })
        
        # Vérifier la limite journalière
        if policy.daily_limit:
            daily_total = db.session.query(func.sum(Expense.total_amount)).filter(
                and_(
                    Expense.employee_id == expense.employee_id,
                    Expense.category == expense.category,
                    Expense.expense_date == expense.expense_date,
                    Expense.payment_status != 'rejected'
                )
            ).scalar() or 0
            
            if daily_total + expense.total_amount > policy.daily_limit:
                violations.append({
                    'policy': policy.name,
                    'violation': f"Limite journalière dépassée ({policy.daily_limit} CHF)",
                    'severity': 'error'
                })
        
        # Vérifier la limite mensuelle
        if policy.monthly_limit:
            month_start = expense.expense_date.replace(day=1)
            month_end = (month_start + relativedelta(months=1)) - timedelta(days=1)
            
            monthly_total = db.session.query(func.sum(Expense.total_amount)).filter(
                and_(
                    Expense.employee_id == expense.employee_id,
                    Expense.category == expense.category,
                    Expense.expense_date >= month_start,
                    Expense.expense_date <= month_end,
                    Expense.payment_status != 'rejected'
                )
            ).scalar() or 0
            
            if monthly_total + expense.total_amount > policy.monthly_limit:
                violations.append({
                    'policy': policy.name,
                    'violation': f"Limite mensuelle dépassée ({policy.monthly_limit} CHF)",
                    'severity': 'error'
                })
    
    return violations

@expense_bp.route('/submit', methods=['POST'])
@log_action('expense_submit')
def submit_expense():
    """Soumettre une nouvelle dépense"""
    try:
        # Récupérer les données
        employee_id = request.form.get('employee_id', type=int)
        category = request.form.get('category')
        expense_type = request.form.get('expense_type')
        description = request.form.get('description')
        amount = request.form.get('amount', type=float)
        tax_amount = request.form.get('tax_amount', type=float, default=0)
        expense_date = request.form.get('expense_date')
        project_id = request.form.get('project_id', type=int)
        payment_method = request.form.get('payment_method', 'Personnel')
        notes = request.form.get('notes')
        
        # Validation
        if not all([employee_id, category, description, amount, expense_date]):
            return jsonify({
                'success': False,
                'message': 'Données manquantes'
            }), 400
        
        employee = Employee.query.get_or_404(employee_id)
        expense_date = datetime.strptime(expense_date, '%Y-%m-%d').date()
        
        # Créer la dépense
        expense = Expense(
            employee_id=employee_id,
            category=category,
            expense_type=expense_type or category,
            description=description,
            amount=Decimal(str(amount)),
            tax_amount=Decimal(str(tax_amount)),
            total_amount=Decimal(str(amount + tax_amount)),
            expense_date=expense_date,
            project_id=project_id,
            payment_method=payment_method,
            payment_status='pending',
            submitted_by_id=employee.user_id,
            submitted_at=datetime.utcnow(),
            notes=notes
        )
        
        # Gérer le reçu/photo
        receipt_file = request.files.get('receipt')
        receipt_photo = request.form.get('receipt_photo')  # Base64
        
        if receipt_file and allowed_file(receipt_file.filename):
            # Sauvegarder le fichier
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = secure_filename(f"{employee.employee_code}_{timestamp}_{receipt_file.filename}")
            
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            receipt_file.save(filepath)
            
            expense.receipt_path = f"uploads/expenses/{filename}"
            
        elif receipt_photo:
            # Sauvegarder la photo base64
            try:
                photo_data = base64.b64decode(receipt_photo.split(',')[1])
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"{employee.employee_code}_{timestamp}_receipt.jpg"
                
                os.makedirs(UPLOAD_FOLDER, exist_ok=True)
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                
                with open(filepath, 'wb') as f:
                    f.write(photo_data)
                
                expense.receipt_photo = f"uploads/expenses/{filename}"
                
            except Exception as e:
                current_app.logger.error(f"Erreur sauvegarde photo: {e}")
        
        # Vérifier les politiques
        db.session.add(expense)
        db.session.flush()  # Pour obtenir l'ID
        
        violations = check_expense_policy(expense)
        
        if violations:
            expense.policy_violation = True
            expense.policy_violation_reason = ', '.join([v['violation'] for v in violations])
            
            # Si violation critique, nécessite approbation spéciale
            if any(v['severity'] == 'error' for v in violations):
                expense.payment_status = 'policy_review'
        
        # Générer le numéro de dépense
        year = datetime.now().year
        month = datetime.now().month
        
        last_expense = Expense.query.filter(
            Expense.expense_number.like(f'EXP-{year}{month:02d}-%')
        ).order_by(Expense.expense_number.desc()).first()
        
        if last_expense and last_expense.expense_number:
            last_num = int(last_expense.expense_number.split('-')[-1])
            next_num = last_num + 1
        else:
            next_num = 1
        
        expense.expense_number = f"EXP-{year}{month:02d}-{next_num:04d}"
        
        db.session.commit()
        
        # Notification au manager
        if employee.department:
            # Trouver le manager du département
            manager = User.query.filter_by(
                role='manager',
                department=employee.department
            ).first()
            
            if manager:
                notification = Notification(
                    user_id=manager.id,
                    title="Nouvelle dépense à approuver",
                    message=f"{employee.full_name} a soumis une dépense de {expense.total_amount} CHF",
                    type='info',
                    category='expense',
                    link_url=f"/expenses/approve/{expense.id}",
                    priority='normal' if not violations else 'high'
                )
                db.session.add(notification)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Dépense soumise avec succès',
            'expense': {
                'id': expense.id,
                'number': expense.expense_number,
                'status': expense.payment_status,
                'violations': violations
            }
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Erreur soumission dépense: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@expense_bp.route('/approve', methods=['POST'])
@log_action('expense_approve')
def approve_expense():
    """Approuver ou rejeter une dépense"""
    try:
        data = request.get_json()
        expense_id = data.get('expense_id')
        action = data.get('action')  # approve, reject
        approver_id = data.get('approver_id')
        comments = data.get('comments')
        level = data.get('level', 'manager')  # manager, finance
        
        if action not in ['approve', 'reject']:
            return jsonify({
                'success': False,
                'message': 'Action invalide'
            }), 400
        
        expense = Expense.query.get_or_404(expense_id)
        approver = User.query.get_or_404(approver_id)
        
        # Vérifier les permissions
        # TODO: Implémenter la vérification des permissions
        
        if action == 'approve':
            if level == 'manager':
                expense.manager_approved_by_id = approver_id
                expense.manager_approved_at = datetime.utcnow()
                expense.manager_comments = comments
                
                # Vérifier si approbation finale nécessaire
                if expense.total_amount > 500 or expense.policy_violation:
                    expense.payment_status = 'finance_review'
                    
                    # Notification au service finance
                    finance_users = User.query.filter_by(role='finance').all()
                    for user in finance_users:
                        notification = Notification(
                            user_id=user.id,
                            title="Dépense à valider (Finance)",
                            message=f"Dépense de {expense.employee.full_name} - {expense.total_amount} CHF",
                            type='warning' if expense.policy_violation else 'info',
                            category='expense',
                            link_url=f"/expenses/approve/{expense.id}",
                            priority='high' if expense.policy_violation else 'normal'
                        )
                        db.session.add(notification)
                else:
                    expense.payment_status = 'approved'
                    expense.final_approved_by_id = approver_id
                    expense.final_approved_at = datetime.utcnow()
                    
            elif level == 'finance':
                expense.final_approved_by_id = approver_id
                expense.final_approved_at = datetime.utcnow()
                expense.final_comments = comments
                expense.payment_status = 'approved'
            
            message = "Dépense approuvée"
            
        else:  # reject
            expense.payment_status = 'rejected'
            expense.rejected_by_id = approver_id
            expense.rejected_at = datetime.utcnow()
            expense.rejection_reason = comments
            message = "Dépense rejetée"
        
        # Notification à l'employé
        if expense.employee.user:
            notification = Notification(
                user_id=expense.employee.user_id,
                title=f"Dépense {expense.expense_number} - {'Approuvée' if action == 'approve' else 'Rejetée'}",
                message=comments or message,
                type='success' if action == 'approve' else 'error',
                category='expense',
                link_url=f"/expenses/view/{expense.id}"
            )
            db.session.add(notification)
        
        # Log d'audit
        audit = AuditLog(
            user_id=approver_id,
            action=action,
            model='Expense',
            model_id=expense_id,
            description=f"{action} expense {expense.expense_number} - {expense.total_amount} CHF",
            category='finance',
            severity='info'
        )
        db.session.add(audit)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': message,
            'expense': {
                'id': expense.id,
                'status': expense.payment_status
            }
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Erreur approbation dépense: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@expense_bp.route('/list')
def list_expenses():
    """Lister les dépenses avec filtres"""
    try:
        # Paramètres
        employee_id = request.args.get('employee_id', type=int)
        category = request.args.get('category')
        status = request.args.get('status')
        project_id = request.args.get('project_id', type=int)
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        department = request.args.get('department')
        
        # Construire la requête
        query = db.session.query(
            Expense,
            Employee,
            User,
            Project
        ).join(
            Employee, Expense.employee_id == Employee.id
        ).join(
            User, Employee.user_id == User.id
        ).outerjoin(
            Project, Expense.project_id == Project.id
        )
        
        # Appliquer les filtres
        if employee_id:
            query = query.filter(Expense.employee_id == employee_id)
        
        if category:
            query = query.filter(Expense.category == category)
        
        if status:
            query = query.filter(Expense.payment_status == status)
        
        if project_id:
            query = query.filter(Expense.project_id == project_id)
        
        if start_date:
            start = datetime.strptime(start_date, '%Y-%m-%d').date()
            query = query.filter(Expense.expense_date >= start)
        
        if end_date:
            end = datetime.strptime(end_date, '%Y-%m-%d').date()
            query = query.filter(Expense.expense_date <= end)
        
        if department:
            query = query.filter(Employee.department == department)
        
        expenses = query.order_by(Expense.expense_date.desc()).all()
        
        # Formater les résultats
        result = []
        total_amount = Decimal('0')
        
        for expense, employee, user, project in expenses:
            result.append({
                'id': expense.id,
                'number': expense.expense_number,
                'employee': {
                    'id': employee.id,
                    'name': user.full_name,
                    'department': employee.department
                },
                'category': expense.category,
                'category_label': EXPENSE_CATEGORIES.get(expense.category, expense.category),
                'description': expense.description,
                'date': expense.expense_date.strftime('%d/%m/%Y'),
                'amount': float(expense.amount),
                'tax': float(expense.tax_amount),
                'total': float(expense.total_amount),
                'project': {
                    'id': project.id,
                    'name': project.name
                } if project else None,
                'status': expense.payment_status,
                'has_receipt': bool(expense.receipt_path or expense.receipt_photo),
                'policy_violation': expense.policy_violation,
                'submitted_at': expense.submitted_at.strftime('%d/%m/%Y %H:%M') if expense.submitted_at else None
            })
            
            if expense.payment_status not in ['rejected', 'policy_review']:
                total_amount += expense.total_amount
        
        # Statistiques par catégorie
        category_stats = {}
        for exp in result:
            cat = exp['category']
            if cat not in category_stats:
                category_stats[cat] = {
                    'count': 0,
                    'total': 0,
                    'label': exp['category_label']
                }
            category_stats[cat]['count'] += 1
            category_stats[cat]['total'] += exp['total']
        
        return jsonify({
            'success': True,
            'expenses': result,
            'summary': {
                'count': len(result),
                'total_amount': float(total_amount),
                'by_category': category_stats
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"Erreur liste dépenses: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@expense_bp.route('/report')
def expense_report():
    """Rapport de dépenses détaillé"""
    try:
        # Paramètres
        period = request.args.get('period', 'month')
        year = request.args.get('year', type=int, default=date.today().year)
        month = request.args.get('month', type=int, default=date.today().month)
        group_by = request.args.get('group_by', 'category')  # category, employee, project, department
        
        # Déterminer les dates
        if period == 'month':
            start_date = date(year, month, 1)
            end_date = (start_date + relativedelta(months=1)) - timedelta(days=1)
        elif period == 'quarter':
            quarter = ((month - 1) // 3) + 1
            start_month = (quarter - 1) * 3 + 1
            start_date = date(year, start_month, 1)
            end_date = (start_date + relativedelta(months=3)) - timedelta(days=1)
        elif period == 'year':
            start_date = date(year, 1, 1)
            end_date = date(year, 12, 31)
        else:
            start_date = date.today() - timedelta(days=30)
            end_date = date.today()
        
        # Requête de base
        base_query = Expense.query.filter(
            and_(
                Expense.expense_date >= start_date,
                Expense.expense_date <= end_date,
                Expense.payment_status != 'rejected'
            )
        )
        
        # Grouper selon le paramètre
        if group_by == 'category':
            grouped_data = db.session.query(
                Expense.category,
                func.count(Expense.id).label('count'),
                func.sum(Expense.total_amount).label('total')
            ).filter(
                and_(
                    Expense.expense_date >= start_date,
                    Expense.expense_date <= end_date,
                    Expense.payment_status != 'rejected'
                )
            ).group_by(Expense.category).all()
            
            result = [{
                'group': cat,
                'label': EXPENSE_CATEGORIES.get(cat, cat),
                'count': count,
                'total': float(total or 0)
            } for cat, count, total in grouped_data]
            
        elif group_by == 'employee':
            grouped_data = db.session.query(
                Employee,
                func.count(Expense.id).label('count'),
                func.sum(Expense.total_amount).label('total')
            ).join(
                Employee, Expense.employee_id == Employee.id
            ).filter(
                and_(
                    Expense.expense_date >= start_date,
                    Expense.expense_date <= end_date,
                    Expense.payment_status != 'rejected'
                )
            ).group_by(Employee.id).all()
            
            result = [{
                'group': emp.id,
                'label': emp.full_name,
                'department': emp.department,
                'count': count,
                'total': float(total or 0)
            } for emp, count, total in grouped_data]
            
        elif group_by == 'project':
            grouped_data = db.session.query(
                Project,
                func.count(Expense.id).label('count'),
                func.sum(Expense.total_amount).label('total')
            ).join(
                Project, Expense.project_id == Project.id
            ).filter(
                and_(
                    Expense.expense_date >= start_date,
                    Expense.expense_date <= end_date,
                    Expense.payment_status != 'rejected'
                )
            ).group_by(Project.id).all()
            
            result = [{
                'group': proj.id,
                'label': proj.name,
                'status': proj.status,
                'count': count,
                'total': float(total or 0)
            } for proj, count, total in grouped_data]
            
        elif group_by == 'department':
            grouped_data = db.session.query(
                Employee.department,
                func.count(Expense.id).label('count'),
                func.sum(Expense.total_amount).label('total')
            ).join(
                Employee, Expense.employee_id == Employee.id
            ).filter(
                and_(
                    Expense.expense_date >= start_date,
                    Expense.expense_date <= end_date,
                    Expense.payment_status != 'rejected'
                )
            ).group_by(Employee.department).all()
            
            result = [{
                'group': dept,
                'label': dept,
                'count': count,
                'total': float(total or 0)
            } for dept, count, total in grouped_data]
        
        # Trier par montant décroissant
        result.sort(key=lambda x: x['total'], reverse=True)
        
        # Totaux
        total_expenses = sum(r['total'] for r in result)
        total_count = sum(r['count'] for r in result)
        
        # Top 5 dépenses
        top_expenses = base_query.order_by(
            Expense.total_amount.desc()
        ).limit(5).all()
        
        top_expenses_data = [{
            'id': exp.id,
            'number': exp.expense_number,
            'employee': exp.employee.full_name,
            'category': EXPENSE_CATEGORIES.get(exp.category, exp.category),
            'amount': float(exp.total_amount),
            'date': exp.expense_date.strftime('%d/%m/%Y'),
            'description': exp.description
        } for exp in top_expenses]
        
        return jsonify({
            'success': True,
            'period': {
                'type': period,
                'start': start_date.strftime('%d/%m/%Y'),
                'end': end_date.strftime('%d/%m/%Y')
            },
            'grouped_by': group_by,
            'data': result,
            'summary': {
                'total_amount': total_expenses,
                'total_count': total_count,
                'average_expense': total_expenses / total_count if total_count > 0 else 0
            },
            'top_expenses': top_expenses_data
        })
        
    except Exception as e:
        current_app.logger.error(f"Erreur rapport dépenses: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@expense_bp.route('/policies')
def list_policies():
    """Lister les politiques de dépenses actives"""
    try:
        policies = ExpensePolicy.query.filter_by(is_active=True).all()
        
        result = []
        for policy in policies:
            result.append({
                'id': policy.id,
                'name': policy.name,
                'category': policy.category,
                'limits': {
                    'daily': float(policy.daily_limit) if policy.daily_limit else None,
                    'monthly': float(policy.monthly_limit) if policy.monthly_limit else None,
                    'per_expense': float(policy.per_expense_limit) if policy.per_expense_limit else None
                },
                'requires_receipt': policy.requires_receipt,
                'requires_approval': policy.requires_approval,
                'approval_threshold': float(policy.approval_threshold) if policy.approval_threshold else None,
                'applies_to': 'all' if policy.applies_to_all else policy.department
            })
        
        return jsonify({
            'success': True,
            'policies': result
        })
        
    except Exception as e:
        current_app.logger.error(f"Erreur liste politiques: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500