#!/usr/bin/env python3
"""
Script para recalcular los saldos de los pagos existentes
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import Database
from models import Pago

def main():
    print("RECALCULANDO SALDOS DE PAGOS")
    print("=" * 40)
    
    try:
        # Crear instancia de base de datos
        db = Database()
        
        # Obtener préstamo
        prestamo = db.obtener_prestamo(1)
        if not prestamo:
            print("No se encontró el préstamo")
            return
        
        print(f"Préstamo ID: {prestamo.id}")
        print(f"Tipo Interés: {prestamo.tipo_interes}")
        print(f"Monto: ${prestamo.monto}")
        
        # Recalcular saldos para cada pago
        monto_total = prestamo.calcular_monto_total()
        pagos_acumulados = Decimal('0')
        
        print(f"\nMonto Total: ${monto_total}")
        print(f"Recalculando saldos...")
        
        for i, pago in enumerate(prestamo.pagos):
            # El saldo después es el total menos los pagos anteriores
            pago.saldo_despues = monto_total - pagos_acumulados
            pagos_acumulados += pago.monto
            
            print(f"  Pago {i+1}: ${pago.monto} → Saldo después: ${pago.saldo_despues}")
        
        # Guardar los cambios
        if db.actualizar_prestamo(prestamo):
            print(f"\n✅ Saldos actualizados correctamente")
        else:
            print(f"\n❌ Error al actualizar préstamo")
        
        # Verificar resultado
        print(f"\nVerificando resultado:")
        prestamo_actualizado = db.obtener_prestamo(1)
        for pago in prestamo_actualizado.pagos:
            print(f"  Pago ${pago.monto}: Saldo después = ${pago.saldo_despues}")
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    from decimal import Decimal
    main()
