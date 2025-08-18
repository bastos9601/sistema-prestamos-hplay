#!/usr/bin/env python3
"""
Ejemplo de Uso del Sistema de Préstamos - Interfaz Gráfica
==========================================================

Este script demuestra las funcionalidades principales del sistema
creando clientes, préstamos y pagos de ejemplo, y luego abre
la interfaz gráfica para que puedas explorar los datos.
"""

from decimal import Decimal
from datetime import date
from database import Database
from services import ClienteService, PrestamoService, PagoService, ReporteService
import tkinter as tk
from tkinter import messagebox

def crear_datos_ejemplo():
    """Crea datos de ejemplo para demostrar el sistema"""
    print("🚀 CREANDO DATOS DE EJEMPLO PARA EL SISTEMA...")
    
    # Inicializar servicios
    db = Database()
    cliente_service = ClienteService(db)
    prestamo_service = PrestamoService(db)
    pago_service = PagoService(db)
    
    try:
        # 1. CREAR CLIENTES DE EJEMPLO
        print("\n👥 Creando clientes de ejemplo...")
        
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
        print("\nAhora se abrirá la interfaz gráfica para que puedas explorar los datos.")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error durante la creación de datos de ejemplo: {e}")
        import traceback
        traceback.print_exc()
        return False

def mostrar_mensaje_bienvenida():
    """Muestra un mensaje de bienvenida en la interfaz gráfica"""
    root = tk.Tk()
    root.withdraw()  # Ocultar ventana principal
    
    messagebox.showinfo(
        "¡Bienvenido al Sistema de Préstamos! 🎉",
        "Se han creado datos de ejemplo para que puedas explorar el sistema:\n\n"
        "👥 3 Clientes registrados\n"
        "💰 3 Préstamos activos\n"
        "💳 4 Pagos registrados\n\n"
        "Usa la interfaz gráfica para:\n"
        "• Gestionar clientes\n"
        "• Crear y consultar préstamos\n"
        "• Registrar pagos\n"
        "• Generar reportes\n\n"
        "¡Disfruta explorando el sistema!"
    )
    
    root.destroy()

def main():
    """Función principal"""
    print("🏦 SISTEMA DE PRÉSTAMOS DE DINERO - INTERFAZ GRÁFICA")
    print("=" * 60)
    
    # Crear datos de ejemplo
    if crear_datos_ejemplo():
        # Mostrar mensaje de bienvenida
        mostrar_mensaje_bienvenida()
        
        # Abrir la interfaz gráfica
        print("\n🖥️ Abriendo interfaz gráfica...")
        try:
            from main_gui import SistemaPrestamosGUI
            app = SistemaPrestamosGUI()
            app.ejecutar()
        except ImportError as e:
            print(f"❌ Error al importar la interfaz gráfica: {e}")
            print("Asegúrate de que todos los archivos estén en el mismo directorio.")
        except Exception as e:
            print(f"❌ Error al ejecutar la interfaz gráfica: {e}")
    else:
        print("\n❌ No se pudieron crear los datos de ejemplo.")
        print("Verifica que el sistema esté funcionando correctamente.")

if __name__ == "__main__":
    main()
