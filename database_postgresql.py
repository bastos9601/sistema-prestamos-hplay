#!/usr/bin/env python3
"""
Adaptador de base de datos PostgreSQL para el Sistema de Préstamos
Reemplaza el sistema de archivos JSON por una base de datos PostgreSQL real
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.pool import SimpleConnectionPool
from typing import List, Optional, Dict, Any
from datetime import datetime, date
import json
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class PostgreSQLDatabase:
    """Clase para manejar la base de datos PostgreSQL"""
    
    def __init__(self):
        self.database_url = os.getenv('DATABASE_URL')
        if not self.database_url:
            raise ValueError("DATABASE_URL no está configurada")
        
        # Convertir postgres:// a postgresql:// para psycopg2
        if self.database_url.startswith('postgres://'):
            self.database_url = self.database_url.replace('postgres://', 'postgresql://', 1)
        
        # Pool de conexiones
        self.pool = SimpleConnectionPool(
            minconn=1,
            maxconn=20,
            dsn=self.database_url
        )
    
    def get_connection(self):
        """Obtiene una conexión del pool"""
        return self.pool.getconn()
    
    def return_connection(self, conn):
        """Devuelve una conexión al pool"""
        self.pool.putconn(conn)
    
    def execute_query(self, query: str, params: tuple = None, fetch: bool = True):
        """Ejecuta una consulta SQL"""
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            cursor.execute(query, params)
            
            if fetch:
                result = cursor.fetchall()
            else:
                conn.commit()
                result = cursor.rowcount
            
            cursor.close()
            return result
            
        except Exception as e:
            if conn:
                conn.rollback()
            raise e
        finally:
            if conn:
                self.return_connection(conn)
    
    def execute_many(self, query: str, params_list: List[tuple]):
        """Ejecuta múltiples consultas SQL"""
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.executemany(query, params_list)
            conn.commit()
            
            result = cursor.rowcount
            cursor.close()
            return result
            
        except Exception as e:
            if conn:
                conn.rollback()
            raise e
        finally:
            if conn:
                self.return_connection(conn)
    
    def close(self):
        """Cierra el pool de conexiones"""
        if self.pool:
            self.pool.closeall()

class UsuarioPostgreSQL:
    """Clase para manejar usuarios en PostgreSQL"""
    
    def __init__(self, db: PostgreSQLDatabase):
        self.db = db
    
    def crear_usuario(self, username: str, password_hash: str, nombre: str, email: str = None, rol: str = 'operador') -> int:
        """Crea un nuevo usuario"""
        query = """
            INSERT INTO usuarios (username, password_hash, nombre, email, rol)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
        """
        result = self.db.execute_query(query, (username, password_hash, nombre, email, rol))
        return result[0]['id']
    
    def obtener_usuario(self, usuario_id: int) -> Optional[Dict]:
        """Obtiene un usuario por ID"""
        query = "SELECT * FROM usuarios WHERE id = %s AND activo = TRUE"
        result = self.db.execute_query(query, (usuario_id,))
        return result[0] if result else None
    
    def obtener_usuario_por_username(self, username: str) -> Optional[Dict]:
        """Obtiene un usuario por username"""
        query = "SELECT * FROM usuarios WHERE username = %s AND activo = TRUE"
        result = self.db.execute_query(query, (username,))
        return result[0] if result else None
    
    def obtener_usuario_por_email(self, email: str) -> Optional[Dict]:
        """Obtiene un usuario por email"""
        query = "SELECT * FROM usuarios WHERE email = %s AND activo = TRUE"
        result = self.db.execute_query(query, (email,))
        return result[0] if result else None
    
    def listar_usuarios(self, usuario_actual_id: int, es_admin: bool = False) -> List[Dict]:
        """Lista usuarios según permisos"""
        if es_admin:
            query = "SELECT * FROM usuarios WHERE activo = TRUE ORDER BY nombre"
            return self.db.execute_query(query)
        else:
            query = "SELECT * FROM usuarios WHERE id = %s AND activo = TRUE"
            return self.db.execute_query(query, (usuario_actual_id,))
    
    def actualizar_usuario(self, usuario_id: int, **kwargs) -> bool:
        """Actualiza un usuario"""
        allowed_fields = ['nombre', 'email', 'rol', 'activo']
        update_fields = []
        params = []
        
        for field, value in kwargs.items():
            if field in allowed_fields:
                update_fields.append(f"{field} = %s")
                params.append(value)
        
        if not update_fields:
            return False
        
        update_fields.append("fecha_actualizacion = CURRENT_TIMESTAMP")
        params.append(usuario_id)
        
        query = f"UPDATE usuarios SET {', '.join(update_fields)} WHERE id = %s"
        result = self.db.execute_query(query, tuple(params), fetch=False)
        return result > 0
    
    def cambiar_password(self, usuario_id: int, nueva_password_hash: str) -> bool:
        """Cambia la contraseña de un usuario"""
        query = "UPDATE usuarios SET password_hash = %s WHERE id = %s"
        result = self.db.execute_query(query, (nueva_password_hash, usuario_id), fetch=False)
        return result > 0
    
    def eliminar_usuario(self, usuario_id: int) -> bool:
        """Elimina un usuario (soft delete)"""
        query = "UPDATE usuarios SET activo = FALSE WHERE id = %s"
        result = self.db.execute_query(query, (usuario_id,), fetch=False)
        return result > 0

class ClientePostgreSQL:
    """Clase para manejar clientes en PostgreSQL"""
    
    def __init__(self, db: PostgreSQLDatabase):
        self.db = db
    
    def crear_cliente(self, dni: str, nombre: str, apellido: str, telefono: str = None, 
                     email: str = None, direccion: str = None, usuario_id: int = None,
                     usuario_creador_id: int = None) -> int:
        """Crea un nuevo cliente"""
        query = """
            INSERT INTO clientes (dni, nombre, apellido, telefono, email, direccion, usuario_id, usuario_creador_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """
        result = self.db.execute_query(query, (dni, nombre, apellido, telefono, email, direccion, usuario_id, usuario_creador_id))
        return result[0]['id']
    
    def obtener_cliente(self, cliente_id: int, usuario_id: int, es_admin: bool = False) -> Optional[Dict]:
        """Obtiene un cliente por ID"""
        if es_admin:
            query = "SELECT * FROM clientes WHERE id = %s AND activo = TRUE"
            result = self.db.execute_query(query, (cliente_id,))
        else:
            query = "SELECT * FROM clientes WHERE id = %s AND usuario_id = %s AND activo = TRUE"
            result = self.db.execute_query(query, (cliente_id, usuario_id))
        
        return result[0] if result else None
    
    def obtener_cliente_por_dni(self, dni: str, usuario_id: int, es_admin: bool = False) -> Optional[Dict]:
        """Obtiene un cliente por DNI"""
        if es_admin:
            query = "SELECT * FROM clientes WHERE dni = %s AND activo = TRUE"
            result = self.db.execute_query(query, (dni,))
        else:
            query = "SELECT * FROM clientes WHERE dni = %s AND usuario_id = %s AND activo = TRUE"
            result = self.db.execute_query(query, (dni, usuario_id))
        
        return result[0] if result else None
    
    def listar_clientes(self, usuario_id: int, es_admin: bool = False) -> List[Dict]:
        """Lista clientes según permisos"""
        if es_admin:
            query = """
                SELECT c.*, u.username as usuario_creador
                FROM clientes c
                LEFT JOIN usuarios u ON c.usuario_creador_id = u.id
                WHERE c.activo = TRUE
                ORDER BY c.nombre, c.apellido
            """
            return self.db.execute_query(query)
        else:
            query = """
                SELECT c.*, u.username as usuario_creador
                FROM clientes c
                LEFT JOIN usuarios u ON c.usuario_creador_id = u.id
                WHERE c.usuario_id = %s AND c.activo = TRUE
                ORDER BY c.nombre, c.apellido
            """
            return self.db.execute_query(query, (usuario_id,))
    
    def actualizar_cliente(self, cliente_id: int, **kwargs) -> bool:
        """Actualiza un cliente"""
        allowed_fields = ['nombre', 'apellido', 'telefono', 'email', 'direccion']
        update_fields = []
        params = []
        
        for field, value in kwargs.items():
            if field in allowed_fields:
                update_fields.append(f"{field} = %s")
                params.append(value)
        
        if not update_fields:
            return False
        
        params.append(cliente_id)
        
        query = f"UPDATE clientes SET {', '.join(update_fields)} WHERE id = %s"
        result = self.db.execute_query(query, tuple(params), fetch=False)
        return result > 0
    
    def eliminar_cliente(self, cliente_id: int) -> bool:
        """Elimina un cliente (soft delete)"""
        query = "UPDATE clientes SET activo = FALSE WHERE id = %s"
        result = self.db.execute_query(query, (cliente_id,), fetch=False)
        return result > 0
    
    def buscar_clientes(self, query: str, usuario_id: int, es_admin: bool = False) -> List[Dict]:
        """Busca clientes por nombre, apellido o DNI"""
        search_term = f"%{query}%"
        
        if es_admin:
            sql_query = """
                SELECT c.*, u.username as usuario_creador
                FROM clientes c
                LEFT JOIN usuarios u ON c.usuario_creador_id = u.id
                WHERE c.activo = TRUE AND 
                      (c.nombre ILIKE %s OR c.apellido ILIKE %s OR c.dni ILIKE %s)
                ORDER BY c.nombre, c.apellido
            """
            return self.db.execute_query(sql_query, (search_term, search_term, search_term))
        else:
            sql_query = """
                SELECT c.*, u.username as usuario_creador
                FROM clientes c
                LEFT JOIN usuarios u ON c.usuario_creador_id = u.id
                WHERE c.usuario_id = %s AND c.activo = TRUE AND 
                      (c.nombre ILIKE %s OR c.apellido ILIKE %s OR c.dni ILIKE %s)
                ORDER BY c.nombre, c.apellido
            """
            return self.db.execute_query(sql_query, (usuario_id, search_term, search_term, search_term))

class PrestamoPostgreSQL:
    """Clase para manejar préstamos en PostgreSQL"""
    
    def __init__(self, db: PostgreSQLDatabase):
        self.db = db
    
    def crear_prestamo(self, cliente_id: int, monto_original: float, tasa_interes: float,
                       plazo_meses: int, fecha_inicio: date, usuario_id: int,
                       usuario_creador_id: int = None, observaciones: str = None) -> int:
        """Crea un nuevo préstamo"""
        monto_restante = monto_original
        fecha_vencimiento = self._calcular_fecha_vencimiento(fecha_inicio, plazo_meses)
        
        query = """
            INSERT INTO prestamos (cliente_id, monto_original, monto_restante, tasa_interes, 
                                 plazo_meses, fecha_inicio, fecha_vencimiento, usuario_id, 
                                 usuario_creador_id, observaciones)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """
        result = self.db.execute_query(query, (
            cliente_id, monto_original, monto_restante, tasa_interes, plazo_meses,
            fecha_inicio, fecha_vencimiento, usuario_id, usuario_creador_id, observaciones
        ))
        return result[0]['id']
    
    def _calcular_fecha_vencimiento(self, fecha_inicio: date, plazo_meses: int) -> date:
        """Calcula la fecha de vencimiento del préstamo"""
        # Implementación simple - en producción usar librería como dateutil
        year = fecha_inicio.year + (fecha_inicio.month + plazo_meses - 1) // 12
        month = (fecha_inicio.month + plazo_meses - 1) % 12 + 1
        return date(year, month, fecha_inicio.day)
    
    def obtener_prestamo(self, prestamo_id: int, usuario_id: int, es_admin: bool = False) -> Optional[Dict]:
        """Obtiene un préstamo por ID"""
        if es_admin:
            query = """
                SELECT p.*, c.nombre as cliente_nombre, c.apellido as cliente_apellido,
                       u.username as usuario_creador
                FROM prestamos p
                JOIN clientes c ON p.cliente_id = c.id
                LEFT JOIN usuarios u ON p.usuario_creador_id = u.id
                WHERE p.id = %s
            """
            result = self.db.execute_query(query, (prestamo_id,))
        else:
            query = """
                SELECT p.*, c.nombre as cliente_nombre, c.apellido as cliente_apellido,
                       u.username as usuario_creador
                FROM prestamos p
                JOIN clientes c ON p.cliente_id = c.id
                LEFT JOIN usuarios u ON p.usuario_creador_id = u.id
                WHERE p.id = %s AND p.usuario_id = %s
            """
            result = self.db.execute_query(query, (prestamo_id, usuario_id))
        
        return result[0] if result else None
    
    def listar_prestamos_activos(self, usuario_id: int, es_admin: bool = False) -> List[Dict]:
        """Lista préstamos activos"""
        if es_admin:
            query = """
                SELECT p.*, c.nombre as cliente_nombre, c.apellido as cliente_apellido,
                       u.username as usuario_creador
                FROM prestamos p
                JOIN clientes c ON p.cliente_id = c.id
                LEFT JOIN usuarios u ON p.usuario_creador_id = u.id
                WHERE p.estado = 'activo'
                ORDER BY p.fecha_creacion DESC
            """
            return self.db.execute_query(query)
        else:
            query = """
                SELECT p.*, c.nombre as cliente_nombre, c.apellido as cliente_apellido,
                       u.username as usuario_creador
                FROM prestamos p
                JOIN clientes c ON p.cliente_id = c.id
                LEFT JOIN usuarios u ON p.usuario_creador_id = u.id
                WHERE p.usuario_id = %s AND p.estado = 'activo'
                ORDER BY p.fecha_creacion DESC
            """
            return self.db.execute_query(query, (usuario_id,))
    
    def actualizar_prestamo(self, prestamo_id: int, **kwargs) -> bool:
        """Actualiza un préstamo"""
        allowed_fields = ['monto_restante', 'estado', 'observaciones']
        update_fields = []
        params = []
        
        for field, value in kwargs.items():
            if field in allowed_fields:
                update_fields.append(f"{field} = %s")
                params.append(value)
        
        if not update_fields:
            return False
        
        params.append(prestamo_id)
        
        query = f"UPDATE prestamos SET {', '.join(update_fields)} WHERE id = %s"
        result = self.db.execute_query(query, tuple(params), fetch=False)
        return result > 0
    
    def obtener_estadisticas(self, usuario_id: int, es_admin: bool = False) -> Dict:
        """Obtiene estadísticas de préstamos"""
        if es_admin:
            query = """
                SELECT 
                    COUNT(*) as total_prestamos,
                    COUNT(CASE WHEN estado = 'activo' THEN 1 END) as prestamos_activos,
                    COUNT(CASE WHEN estado = 'pagado' THEN 1 END) as prestamos_pagados,
                    COUNT(CASE WHEN estado = 'vencido' THEN 1 END) as prestamos_vencidos,
                    SUM(CASE WHEN estado = 'activo' THEN monto_restante ELSE 0 END) as monto_total_activo,
                    AVG(tasa_interes) as tasa_promedio
                FROM prestamos
            """
            result = self.db.execute_query(query)
        else:
            query = """
                SELECT 
                    COUNT(*) as total_prestamos,
                    COUNT(CASE WHEN estado = 'activo' THEN 1 END) as prestamos_activos,
                    COUNT(CASE WHEN estado = 'pagado' THEN 1 END) as prestamos_pagados,
                    COUNT(CASE WHEN estado = 'vencido' THEN 1 END) as prestamos_vencidos,
                    SUM(CASE WHEN estado = 'activo' THEN monto_restante ELSE 0 END) as monto_total_activo,
                    AVG(tasa_interes) as tasa_promedio
                FROM prestamos
                WHERE usuario_id = %s
            """
            result = self.db.execute_query(query, (usuario_id,))
        
        return result[0] if result else {}

class PagoPostgreSQL:
    """Clase para manejar pagos en PostgreSQL"""
    
    def __init__(self, db: PostgreSQLDatabase):
        self.db = db
    
    def crear_pago(self, prestamo_id: int, monto: float, fecha_pago: date,
                   tipo_pago: str = 'cuota', usuario_id: int = None,
                   observaciones: str = None) -> int:
        """Crea un nuevo pago"""
        query = """
            INSERT INTO pagos (prestamo_id, monto, fecha_pago, tipo_pago, usuario_id, observaciones)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id
        """
        result = self.db.execute_query(query, (
            prestamo_id, monto, fecha_pago, tipo_pago, usuario_id, observaciones
        ))
        return result[0]['id']
    
    def obtener_pagos_por_prestamo(self, prestamo_id: int) -> List[Dict]:
        """Obtiene todos los pagos de un préstamo"""
        query = """
            SELECT p.*, u.username as usuario_nombre
            FROM pagos p
            LEFT JOIN usuarios u ON p.usuario_id = u.id
            WHERE p.prestamo_id = %s
            ORDER BY p.fecha_pago DESC
        """
        return self.db.execute_query(query, (prestamo_id,))
    
    def obtener_estadisticas_pagos(self, usuario_id: int, es_admin: bool = False) -> Dict:
        """Obtiene estadísticas de pagos"""
        if es_admin:
            query = """
                SELECT 
                    COUNT(*) as total_pagos,
                    SUM(monto) as monto_total_pagado,
                    AVG(monto) as monto_promedio_pago,
                    COUNT(CASE WHEN tipo_pago = 'cuota' THEN 1 END) as pagos_cuota,
                    COUNT(CASE WHEN tipo_pago = 'adelanto' THEN 1 END) as pagos_adelanto
                FROM pagos
            """
            result = self.db.execute_query(query)
        else:
            query = """
                SELECT 
                    COUNT(*) as total_pagos,
                    SUM(monto) as monto_total_pagado,
                    AVG(monto) as monto_promedio_pago,
                    COUNT(CASE WHEN tipo_pago = 'cuota' THEN 1 END) as pagos_cuota,
                    COUNT(CASE WHEN tipo_pago = 'adelanto' THEN 1 END) as pagos_adelanto
                FROM pagos p
                JOIN prestamos pr ON p.prestamo_id = pr.id
                WHERE pr.usuario_id = %s
            """
            result = self.db.execute_query(query, (usuario_id,))
        
        return result[0] if result else {}

# Función para crear instancia de la base de datos
def create_database():
    """Crea una instancia de la base de datos PostgreSQL"""
    try:
        db = PostgreSQLDatabase()
        return {
            'usuarios': UsuarioPostgreSQL(db),
            'clientes': ClientePostgreSQL(db),
            'prestamos': PrestamoPostgreSQL(db),
            'pagos': PagoPostgreSQL(db),
            'db': db
        }
    except Exception as e:
        print(f"Error creando base de datos: {e}")
        return None
