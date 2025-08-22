#!/usr/bin/env python3
"""
Script de migración de SQLite a PostgreSQL
Este script migra todos los datos de los archivos JSON a PostgreSQL
"""

import os
import json
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import sys

# Cargar variables de entorno
load_dotenv()

class PostgreSQLMigrator:
    """Clase para migrar datos de SQLite/JSON a PostgreSQL"""
    
    def __init__(self):
        self.database_url = os.getenv('DATABASE_URL')
        if not self.database_url:
            print("❌ Error: DATABASE_URL no está configurada")
            sys.exit(1)
        
        # Convertir postgres:// a postgresql:// para psycopg2
        if self.database_url.startswith('postgres://'):
            self.database_url = self.database_url.replace('postgres://', 'postgresql://', 1)
        
        self.connection = None
        self.cursor = None
    
    def connect(self):
        """Conecta a PostgreSQL"""
        try:
            self.connection = psycopg2.connect(self.database_url)
            self.cursor = self.connection.cursor(cursor_factory=RealDictCursor)
            print("✅ Conexión a PostgreSQL establecida")
        except Exception as e:
            print(f"❌ Error conectando a PostgreSQL: {e}")
            sys.exit(1)
    
    def disconnect(self):
        """Desconecta de PostgreSQL"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        print("🔌 Conexión a PostgreSQL cerrada")
    
    def create_tables(self):
        """Crea las tablas en PostgreSQL"""
        try:
            # Tabla de usuarios
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS usuarios (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    nombre VARCHAR(100) NOT NULL,
                    email VARCHAR(100) UNIQUE,
                    rol VARCHAR(20) NOT NULL DEFAULT 'operador',
                    activo BOOLEAN DEFAULT TRUE,
                    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    fecha_ultimo_acceso TIMESTAMP
                )
            """)
            
            # Tabla de clientes
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS clientes (
                    id SERIAL PRIMARY KEY,
                    dni VARCHAR(20) UNIQUE NOT NULL,
                    nombre VARCHAR(100) NOT NULL,
                    apellido VARCHAR(100) NOT NULL,
                    telefono VARCHAR(20),
                    email VARCHAR(100),
                    direccion TEXT,
                    usuario_id INTEGER REFERENCES usuarios(id),
                    usuario_creador_id INTEGER REFERENCES usuarios(id),
                    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    activo BOOLEAN DEFAULT TRUE
                )
            """)
            
            # Tabla de préstamos
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS prestamos (
                    id SERIAL PRIMARY KEY,
                    cliente_id INTEGER REFERENCES clientes(id),
                    monto_original DECIMAL(10,2) NOT NULL,
                    monto_restante DECIMAL(10,2) NOT NULL,
                    tasa_interes DECIMAL(5,2) NOT NULL,
                    plazo_meses INTEGER NOT NULL,
                    fecha_inicio DATE NOT NULL,
                    fecha_vencimiento DATE NOT NULL,
                    estado VARCHAR(20) DEFAULT 'activo',
                    usuario_id INTEGER REFERENCES usuarios(id),
                    usuario_creador_id INTEGER REFERENCES usuarios(id),
                    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    observaciones TEXT
                )
            """)
            
            # Tabla de pagos
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS pagos (
                    id SERIAL PRIMARY KEY,
                    prestamo_id INTEGER REFERENCES prestamos(id),
                    monto DECIMAL(10,2) NOT NULL,
                    fecha_pago DATE NOT NULL,
                    tipo_pago VARCHAR(20) DEFAULT 'cuota',
                    usuario_id INTEGER REFERENCES usuarios(id),
                    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    observaciones TEXT
                )
            """)
            
            # Tabla de configuraciones
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS configuraciones (
                    id SERIAL PRIMARY KEY,
                    clave VARCHAR(100) UNIQUE NOT NULL,
                    valor TEXT,
                    descripcion TEXT,
                    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            self.connection.commit()
            print("✅ Tablas creadas exitosamente")
            
        except Exception as e:
            print(f"❌ Error creando tablas: {e}")
            self.connection.rollback()
            raise
    
    def migrate_usuarios(self):
        """Migra usuarios desde JSON a PostgreSQL"""
        try:
            if not os.path.exists('data/usuarios.json'):
                print("⚠️ Archivo usuarios.json no encontrado, saltando...")
                return
            
            with open('data/usuarios.json', 'r', encoding='utf-8') as f:
                usuarios = json.load(f)
            
            for usuario in usuarios:
                self.cursor.execute("""
                    INSERT INTO usuarios (id, username, password_hash, nombre, email, rol, activo, fecha_creacion)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO UPDATE SET
                        username = EXCLUDED.username,
                        password_hash = EXCLUDED.password_hash,
                        nombre = EXCLUDED.nombre,
                        email = EXCLUDED.email,
                        rol = EXCLUDED.rol,
                        activo = EXCLUDED.activo
                """, (
                    usuario['id'],
                    usuario['username'],
                    usuario['password_hash'],
                    usuario['nombre'],
                    usuario.get('email'),
                    usuario['rol'],
                    usuario['activo'],
                    usuario.get('fecha_creacion')
                ))
            
            self.connection.commit()
            print(f"✅ {len(usuarios)} usuarios migrados")
            
        except Exception as e:
            print(f"❌ Error migrando usuarios: {e}")
            self.connection.rollback()
            raise
    
    def migrate_clientes(self):
        """Migra clientes desde JSON a PostgreSQL"""
        try:
            if not os.path.exists('data/clientes.json'):
                print("⚠️ Archivo clientes.json no encontrado, saltando...")
                return
            
            with open('data/clientes.json', 'r', encoding='utf-8') as f:
                clientes = json.load(f)
            
            for cliente in clientes:
                self.cursor.execute("""
                    INSERT INTO clientes (id, dni, nombre, apellido, telefono, email, direccion, usuario_id, usuario_creador_id, fecha_creacion, activo)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO UPDATE SET
                        dni = EXCLUDED.dni,
                        nombre = EXCLUDED.nombre,
                        apellido = EXCLUDED.apellido,
                        telefono = EXCLUDED.telefono,
                        email = EXCLUDED.email,
                        direccion = EXCLUDED.direccion,
                        usuario_id = EXCLUDED.usuario_id,
                        usuario_creador_id = EXCLUDED.usuario_creador_id,
                        activo = EXCLUDED.activo
                """, (
                    cliente['id'],
                    cliente['dni'],
                    cliente['nombre'],
                    cliente['apellido'],
                    cliente.get('telefono'),
                    cliente.get('email'),
                    cliente.get('direccion'),
                    cliente.get('usuario_id'),
                    cliente.get('usuario_creador_id'),
                    cliente.get('fecha_creacion'),
                    cliente.get('activo', True)
                ))
            
            self.connection.commit()
            print(f"✅ {len(clientes)} clientes migrados")
            
        except Exception as e:
            print(f"❌ Error migrando clientes: {e}")
            self.connection.rollback()
            raise
    
    def migrate_prestamos(self):
        """Migra préstamos desde JSON a PostgreSQL"""
        try:
            if not os.path.exists('data/prestamos.json'):
                print("⚠️ Archivo prestamos.json no encontrado, saltando...")
                return
            
            with open('data/prestamos.json', 'r', encoding='utf-8') as f:
                prestamos = json.load(f)
            
            for prestamo in prestamos:
                self.cursor.execute("""
                    INSERT INTO prestamos (id, cliente_id, monto_original, monto_restante, tasa_interes, plazo_meses, fecha_inicio, fecha_vencimiento, estado, usuario_id, usuario_creador_id, fecha_creacion, observaciones)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO UPDATE SET
                        cliente_id = EXCLUDED.cliente_id,
                        monto_original = EXCLUDED.monto_original,
                        monto_restante = EXCLUDED.monto_restante,
                        tasa_interes = EXCLUDED.tasa_interes,
                        plazo_meses = EXCLUDED.plazo_meses,
                        fecha_inicio = EXCLUDED.fecha_inicio,
                        fecha_vencimiento = EXCLUDED.fecha_vencimiento,
                        estado = EXCLUDED.estado,
                        usuario_id = EXCLUDED.usuario_id,
                        usuario_creador_id = EXCLUDED.usuario_creador_id,
                        observaciones = EXCLUDED.observaciones
                """, (
                    prestamo['id'],
                    prestamo['cliente_id'],
                    prestamo['monto_original'],
                    prestamo['monto_restante'],
                    prestamo['tasa_interes'],
                    prestamo['plazo_meses'],
                    prestamo['fecha_inicio'],
                    prestamo['fecha_vencimiento'],
                    prestamo.get('estado', 'activo'),
                    prestamo.get('usuario_id'),
                    prestamo.get('usuario_creador_id'),
                    prestamo.get('fecha_creacion'),
                    prestamo.get('observaciones')
                ))
            
            self.connection.commit()
            print(f"✅ {len(prestamos)} préstamos migrados")
            
        except Exception as e:
            print(f"❌ Error migrando préstamos: {e}")
            self.connection.rollback()
            raise
    
    def migrate_pagos(self):
        """Migra pagos desde JSON a PostgreSQL"""
        try:
            if not os.path.exists('data/pagos.json'):
                print("⚠️ Archivo pagos.json no encontrado, saltando...")
                return
            
            with open('data/pagos.json', 'r', encoding='utf-8') as f:
                pagos = json.load(f)
            
            for pago in pagos:
                self.cursor.execute("""
                    INSERT INTO pagos (id, prestamo_id, monto, fecha_pago, tipo_pago, usuario_id, fecha_creacion, observaciones)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO UPDATE SET
                        prestamo_id = EXCLUDED.prestamo_id,
                        monto = EXCLUDED.monto,
                        fecha_pago = EXCLUDED.fecha_pago,
                        tipo_pago = EXCLUDED.tipo_pago,
                        usuario_id = EXCLUDED.usuario_id,
                        observaciones = EXCLUDED.observaciones
                """, (
                    pago['id'],
                    pago['prestamo_id'],
                    pago['monto'],
                    pago['fecha_pago'],
                    pago.get('tipo_pago', 'cuota'),
                    pago.get('usuario_id'),
                    pago.get('fecha_creacion'),
                    pago.get('observaciones')
                ))
            
            self.connection.commit()
            print(f"✅ {len(pagos)} pagos migrados")
            
        except Exception as e:
            print(f"❌ Error migrando pagos: {e}")
            self.connection.rollback()
            raise
    
    def create_indexes(self):
        """Crea índices para mejorar el rendimiento"""
        try:
            # Índices para usuarios
            self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_usuarios_username ON usuarios(username)")
            self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_usuarios_email ON usuarios(email)")
            self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_usuarios_rol ON usuarios(rol)")
            
            # Índices para clientes
            self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_clientes_dni ON clientes(dni)")
            self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_clientes_usuario_id ON clientes(usuario_id)")
            self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_clientes_nombre_apellido ON clientes(nombre, apellido)")
            
            # Índices para préstamos
            self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_prestamos_cliente_id ON prestamos(cliente_id)")
            self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_prestamos_estado ON prestamos(estado)")
            self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_prestamos_fecha_vencimiento ON prestamos(fecha_vencimiento)")
            
            # Índices para pagos
            self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_pagos_prestamo_id ON pagos(prestamo_id)")
            self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_pagos_fecha_pago ON pagos(fecha_pago)")
            
            self.connection.commit()
            print("✅ Índices creados exitosamente")
            
        except Exception as e:
            print(f"❌ Error creando índices: {e}")
            self.connection.rollback()
            raise
    
    def run_migration(self):
        """Ejecuta la migración completa"""
        try:
            print("🚀 Iniciando migración a PostgreSQL...")
            
            self.connect()
            self.create_tables()
            self.migrate_usuarios()
            self.migrate_clientes()
            self.migrate_prestamos()
            self.migrate_pagos()
            self.create_indexes()
            
            print("🎉 ¡Migración completada exitosamente!")
            
        except Exception as e:
            print(f"❌ Error durante la migración: {e}")
            raise
        finally:
            self.disconnect()

def main():
    """Función principal"""
    try:
        migrator = PostgreSQLMigrator()
        migrator.run_migration()
    except Exception as e:
        print(f"❌ Error fatal: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
