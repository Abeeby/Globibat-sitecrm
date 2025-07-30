"""
Blueprint Admin - Gestion système et utilisateurs
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import User, Role, Employee, Attendance, Leave, Payroll
from app.utils.decorators import admin_required
from datetime import datetime, date
from werkzeug.security import generate_password_hash

bp = Blueprint('admin', __name__, url_prefix='/admin')

@bp.route('/')
@login_required
@admin_required
def dashboard():
    """Tableau de bord administrateur"""
    stats = {
        'users': {
            'total': User.query.count(),
            'active': User.query.filter_by(is_active=True).count(),
            'with_2fa': User.query.filter_by(is_2fa_enabled=True).count()
        },
        'employees': {
            'total': Employee.query.count(),
            'active': Employee.query.filter_by(is_active=True).count()
        },
        'attendance': {
            'today': Attendance.query.filter_by(date=date.today()).count(),
            'late_today': Attendance.query.filter_by(
                date=date.today()
            ).filter(
                db.or_(
                    Attendance.is_late_morning == True,
                    Attendance.is_late_afternoon == True
                )
            ).count()
        },
        'leaves': {
            'pending': Leave.query.filter_by(status='pending').count(),
            'current': Leave.query.filter(
                Leave.status == 'approved',
                Leave.start_date <= date.today(),
                Leave.end_date >= date.today()
            ).count()
        }
    }
    
    # Activité récente
    recent_logins = User.query.filter(
        User.last_login != None
    ).order_by(User.last_login.desc()).limit(10).all()
    
    # Demandes de congés en attente
    pending_leaves = Leave.query.filter_by(
        status='pending'
    ).order_by(Leave.requested_at).limit(10).all()
    
    return render_template('admin/dashboard.html',
                         stats=stats,
                         recent_logins=recent_logins,
                         pending_leaves=pending_leaves)

# =======================
# GESTION UTILISATEURS
# =======================

@bp.route('/users')
@login_required
@admin_required
def users_list():
    """Liste des utilisateurs"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    role_filter = request.args.get('role', 'all')
    
    query = User.query
    
    if search:
        query = query.filter(
            db.or_(
                User.username.ilike(f'%{search}%'),
                User.email.ilike(f'%{search}%'),
                User.first_name.ilike(f'%{search}%'),
                User.last_name.ilike(f'%{search}%')
            )
        )
    
    if role_filter != 'all':
        query = query.join(Role).filter(Role.name == role_filter)
    
    users = query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    roles = Role.query.all()
    
    return render_template('admin/users/list.html', 
                         users=users,
                         roles=roles)

@bp.route('/users/new', methods=['GET', 'POST'])
@login_required
@admin_required
def user_new():
    """Créer un nouvel utilisateur"""
    if request.method == 'POST':
        user = User()
        user.username = request.form.get('username')
        user.email = request.form.get('email')
        user.first_name = request.form.get('first_name')
        user.last_name = request.form.get('last_name')
        user.phone = request.form.get('phone')
        
        # Mot de passe
        password = request.form.get('password')
        if password:
            user.set_password(password)
        
        # Rôle
        user.role_id = request.form.get('role_id', type=int)
        
        # Statut
        user.is_active = request.form.get('is_active') == 'on'
        
        # Créer l'employé associé si demandé
        if request.form.get('create_employee') == 'on':
            employee = Employee()
            employee.employee_code = request.form.get('employee_code')
            employee.department = request.form.get('department')
            employee.position = request.form.get('position')
            employee.hire_date = datetime.strptime(
                request.form.get('hire_date'), '%Y-%m-%d'
            ).date()
            
            db.session.add(employee)
            db.session.flush()
            
            user.employee = employee
        
        db.session.add(user)
        db.session.commit()
        
        flash('Utilisateur créé avec succès!', 'success')
        return redirect(url_for('admin.user_detail', user_id=user.id))
    
    roles = Role.query.all()
    return render_template('admin/users/form.html', roles=roles)

@bp.route('/users/<int:user_id>')
@login_required
@admin_required
def user_detail(user_id):
    """Détail d'un utilisateur"""
    user = User.query.get_or_404(user_id)
    
    # Historique de connexion
    # (Nécessiterait une table de logs séparée)
    
    return render_template('admin/users/detail.html', user=user)

@bp.route('/users/<int:user_id>/toggle-status', methods=['POST'])
@login_required
@admin_required
def user_toggle_status(user_id):
    """Activer/Désactiver un utilisateur"""
    user = User.query.get_or_404(user_id)
    
    if user.id == current_user.id:
        flash('Vous ne pouvez pas désactiver votre propre compte!', 'error')
    else:
        user.is_active = not user.is_active
        db.session.commit()
        
        status = "activé" if user.is_active else "désactivé"
        flash(f'Utilisateur {status} avec succès!', 'success')
    
    return redirect(url_for('admin.user_detail', user_id=user_id))

@bp.route('/users/<int:user_id>/reset-password', methods=['POST'])
@login_required
@admin_required
def user_reset_password(user_id):
    """Réinitialiser le mot de passe"""
    user = User.query.get_or_404(user_id)
    
    new_password = request.form.get('new_password')
    if new_password:
        user.set_password(new_password)
        user.is_2fa_enabled = False  # Désactiver 2FA
        user.totp_secret = None
        db.session.commit()
        
        flash('Mot de passe réinitialisé avec succès!', 'success')
    else:
        flash('Veuillez fournir un nouveau mot de passe.', 'error')
    
    return redirect(url_for('admin.user_detail', user_id=user_id))

# =======================
# GESTION EMPLOYÉS
# =======================

@bp.route('/employees')
@login_required
@admin_required
def employees_list():
    """Liste des employés"""
    page = request.args.get('page', 1, type=int)
    department = request.args.get('department', 'all')
    
    query = Employee.query
    
    if department != 'all':
        query = query.filter_by(department=department)
    
    employees = query.order_by(Employee.employee_code).paginate(
        page=page, per_page=20, error_out=False
    )
    
    # Départements uniques pour le filtre
    departments = db.session.query(Employee.department).distinct().all()
    departments = [d[0] for d in departments if d[0]]
    
    return render_template('admin/employees/list.html',
                         employees=employees,
                         departments=departments)

@bp.route('/employees/<int:employee_id>/attendance')
@login_required
@admin_required
def employee_attendance(employee_id):
    """Historique de pointage d'un employé"""
    employee = Employee.query.get_or_404(employee_id)
    
    # Mois actuel par défaut
    month = request.args.get('month', date.today().month, type=int)
    year = request.args.get('year', date.today().year, type=int)
    
    # Pointages du mois
    attendances = Attendance.query.filter_by(
        employee_id=employee_id
    ).filter(
        db.extract('month', Attendance.date) == month,
        db.extract('year', Attendance.date) == year
    ).order_by(Attendance.date).all()
    
    # Statistiques
    stats = {
        'total_days': len(attendances),
        'total_hours': sum(a.total_hours for a in attendances),
        'overtime_hours': sum(a.overtime_hours for a in attendances),
        'late_days': len([a for a in attendances if a.is_late_morning or a.is_late_afternoon]),
        'absent_days': len([a for a in attendances if a.is_absent])
    }
    
    return render_template('admin/employees/attendance.html',
                         employee=employee,
                         attendances=attendances,
                         stats=stats,
                         month=month,
                         year=year)

# =======================
# GESTION CONGÉS
# =======================

@bp.route('/leaves')
@login_required
@admin_required
def leaves_list():
    """Liste des demandes de congés"""
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', 'pending')
    
    query = Leave.query
    
    if status != 'all':
        query = query.filter_by(status=status)
    
    leaves = query.order_by(Leave.requested_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('admin/leaves/list.html', leaves=leaves)

@bp.route('/leaves/<int:leave_id>/approve', methods=['POST'])
@login_required
@admin_required
def leave_approve(leave_id):
    """Approuver une demande de congé"""
    leave = Leave.query.get_or_404(leave_id)
    
    if leave.status != 'pending':
        flash('Cette demande a déjà été traitée.', 'error')
    else:
        leave.status = 'approved'
        leave.approved_by_id = current_user.id
        leave.approved_at = datetime.utcnow()
        
        # Mettre à jour le solde de congés
        leave.employee.calculate_vacation_balance()
        
        db.session.commit()
        
        # TODO: Envoyer notification à l'employé
        
        flash('Demande de congé approuvée!', 'success')
    
    return redirect(url_for('admin.leaves_list'))

@bp.route('/leaves/<int:leave_id>/reject', methods=['POST'])
@login_required
@admin_required
def leave_reject(leave_id):
    """Rejeter une demande de congé"""
    leave = Leave.query.get_or_404(leave_id)
    
    if leave.status != 'pending':
        flash('Cette demande a déjà été traitée.', 'error')
    else:
        leave.status = 'rejected'
        leave.approved_by_id = current_user.id
        leave.approved_at = datetime.utcnow()
        
        db.session.commit()
        
        # TODO: Envoyer notification à l'employé
        
        flash('Demande de congé rejetée.', 'info')
    
    return redirect(url_for('admin.leaves_list'))

# =======================
# GESTION PAIE
# =======================

@bp.route('/payroll')
@login_required
@admin_required
def payroll_list():
    """Liste des fiches de paie"""
    month = request.args.get('month', date.today().month, type=int)
    year = request.args.get('year', date.today().year, type=int)
    
    payrolls = Payroll.query.filter_by(
        month=month,
        year=year
    ).order_by(Payroll.employee_id).all()
    
    # Employés sans fiche de paie ce mois
    employees_with_payroll = [p.employee_id for p in payrolls]
    employees_without_payroll = Employee.query.filter(
        ~Employee.id.in_(employees_with_payroll),
        Employee.is_active == True
    ).all()
    
    return render_template('admin/payroll/list.html',
                         payrolls=payrolls,
                         employees_without_payroll=employees_without_payroll,
                         month=month,
                         year=year)

@bp.route('/payroll/generate', methods=['POST'])
@login_required
@admin_required
def payroll_generate():
    """Générer les fiches de paie du mois"""
    month = request.form.get('month', type=int)
    year = request.form.get('year', type=int)
    employee_ids = request.form.getlist('employee_ids[]', type=int)
    
    generated_count = 0
    
    for employee_id in employee_ids:
        employee = Employee.query.get(employee_id)
        if not employee:
            continue
        
        # Vérifier si la fiche existe déjà
        existing = Payroll.query.filter_by(
            employee_id=employee_id,
            month=month,
            year=year
        ).first()
        
        if existing:
            continue
        
        # Calculer les heures travaillées ce mois
        attendances = Attendance.query.filter_by(
            employee_id=employee_id
        ).filter(
            db.extract('month', Attendance.date) == month,
            db.extract('year', Attendance.date) == year
        ).all()
        
        regular_hours = sum(min(a.total_hours, 8) for a in attendances)
        overtime_hours = sum(max(a.total_hours - 8, 0) for a in attendances)
        
        # Créer la fiche de paie
        payroll = Payroll(
            employee_id=employee_id,
            month=month,
            year=year,
            regular_hours=regular_hours,
            overtime_hours=overtime_hours
        )
        
        # Calculer les montants
        if employee.hourly_rate:
            payroll.base_amount = regular_hours * employee.hourly_rate
            payroll.overtime_amount = overtime_hours * employee.hourly_rate * 1.25
        elif employee.base_salary:
            payroll.base_amount = employee.base_salary
            payroll.overtime_amount = (employee.base_salary / 173) * overtime_hours * 1.25
        
        payroll.gross_salary = payroll.base_amount + payroll.overtime_amount
        
        # Calculer les déductions
        payroll.calculate_deductions()
        
        db.session.add(payroll)
        generated_count += 1
    
    db.session.commit()
    
    flash(f'{generated_count} fiches de paie générées!', 'success')
    return redirect(url_for('admin.payroll_list', month=month, year=year))

# =======================
# PARAMÈTRES
# =======================

@bp.route('/settings')
@login_required
@admin_required
def settings():
    """Paramètres système"""
    return render_template('admin/settings.html')

@bp.route('/roles')
@login_required
@admin_required
def roles_list():
    """Gestion des rôles"""
    roles = Role.query.all()
    return render_template('admin/roles/list.html', roles=roles)

@bp.route('/roles/<int:role_id>/permissions', methods=['POST'])
@login_required
@admin_required
def role_update_permissions(role_id):
    """Mettre à jour les permissions d'un rôle"""
    role = Role.query.get_or_404(role_id)
    
    # Récupérer les permissions depuis le formulaire
    permissions = request.form.getlist('permissions[]')
    role.permissions = permissions
    
    db.session.commit()
    
    flash('Permissions mises à jour!', 'success')
    return redirect(url_for('admin.roles_list'))