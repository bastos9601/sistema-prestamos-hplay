from typing import List, Optional, Dict, Any
from decimal import Decimal
from datetime import date, datetime
from models import Cliente, Prestamo, Pago, Usuario
from database import Database
from pagare_generator import PagareGenerator
import json

class ClienteService:
    def __init__(self, db: Database):
        self.db = db
    
    def crear_cliente(self, nombre: str, apellido: str, dni: str, telefono: str, email: str = "", usuario_id: int = None) -> Cliente:
        """Crea un nuevo cliente asociado a un usuario"""
        # Verificar que el DNI no esté duplicado para este usuario
        if self.db.obtener_cliente_por_dni(dni, usuario_id, False):
            raise ValueError(f"Ya existe un cliente con el DNI {dni}")
        
        cliente = Cliente(
            id=0,  # Se asignará automáticamente
            nombre=nombre,
            apellido=apellido,
            dni=dni,
            telefono=telefono,
            email=email,
            usuario_id=usuario_id
        )
        
        return self.db.agregar_cliente(cliente, usuario_id)
    
    def buscar_cliente(self, termino: str, usuario_id: int, es_admin: bool = False) -> List[Cliente]:
        """Busca clientes por nombre, apellido o DNI, respetando el aislamiento de datos"""
        return self.db.buscar_clientes(termino, usuario_id, es_admin)
    
    def obtener_cliente(self, cliente_id: int, usuario_id: int, es_admin: bool = False) -> Optional[Cliente]:
        """Obtiene un cliente por ID, respetando el aislamiento de datos"""
        return self.db.obtener_cliente(cliente_id, usuario_id, es_admin)
    
    def listar_clientes(self, usuario_id: int, es_admin: bool = False) -> List[Cliente]:
        """Lista clientes, respetando el aislamiento de datos"""
        # Si usuario_id es None, significa que es un supervisor que quiere ver todos los usuarios no-admin
        if usuario_id is None:
            clientes = self.db.listar_clientes(None, False)
            return [c for c in clientes if c.activo]
        
        # Obtener el usuario actual para verificar su rol
        usuario_actual = self.db.obtener_usuario(usuario_id, usuario_id, False)
        
        # Para supervisores, usar filtrado especial
        if usuario_actual and usuario_actual.rol in ['supervisor', 'consultor']:
            es_admin = False  # Usar filtrado de supervisor en lugar de admin
            # Para supervisores, pasar None como usuario_id para que vea todos los usuarios no-admin
            clientes = self.db.listar_clientes(None, es_admin)
        elif usuario_actual and usuario_actual.rol == 'admin':
            es_admin = True
            clientes = self.db.listar_clientes(usuario_id, es_admin)
        else:
            clientes = self.db.listar_clientes(usuario_id, es_admin)
        
        return [c for c in clientes if c.activo]
    
    def actualizar_cliente(self, cliente_id: int, usuario_id: int, es_admin: bool = False, **kwargs) -> bool:
        """Actualiza un cliente existente, respetando el aislamiento de datos"""
        cliente = self.db.obtener_cliente(cliente_id, usuario_id, es_admin)
        if not cliente:
            return False
        
        # Actualizar solo los campos proporcionados
        for key, value in kwargs.items():
            if hasattr(cliente, key):
                setattr(cliente, key, value)
        
        return self.db.actualizar_cliente(cliente, usuario_id, es_admin)
    
    def eliminar_cliente(self, cliente_id: int, usuario_id: int, es_admin: bool = False) -> bool:
        """Elimina un cliente, respetando el aislamiento de datos"""
        return self.db.eliminar_cliente(cliente_id, usuario_id, es_admin)

class PrestamoService:
    """Servicio para manejar la lógica de negocio de préstamos"""
    
    def __init__(self, db: Database):
        self.db = db
        self.pagare_generator = PagareGenerator()
    
    def crear_prestamo(self, cliente_id: int, monto: Decimal, plazo_dias: int, 
                       tasa_interes: Decimal, tipo_interes: str = "simple", descripcion: str = "", 
                       usuario_id: int = None, es_admin: bool = False) -> Prestamo:
        """Crea un nuevo préstamo y genera automáticamente el pagaré"""
        try:
            # Verificar que el cliente existe y pertenece al usuario
            cliente = self.db.obtener_cliente(cliente_id, usuario_id, es_admin)
            if not cliente:
                raise ValueError("Cliente no encontrado o no tienes permisos")
            
            # Crear el préstamo
            prestamo = Prestamo(
                id=self.db._get_next_id("prestamos"),
                cliente_id=cliente_id,
                monto=monto,
                plazo_dias=plazo_dias,
                tasa_interes=tasa_interes,
                tipo_interes=tipo_interes,
                descripcion=descripcion,
                fecha_inicio=datetime.now().date(),
                usuario_id=usuario_id
            )
            
            # Guardar en la base de datos
            prestamo_creado = self.db.agregar_prestamo(prestamo, usuario_id)
            
            if prestamo_creado:
                # Generar y enviar pagaré automáticamente
                self._generar_y_enviar_pagare(cliente, prestamo)
                
                return prestamo
            else:
                raise ValueError("Error al crear el préstamo")
                
        except Exception as e:
            print(f"❌ Error al crear préstamo: {e}")
            raise
    
    def _generar_y_enviar_pagare(self, cliente: Cliente, prestamo: Prestamo):
        """Genera y envía el pagaré automáticamente"""
        try:
            print(f"📋 Generando pagaré para préstamo #{prestamo.id}...")
            
            # 1. Guardar pagaré como archivo HTML
            archivo_pagare = self.pagare_generator.guardar_pagare_archivo(cliente, prestamo)
            
            if archivo_pagare:
                print(f"✅ Pagaré guardado en: {archivo_pagare}")
            
            # 2. Enviar por WhatsApp
            if cliente.telefono:
                print(f"📱 Enviando pagaré por WhatsApp a {cliente.telefono}...")
                enviado = self.pagare_generator.enviar_pagare_whatsapp(cliente, prestamo)
                
                if enviado:
                    print(f"✅ Pagaré enviado exitosamente por WhatsApp")
                else:
                    print(f"⚠️  No se pudo enviar el pagaré por WhatsApp")
            else:
                print(f"⚠️  Cliente sin teléfono, no se puede enviar por WhatsApp")
                
        except Exception as e:
            print(f"❌ Error al generar/enviar pagaré: {e}")
            # No fallar la creación del préstamo por errores en el pagaré
    
    def listar_prestamos(self, usuario_id: int, es_admin: bool = False) -> list:
        """Lista todos los préstamos del usuario"""
        return self.db.listar_prestamos(usuario_id, es_admin)
    
    def obtener_prestamo(self, prestamo_id: int, usuario_id: int, es_admin: bool = False) -> Prestamo:
        """Obtiene un préstamo específico"""
        return self.db.obtener_prestamo(prestamo_id, usuario_id, es_admin)
    
    def actualizar_prestamo(self, prestamo: Prestamo, usuario_id: int, es_admin: bool = False) -> bool:
        """Actualiza un préstamo existente"""
        return self.db.actualizar_prestamo(prestamo, usuario_id, es_admin)
    
    def eliminar_prestamo(self, prestamo_id: int, usuario_id: int, es_admin: bool = False) -> bool:
        """Elimina un préstamo físicamente"""
        return self.db.eliminar_prestamo(prestamo_id, usuario_id, es_admin)
    
    def listar_prestamos_activos(self, usuario_id: int, es_admin: bool = False) -> list:
        """Lista solo los préstamos activos"""
        print(f"🔍 listar_prestamos_activos - usuario_id: {usuario_id}, es_admin: {es_admin}")
        
        # Si usuario_id es None, significa que es un supervisor que quiere ver todos los usuarios no-admin
        if usuario_id is None:
            print(f"👁️ Supervisor - usuario_id es None, listando préstamos de usuarios no-admin")
            prestamos = self.db.listar_prestamos(None, False)
            prestamos_activos = [p for p in prestamos if p.estado == "activo"]
            print(f"📊 Préstamos totales: {len(prestamos)}, Activos: {len(prestamos_activos)}")
            return prestamos_activos
        
        # Obtener el usuario actual para verificar su rol
        usuario_actual = self.db.obtener_usuario(usuario_id, usuario_id, False)
        print(f"👤 Usuario actual: {usuario_actual.username if usuario_actual else 'None'}, Rol: {usuario_actual.rol if usuario_actual else 'None'}")
        
        # Para supervisores, usar filtrado especial
        if usuario_actual and usuario_actual.rol in ['supervisor', 'consultor']:
            print(f"👁️ Usuario es supervisor/consultor - usando filtrado especial")
            es_admin = False  # Usar filtrado de supervisor en lugar de admin
            # Para supervisores, pasar None como usuario_id para que vea todos los usuarios no-admin
            prestamos = self.db.listar_prestamos(None, es_admin)
        elif usuario_actual and usuario_actual.rol == 'admin':
            print(f"👑 Usuario es admin - usando filtrado de admin")
            es_admin = True
            prestamos = self.db.listar_prestamos(usuario_id, es_admin)
        else:
            print(f"👤 Usuario normal - usando filtrado estándar")
            prestamos = self.db.listar_prestamos(usuario_id, es_admin)
        
        prestamos_activos = [p for p in prestamos if p.estado == "activo"]
        print(f"📊 Préstamos encontrados: {len(prestamos)}, Activos: {len(prestamos_activos)}")
        return prestamos_activos
    
    def calcular_estadisticas_prestamos(self, usuario_id: int, es_admin: bool = False) -> dict:
        """Calcula estadísticas de préstamos"""
        prestamos = self.db.listar_prestamos(usuario_id, es_admin)
        
        if not prestamos:
            return {
                'total_prestamos': 0,
                'monto_total': 0,
                'prestamos_activos': 0,
                'prestamos_pagados': 0,
                'monto_pendiente': 0
            }
        
        total_prestamos = len(prestamos)
        monto_total = sum(p.monto for p in prestamos)
        prestamos_activos = len([p for p in prestamos if p.estado == "activo"])
        prestamos_pagados = len([p for p in prestamos if p.estado == "pagado"])
        monto_pendiente = sum(p.monto for p in prestamos if p.estado == "activo")
        
        return {
            'total_prestamos': total_prestamos,
            'monto_total': monto_total,
            'prestamos_activos': prestamos_activos,
            'prestamos_pagados': prestamos_pagados,
            'monto_pendiente': monto_pendiente
        }
    
    def calcular_cuota_diaria(self, prestamo_id: int, usuario_id: int, es_admin: bool = False) -> Decimal:
        """Calcula la cuota diaria de un préstamo, respetando el aislamiento de datos"""
        prestamo = self.obtener_prestamo(prestamo_id, usuario_id, es_admin)
        if not prestamo:
            raise ValueError(f"No existe un préstamo con ID {prestamo_id} o no tienes permisos para acceder a él")
        
        return prestamo.calcular_cuota_diaria()
    
    def obtener_resumen_prestamo(self, prestamo_id: int, usuario_id: int, es_admin: bool = False) -> Dict[str, Any]:
        """Obtiene un resumen completo de un préstamo, respetando el aislamiento de datos"""
        prestamo = self.obtener_prestamo(prestamo_id, usuario_id, es_admin)
        if not prestamo:
            raise ValueError(f"No existe un préstamo con ID {prestamo_id} o no tienes permisos para acceder a él")
        
        cliente = self.db.obtener_cliente(prestamo.cliente_id, usuario_id, es_admin)
        pagos = self.db.listar_pagos(usuario_id, es_admin, prestamo_id)
        
        return {
            'prestamo': prestamo,
            'cliente': cliente,
            'pagos': pagos,
            'resumen': {
                'monto_original': float(prestamo.monto),
                'interes_total': float(prestamo.calcular_interes_total()),
                'monto_total': float(prestamo.calcular_monto_total()),
                'cuota_diaria': float(prestamo.calcular_cuota_diaria()),
                'saldo_pendiente': float(prestamo.calcular_saldo_pendiente()),
                'pagos_realizados': len(pagos),
                'cuotas_pendientes': prestamo.plazo_dias - len(pagos)
            }
        }
    
    def eliminar_prestamo(self, prestamo_id: int, usuario_id: int, es_admin: bool = False) -> bool:
        """Elimina un préstamo, respetando el aislamiento de datos"""
        return self.db.eliminar_prestamo(prestamo_id, usuario_id, es_admin)

class PagoService:
    def __init__(self, db: Database):
        self.db = db
    
    def registrar_pago(self, prestamo_id: int, monto: Decimal, concepto: str = "Pago de cuota", 
                      fecha: Optional[date] = None, usuario_id: int = None) -> Pago:
        """Registra un nuevo pago asociado a un usuario"""
        # Verificar que el préstamo existe y pertenece al usuario
        prestamo = self.db.obtener_prestamo(prestamo_id, usuario_id, False)
        if not prestamo:
            raise ValueError(f"No existe un préstamo con ID {prestamo_id} o no tienes permisos para acceder a él")
        
        if prestamo.estado != "activo":
            raise ValueError("No se puede registrar un pago en un préstamo no activo")
        
        # Verificar que el monto sea válido
        if monto <= 0:
            raise ValueError("El monto del pago debe ser mayor a 0")
        
        # Verificar que no se exceda el saldo pendiente
        saldo_pendiente = prestamo.calcular_saldo_pendiente()
        if monto > saldo_pendiente:
            raise ValueError(f"El monto del pago ({monto}) excede el saldo pendiente ({saldo_pendiente})")
        
        # Crear el pago
        pago = Pago(
            id=0,  # Se asignará automáticamente
            prestamo_id=prestamo_id,
            monto=monto,
            fecha=fecha,
            concepto=concepto,
            usuario_id=usuario_id
        )
        
        # Calcular saldo después del pago
        pago.saldo_despues = saldo_pendiente - monto
        
        # Guardar el pago
        pago_creado = self.db.agregar_pago(pago, usuario_id)
        
        if pago_creado:
            # Actualizar el préstamo con el nuevo pago
            prestamo.agregar_pago(pago)
            self.db.actualizar_prestamo(prestamo, usuario_id, False)
            
            return pago
        else:
            raise ValueError("Error al guardar el pago")
    
    def listar_pagos_prestamo(self, prestamo_id: int, usuario_id: int, es_admin: bool = False) -> List[Pago]:
        """Lista todos los pagos de un préstamo específico, respetando el aislamiento de datos"""
        # Si usuario_id es None, significa que es un supervisor que quiere ver todos los usuarios no-admin
        if usuario_id is None:
            return self.db.listar_pagos(None, False, prestamo_id)
        
        # Obtener el usuario actual para verificar su rol
        usuario_actual = self.db.obtener_usuario(usuario_id, usuario_id, False)
        
        # Para supervisores, usar filtrado especial
        if usuario_actual and usuario_actual.rol in ['supervisor', 'consultor']:
            es_admin = False  # Usar filtrado de supervisor en lugar de admin
            # Para supervisores, pasar None como usuario_id para que vea todos los usuarios no-admin
            return self.db.listar_pagos(None, es_admin, prestamo_id)
        elif usuario_actual and usuario_actual.rol == 'admin':
            es_admin = True
            return self.db.listar_pagos(usuario_id, es_admin, prestamo_id)
        else:
            return self.db.listar_pagos(usuario_id, es_admin, prestamo_id)
    
    def obtener_historial_pagos(self, prestamo_id: int, usuario_id: int, es_admin: bool = False) -> List[Dict[str, Any]]:
        """Obtiene el historial de pagos de un préstamo con información detallada, respetando el aislamiento de datos"""
        pagos = self.listar_pagos_prestamo(prestamo_id, usuario_id, es_admin)
        prestamo = self.db.obtener_prestamo(prestamo_id, usuario_id, es_admin)
        
        historial = []
        saldo_acumulado = prestamo.calcular_monto_total()
        
        for pago in pagos:
            saldo_acumulado -= pago.monto
            historial.append({
                'fecha': pago.fecha,
                'monto': float(pago.monto),
                'concepto': pago.concepto,
                'saldo_restante': float(saldo_acumulado)
            })
        
        return historial
    
    def eliminar_pago(self, pago_id: int, usuario_id: int, es_admin: bool = False) -> bool:
        """Elimina un pago específico, respetando el aislamiento de datos"""
        return self.db.eliminar_pago(pago_id, usuario_id, es_admin)

class ReporteService:
    def __init__(self, db: Database):
        self.db = db
    
    def generar_reporte_general(self, usuario_id: int, es_admin: bool = False) -> Dict[str, Any]:
        """Genera un reporte general del sistema, respetando el aislamiento de datos"""
        # Si usuario_id es None, significa que es un supervisor que quiere ver todos los usuarios no-admin
        if usuario_id is None:
            return self.db.obtener_estadisticas(None, False)
        
        # Obtener el usuario actual para verificar su rol
        usuario_actual = self.db.obtener_usuario(usuario_id, usuario_id, False)
        
        # Para supervisores, usar filtrado especial
        if usuario_actual and usuario_actual.rol in ['supervisor', 'consultor']:
            es_admin = False  # Usar filtrado de supervisor en lugar de admin
            # Para supervisores, pasar None como usuario_id para que vea todos los usuarios no-admin
            return self.db.obtener_estadisticas(None, False)
        elif usuario_actual and usuario_actual.rol == 'admin':
            es_admin = True
            return self.db.obtener_estadisticas(usuario_id, True)
        else:
            if es_admin:
                # Los admins pueden ver estadísticas de todo el sistema
                return self.db.obtener_estadisticas(usuario_id, True)
            else:
                # Los usuarios solo ven sus propias estadísticas
                return self.db.obtener_estadisticas(usuario_id, False)
    
    def generar_reporte_cliente(self, cliente_id: int, usuario_id: int, es_admin: bool = False) -> Dict[str, Any]:
        """Genera un reporte detallado de un cliente, respetando el aislamiento de datos"""
        cliente = self.db.obtener_cliente(cliente_id, usuario_id, es_admin)
        if not cliente:
            raise ValueError(f"No existe un cliente con ID {cliente_id} o no tienes permisos para acceder a él")
        
        prestamos = self.db.listar_prestamos(usuario_id, es_admin, cliente_id)
        total_prestado = sum(p.monto for p in prestamos)
        total_pagado = sum(p.monto for p in self.db.listar_pagos(usuario_id, es_admin))
        
        return {
            'cliente': cliente,
            'prestamos': prestamos,
            'resumen': {
                'total_prestamos': len(prestamos),
                'monto_total_prestado': float(total_prestado),
                'monto_total_pagado': float(total_pagado),
                'saldo_total_pendiente': float(total_prestado - total_pagado)
            }
        }
    
    def generar_reporte_prestamos_activos(self, usuario_id: int, es_admin: bool = False) -> List[Dict[str, Any]]:
        """Genera un reporte de todos los préstamos activos, respetando el aislamiento de datos"""
        # Si usuario_id es None, significa que es un supervisor que quiere ver todos los usuarios no-admin
        if usuario_id is None:
            prestamos_activos = self.db.listar_prestamos(None, False)
            prestamos_activos = [p for p in prestamos_activos if p.estado == "activo"]
        else:
            # Obtener el usuario actual para verificar su rol
            usuario_actual = self.db.obtener_usuario(usuario_id, usuario_id, False)
            
            # Para supervisores, usar filtrado especial
            if usuario_actual and usuario_actual.rol in ['supervisor', 'consultor']:
                es_admin = False  # Usar filtrado de supervisor en lugar de admin
                # Para supervisores, pasar None como usuario_id para que vea todos los usuarios no-admin
                prestamos_activos = self.db.listar_prestamos(None, es_admin)
            elif usuario_actual and usuario_actual.rol == 'admin':
                es_admin = True
                prestamos_activos = self.db.listar_prestamos(usuario_id, es_admin)
            else:
                prestamos_activos = self.db.listar_prestamos(usuario_id, es_admin)
        
        # Filtrar solo préstamos activos
        prestamos_activos = [p for p in prestamos_activos if p.estado == "activo"]
        reporte = []
        
        for prestamo in prestamos_activos:
            # Para supervisores y consultores, usar None como usuario_id para obtener clientes
            if usuario_id is None:
                cliente = self.db.obtener_cliente(prestamo.cliente_id, None, True)
            else:
                cliente = self.db.obtener_cliente(prestamo.cliente_id, usuario_id, es_admin)
            
            if cliente:  # Solo incluir si el cliente es accesible
                reporte.append({
                    'id_prestamo': prestamo.id,
                    'cliente': f"{cliente.nombre} {cliente.apellido}",
                    'dni': cliente.dni,
                    'monto_original': float(prestamo.monto),
                    'tasa_interes': float(prestamo.tasa_interes),
                    'plazo_dias': prestamo.plazo_dias,
                    'cuota_diaria': float(prestamo.calcular_cuota_diaria()),
                    'saldo_pendiente': float(prestamo.calcular_saldo_pendiente()),
                    'fecha_inicio': prestamo.fecha_inicio,
                    'estado': prestamo.estado
                })
        
        return reporte

class ConfiguracionService:
    def __init__(self, db: Database):
        self.db = db
    
    def obtener_configuracion(self) -> Dict[str, Any]:
        """Obtiene la configuración actual del sistema"""
        return self.db.obtener_configuracion()
    
    def actualizar_configuracion(self, nueva_config: Dict[str, Any]) -> bool:
        """Actualiza la configuración del sistema"""
        return self.db.actualizar_configuracion(nueva_config)
    
    def cambiar_nombre_sistema(self, nuevo_nombre: str) -> bool:
        """Cambia el nombre del sistema"""
        return self.db.cambiar_nombre_sistema(nuevo_nombre)
