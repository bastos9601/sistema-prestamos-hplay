#!/usr/bin/env python3
"""
Script para crear un usuario supervisor en el sistema
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import Database
from models import Usuario

def crear_supervisor():
    """Crea un usuario supervisor para probar la funcionalidad"""
    db = Database()
    
    # Crear usuario supervisor
    supervisor = Usuario(
        id=0,  # Se asignará automáticamente
        username="supervisor",
        password_hash=Usuario.hash_password("supervisor123"),
        nombre="Supervisor del Sistema",
        email="supervisor@sistema.com",
        rol="supervisor",
        activo=True
    )
    
    try:
        # Agregar el supervisor al sistema (creado por el admin)
        supervisor_creado = db.agregar_usuario(supervisor, usuario_creador_id=1)
        print(f"✅ Usuario supervisor creado exitosamente:")
        print(f"   ID: {supervisor_creado.id}")
        print(f"   Username: {supervisor_creado.username}")
        print(f"   Contraseña: supervisor123")
        print(f"   Rol: {supervisor_creado.rol}")
        print(f"   Permisos: {supervisor_creado.permisos}")
        
    except Exception as e:
        print(f"❌ Error al crear el supervisor: {e}")

if __name__ == "__main__":
    crear_supervisor()
