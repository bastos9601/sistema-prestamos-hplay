#!/usr/bin/env python3
"""
Script para reiniciar completamente la base de datos
==================================================

Este script elimina todos los datos existentes y crea una base de datos
limpia con solo el usuario administrador.
"""

import os
import json
import shutil
from models import Usuario

def reiniciar_base_datos():
    """Reinicia completamente la base de datos"""
    print("🔄 Reiniciando base de datos...")
    
    data_dir = "data"
    
    # 1. Hacer backup de la base de datos actual
    if os.path.exists(data_dir):
        backup_dir = "data_backup"
        if os.path.exists(backup_dir):
            shutil.rmtree(backup_dir)
        shutil.copytree(data_dir, backup_dir)
        print(f"✅ Backup creado en: {backup_dir}")
    
    # 2. Eliminar directorio de datos
    if os.path.exists(data_dir):
        shutil.rmtree(data_dir)
        print("🗑️  Directorio de datos eliminado")
    
    # 3. Crear nuevo directorio de datos
    os.makedirs(data_dir, exist_ok=True)
    print("📁 Nuevo directorio de datos creado")
    
    # 4. Crear archivos JSON vacíos
    archivos = [
        "clientes.json",
        "prestamos.json", 
        "pagos.json"
    ]
    
    for archivo in archivos:
        archivo_path = os.path.join(data_dir, archivo)
        with open(archivo_path, 'w', encoding='utf-8') as f:
            json.dump([], f, ensure_ascii=False, indent=2)
        print(f"📄 Archivo {archivo} creado (vacío)")
    
    # 5. Crear usuario administrador
    print("\n👤 Creando usuario administrador...")
    
    admin = Usuario(
        id=1,
        username="admin",
        password_hash=Usuario.hash_password("admin123"),
        nombre="Administrador del Sistema",
        email="admin@sistema.com",
        rol="admin",
        activo=True,
        usuario_creador_id=None
    )
    
    usuarios_data = [admin.to_dict()]
    usuarios_file = os.path.join(data_dir, "usuarios.json")
    
    with open(usuarios_file, 'w', encoding='utf-8') as f:
        json.dump(usuarios_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Usuario administrador creado:")
    print(f"   Usuario: {admin.username}")
    print(f"   Contraseña: admin123")
    print(f"   Nombre: {admin.nombre}")
    print(f"   Rol: {admin.rol}")
    
    print("\n🎉 ¡Base de datos reiniciada exitosamente!")
    print("📱 Puedes acceder al sistema con:")
    print("   Usuario: admin")
    print("   Contraseña: admin123")
    print("\n⚠️  IMPORTANTE: Todos los datos anteriores han sido eliminados")
    print(f"💾 Backup disponible en: {backup_dir}")

def mostrar_estado():
    """Muestra el estado actual de la base de datos"""
    print("\n📊 Estado de la Base de Datos:")
    print("=" * 50)
    
    data_dir = "data"
    
    if not os.path.exists(data_dir):
        print("❌ Directorio de datos no encontrado")
        return
    
    archivos = [
        "usuarios.json",
        "clientes.json",
        "prestamos.json",
        "pagos.json"
    ]
    
    for archivo in archivos:
        archivo_path = os.path.join(data_dir, archivo)
        if os.path.exists(archivo_path):
            with open(archivo_path, 'r', encoding='utf-8') as f:
                try:
                    data = json.load(f)
                    print(f"📄 {archivo}: {len(data)} registros")
                except:
                    print(f"📄 {archivo}: Error al leer")
        else:
            print(f"📄 {archivo}: No encontrado")

if __name__ == "__main__":
    try:
        print("🚨 ADVERTENCIA: Este script eliminará TODOS los datos existentes!")
        print("💾 Se creará un backup automáticamente")
        
        confirmacion = input("\n¿Estás seguro de que quieres continuar? (escribe 'SI' para confirmar): ")
        
        if confirmacion == "SI":
            reiniciar_base_datos()
            mostrar_estado()
            
            print("\n🎯 Próximos pasos:")
            print("1. Ejecuta la aplicación: python app.py")
            print("2. Accede con: admin / admin123")
            print("3. Comienza a crear nuevos clientes, préstamos y pagos")
            
        else:
            print("❌ Operación cancelada")
            
    except Exception as e:
        print(f"\n❌ Error durante el reinicio: {e}")
        import traceback
        traceback.print_exc()
