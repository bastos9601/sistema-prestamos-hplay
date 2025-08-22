#!/usr/bin/env python3
"""
Script para migrar clientes existentes al sistema multi-usuario
=============================================================

Este script asigna un usuario_id a los clientes que no lo tienen
para que funcionen correctamente con el sistema multi-usuario.
"""

import json
import os
from models import Cliente

def migrar_clientes():
    """Migra clientes existentes al sistema multi-usuario"""
    print("🔄 Migrando clientes al sistema multi-usuario...")
    
    clientes_file = "data/clientes.json"
    
    if not os.path.exists(clientes_file):
        print("❌ Archivo de clientes no encontrado")
        return
    
    # Leer clientes existentes
    with open(clientes_file, 'r', encoding='utf-8') as f:
        clientes_data = json.load(f)
    
    print(f"📊 Clientes encontrados: {len(clientes_data)}")
    
    # Contar clientes sin usuario_id
    clientes_sin_usuario = [c for c in clientes_data if c.get('usuario_id') is None]
    print(f"⚠️  Clientes sin usuario_id: {len(clientes_sin_usuario)}")
    
    if not clientes_sin_usuario:
        print("✅ Todos los clientes ya tienen usuario_id asignado")
        return
    
    # Asignar usuario_id = 1 (administrador) a clientes sin usuario_id
    for cliente in clientes_data:
        if cliente.get('usuario_id') is None:
            cliente['usuario_id'] = 1  # Asignar al administrador
            print(f"   📝 Cliente '{cliente['nombre']} {cliente['apellido']}' asignado al administrador")
    
    # Guardar clientes migrados
    with open(clientes_file, 'w', encoding='utf-8') as f:
        json.dump(clientes_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Migración completada: {len(clientes_sin_usuario)} clientes migrados")
    print("🎯 Todos los clientes ahora tienen usuario_id asignado")

def mostrar_estado_clientes():
    """Muestra el estado actual de los clientes"""
    print("\n📊 Estado de los Clientes:")
    print("=" * 50)
    
    clientes_file = "data/clientes.json"
    
    if not os.path.exists(clientes_file):
        print("❌ Archivo de clientes no encontrado")
        return
    
    with open(clientes_file, 'r', encoding='utf-8') as f:
        clientes_data = json.load(f)
    
    # Agrupar por usuario_id
    por_usuario = {}
    sin_usuario = []
    
    for cliente in clientes_data:
        usuario_id = cliente.get('usuario_id')
        if usuario_id is None:
            sin_usuario.append(cliente)
        else:
            if usuario_id not in por_usuario:
                por_usuario[usuario_id] = []
            por_usuario[usuario_id].append(cliente)
    
    print(f"👥 Total de clientes: {len(clientes_data)}")
    print(f"✅ Con usuario_id: {len(clientes_data) - len(sin_usuario)}")
    print(f"⚠️  Sin usuario_id: {len(sin_usuario)}")
    
    for usuario_id, clientes in por_usuario.items():
        activos = len([c for c in clientes if c.get('activo', True)])
        print(f"   Usuario {usuario_id}: {len(clientes)} clientes ({activos} activos)")
    
    if sin_usuario:
        print(f"\n⚠️  Clientes sin usuario_id:")
        for cliente in sin_usuario:
            print(f"   - {cliente['nombre']} {cliente['apellido']} (DNI: {cliente['dni']})")

if __name__ == "__main__":
    try:
        mostrar_estado_clientes()
        migrar_clientes()
        mostrar_estado_clientes()
        
        print("\n🎉 Migración completada exitosamente!")
        print("📱 Ahora puedes acceder al sistema y ver las estadísticas correctas")
        
    except Exception as e:
        print(f"\n❌ Error durante la migración: {e}")
        import traceback
        traceback.print_exc()
