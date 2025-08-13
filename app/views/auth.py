"""
Blueprint pour l'authentification
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User  # Role removed as it doesn't exist
from app.forms.auth import LoginForm, RegisterForm, TwoFactorForm
import qrcode
import io
import base64

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    """Page de connexion"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        if user and user.check_password(form.password.data):
            if not user.is_active:
                flash('Votre compte a été désactivé. Contactez l\'administrateur.', 'error')
                return redirect(url_for('auth.login'))
            
            # Si 2FA activé
            if user.is_2fa_enabled:
                session['pending_user_id'] = user.id
                return redirect(url_for('auth.two_factor'))
            
            # Connexion directe
            login_user(user, remember=form.remember_me.data)
            user.update_last_login()
            
            next_page = request.args.get('next')
            if not next_page or not next_page.startswith('/'):
                next_page = url_for('main.dashboard')
            
            flash(f'Bienvenue {user.full_name} !', 'success')
            return redirect(next_page)
        else:
            flash('Email ou mot de passe incorrect.', 'error')
    
    return render_template('auth/login.html', form=form)

@bp.route('/two-factor', methods=['GET', 'POST'])
def two_factor():
    """Vérification 2FA"""
    if 'pending_user_id' not in session:
        return redirect(url_for('auth.login'))
    
    form = TwoFactorForm()
    if form.validate_on_submit():
        user = User.query.get(session['pending_user_id'])
        
        if user and user.verify_totp(form.code.data):
            session.pop('pending_user_id', None)
            login_user(user, remember=True)
            user.update_last_login()
            
            flash(f'Bienvenue {user.full_name} !', 'success')
            return redirect(url_for('main.dashboard'))
        else:
            flash('Code invalide ou expiré.', 'error')
    
    return render_template('auth/two_factor.html', form=form)

@bp.route('/logout')
@login_required
def logout():
    """Déconnexion"""
    logout_user()
    flash('Vous avez été déconnecté.', 'info')
    return redirect(url_for('main.index'))

@bp.route('/setup-2fa')
@login_required
def setup_2fa():
    """Configuration 2FA"""
    if current_user.is_2fa_enabled:
        flash('L\'authentification à deux facteurs est déjà activée.', 'info')
        return redirect(url_for('main.dashboard'))
    
    # Générer le secret
    secret = current_user.generate_totp_secret()
    db.session.commit()
    
    # Générer le QR code
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(current_user.get_totp_uri())
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    
    qr_code = base64.b64encode(buf.getvalue()).decode()
    
    return render_template('auth/setup_2fa.html', 
                         secret=secret,
                         qr_code=qr_code)

@bp.route('/confirm-2fa', methods=['POST'])
@login_required
def confirm_2fa():
    """Confirmer l'activation 2FA"""
    code = request.form.get('code')
    
    if current_user.verify_totp(code):
        current_user.is_2fa_enabled = True
        db.session.commit()
        flash('Authentification à deux facteurs activée avec succès !', 'success')
        return redirect(url_for('main.dashboard'))
    else:
        flash('Code invalide. Veuillez réessayer.', 'error')
        return redirect(url_for('auth.setup_2fa'))

@bp.route('/disable-2fa', methods=['POST'])
@login_required
def disable_2fa():
    """Désactiver 2FA"""
    password = request.form.get('password')
    
    if current_user.check_password(password):
        current_user.is_2fa_enabled = False
        current_user.totp_secret = None
        db.session.commit()
        flash('Authentification à deux facteurs désactivée.', 'info')
    else:
        flash('Mot de passe incorrect.', 'error')
    
    return redirect(url_for('main.dashboard'))

@bp.route('/profile')
@login_required
def profile():
    """Profil utilisateur"""
    return render_template('auth/profile.html')

@bp.route('/profile/update', methods=['POST'])
@login_required
def update_profile():
    """Mettre à jour le profil"""
    current_user.first_name = request.form.get('first_name')
    current_user.last_name = request.form.get('last_name')
    current_user.phone = request.form.get('phone')
    current_user.language = request.form.get('language', 'fr')
    current_user.timezone = request.form.get('timezone', 'Europe/Zurich')
    
    db.session.commit()
    flash('Profil mis à jour avec succès.', 'success')
    return redirect(url_for('auth.profile'))

@bp.route('/change-password', methods=['POST'])
@login_required
def change_password():
    """Changer le mot de passe"""
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')
    
    if not current_user.check_password(current_password):
        flash('Mot de passe actuel incorrect.', 'error')
    elif new_password != confirm_password:
        flash('Les nouveaux mots de passe ne correspondent pas.', 'error')
    elif len(new_password) < 8:
        flash('Le nouveau mot de passe doit contenir au moins 8 caractères.', 'error')
    else:
        current_user.set_password(new_password)
        db.session.commit()
        flash('Mot de passe changé avec succès.', 'success')
    
    return redirect(url_for('auth.profile'))