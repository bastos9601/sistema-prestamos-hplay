#!/usr/bin/env python3
"""
Script para limpiar usuarios duplicados del sistema
==================================================

Este script elimina usuarios duplicados y deja solo
un usuario administrador limpio.
"""

import json
import os
from models import Usuario

def limpiar_usuarios():
    """Limpia usuarios duplicados y deja solo el administrador"""
    print("🧹 Limpiando usuarios duplicados...")
    
    usuarios_file = "data/usuarios.json"
    
    if not os.path.exists(usuarios_file):
        print("❌ Archivo de usuarios no encontrado")
        return
    
    # Leer usuarios existentes
    with open(usuarios_file, 'r', encoding='utf-8') as f:
        usuarios_data = json.load(f)
    
    print(f"📊 Usuarios encontrados: {len(usuarios_data)}")
    
    # Crear nuevo usuario administrador limpio
    admin_limpio = Usuario(
        id=1,
        username="admin",
        password_hash=Usuario.hash_password("admin123"),
        nombre="Administrador del Sistema",
        email="admin@sistema.com",
        rol="admin",
        activo=True,
        usuario_creador_id=None
    )
    
    # Crear lista limpia con solo el administrador
    usuarios_limpios = [admin_limpio.to_dict()]
    
    # Guardar usuarios limpios
    with open(usuarios_file, 'w', encoding='utf-8') as f:
        json.dump(usuarios_limpios, f, ensure_ascii=False, indent=2)
    
    print("✅ Usuarios limpiados correctamente")
    print(f"👤 Usuario administrador creado:")
    print(f"   Usuario: {admin_limpio.username}")
    print(f"   Contraseña: admin123")
    print(f"   Nombre: {admin_limpio.nombre}")
    print(f"   Rol: {admin_limpio.rol}")

if __name__ == "__main__":
    limpiar_usuarios()
