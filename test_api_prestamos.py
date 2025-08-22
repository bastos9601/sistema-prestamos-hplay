#!/usr/bin/env python3
"""
Script de prueba para verificar la API de préstamos activos
"""

import requests
import json
import sys

def test_api_prestamos_activos():
    """Prueba la API de préstamos activos"""
    print("🧪 Probando API de préstamos activos...")
    
    try:
        # URL de la API
        url = "http://localhost:5000/api/prestamos-activos"
        
        print(f"📡 Haciendo petición a: {url}")
        
        # Hacer la petición GET
        response = requests.get(url, timeout=10)
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📋 Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"✅ Datos recibidos: {json.dumps(data, indent=2, ensure_ascii=False)}")
                
                if isinstance(data, list):
                    print(f"📊 Tipo: Array con {len(data)} elementos")
                    for i, prestamo in enumerate(data):
                        print(f"📋 Préstamo {i+1}:")
                        for key, value in prestamo.items():
                            print(f"   {key}: {value}")
                else:
                    print(f"⚠️  Los datos no son un array: {type(data)}")
                    
            except json.JSONDecodeError as e:
                print(f"❌ Error al decodificar JSON: {e}")
                print(f"📄 Contenido de respuesta: {response.text}")
                
        else:
            print(f"❌ Error HTTP: {response.status_code}")
            print(f"📄 Contenido de respuesta: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Error de conexión: No se pudo conectar al servidor")
        print("💡 Asegúrate de que la aplicación esté ejecutándose en localhost:5000")
    except requests.exceptions.Timeout:
        print("❌ Error de timeout: La petición tardó demasiado")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

def test_api_reporte_general():
    """Prueba la API de reporte general"""
    print("\n🧪 Probando API de reporte general...")
    
    try:
        url = "http://localhost:5000/api/reporte-general"
        print(f"📡 Haciendo petición a: {url}")
        
        response = requests.get(url, timeout=10)
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Datos recibidos: {json.dumps(data, indent=2, ensure_ascii=False)}")
        else:
            print(f"❌ Error HTTP: {response.status_code}")
            print(f"📄 Contenido: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🚀 Iniciando pruebas de API...")
    print("=" * 50)
    
    test_api_prestamos_activos()
    test_api_reporte_general()
    
    print("=" * 50)
    print("✅ Pruebas completadas")
