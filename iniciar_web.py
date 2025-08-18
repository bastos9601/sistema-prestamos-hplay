#!/usr/bin/env python3
"""
Script simple para iniciar el Sistema de Préstamos Web
=====================================================

Este script solo inicia la aplicación web sin crear datos de ejemplo.
"""

import webbrowser
import time

def abrir_navegador():
    """Abre el navegador automáticamente"""
    url = "http://localhost:5000"
    print(f"\n🌐 Abriendo navegador en: {url}")
    
    try:
        webbrowser.open(url)
    except Exception as e:
        print(f"⚠️ No se pudo abrir el navegador automáticamente: {e}")
        print(f"📱 Por favor, abre manualmente: {url}")

def main():
    """Función principal"""
    print("🏦 SISTEMA DE PRÉSTAMOS DE DINERO - VERSIÓN WEB")
    print("=" * 60)
    print("📝 Iniciando aplicación web...")
    print("📝 El sistema está listo para crear clientes y préstamos manualmente")
    print("⏳ Esperando 3 segundos para que se inicie el servidor...")
    
    # Esperar un poco para que se inicie el servidor
    time.sleep(3)
    
    # Abrir navegador
    abrir_navegador()
    
    print("\n✅ ¡Aplicación web iniciada exitosamente!")
    print("📱 La aplicación está disponible en: http://localhost:5000")
    print("🔄 Para detener el servidor, presiona Ctrl+C")
    print("\n" + "=" * 60)
    
    # Ejecutar la aplicación Flask
    try:
        from app import app
        app.run(debug=True, host='0.0.0.0', port=5000)
    except ImportError as e:
        print(f"❌ Error al importar la aplicación Flask: {e}")
        print("Asegúrate de que todos los archivos estén en el mismo directorio.")
    except Exception as e:
        print(f"❌ Error al ejecutar la aplicación: {e}")

if __name__ == "__main__":
    main()
