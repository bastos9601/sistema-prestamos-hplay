#!/usr/bin/env python3
"""
Script para crear un usuario operador en el sistema
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import Database
from models import Usuario
from decimal import Decimal

def crear_operador():
    """Crea un usuario operador para probar la funcionalidad del supervisor"""
    db = Database()
    
    # Crear usuario operador
    operador = Usuario(
        id=0,  # Se asignará automáticamente
        username="operador",
        password_hash=Usuario.hash_password("operador123"),
        nombre="Operador del Sistema",
        email="operador@sistema.com",
        rol="operador",
        activo=True
    )
    
    try:
        # Agregar el operador al sistema (creado por el admin)
        operador_creado = db.agregar_usuario(operador, usuario_creador_id=1)
        print(f"✅ Usuario operador creado exitosamente:")
        print(f"   ID: {operador_creado.id}")
        print(f"   Username: {operador_creado.username}")
        print(f"   Contraseña: operador123")
        print(f"   Rol: {operador_creado.rol}")
        print(f"   Permisos: {operador_creado.permisos}")
        
        # Crear algunos datos de prueba para el operador
        print(f"\n📝 Creando datos de prueba para el operador...")
        
        # Crear un cliente
        from models import Cliente
        cliente = Cliente(
            id=0,
            nombre="Juan",
            apellido="Pérez",
            dni="12345678",
            telefono="+51987654321",
            email="juan.perez@email.com",
            usuario_id=operador_creado.id
        )
        cliente_creado = db.agregar_cliente(cliente, operador_creado.id)
        print(f"   ✅ Cliente creado: {cliente_creado.nombre} {cliente_creado.apellido}")
        
        # Crear un préstamo
        from models import Prestamo
        prestamo = Prestamo(
            id=0,
            cliente_id=cliente_creado.id,
            monto=Decimal('200.00'),
            tasa_interes=Decimal('15.00'),
            plazo_dias=30,
            tipo_interes="gota_a_gota",
            descripcion="Préstamo de prueba",
            usuario_id=operador_creado.id
        )
        prestamo_creado = db.agregar_prestamo(prestamo, operador_creado.id)
        print(f"   ✅ Préstamo creado: ${prestamo_creado.monto} por {prestamo_creado.plazo_dias} días")
        
        # Crear un pago
        from models import Pago
        pago = Pago(
            id=0,
            prestamo_id=prestamo_creado.id,
            monto=Decimal('50.00'),
            concepto="Pago de prueba",
            usuario_id=operador_creado.id
        )
        pago_creado = db.agregar_pago(pago, operador_creado.id)
        print(f"   ✅ Pago creado: ${pago_creado.monto}")
        
        print(f"\n🎯 Ahora puedes probar:")
        print(f"   1. Iniciar sesión como 'supervisor' / 'supervisor123'")
        print(f"   2. Ver los datos del operador en Clientes, Préstamos y Pagos")
        print(f"   3. Eliminar al operador y todos sus datos")
        
    except Exception as e:
        print(f"❌ Error al crear el operador: {e}")

if __name__ == "__main__":
    crear_operador()
