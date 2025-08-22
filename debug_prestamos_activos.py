#!/usr/bin/env python3
"""
Script de diagnóstico para verificar la API de préstamos activos
"""

import requests
import json

def test_api_prestamos_activos():
    """Prueba la API de préstamos activos"""
    print("🔍 Probando API de préstamos activos...")
    
    try:
        # Simular una sesión de usuario (necesitamos estar logueados)
        session = requests.Session()
        
        # Primero hacer login (simular)
        print("📝 Simulando login...")
        
        # Probar la API directamente
        url = "http://localhost:5000/api/prestamos-activos"
        print(f"🌐 URL: {url}")
        
        # Hacer la petición
        response = session.get(url)
        print(f"📡 Status Code: {response.status_code}")
        print(f"📋 Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Respuesta exitosa:")
            print(f"📊 Tipo de datos: {type(data)}")
            print(f"📊 Longitud: {len(data) if isinstance(data, list) else 'No es lista'}")
            print(f"📊 Contenido: {json.dumps(data, indent=2, default=str)}")
        else:
            print(f"❌ Error en la respuesta:")
            print(f"📋 Contenido: {response.text}")
            
    except Exception as e:
        print(f"❌ Error al probar la API: {e}")

def test_api_reporte_general():
    """Prueba la API de reporte general"""
    print("\n🔍 Probando API de reporte general...")
    
    try:
        session = requests.Session()
        url = "http://localhost:5000/api/reporte-general"
        print(f"🌐 URL: {url}")
        
        response = session.get(url)
        print(f"📡 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Respuesta exitosa:")
            print(f"📊 Tipo de datos: {type(data)}")
            print(f"📊 Contenido: {json.dumps(data, indent=2, default=str)}")
        else:
            print(f"❌ Error en la respuesta:")
            print(f"📋 Contenido: {response.text}")
            
    except Exception as e:
        print(f"❌ Error al probar la API: {e}")

if __name__ == "__main__":
    print("🚀 Iniciando diagnóstico de APIs...")
    print("=" * 50)
    
    test_api_reporte_general()
    test_api_prestamos_activos()
    
    print("\n" + "=" * 50)
    print("✅ Diagnóstico completado")
