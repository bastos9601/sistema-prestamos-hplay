#!/usr/bin/env python3
"""
Script de diagnóstico para usuarios supervisores
"""

import json
import os
from datetime import datetime

def cargar_json(archivo):
    """Carga un archivo JSON"""
    try:
        if os.path.exists(archivo):
            with open(archivo, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    except Exception as e:
        print(f"❌ Error al cargar {archivo}: {e}")
        return []

def diagnostico_supervisor():
    """Diagnóstico específico para supervisores"""
    print("🔍 Diagnóstico para Usuarios Supervisores")
    print("=" * 50)
    
    # Cargar datos
    usuarios = cargar_json('data/usuarios.json')
    clientes = cargar_json('data/clientes.json')
    prestamos = cargar_json('data/prestamos.json')
    pagos = cargar_json('data/pagos.json')
    
    print(f"📊 Datos cargados:")
    print(f"   👥 Usuarios: {len(usuarios)}")
    print(f"   👤 Clientes: {len(clientes)}")
    print(f"   💰 Préstamos: {len(prestamos)}")
    print(f"   💳 Pagos: {len(pagos)}")
    
    # Identificar supervisores
    supervisores = [u for u in usuarios if u.get('rol') in ['supervisor', 'consultor']]
    admins = [u for u in usuarios if u.get('rol') == 'admin']
    usuarios_normales = [u for u in usuarios if u.get('rol') not in ['admin', 'supervisor', 'consultor']]
    
    print(f"\n👥 Distribución de usuarios:")
    print(f"   👑 Admins: {len(admins)}")
    print(f"   👁️ Supervisores/Consultores: {len(supervisores)}")
    print(f"   👤 Usuarios normales: {len(usuarios_normales)}")
    
    # Mostrar supervisores
    if supervisores:
        print(f"\n👁️ Supervisores encontrados:")
        for sup in supervisores:
            print(f"   ID: {sup['id']}, Username: {sup['username']}, Rol: {sup['rol']}")
    
    # Analizar préstamos por usuario
    print(f"\n💰 Análisis de préstamos por usuario:")
    prestamos_por_usuario = {}
    for prestamo in prestamos:
        usuario_id = prestamo.get('usuario_id')
        if usuario_id not in prestamos_por_usuario:
            prestamos_por_usuario[usuario_id] = []
        prestamos_por_usuario[usuario_id].append(prestamo)
    
    for usuario_id, prestamos_usuario in prestamos_por_usuario.items():
        # Encontrar información del usuario
        usuario_info = None
        for u in usuarios:
            if u['id'] == usuario_id:
                usuario_info = u
                break
        
        if usuario_info:
            rol = usuario_info.get('rol', 'desconocido')
            username = usuario_info.get('username', 'N/A')
            prestamos_activos = [p for p in prestamos_usuario if p.get('estado') == 'activo']
            
            print(f"   👤 Usuario {username} (ID: {usuario_id}, Rol: {rol}):")
            print(f"      Total préstamos: {len(prestamos_usuario)}")
            print(f"      Préstamos activos: {len(prestamos_activos)}")
            
            # Mostrar detalles de préstamos activos
            for prestamo in prestamos_activos:
                # Encontrar cliente
                cliente_info = None
                for c in clientes:
                    if c['id'] == prestamo.get('cliente_id'):
                        cliente_info = c
                        break
                
                if cliente_info:
                    print(f"      📋 Préstamo #{prestamo['id']}: ${prestamo['monto']} - {cliente_info['nombre']} {cliente_info['apellido']}")
    
    # Analizar qué debería ver un supervisor
    print(f"\n👁️ Lo que debería ver un supervisor:")
    
    # Préstamos de usuarios no-admin
    prestamos_no_admin = []
    for prestamo in prestamos:
        usuario_id = prestamo.get('usuario_id')
        for u in usuarios:
            if u['id'] == usuario_id and u.get('rol') != 'admin':
                prestamos_no_admin.append(prestamo)
                break
    
    prestamos_activos_no_admin = [p for p in prestamos_no_admin if p.get('estado') == 'activo']
    
    print(f"   📊 Préstamos totales de usuarios no-admin: {len(prestamos_no_admin)}")
    print(f"   📊 Préstamos activos de usuarios no-admin: {len(prestamos_activos_no_admin)}")
    
    if prestamos_activos_no_admin:
        print(f"   📋 Detalles de préstamos activos no-admin:")
        for prestamo in prestamos_activos_no_admin:
            # Encontrar cliente y usuario
            cliente_info = None
            usuario_info = None
            
            for c in clientes:
                if c['id'] == prestamo.get('cliente_id'):
                    cliente_info = c
                    break
            
            for u in usuarios:
                if u['id'] == prestamo.get('usuario_id'):
                    usuario_info = u
                    break
            
            if cliente_info and usuario_info:
                print(f"      💰 Préstamo #{prestamo['id']}: ${prestamo['monto']}")
                print(f"         👤 Cliente: {cliente_info['nombre']} {cliente_info['apellido']}")
                print(f"         👤 Usuario: {usuario_info['username']} (Rol: {usuario_info['rol']})")
                print(f"         📅 Estado: {prestamo['estado']}")
    
    # Verificar clientes accesibles para supervisores
    print(f"\n👤 Clientes accesibles para supervisores:")
    clientes_no_admin = []
    for cliente in clientes:
        usuario_id = cliente.get('usuario_id')
        for u in usuarios:
            if u['id'] == usuario_id and u.get('rol') != 'admin':
                clientes_no_admin.append(cliente)
                break
    
    print(f"   📊 Total clientes de usuarios no-admin: {len(clientes_no_admin)}")
    
    if clientes_no_admin:
        print(f"   📋 Lista de clientes:")
        for cliente in clientes_no_admin:
            # Encontrar usuario propietario
            usuario_info = None
            for u in usuarios:
                if u['id'] == cliente.get('usuario_id'):
                    usuario_info = u
                    break
            
            if usuario_info:
                print(f"      👤 {cliente['nombre']} {cliente['apellido']} (DNI: {cliente['dni']})")
                print(f"         Propietario: {usuario_info['username']} (Rol: {usuario_info['rol']})")
    
    print(f"\n" + "=" * 50)
    print(f"✅ Diagnóstico completado")

if __name__ == "__main__":
    diagnostico_supervisor()
