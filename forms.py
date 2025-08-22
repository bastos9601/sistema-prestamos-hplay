from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Email, Length, EqualTo

class LoginForm(FlaskForm):
    """Formulario de login"""
    username = StringField('Usuario', validators=[
        DataRequired(message='El usuario es requerido'),
        Length(min=3, max=50, message='El usuario debe tener entre 3 y 50 caracteres')
    ])
    password = PasswordField('Contraseña', validators=[
        DataRequired(message='La contraseña es requerida'),
        Length(min=6, message='La contraseña debe tener al menos 6 caracteres')
    ])
    remember_me = BooleanField('Recordarme')
    submit = SubmitField('Iniciar Sesión')

class CambiarPasswordForm(FlaskForm):
    """Formulario para cambiar contraseña"""
    password_actual = PasswordField('Contraseña Actual', validators=[
        DataRequired(message='La contraseña actual es requerida')
    ])
    password_nueva = PasswordField('Nueva Contraseña', validators=[
        DataRequired(message='La nueva contraseña es requerida'),
        Length(min=6, message='La contraseña debe tener al menos 6 caracteres')
    ])
    password_confirmar = PasswordField('Confirmar Nueva Contraseña', validators=[
        DataRequired(message='Debe confirmar la nueva contraseña')
    ])
    submit = SubmitField('Cambiar Contraseña')

class OlvidePasswordForm(FlaskForm):
    """Formulario para recuperar contraseña"""
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Enviar Código')

class VerificarCodigoForm(FlaskForm):
    """Formulario para verificar código de recuperación"""
    codigo = StringField('Código', validators=[
        DataRequired(),
        Length(min=6, max=6, message='El código debe tener exactamente 6 dígitos')
    ])
    submit = SubmitField('Verificar Código')

class RestablecerPasswordForm(FlaskForm):
    """Formulario para restablecer contraseña"""
    password = PasswordField('Nueva Contraseña', validators=[
        DataRequired(),
        Length(min=6, message='La contraseña debe tener al menos 6 caracteres')
    ])
    confirm_password = PasswordField('Confirmar Contraseña', validators=[
        DataRequired(),
        EqualTo('password', message='Las contraseñas no coinciden')
    ])
    submit = SubmitField('Restablecer Contraseña')
