#!/usr/bin/env python3
"""
Ejemplo de Uso del Sistema de Préstamos
========================================

Este script demuestra las funcionalidades principales del sistema
creando clientes, préstamos y pagos de ejemplo.
"""

from decimal import Decimal
from datetime import date
from database import Database
from services import ClienteService, PrestamoService, PagoService, ReporteService

def main():
    """Función principal del ejemplo"""
    print("🚀 INICIANDO EJEMPLO DEL SISTEMA DE PRÉSTAMOS")
    print("=" * 50)
    
    # Inicializar servicios
    db = Database()
    cliente_service = ClienteService(db)
    prestamo_service = PrestamoService(db)
    pago_service = PagoService(db)
    reporte_service = ReporteService(db)
    
    try:
        # 1. CREAR CLIENTES DE EJEMPLO
        print("\n👥 CREANDO CLIENTES DE EJEMPLO...")
        
        cliente1 = cliente_service.crear_cliente(
            nombre="Juan Carlos",
            apellido="Pérez González",
            dni="12345678",
            telefono="555-0101",
            email="juan.perez@email.com"
        )
        print(f"✓ Cliente creado: {cliente1}")
        
        cliente2 = cliente_service.crear_cliente(
            nombre="María Elena",
            apellido="Rodríguez López",
            dni="87654321",
            telefono="555-0202",
            email="maria.rodriguez@email.com"
        )
        print(f"✓ Cliente creado: {cliente2}")
        
        cliente3 = cliente_service.crear_cliente(
            nombre="Carlos Alberto",
            apellido="García Martínez",
            dni="11223344",
            telefono="555-0303",
            email="carlos.garcia@email.com"
        )
        print(f"✓ Cliente creado: {cliente3}")
        
        # 2. CREAR PRÉSTAMOS DE EJEMPLO
        print("\n💰 CREANDO PRÉSTAMOS DE EJEMPLO...")
        
        # Préstamo 1: Interés simple
        prestamo1 = prestamo_service.crear_prestamo(
            cliente_id=cliente1.id,
            monto=Decimal("15000"),
            tasa_interes=Decimal("12.5"),
            plazo_meses=24,
            tipo_interes="simple"
        )
        print(f"✓ Préstamo 1 creado: ${prestamo1.monto:.2f} - {prestamo1.tipo_interes}")
        print(f"  Cuota mensual: ${prestamo1.calcular_cuota_mensual():.2f}")
        print(f"  Total a pagar: ${prestamo1.calcular_monto_total():.2f}")
        
        # Préstamo 2: Interés compuesto
        prestamo2 = prestamo_service.crear_prestamo(
            cliente_id=cliente2.id,
            monto=Decimal("25000"),
            tasa_interes=Decimal("15.0"),
            plazo_meses=36,
            tipo_interes="compuesto"
        )
        print(f"✓ Préstamo 2 creado: ${prestamo2.monto:.2f} - {prestamo2.tipo_interes}")
        print(f"  Cuota mensual: ${prestamo2.calcular_cuota_mensual():.2f}")
        print(f"  Total a pagar: ${prestamo2.calcular_monto_total():.2f}")
        
        # Préstamo 3: Interés simple
        prestamo3 = prestamo_service.crear_prestamo(
            cliente_id=cliente3.id,
            monto=Decimal("8000"),
            tasa_interes=Decimal("10.0"),
            plazo_meses=12,
            tipo_interes="simple"
        )
        print(f"✓ Préstamo 3 creado: ${prestamo3.monto:.2f} - {prestamo3.tipo_interes}")
        print(f"  Cuota mensual: ${prestamo3.calcular_cuota_mensual():.2f}")
        print(f"  Total a pagar: ${prestamo3.calcular_monto_total():.2f}")
        
        # 3. REGISTRAR PAGOS DE EJEMPLO
        print("\n💳 REGISTRANDO PAGOS DE EJEMPLO...")
        
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
        
        # 4. GENERAR REPORTES DE EJEMPLO
        print("\n📊 GENERANDO REPORTES DE EJEMPLO...")
        
        # Reporte general
        stats = reporte_service.generar_reporte_general()
        print(f"📈 REPORTE GENERAL DEL SISTEMA:")
        print(f"   • Total de clientes: {stats['total_clientes']}")
        print(f"   • Total de préstamos: {stats['total_prestamos']}")
        print(f"   • Monto total prestado: ${stats['monto_total_prestado']:.2f}")
        print(f"   • Monto total pagado: ${stats['monto_total_pagado']:.2f}")
        print(f"   • Préstamos activos: {stats['prestamos_activos']}")
        print(f"   • Total de pagos: {stats['total_pagos']}")
        
        # Reporte de préstamos activos
        prestamos_activos = reporte_service.generar_reporte_prestamos_activos()
        print(f"\n💰 PRÉSTAMOS ACTIVOS:")
        for prestamo in prestamos_activos:
            print(f"   • ID {prestamo['id_prestamo']}: {prestamo['cliente']} - ${prestamo['saldo_pendiente']:.2f} pendiente")
        
        # Reporte de cliente específico
        reporte_cliente = reporte_service.generar_reporte_cliente(cliente1.id)
        print(f"\n👤 REPORTE DEL CLIENTE {cliente1.nombre} {cliente1.apellido}:")
        print(f"   • Total de préstamos: {reporte_cliente['resumen']['total_prestamos']}")
        print(f"   • Monto total prestado: ${reporte_cliente['resumen']['monto_total_prestado']:.2f}")
        print(f"   • Monto total pagado: ${reporte_cliente['resumen']['monto_total_pagado']:.2f}")
        print(f"   • Saldo total pendiente: ${reporte_cliente['resumen']['saldo_total_pendiente']:.2f}")
        
        # 5. DEMOSTRAR BÚSQUEDAS
        print("\n🔍 DEMOSTRANDO BÚSQUEDAS...")
        
        # Buscar cliente por término
        clientes_encontrados = cliente_service.buscar_cliente("Juan")
        print(f"✓ Búsqueda 'Juan' encontró {len(clientes_encontrados)} cliente(s)")
        
        # Listar préstamos de un cliente
        prestamos_cliente = prestamo_service.listar_prestamos_cliente(cliente1.id)
        print(f"✓ Cliente {cliente1.nombre} tiene {len(prestamos_cliente)} préstamo(s)")
        
        # 6. MOSTRAR RESUMENES DE PRÉSTAMOS
        print("\n📋 RESUMENES DE PRÉSTAMOS...")
        
        for i, prestamo in enumerate([prestamo1, prestamo2, prestamo3], 1):
            resumen = prestamo_service.obtener_resumen_prestamo(prestamo.id)
            print(f"\n📋 PRÉSTAMO {i}:")
            print(f"   • Cliente: {resumen['cliente']}")
            print(f"   • Monto original: ${resumen['resumen']['monto_original']:.2f}")
            print(f"   • Interés total: ${resumen['resumen']['interes_total']:.2f}")
            print(f"   • Monto total: ${resumen['resumen']['monto_total']:.2f}")
            print(f"   • Cuota mensual: ${resumen['resumen']['cuota_mensual']:.2f}")
            print(f"   • Saldo pendiente: ${resumen['resumen']['saldo_pendiente']:.2f}")
            print(f"   • Pagos realizados: {resumen['resumen']['pagos_realizados']}")
            print(f"   • Cuotas pendientes: {resumen['resumen']['cuotas_pendientes']}")
        
        print("\n🎉 ¡EJEMPLO COMPLETADO EXITOSAMENTE!")
        print("=" * 50)
        print("El sistema está listo para usar. Ejecute 'python main.py' para acceder a la interfaz completa.")
        
    except Exception as e:
        print(f"\n❌ Error durante la ejecución del ejemplo: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
