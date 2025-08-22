#!/usr/bin/env python3
"""
Sistema de Préstamos - Versión Hello World para Render
======================================================

Versión ultra-básica que funciona sin importar módulos problemáticos.
"""

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
import secrets
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import os
from functools import wraps
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'tu_clave_secreta_aqui_cambiala_en_produccion'
app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 hora

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

# Simulación de base de datos en memoria
USUARIOS_DEMO = {
    'admin': {
        'id': 1,
        'username': 'admin',
        'password': 'admin123',
        'nombre': 'Administrador',
        'rol': 'admin',
        'email': 'admin@example.com'
    }
}

# Simulación de datos
PRESTAMOS_DEMO = [
    {
        'id': 1,
        'cliente': 'Juan Pérez',
        'monto_original': 1000.00,
        'monto_restante': 500.00,
        'estado': 'activo',
        'usuario_creador': 'admin'
    },
    {
        'id': 2,
        'cliente': 'María García',
        'monto_original': 2000.00,
        'monto_restante': 1500.00,
        'estado': 'activo',
        'usuario_creador': 'admin'
    }
]

# Decoradores para requerir login
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Debe iniciar sesión para acceder a esta página', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

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
        
        # Verificar credenciales demo
        if username in USUARIOS_DEMO and USUARIOS_DEMO[username]['password'] == password:
            usuario = USUARIOS_DEMO[username]
            session['user_id'] = usuario['id']
            session['username'] = usuario['username']
            session['rol'] = usuario['rol']
            flash(f'Bienvenido, {usuario["nombre"]}!', 'success')
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
        usuario = None
        for u in USUARIOS_DEMO.values():
            if u.get('email') == email:
                usuario = u
                break
        
        if usuario:
            # Generar código de recuperación
            codigo = generar_codigo_recuperacion()
            # En un sistema real, esto se guardaría en base de datos
            flash('Se ha enviado un código de recuperación a tu email', 'success')
            return redirect(url_for('verificar_codigo'))
        else:
            flash('No se encontró un usuario con ese email', 'error')
    
    return render_template('olvide_password.html')

@app.route('/verificar-codigo', methods=['GET', 'POST'])
def verificar_codigo():
    """Verificar código de recuperación"""
    if request.method == 'POST':
        codigo = request.form['codigo']
        # En un sistema real, se verificaría el código
        flash('Código verificado correctamente', 'success')
        return redirect(url_for('restablecer_password'))
    
    return render_template('verificar_codigo.html')

@app.route('/restablecer-password', methods=['GET', 'POST'])
def restablecer_password():
    """Restablecer contraseña"""
    if request.method == 'POST':
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        if password == confirm_password:
            flash('Contraseña cambiada exitosamente', 'success')
            return redirect(url_for('login'))
        else:
            flash('Las contraseñas no coinciden', 'error')
    
    return render_template('restablecer_password.html')

# API básica
@app.route('/api/prestamos-activos')
@login_required
def api_prestamos_activos():
    """API para obtener préstamos activos"""
    try:
        return jsonify(PRESTAMOS_DEMO)
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
        'database': 'Demo (en memoria)',
        'version': 'hello-world'
    })

# Ruta de salud
@app.route('/health')
def health():
    """Ruta de salud para Render"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'Sistema de Préstamos'
    })

if __name__ == '__main__':
    app.run(debug=True)
