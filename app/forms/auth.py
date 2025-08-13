"""
Formulaires d'authentification
"""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError

class LoginForm(FlaskForm):
    """Formulaire de connexion"""
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Mot de passe', validators=[DataRequired()])
    remember = BooleanField('Se souvenir de moi')
    submit = SubmitField('Se connecter')

class RegisterForm(FlaskForm):
    """Formulaire d'inscription"""
    email = StringField('Email', validators=[DataRequired(), Email()])
    first_name = StringField('Prénom', validators=[DataRequired(), Length(min=2, max=50)])
    last_name = StringField('Nom', validators=[DataRequired(), Length(min=2, max=50)])
    password = PasswordField('Mot de passe', validators=[
        DataRequired(),
        Length(min=8, message='Le mot de passe doit contenir au moins 8 caractères')
    ])
    confirm = PasswordField('Confirmer le mot de passe', validators=[
        DataRequired(),
        EqualTo('password', message='Les mots de passe doivent correspondre')
    ])
    submit = SubmitField('S\'inscrire')

class TwoFactorForm(FlaskForm):
    """Formulaire pour l'authentification à deux facteurs"""
    token = StringField('Code à 6 chiffres', validators=[
        DataRequired(),
        Length(min=6, max=6, message='Le code doit contenir 6 chiffres')
    ])
    submit = SubmitField('Vérifier')

class ResetPasswordRequestForm(FlaskForm):
    """Formulaire de demande de réinitialisation de mot de passe"""
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Envoyer le lien de réinitialisation')

class ResetPasswordForm(FlaskForm):
    """Formulaire de réinitialisation de mot de passe"""
    password = PasswordField('Nouveau mot de passe', validators=[
        DataRequired(),
        Length(min=8, message='Le mot de passe doit contenir au moins 8 caractères')
    ])
    confirm = PasswordField('Confirmer le mot de passe', validators=[
        DataRequired(),
        EqualTo('password', message='Les mots de passe doivent correspondre')
    ])
    submit = SubmitField('Réinitialiser le mot de passe')