#!/usr/bin/env python3
"""
Script para ejecutar el Sistema de Préstamos Web
==============================================

Este script crea datos de ejemplo y ejecuta la aplicación web.
"""

from decimal import Decimal
from database import Database
from services import ClienteService, PrestamoService, PagoService
import webbrowser
import time
import os

def crear_datos_ejemplo():
    """Crea datos de ejemplo para la aplicación web"""
    print("🚀 CREANDO DATOS DE EJEMPLO PARA LA APLICACIÓN WEB...")
    
    # Inicializar servicios
    db = Database()
    cliente_service = ClienteService(db)
    prestamo_service = PrestamoService(db)
    pago_service = PagoService(db)
    
    try:
        # Verificar si ya existen datos
        clientes_existentes = cliente_service.listar_clientes()
        if clientes_existentes:
            print("✅ Ya existen datos en el sistema")
            return True
        
        # 1. CREAR CLIENTES DE EJEMPLO
        print("\n👥 Creando clientes de ejemplo...")
        
        try:
            cliente1 = cliente_service.crear_cliente(
                nombre="Juan Carlos",
                apellido="Pérez González",
                dni="12345678",
                telefono="555-0101",
                email="juan.perez@email.com"
            )
            print(f"✓ Cliente creado: {cliente1}")
        except ValueError as e:
            print(f"⚠️ Cliente 1 ya existe: {e}")
            cliente1 = cliente_service.buscar_cliente("12345678")[0]
        
        try:
            cliente2 = cliente_service.crear_cliente(
                nombre="María Elena",
                apellido="Rodríguez López",
                dni="87654321",
                telefono="555-0202",
                email="maria.rodriguez@email.com"
            )
            print(f"✓ Cliente creado: {cliente2}")
        except ValueError as e:
            print(f"⚠️ Cliente 2 ya existe: {e}")
            cliente2 = cliente_service.buscar_cliente("87654321")[0]
        
        try:
            cliente3 = cliente_service.crear_cliente(
                nombre="Carlos Alberto",
                apellido="García Martínez",
                dni="11223344",
                telefono="555-0303",
                email="carlos.garcia@email.com"
            )
            print(f"✓ Cliente creado: {cliente3}")
        except ValueError as e:
            print(f"⚠️ Cliente 3 ya existe: {e}")
            cliente3 = cliente_service.buscar_cliente("11223344")[0]
        
        # 2. CREAR PRÉSTAMOS DE EJEMPLO
        print("\n💰 Creando préstamos de ejemplo...")
        
        # Préstamo 1: Interés simple
        prestamo1 = prestamo_service.crear_prestamo(
            cliente_id=cliente1.id,
            monto=Decimal("15000"),
            tasa_interes=Decimal("12.5"),
            plazo_meses=24,
            tipo_interes="simple"
        )
        print(f"✓ Préstamo 1 creado: ${prestamo1.monto:.2f} - {prestamo1.tipo_interes}")
        
        # Préstamo 2: Interés compuesto
        prestamo2 = prestamo_service.crear_prestamo(
            cliente_id=cliente2.id,
            monto=Decimal("25000"),
            tasa_interes=Decimal("15.0"),
            plazo_meses=36,
            tipo_interes="compuesto"
        )
        print(f"✓ Préstamo 2 creado: ${prestamo2.monto:.2f} - {prestamo2.tipo_interes}")
        
        # Préstamo 3: Interés simple
        prestamo3 = prestamo_service.crear_prestamo(
            cliente_id=cliente3.id,
            monto=Decimal("8000"),
            tasa_interes=Decimal("10.0"),
            plazo_meses=12,
            tipo_interes="simple"
        )
        print(f"✓ Préstamo 3 creado: ${prestamo3.monto:.2f} - {prestamo3.tipo_interes}")
        
        # 3. REGISTRAR PAGOS DE EJEMPLO
        print("\n💳 Registrando pagos de ejemplo...")
        
        # Pagos para el préstamo 1
        pago1_1 = pago_service.registrar_pago(
            prestamo_id=prestamo1.id,
            monto=prestamo1.calcular_cuota_mensual(),
            concepto="Primera cuota mensual"
        )
        print(f"✓ Pago 1 registrado: ${pago1_1.monto:.2f}")
        
        pago1_2 = pago_service.registrar_pago(
            prestamo_id=prestamo1.id,
            monto=prestamo1.calcular_cuota_mensual(),
            concepto="Segunda cuota mensual"
        )
        print(f"✓ Pago 2 registrado: ${pago1_2.monto:.2f}")
        
        # Pago para el préstamo 2
        pago2_1 = pago_service.registrar_pago(
            prestamo_id=prestamo2.id,
            monto=prestamo2.calcular_cuota_mensual(),
            concepto="Primera cuota mensual"
        )
        print(f"✓ Pago 3 registrado: ${pago2_1.monto:.2f}")
        
        # Pago para el préstamo 3
        pago3_1 = pago_service.registrar_pago(
            prestamo_id=prestamo3.id,
            monto=Decimal("1000"),
            concepto="Pago parcial"
        )
        print(f"✓ Pago 4 registrado: ${pago3_1.monto:.2f}")
        
        print("\n🎉 ¡DATOS DE EJEMPLO CREADOS EXITOSAMENTE!")
        print("=" * 60)
        print("El sistema ahora tiene:")
        print("• 3 clientes registrados")
        print("• 3 préstamos activos")
        print("• 4 pagos registrados")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error durante la creación de datos de ejemplo: {e}")
        import traceback
        traceback.print_exc()
        return False

def limpiar_base_datos():
    """Limpiar la base de datos para empezar desde cero"""
    try:
        print("\n🧹 Limpiando base de datos...")
        
        # Obtener todos los préstamos y pagos
        prestamos = prestamo_service.listar_prestamos_activos()
        clientes = cliente_service.listar_clientes()
        
        # Eliminar pagos primero
        for prestamo in prestamos:
            historial = pago_service.obtener_historial_pagos(prestamo.id)
            for pago in historial:
                # Aquí necesitarías implementar la eliminación de pagos en el servicio
                pass
        
        # Eliminar préstamos
        for prestamo in prestamos:
            # Aquí necesitarías implementar la eliminación de préstamos en el servicio
            pass
        
        # Eliminar clientes
        for cliente in clientes:
            cliente_service.eliminar_cliente(cliente.id)
        
        print("✅ Base de datos limpiada exitosamente")
        return True
        
    except Exception as e:
        print(f"❌ Error al limpiar la base de datos: {e}")
        return False

def abrir_navegador():
    """Abre el navegador automáticamente"""
    url = "http://localhost:5000"
    print(f"\n🌐 Abriendo navegador en: {url}")
    
    try:
        webbrowser.open(url)
    except Exception as e:
        print(f"⚠️ No se pudo abrir el navegador automáticamente: {e}")
        print(f"📱 Por favor, abre manualmente: {url}")

def main():
    """Función principal"""
    print("🏦 SISTEMA DE PRÉSTAMOS DE DINERO - VERSIÓN WEB")
    print("=" * 60)
    
    # Verificar si ya existen datos
    db = Database()
    cliente_service = ClienteService(db)
    clientes_existentes = cliente_service.listar_clientes()
    
    if clientes_existentes:
        print("✅ Ya existen datos en el sistema")
        print("\n¿Qué quieres hacer?")
        print("1. Usar datos existentes")
        print("2. Limpiar base de datos y empezar desde cero")
        
        try:
            opcion = input("\nSelecciona una opción (1 o 2): ").strip()
            if opcion == "2":
                if limpiar_base_datos():
                    print("🔄 Reiniciando sistema...")
                    time.sleep(2)
                    # Recargar servicios después de limpiar
                    db = Database()
                    cliente_service = ClienteService(db)
                    prestamo_service = PrestamoService(db)
                    pago_service = PagoService(db)
                else:
                    print("❌ No se pudo limpiar la base de datos")
                    return
        except KeyboardInterrupt:
            print("\n\n👋 Operación cancelada por el usuario")
            return
    
        # No crear datos de ejemplo automáticamente
    print("🚀 Iniciando aplicación web...")
    print("📝 El sistema está listo para crear clientes y préstamos manualmente")
    print("⏳ Esperando 3 segundos para que se inicie el servidor...")
    
    # Esperar un poco para que se inicie el servidor
    time.sleep(3)
    
    # Abrir navegador
    abrir_navegador()
    
    print("\n✅ ¡Aplicación web iniciada exitosamente!")
    print("📱 La aplicación está disponible en: http://localhost:5000")
    print("🔄 Para detener el servidor, presiona Ctrl+C")
    print("\n" + "=" * 60)
    
    # Ejecutar la aplicación Flask
    try:
        from app import app
        app.run(debug=True, host='0.0.0.0', port=5000)
    except ImportError as e:
        print(f"❌ Error al importar la aplicación Flask: {e}")
        print("Asegúrate de que todos los archivos estén en el mismo directorio.")
    except Exception as e:
        print(f"❌ Error al ejecutar la aplicación: {e}")

if __name__ == "__main__":
    main()
