#!/usr/bin/env python3
"""
Script de prueba para verificar el sistema multi-usuario
=======================================================

Este script prueba las funcionalidades básicas del sistema
para asegurar que el aislamiento de datos funcione correctamente.
"""

from models import Usuario, Cliente, Prestamo, Pago
from database import Database
from services import ClienteService, PrestamoService, PagoService
from decimal import Decimal

def test_sistema_multi_usuario():
    """Prueba el sistema multi-usuario"""
    print("🧪 Probando Sistema Multi-Usuario...")
    
    # Crear instancia de la base de datos
    db = Database()
    
    try:
        # 1. Verificar que existe el usuario administrador
        print("\n1. Verificando usuario administrador...")
        admin = db.obtener_usuario(1, 1, True)  # Admin puede ver cualquier usuario
        if admin:
            print(f"✅ Admin encontrado: {admin.nombre} (Rol: {admin.rol})")
        else:
            print("❌ Admin no encontrado")
            return False
        
        # 2. Crear un usuario de prueba
        print("\n2. Creando usuario de prueba...")
        usuario_test = Usuario(
            id=0,
            username="test_user",
            password_hash=Usuario.hash_password("test123"),
            nombre="Usuario de Prueba",
            email="test@test.com",
            rol="operador",
            usuario_creador_id=1  # Creado por el admin
        )
        
        usuario_creado = db.agregar_usuario(usuario_test, 1)
        print(f"✅ Usuario de prueba creado: {usuario_creado.nombre}")
        
        # 3. Crear cliente para el usuario de prueba
        print("\n3. Creando cliente para usuario de prueba...")
        cliente_service = ClienteService(db)
        cliente = cliente_service.crear_cliente(
            nombre="Juan",
            apellido="Pérez",
            dni="12345678",
            telefono="123-456-789",
            email="juan@test.com",
            usuario_id=usuario_creado.id
        )
        print(f"✅ Cliente creado: {cliente.nombre} {cliente.apellido}")
        
        # 4. Crear préstamo para el cliente
        print("\n4. Creando préstamo para el cliente...")
        prestamo_service = PrestamoService(db)
        prestamo = prestamo_service.crear_prestamo(
            cliente_id=cliente.id,
            monto=Decimal("1000.00"),
            tasa_interes=Decimal("15.0"),
            plazo_dias=30,
            tipo_interes="gota_a_gota",
            usuario_id=usuario_creado.id
        )
        print(f"✅ Préstamo creado: ID {prestamo.id}, Monto: ${prestamo.monto}")
        
        # 5. Crear pago para el préstamo
        print("\n5. Creando pago para el préstamo...")
        pago_service = PagoService(db)
        pago = pago_service.registrar_pago(
            prestamo_id=prestamo.id,
            monto=Decimal("100.00"),
            concepto="Pago de prueba",
            usuario_id=usuario_creado.id
        )
        print(f"✅ Pago creado: ID {pago.id}, Monto: ${pago.monto}")
        
        # 6. Probar aislamiento de datos
        print("\n6. Probando aislamiento de datos...")
        
        # El usuario de prueba debe ver solo sus datos
        clientes_usuario = cliente_service.listar_clientes(usuario_creado.id, False)
        print(f"   Usuario ve {len(clientes_usuario)} clientes")
        
        # El admin debe ver todos los datos
        clientes_admin = cliente_service.listar_clientes(1, True)
        print(f"   Admin ve {len(clientes_admin)} clientes")
        
        # Verificar que el usuario solo ve sus propios datos
        if len(clientes_usuario) == 1 and len(clientes_admin) >= 1:
            print("✅ Aislamiento de datos funcionando correctamente")
        else:
            print("❌ Problema con el aislamiento de datos")
            return False
        
        # 7. Probar permisos
        print("\n7. Probando permisos...")
        
        # El usuario de prueba debe poder ver su propio cliente
        cliente_visto = cliente_service.obtener_cliente(cliente.id, usuario_creado.id, False)
        if cliente_visto:
            print("✅ Usuario puede ver su propio cliente")
        else:
            print("❌ Usuario no puede ver su propio cliente")
            return False
        
        # El admin debe poder ver cualquier cliente
        cliente_admin = cliente_service.obtener_cliente(cliente.id, 1, True)
        if cliente_admin:
            print("✅ Admin puede ver cualquier cliente")
        else:
            print("❌ Admin no puede ver cualquier cliente")
            return False
        
        print("\n🎉 ¡Todas las pruebas pasaron exitosamente!")
        print("✅ El sistema multi-usuario está funcionando correctamente")
        print("✅ El aislamiento de datos está funcionando")
        print("✅ Los permisos están funcionando")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error durante las pruebas: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_sistema_multi_usuario()
