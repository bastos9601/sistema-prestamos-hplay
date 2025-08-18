#!/usr/bin/env python3
"""
Sistema de Préstamos de Dinero - Aplicación Web
===============================================

Una aplicación web moderna y responsive para gestionar préstamos de dinero.
"""

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_wtf.csrf import CSRFProtect
from wtforms import StringField, DecimalField, IntegerField, SelectField, TextAreaField
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, Email, NumberRange
from decimal import Decimal, InvalidOperation
from datetime import date
import os
from functools import wraps

# Importar módulos del sistema
from database import Database
from services import ClienteService, PrestamoService, PagoService, ReporteService
from models import Usuario
from forms import LoginForm, CambiarPasswordForm

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
            usuario = db.obtener_usuario(session['user_id'])
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
                return redirect(url_for('login'))
            
            # Obtener usuario actual
            usuario = db.obtener_usuario(session['user_id'])
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
        stats = reporte_service.generar_reporte_general()
        return render_template('index.html', stats=stats)
    except Exception as e:
        flash(f'Error al cargar estadísticas: {e}', 'error')
        return render_template('index.html', stats={})

@app.route('/clientes')
@permiso_requerido('clientes.ver')
def clientes():
    """Lista de clientes"""
    try:
        clientes_list = cliente_service.listar_clientes()
        return render_template('clientes.html', clientes=clientes_list)
    except Exception as e:
        flash(f'Error al cargar clientes: {e}', 'error')
        return render_template('clientes.html', clientes=[])

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
                    email=form.email.data
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
        cliente = cliente_service.obtener_cliente(cliente_id)
        if not cliente:
            flash('Cliente no encontrado', 'error')
            return redirect(url_for('clientes'))
        
        if request.method == 'POST':
            form = ClienteForm(request.form, obj=cliente)
            if form.validate():
                if cliente_service.actualizar_cliente(
                    cliente_id,
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
        if cliente_service.eliminar_cliente(cliente_id):
            flash('Cliente eliminado completamente de la base de datos', 'success')
        else:
            flash('Error al eliminar cliente', 'error')
    except Exception as e:
        flash(f'Error: {e}', 'error')
    
    return redirect(url_for('clientes'))

@app.route('/prestamos')
@permiso_requerido('prestamos.ver')
def prestamos():
    """Lista de préstamos"""
    try:
        prestamos_list = prestamo_service.listar_prestamos_activos()
        
        # Enriquecer cada préstamo con información del cliente y pagos
        prestamos_enriquecidos = []
        for prestamo in prestamos_list:
            cliente = cliente_service.obtener_cliente(prestamo.cliente_id)
            # Obtener pagos del préstamo como objetos Pago
            pagos = pago_service.listar_pagos_prestamo(prestamo.id)
            prestamos_enriquecidos.append({
                'prestamo': prestamo,
                'cliente': cliente,
                'pagos': pagos
            })
        
        return render_template('prestamos.html', prestamos=prestamos_enriquecidos)
    except Exception as e:
        flash(f'Error al cargar préstamos: {e}', 'error')
        return render_template('prestamos.html', prestamos=[])

@app.route('/prestamos/nuevo', methods=['GET', 'POST'])
@permiso_requerido('prestamos.crear')
def nuevo_prestamo():
    """Crear nuevo préstamo"""
    # Obtener lista de clientes para el formulario
    clientes_list = cliente_service.listar_clientes()
    
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
                    tipo_interes=form.tipo_interes.data
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
    
    return render_template('nuevo_prestamo.html', form=form, clientes_list=clientes_list)

@app.route('/prestamos/<int:prestamo_id>')
@permiso_requerido('prestamos.ver')
def ver_prestamo(prestamo_id):
    """Ver detalles de un préstamo"""
    try:
        resumen = prestamo_service.obtener_resumen_prestamo(prestamo_id)
        return render_template('ver_prestamo.html', resumen=resumen)
    except Exception as e:
        flash(f'Error al obtener préstamo: {e}', 'error')
        return redirect(url_for('prestamos'))

@app.route('/prestamos/<int:prestamo_id>/eliminar', methods=['POST'])
@permiso_requerido('prestamos.eliminar')
def eliminar_prestamo(prestamo_id):
    """Eliminar un préstamo (con o sin pagos)"""
    try:
        # Verificar que el préstamo existe
        prestamo = prestamo_service.obtener_prestamo(prestamo_id)
        if not prestamo:
            flash('Préstamo no encontrado', 'error')
            return redirect(url_for('prestamos'))
        
        # Verificar si tiene pagos para mostrar advertencia
        tiene_pagos = len(prestamo.pagos) > 0
        monto_total_pagos = sum(pago.monto for pago in prestamo.pagos)
        
        # Eliminar el préstamo (ahora se puede eliminar cualquier préstamo)
        if prestamo_service.eliminar_prestamo(prestamo_id):
            if tiene_pagos:
                flash(f'Préstamo eliminado exitosamente. Se eliminaron {len(prestamo.pagos)} pagos por un total de ${monto_total_pagos:.2f}', 'warning')
            else:
                flash('Préstamo eliminado exitosamente', 'success')
        else:
            flash('Error al eliminar préstamo', 'error')
            
    except Exception as e:
        flash(f'Error al eliminar préstamo: {e}', 'error')
    
    return redirect(url_for('prestamos'))

@app.route('/pagos')
@permiso_requerido('pagos.ver')
def pagos():
    """Lista de pagos"""
    try:
        # Obtener todos los pagos del sistema con información del cliente
        pagos_list = []
        prestamos = prestamo_service.listar_prestamos_activos()
        for prestamo in prestamos:
            # Usar listar_pagos_prestamo que devuelve objetos Pago completos
            pagos_prestamo = pago_service.listar_pagos_prestamo(prestamo.id)
            cliente = cliente_service.obtener_cliente(prestamo.cliente_id)
            
            # Enriquecer cada pago con información del préstamo y cliente
            for pago in pagos_prestamo:
                pagos_list.append({
                    'pago': pago,
                    'prestamo': prestamo,
                    'cliente': cliente
                })
        
        return render_template('pagos.html', pagos=pagos_list)
    except Exception as e:
        flash(f'Error al cargar pagos: {e}', 'error')
        return render_template('pagos.html', pagos=[])

@app.route('/pagos/nuevo', methods=['GET', 'POST'])
@permiso_requerido('pagos.crear')
def nuevo_pago():
    """Registrar nuevo pago"""
    if request.method == 'POST':
        form = PagoForm(request.form)
        if form.validate():
            try:
                pago = pago_service.registrar_pago(
                    prestamo_id=form.prestamo_id.data,
                    monto=form.monto.data,
                    concepto=form.concepto.data or "Pago de cuota"
                )
                flash(f'Pago registrado exitosamente con ID: {pago.id}', 'success')
                return redirect(url_for('pagos'))
            except Exception as e:
                flash(f'Error al registrar pago: {e}', 'error')
    else:
        form = PagoForm()
    
    # Obtener lista de préstamos activos con información del cliente
    prestamos_list = prestamo_service.listar_prestamos_activos()
    
    # Enriquecer cada préstamo con información del cliente
    prestamos_enriquecidos = []
    for prestamo in prestamos_list:
        cliente = cliente_service.obtener_cliente(prestamo.cliente_id)
        prestamos_enriquecidos.append({
            'prestamo': prestamo,
            'cliente': cliente
        })
    
    return render_template('nuevo_pago.html', form=form, prestamos=prestamos_enriquecidos)

@app.route('/pagos/<int:pago_id>/eliminar', methods=['POST'])
@permiso_requerido('pagos.eliminar')
def eliminar_pago(pago_id):
    """Eliminar un pago específico"""
    try:
        if pago_service.eliminar_pago(pago_id):
            flash('Pago eliminado exitosamente', 'success')
        else:
            flash('Error al eliminar pago', 'error')
    except Exception as e:
        flash(f'Error al eliminar pago: {e}', 'error')
    
    return redirect(url_for('pagos'))

@app.route('/reportes')
@permiso_requerido('reportes.ver')
def reportes():
    """Página de reportes"""
    return render_template('reportes.html')

@app.route('/api/reporte-general')
def api_reporte_general():
    """API para obtener reporte general"""
    try:
        stats = reporte_service.generar_reporte_general()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/reporte-cliente/<int:cliente_id>')
def api_reporte_cliente(cliente_id):
    """API para obtener reporte de un cliente"""
    try:
        reporte = reporte_service.generar_reporte_cliente(cliente_id)
        return jsonify(reporte)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/prestamos-activos')
def api_prestamos_activos():
    """API para obtener préstamos activos"""
    try:
        reporte = reporte_service.generar_reporte_prestamos_activos()
        return jsonify(reporte)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/buscar-cliente')
def api_buscar_cliente():
    """API para buscar clientes"""
    termino = request.args.get('q', '')
    if not termino:
        return jsonify([])
    
    try:
        clientes = cliente_service.buscar_cliente(termino)
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
                flash(f'¡Bienvenido, {usuario.nombre}! (Rol: {usuario.rol})', 'success')
                return redirect(url_for('index'))
            else:
                flash('Usuario o contraseña incorrectos', 'error')
        except Exception as e:
            flash(f'Error en el login: {e}', 'error')
    
    return render_template('login.html', form=form)

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
            usuario = db.obtener_usuario(session['user_id'])
            if usuario and usuario.verificar_password(form.password_actual.data):
                if form.password_nueva.data == form.password_confirmar.data:
                    usuario.password_hash = Usuario.hash_password(form.password_nueva.data)
                    if db.actualizar_usuario(usuario):
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
        usuarios_list = db.listar_usuarios()
        return render_template('usuarios.html', usuarios=usuarios_list)
    except Exception as e:
        flash(f'Error al cargar usuarios: {e}', 'error')
        return render_template('usuarios.html', usuarios=[])

@app.route('/usuarios/nuevo', methods=['GET', 'POST'])
@permiso_requerido('usuarios.crear')
def nuevo_usuario():
    """Crear nuevo usuario"""
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
            
            usuario_creado = db.agregar_usuario(usuario)
            if usuario_creado:
                flash(f'Usuario {usuario_creado.nombre} creado exitosamente', 'success')
                return redirect(url_for('usuarios'))
            else:
                flash('Error al crear usuario', 'error')
        except Exception as e:
            flash(f'Error al crear usuario: {e}', 'error')
    
    roles_disponibles = ['admin', 'supervisor', 'operador', 'consultor']
    return render_template('nuevo_usuario.html', roles=roles_disponibles)

@app.route('/usuarios/<int:usuario_id>/editar', methods=['GET', 'POST'])
@permiso_requerido('usuarios.editar')
def editar_usuario(usuario_id):
    """Editar usuario existente"""
    try:
        usuario = db.obtener_usuario(usuario_id)
        if not usuario:
            flash('Usuario no encontrado', 'error')
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
            
            if db.actualizar_usuario(usuario):
                flash('Usuario actualizado exitosamente', 'success')
                return redirect(url_for('usuarios'))
            else:
                flash('Error al actualizar usuario', 'error')
        
        roles_disponibles = ['admin', 'supervisor', 'operador', 'consultor']
        return render_template('editar_usuario.html', usuario=usuario, roles=roles_disponibles)
        
    except Exception as e:
        flash(f'Error: {e}', 'error')
        return redirect(url_for('usuarios'))

@app.route('/usuarios/<int:usuario_id>/eliminar', methods=['POST'])
@permiso_requerido('usuarios.eliminar')
def eliminar_usuario(usuario_id):
    """Eliminar usuario (marcar como inactivo)"""
    try:
        if usuario_id == session.get('user_id'):
            flash('No puede eliminar su propia cuenta', 'error')
        elif db.eliminar_usuario(usuario_id):
            flash('Usuario eliminado exitosamente', 'success')
        else:
            flash('Error al eliminar usuario', 'error')
    except Exception as e:
        flash(f'Error: {e}', 'error')
    
    return redirect(url_for('usuarios'))
    if form.validate_on_submit():
        try:
            usuario = db.obtener_usuario(session['user_id'])
            if usuario and usuario.verificar_password(form.password_actual.data):
                if form.password_nueva.data == form.password_confirmar.data:
                    usuario.password_hash = Usuario.hash_password(form.password_nueva.data)
                    if db.actualizar_usuario(usuario):
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

if __name__ == '__main__':
    print("🚀 Iniciando Sistema de Préstamos Web...")
    print("📱 Abre tu navegador en: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
