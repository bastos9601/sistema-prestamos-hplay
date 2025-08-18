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
    
    # Métodos para Clientes
    def agregar_cliente(self, cliente: Cliente) -> Cliente:
        """Agrega un nuevo cliente"""
        clientes = self._load_json(self.clientes_file)
        cliente.id = self._get_next_id(self.clientes_file)
        clientes.append(cliente.to_dict())
        self._save_json(self.clientes_file, clientes)
        return cliente
    
    def obtener_cliente(self, cliente_id: int) -> Optional[Cliente]:
        """Obtiene un cliente por ID"""
        clientes = self._load_json(self.clientes_file)
        for cliente_data in clientes:
            if cliente_data['id'] == cliente_id:
                return Cliente.from_dict(cliente_data)
        return None
    
    def obtener_cliente_por_dni(self, dni: str) -> Optional[Cliente]:
        """Obtiene un cliente por DNI"""
        clientes = self._load_json(self.clientes_file)
        for cliente_data in clientes:
            if cliente_data['dni'] == dni:
                return Cliente.from_dict(cliente_data)
        return None
    
    def listar_clientes(self) -> List[Cliente]:
        """Lista todos los clientes"""
        clientes = self._load_json(self.clientes_file)
        return [Cliente.from_dict(cliente_data) for cliente_data in clientes]
    
    def actualizar_cliente(self, cliente: Cliente) -> bool:
        """Actualiza un cliente existente"""
        clientes = self._load_json(self.clientes_file)
        for i, cliente_data in enumerate(clientes):
            if cliente_data['id'] == cliente.id:
                clientes[i] = cliente.to_dict()
                self._save_json(self.clientes_file, clientes)
                return True
        return False
    
    def eliminar_cliente(self, cliente_id: int) -> bool:
        """Elimina un cliente (marca como inactivo)"""
        cliente = self.obtener_cliente(cliente_id)
        if cliente:
            cliente.activo = False
            return self.actualizar_cliente(cliente)
        return False
    
    def eliminar_cliente_completo(self, cliente_id: int) -> bool:
        """Elimina un cliente completamente de la base de datos"""
        # Verificar que el cliente existe
        cliente = self.obtener_cliente(cliente_id)
        if not cliente:
            return False
        
        # Eliminar el cliente
        clientes = self._load_json(self.clientes_file)
        cliente_encontrado = False
        for i, cliente_data in enumerate(clientes):
            if cliente_data['id'] == cliente_id:
                del clientes[i]
                cliente_encontrado = True
                break
        
        if cliente_encontrado:
            self._save_json(self.clientes_file, clientes)
            
            # Eliminar todos los préstamos asociados a este cliente
            prestamos = self._load_json(self.prestamos_file)
            prestamos_filtrados = [p for p in prestamos if p['cliente_id'] != cliente_id]
            self._save_json(self.prestamos_file, prestamos_filtrados)
            
            # Eliminar todos los pagos de los préstamos eliminados
            prestamos_eliminados = [p for p in prestamos if p['cliente_id'] == cliente_id]
            prestamos_ids_eliminados = [p['id'] for p in prestamos_eliminados]
            
            pagos = self._load_json(self.pagos_file)
            pagos_filtrados = [p for p in pagos if p['prestamo_id'] not in prestamos_ids_eliminados]
            self._save_json(self.pagos_file, pagos_filtrados)
            
            return True
        
        return False
    
    # Métodos para Préstamos
    def agregar_prestamo(self, prestamo: Prestamo) -> Prestamo:
        """Agrega un nuevo préstamo"""
        prestamos = self._load_json(self.prestamos_file)
        prestamo.id = self._get_next_id(self.prestamos_file)
        prestamos.append(prestamo.to_dict())
        self._save_json(self.prestamos_file, prestamos)
        return prestamo
    
    def obtener_prestamo(self, prestamo_id: int) -> Optional[Prestamo]:
        """Obtiene un préstamo por ID"""
        prestamos = self._load_json(self.prestamos_file)
        for prestamo_data in prestamos:
            if prestamo_data['id'] == prestamo_id:
                return Prestamo.from_dict(prestamo_data)
        return None
    
    def listar_prestamos(self, cliente_id: Optional[int] = None) -> List[Prestamo]:
        """Lista todos los préstamos o los de un cliente específico"""
        prestamos = self._load_json(self.prestamos_file)
        prestamos_objs = [Prestamo.from_dict(prestamo_data) for prestamo_data in prestamos]
        
        if cliente_id:
            return [p for p in prestamos_objs if p.cliente_id == cliente_id]
        return prestamos_objs
    
    def actualizar_prestamo(self, prestamo: Prestamo) -> bool:
        """Actualiza un préstamo existente"""
        prestamos = self._load_json(self.prestamos_file)
        for i, prestamo_data in enumerate(prestamos):
            if prestamo_data['id'] == prestamo.id:
                prestamos[i] = prestamo.to_dict()
                self._save_json(self.prestamos_file, prestamos)
                return True
        return False
    
    def eliminar_prestamo(self, prestamo_id: int) -> bool:
        """Elimina un préstamo y todos sus pagos asociados de la base de datos"""
        # Eliminar el préstamo
        prestamos = self._load_json(self.prestamos_file)
        prestamo_encontrado = False
        for i, prestamo_data in enumerate(prestamos):
            if prestamo_data['id'] == prestamo_id:
                del prestamos[i]
                prestamo_encontrado = True
                break
        
        if prestamo_encontrado:
            self._save_json(self.prestamos_file, prestamos)
            
            # Eliminar todos los pagos asociados a este préstamo
            pagos = self._load_json(self.pagos_file)
            pagos_filtrados = [pago for pago in pagos if pago['prestamo_id'] != prestamo_id]
            self._save_json(self.pagos_file, pagos_filtrados)
            
            return True
        
        return False
    
    # Métodos para Pagos
    def agregar_pago(self, pago: Pago) -> Pago:
        """Agrega un nuevo pago"""
        # Primero actualizar el préstamo para calcular saldo_despues
        prestamo = self.obtener_prestamo(pago.prestamo_id)
        if prestamo:
            prestamo.agregar_pago(pago)  # Esto calcula saldo_despues
            self.actualizar_prestamo(prestamo)
        
        # Ahora guardar el pago con el saldo_despues calculado
        pagos = self._load_json(self.pagos_file)
        pago.id = self._get_next_id(self.pagos_file)
        pagos.append(pago.to_dict())
        self._save_json(self.pagos_file, pagos)
        
        return pago
    
    def listar_pagos(self, prestamo_id: Optional[int] = None) -> List[Pago]:
        """Lista todos los pagos o los de un préstamo específico"""
        pagos = self._load_json(self.pagos_file)
        pagos_objs = [Pago.from_dict(pago_data) for pago_data in pagos]
        
        if prestamo_id:
            return [p for p in pagos_objs if p.prestamo_id == prestamo_id]
        return pagos_objs
    
    def eliminar_pago(self, pago_id: int) -> bool:
        """Elimina un pago específico de la base de datos"""
        pagos = self._load_json(self.pagos_file)
        pago_encontrado = False
        for i, pago_data in enumerate(pagos):
            if pago_data['id'] == pago_id:
                del pagos[i]
                pago_encontrado = True
                break
        
        if pago_encontrado:
            self._save_json(self.pagos_file, pagos)
            return True
        
        return False
    
    # Métodos de búsqueda y reportes
    def buscar_clientes(self, termino: str) -> List[Cliente]:
        """Busca clientes por nombre, apellido o DNI"""
        termino = termino.lower()
        clientes = self.listar_clientes()
        return [
            cliente for cliente in clientes
            if (termino in cliente.nombre.lower() or 
                termino in cliente.apellido.lower() or 
                termino in cliente.dni.lower())
        ]
    
    def obtener_prestamos_activos(self) -> List[Prestamo]:
        """Obtiene todos los préstamos activos"""
        prestamos = self.listar_prestamos()
        return [p for p in prestamos if p.estado == "activo"]
    
    def obtener_prestamos_vencidos(self) -> List[Prestamo]:
        """Obtiene préstamos vencidos (implementar lógica de vencimiento)"""
        # Por ahora retorna préstamos activos, se puede implementar lógica de vencimiento
        return self.obtener_prestamos_activos()
    
    def obtener_estadisticas(self) -> Dict[str, Any]:
        """Obtiene estadísticas generales del sistema"""
        clientes = self.listar_clientes()
        prestamos = self.listar_prestamos()
        pagos = self.listar_pagos()
        
        # Solo contar clientes activos
        clientes_activos = len([c for c in clientes if c.activo])
        
        # Calcular totales
        total_prestado = sum(p.monto for p in prestamos if p.estado == "activo")
        total_pagado = sum(p.monto for p in pagos)
        prestamos_activos = len([p for p in prestamos if p.estado == "activo"])
        
        return {
            'total_clientes': clientes_activos,
            'total_prestamos': len(prestamos),
            'monto_total_prestado': float(total_prestado),
            'monto_total_pagado': float(total_pagado),
            'prestamos_activos': prestamos_activos,
            'total_pagos': len(pagos)
        }

    # Métodos para Usuarios
    def agregar_usuario(self, usuario: 'Usuario') -> 'Usuario':
        """Agrega un nuevo usuario"""
        usuarios = self._load_json(self.usuarios_file)
        usuario.id = self._get_next_id(self.usuarios_file)
        usuarios.append(usuario.to_dict())
        self._save_json(self.usuarios_file, usuarios)
        return usuario
    
    def obtener_usuario(self, usuario_id: int) -> Optional['Usuario']:
        """Obtiene un usuario por ID"""
        usuarios = self._load_json(self.usuarios_file)
        for usuario_data in usuarios:
            if usuario_data['id'] == usuario_id:
                return Usuario.from_dict(usuario_data)
        return None
    
    def obtener_usuario_por_username(self, username: str) -> Optional['Usuario']:
        """Obtiene un usuario por nombre de usuario"""
        usuarios = self._load_json(self.usuarios_file)
        for usuario_data in usuarios:
            if usuario_data['username'] == username and usuario_data['activo']:
                return Usuario.from_dict(usuario_data)
        return None
    
    def listar_usuarios(self) -> List['Usuario']:
        """Lista todos los usuarios activos"""
        usuarios = self._load_json(self.usuarios_file)
        return [Usuario.from_dict(usuario_data) for usuario_data in usuarios if usuario_data['activo']]
    
    def actualizar_usuario(self, usuario: 'Usuario') -> bool:
        """Actualiza un usuario existente"""
        usuarios = self._load_json(self.usuarios_file)
        for i, usuario_data in enumerate(usuarios):
            if usuario_data['id'] == usuario.id:
                usuarios[i] = usuario.to_dict()
                self._save_json(self.usuarios_file, usuarios)
                return True
        return False
    
    def eliminar_usuario(self, usuario_id: int) -> bool:
        """Elimina un usuario (marca como inactivo)"""
        usuario = self.obtener_usuario(usuario_id)
        if usuario:
            usuario.activo = False
            return self.actualizar_usuario(usuario)
        return False
    
    def verificar_login(self, username: str, password: str) -> Optional['Usuario']:
        """Verifica las credenciales de login"""
        usuario = self.obtener_usuario_por_username(username)
        if usuario and usuario.verificar_password(password):
            usuario.actualizar_ultimo_acceso()
            self.actualizar_usuario(usuario)
            return usuario
        return None
