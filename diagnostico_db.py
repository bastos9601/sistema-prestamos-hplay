#!/usr/bin/env python3
"""
Script de diagnóstico para verificar el estado de la base de datos
"""

import json
import os
from decimal import Decimal
from datetime import datetime, date

def cargar_json(archivo):
    """Carga un archivo JSON"""
    try:
        if os.path.exists(archivo):
            with open(archivo, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    except Exception as e:
        print(f"Error al cargar {archivo}: {e}")
        return []

def main():
    print("🔍 DIAGNÓSTICO DE LA BASE DE DATOS")
    print("=" * 50)
    
    # Verificar archivos de datos
    data_dir = "data"
    clientes_file = os.path.join(data_dir, "clientes.json")
    prestamos_file = os.path.join(data_dir, "prestamos.json")
    pagos_file = os.path.join(data_dir, "pagos.json")
    
    print(f"\n📁 Directorio de datos: {data_dir}")
    print(f"📄 Archivo clientes: {clientes_file}")
    print(f"📄 Archivo préstamos: {prestamos_file}")
    print(f"📄 Archivo pagos: {pagos_file}")
    
    # Cargar datos
    clientes = cargar_json(clientes_file)
    prestamos = cargar_json(prestamos_file)
    pagos = cargar_json(pagos_file)
    
    print(f"\n📊 ESTADÍSTICAS:")
    print(f"   👥 Total clientes: {len(clientes)}")
    print(f"   💰 Total préstamos: {len(prestamos)}")
    print(f"   💳 Total pagos: {len(pagos)}")
    
    # Analizar clientes
    if clientes:
        print(f"\n👥 CLIENTES:")
        for cliente in clientes:
            print(f"   ID: {cliente.get('id')}, Nombre: {cliente.get('nombre')} {cliente.get('apellido')}, Activo: {cliente.get('activo', True)}")
    
    # Analizar préstamos
    if prestamos:
        print(f"\n💰 PRÉSTAMOS:")
        for prestamo in prestamos:
            print(f"   ID: {prestamo.get('id')}, Cliente ID: {prestamo.get('cliente_id')}, Monto: ${prestamo.get('monto')}, Estado: {prestamo.get('estado')}")
    
    # Analizar pagos
    if pagos:
        print(f"\n💳 PAGOS:")
        for pago in pagos:
            print(f"   ID: {pago.get('id')}, Préstamo ID: {pago.get('prestamo_id')}, Monto: ${pago.get('monto')}")
    
    # Verificar consistencia
    print(f"\n🔍 VERIFICACIÓN DE CONSISTENCIA:")
    
    # Verificar que los préstamos tengan clientes válidos
    clientes_ids = {c['id'] for c in clientes}
    prestamos_sin_cliente = [p for p in prestamos if p.get('cliente_id') not in clientes_ids]
    if prestamos_sin_cliente:
        print(f"   ⚠️  Préstamos sin cliente válido: {len(prestamos_sin_cliente)}")
    
    # Verificar que los pagos tengan préstamos válidos
    prestamos_ids = {p['id'] for p in prestamos}
    pagos_sin_prestamo = [p for p in pagos if p.get('prestamo_id') not in prestamos_ids]
    if pagos_sin_prestamo:
        print(f"   ⚠️  Pagos sin préstamo válido: {len(pagos_sin_prestamo)}")
    
    # Calcular estadísticas del reporte
    print(f"\n📈 ESTADÍSTICAS DEL REPORTE:")
    prestamos_activos = [p for p in prestamos if p.get('estado') == 'activo']
    total_prestado = sum(Decimal(str(p.get('monto', 0))) for p in prestamos)
    total_pagado = sum(Decimal(str(p.get('monto', 0))) for p in pagos)
    
    print(f"   🟢 Préstamos activos: {len(prestamos_activos)}")
    print(f"   💵 Total prestado: ${total_prestado}")
    print(f"   💳 Total pagado: ${total_pagado}")
    
    if not prestamos_activos:
        print(f"   ❌ PROBLEMA: No hay préstamos activos")
        if prestamos:
            print(f"      Estados de préstamos: {[p.get('estado') for p in prestamos]}")
    
    print(f"\n✅ Diagnóstico completado")

if __name__ == "__main__":
    main()
