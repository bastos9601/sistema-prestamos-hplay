#!/usr/bin/env python3
"""
Sistema de Préstamos de Dinero - Aplicación Web
===============================================

Una aplicación web moderna y responsive para gestionar préstamos de dinero.
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
from pdf_generator import PagarePDFGenerator

# Importar módulos del sistema
from database import Database
from services import ClienteService, PrestamoService, PagoService, ReporteService, ConfiguracionService
from models import Usuario
from forms import LoginForm, CambiarPasswordForm, OlvidePasswordForm, VerificarCodigoForm, RestablecerPasswordForm
from pagare_generator import PagareGenerator
from whatsapp_sender import WhatsAppSender
import json

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

try:
    from config_email import SMTP_CONFIG, SYSTEM_CONFIG
except ImportError:
    # Configuración por defecto si no existe el archivo
    SMTP_CONFIG = {
        'server': 'smtp.gmail.com',
        'port': 587,
        'username': 'bastosbarbaranvictor@gmail.com',  # Cambiar por tu emailrbaran
        'password': 'ldkhglaolpcofqbs'      # Cambiar por tu contraseña de aplicación
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

def permisos_requeridos(permisos: list):
    """Decorador para requerir múltiples permisos"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Debe iniciar sesión para acceder a esta página', 'warning')
                return redirect(url_for('index'))
            
            # Obtener usuario actual
            usuario = db.obtener_usuario(session['user_id'], session['user_id'], False)
            if not usuario or not usuario.tiene_permisos(permisos):
                flash('No tiene permisos para acceder a esta funcionalidad', 'error')
                return redirect(url_for('index'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Formularios
class ClienteForm(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired()])
    apellido = StringField('Apellido', validators=[DataRequired()])
    dni = StringField('DNI', validators=[DataRequired()])
    telefono = StringField('Teléfono', validators=[DataRequired()])
    email = StringField('Email', validators=[Email()])

class PrestamoForm(FlaskForm):
    cliente_id = SelectField('Cliente', coerce=int, validators=[DataRequired()], choices=[])
    monto = DecimalField('Monto', validators=[DataRequired(), NumberRange(min=0.01)])
    tasa_interes = DecimalField('Tasa de Interés Anual (%)', validators=[DataRequired(), NumberRange(min=0.01)])
    plazo_dias = IntegerField('Plazo en Días', validators=[DataRequired(), NumberRange(min=1)])
    tipo_interes = SelectField('Tipo de Interés', 
        choices=[
            ('gota_a_gota', 'Gota a Gota (Recomendado)'), 
            ('simple', 'Simple'), 
            ('compuesto', 'Compuesto')
        ],
        default='gota_a_gota'
    )

class PagoForm(FlaskForm):
    prestamo_id = IntegerField('ID del Préstamo', validators=[DataRequired()])
    monto = DecimalField('Monto del Pago', validators=[DataRequired(), NumberRange(min=0.01)])
    concepto = TextAreaField('Concepto')

# Rutas principales
@app.route('/')
@login_required
def index():
    """Página principal del sistema"""
    try:
        usuario_actual = db.obtener_usuario(session['user_id'], session['user_id'], False)
        es_admin = usuario_actual.rol == 'admin' if usuario_actual else False
        
        # Para supervisores, usar None como usuario_id para que vea todos los usuarios no-admin
        if usuario_actual and usuario_actual.rol in ['supervisor', 'consultor']:
            stats = reporte_service.generar_reporte_general(None, es_admin)
        else:
            stats = reporte_service.generar_reporte_general(session['user_id'], es_admin)
        
        return render_template('index.html', stats=stats, usuario=usuario_actual)
    except Exception as e:
        flash(f'Error al cargar estadísticas: {e}', 'error')
        return render_template('index.html', stats={}, usuario=None)

@app.route('/clientes')
@permiso_requerido('clientes.ver')
def clientes():
    """Lista de clientes"""
    try:
        usuario_actual = db.obtener_usuario(session['user_id'], session['user_id'], False)
        es_admin = usuario_actual.rol == 'admin' if usuario_actual else False
        
        # Para supervisores, permitir ver clientes de usuarios no-admin
        if usuario_actual and usuario_actual.rol in ['supervisor', 'consultor']:
            es_admin = False  # Usar filtrado de supervisor en lugar de admin
            # Para supervisores, usar None como usuario_id para que vea todos los usuarios no-admin
            clientes_list = cliente_service.listar_clientes(None, es_admin)
        elif usuario_actual and usuario_actual.rol == 'admin':
            es_admin = True
            clientes_list = cliente_service.listar_clientes(session['user_id'], es_admin)
        else:
            clientes_list = cliente_service.listar_clientes(session['user_id'], es_admin)
        
        # Enriquecer clientes con información del usuario creador
        clientes_enriquecidos = []
        for cliente in clientes_list:
            # Obtener usuario creador del cliente
            if usuario_actual and usuario_actual.rol in ['supervisor', 'consultor']:
                usuario_creador = db.obtener_usuario(cliente.usuario_id, None, True)
            else:
                usuario_creador = db.obtener_usuario(cliente.usuario_id, session['user_id'], es_admin)
            
            # Crear cliente enriquecido
            cliente_enriquecido = cliente
            cliente_enriquecido.usuario_creador = usuario_creador
            clientes_enriquecidos.append(cliente_enriquecido)
        
        return render_template('clientes.html', clientes=clientes_enriquecidos, usuario=usuario_actual)
    except Exception as e:
        flash(f'Error al cargar clientes: {e}', 'error')
        return render_template('clientes.html', clientes=[], usuario=None)

@app.route('/clientes/nuevo', methods=['GET', 'POST'])
@permiso_requerido('clientes.crear')
def nuevo_cliente():
    """Crear nuevo cliente"""
    if request.method == 'POST':
        form = ClienteForm(request.form)
        if form.validate():
            try:
                cliente = cliente_service.crear_cliente(
                    nombre=form.nombre.data,
                    apellido=form.apellido.data,
                    dni=form.dni.data,
                    telefono=form.telefono.data,
                    email=form.email.data,
                    usuario_id=session['user_id']
                )
                flash(f'Cliente {cliente.nombre} {cliente.apellido} creado exitosamente con ID: {cliente.id}', 'success')
                return redirect(url_for('clientes'))
            except Exception as e:
                flash(f'Error al crear cliente: {e}', 'error')
    else:
        form = ClienteForm()
    
    return render_template('nuevo_cliente.html', form=form)

@app.route('/clientes/<int:cliente_id>/editar', methods=['GET', 'POST'])
@permiso_requerido('clientes.editar')
def editar_cliente(cliente_id):
    """Editar cliente existente"""
    try:
        usuario_actual = db.obtener_usuario(session['user_id'], session['user_id'], False)
        es_admin = usuario_actual.rol == 'admin' if usuario_actual else False
        
        cliente = cliente_service.obtener_cliente(cliente_id, session['user_id'], es_admin)
        if not cliente:
            flash('Cliente no encontrado o no tienes permisos para acceder a él', 'error')
            return redirect(url_for('clientes'))
        
        if request.method == 'POST':
            form = ClienteForm(request.form, obj=cliente)
            if form.validate():
                if cliente_service.actualizar_cliente(
                    cliente_id,
                    usuario_id=session['user_id'],
                    es_admin=es_admin,
                    nombre=form.nombre.data,
                    apellido=form.apellido.data,
                    telefono=form.telefono.data,
                    email=form.email.data
                ):
                    flash('Cliente actualizado exitosamente', 'success')
                    return redirect(url_for('clientes'))
                else:
                    flash('Error al actualizar cliente', 'error')
        else:
            form = ClienteForm(obj=cliente)
        
        return render_template('editar_cliente.html', form=form, cliente=cliente)
        
    except Exception as e:
        flash(f'Error: {e}', 'error')
        return redirect(url_for('clientes'))

@app.route('/clientes/<int:cliente_id>/eliminar', methods=['POST'])
@permiso_requerido('clientes.eliminar')
def eliminar_cliente(cliente_id):
    """Eliminar cliente completamente"""
    try:
        usuario_actual = db.obtener_usuario(session['user_id'], session['user_id'], False)
        es_admin = usuario_actual.rol == 'admin' if usuario_actual else False
        
        if cliente_service.eliminar_cliente(cliente_id, session['user_id'], es_admin):
            flash('Cliente eliminado completamente de la base de datos', 'success')
        else:
            flash('Error al eliminar cliente o no tienes permisos', 'error')
    except Exception as e:
        flash(f'Error: {e}', 'error')
    
    return redirect(url_for('clientes'))

@app.route('/prestamos')
@permiso_requerido('prestamos.ver')
def prestamos():
    """Lista de préstamos"""
    try:
        usuario_actual = db.obtener_usuario(session['user_id'], session['user_id'], False)
        es_admin = usuario_actual.rol == 'admin' if usuario_actual else False
        
        # Para supervisores, permitir ver préstamos de usuarios no-admin
        if usuario_actual and usuario_actual.rol in ['supervisor', 'consultor']:
            es_admin = False  # Usar filtrado de supervisor en lugar de admin
            # Para supervisores, usar None como usuario_id para que vea todos los usuarios no-admin
            prestamos_list = prestamo_service.listar_prestamos_activos(None, es_admin)
        elif usuario_actual and usuario_actual.rol == 'admin':
            es_admin = True
            prestamos_list = prestamo_service.listar_prestamos_activos(session['user_id'], es_admin)
        else:
            prestamos_list = prestamo_service.listar_prestamos_activos(session['user_id'], es_admin)
        
        # Enriquecer cada préstamo con información del cliente y pagos
        prestamos_enriquecidos = []
        for prestamo in prestamos_list:
            # Para supervisores, usar None como usuario_id para obtener cliente y pagos
            if usuario_actual and usuario_actual.rol in ['supervisor', 'consultor']:
                cliente = cliente_service.obtener_cliente(prestamo.cliente_id, None, True)  # Usar es_admin = True para supervisores
                pagos = pago_service.listar_pagos_prestamo(prestamo.id, None, True)  # Usar es_admin = True para supervisores
            else:
                cliente = cliente_service.obtener_cliente(prestamo.cliente_id, session['user_id'], es_admin)
                pagos = pago_service.listar_pagos_prestamo(prestamo.id, session['user_id'], es_admin)
            
            if cliente:  # Solo incluir si el cliente es accesible
                # Para supervisores, obtener información del usuario creador del préstamo
                if usuario_actual and usuario_actual.rol in ['supervisor', 'consultor']:
                    usuario_creador = db.obtener_usuario(prestamo.usuario_id, None, True)
                else:
                    usuario_creador = db.obtener_usuario(prestamo.usuario_id, session['user_id'], es_admin)
                
                prestamos_enriquecidos.append({
                    'prestamo': prestamo,
                    'cliente': cliente,
                    'pagos': pagos,
                    'usuario_creador': usuario_creador
                })
        
        return render_template('prestamos.html', prestamos=prestamos_enriquecidos, usuario=usuario_actual)
    except Exception as e:
        flash(f'Error al cargar préstamos: {e}', 'error')
        return render_template('prestamos.html', prestamos=[], usuario=None)

@app.route('/prestamos/nuevo', methods=['GET', 'POST'])
@permiso_requerido('prestamos.crear')
def nuevo_prestamo():
    """Crear nuevo préstamo"""
    try:
        usuario_actual = db.obtener_usuario(session['user_id'], session['user_id'], False)
        es_admin = usuario_actual.rol == 'admin' if usuario_actual else False
        
        # Obtener lista de clientes para el formulario
        # Para supervisores, permitir ver clientes de usuarios no-admin
        if usuario_actual and usuario_actual.rol in ['supervisor', 'consultor']:
            es_admin = False  # Usar filtrado de supervisor en lugar de admin
            # Para supervisores, usar None como usuario_id para que vea todos los usuarios no-admin
            clientes_list = cliente_service.listar_clientes(None, es_admin)
        elif usuario_actual and usuario_actual.rol == 'admin':
            es_admin = True
            clientes_list = cliente_service.listar_clientes(session['user_id'], es_admin)
        else:
            clientes_list = cliente_service.listar_clientes(session['user_id'], es_admin)
        
        if request.method == 'POST':
            form = PrestamoForm(request.form)
            # Configurar las opciones ANTES de validar
            form.cliente_id.choices = [(cliente.id, f"{cliente.nombre} {cliente.apellido} - DNI: {cliente.dni}") for cliente in clientes_list]
            
            if form.validate():
                try:
                    prestamo = prestamo_service.crear_prestamo(
                        cliente_id=form.cliente_id.data,
                        monto=form.monto.data,
                        tasa_interes=form.tasa_interes.data,
                        plazo_dias=form.plazo_dias.data,
                        tipo_interes=form.tipo_interes.data,
                        usuario_id=session['user_id']
                    )
                    flash(f'Préstamo creado exitosamente con ID: {prestamo.id}', 'success')
                    return redirect(url_for('prestamos'))
                except Exception as e:
                    flash(f'Error al crear préstamo: {e}', 'error')
            else:
                # Si hay errores de validación, mostrar los errores
                for field, errors in form.errors.items():
                    for error in errors:
                        flash(f'Error en {field}: {error}', 'error')
        else:
            form = PrestamoForm()
            # Configurar las opciones para GET también
            form.cliente_id.choices = [(cliente.id, f"{cliente.nombre} {cliente.apellido} - DNI: {cliente.dni}") for cliente in clientes_list]
        
        return render_template('nuevo_prestamo.html', form=form, clientes_list=clientes_list, usuario=usuario_actual)
        
    except Exception as e:
        flash(f'Error: {e}', 'error')
        return redirect(url_for('prestamos'))

@app.route('/prestamos/<int:prestamo_id>')
@permiso_requerido('prestamos.ver')
def ver_prestamo(prestamo_id):
    """Ver detalles de un préstamo"""
    try:
        usuario_actual = db.obtener_usuario(session['user_id'], session['user_id'], False)
        es_admin = usuario_actual.rol == 'admin' if usuario_actual else False
        
        # Para supervisores, usar None como usuario_id para obtener resumen del préstamo
        if usuario_actual and usuario_actual.rol in ['supervisor', 'consultor']:
            resumen = prestamo_service.obtener_resumen_prestamo(prestamo_id, None, es_admin)
        else:
            resumen = prestamo_service.obtener_resumen_prestamo(prestamo_id, session['user_id'], es_admin)
        return render_template('ver_prestamo.html', resumen=resumen, usuario=usuario_actual)
    except Exception as e:
        flash(f'Error al obtener préstamo: {e}', 'error')
        return redirect(url_for('prestamos'))

@app.route('/prestamos/<int:prestamo_id>/pagare')
@permiso_requerido('prestamos.ver')
def ver_pagare(prestamo_id):
    """Ver pagaré interactivo de un préstamo"""
    try:
        usuario_actual = db.obtener_usuario(session['user_id'], session['user_id'], False)
        es_admin = usuario_actual.rol == 'admin' if usuario_actual else False
        
        prestamo = prestamo_service.obtener_prestamo(prestamo_id, session['user_id'], es_admin)
        if not prestamo:
            flash('Préstamo no encontrado o no tienes permisos para acceder a él', 'error')
            return redirect(url_for('prestamos'))
        
        cliente = cliente_service.obtener_cliente(prestamo.cliente_id, session['user_id'], es_admin)
        if not cliente:
            flash('Cliente no encontrado o no tienes permisos para acceder a él', 'error')
            return redirect(url_for('prestamos'))
        
        # Importar timedelta para el template
        from datetime import timedelta
        
        return render_template('pagare_interactivo.html', 
                             prestamo=prestamo, 
                             cliente=cliente, 
                             usuario=usuario_actual,
                             timedelta=timedelta)
    except Exception as e:
        flash(f'Error al generar pagaré: {e}', 'error')
        return redirect(url_for('prestamos'))

@app.route('/prestamos/<int:prestamo_id>/eliminar', methods=['POST'])
@permiso_requerido('prestamos.eliminar')
def eliminar_prestamo(prestamo_id):
    """Eliminar un préstamo (con o sin pagos)"""
    try:
        usuario_actual = db.obtener_usuario(session['user_id'], session['user_id'], False)
        es_admin = usuario_actual.rol == 'admin' if usuario_actual else False
        
        # Verificar que el préstamo existe y es accesible
        prestamo = prestamo_service.obtener_prestamo(prestamo_id, session['user_id'], es_admin)
        if not prestamo:
            flash('Préstamo no encontrado o no tienes permisos para acceder a él', 'error')
            return redirect(url_for('prestamos'))
        
        # Verificar si tiene pagos para mostrar advertencia
        tiene_pagos = len(prestamo.pagos) > 0
        monto_total_pagos = sum(pago.monto for pago in prestamo.pagos)
        
        # Eliminar el préstamo
        if prestamo_service.eliminar_prestamo(prestamo_id, session['user_id'], es_admin):
            if tiene_pagos:
                flash(f'Préstamo eliminado exitosamente. Se eliminaron {len(prestamo.pagos)} pagos por un total de ${monto_total_pagos:.2f}', 'warning')
            else:
                flash('Préstamo eliminado exitosamente', 'success')
        else:
            flash('Error al eliminar préstamo o no tienes permisos', 'error')
            
    except Exception as e:
        flash(f'Error al eliminar préstamo: {e}', 'error')
    
    return redirect(url_for('prestamos'))

@app.route('/pagos')
@permiso_requerido('pagos.ver')
def pagos():
    """Lista de pagos"""
    try:
        usuario_actual = db.obtener_usuario(session['user_id'], session['user_id'], False)
        es_admin = usuario_actual.rol == 'admin' if usuario_actual else False
        
        # Para supervisores, permitir ver pagos de usuarios no-admin
        if usuario_actual and usuario_actual.rol in ['supervisor', 'consultor']:
            es_admin = False  # Usar filtrado de supervisor en lugar de admin
        elif usuario_actual and usuario_actual.rol == 'admin':
            es_admin = True
        
        # Obtener todos los pagos del usuario con información del cliente
        pagos_list = []
        # Para supervisores, usar None como usuario_id para obtener préstamos
        if usuario_actual and usuario_actual.rol in ['supervisor', 'consultor']:
            prestamos = prestamo_service.listar_prestamos_activos(None, es_admin)
        else:
            prestamos = prestamo_service.listar_prestamos_activos(session['user_id'], es_admin)
        
        for prestamo in prestamos:
            # Para supervisores, usar None como usuario_id para obtener pagos y cliente
            if usuario_actual and usuario_actual.rol in ['supervisor', 'consultor']:
                pagos_prestamo = pago_service.listar_pagos_prestamo(prestamo.id, None, es_admin)
                cliente = cliente_service.obtener_cliente(prestamo.cliente_id, None, es_admin)
            else:
                pagos_prestamo = pago_service.listar_pagos_prestamo(prestamo.id, session['user_id'], es_admin)
                cliente = cliente_service.obtener_cliente(prestamo.cliente_id, session['user_id'], es_admin)
            
            if cliente:  # Solo incluir si el cliente es accesible
                # Enriquecer cada pago con información del préstamo y cliente
                for pago in pagos_prestamo:
                    # Obtener usuario creador del pago
                    if usuario_actual and usuario_actual.rol in ['supervisor', 'consultor']:
                        usuario_creador = db.obtener_usuario(pago.usuario_id, None, True)
                    else:
                        usuario_creador = db.obtener_usuario(pago.usuario_id, session['user_id'], es_admin)
                    
                    pagos_list.append({
                        'pago': pago,
                        'prestamo': prestamo,
                        'cliente': cliente,
                        'usuario_creador': usuario_creador
                    })
        
        return render_template('pagos.html', pagos=pagos_list, usuario=usuario_actual)
    except Exception as e:
        flash(f'Error al cargar pagos: {e}', 'error')
        return render_template('pagos.html', pagos=[], usuario=None)

@app.route('/pagos/nuevo', methods=['GET', 'POST'])
@permiso_requerido('pagos.crear')
def nuevo_pago():
    """Registrar nuevo pago"""
    try:
        usuario_actual = db.obtener_usuario(session['user_id'], session['user_id'], False)
        es_admin = usuario_actual.rol == 'admin' if usuario_actual else False
        
        if request.method == 'POST':
            form = PagoForm(request.form)
            if form.validate():
                try:
                    pago = pago_service.registrar_pago(
                        prestamo_id=form.prestamo_id.data,
                        monto=form.monto.data,
                        concepto=form.concepto.data or "Pago de cuota",
                        usuario_id=session['user_id']
                    )
                    flash(f'Pago registrado exitosamente con ID: {pago.id}', 'success')
                    return redirect(url_for('pagos'))
                except Exception as e:
                    flash(f'Error al registrar pago: {e}', 'error')
        else:
            form = PagoForm()
        
        # Obtener lista de préstamos activos del usuario con información del cliente
        # Para supervisores, permitir ver préstamos de usuarios no-admin
        if usuario_actual and usuario_actual.rol in ['supervisor', 'consultor']:
            es_admin = False  # Usar filtrado de supervisor en lugar de admin
        elif usuario_actual and usuario_actual.rol == 'admin':
            es_admin = True
            
        # Para supervisores, usar None como usuario_id para obtener préstamos
        if usuario_actual and usuario_actual.rol in ['supervisor', 'consultor']:
            prestamos_list = prestamo_service.listar_prestamos_activos(None, es_admin)
        else:
            prestamos_list = prestamo_service.listar_prestamos_activos(session['user_id'], es_admin)
        
        # Enriquecer cada préstamo con información del cliente
        prestamos_enriquecidos = []
        for prestamo in prestamos_list:
            # Para supervisores, usar None como usuario_id para obtener cliente
            if usuario_actual and usuario_actual.rol in ['supervisor', 'consultor']:
                cliente = cliente_service.obtener_cliente(prestamo.cliente_id, None, es_admin)
            else:
                cliente = cliente_service.obtener_cliente(prestamo.cliente_id, session['user_id'], es_admin)
            if cliente:  # Solo incluir si el cliente es accesible
                prestamos_enriquecidos.append({
                    'prestamo': prestamo,
                    'cliente': cliente
                })
        
        return render_template('nuevo_pago.html', form=form, prestamos=prestamos_enriquecidos, usuario=usuario_actual)
        
    except Exception as e:
        flash(f'Error: {e}', 'error')
        return redirect(url_for('pagos'))

@app.route('/pagos/<int:pago_id>/eliminar', methods=['POST'])
@permiso_requerido('pagos.eliminar')
def eliminar_pago(pago_id):
    """Eliminar un pago específico"""
    try:
        usuario_actual = db.obtener_usuario(session['user_id'], session['user_id'], False)
        es_admin = usuario_actual.rol == 'admin' if usuario_actual else False
        
        if pago_service.eliminar_pago(pago_id, session['user_id'], es_admin):
            flash('Pago eliminado exitosamente', 'success')
        else:
            flash('Error al eliminar pago o no tienes permisos', 'error')
    except Exception as e:
        flash(f'Error al eliminar pago: {e}', 'error')
    
    return redirect(url_for('pagos'))

@app.route('/reportes')
@permiso_requerido('reportes.ver')
def reportes():
    """Página de reportes"""
    try:
        usuario_actual = db.obtener_usuario(session['user_id'], session['user_id'], False)
        es_admin = usuario_actual.rol == 'admin' if usuario_actual else False
        
        # Para supervisores y consultores, permitir ver reportes de usuarios no-admin
        if usuario_actual and usuario_actual.rol in ['supervisor', 'consultor']:
            es_admin = False  # Usar filtrado de supervisor en lugar de admin
            # Para supervisores y consultores, usar None como usuario_id para que vea todos los usuarios no-admin
            reporte_general = reporte_service.generar_reporte_general(None, es_admin)
            reporte_prestamos_activos = reporte_service.generar_reporte_prestamos_activos(None, es_admin)
        elif usuario_actual and usuario_actual.rol == 'admin':
            es_admin = True
            reporte_general = reporte_service.generar_reporte_general(session['user_id'], es_admin)
            reporte_prestamos_activos = reporte_service.generar_reporte_prestamos_activos(session['user_id'], es_admin)
        else:
            # Generar reportes del usuario
            reporte_general = reporte_service.generar_reporte_general(session['user_id'], es_admin)
            reporte_prestamos_activos = reporte_service.generar_reporte_prestamos_activos(session['user_id'], es_admin)
        
        return render_template('reportes.html', 
                             reporte_general=reporte_general, 
                             reporte_prestamos_activos=reporte_prestamos_activos,
                             usuario=usuario_actual)
    except Exception as e:
        flash(f'Error al cargar reportes: {e}', 'error')
        return render_template('reportes.html', 
                             reporte_general={}, 
                             reporte_prestamos_activos=[],
                             usuario=None)

@app.route('/api/reporte-general')
@login_required
def api_reporte_general():
    """API para obtener reporte general"""
    try:
        usuario_actual = db.obtener_usuario(session['user_id'], session['user_id'], False)
        es_admin = usuario_actual.rol == 'admin' if usuario_actual else False
        
        # Para supervisores, permitir ver reportes de usuarios no-admin
        if usuario_actual and usuario_actual.rol in ['supervisor', 'consultor']:
            es_admin = False  # Usar filtrado de supervisor en lugar de admin
            # Para supervisores, usar None como usuario_id para que vea todos los usuarios no-admin
            stats = reporte_service.generar_reporte_general(None, es_admin)
        elif usuario_actual and usuario_actual.rol == 'admin':
            es_admin = True
            stats = reporte_service.generar_reporte_general(session['user_id'], es_admin)
        else:
            stats = reporte_service.generar_reporte_general(session['user_id'], es_admin)
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/reporte-cliente/<int:cliente_id>')
@login_required
def api_reporte_cliente(cliente_id):
    """API para obtener reporte de un cliente"""
    try:
        usuario_actual = db.obtener_usuario(session['user_id'], session['user_id'], False)
        es_admin = usuario_actual.rol == 'admin' if usuario_actual else False
        
        reporte = reporte_service.generar_reporte_cliente(cliente_id, session['user_id'], es_admin)
        return jsonify(reporte)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/prestamos-activos')
@login_required
def api_prestamos_activos():
    """API para obtener préstamos activos"""
    try:
        usuario_actual = db.obtener_usuario(session['user_id'], session['user_id'], False)
        es_admin = usuario_actual.rol == 'admin' if usuario_actual else False
        
        print(f"🔍 API Préstamos Activos - Usuario: {usuario_actual.rol if usuario_actual else 'None'}, ID: {session['user_id']}")
        
        # Para supervisores, permitir ver préstamos de usuarios no-admin
        if usuario_actual and usuario_actual.rol in ['supervisor', 'consultor']:
            es_admin = False  # Usar filtrado de supervisor en lugar de admin
            # Para supervisores, usar None como usuario_id para que vea todos los usuarios no-admin
            prestamos = prestamo_service.listar_prestamos_activos(None, es_admin)
            print(f"👁️ Supervisor/Consultor - Préstamos encontrados: {len(prestamos)}")
        elif usuario_actual and usuario_actual.rol == 'admin':
            es_admin = True
            prestamos = prestamo_service.listar_prestamos_activos(session['user_id'], es_admin)
            print(f"👑 Admin - Préstamos encontrados: {len(prestamos)}")
        else:
            prestamos = prestamo_service.listar_prestamos_activos(session['user_id'], es_admin)
            print(f"👤 Usuario normal - Préstamos encontrados: {len(prestamos)}")
        
        prestamos_data = []
        
        for prestamo in prestamos:
            print(f"📋 Procesando préstamo ID: {prestamo.id}, Cliente ID: {prestamo.cliente_id}")
            
            # Para supervisores, usar None como usuario_id para que puedan ver todos los clientes de usuarios no-admin
            if usuario_actual and usuario_actual.rol in ['supervisor', 'consultor']:
                cliente = cliente_service.obtener_cliente(prestamo.cliente_id, None, es_admin)
                print(f"👁️ Supervisor buscando cliente {prestamo.cliente_id} con usuario_id=None")
            else:
                cliente = cliente_service.obtener_cliente(prestamo.cliente_id, session['user_id'], es_admin)
                print(f"👤 Usuario normal buscando cliente {prestamo.cliente_id} con usuario_id={session['user_id']}")
            
            if cliente:  # Solo incluir si el cliente es accesible
                print(f"✅ Cliente encontrado: {cliente.nombre} {cliente.apellido}")
                
                # Obtener información del usuario creador del préstamo
                usuario_creador = None
                if prestamo.usuario_id:
                    usuario_creador = db.obtener_usuario(prestamo.usuario_id, session['user_id'], es_admin)
                
                prestamos_data.append({
                    'id_prestamo': prestamo.id,
                    'cliente': f"{cliente.nombre} {cliente.apellido}",
                    'cliente_dni': cliente.dni,
                    'monto_original': float(prestamo.monto),
                    'tasa_interes': float(prestamo.tasa_interes),
                    'plazo_dias': prestamo.plazo_dias,
                    'fecha_inicio': prestamo.fecha_inicio.isoformat(),
                    'estado': prestamo.estado,
                    'usuario_creador': usuario_creador.username if usuario_creador else 'N/A',
                    'usuario_creador_id': prestamo.usuario_id
                })
            else:
                print(f"❌ Cliente {prestamo.cliente_id} no accesible para este usuario")
        
        print(f"📊 Total de préstamos procesados: {len(prestamos_data)}")
        return jsonify(prestamos_data)
    except Exception as e:
        print(f"❌ Error en API préstamos activos: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/buscar-cliente')
def api_buscar_cliente():
    """API para buscar clientes"""
    termino = request.args.get('q', '')
    if not termino:
        return jsonify([])
    
    try:
        # Obtener usuario actual para pasar los parámetros correctos
        usuario_actual = db.obtener_usuario(session['user_id'], session['user_id'], False)
        es_admin = usuario_actual.rol == 'admin' if usuario_actual else False
        
        # Para supervisores y consultores, usar None como usuario_id
        if usuario_actual and usuario_actual.rol in ['supervisor', 'consultor']:
            clientes = cliente_service.buscar_cliente(termino, None, es_admin)
        else:
            clientes = cliente_service.buscar_cliente(termino, session['user_id'], es_admin)
        return jsonify([{
            'id': c.id,
            'nombre': c.nombre,
            'apellido': c.apellido,
            'dni': c.dni,
            'telefono': c.telefono,
            'email': c.email
        } for c in clientes])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/enviar-pagare/<int:prestamo_id>', methods=['POST'])
@csrf.exempt
@permiso_requerido('ver_prestamos')
def enviar_pagare_whatsapp(prestamo_id):
    """Envía un pagaré por WhatsApp al cliente"""
    try:
        # Obtener usuario actual
        usuario_actual = db.obtener_usuario(session['user_id'], session['user_id'], False)
        es_admin = usuario_actual.rol == 'admin' if usuario_actual else False
        
        # Obtener el préstamo
        prestamo = db.obtener_prestamo(prestamo_id, session['user_id'], es_admin)
        if not prestamo:
            return jsonify({'success': False, 'error': 'Préstamo no encontrado'}), 404
        
        # Obtener el cliente
        cliente = db.obtener_cliente(prestamo.cliente_id, session['user_id'], es_admin)
        if not cliente:
            return jsonify({'success': False, 'error': 'Cliente no encontrado'}), 404
        
        # Verificar que el cliente tenga teléfono
        if not cliente.telefono:
            return jsonify({'success': False, 'error': 'El cliente no tiene número de teléfono registrado'}), 400
        
        # Generar el pagaré
        generador_pagare = PagareGenerator()
        pagare_texto = generador_pagare.generar_pagare(cliente, prestamo)
        
        # Enviar por WhatsApp
        whatsapp = WhatsAppSender()
        resultado = whatsapp.enviar_pagare_whatsapp(cliente.telefono, pagare_texto)
        
        if resultado:
            return jsonify({
                'success': True, 
                'message': f'Pagaré enviado exitosamente a {cliente.nombre} {cliente.apellido}',
                'telefono': cliente.telefono
            })
        else:
            return jsonify({'success': False, 'error': 'Error al enviar el pagaré'}), 500
            
    except Exception as e:
        print(f"❌ Error al enviar pagaré: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/abrir-whatsapp/<int:cliente_id>', methods=['POST'])
@csrf.exempt
@permiso_requerido('ver_clientes')
def abrir_whatsapp_cliente(cliente_id):
    """Abre WhatsApp para un cliente específico"""
    try:
        # Obtener usuario actual
        usuario_actual = db.obtener_usuario(session['user_id'], session['user_id'], False)
        es_admin = usuario_actual.rol == 'admin' if usuario_actual else False
        
        # Obtener el cliente
        cliente = db.obtener_cliente(cliente_id, session['user_id'], es_admin)
        if not cliente:
            return jsonify({'success': False, 'error': 'Cliente no encontrado'}), 404
        
        # Verificar que el cliente tenga teléfono
        if not cliente.telefono:
            return jsonify({'success': False, 'error': 'El cliente no tiene número de teléfono registrado'}), 400
        
        # Abrir WhatsApp
        whatsapp = WhatsAppSender()
        resultado = whatsapp.abrir_chat_whatsapp(cliente.telefono)
        
        if resultado:
            return jsonify({
                'success': True, 
                'message': f'WhatsApp abierto para {cliente.nombre} {cliente.apellido}',
                'telefono': cliente.telefono
            })
        else:
            return jsonify({'success': False, 'error': 'Error al abrir WhatsApp'}), 500
            
    except Exception as e:
        print(f"❌ Error al abrir WhatsApp: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/enviar-comprobante/<int:pago_id>', methods=['POST'])
@csrf.exempt
@permiso_requerido('ver_pagos')
def enviar_comprobante_pago(pago_id):
    """Genera y envía un comprobante de pago por WhatsApp"""
    try:
        # Obtener usuario actual
        usuario_actual = db.obtener_usuario(session['user_id'], session['user_id'], False)
        es_admin = usuario_actual.rol == 'admin' if usuario_actual else False
        
        # Obtener datos del pago
        pago = db.obtener_pago(pago_id, session['user_id'], es_admin)
        if not pago:
            return jsonify({'success': False, 'error': 'Pago no encontrado'}), 404
        
        # Obtener datos del préstamo
        prestamo = db.obtener_prestamo(pago.prestamo_id, session['user_id'], es_admin)
        if not prestamo:
            return jsonify({'success': False, 'error': 'Préstamo no encontrado'}), 404
        
        # Obtener datos del cliente
        cliente = db.obtener_cliente(prestamo.cliente_id, session['user_id'], es_admin)
        if not cliente:
            return jsonify({'success': False, 'error': 'Cliente no encontrado'}), 404
        
        # Verificar que el cliente tenga teléfono
        if not cliente.telefono:
            return jsonify({'success': False, 'error': 'El cliente no tiene número de teléfono registrado'}), 400
        
        # Generar comprobante
        from comprobante_generator import ComprobanteGenerator
        comprobante_gen = ComprobanteGenerator()
        
        # Convertir a diccionarios para el generador
        pago_dict = pago.to_dict()
        prestamo_dict = prestamo.to_dict()
        cliente_dict = cliente.to_dict()
        
        # Generar comprobante en texto
        comprobante_texto = comprobante_gen.generar_comprobante(pago_dict, prestamo_dict, cliente_dict)
        
        # Enviar por WhatsApp
        whatsapp = WhatsAppSender()
        success = whatsapp.enviar_mensaje(cliente.telefono, comprobante_texto)
        
        if success:
            return jsonify({
                'success': True, 
                'message': f'Comprobante enviado a {cliente.nombre} {cliente.apellido}'
            })
        else:
            return jsonify({'success': False, 'error': 'Error al enviar por WhatsApp'}), 500
            
    except Exception as e:
        print(f"❌ Error al enviar comprobante: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/abrir-whatsapp-cliente', methods=['POST'])
@csrf.exempt
@permiso_requerido('ver_pagos')
def abrir_whatsapp_cliente_pago():
    """Abre WhatsApp para chatear con un cliente desde la lista de pagos"""
    try:
        # Obtener datos del request
        data = request.get_json()
        telefono = data.get('telefono')
        nombre_cliente = data.get('nombre_cliente')
        
        if not telefono:
            return jsonify({'success': False, 'error': 'Teléfono no proporcionado'}), 400
        
        # Abrir WhatsApp
        whatsapp = WhatsAppSender()
        success = whatsapp.abrir_chat_whatsapp(telefono)
        
        if success:
            return jsonify({
                'success': True, 
                'message': f'WhatsApp abierto para {nombre_cliente}'
            })
        else:
            return jsonify({'success': False, 'error': 'Error al abrir WhatsApp'}), 500
            
    except Exception as e:
        print(f"❌ Error al abrir WhatsApp: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/guardar-firma/<int:prestamo_id>', methods=['POST'])
@csrf.exempt
def guardar_firma_digital(prestamo_id):
    """Guardar la firma digital del cliente"""
    try:
        usuario_actual = db.obtener_usuario(session['user_id'], session['user_id'], False)
        es_admin = usuario_actual.rol == 'admin' if usuario_actual else False
        
        prestamo = prestamo_service.obtener_prestamo(prestamo_id, session['user_id'], es_admin)
        if not prestamo:
            return jsonify({'success': False, 'error': 'Préstamo no encontrado'})
        
        # Obtener la imagen de la firma del request
        data = request.get_json()
        firma_base64 = data.get('firma')
        
        if not firma_base64:
            return jsonify({'success': False, 'error': 'No se recibió la firma'})
        
        # Guardar la firma en el sistema de archivos
        import base64
        import os
        from datetime import datetime
        
        # Crear directorio para firmas si no existe
        firmas_dir = 'static/firmas'
        os.makedirs(firmas_dir, exist_ok=True)
        
        # Generar nombre único para la firma
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        nombre_archivo = f"firma_prestamo_{prestamo_id}_{timestamp}.png"
        ruta_firma = os.path.join(firmas_dir, nombre_archivo)
        
        # Decodificar y guardar la imagen
        firma_data = base64.b64decode(firma_base64.split(',')[1])
        with open(ruta_firma, 'wb') as f:
            f.write(firma_data)
        
        # Guardar la ruta de la firma en la base de datos (opcional)
        # Aquí podrías agregar un campo 'firma_digital' al modelo Prestamo
        
        return jsonify({
            'success': True, 
            'message': 'Firma guardada exitosamente',
            'ruta_firma': ruta_firma
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/enviar-pagare-firmado/<int:prestamo_id>', methods=['POST'])
@csrf.exempt
def enviar_pagare_firmado_whatsapp(prestamo_id):
    """Enviar pagaré completo con firma por WhatsApp"""
    try:
        usuario_actual = db.obtener_usuario(session['user_id'], session['user_id'], False)
        es_admin = usuario_actual.rol == 'admin' if usuario_actual else False
        
        prestamo = prestamo_service.obtener_prestamo(prestamo_id, session['user_id'], es_admin)
        if not prestamo:
            return jsonify({'success': False, 'error': 'Préstamo no encontrado'})
        
        cliente = cliente_service.obtener_cliente(prestamo.cliente_id, session['user_id'], es_admin)
        if not cliente:
            return jsonify({'success': False, 'error': 'Cliente no encontrado'})
        
        # Buscar si existe una firma digital guardada
        import os
        firmas_dir = 'static/firmas'
        firma_encontrada = None
        
        if os.path.exists(firmas_dir):
            for archivo in os.listdir(firmas_dir):
                if archivo.startswith(f"firma_prestamo_{prestamo_id}_"):
                    firma_encontrada = archivo
                    break
        
        # Generar mensaje de WhatsApp
        from datetime import datetime, timedelta
        telefono = cliente.telefono
        mensaje = f"""📄 *PAGARÉ COMPLETO - PRÉSTAMO #{prestamo.id}*

👤 *CLIENTE:*
• Nombre: {cliente.nombre} {cliente.apellido}
• DNI: {cliente.dni}
• Teléfono: {cliente.telefono}

💰 *DETALLES DEL PRÉSTAMO:*
• Monto: ${prestamo.monto:.2f}
• Plazo: {prestamo.plazo_dias} días
• Tasa: {prestamo.tasa_interes:.1f}% anual
• Tipo: {prestamo.tipo_interes.title()}
• Cuota Diaria: ${prestamo.calcular_cuota_diaria():.2f}
• Total Intereses: ${prestamo.calcular_interes_total():.2f}
• Total a Pagar: ${prestamo.calcular_monto_total():.2f}

📅 *FECHAS:*
• Emisión: {prestamo.fecha_inicio.strftime('%d/%m/%Y')}
• Vencimiento: {(prestamo.fecha_inicio + timedelta(days=prestamo.plazo_dias)).strftime('%d/%m/%Y')}

📝 *CONDICIONES:*
• Pago diario de ${prestamo.calcular_cuota_diaria():.2f}
• Plazo total: {prestamo.plazo_dias} días
• En caso de mora: intereses adicionales
• Cancelación total al vencimiento

✍️ *FIRMA DEL CLIENTE:*
{f"✅ Firma digital registrada" if firma_encontrada else "📝 Firma pendiente - Firmar en el sistema"}

📋 *INSTRUCCIONES:*
1. Revisar todos los detalles del préstamo
2. Confirmar que los datos son correctos
3. Firmar digitalmente en el sistema web
4. Guardar copia del pagaré firmado

🔗 *ACCESO AL SISTEMA:*
Para firmar digitalmente, acceder al sistema web del prestamista

---
*Prestamista: Sistema de Préstamos*
*Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}*"""
        
        # Codificar el mensaje para WhatsApp
        mensaje_codificado = mensaje.replace('\n', '%0A').replace('*', '*')
        
        # Crear enlace de WhatsApp
        url_whatsapp = f"https://wa.me/51{telefono}?text={mensaje_codificado}"
        
        return jsonify({
            'success': True,
            'message': 'Pagaré preparado para WhatsApp',
            'url_whatsapp': url_whatsapp,
            'tiene_firma': firma_encontrada is not None
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/enviar-pagare-pdf-whatsapp/<int:prestamo_id>', methods=['POST'])
@csrf.exempt
def enviar_pagare_pdf_whatsapp(prestamo_id):
    """Enviar pagaré en PDF por WhatsApp"""
    try:
        usuario_actual = db.obtener_usuario(session['user_id'], session['user_id'], False)
        es_admin = usuario_actual.rol == 'admin' if usuario_actual else False
        
        prestamo = prestamo_service.obtener_prestamo(prestamo_id, session['user_id'], es_admin)
        if not prestamo:
            return jsonify({'success': False, 'error': 'Préstamo no encontrado'})
        
        cliente = cliente_service.obtener_cliente(prestamo.cliente_id, session['user_id'], es_admin)
        if not cliente:
            return jsonify({'success': False, 'error': 'Cliente no encontrado'})
        
        # Generar PDF del pagaré
        import os
        from datetime import datetime
        
        # Crear directorio de PDFs si no existe
        pdfs_dir = 'static/pdfs'
        os.makedirs(pdfs_dir, exist_ok=True)
        
        # Generar nombre del archivo PDF
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        nombre_pdf = f"pagare_prestamo_{prestamo_id}_{timestamp}.pdf"
        ruta_pdf = os.path.join(pdfs_dir, nombre_pdf)
        
        # Buscar si existe una firma digital
        firmas_dir = 'static/firmas'
        firma_encontrada = None
        
        if os.path.exists(firmas_dir):
            for archivo in os.listdir(firmas_dir):
                if archivo.startswith(f"firma_prestamo_{prestamo_id}_"):
                    firma_encontrada = os.path.join(firmas_dir, archivo)
                    break
        
        # Generar PDF
        pdf_generator = PagarePDFGenerator()
        
        if firma_encontrada:
            success, message = pdf_generator.generar_pagare_con_firma_pdf(
                prestamo, cliente, firma_encontrada, ruta_pdf
            )
        else:
            success, message = pdf_generator.generar_pagare_pdf(
                prestamo, cliente, ruta_pdf
            )
        
        if not success:
            return jsonify({'success': False, 'error': f'Error al generar PDF: {message}'})
        
        # Crear mensaje de WhatsApp con el PDF
        telefono = cliente.telefono
        mensaje = f"""📄 *PAGARÉ EN PDF - PRÉSTAMO #{prestamo.id}*

👤 *CLIENTE:*
• Nombre: {cliente.nombre} {cliente.apellido}
• DNI: {cliente.dni}

💰 *DETALLES DEL PRÉSTAMO:*
• Monto: ${prestamo.monto:.2f}
• Plazo: {prestamo.plazo_dias} días
• Cuota Diaria: ${prestamo.calcular_cuota_diaria():.2f}
• Total a Pagar: ${prestamo.calcular_monto_total():.2f}

📋 *INSTRUCCIONES:*
1. El PDF del pagaré ha sido generado exitosamente
2. Para descargarlo, ve al sistema web del prestamista
3. Busca el préstamo #{prestamo.id} y haz clic en "Descargar PDF"
4. O solicita al prestamista que te envíe el archivo por email

✅ *PDF GENERADO:* {nombre_pdf}
📱 *ACCESO:* Sistema web del prestamista

---
*Prestamista: Sistema de Préstamos*
*Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}*"""
        
        # Codificar el mensaje para WhatsApp
        mensaje_codificado = mensaje.replace('\n', '%0A').replace('*', '*')
        
        # Crear enlace de WhatsApp
        url_whatsapp = f"https://wa.me/51{telefono}?text={mensaje_codificado}"
        
        return jsonify({
            'success': True,
            'message': 'Pagaré en PDF generado y preparado para WhatsApp',
            'url_whatsapp': url_whatsapp,
            'pdf_generado': nombre_pdf,
            'tiene_firma': firma_encontrada is not None
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/enviar-pagare-email/<int:prestamo_id>', methods=['POST'])
@csrf.exempt
def enviar_pagare_email(prestamo_id):
    """Enviar pagaré en PDF por email"""
    try:
        usuario_actual = db.obtener_usuario(session['user_id'], session['user_id'], False)
        es_admin = usuario_actual.rol == 'admin' if usuario_actual else False
        
        prestamo = prestamo_service.obtener_prestamo(prestamo_id, session['user_id'], es_admin)
        if not prestamo:
            return jsonify({'success': False, 'error': 'Préstamo no encontrado'})
        
        cliente = cliente_service.obtener_cliente(prestamo.cliente_id, session['user_id'], es_admin)
        if not cliente:
            return jsonify({'success': False, 'error': 'Cliente no encontrado'})
        
        # Verificar si el cliente tiene email
        if not cliente.email:
            return jsonify({'success': False, 'error': 'El cliente no tiene email registrado'})
        
        # Generar PDF del pagaré
        import os
        from datetime import datetime
        
        # Crear directorio de PDFs si no existe
        pdfs_dir = 'static/pdfs'
        os.makedirs(pdfs_dir, exist_ok=True)
        
        # Generar nombre del archivo PDF
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        nombre_pdf = f"pagare_prestamo_{prestamo_id}_{timestamp}.pdf"
        ruta_pdf = os.path.join(pdfs_dir, nombre_pdf)
        
        # Buscar si existe una firma digital
        firmas_dir = 'static/firmas'
        firma_encontrada = None
        
        if os.path.exists(firmas_dir):
            for archivo in os.listdir(firmas_dir):
                if archivo.startswith(f"firma_prestamo_{prestamo_id}_"):
                    firma_encontrada = os.path.join(firmas_dir, archivo)
                    break
        
        # Generar PDF
        pdf_generator = PagarePDFGenerator()
        
        if firma_encontrada:
            success, message = pdf_generator.generar_pagare_con_firma_pdf(
                prestamo, cliente, firma_encontrada, ruta_pdf
            )
        else:
            success, message = pdf_generator.generar_pagare_pdf(
                prestamo, cliente, ruta_pdf
            )
        
        if not success:
            return jsonify({'success': False, 'error': f'Error al generar PDF: {message}'})
        
        # Implementar envío real por email usando Gmail SMTP
        try:
            import smtplib
            from email.mime.multipart import MIMEMultipart
            from email.mime.text import MIMEText
            from email.mime.base import MIMEBase
            from email import encoders
            
            # Configuración de Gmail (requiere configuración previa)
            # Para usar Gmail, necesitas:
            # 1. Activar verificación en 2 pasos
            # 2. Generar contraseña de aplicación
            # 3. Configurar variables de entorno
            
            # Leer configuración desde variables de entorno
            import os
            from dotenv import load_dotenv
            load_dotenv()
            
            gmail_user = os.getenv('GMAIL_USER')
            gmail_password = os.getenv('GMAIL_APP_PASSWORD')
            
            if not gmail_user or not gmail_password:
                return jsonify({
                    'success': False, 
                    'error': 'Configuración de email no encontrada. Contacta al administrador.',
                    'pdf_generado': nombre_pdf,
                    'nota': 'PDF generado pero email no configurado'
                })
            
            # Crear mensaje
            msg = MIMEMultipart()
            msg['From'] = gmail_user
            msg['To'] = cliente.email
            msg['Subject'] = f'Pagaré - Préstamo #{prestamo.id} - {cliente.nombre} {cliente.apellido}'
            
            # Cuerpo del email
            body = f"""
            Estimado/a {cliente.nombre} {cliente.apellido},
            
            Se ha generado el pagaré para su préstamo #{prestamo.id}.
            
            DETALLES DEL PRÉSTAMO:
            - Monto: ${prestamo.monto:.2f}
            - Plazo: {prestamo.plazo_dias} días
            - Cuota Diaria: ${prestamo.calcular_cuota_diaria():.2f}
            - Total a Pagar: ${prestamo.calcular_monto_total():.2f}
            
            El archivo PDF del pagaré se encuentra adjunto a este correo.
            
            Atentamente,
            Sistema de Préstamos
            """
            
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            # Adjuntar PDF
            with open(ruta_pdf, 'rb') as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
            
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename= {nombre_pdf}'
            )
            msg.attach(part)
            
            # Enviar email
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(gmail_user, gmail_password)
            text = msg.as_string()
            server.sendmail(gmail_user, cliente.email, text)
            server.quit()
            
            return jsonify({
                'success': True,
                'message': 'Pagaré en PDF generado y enviado por email exitosamente',
                'email': cliente.email,
                'pdf_generado': nombre_pdf,
                'tiene_firma': firma_encontrada is not None
            })
            
        except Exception as email_error:
            # Si falla el email, devolver el PDF generado pero informar el error
            return jsonify({
                'success': False,
                'error': f'Error al enviar email: {str(email_error)}',
                'pdf_generado': nombre_pdf,
                'nota': 'PDF generado pero email falló. Contacta al administrador.'
            })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/configuracion')
@permiso_requerido('usuarios.ver')
def configuracion_sistema():
    """Página de configuración del sistema (solo para administradores)"""
    try:
        usuario_actual = db.obtener_usuario(session['user_id'], session['user_id'], False)
        es_admin = usuario_actual.rol == 'admin' if usuario_actual else False
        
        if not es_admin:
            flash('Solo los administradores pueden acceder a la configuración del sistema', 'error')
            return redirect(url_for('index'))
        
        config = configuracion_service.obtener_configuracion()
        return render_template('configuracion.html', config=config, usuario=usuario_actual)
        
    except Exception as e:
        flash(f'Error al cargar configuración: {e}', 'error')
        return redirect(url_for('index'))

@app.route('/api/configuracion/cambiar-nombre', methods=['POST'])
@permiso_requerido('usuarios.ver')
@csrf.exempt
def cambiar_nombre_sistema():
    """API para cambiar el nombre del sistema"""
    try:
        usuario_actual = db.obtener_usuario(session['user_id'], session['user_id'], False)
        es_admin = usuario_actual.rol == 'admin' if usuario_actual else False
        
        if not es_admin:
            return jsonify({'success': False, 'error': 'Solo los administradores pueden cambiar la configuración'})
        
        data = request.get_json()
        nuevo_nombre = data.get('nuevo_nombre', '').strip()
        
        if not nuevo_nombre:
            return jsonify({'success': False, 'error': 'El nombre del sistema no puede estar vacío'})
        
        if len(nuevo_nombre) > 100:
            return jsonify({'success': False, 'error': 'El nombre del sistema es demasiado largo (máximo 100 caracteres)'})
        
        if configuracion_service.cambiar_nombre_sistema(nuevo_nombre):
            return jsonify({
                'success': True, 
                'message': f'Nombre del sistema cambiado a: {nuevo_nombre}',
                'nuevo_nombre': nuevo_nombre
            })
        else:
            return jsonify({'success': False, 'error': 'Error al actualizar la configuración'})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/prestamos/<int:prestamo_id>/descargar-pdf')
@permiso_requerido('prestamos.ver')
def descargar_pagare_pdf(prestamo_id):
    """Descargar pagaré en formato PDF"""
    try:
        usuario_actual = db.obtener_usuario(session['user_id'], session['user_id'], False)
        es_admin = usuario_actual.rol == 'admin' if usuario_actual else False
        
        prestamo = prestamo_service.obtener_prestamo(prestamo_id, session['user_id'], es_admin)
        if not prestamo:
            flash('Préstamo no encontrado o no tienes permisos para acceder a él', 'error')
            return redirect(url_for('prestamos'))
        
        cliente = cliente_service.obtener_cliente(prestamo.cliente_id, session['user_id'], es_admin)
        if not cliente:
            flash('Cliente no encontrado o no tienes permisos para acceder a él', 'error')
            return redirect(url_for('prestamos'))
        
        # Buscar si existe una firma digital
        import os
        firmas_dir = 'static/firmas'
        firma_encontrada = None
        
        if os.path.exists(firmas_dir):
            for archivo in os.listdir(firmas_dir):
                if archivo.startswith(f"firma_prestamo_{prestamo_id}_"):
                    firma_encontrada = os.path.join(firmas_dir, archivo)
                    break
        
        # Generar nombre del archivo PDF
        from datetime import datetime
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        nombre_pdf = f"pagare_prestamo_{prestamo_id}_{timestamp}.pdf"
        ruta_pdf = os.path.join('static/pdfs', nombre_pdf)
        
        # Crear instancia del generador de PDF
        pdf_generator = PagarePDFGenerator()
        
        # Generar PDF con o sin firma
        if firma_encontrada:
            success, message = pdf_generator.generar_pagare_con_firma_pdf(
                prestamo, cliente, firma_encontrada, ruta_pdf
            )
        else:
            success, message = pdf_generator.generar_pagare_pdf(
                prestamo, cliente, ruta_pdf
            )
        
        if success:
            # Retornar el archivo PDF para descarga
            from flask import send_file
            return send_file(
                ruta_pdf,
                as_attachment=True,
                download_name=nombre_pdf,
                mimetype='application/pdf'
            )
        else:
            flash(f'Error al generar PDF: {message}', 'error')
            return redirect(url_for('prestamos'))
            
    except Exception as e:
        flash(f'Error al generar PDF: {e}', 'error')
        return redirect(url_for('prestamos'))

# Crear directorio de templates si no existe
os.makedirs('templates', exist_ok=True)
os.makedirs('static/css', exist_ok=True)
os.makedirs('static/js', exist_ok=True)

# Rutas de autenticación
@app.route('/login', methods=['GET', 'POST'])
def login():
    """Página de login"""
    if 'user_id' in session:
        return redirect(url_for('index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        try:
            usuario = db.verificar_login(form.username.data, form.password.data)
            if usuario:
                session.permanent = True
                session['user_id'] = usuario.id
                session['username'] = usuario.username
                session['nombre'] = usuario.nombre
                session['rol'] = usuario.rol
                session['permisos'] = usuario.permisos
                # Agregar configuración del sistema a la sesión
                session['configuracion'] = configuracion_service.obtener_configuracion()
                flash(f'¡Bienvenido, {usuario.nombre}! (Rol: {usuario.rol})', 'success')
                return redirect(url_for('index'))
            else:
                flash('Usuario o contraseña incorrectos', 'error')
        except Exception as e:
            flash(f'Error en el login: {e}', 'error')
    
    return render_template('login.html', form=form)

@app.route('/olvide-password', methods=['GET', 'POST'])
def olvide_password():
    """Página para recuperar contraseña"""
    if 'user_id' in session:
        return redirect(url_for('index'))
    
    form = OlvidePasswordForm()
    if form.validate_on_submit():
        email = form.email.data
        
        # Buscar usuario por email
        usuario = db.obtener_usuario_por_email(email)
        if usuario:
            # Generar código de recuperación
            codigo = generar_codigo_recuperacion(usuario.id)
            
            # Enviar email con código
            if enviar_email_codigo(usuario.email, usuario.username, codigo):
                flash('Se ha enviado un código de 6 dígitos a tu correo electrónico', 'success')
                return redirect(url_for('verificar_codigo'))
            else:
                flash('Error al enviar el email. Intenta nuevamente.', 'error')
        else:
            # Por seguridad, no revelar si el email existe o no
            flash('Si el email existe en nuestro sistema, recibirás un código de recuperación', 'info')
        
        return redirect(url_for('login'))
    
    return render_template('olvide_password.html', form=form)

@app.route('/verificar-codigo', methods=['GET', 'POST'])
def verificar_codigo():
    """Página para verificar código de recuperación"""
    if 'user_id' in session:
        return redirect(url_for('index'))
    
    form = VerificarCodigoForm()
    if form.validate_on_submit():
        codigo = form.codigo.data
        
        # Verificar código
        usuario_id = verificar_codigo_recuperacion(codigo)
        if usuario_id:
            # Redirigir a restablecer contraseña con el usuario_id en sesión temporal
            session['temp_user_id'] = usuario_id
            return redirect(url_for('restablecer_password'))
        else:
            flash('El código es incorrecto o ha expirado', 'error')
    
    return render_template('verificar_codigo.html', form=form)

@app.route('/restablecer-password', methods=['GET', 'POST'])
def restablecer_password():
    """Página para restablecer contraseña"""
    if 'user_id' in session:
        return redirect(url_for('index'))
    
    # Verificar sesión temporal
    if 'temp_user_id' not in session:
        flash('Debes verificar el código primero', 'error')
        return redirect(url_for('olvide_password'))
    
    usuario_id = session['temp_user_id']
    
    form = RestablecerPasswordForm()
    if form.validate_on_submit():
        nueva_password = form.password.data
        
        # Cambiar contraseña del usuario
        if db.cambiar_password_usuario(usuario_id, nueva_password):
            # Limpiar sesión temporal
            session.pop('temp_user_id', None)
            flash('Tu contraseña ha sido restablecida exitosamente', 'success')
            return redirect(url_for('login'))
        else:
            flash('Error al restablecer la contraseña', 'error')
    
    return render_template('restablecer_password.html', form=form)

@app.route('/logout')
def logout():
    """Cerrar sesión"""
    session.clear()
    flash('Sesión cerrada exitosamente', 'info')
    return redirect(url_for('login'))

@app.route('/cambiar-password', methods=['GET', 'POST'])
@login_required
def cambiar_password():
    """Cambiar contraseña del usuario actual"""
    form = CambiarPasswordForm()
    if form.validate_on_submit():
        try:
            usuario = db.obtener_usuario(session['user_id'], session['user_id'], False)
            if usuario and usuario.verificar_password(form.password_actual.data):
                if form.password_nueva.data == form.password_confirmar.data:
                    usuario.password_hash = Usuario.hash_password(form.password_nueva.data)
                    if db.actualizar_usuario(usuario, session['user_id'], False):
                        flash('Contraseña cambiada exitosamente', 'success')
                        return redirect(url_for('index'))
                    else:
                        flash('Error al actualizar la contraseña', 'error')
                else:
                    flash('Las contraseñas nuevas no coinciden', 'error')
            else:
                flash('Contraseña actual incorrecta', 'error')
        except Exception as e:
            flash(f'Error al cambiar contraseña: {e}', 'error')
    
    return render_template('cambiar_password.html', form=form)

# Gestión de Usuarios (Solo para administradores)
@app.route('/usuarios')
@permiso_requerido('usuarios.ver')
def usuarios():
    """Lista de usuarios del sistema"""
    try:
        usuario_actual = db.obtener_usuario(session['user_id'], session['user_id'], False)
        es_admin = usuario_actual.rol == 'admin' if usuario_actual else False
        
        usuarios_list = db.listar_usuarios(session['user_id'], es_admin)
        return render_template('usuarios.html', usuarios=usuarios_list, usuario=usuario_actual)
    except Exception as e:
        flash(f'Error al cargar usuarios: {e}', 'error')
        return render_template('usuarios.html', usuarios=[], usuario=None)

@app.route('/usuarios/nuevo', methods=['GET', 'POST'])
@permiso_requerido('usuarios.crear')
def nuevo_usuario():
    """Crear nuevo usuario (solo administradores)"""
    try:
        usuario_actual = db.obtener_usuario(session['user_id'], session['user_id'], False)
        if not usuario_actual or not usuario_actual.puede_crear_usuarios():
            flash('Solo los administradores pueden crear usuarios', 'error')
            return redirect(url_for('usuarios'))
        
        if request.method == 'POST':
            try:
                # Crear usuario con hash de contraseña
                usuario = Usuario(
                    id=0,  # Se asignará automáticamente
                    username=request.form['username'],
                    password_hash=Usuario.hash_password(request.form['password']),
                    nombre=request.form['nombre'],
                    email=request.form.get('email', ''),
                    rol=request.form['rol']
                )
                
                usuario_creado = db.agregar_usuario(usuario, session['user_id'])
                if usuario_creado:
                    flash(f'Usuario {usuario_creado.nombre} creado exitosamente', 'success')
                    return redirect(url_for('usuarios'))
                else:
                    flash('Error al crear usuario', 'error')
            except Exception as e:
                flash(f'Error al crear usuario: {e}', 'error')
        
        roles_disponibles = ['supervisor', 'operador', 'consultor']  # No permitir crear admins
        return render_template('nuevo_usuario.html', roles=roles_disponibles)
        
    except Exception as e:
        flash(f'Error: {e}', 'error')
        return redirect(url_for('usuarios'))

@app.route('/usuarios/<int:usuario_id>/editar', methods=['GET', 'POST'])
@permiso_requerido('usuarios.editar')
def editar_usuario(usuario_id):
    """Editar usuario existente"""
    try:
        usuario_actual = db.obtener_usuario(session['user_id'], session['user_id'], False)
        es_admin = usuario_actual.rol == 'admin' if usuario_actual else False
        
        usuario = db.obtener_usuario(usuario_id, session['user_id'], es_admin)
        if not usuario:
            flash('Usuario no encontrado o no tienes permisos para acceder a él', 'error')
            return redirect(url_for('usuarios'))
        
        if request.method == 'POST':
            # Actualizar datos del usuario
            usuario.nombre = request.form['nombre']
            usuario.email = request.form.get('email', '')
            usuario.rol = request.form['rol']
            usuario.activo = 'activo' in request.form
            
            # Si se proporciona nueva contraseña, actualizarla
            if request.form.get('password'):
                usuario.password_hash = Usuario.hash_password(request.form['password'])
            
            if db.actualizar_usuario(usuario, session['user_id'], es_admin):
                flash('Usuario actualizado exitosamente', 'success')
                return redirect(url_for('usuarios'))
            else:
                flash('Error al actualizar usuario o no tienes permisos', 'error')
        
        roles_disponibles = ['supervisor', 'operador', 'consultor']  # No permitir cambiar a admin
        return render_template('editar_usuario.html', usuario=usuario, roles=roles_disponibles)
        
    except Exception as e:
        flash(f'Error: {e}', 'error')
        return redirect(url_for('usuarios'))

@app.route('/usuarios/<int:usuario_id>/eliminar', methods=['POST'])
@permiso_requerido('usuarios.eliminar')
def eliminar_usuario(usuario_id):
    """Eliminar usuario (marcar como inactivo)"""
    try:
        usuario_actual = db.obtener_usuario(session['user_id'], session['user_id'], False)
        es_admin = usuario_actual.rol == 'admin' if usuario_actual else False
        
        if usuario_id == session.get('user_id'):
            flash('No puede eliminar su propia cuenta', 'error')
        elif db.eliminar_usuario(usuario_id, session['user_id'], es_admin):
            flash('Usuario eliminado exitosamente', 'success')
        else:
            flash('Error al eliminar usuario o no tienes permisos', 'error')
    except Exception as e:
        flash(f'Error: {e}', 'error')
    
    return redirect(url_for('usuarios'))

@app.route('/usuarios/<int:usuario_id>/eliminar-completo', methods=['POST'])
@permiso_requerido('usuarios.eliminar')
def eliminar_usuario_completo(usuario_id):
    """Eliminar usuario completamente (incluyendo todos sus datos)"""
    try:
        usuario_actual = db.obtener_usuario(session['user_id'], session['user_id'], False)
        es_admin = usuario_actual.rol == 'admin' if usuario_actual else False
        
        if usuario_id == session.get('user_id'):
            flash('No puede eliminar su propia cuenta', 'error')
        elif db.eliminar_usuario_completo(usuario_id, session['user_id'], es_admin):
            flash('Usuario eliminado completamente exitosamente', 'success')
        else:
            flash('Error al eliminar usuario o no tienes permisos', 'error')
    except Exception as e:
        flash(f'Error: {e}', 'error')
    
    return redirect(url_for('usuarios'))

# Funciones auxiliares para recuperación de contraseña
def generar_codigo_recuperacion(usuario_id):
    """Genera un código de 6 dígitos para recuperación de contraseña"""
    codigo = ''.join([str(secrets.randbelow(10)) for _ in range(6)])
    RECOVERY_CODES[codigo] = {
        'usuario_id': usuario_id,
        'timestamp': datetime.now(),
        'usado': False
    }
    return codigo

def verificar_codigo_recuperacion(codigo):
    """Verifica si un código de recuperación es válido"""
    if codigo not in RECOVERY_CODES:
        return None
    
    codigo_data = RECOVERY_CODES[codigo]
    
    # Verificar si el código ha expirado (10 minutos)
    if datetime.now() - codigo_data['timestamp'] > timedelta(minutes=10):
        del RECOVERY_CODES[codigo]
        return None
    
    # Verificar si ya fue usado
    if codigo_data['usado']:
        del RECOVERY_CODES[codigo]
        return None
    
    # Marcar como usado
    codigo_data['usado'] = True
    return codigo_data['usuario_id']

def enviar_email_codigo(email, username, codigo):
    """Envía email con código de recuperación de contraseña"""
    try:
        # Crear mensaje
        msg = MIMEMultipart()
        msg['From'] = SMTP_CONFIG['username']
        msg['To'] = email
        msg['Subject'] = 'Código de Recuperación - Sistema de Préstamos'
        
        # Cuerpo del email
        body = f"""
        Hola {username},
        
        Has solicitado restablecer tu contraseña en el Sistema de Préstamos.
        
        Tu código de verificación es: {codigo}
        
        Este código es válido por 10 minutos.
        
        Si no solicitaste este cambio, puedes ignorar este email.
        
        Saludos,
        Sistema de Préstamos
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Conectar al servidor SMTP
        server = smtplib.SMTP(SMTP_CONFIG['server'], SMTP_CONFIG['port'])
        server.starttls()
        server.login(SMTP_CONFIG['username'], SMTP_CONFIG['password'])
        
        # Enviar email
        text = msg.as_string()
        server.sendmail(SMTP_CONFIG['username'], email, text)
        server.quit()
        
        return True
        
    except Exception as e:
        print(f"Error al enviar email: {e}")
        return False

if __name__ == '__main__':
    print("🚀 Iniciando Sistema de Préstamos Web...")
    print("📱 Abre tu navegador en: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
