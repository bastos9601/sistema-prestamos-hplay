#!/usr/bin/env python3
"""
Script para inicializar el sistema de préstamos multi-usuario
===========================================================

Este script crea un usuario administrador por defecto y configura
el sistema para funcionar con múltiples usuarios.
"""

import os
import sys
from models import Usuario
from database import Database

def inicializar_sistema():
    """Inicializa el sistema con un usuario administrador por defecto"""
    print("🚀 Inicializando Sistema de Préstamos Multi-Usuario...")
    
    # Crear instancia de la base de datos
    db = Database()
    
    # Verificar si ya existe un usuario administrador
    usuarios_existentes = db.listar_usuarios(0, False)  # 0 como placeholder para no usuario
    admin_existente = any(u.rol == 'admin' for u in usuarios_existentes)
    
    if admin_existente:
        print("✅ Ya existe un usuario administrador en el sistema")
        return
    
    # Crear usuario administrador por defecto
    print("👤 Creando usuario administrador por defecto...")
    
    admin = Usuario(
        id=0,  # Se asignará automáticamente
        username="admin",
        password_hash=Usuario.hash_password("admin123"),
        nombre="Administrador del Sistema",
        email="admin@sistema.com",
        rol="admin",
        activo=True,
        usuario_creador_id=None  # El primer admin no tiene creador
    )
    
    try:
        # Agregar el administrador (usando 0 como placeholder para no usuario)
        admin_creado = db.agregar_usuario(admin, 0)
        print(f"✅ Usuario administrador creado exitosamente:")
        print(f"   Usuario: {admin_creado.username}")
        print(f"   Contraseña: admin123")
        print(f"   Nombre: {admin_creado.nombre}")
        print(f"   Rol: {admin_creado.rol}")
        print("\n⚠️  IMPORTANTE: Cambia la contraseña del administrador después del primer login!")
        
    except Exception as e:
        print(f"❌ Error al crear usuario administrador: {e}")
        return
    
    print("\n🎉 Sistema inicializado correctamente!")
    print("📱 Puedes acceder al sistema con:")
    print("   Usuario: admin")
    print("   Contraseña: admin123")

def mostrar_estado_sistema():
    """Muestra el estado actual del sistema"""
    print("\n📊 Estado del Sistema:")
    print("=" * 50)
    
    db = Database()
    
    try:
        # Contar usuarios
        usuarios = db.listar_usuarios(0, False)
        print(f"👥 Usuarios totales: {len(usuarios)}")
        
        # Contar por rol
        roles = {}
        for usuario in usuarios:
            rol = usuario.rol
            roles[rol] = roles.get(rol, 0) + 1
        
        for rol, cantidad in roles.items():
            print(f"   - {rol.capitalize()}: {cantidad}")
        
        # Contar clientes
        clientes = db.listar_clientes(0, False)
        print(f"👤 Clientes totales: {len(clientes)}")
        
        # Contar préstamos
        prestamos = db.listar_prestamos(0, False)
        print(f"💰 Préstamos totales: {len(prestamos)}")
        
        # Contar pagos
        pagos = db.listar_pagos(0, False)
        print(f"💳 Pagos totales: {len(pagos)}")
        
    except Exception as e:
        print(f"❌ Error al obtener estadísticas: {e}")

if __name__ == "__main__":
    try:
        inicializar_sistema()
        mostrar_estado_sistema()
        
        print("\n🎯 Próximos pasos:")
        print("1. Ejecuta la aplicación web: python app.py")
        print("2. Accede con usuario: admin, contraseña: admin123")
        print("3. Cambia la contraseña del administrador")
        print("4. Crea usuarios adicionales desde el panel de administración")
        print("5. Cada usuario podrá gestionar sus propios clientes, préstamos y pagos")
        
    except Exception as e:
        print(f"❌ Error durante la inicialización: {e}")
        sys.exit(1)
