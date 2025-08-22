import json
import os
from typing import List, Optional, Dict, Any
from models import Cliente, Prestamo, Pago, Usuario
from decimal import Decimal

class Database:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.clientes_file = os.path.join(data_dir, "clientes.json")
        self.prestamos_file = os.path.join(data_dir, "prestamos.json")
        self.pagos_file = os.path.join(data_dir, "pagos.json")
        self.usuarios_file = os.path.join(data_dir, "usuarios.json")
        self.configuracion_file = os.path.join(data_dir, "configuracion.json")
        
        # Crear directorio de datos si no existe
        os.makedirs(data_dir, exist_ok=True)
        
        # Inicializar archivos si no existen
        self._init_files()
    
    def _init_files(self):
        """Inicializa los archivos JSON si no existen"""
        if not os.path.exists(self.clientes_file):
            self._save_json(self.clientes_file, [])
        
        if not os.path.exists(self.prestamos_file):
            self._save_json(self.prestamos_file, [])
        
        if not os.path.exists(self.pagos_file):
            self._save_json(self.pagos_file, [])
        
        if not os.path.exists(self.usuarios_file):
            self._save_json(self.usuarios_file, [])
        
        if not os.path.exists(self.configuracion_file):
            self._save_json(self.configuracion_file, {
                "nombre_sistema": "Sistema de Préstamos",
                "version": "1.0",
                "descripcion": "Sistema de gestión de préstamos personales",
                "empresa": "Tu Empresa",
                "contacto": "contacto@tuempresa.com",
                "fecha_creacion": "2025-08-22",
                "ultima_actualizacion": "2025-08-22"
            })
    
    def _load_json(self, file_path: str) -> List[Dict[str, Any]]:
        """Carga datos desde un archivo JSON"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_json(self, file_path: str, data: List[Dict[str, Any]]):
        """Guarda datos en un archivo JSON"""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def _get_next_id(self, file_path: str) -> int:
        """Obtiene el siguiente ID disponible"""
        data = self._load_json(file_path)
        if not data:
            return 1
        return max(item['id'] for item in data) + 1
    
    def _filtrar_por_usuario(self, data: List[Dict[str, Any]], usuario_id: int, es_admin: bool = False) -> List[Dict[str, Any]]:
        """Filtra datos por usuario, los admins pueden ver todo"""
        if es_admin:
            return data
        
        # Obtener el usuario actual para verificar su rol
        usuarios = self._load_json(self.usuarios_file)
        usuario_actual = None
        
        # Si usuario_id es None, significa que es un supervisor que quiere ver todos los usuarios no-admin
        if usuario_id is None:
            # Filtrar solo datos de usuarios que no sean admin
            datos_filtrados = []
            for item in data:
                if item.get('usuario_id'):
                    # Obtener el usuario propietario del dato
                    usuario_propietario = None
                    for u in usuarios:
                        if u['id'] == item['usuario_id']:
                            usuario_propietario = u
                            break
                    
                    # Solo incluir si el usuario propietario no es admin
                    if usuario_propietario and usuario_propietario.get('rol') != 'admin':
                        datos_filtrados.append(item)
            
            return datos_filtrados
        
        for u in usuarios:
            if u['id'] == usuario_id:
                usuario_actual = u
                break
        
        if usuario_actual and usuario_actual.get('rol') in ['supervisor', 'consultor']:
            # Los supervisores y consultores pueden ver datos de usuarios no-admin
            # Filtrar solo datos de usuarios que no sean admin
            datos_filtrados = []
            for item in data:
                if item.get('usuario_id'):
                    # Obtener el usuario propietario del dato
                    usuario_propietario = None
                    for u in usuarios:
                        if u['id'] == item['usuario_id']:
                            usuario_propietario = u
                            break
                    
                    # Solo incluir si el usuario propietario no es admin
                    if usuario_propietario and usuario_propietario.get('rol') != 'admin':
                        datos_filtrados.append(item)
            
            return datos_filtrados
        
        # Los usuarios normales solo ven sus propios datos
        return [item for item in data if item.get('usuario_id') == usuario_id]
    
    # Métodos para Clientes
    def agregar_cliente(self, cliente: Cliente, usuario_id: int) -> Cliente:
        """Agrega un nuevo cliente asociado a un usuario"""
        clientes = self._load_json(self.clientes_file)
        cliente.id = self._get_next_id(self.clientes_file)
        cliente.usuario_id = usuario_id
        clientes.append(cliente.to_dict())
        self._save_json(self.clientes_file, clientes)
        return cliente
    
    def obtener_cliente(self, cliente_id: int, usuario_id: int, es_admin: bool = False) -> Optional[Cliente]:
        """Obtiene un cliente por ID, respetando el aislamiento de datos"""
        print(f"🔍 obtener_cliente - cliente_id: {cliente_id}, usuario_id: {usuario_id}, es_admin: {es_admin}")
        
        clientes = self._load_json(self.clientes_file)
        for cliente_data in clientes:
            if cliente_data['id'] == cliente_id:
                print(f"📋 Cliente encontrado: {cliente_data['nombre']} {cliente_data['apellido']}, usuario_id: {cliente_data.get('usuario_id')}")
                
                # Si usuario_id es None, significa que es un supervisor que quiere ver todos los usuarios no-admin
                if usuario_id is None:
                    print(f"👁️ Supervisor buscando cliente - verificando si pertenece a usuario no-admin")
                    # Verificar que el cliente pertenezca a un usuario no-admin
                    usuarios = self._load_json(self.usuarios_file)
                    usuario_propietario = None
                    for u in usuarios:
                        if u['id'] == cliente_data.get('usuario_id'):
                            usuario_propietario = u
                            break
                    
                    if usuario_propietario:
                        print(f"👤 Usuario propietario: {usuario_propietario['username']}, Rol: {usuario_propietario['rol']}")
                    # Solo incluir si el usuario propietario no es admin
                        if usuario_propietario.get('rol') != 'admin':
                            print(f"✅ Cliente accesible para supervisor")
                        return Cliente.from_dict(cliente_data)
                        else:
                            print(f"❌ Cliente pertenece a admin - no accesible")
                    else:
                        print(f"❌ No se encontró usuario propietario")
                # Verificar si el usuario puede ver este cliente
                elif es_admin or cliente_data.get('usuario_id') == usuario_id:
                    print(f"✅ Cliente accesible para usuario normal/admin")
                    return Cliente.from_dict(cliente_data)
                else:
                    print(f"❌ Cliente no accesible - usuario_id no coincide")
        
        print(f"❌ Cliente {cliente_id} no encontrado o no accesible")
        return None
    
    def obtener_cliente_por_dni(self, dni: str, usuario_id: int, es_admin: bool = False) -> Optional[Cliente]:
        """Obtiene un cliente por DNI, respetando el aislamiento de datos"""
        clientes = self._load_json(self.clientes_file)
        for cliente_data in clientes:
            if cliente_data['dni'] == dni:
                # Si usuario_id es None, significa que es un supervisor que quiere ver todos los usuarios no-admin
                if usuario_id is None:
                    # Verificar que el cliente pertenezca a un usuario no-admin
                    usuarios = self._load_json(self.usuarios_file)
                    usuario_propietario = None
                    for u in usuarios:
                        if u['id'] == cliente_data.get('usuario_id'):
                            usuario_propietario = u
                            break
                    
                    # Solo incluir si el usuario propietario no es admin
                    if usuario_propietario and usuario_propietario.get('rol') != 'admin':
                        return Cliente.from_dict(cliente_data)
                # Verificar si el usuario puede ver este cliente
                elif es_admin or cliente_data.get('usuario_id') == usuario_id:
                    return Cliente.from_dict(cliente_data)
        return None
    
    def listar_clientes(self, usuario_id: int, es_admin: bool = False) -> List[Cliente]:
        """Lista clientes, respetando el aislamiento de datos"""
        clientes = self._load_json(self.clientes_file)
        clientes_filtrados = self._filtrar_por_usuario(clientes, usuario_id, es_admin)
        
        # Obtener el usuario actual para verificar su rol
        usuarios = self._load_json(self.usuarios_file)
        usuario_actual = None
        for u in usuarios:
            if u['id'] == usuario_id:
                usuario_actual = u
                break
        
        # Si es admin, supervisor o consultor, enriquecer con información del usuario creador
        if es_admin or (usuario_actual and usuario_actual.get('rol') in ['supervisor', 'consultor']):
            for cliente_data in clientes_filtrados:
                if cliente_data.get('usuario_creador_id'):
                    usuario_creador = self.obtener_usuario(cliente_data['usuario_creador_id'], usuario_id, es_admin)
                    if usuario_creador:
                        cliente_data['usuario_creador'] = {
                            'id': usuario_creador.id,
                            'nombre': usuario_creador.nombre,
                            'username': usuario_creador.username
                        }
        
        return [Cliente.from_dict(cliente_data) for cliente_data in clientes_filtrados]
    
    def actualizar_cliente(self, cliente: Cliente, usuario_id: int, es_admin: bool = False) -> bool:
        """Actualiza un cliente existente, respetando el aislamiento de datos"""
        # Obtener el usuario actual para verificar su rol
        usuarios = self._load_json(self.usuarios_file)
        usuario_actual = None
        for u in usuarios:
            if u['id'] == usuario_id:
                usuario_actual = u
                break
        
        clientes = self._load_json(self.clientes_file)
        for i, cliente_data in enumerate(clientes):
            if cliente_data['id'] == cliente.id:
                # Verificar si el usuario puede modificar este cliente
                if es_admin:
                    # Los admins pueden modificar cualquier cliente
                    pass
                elif usuario_actual and usuario_actual.get('rol') in ['supervisor', 'consultor']:
                    # Los supervisores y consultores pueden modificar clientes de usuarios no-admin
                    # Obtener el usuario propietario del cliente
                    usuario_propietario = None
                    for u in usuarios:
                        if u['id'] == cliente_data.get('usuario_id'):
                            usuario_propietario = u
                            break
                    
                    # Solo permitir si el usuario propietario no es admin
                    if not usuario_propietario or usuario_propietario.get('rol') == 'admin':
                        return False
                elif cliente_data.get('usuario_id') == usuario_id:
                    # Los usuarios normales solo pueden modificar sus propios clientes
                    pass
                else:
                    return False
                
                # Si llegamos aquí, el usuario tiene permisos para modificar
                clientes[i] = cliente.to_dict()
                self._save_json(self.clientes_file, clientes)
                return True
        
        return False
    
    def eliminar_cliente(self, cliente_id: int, usuario_id: int, es_admin: bool = False) -> bool:
        """Elimina un cliente físicamente de la base de datos, respetando el aislamiento de datos"""
        # Obtener el usuario actual para verificar su rol
        usuarios = self._load_json(self.usuarios_file)
        usuario_actual = None
        for u in usuarios:
            if u['id'] == usuario_id:
                usuario_actual = u
                break
        
        # Verificar si el usuario puede eliminar este cliente
        if es_admin:
            # Los admins pueden eliminar cualquier cliente
            pass
        elif usuario_actual and usuario_actual.get('rol') in ['supervisor', 'consultor']:
            # Los supervisores y consultores pueden eliminar clientes de usuarios no-admin
            # Obtener el cliente directamente para verificar permisos
            clientes = self._load_json(self.clientes_file)
            cliente_data = None
            for c in clientes:
                if c['id'] == cliente_id:
                    cliente_data = c
                    break
            
            if not cliente_data:
                return False
            
            # Obtener el usuario propietario del cliente
            usuario_propietario = None
            for u in usuarios:
                if u['id'] == cliente_data.get('usuario_id'):
                    usuario_propietario = u
                    break
            
            # Solo permitir si el usuario propietario no es admin
            if not usuario_propietario or usuario_propietario.get('rol') == 'admin':
                return False
        else:
            # Los usuarios normales solo pueden eliminar sus propios clientes
            cliente = self.obtener_cliente(cliente_id, usuario_id, es_admin)
            if not cliente:
                return False
            
        # Eliminar físicamente el cliente
        clientes = self._load_json(self.clientes_file)
        clientes_filtrados = [c for c in clientes if c['id'] != cliente_id]
        
        if len(clientes_filtrados) < len(clientes):
            self._save_json(self.clientes_file, clientes_filtrados)
            
            # También eliminar todos los préstamos asociados a este cliente
            prestamos = self._load_json(self.prestamos_file)
            prestamos_filtrados = [p for p in prestamos if p['cliente_id'] != cliente_id]
            self._save_json(self.prestamos_file, prestamos_filtrados)
            
            # Y eliminar todos los pagos de esos préstamos
            prestamos_eliminados = [p for p in prestamos if p['cliente_id'] == cliente_id]
            prestamos_ids_eliminados = [p['id'] for p in prestamos_eliminados]
            
            pagos = self._load_json(self.pagos_file)
            pagos_filtrados = [p for p in pagos if p['prestamo_id'] not in prestamos_ids_eliminados]
            self._save_json(self.pagos_file, pagos_filtrados)
            
            return True
        
        return False
    
    def eliminar_cliente_completo(self, cliente_id: int) -> bool:
        """Elimina un cliente completamente de la base de datos (método de administrador)"""
        # Este método es para admins que quieren eliminar cualquier cliente
        clientes = self._load_json(self.clientes_file)
        clientes_filtrados = [c for c in clientes if c['id'] != cliente_id]
        
        if len(clientes_filtrados) < len(clientes):
            self._save_json(self.clientes_file, clientes_filtrados)
            
            # Eliminar préstamos asociados
            prestamos = self._load_json(self.prestamos_file)
            prestamos_filtrados = [p for p in prestamos if p['cliente_id'] != cliente_id]
            self._save_json(self.prestamos_file, prestamos_filtrados)
            
            # Eliminar pagos asociados
            prestamos_eliminados = [p for p in prestamos if p['cliente_id'] == cliente_id]
            prestamos_ids_eliminados = [p['id'] for p in prestamos_eliminados]
            
            pagos = self._load_json(self.pagos_file)
            pagos_filtrados = [p for p in pagos if p['prestamo_id'] not in prestamos_ids_eliminados]
            self._save_json(self.pagos_file, pagos_filtrados)
            
            return True
        
        return False
    
    # Métodos para Préstamos
    def agregar_prestamo(self, prestamo: Prestamo, usuario_id: int) -> Prestamo:
        """Agrega un nuevo préstamo asociado a un usuario"""
        prestamos = self._load_json(self.prestamos_file)
        prestamo.id = self._get_next_id(self.prestamos_file)
        prestamo.usuario_id = usuario_id
        prestamos.append(prestamo.to_dict())
        self._save_json(self.prestamos_file, prestamos)
        return prestamo
    
    def obtener_prestamo(self, prestamo_id: int, usuario_id: int, es_admin: bool = False) -> Optional[Prestamo]:
        """Obtiene un préstamo por ID, respetando el aislamiento de datos"""
        # Obtener el usuario actual para verificar su rol
        usuarios = self._load_json(self.usuarios_file)
        usuario_actual = None
        for u in usuarios:
            if u['id'] == usuario_id:
                usuario_actual = u
                break
        
        prestamos = self._load_json(self.prestamos_file)
        for prestamo_data in prestamos:
            if prestamo_data['id'] == prestamo_id:
                # Verificar si el usuario puede ver este préstamo
                if es_admin:
                    # Los admins pueden ver cualquier préstamo
                    return Prestamo.from_dict(prestamo_data)
                elif usuario_actual and usuario_actual.get('rol') in ['supervisor', 'consultor']:
                    # Los supervisores y consultores pueden ver préstamos de usuarios no-admin
                    # Obtener el usuario propietario del préstamo
                    usuario_propietario = None
                    for u in usuarios:
                        if u['id'] == prestamo_data.get('usuario_id'):
                            usuario_propietario = u
                            break
                    
                    # Solo permitir si el usuario propietario no es admin
                    if usuario_propietario and usuario_propietario.get('rol') != 'admin':
                        return Prestamo.from_dict(prestamo_data)
                elif prestamo_data.get('usuario_id') == usuario_id:
                    # Los usuarios normales solo pueden ver sus propios préstamos
                    return Prestamo.from_dict(prestamo_data)
        
        return None
    
    def listar_prestamos(self, usuario_id: int, es_admin: bool = False, cliente_id: Optional[int] = None) -> List[Prestamo]:
        """Lista préstamos, respetando el aislamiento de datos"""
        prestamos = self._load_json(self.prestamos_file)
        prestamos_filtrados = self._filtrar_por_usuario(prestamos, usuario_id, es_admin)
        
        # Obtener el usuario actual para verificar su rol
        usuarios = self._load_json(self.usuarios_file)
        usuario_actual = None
        for u in usuarios:
            if u['id'] == usuario_id:
                usuario_actual = u
                break
        
        # Si es admin, supervisor o consultor, enriquecer con información del usuario creador
        if es_admin or (usuario_actual and usuario_actual.get('rol') in ['supervisor', 'consultor']):
            for prestamo_data in prestamos_filtrados:
                if prestamo_data.get('usuario_creador_id'):
                    usuario_creador = self.obtener_usuario(prestamo_data['usuario_creador_id'], usuario_id, es_admin)
                    if usuario_creador:
                        prestamo_data['usuario_creador'] = {
                            'id': usuario_creador.id,
                            'nombre': usuario_creador.nombre,
                            'username': usuario_creador.username
                        }
        
        prestamos_objs = [Prestamo.from_dict(prestamo_data) for prestamo_data in prestamos_filtrados]
        
        if cliente_id:
            return [p for p in prestamos_objs if p.cliente_id == cliente_id]
        return prestamos_objs
    
    def actualizar_prestamo(self, prestamo: Prestamo, usuario_id: int, es_admin: bool = False) -> bool:
        """Actualiza un préstamo existente, respetando el aislamiento de datos"""
        prestamos = self._load_json(self.prestamos_file)
        for i, prestamo_data in enumerate(prestamos):
            if prestamo_data['id'] == prestamo.id:
                # Verificar si el usuario puede modificar este préstamo
                if es_admin or prestamo_data.get('usuario_id') == usuario_id:
                    prestamos[i] = prestamo.to_dict()
                    self._save_json(self.prestamos_file, prestamos)
                    return True
        return False
    
    def eliminar_prestamo(self, prestamo_id: int, usuario_id: int, es_admin: bool = False) -> bool:
        """Elimina un préstamo físicamente de la base de datos, respetando el aislamiento de datos"""
        # Verificar si el usuario puede eliminar este préstamo
        prestamo = self.obtener_prestamo(prestamo_id, usuario_id, es_admin)
        if not prestamo:
            return False
            
        # Eliminar el préstamo físicamente
        prestamos = self._load_json(self.prestamos_file)
        prestamos_filtrados = [p for p in prestamos if p['id'] != prestamo_id]
        
        if len(prestamos_filtrados) < len(prestamos):
            self._save_json(self.prestamos_file, prestamos_filtrados)
            
            # Eliminar todos los pagos asociados a este préstamo
            pagos = self._load_json(self.pagos_file)
            pagos_filtrados = [p for p in pagos if p['prestamo_id'] != prestamo_id]
            self._save_json(self.pagos_file, pagos_filtrados)
            
            return True
        
        return False
    
    # Métodos para Pagos
    def agregar_pago(self, pago: Pago, usuario_id: int) -> Pago:
        """Agrega un nuevo pago asociado a un usuario"""
        # Primero actualizar el préstamo para calcular saldo_despues
        prestamo = self.obtener_prestamo(pago.prestamo_id, usuario_id, False)
        if prestamo:
            prestamo.agregar_pago(pago)  # Esto calcula saldo_despues
            self.actualizar_prestamo(prestamo, usuario_id, False)
        
        # Ahora guardar el pago con el saldo_despues calculado
        pagos = self._load_json(self.pagos_file)
        pago.id = self._get_next_id(self.pagos_file)
        pago.usuario_id = usuario_id
        pagos.append(pago.to_dict())
        self._save_json(self.pagos_file, pagos)
        
        return pago
    
    def obtener_pago(self, pago_id: int, usuario_id: int, es_admin: bool = False) -> Optional[Pago]:
        """Obtiene un pago específico, respetando el aislamiento de datos"""
        # Obtener el usuario actual para verificar su rol
        usuarios = self._load_json(self.usuarios_file)
        usuario_actual = None
        for u in usuarios:
            if u['id'] == usuario_id:
                usuario_actual = u
                break
        
        pagos = self._load_json(self.pagos_file)
        
        for pago_data in pagos:
            if pago_data['id'] == pago_id:
                # Verificar si el usuario puede ver este pago
                if es_admin:
                    # Los admins pueden ver cualquier pago
                    return Pago.from_dict(pago_data)
                elif usuario_actual and usuario_actual.get('rol') in ['supervisor', 'consultor']:
                    # Los supervisores y consultores pueden ver pagos de usuarios no-admin
                    # Obtener el usuario propietario del pago
                    usuario_propietario = None
                    for u in usuarios:
                        if u['id'] == pago_data.get('usuario_id'):
                            usuario_propietario = u
                            break
                    
                    # Solo permitir si el usuario propietario no es admin
                    if usuario_propietario and usuario_propietario.get('rol') != 'admin':
                        return Pago.from_dict(pago_data)
                elif pago_data.get('usuario_id') == usuario_id:
                    # Los usuarios normales solo pueden ver sus propios pagos
                    return Pago.from_dict(pago_data)
        
        return None
    
    def listar_pagos(self, usuario_id: int, es_admin: bool = False, prestamo_id: Optional[int] = None) -> List[Pago]:
        """Lista pagos, respetando el aislamiento de datos"""
        pagos = self._load_json(self.pagos_file)
        pagos_filtrados = self._filtrar_por_usuario(pagos, usuario_id, es_admin)
        
        # Obtener el usuario actual para verificar su rol
        usuarios = self._load_json(self.usuarios_file)
        usuario_actual = None
        for u in usuarios:
            if u['id'] == usuario_id:
                usuario_actual = u
                break
        
        # Si es admin, supervisor o consultor, enriquecer con información del usuario creador
        if es_admin or (usuario_actual and usuario_actual.get('rol') in ['supervisor', 'consultor']):
            for pago_data in pagos_filtrados:
                if pago_data.get('usuario_creador_id'):
                    usuario_creador = self.obtener_usuario(pago_data['usuario_creador_id'], usuario_id, es_admin)
                    if usuario_creador:
                        pago_data['usuario_creador'] = {
                            'id': usuario_creador.id,
                            'nombre': usuario_creador.nombre,
                            'username': usuario_creador.username
                        }
        
        pagos_objs = [Pago.from_dict(pago_data) for pago_data in pagos_filtrados]
        
        if prestamo_id:
            return [p for p in pagos_objs if p.prestamo_id == prestamo_id]
        return pagos_objs
    
    def eliminar_pago(self, pago_id: int, usuario_id: int, es_admin: bool = False) -> bool:
        """Elimina un pago específico físicamente de la base de datos, respetando el aislamiento de datos"""
        pagos = self._load_json(self.pagos_file)
        pago_encontrado = False
        
        for i, pago_data in enumerate(pagos):
            if pago_data['id'] == pago_id:
                # Verificar si el usuario puede eliminar este pago
                if es_admin or pago_data.get('usuario_id') == usuario_id:
                    del pagos[i]
                    pago_encontrado = True
                    break
        
        if pago_encontrado:
            self._save_json(self.pagos_file, pagos)
            return True
        
        return False
    
    # Métodos de búsqueda y reportes
    def buscar_clientes(self, termino: str, usuario_id: int, es_admin: bool = False) -> List[Cliente]:
        """Busca clientes por nombre, apellido o DNI, respetando el aislamiento de datos"""
        termino = termino.lower()
        clientes = self.listar_clientes(usuario_id, es_admin)
        return [
            cliente for cliente in clientes
            if (termino in cliente.nombre.lower() or 
                termino in cliente.apellido.lower() or 
                termino in cliente.dni.lower())
        ]
    
    def obtener_prestamos_activos(self, usuario_id: int = None, es_admin: bool = False) -> List[Prestamo]:
        """Obtiene todos los préstamos activos, respetando el aislamiento de datos"""
        prestamos = self.listar_prestamos(usuario_id, es_admin)
        return [p for p in prestamos if p.estado == "activo"]
    
    def obtener_prestamos_vencidos(self) -> List[Prestamo]:
        """Obtiene préstamos vencidos (implementar lógica de vencimiento)"""
        # Por ahora retorna préstamos activos, se puede implementar lógica de vencimiento
        return self.obtener_prestamos_activos()
    
    def obtener_estadisticas(self, usuario_id: int = None, es_admin: bool = False) -> Dict[str, Any]:
        """Obtiene estadísticas generales del sistema, respetando el aislamiento de datos"""
        # Si usuario_id es None, significa que es un supervisor que quiere ver todos los usuarios no-admin
        if usuario_id is None:
            # Filtrar solo datos de usuarios que no sean admin
            clientes = self.listar_clientes(None, False)
            prestamos = self.listar_prestamos(None, False)
            pagos = self.listar_pagos(None, False)
            usuarios = self.listar_usuarios(None, False)
        else:
            # Obtener el usuario actual para verificar su rol
            usuarios_data = self._load_json(self.usuarios_file)
            usuario_actual = None
            for u in usuarios_data:
                if u['id'] == usuario_id:
                    usuario_actual = u
                    break
            
            if es_admin:
                # Los admins pueden ver todas las estadísticas
                clientes = self.listar_clientes(usuario_id or 0, True)
                prestamos = self.listar_prestamos(usuario_id or 0, True)
                pagos = self.listar_pagos(usuario_id or 0, True)
                usuarios = self.listar_usuarios(usuario_id or 0, True)
            elif usuario_actual and usuario_actual.get('rol') in ['supervisor', 'consultor']:
                # Los supervisores y consultores pueden ver estadísticas de usuarios no-admin
                clientes = self.listar_clientes(None, False)
                prestamos = self.listar_prestamos(None, False)
                pagos = self.listar_pagos(None, False)
                usuarios = self.listar_usuarios(None, False)
            else:
                # Los usuarios solo ven sus propias estadísticas
                clientes = self.listar_clientes(usuario_id or 0, False)
                prestamos = self.listar_prestamos(usuario_id or 0, False)
                pagos = self.listar_pagos(usuario_id or 0, False)
                usuarios = self.listar_usuarios(usuario_id or 0, False)
        
        # Solo contar clientes activos
        clientes_activos = len([c for c in clientes if c.activo])
        
        # Calcular totales
        total_prestado = sum(p.monto for p in prestamos if p.estado == "activo")
        total_pagado = sum(p.monto for p in pagos)
        prestamos_activos = len([p for p in prestamos if p.estado == "activo"])
        

        
        total_usuarios = len([u for u in usuarios if u.activo])
        
        return {
            'total_clientes': clientes_activos,
            'total_prestamos': len(prestamos),
            'monto_total_prestado': float(total_prestado),
            'monto_total_pagado': float(total_pagado),
            'prestamos_activos': prestamos_activos,
            'total_pagos': len(pagos),
            'total_usuarios': total_usuarios
        }

    # Métodos para Usuarios
    def agregar_usuario(self, usuario: 'Usuario', usuario_creador_id: int) -> 'Usuario':
        """Agrega un nuevo usuario asociado al usuario que lo creó"""
        usuarios = self._load_json(self.usuarios_file)
        usuario.id = self._get_next_id(self.usuarios_file)
        usuario.usuario_creador_id = usuario_creador_id
        usuarios.append(usuario.to_dict())
        self._save_json(self.usuarios_file, usuarios)
        return usuario
    
    def obtener_usuario(self, usuario_id: int, usuario_actual_id: int, es_admin: bool = False) -> Optional['Usuario']:
        """Obtiene un usuario por ID, respetando el aislamiento de datos"""
        usuarios = self._load_json(self.usuarios_file)
        
        # Si usuario_actual_id es None, significa que es un supervisor que quiere ver todos los usuarios no-admin
        if usuario_actual_id is None:
            for usuario_data in usuarios:
                if usuario_data['id'] == usuario_id:
                    # Los supervisores y consultores pueden ver usuarios no-admin
                    if usuario_data.get('rol') != 'admin':
                        return Usuario.from_dict(usuario_data)
            return None
        
        # Obtener el usuario actual para verificar su rol
        usuario_actual = None
        for u in usuarios:
            if u['id'] == usuario_actual_id:
                usuario_actual = u
                break
        
        for usuario_data in usuarios:
            if usuario_data['id'] == usuario_id:
                # Verificar si el usuario puede ver este usuario
                if es_admin:
                    return Usuario.from_dict(usuario_data)
                elif usuario_actual and usuario_actual.get('rol') in ['supervisor', 'consultor']:
                    # Los supervisores y consultores pueden ver usuarios no-admin
                    if usuario_data.get('rol') != 'admin':
                        return Usuario.from_dict(usuario_data)
                elif usuario_data.get('usuario_creador_id') == usuario_actual_id or usuario_id == usuario_actual_id:
                    return Usuario.from_dict(usuario_data)
        return None
    
    def obtener_usuario_por_username(self, username: str) -> Optional['Usuario']:
        """Obtiene un usuario por nombre de usuario (para login)"""
        usuarios = self._load_json(self.usuarios_file)
        for usuario_data in usuarios:
            if usuario_data['username'] == username and usuario_data['activo']:
                return Usuario.from_dict(usuario_data)
        return None
    
    def obtener_usuario_por_email(self, email: str) -> Optional['Usuario']:
        """Obtiene un usuario por email (para recuperación de contraseña)"""
        usuarios = self._load_json(self.usuarios_file)
        for usuario_data in usuarios:
            if usuario_data.get('email') == email and usuario_data['activo']:
                return Usuario.from_dict(usuario_data)
        return None
    
    def cambiar_password_usuario(self, usuario_id: int, nueva_password: str) -> bool:
        """Cambia la contraseña de un usuario"""
        try:
            usuarios = self._load_json(self.usuarios_file)
            for i, usuario_data in enumerate(usuarios):
                if usuario_data['id'] == usuario_id:
                    # Crear objeto Usuario y cambiar contraseña
                    usuario = Usuario.from_dict(usuario_data)
                    usuario.password_hash = Usuario.hash_password(nueva_password)
                    usuarios[i] = usuario.to_dict()
                    self._save_json(self.usuarios_file, usuarios)
                    return True
            return False
        except Exception as e:
            print(f"Error al cambiar contraseña: {e}")
            return False
    
    def listar_usuarios(self, usuario_actual_id: int, es_admin: bool = False) -> List['Usuario']:
        """Lista usuarios, respetando el aislamiento de datos"""
        usuarios = self._load_json(self.usuarios_file)
        
        # Obtener el usuario actual para verificar su rol
        usuario_actual = None
        for u in usuarios:
            if u['id'] == usuario_actual_id:
                usuario_actual = u
                break
        
        if es_admin:
            # Los admins pueden ver todos los usuarios
            return [Usuario.from_dict(usuario_data) for usuario_data in usuarios if usuario_data['activo']]
        elif usuario_actual and usuario_actual.get('rol') in ['supervisor', 'consultor']:
            # Los supervisores y consultores pueden ver usuarios no-admin
            usuarios_filtrados = [
                usuario_data for usuario_data in usuarios 
                if usuario_data['activo'] and usuario_data.get('rol') != 'admin'
            ]
            return [Usuario.from_dict(usuario_data) for usuario_data in usuarios_filtrados]
        else:
            # Los usuarios solo pueden ver los que crearon
            usuarios_filtrados = [
                usuario_data for usuario_data in usuarios 
                if usuario_data['activo'] and usuario_data.get('usuario_creador_id') == usuario_actual_id
            ]
            return [Usuario.from_dict(usuario_data) for usuario_data in usuarios_filtrados]
    
    def actualizar_usuario(self, usuario: 'Usuario', usuario_actual_id: int, es_admin: bool = False) -> bool:
        """Actualiza un usuario existente, respetando el aislamiento de datos"""
        usuarios = self._load_json(self.usuarios_file)
        for i, usuario_data in enumerate(usuarios):
            if usuario_data['id'] == usuario.id:
                # Verificar si el usuario puede modificar este usuario
                if es_admin or usuario_data.get('usuario_creador_id') == usuario_actual_id or usuario.id == usuario_actual_id:
                    usuarios[i] = usuario.to_dict()
                    self._save_json(self.usuarios_file, usuarios)
                    return True
        return False
    
    def eliminar_usuario(self, usuario_id: int, usuario_actual_id: int, es_admin: bool = False) -> bool:
        """Elimina un usuario, respetando el aislamiento de datos"""
        # Obtener el usuario actual para verificar su rol
        usuarios = self._load_json(self.usuarios_file)
        usuario_actual = None
        for u in usuarios:
            if u['id'] == usuario_actual_id:
                usuario_actual = u
                break
        
        # Verificar permisos
        if es_admin:
            # Los admins pueden eliminar a cualquiera
            pass
        elif usuario_actual and usuario_actual.get('rol') in ['supervisor', 'consultor']:
            # Los supervisores y consultores solo pueden eliminar usuarios no-admin
            usuario_objetivo = None
            for u in usuarios:
                if u['id'] == usuario_id:
                    usuario_objetivo = u
                    break
            
            if not usuario_objetivo or usuario_objetivo.get('rol') == 'admin':
                return False  # No puede eliminar admins
        else:
            # Los usuarios normales no pueden eliminar a otros
            return False
        
        # Obtener el usuario a eliminar
        usuario = self.obtener_usuario(usuario_id, usuario_actual_id, es_admin)
        if usuario:
            usuario.activo = False
            return self.actualizar_usuario(usuario, usuario_actual_id, es_admin)
        return False
    
    def eliminar_usuario_completo(self, usuario_id: int, usuario_actual_id: int, es_admin: bool = False) -> bool:
        """Elimina completamente un usuario y todos sus datos, respetando el aislamiento de datos"""
        # Obtener el usuario actual para verificar su rol
        usuarios = self._load_json(self.usuarios_file)
        usuario_actual = None
        for u in usuarios:
            if u['id'] == usuario_actual_id:
                usuario_actual = u
                break
        
        # Verificar permisos
        if es_admin:
            # Los admins pueden eliminar a cualquiera
            pass
        elif usuario_actual and usuario_actual.get('rol') in ['supervisor', 'consultor']:
            # Los supervisores y consultores solo pueden eliminar usuarios no-admin
            usuario_objetivo = None
            for u in usuarios:
                if u['id'] == usuario_id:
                    usuario_objetivo = u
                    break
            
            if not usuario_objetivo or usuario_objetivo.get('rol') == 'admin':
                return False  # No puede eliminar admins
        else:
            # Los usuarios normales no pueden eliminar a otros
            return False
        
        # Eliminar físicamente el usuario
        usuarios_filtrados = [u for u in usuarios if u['id'] != usuario_id]
        if len(usuarios_filtrados) < len(usuarios):
            self._save_json(self.usuarios_file, usuarios_filtrados)
            
            # Eliminar todos los clientes del usuario
            clientes = self._load_json(self.clientes_file)
            clientes_filtrados = [c for c in clientes if c.get('usuario_id') != usuario_id]
            self._save_json(self.clientes_file, clientes_filtrados)
            
            # Eliminar todos los préstamos del usuario
            prestamos = self._load_json(self.prestamos_file)
            prestamos_filtrados = [p for p in prestamos if p.get('usuario_id') != usuario_id]
            self._save_json(self.prestamos_file, prestamos_filtrados)
            
            # Eliminar todos los pagos del usuario
            pagos = self._load_json(self.pagos_file)
            pagos_filtrados = [p for p in pagos if p.get('usuario_id') != usuario_id]
            self._save_json(self.pagos_file, pagos_filtrados)
            
            return True
        
        return False
    
    def verificar_login(self, username: str, password: str) -> Optional['Usuario']:
        """Verifica las credenciales de login"""
        usuario = self.obtener_usuario_por_username(username)
        if usuario and usuario.verificar_password(password):
            usuario.actualizar_ultimo_acceso()
            self.actualizar_usuario(usuario, usuario.id, False)  # El usuario puede actualizarse a sí mismo
            return usuario
        return None
    
    # Métodos para Configuración del Sistema
    def obtener_configuracion(self) -> Dict[str, Any]:
        """Obtiene la configuración actual del sistema"""
        try:
            return self._load_json(self.configuracion_file)[0] if self._load_json(self.configuracion_file) else {}
        except:
            return {
                "nombre_sistema": "Sistema de Préstamos",
                "version": "1.0",
                "descripcion": "Sistema de gestión de préstamos personales",
                "empresa": "Tu Empresa",
                "contacto": "contacto@tuempresa.com",
                "fecha_creacion": "2025-08-22",
                "ultima_actualizacion": "2025-08-22"
            }
    
    def actualizar_configuracion(self, nueva_config: Dict[str, Any]) -> bool:
        """Actualiza la configuración del sistema"""
        try:
            from datetime import datetime
            nueva_config['ultima_actualizacion'] = datetime.now().strftime('%Y-%m-%d')
            self._save_json(self.configuracion_file, [nueva_config])
            return True
        except Exception as e:
            print(f"Error al actualizar configuración: {e}")
            return False
    
    def cambiar_nombre_sistema(self, nuevo_nombre: str) -> bool:
        """Cambia el nombre del sistema"""
        config = self.obtener_configuracion()
        config['nombre_sistema'] = nuevo_nombre
        return self.actualizar_configuracion(config)
