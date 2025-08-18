#!/usr/bin/env python3
"""
Script para probar específicamente los pagos
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import Database
from services import PagoService

def main():
    print("TEST DE PAGOS")
    print("=" * 20)
    
    try:
        # Crear instancia de base de datos
        db = Database()
        
        # Crear servicio de pagos
        pago_service = PagoService(db)
        
        print("\n1. PAGOS EN LA BASE DE DATOS:")
        pagos_db = db.listar_pagos()
        print(f"   Total pagos: {len(pagos_db)}")
        for pago in pagos_db:
            print(f"   - ID: {pago.id}, Préstamo: {pago.prestamo_id}, Monto: ${pago.monto}")
        
        print("\n2. PAGOS POR PRESTAMO (ID 1):")
        pagos_prestamo = pago_service.listar_pagos_prestamo(1)
        print(f"   Cantidad: {len(pagos_prestamo)}")
        for pago in pagos_prestamo:
            print(f"   - ID: {pago.id}, Monto: ${pago.monto}, Fecha: {pago.fecha}")
        
        print("\n3. PRESTAMOS ACTIVOS:")
        prestamos = db.obtener_prestamos_activos()
        for prestamo in prestamos:
            print(f"   - ID: {prestamo.id}, Cliente: {prestamo.cliente_id}, Estado: {prestamo.estado}")
        
        print("\n4. SIMULANDO LA RUTA /pagos:")
        pagos_list = []
        for prestamo in prestamos:
            pagos_prestamo = pago_service.listar_pagos_prestamo(prestamo.id)
            print(f"   Préstamo {prestamo.id}: {len(pagos_prestamo)} pagos")
            for pago in pagos_prestamo:
                pagos_list.append({
                    'pago': pago,
                    'prestamo': prestamo,
                    'cliente': None  # No lo buscamos aquí
                })
        
        print(f"   Total pagos enriquecidos: {len(pagos_list)}")
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
