#!/usr/bin/env python3
"""
Script simple para probar la base de datos
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import Database
from services import ReporteService

def main():
    print("TEST DE BASE DE DATOS")
    print("=" * 30)
    
    try:
        # Crear instancia de base de datos
        db = Database()
        
        # Crear servicio de reportes
        reporte_service = ReporteService(db)
        
        print("\n1. OBTENIENDO ESTADISTICAS:")
        stats = db.obtener_estadisticas()
        for key, value in stats.items():
            print(f"   {key}: {value}")
        
        print("\n2. OBTENIENDO PRESTAMOS ACTIVOS:")
        prestamos_activos = db.obtener_prestamos_activos()
        print(f"   Cantidad: {len(prestamos_activos)}")
        for p in prestamos_activos:
            print(f"   - ID: {p.id}, Monto: ${p.monto}, Estado: {p.estado}")
        
        print("\n3. PROBANDO SERVICIO DE REPORTES:")
        reporte_general = reporte_service.generar_reporte_general()
        print(f"   Reporte general: {reporte_general}")
        
        print("\n4. PROBANDO REPORTE DE PRESTAMOS ACTIVOS:")
        prestamos_report = reporte_service.generar_reporte_prestamos_activos()
        print(f"   Cantidad en reporte: {len(prestamos_report)}")
        for p in prestamos_report:
            print(f"   - {p}")
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
