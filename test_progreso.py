#!/usr/bin/env python3
"""
Script para probar el cálculo del progreso
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import Database
from services import PagoService

def main():
    print("TEST DE PROGRESO")
    print("=" * 20)
    
    try:
        # Crear instancia de base de datos
        db = Database()
        
        # Obtener préstamo
        prestamo = db.obtener_prestamo(1)
        if prestamo:
            print(f"Préstamo ID: {prestamo.id}")
            print(f"Tipo Interés: {prestamo.tipo_interes}")
            print(f"Monto: ${prestamo.monto}")
            print(f"Estado: {prestamo.estado}")
            
            # Calcular valores para el progreso
            monto_total = prestamo.calcular_monto_total()
            intereses_pagados = prestamo.calcular_intereses_pagados()
            saldo_pendiente = prestamo.calcular_saldo_pendiente()
            
            print(f"\nValores para progreso:")
            print(f"  Monto Total: ${monto_total}")
            print(f"  Intereses Pagados: ${intereses_pagados}")
            print(f"  Saldo Pendiente: ${saldo_pendiente}")
            
            # Calcular progreso
            if monto_total > 0:
                progreso = (intereses_pagados / monto_total * 100)
                print(f"  Progreso: {progreso:.1f}%")
            else:
                print(f"  Progreso: No se puede calcular")
            
            # Ver pagos
            print(f"\nPagos:")
            for pago in prestamo.pagos:
                print(f"  - Pago ${pago.monto}, Saldo después: ${pago.saldo_despues}")
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
