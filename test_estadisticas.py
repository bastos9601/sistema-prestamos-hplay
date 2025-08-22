#!/usr/bin/env python3
"""
Script para probar las estadísticas del sistema
==============================================

Este script verifica que las estadísticas se generen correctamente
para el usuario administrador.
"""

from database import Database
from services import ReporteService

def test_estadisticas():
    """Prueba las estadísticas del sistema"""
    print("📊 Probando estadísticas del sistema...")
    
    # Crear instancia de la base de datos
    db = Database()
    
    try:
        # 1. Probar estadísticas como administrador
        print("\n1. Estadísticas como administrador:")
        reporte_service = ReporteService(db)
        stats_admin = reporte_service.generar_reporte_general(1, True)  # usuario_id=1, es_admin=True
        
        print(f"   Total Clientes: {stats_admin['total_clientes']}")
        print(f"   Total Préstamos: {stats_admin['total_prestamos']}")
        print(f"   Monto Prestado: ${stats_admin['monto_total_prestado']:.2f}")
        print(f"   Préstamos Activos: {stats_admin['prestamos_activos']}")
        print(f"   Total Pagos: {stats_admin['total_pagos']}")
        
        # 2. Verificar que los números sean correctos
        if stats_admin['total_clientes'] > 0:
            print("✅ Las estadísticas están funcionando correctamente")
            print("🎯 Ahora el dashboard debería mostrar los números correctos")
        else:
            print("❌ Las estadísticas muestran 0 clientes")
            
        # 3. Mostrar detalles de clientes
        print(f"\n2. Detalles de clientes:")
        clientes = db.listar_clientes(1, True)  # Admin ve todos los clientes
        print(f"   Clientes totales: {len(clientes)}")
        
        for cliente in clientes:
            estado = "Activo" if cliente.activo else "Inactivo"
            print(f"   - {cliente.nombre} {cliente.apellido} (DNI: {cliente.dni}) - {estado}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error durante las pruebas: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_estadisticas()
