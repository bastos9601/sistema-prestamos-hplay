#!/usr/bin/env python3
"""
Script para probar el sistema de pagaré
======================================

Este script prueba la generación de pagarés sin necesidad de
tener WhatsApp configurado.
"""

from models import Cliente, Prestamo
from pagare_generator import PagareGenerator
from datetime import datetime, date
from decimal import Decimal

def test_pagare():
    """Prueba la generación de pagarés"""
    print("📋 Probando sistema de pagaré...")
    
    # Crear cliente de prueba
    cliente = Cliente(
        id=1,
        nombre="Juan",
        apellido="Pérez",
        dni="12345678",
        telefono="+54 9 11 1234-5678",
        email="juan.perez@email.com",
        usuario_id=1
    )
    
    # Crear préstamo de prueba
    prestamo = Prestamo(
        id=1,
        cliente_id=1,
        monto=Decimal('50000.0'),
        plazo_dias=90,
        tasa_interes=Decimal('5.0'),
        tipo_interes="simple",
        fecha_inicio=date.today(),
        usuario_id=1
    )
    
    # Crear generador de pagaré
    generador = PagareGenerator()
    
    try:
        # 1. Generar pagaré en texto
        print("\n1. Generando pagaré en texto...")
        pagare_texto = generador.generar_pagare(cliente, prestamo)
        print("✅ Pagaré en texto generado:")
        print("-" * 50)
        print(pagare_texto)
        print("-" * 50)
        
        # 2. Generar pagaré en HTML
        print("\n2. Generando pagaré en HTML...")
        pagare_html = generador.generar_pagare_html(cliente, prestamo)
        print("✅ Pagaré en HTML generado")
        
        # 3. Guardar pagaré como archivo
        print("\n3. Guardando pagaré como archivo...")
        archivo_pagare = generador.guardar_pagare_archivo(cliente, prestamo)
        
        if archivo_pagare:
            print(f"✅ Pagaré guardado en: {archivo_pagare}")
            print("📁 Puedes abrir este archivo en tu navegador para ver el pagaré")
        else:
            print("❌ Error al guardar pagaré")
        
        # 4. Probar envío por WhatsApp (simulado)
        print("\n4. Probando envío por WhatsApp...")
        if hasattr(generador.whatsapp, 'access_token') and generador.whatsapp.access_token:
            print("✅ WhatsApp configurado, enviando pagaré...")
            resultado = generador.enviar_pagare_whatsapp(cliente, prestamo)
            if resultado:
                print("✅ Pagaré enviado por WhatsApp")
            else:
                print("❌ Error al enviar por WhatsApp")
        else:
            print("⚠️  WhatsApp no configurado")
            print("📱 Para configurar WhatsApp, ejecuta: python config_whatsapp.py")
        
        print("\n🎉 Prueba del sistema de pagaré completada!")
        print("\n📋 Resumen:")
        print(f"   • Cliente: {cliente.nombre} {cliente.apellido}")
        print(f"   • Préstamo: ${prestamo.monto:,.2f}")
        print(f"   • Plazo: {prestamo.plazo_dias} días")
        print(f"   • Tasa: {prestamo.tasa_interes}% mensual")
        print(f"   • Pagaré: {archivo_pagare or 'No guardado'}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error durante la prueba: {e}")
        import traceback
        traceback.print_exc()
        return False

def mostrar_instrucciones():
    """Muestra instrucciones para usar el sistema"""
    print("\n📚 INSTRUCCIONES DE USO:")
    print("=" * 50)
    print("1. **Crear Cliente**: Primero crea un cliente con teléfono")
    print("2. **Crear Préstamo**: Al crear un préstamo, se genera automáticamente el pagaré")
    print("3. **Pagaré Automático**: El sistema genera y envía el pagaré por WhatsApp")
    print("4. **Archivos HTML**: Los pagarés se guardan como archivos HTML")
    print("5. **Configurar WhatsApp**: Ejecuta 'python config_whatsapp.py' para configurar")
    
    print("\n🔧 CONFIGURACIÓN DE WHATSAPP:")
    print("1. Ve a https://developers.facebook.com/")
    print("2. Crea una aplicación con WhatsApp Business API")
    print("3. Obtén Phone Number ID y Access Token")
    print("4. Configura las variables de entorno en .env")
    print("5. Reinicia la aplicación")

if __name__ == "__main__":
    try:
        print("🧪 SISTEMA DE PRUEBA DE PAGARÉ")
        print("=" * 50)
        
        resultado = test_pagare()
        
        if resultado:
            mostrar_instrucciones()
        else:
            print("\n❌ La prueba falló. Revisa los errores arriba.")
            
    except Exception as e:
        print(f"\n❌ Error fatal: {e}")
        import traceback
        traceback.print_exc()
