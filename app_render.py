#!/usr/bin/env python3
"""
Sistema de Préstamos - Versión Render
=====================================

Versión completa del sistema que funciona en Render sin dependencias problemáticas.
Por ahora solo rutas JSON para evitar problemas con plantillas.
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
            return jsonify({'error': 'Debe iniciar sesión para acceder a esta funcionalidad'}), 401
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Debe iniciar sesión para acceder a esta funcionalidad'}), 401
        if session.get('rol') != 'admin':
            return jsonify({'error': 'No tiene permisos de administrador'}), 403
        return f(*args, **kwargs)
    return decorated_function

# Función para generar códigos de recuperación
def generar_codigo_recuperacion():
    """Genera un código de 6 dígitos para recuperación de contraseña"""
    return ''.join(secrets.choice('0123456789') for _ in range(6))

# RUTAS DE LA APLICACIÓN

@app.route('/')
def index():
    """Página principal del sistema - JSON por ahora"""
    return jsonify({
        'mensaje': 'Sistema de Préstamos funcionando correctamente',
        'estado': 'activo',
        'timestamp': datetime.now().isoformat(),
        'version': 'render-json',
        'endpoints_disponibles': [
            '/login',
            '/logout',
            '/api/prestamos-activos',
            '/api/clientes',
            '/api/usuarios',
            '/test',
            '/health'
        ]
    })

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Iniciar sesión - Solo JSON por ahora"""
    if request.method == 'POST':
        data = request.get_json() or request.form
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'error': 'Usuario y contraseña son requeridos'}), 400
        
        # Verificar credenciales
        usuario = USUARIOS_DEMO.get(username)
        if usuario and usuario['password'] == password:
            session['user_id'] = usuario['id']
            session['username'] = usuario['username']
            session['rol'] = usuario['rol']
            return jsonify({
                'success': True,
                'mensaje': f'Bienvenido, {usuario["nombre"]}!',
                'usuario': {
                    'id': usuario['id'],
                    'username': usuario['username'],
                    'nombre': usuario['nombre'],
                    'rol': usuario['rol']
                }
            })
        else:
            return jsonify({'error': 'Usuario o contraseña incorrectos'}), 401
    
    # GET request - mostrar información del login
    return jsonify({
        'mensaje': 'Endpoint de login',
        'metodo': 'POST',
        'campos_requeridos': ['username', 'password'],
        'usuarios_demo': {
            'admin': 'admin123',
            'operador': 'operador123'
        }
    })

@app.route('/logout')
def logout():
    """Cerrar sesión"""
    session.clear()
    return jsonify({'mensaje': 'Has cerrado sesión exitosamente'})

# API básica
@app.route('/api/prestamos-activos')
@login_required
def api_prestamos_activos():
    """API para obtener préstamos activos"""
    try:
        prestamos_activos = [p for p in PRESTAMOS_DEMO if p['estado'] == 'activo']
        return jsonify({
            'success': True,
            'data': prestamos_activos,
            'total': len(prestamos_activos)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/clientes')
@login_required
def api_clientes():
    """API para obtener clientes"""
    try:
        return jsonify({
            'success': True,
            'data': CLIENTES_DEMO,
            'total': len(CLIENTES_DEMO)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/usuarios')
@admin_required
def api_usuarios():
    """API para obtener usuarios (solo admin)"""
    try:
        usuarios_lista = list(USUARIOS_DEMO.values())
        return jsonify({
            'success': True,
            'data': usuarios_lista,
            'total': len(usuarios_lista)
        })
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
        'version': 'render-json',
        'funcionalidades': [
            'API de préstamos activos',
            'API de clientes',
            'API de usuarios',
            'Autenticación JSON',
            'Gestión de sesiones'
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
        'version': 'render-json'
    })

if __name__ == '__main__':
    app.run(debug=True)
