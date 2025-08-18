from typing import List, Optional, Dict, Any
from decimal import Decimal
from datetime import date, datetime
from models import Cliente, Prestamo, Pago
from database import Database

class ClienteService:
    def __init__(self, db: Database):
        self.db = db
    
    def crear_cliente(self, nombre: str, apellido: str, dni: str, telefono: str, email: str = "") -> Cliente:
        """Crea un nuevo cliente"""
        # Verificar que el DNI no esté duplicado
        if self.db.obtener_cliente_por_dni(dni):
            raise ValueError(f"Ya existe un cliente con el DNI {dni}")
        
        cliente = Cliente(
            id=0,  # Se asignará automáticamente
            nombre=nombre,
            apellido=apellido,
            dni=dni,
            telefono=telefono,
            email=email
        )
        
        return self.db.agregar_cliente(cliente)
    
    def buscar_cliente(self, termino: str) -> List[Cliente]:
        """Busca clientes por nombre, apellido o DNI"""
        return self.db.buscar_clientes(termino)
    
    def obtener_cliente(self, cliente_id: int) -> Optional[Cliente]:
        """Obtiene un cliente por ID"""
        return self.db.obtener_cliente(cliente_id)
    
    def listar_clientes(self) -> List[Cliente]:
        """Lista todos los clientes activos"""
        clientes = self.db.listar_clientes()
        return [c for c in clientes if c.activo]
    
    def actualizar_cliente(self, cliente_id: int, **kwargs) -> bool:
        """Actualiza un cliente existente"""
        cliente = self.db.obtener_cliente(cliente_id)
        if not cliente:
            return False
        
        # Actualizar solo los campos proporcionados
        for key, value in kwargs.items():
            if hasattr(cliente, key):
                setattr(cliente, key, value)
        
        return self.db.actualizar_cliente(cliente)
    
    def eliminar_cliente(self, cliente_id: int) -> bool:
        """Elimina un cliente completamente de la base de datos"""
        return self.db.eliminar_cliente_completo(cliente_id)

class PrestamoService:
    def __init__(self, db: Database):
        self.db = db
    
    def crear_prestamo(self, cliente_id: int, monto: Decimal, tasa_interes: Decimal, 
                       plazo_dias: int, tipo_interes: str = "simple", 
                       fecha_inicio: Optional[date] = None) -> Prestamo:
        """Crea un nuevo préstamo"""
        # Verificar que el cliente existe
        cliente = self.db.obtener_cliente(cliente_id)
        if not cliente:
            raise ValueError(f"No existe un cliente con ID {cliente_id}")
        
        if not cliente.activo:
            raise ValueError("No se puede crear un préstamo para un cliente inactivo")
        
        # Validar parámetros del préstamo
        if monto <= 0:
            raise ValueError("El monto debe ser mayor a 0")
        
        if tasa_interes < 0:
            raise ValueError("La tasa de interés no puede ser negativa")
        
        if plazo_dias <= 0:
            raise ValueError("El plazo debe ser mayor a 0")
        
        if tipo_interes not in ["simple", "compuesto", "gota_a_gota"]:
            raise ValueError("El tipo de interés debe ser 'simple', 'compuesto' o 'gota_a_gota'")
        
        prestamo = Prestamo(
            id=0,  # Se asignará automáticamente
            cliente_id=cliente_id,
            monto=monto,
            tasa_interes=tasa_interes,
            plazo_dias=plazo_dias,
            tipo_interes=tipo_interes,
            fecha_inicio=fecha_inicio
        )
        
        return self.db.agregar_prestamo(prestamo)
    
    def obtener_prestamo(self, prestamo_id: int) -> Optional[Prestamo]:
        """Obtiene un préstamo por ID"""
        return self.db.obtener_prestamo(prestamo_id)
    
    def listar_prestamos_cliente(self, cliente_id: int) -> List[Prestamo]:
        """Lista todos los préstamos de un cliente específico"""
        return self.db.listar_prestamos(cliente_id)
    
    def listar_prestamos_activos(self) -> List[Prestamo]:
        """Lista todos los préstamos activos"""
        return self.db.obtener_prestamos_activos()
    
    def calcular_cuota_diaria(self, prestamo_id: int) -> Decimal:
        """Calcula la cuota diaria de un préstamo"""
        prestamo = self.obtener_prestamo(prestamo_id)
        if not prestamo:
            raise ValueError(f"No existe un préstamo con ID {prestamo_id}")
        
        return prestamo.calcular_cuota_diaria()
    
    def obtener_resumen_prestamo(self, prestamo_id: int) -> Dict[str, Any]:
        """Obtiene un resumen completo de un préstamo"""
        prestamo = self.obtener_prestamo(prestamo_id)
        if not prestamo:
            raise ValueError(f"No existe un préstamo con ID {prestamo_id}")
        
        cliente = self.db.obtener_cliente(prestamo.cliente_id)
        pagos = self.db.listar_pagos(prestamo_id)
        
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
    
    def eliminar_prestamo(self, prestamo_id: int) -> bool:
        """Elimina un préstamo (con o sin pagos)"""
        prestamo = self.obtener_prestamo(prestamo_id)
        if not prestamo:
            return False
        
        # Ahora se puede eliminar cualquier préstamo
        return self.db.eliminar_prestamo(prestamo_id)

class PagoService:
    def __init__(self, db: Database):
        self.db = db
    
    def registrar_pago(self, prestamo_id: int, monto: Decimal, concepto: str = "Pago de cuota", 
                      fecha: Optional[date] = None) -> Pago:
        """Registra un nuevo pago"""
        # Verificar que el préstamo existe
        prestamo = self.db.obtener_prestamo(prestamo_id)
        if not prestamo:
            raise ValueError(f"No existe un préstamo con ID {prestamo_id}")
        
        if prestamo.estado != "activo":
            raise ValueError("No se puede registrar un pago en un préstamo no activo")
        
        # Verificar que el monto sea válido
        if monto <= 0:
            raise ValueError("El monto del pago debe ser mayor a 0")
        
        # Verificar que no se exceda el saldo pendiente
        saldo_pendiente = prestamo.calcular_saldo_pendiente()
        if monto > saldo_pendiente:
            raise ValueError(f"El monto del pago ({monto}) excede el saldo pendiente ({saldo_pendiente})")
        
        pago = Pago(
            id=0,  # Se asignará automáticamente
            prestamo_id=prestamo_id,
            monto=monto,
            fecha=fecha,
            concepto=concepto
        )
        
        return self.db.agregar_pago(pago)
    
    def listar_pagos_prestamo(self, prestamo_id: int) -> List[Pago]:
        """Lista todos los pagos de un préstamo específico"""
        return self.db.listar_pagos(prestamo_id)
    
    def obtener_historial_pagos(self, prestamo_id: int) -> List[Dict[str, Any]]:
        """Obtiene el historial de pagos de un préstamo con información detallada"""
        pagos = self.listar_pagos_prestamo(prestamo_id)
        prestamo = self.db.obtener_prestamo(prestamo_id)
        
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
    
    def eliminar_pago(self, pago_id: int) -> bool:
        """Elimina un pago específico"""
        return self.db.eliminar_pago(pago_id)

class ReporteService:
    def __init__(self, db: Database):
        self.db = db
    
    def generar_reporte_general(self) -> Dict[str, Any]:
        """Genera un reporte general del sistema"""
        return self.db.obtener_estadisticas()
    
    def generar_reporte_cliente(self, cliente_id: int) -> Dict[str, Any]:
        """Genera un reporte detallado de un cliente"""
        cliente = self.db.obtener_cliente(cliente_id)
        if not cliente:
            raise ValueError(f"No existe un cliente con ID {cliente_id}")
        
        prestamos = self.db.listar_prestamos(cliente_id)
        total_prestado = sum(p.monto for p in prestamos)
        total_pagado = sum(p.monto for p in self.db.listar_pagos())
        
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
    
    def generar_reporte_prestamos_activos(self) -> List[Dict[str, Any]]:
        """Genera un reporte de todos los préstamos activos"""
        prestamos_activos = self.db.obtener_prestamos_activos()
        reporte = []
        
        for prestamo in prestamos_activos:
            cliente = self.db.obtener_cliente(prestamo.cliente_id)
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
