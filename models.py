from datetime import datetime, date
from decimal import Decimal
from typing import List, Optional
import json
import os

class Cliente:
    def __init__(self, id: int, nombre: str, apellido: str, dni: str, telefono: str, email: str = "", usuario_id: int = None):
        self.id = id
        self.nombre = nombre
        self.apellido = apellido
        self.dni = dni
        self.telefono = telefono
        self.email = email
        self.usuario_id = usuario_id  # ID del usuario que creó el cliente
        self.usuario_creador_id = usuario_id  # Alias para compatibilidad
        self.fecha_registro = datetime.now()
        self.activo = True
    
    def __str__(self):
        return f"{self.nombre} {self.apellido} (DNI: {self.dni})"
    
    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'apellido': self.apellido,
            'dni': self.dni,
            'telefono': self.telefono,
            'email': self.email,
            'usuario_id': self.usuario_id,
            'usuario_creador_id': self.usuario_creador_id,
            'fecha_registro': self.fecha_registro.isoformat(),
            'activo': self.activo
        }
    
    @classmethod
    def from_dict(cls, data):
        cliente = cls(
            id=data['id'],
            nombre=data['nombre'],
            apellido=data['apellido'],
            dni=data['dni'],
            telefono=data['telefono'],
            email=data.get('email', ''),
            usuario_id=data.get('usuario_id')
        )
        cliente.fecha_registro = datetime.fromisoformat(data['fecha_registro'])
        cliente.activo = data.get('activo', True)
        
        # Agregar información del usuario creador si está disponible
        if 'usuario_creador' in data:
            cliente.usuario_creador = data['usuario_creador']
        
        return cliente

class Prestamo:
    def __init__(self, id: int, cliente_id: int, monto: Decimal, tasa_interes: Decimal, 
                 plazo_dias: int, tipo_interes: str = "gota_a_gota", fecha_inicio: Optional[date] = None,
                 descripcion: str = "", usuario_id: int = None):
        self.id = id
        self.cliente_id = cliente_id
        self.monto = monto
        self.tasa_interes = tasa_interes  # Tasa anual en porcentaje
        self.plazo_dias = plazo_dias
        self.tipo_interes = tipo_interes  # "simple", "compuesto" o "gota_a_gota"
        self.fecha_inicio = fecha_inicio or date.today()
        self.fecha_creacion = datetime.now()
        self.estado = "activo"  # activo, pagado, vencido, cancelado
        self.descripcion = descripcion  # Descripción del préstamo
        self.usuario_id = usuario_id  # ID del usuario que creó el préstamo
        self.usuario_creador_id = usuario_id  # Alias para compatibilidad
        self.pagos: List[Pago] = []
    
    def calcular_interes_total(self) -> Decimal:
        """Calcula el interés total del préstamo"""
        if self.tipo_interes == "simple":
            # Interés simple: I = P * r * t
            tasa_diaria = self.tasa_interes / 100 / 365
            return self.monto * tasa_diaria * self.plazo_dias
        elif self.tipo_interes == "compuesto":
            # Interés compuesto: A = P * (1 + r)^t
            tasa_diaria = self.tasa_interes / 100 / 365
            monto_final = self.monto * ((1 + tasa_diaria) ** self.plazo_dias)
            return monto_final - self.monto
        elif self.tipo_interes == "gota_a_gota":
            # Interés gota a gota: se paga diariamente, capital al final
            tasa_diaria = self.tasa_interes / 100 / 365
            return self.monto * tasa_diaria * self.plazo_dias
        else:
            # Por defecto, interés simple
            tasa_diaria = self.tasa_interes / 100 / 365
            return self.monto * tasa_diaria * self.plazo_dias
    
    def calcular_monto_total(self) -> Decimal:
        """Calcula el monto total a pagar (capital + intereses)"""
        return self.monto + self.calcular_interes_total()
    
    def calcular_cuota_diaria(self) -> Decimal:
        """Calcula la cuota diaria"""
        if self.tipo_interes == "gota_a_gota":
            # En gota a gota: solo se paga el interés diario
            tasa_diaria = self.tasa_interes / 100 / 365
            return self.monto * tasa_diaria
        else:
            # Para simple y compuesto: se divide el total entre los días
            monto_total = self.calcular_monto_total()
            return monto_total / self.plazo_dias
    
    def calcular_saldo_pendiente(self) -> Decimal:
        """Calcula el saldo pendiente del préstamo"""
        if self.tipo_interes == "gota_a_gota":
            # En gota a gota: se paga el capital al final
            # Los intereses se pagan diariamente
            # El saldo pendiente es el capital + intereses no pagados
            intereses_pendientes = self.calcular_intereses_pendientes()
            return self.monto + intereses_pendientes
        else:
            # Para simple y compuesto: se descuenta todo
            monto_total = self.calcular_monto_total()
            pagos_realizados = sum(pago.monto for pago in self.pagos)
            return monto_total - pagos_realizados
    
    def agregar_pago(self, pago: 'Pago'):
        """Agrega un pago al préstamo"""
        self.pagos.append(pago)
        
        # Calcular saldo después del pago
        if self.tipo_interes == "gota_a_gota":
            # Para gota a gota, el saldo es capital pendiente + intereses pendientes
            capital_pendiente = self.calcular_capital_pendiente()
            intereses_pendientes = self.calcular_intereses_pendientes()
            pago.saldo_despues = capital_pendiente + intereses_pendientes
        else:
            # Para otros tipos, el saldo es el total menos todos los pagos (incluyendo el pago actual)
            # Esto hace que sea consistente con calcular_saldo_pendiente()
            monto_total = self.calcular_monto_total()
            todos_los_pagos = sum(p.monto for p in self.pagos)  # Incluir el pago actual
            pago.saldo_despues = monto_total - todos_los_pagos
        
        # Verificar si el préstamo está pagado
        if self.calcular_saldo_pendiente() <= 0:
            self.estado = "pagado"
    
    def calcular_cuota_capital(self) -> Decimal:
        """Calcula la cuota de capital (solo para gota a gota)"""
        if self.tipo_interes == "gota_a_gota":
            return self.monto  # El capital se paga completo al final
        else:
            return Decimal('0')  # No aplica para otros tipos
    
    def calcular_intereses_pagados(self) -> Decimal:
        """Calcula el total de intereses pagados"""
        return sum(pago.monto for pago in self.pagos)
    
    def calcular_intereses_pendientes(self) -> Decimal:
        """Calcula los intereses pendientes de pago"""
        if self.tipo_interes == "gota_a_gota":
            intereses_total = self.calcular_interes_total()
            intereses_pagados = self.calcular_intereses_pagados()
            return max(Decimal('0'), intereses_total - intereses_pagados)
        else:
            return Decimal('0')  # Para otros tipos, los intereses se pagan con el capital
    
    def calcular_capital_pendiente(self) -> Decimal:
        """Calcula el capital pendiente de pago"""
        if self.tipo_interes == "gota_a_gota":
            # En gota a gota, el capital se paga al final
            # Pero si se han pagado intereses, se puede reducir proporcionalmente
            intereses_pagados = self.calcular_intereses_pagados()
            intereses_total = self.calcular_interes_total()
            
            if intereses_total > 0:
                # Calcular qué porcentaje de intereses se han pagado
                porcentaje_pagado = intereses_pagados / intereses_total
                # Reducir el capital proporcionalmente
                capital_reducido = self.monto * (1 - porcentaje_pagado)
                return max(Decimal('0'), capital_reducido)
            else:
                return self.monto
        else:
            # Para otros tipos, el capital se paga con los pagos
            monto_total = self.calcular_monto_total()
            pagos_realizados = sum(pago.monto for pago in self.pagos)
            return max(Decimal('0'), monto_total - pagos_realizados)
    
    def to_dict(self):
        return {
            'id': self.id,
            'cliente_id': self.cliente_id,
            'monto': float(self.monto),
            'tasa_interes': float(self.tasa_interes),
            'plazo_dias': self.plazo_dias,
            'tipo_interes': self.tipo_interes,
            'fecha_inicio': self.fecha_inicio.isoformat(),
            'fecha_creacion': self.fecha_creacion.isoformat(),
            'estado': self.estado,
            'descripcion': self.descripcion,
            'usuario_id': self.usuario_id,
            'usuario_creador_id': self.usuario_creador_id,
            'pagos': [pago.to_dict() for pago in self.pagos]
        }
    
    @classmethod
    def from_dict(cls, data):
        prestamo = cls(
            id=data['id'],
            cliente_id=data['cliente_id'],
            monto=Decimal(str(data['monto'])),
            tasa_interes=Decimal(str(data['tasa_interes'])),
            plazo_dias=data.get('plazo_dias', data.get('plazo_meses', 30)),  # Compatibilidad con datos antiguos
            tipo_interes=data['tipo_interes'],
            fecha_inicio=date.fromisoformat(data['fecha_inicio']),
            descripcion=data.get('descripcion', ''),
            usuario_id=data.get('usuario_id')
        )
        prestamo.fecha_creacion = datetime.fromisoformat(data['fecha_creacion'])
        prestamo.estado = data['estado']
        prestamo.pagos = [Pago.from_dict(pago_data) for pago_data in data.get('pagos', [])]
        
        # Agregar información del usuario creador si está disponible
        if 'usuario_creador' in data:
            prestamo.usuario_creador = data['usuario_creador']
        
        return prestamo

class Pago:
    def __init__(self, id: int, prestamo_id: int, monto: Decimal, fecha: Optional[datetime] = None, 
                 concepto: str = "Pago de cuota", usuario_id: int = None):
        self.id = id
        self.prestamo_id = prestamo_id
        self.monto = monto
        self.fecha = fecha or datetime.now()  # Ahora guarda fecha + hora
        self.concepto = concepto
        self.fecha_registro = datetime.now()
        self.saldo_despues = Decimal('0')  # Saldo después del pago
        self.usuario_id = usuario_id  # ID del usuario que creó el pago
        self.usuario_creador_id = usuario_id  # Alias para compatibilidad
    
    def to_dict(self):
        return {
            'id': self.id,
            'prestamo_id': self.prestamo_id,
            'monto': float(self.monto),
            'fecha': self.fecha.isoformat(),
            'concepto': self.concepto,
            'fecha_registro': self.fecha_registro.isoformat(),
            'saldo_despues': float(self.saldo_despues),
            'usuario_id': self.usuario_id,
            'usuario_creador_id': self.usuario_creador_id
        }
    
    @classmethod
    def from_dict(cls, data):
        pago = cls(
            id=data['id'],
            prestamo_id=data['prestamo_id'],
            monto=Decimal(str(data['monto'])),
            fecha=datetime.fromisoformat(data['fecha']),  # Ahora maneja datetime
            concepto=data['concepto'],
            usuario_id=data.get('usuario_id')
        )
        pago.fecha_registro = datetime.fromisoformat(data['fecha_registro'])
        pago.saldo_despues = Decimal(str(data.get('saldo_despues', 0)))
        
        # Agregar información del usuario creador si está disponible
        if 'usuario_creador' in data:
            pago.usuario_creador = data['usuario_creador']
        
        return pago

class Usuario:
    def __init__(self, id: int, username: str, password_hash: str, nombre: str, 
                 email: str = "", rol: str = "admin", activo: bool = True, permisos: list = None,
                 usuario_creador_id: int = None):
        self.id = id
        self.username = username
        self.password_hash = password_hash
        self.nombre = nombre
        self.email = email
        self.rol = rol  # admin, supervisor, operador, consultor
        self.activo = activo
        self.fecha_registro = datetime.now()
        self.ultimo_acceso = None
        self.usuario_creador_id = usuario_creador_id  # ID del usuario que lo creó
        self.permisos = permisos or self._get_permisos_por_rol(rol)
    
    def _get_permisos_por_rol(self, rol: str) -> list:
        """Define los permisos por defecto según el rol"""
        permisos_base = {
            'admin': [
                'clientes.ver', 'clientes.crear', 'clientes.editar', 'clientes.eliminar',
                'prestamos.ver', 'prestamos.crear', 'prestamos.editar', 'prestamos.eliminar',
                'pagos.ver', 'pagos.crear', 'pagos.editar', 'pagos.eliminar',
                'reportes.ver', 'usuarios.ver', 'usuarios.crear', 'usuarios.editar', 'usuarios.eliminar',
                'ver_todos_usuarios'  # Permiso especial para ver datos de otros usuarios
            ],
            'supervisor': [
                'clientes.ver', 'clientes.crear', 'clientes.editar', 'clientes.eliminar',
                'prestamos.ver', 'prestamos.crear', 'prestamos.editar', 'prestamos.eliminar',
                'pagos.ver', 'pagos.crear', 'pagos.editar', 'pagos.eliminar',
                'reportes.ver', 'usuarios.ver', 'usuarios.crear', 'usuarios.editar', 'usuarios.eliminar',
                'ver_usuarios_no_admin'  # Permiso para ver datos de usuarios no-admin
            ],
            'operador': [
                'clientes.ver', 'clientes.crear',
                'prestamos.ver', 'prestamos.crear',
                'pagos.ver', 'pagos.crear',
                'reportes.ver'
            ],
            'consultor': [
                'clientes.ver', 'prestamos.ver', 'pagos.ver', 'reportes.ver', 'usuarios.ver',
                'ver_usuarios_no_admin'  # Permiso para ver datos de usuarios no-admin (igual que supervisor)
            ]
        }
        return permisos_base.get(rol, permisos_base['consultor'])
    
    def puede_ver_datos_usuario(self, usuario_id: int) -> bool:
        """Verifica si puede ver los datos de otro usuario"""
        # Los admins pueden ver todos los datos
        if self.rol == 'admin':
            return True
        
        # Los supervisores y consultores pueden ver datos de usuarios no-admin
        if self.rol in ['supervisor', 'consultor']:
            # Obtener el usuario objetivo para verificar su rol
            from database import Database
            db = Database()
            usuario_objetivo = db.obtener_usuario(usuario_id, self.id, False)
            if usuario_objetivo:
                # Los supervisores y consultores NO pueden ver datos de administradores
                return usuario_objetivo.rol != 'admin'
            return False
        
        # Los usuarios solo pueden ver sus propios datos
        return self.id == usuario_id
    
    def puede_crear_usuarios(self) -> bool:
        """Verifica si puede crear usuarios"""
        return self.rol in ['admin', 'supervisor']
    
    def puede_eliminar_usuarios(self) -> bool:
        """Verifica si puede eliminar usuarios"""
        return self.rol in ['admin', 'supervisor']
    
    def puede_eliminar_usuario(self, usuario_id: int) -> bool:
        """Verifica si puede eliminar un usuario específico"""
        # Los admins pueden eliminar a cualquiera
        if self.rol == 'admin':
            return True
        
        # Los supervisores solo pueden eliminar usuarios no-admin
        if self.rol == 'supervisor':
            from database import Database
            db = Database()
            usuario_objetivo = db.obtener_usuario(usuario_id, self.id, False)
            if usuario_objetivo:
                return usuario_objetivo.rol != 'admin'
            return False
        
        return False
    
    def tiene_permiso(self, permiso: str) -> bool:
        """Verifica si el usuario tiene un permiso específico"""
        return permiso in self.permisos
    
    def tiene_permisos(self, permisos: list) -> bool:
        """Verifica si el usuario tiene todos los permisos especificados"""
        return all(self.tiene_permiso(p) for p in permisos)
    
    def __str__(self):
        return f"{self.nombre} ({self.username})"
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'password_hash': self.password_hash,
            'nombre': self.nombre,
            'email': self.email,
            'rol': self.rol,
            'activo': self.activo,
            'fecha_registro': self.fecha_registro.isoformat(),
            'ultimo_acceso': self.ultimo_acceso.isoformat() if self.ultimo_acceso else None,
            'usuario_creador_id': self.usuario_creador_id,
            'permisos': self.permisos
        }
    
    @classmethod
    def from_dict(cls, data):
        usuario = cls(
            id=data['id'],
            username=data['username'],
            password_hash=data['password_hash'],
            nombre=data['nombre'],
            email=data.get('email', ''),
            rol=data.get('rol', 'admin'),
            activo=data.get('activo', True),
            permisos=data.get('permisos', None),
            usuario_creador_id=data.get('usuario_creador_id')
        )
        usuario.fecha_registro = datetime.fromisoformat(data['fecha_registro'])
        if data.get('ultimo_acceso'):
            usuario.ultimo_acceso = datetime.fromisoformat(data['ultimo_acceso'])
        return usuario
    
    def actualizar_ultimo_acceso(self):
        """Actualiza la fecha del último acceso"""
        self.ultimo_acceso = datetime.now()
    
    def verificar_password(self, password: str) -> bool:
        """Verifica si la contraseña es correcta"""
        import hashlib
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        return password_hash == self.password_hash
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Genera el hash de una contraseña"""
        import hashlib
        return hashlib.sha256(password.encode()).hexdigest()
