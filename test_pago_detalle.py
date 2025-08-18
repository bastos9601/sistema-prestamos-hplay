#!/usr/bin/env python3
"""
Script para ver los campos detallados de un pago
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import Database
from services import PagoService

def main():
    print("TEST DETALLADO DE PAGO")
    print("=" * 30)
    
    try:
        # Crear instancia de base de datos
        db = Database()
        
        # Crear servicio de pagos
        pago_service = PagoService(db)
        
        print("\n1. PAGO ESPECÍFICO (ID 1):")
        pagos = pago_service.listar_pagos_prestamo(1)
        if pagos:
            pago = pagos[0]  # Primer pago
            print(f"   ID: {pago.id}")
            print(f"   Monto: ${pago.monto}")
            print(f"   Fecha: {pago.fecha}")
            print(f"   Concepto: {pago.concepto}")
            print(f"   Préstamo ID: {pago.prestamo_id}")
            
            # Verificar si tiene saldo_despues
            if hasattr(pago, 'saldo_despues'):
                print(f"   Saldo Después: ${pago.saldo_despues}")
            else:
                print(f"   Saldo Después: NO TIENE ESTE CAMPO")
            
            # Ver todos los atributos del pago
            print(f"\n   Todos los atributos:")
            for attr in dir(pago):
                if not attr.startswith('_'):
                    try:
                        value = getattr(pago, attr)
                        if not callable(value):
                            print(f"     {attr}: {value}")
                    except:
                        pass
        
        print("\n2. PRESTAMO ASOCIADO:")
        prestamo = db.obtener_prestamo(1)
        if prestamo:
            print(f"   ID: {prestamo.id}")
            print(f"   Monto: ${prestamo.monto}")
            print(f"   Tipo Interés: {prestamo.tipo_interes}")
            print(f"   Estado: {prestamo.estado}")
            
            # Calcular saldo pendiente
            saldo = prestamo.calcular_saldo_pendiente()
            print(f"   Saldo Pendiente: ${saldo}")
            
            # Ver pagos del préstamo
            pagos_prestamo = prestamo.pagos
            print(f"   Pagos en préstamo: {len(pagos_prestamo)}")
            for p in pagos_prestamo:
                print(f"     - Pago ${p.monto}")
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
