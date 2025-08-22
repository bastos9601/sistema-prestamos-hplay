#!/usr/bin/env python3
"""
Sistema de Préstamos de Dinero - Versión Mínima para Render
==========================================================

Versión ultra-simplificada que funciona solo con dependencias básicas.
"""

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
import secrets
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from flask_wtf.csrf import CSRFProtect
from wtforms import StringField, DecimalField, IntegerField, SelectField, TextAreaField
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, Email, NumberRange
from decimal import Decimal, InvalidOperation
from datetime import date, timedelta
import os
from functools import wraps
import json

# Importar solo módulos básicos
from database import Database
from services import ClienteService, PrestamoService, PagoService, ReporteService, ConfiguracionService
from models import Usuario
from forms import LoginForm, CambiarPasswordForm, OlvidePasswordForm, VerificarCodigoForm, RestablecerPasswordForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'tu_clave_secreta_aqui_cambiala_en_produccion'
app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 hora
csrf = CSRFProtect(app)

# Inicializar servicios
db = Database()
cliente_service = ClienteService(db)
prestamo_service = PrestamoService(db)
pago_service = PagoService(db)
reporte_service = ReporteService(db)
configuracion_service = ConfiguracionService(db)

# Configuración para emails de recuperación
RECOVERY_CODES = {}  # En producción, usar Redis o base de datos

# Configuración por defecto para email
SMTP_CONFIG = {
    'server': 'smtp.gmail.com',
    'port': 587,
    'username': 'bastosbarbaranvictor@gmail.com',
    'password': 'ldkhglaolpcofqbs'
}

SYSTEM_CONFIG = {
    'nombre_sistema': 'Sistema de Préstamos',
    'url_base': 'http://localhost:5000',
    'tiempo_expiracion_token': 24
}

# Decoradores para requerir login y permisos
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Debe iniciar sesión para acceder a esta página', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def permiso_requerido(permiso: str):
    """Decorador para requerir un permiso específico"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Debe iniciar sesión para acceder a esta página', 'warning')
                return redirect(url_for('login'))
            
            # Obtener usuario actual
            usuario = db.obtener_usuario(session['user_id'], session['user_id'], False)
            if not usuario or not usuario.tiene_permiso(permiso):
                flash('No tiene permisos para acceder a esta funcionalidad', 'error')
                return redirect(url_for('index'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Función para generar códigos de recuperación
def generar_codigo_recuperacion():
    """Genera un código de 6 dígitos para recuperación de contraseña"""
    return ''.join(secrets.choice('0123456789') for _ in range(6))

# Función para enviar email de recuperación
def enviar_email_codigo(email, codigo):
    """Envía email con código de recuperación"""
    try:
        msg = MIMEMultipart()
        msg['From'] = SMTP_CONFIG['username']
        msg['To'] = email
        msg['Subject'] = f"Código de Recuperación - {SYSTEM_CONFIG['nombre_sistema']}"
        
        body = f"""
        Hola,
        
        Has solicitado recuperar tu contraseña en {SYSTEM_CONFIG['nombre_sistema']}.
        
        Tu código de recuperación es: {codigo}
        
        Este código expira en 10 minutos.
        
        Si no solicitaste este código, ignora este email.
        
        Saludos,
        {SYSTEM_CONFIG['nombre_sistema']}
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP(SMTP_CONFIG['server'], SMTP_CONFIG['port'])
        server.starttls()
        server.login(SMTP_CONFIG['username'], SMTP_CONFIG['password'])
        text = msg.as_string()
        server.sendmail(SMTP_CONFIG['username'], email, text)
        server.quit()
        
        return True
    except Exception as e:
        print(f"Error enviando email: {e}")
        return False

# Rutas básicas
@app.route('/')
@login_required
def index():
    """Página principal"""
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Página de login"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Verificar credenciales
        usuario = db.verificar_usuario(username, password)
        if usuario:
            session['user_id'] = usuario.id
            session['username'] = usuario.username
            session['rol'] = usuario.rol
            flash(f'Bienvenido, {usuario.nombre}!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Usuario o contraseña incorrectos', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Cerrar sesión"""
    session.clear()
    flash('Has cerrado sesión', 'info')
    return redirect(url_for('login'))

@app.route('/olvide-password', methods=['GET', 'POST'])
def olvide_password():
    """Recuperar contraseña"""
    if request.method == 'POST':
        email = request.form['email']
        
        # Buscar usuario por email
        usuario = db.obtener_usuario_por_email(email)
        if usuario:
            # Generar código de recuperación
            codigo = generar_codigo_recuperacion()
            RECOVERY_CODES[codigo] = {
                'usuario_id': usuario.id,
                'timestamp': datetime.now(),
                'email': email
            }
            
            # Enviar email
            if enviar_email_codigo(email, codigo):
                flash('Se ha enviado un código de recuperación a tu email', 'success')
                return redirect(url_for('verificar_codigo'))
            else:
                flash('Error enviando el email. Intenta nuevamente.', 'error')
        else:
            flash('No se encontró un usuario con ese email', 'error')
    
    return render_template('olvide_password.html')

@app.route('/verificar-codigo', methods=['GET', 'POST'])
def verificar_codigo():
    """Verificar código de recuperación"""
    if request.method == 'POST':
        codigo = request.form['codigo']
        
        if codigo in RECOVERY_CODES:
            recovery_data = RECOVERY_CODES[codigo]
            
            # Verificar que no haya expirado (10 minutos)
            if datetime.now() - recovery_data['timestamp'] < timedelta(minutes=10):
                session['temp_user_id'] = recovery_data['usuario_id']
                del RECOVERY_CODES[codigo]
                flash('Código verificado correctamente', 'success')
                return redirect(url_for('restablecer_password'))
            else:
                del RECOVERY_CODES[codigo]
                flash('El código ha expirado. Solicita uno nuevo.', 'error')
        else:
            flash('Código incorrecto', 'error')
    
    return render_template('verificar_codigo.html')

@app.route('/restablecer-password', methods=['GET', 'POST'])
def restablecer_password():
    """Restablecer contraseña"""
    if 'temp_user_id' not in session:
        flash('Debes verificar tu código primero', 'warning')
        return redirect(url_for('olvide_password'))
    
    if request.method == 'POST':
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        if password == confirm_password:
            # Cambiar contraseña
            if db.cambiar_password_usuario(session['temp_user_id'], password):
                del session['temp_user_id']
                flash('Contraseña cambiada exitosamente', 'success')
                return redirect(url_for('login'))
            else:
                flash('Error cambiando la contraseña', 'error')
        else:
            flash('Las contraseñas no coinciden', 'error')
    
    return render_template('restablecer_password.html')

# API básica
@app.route('/api/prestamos-activos')
@login_required
def api_prestamos_activos():
    """API para obtener préstamos activos"""
    try:
        prestamos = reporte_service.listar_prestamos_activos(session['user_id'])
        return jsonify(prestamos)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Ruta de prueba
@app.route('/test')
def test():
    """Ruta de prueba para verificar que la aplicación funciona"""
    return jsonify({
        'status': 'success',
        'message': 'Sistema de Préstamos funcionando correctamente',
        'timestamp': datetime.now().isoformat(),
        'database': 'SQLite (local)',
        'version': 'minimal'
    })

if __name__ == '__main__':
    app.run(debug=True)
