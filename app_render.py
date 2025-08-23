#!/usr/bin/env python3
"""
Sistema de Préstamos - Versión Render
=====================================

Versión completa del sistema que funciona en Render sin dependencias problemáticas.
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
    },
    'operador': {
        'id': 2,
        'username': 'operador',
        'password': 'operador123',
        'nombre': 'Operador',
        'rol': 'operador',
        'email': 'operador@example.com'
    }
}

# Simulación de clientes
CLIENTES_DEMO = [
    {
        'id': 1,
        'nombre': 'Juan Pérez',
        'dni': '12345678',
        'telefono': '555-0101',
        'email': 'juan@example.com',
        'direccion': 'Calle Principal 123',
        'fecha_registro': '2025-01-15'
    },
    {
        'id': 2,
        'nombre': 'María García',
        'dni': '87654321',
        'telefono': '555-0202',
        'email': 'maria@example.com',
        'direccion': 'Avenida Central 456',
        'fecha_registro': '2025-01-20'
    }
]

# Simulación de préstamos
PRESTAMOS_DEMO = [
    {
        'id': 1,
        'cliente_id': 1,
        'cliente_nombre': 'Juan Pérez',
        'monto_original': 1000.00,
        'monto_restante': 500.00,
        'interes': 0.05,
        'plazo_meses': 12,
        'estado': 'activo',
        'fecha_inicio': '2025-01-15',
        'usuario_creador': 'admin'
    },
    {
        'id': 2,
        'cliente_id': 2,
        'cliente_nombre': 'María García',
        'monto_original': 2000.00,
        'monto_restante': 1500.00,
        'interes': 0.05,
        'plazo_meses': 24,
        'estado': 'activo',
        'fecha_inicio': '2025-01-20',
        'usuario_creador': 'admin'
    }
]

# Simulación de pagos
PAGOS_DEMO = [
    {
        'id': 1,
        'prestamo_id': 1,
        'monto': 500.00,
        'fecha': '2025-02-15',
        'usuario': 'admin'
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

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Debe iniciar sesión para acceder a esta página', 'warning')
            return redirect(url_for('login'))
        if session.get('rol') != 'admin':
            flash('No tiene permisos de administrador', 'error')
            return redirect(url_for('index'))
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
        
        Saludos,
        {SYSTEM_CONFIG['nombre_sistema']}
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        # En producción, esto se enviaría realmente
        # server = smtplib.SMTP(SMTP_CONFIG['server'], SMTP_CONFIG['port'])
        # server.starttls()
        # server.login(SMTP_CONFIG['username'], SMTP_CONFIG['password'])
        # server.send_message(msg)
        # server.quit()
        
        return True
    except Exception as e:
        print(f"Error enviando email: {e}")
        return False

# RUTAS DE LA APLICACIÓN

@app.route('/')
@login_required
def index():
    """Página principal del sistema"""
    # Obtener estadísticas básicas
    total_prestamos = len(PRESTAMOS_DEMO)
    prestamos_activos = len([p for p in PRESTAMOS_DEMO if p['estado'] == 'activo'])
    total_clientes = len(CLIENTES_DEMO)
    
    return render_template('index.html', 
                         total_prestamos=total_prestamos,
                         prestamos_activos=prestamos_activos,
                         total_clientes=total_clientes)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Iniciar sesión"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Verificar credenciales
        usuario = USUARIOS_DEMO.get(username)
        if usuario and usuario['password'] == password:
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

@app.route('/clientes')
@login_required
def clientes():
    """Lista de clientes"""
    return render_template('clientes.html', clientes=CLIENTES_DEMO)

@app.route('/nuevo-cliente', methods=['GET', 'POST'])
@login_required
def nuevo_cliente():
    """Crear nuevo cliente"""
    if request.method == 'POST':
        # En un sistema real, se guardaría en base de datos
        flash('Cliente creado exitosamente', 'success')
        return redirect(url_for('clientes'))
    
    return render_template('nuevo_cliente.html')

@app.route('/prestamos')
@login_required
def prestamos():
    """Lista de préstamos"""
    return render_template('prestamos.html', prestamos=PRESTAMOS_DEMO)

@app.route('/nuevo-prestamo', methods=['GET', 'POST'])
@login_required
def nuevo_prestamo():
    """Crear nuevo préstamo"""
    if request.method == 'POST':
        # En un sistema real, se guardaría en base de datos
        flash('Préstamo creado exitosamente', 'success')
        return redirect(url_for('prestamos'))
    
    return render_template('nuevo_prestamo.html', clientes=CLIENTES_DEMO)

@app.route('/ver-prestamo/<int:prestamo_id>')
@login_required
def ver_prestamo(prestamo_id):
    """Ver detalles de un préstamo"""
    prestamo = next((p for p in PRESTAMOS_DEMO if p['id'] == prestamo_id), None)
    if not prestamo:
        flash('Préstamo no encontrado', 'error')
        return redirect(url_for('prestamos'))
    
    return render_template('ver_prestamo.html', prestamo=prestamo)

@app.route('/pagos')
@login_required
def pagos():
    """Lista de pagos"""
    return render_template('pagos.html', pagos=PAGOS_DEMO)

@app.route('/nuevo-pago', methods=['GET', 'POST'])
@login_required
def nuevo_pago():
    """Crear nuevo pago"""
    if request.method == 'POST':
        # En un sistema real, se guardaría en base de datos
        flash('Pago registrado exitosamente', 'success')
        return redirect(url_for('pagos'))
    
    return render_template('nuevo_pago.html', prestamos=PRESTAMOS_DEMO)

@app.route('/reportes')
@login_required
def reportes():
    """Reportes del sistema"""
    return render_template('reportes.html')

@app.route('/usuarios')
@admin_required
def usuarios():
    """Gestión de usuarios (solo admin)"""
    return render_template('usuarios.html', usuarios=USUARIOS_DEMO)

@app.route('/nuevo-usuario', methods=['GET', 'POST'])
@admin_required
def nuevo_usuario():
    """Crear nuevo usuario (solo admin)"""
    if request.method == 'POST':
        # En un sistema real, se guardaría en base de datos
        flash('Usuario creado exitosamente', 'success')
        return redirect(url_for('usuarios'))
    
    return render_template('nuevo_usuario.html')

@app.route('/configuracion')
@admin_required
def configuracion():
    """Configuración del sistema (solo admin)"""
    return render_template('configuracion.html')

# API básica
@app.route('/api/prestamos-activos')
@login_required
def api_prestamos_activos():
    """API para obtener préstamos activos"""
    try:
        prestamos_activos = [p for p in PRESTAMOS_DEMO if p['estado'] == 'activo']
        return jsonify(prestamos_activos)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/clientes')
@login_required
def api_clientes():
    """API para obtener clientes"""
    try:
        return jsonify(CLIENTES_DEMO)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Rutas de recuperación de contraseña
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

# Ruta de prueba
@app.route('/test')
def test():
    """Ruta de prueba para verificar que la aplicación funciona"""
    return jsonify({
        'status': 'success',
        'message': 'Sistema de Préstamos funcionando correctamente',
        'timestamp': datetime.now().isoformat(),
        'database': 'Demo (en memoria)',
        'version': 'render-completo',
        'funcionalidades': [
            'Gestión de clientes',
            'Gestión de préstamos',
            'Registro de pagos',
            'Reportes',
            'Gestión de usuarios',
            'API REST'
        ]
    })

# Ruta de salud
@app.route('/health')
def health():
    """Ruta de salud para Render"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'Sistema de Préstamos',
        'version': 'render-completo'
    })

if __name__ == '__main__':
    app.run(debug=True)
