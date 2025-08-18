#!/usr/bin/env python3
"""
Sistema de Préstamos de Dinero
===============================

Un sistema completo para gestionar préstamos de dinero con cálculo de intereses,
gestión de clientes, pagos y reportes.

Autor: Sistema de Préstamos
Versión: 1.0
"""

import sys
import os
from decimal import Decimal, InvalidOperation
from datetime import date
from colorama import init, Fore, Back, Style
from tabulate import tabulate

# Importar módulos del sistema
from database import Database
from services import ClienteService, PrestamoService, PagoService, ReporteService

# Inicializar colorama para colores en consola
init(autoreset=True)

class SistemaPrestamos:
    def __init__(self):
        self.db = Database()
        self.cliente_service = ClienteService(self.db)
        self.prestamo_service = PrestamoService(self.db)
        self.pago_service = PagoService(self.db)
        self.reporte_service = ReporteService(self.db)
    
    def mostrar_menu_principal(self):
        """Muestra el menú principal del sistema"""
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"{Fore.CYAN}{'='*60}")
        print(f"{Fore.CYAN}{'SISTEMA DE PRÉSTAMOS DE DINERO':^60}")
        print(f"{Fore.CYAN}{'='*60}")
        print()
        print(f"{Fore.YELLOW}Menú Principal:")
        print(f"{Fore.WHITE}1. {Fore.GREEN}Gestión de Clientes")
        print(f"{Fore.WHITE}2. {Fore.GREEN}Gestión de Préstamos")
        print(f"{Fore.WHITE}3. {Fore.GREEN}Gestión de Pagos")
        print(f"{Fore.WHITE}4. {Fore.GREEN}Reportes")
        print(f"{Fore.WHITE}5. {Fore.RED}Salir")
        print()
    
    def mostrar_menu_clientes(self):
        """Muestra el menú de gestión de clientes"""
        while True:
            os.system('cls' if os.name == 'nt' else 'clear')
            print(f"{Fore.CYAN}{'GESTIÓN DE CLIENTES':^60}")
            print(f"{Fore.CYAN}{'='*60}")
            print()
            print(f"{Fore.YELLOW}Opciones:")
            print(f"{Fore.WHITE}1. {Fore.GREEN}Registrar nuevo cliente")
            print(f"{Fore.WHITE}2. {Fore.GREEN}Buscar cliente")
            print(f"{Fore.WHITE}3. {Fore.GREEN}Listar todos los clientes")
            print(f"{Fore.WHITE}4. {Fore.GREEN}Actualizar cliente")
            print(f"{Fore.WHITE}5. {Fore.GREEN}Eliminar cliente")
            print(f"{Fore.WHITE}6. {Fore.BLUE}Volver al menú principal")
            print()
            
            opcion = input(f"{Fore.YELLOW}Seleccione una opción: {Fore.WHITE}")
            
            if opcion == "1":
                self.registrar_cliente()
            elif opcion == "2":
                self.buscar_cliente()
            elif opcion == "3":
                self.listar_clientes()
            elif opcion == "4":
                self.actualizar_cliente()
            elif opcion == "5":
                self.eliminar_cliente()
            elif opcion == "6":
                break
            else:
                print(f"{Fore.RED}Opción inválida. Intente nuevamente.")
                input("Presione Enter para continuar...")
    
    def mostrar_menu_prestamos(self):
        """Muestra el menú de gestión de préstamos"""
        while True:
            os.system('cls' if os.name == 'nt' else 'clear')
            print(f"{Fore.CYAN}{'GESTIÓN DE PRÉSTAMOS':^60}")
            print(f"{Fore.CYAN}{'='*60}")
            print()
            print(f"{Fore.YELLOW}Opciones:")
            print(f"{Fore.WHITE}1. {Fore.GREEN}Crear nuevo préstamo")
            print(f"{Fore.WHITE}2. {Fore.GREEN}Consultar préstamo")
            print(f"{Fore.WHITE}3. {Fore.GREEN}Listar préstamos de un cliente")
            print(f"{Fore.WHITE}4. {Fore.GREEN}Listar préstamos activos")
            print(f"{Fore.WHITE}5. {Fore.GREEN}Calcular cuota mensual")
            print(f"{Fore.WHITE}6. {Fore.BLUE}Volver al menú principal")
            print()
            
            opcion = input(f"{Fore.YELLOW}Seleccione una opción: {Fore.WHITE}")
            
            if opcion == "1":
                self.crear_prestamo()
            elif opcion == "2":
                self.consultar_prestamo()
            elif opcion == "3":
                self.listar_prestamos_cliente()
            elif opcion == "4":
                self.listar_prestamos_activos()
            elif opcion == "5":
                self.calcular_cuota_mensual()
            elif opcion == "6":
                break
            else:
                print(f"{Fore.RED}Opción inválida. Intente nuevamente.")
                input("Presione Enter para continuar...")
    
    def mostrar_menu_pagos(self):
        """Muestra el menú de gestión de pagos"""
        while True:
            os.system('cls' if os.name == 'nt' else 'clear')
            print(f"{Fore.CYAN}{'GESTIÓN DE PAGOS':^60}")
            print(f"{Fore.CYAN}{'='*60}")
            print()
            print(f"{Fore.YELLOW}Opciones:")
            print(f"{Fore.WHITE}1. {Fore.GREEN}Registrar pago")
            print(f"{Fore.WHITE}2. {Fore.GREEN}Ver historial de pagos")
            print(f"{Fore.WHITE}3. {Fore.BLUE}Volver al menú principal")
            print()
            
            opcion = input(f"{Fore.YELLOW}Seleccione una opción: {Fore.WHITE}")
            
            if opcion == "1":
                self.registrar_pago()
            elif opcion == "2":
                self.ver_historial_pagos()
            elif opcion == "3":
                break
            else:
                print(f"{Fore.RED}Opción inválida. Intente nuevamente.")
                input("Presione Enter para continuar...")
    
    def mostrar_menu_reportes(self):
        """Muestra el menú de reportes"""
        while True:
            os.system('cls' if os.name == 'nt' else 'clear')
            print(f"{Fore.CYAN}{'REPORTES':^60}")
            print(f"{Fore.CYAN}{'='*60}")
            print()
            print(f"{Fore.YELLOW}Opciones:")
            print(f"{Fore.WHITE}1. {Fore.GREEN}Reporte general del sistema")
            print(f"{Fore.WHITE}2. {Fore.GREEN}Reporte de un cliente")
            print(f"{Fore.WHITE}3. {Fore.GREEN}Reporte de préstamos activos")
            print(f"{Fore.WHITE}4. {Fore.BLUE}Volver al menú principal")
            print()
            
            opcion = input(f"{Fore.YELLOW}Seleccione una opción: {Fore.WHITE}")
            
            if opcion == "1":
                self.reporte_general()
            elif opcion == "2":
                self.reporte_cliente()
            elif opcion == "3":
                self.reporte_prestamos_activos()
            elif opcion == "4":
                break
            else:
                print(f"{Fore.RED}Opción inválida. Intente nuevamente.")
                input("Presione Enter para continuar...")
    
    # Métodos de gestión de clientes
    def registrar_cliente(self):
        """Registra un nuevo cliente"""
        print(f"\n{Fore.CYAN}REGISTRAR NUEVO CLIENTE")
        print(f"{Fore.CYAN}{'-'*30}")
        
        try:
            nombre = input(f"{Fore.YELLOW}Nombre: {Fore.WHITE}").strip()
            apellido = input(f"{Fore.YELLOW}Apellido: {Fore.WHITE}").strip()
            dni = input(f"{Fore.YELLOW}DNI: {Fore.WHITE}").strip()
            telefono = input(f"{Fore.YELLOW}Teléfono: {Fore.WHITE}").strip()
            email = input(f"{Fore.YELLOW}Email (opcional): {Fore.WHITE}").strip()
            
            if not nombre or not apellido or not dni or not telefono:
                print(f"{Fore.RED}Los campos nombre, apellido, DNI y teléfono son obligatorios.")
                input("Presione Enter para continuar...")
                return
            
            cliente = self.cliente_service.crear_cliente(nombre, apellido, dni, telefono, email)
            print(f"\n{Fore.GREEN}✓ Cliente registrado exitosamente!")
            print(f"{Fore.WHITE}ID: {cliente.id}")
            print(f"{Fore.WHITE}Cliente: {cliente}")
            
        except ValueError as e:
            print(f"\n{Fore.RED}Error: {e}")
        except Exception as e:
            print(f"\n{Fore.RED}Error inesperado: {e}")
        
        input("\nPresione Enter para continuar...")
    
    def buscar_cliente(self):
        """Busca un cliente"""
        print(f"\n{Fore.CYAN}BUSCAR CLIENTE")
        print(f"{Fore.CYAN}{'-'*20}")
        
        termino = input(f"{Fore.YELLOW}Ingrese nombre, apellido o DNI: {Fore.WHITE}").strip()
        if not termino:
            print(f"{Fore.RED}Debe ingresar un término de búsqueda.")
            input("Presione Enter para continuar...")
            return
        
        try:
            clientes = self.cliente_service.buscar_cliente(termino)
            if clientes:
                print(f"\n{Fore.GREEN}Clientes encontrados:")
                self._mostrar_tabla_clientes(clientes)
            else:
                print(f"\n{Fore.YELLOW}No se encontraron clientes con ese término.")
        except Exception as e:
            print(f"\n{Fore.RED}Error: {e}")
        
        input("\nPresione Enter para continuar...")
    
    def listar_clientes(self):
        """Lista todos los clientes"""
        print(f"\n{Fore.CYAN}LISTA DE CLIENTES")
        print(f"{Fore.CYAN}{'-'*20}")
        
        try:
            clientes = self.cliente_service.listar_clientes()
            if clientes:
                self._mostrar_tabla_clientes(clientes)
            else:
                print(f"\n{Fore.YELLOW}No hay clientes registrados.")
        except Exception as e:
            print(f"\n{Fore.RED}Error: {e}")
        
        input("\nPresione Enter para continuar...")
    
    def actualizar_cliente(self):
        """Actualiza un cliente existente"""
        print(f"\n{Fore.CYAN}ACTUALIZAR CLIENTE")
        print(f"{Fore.CYAN}{'-'*20}")
        
        try:
            cliente_id = int(input(f"{Fore.YELLOW}ID del cliente: {Fore.WHITE}"))
            cliente = self.cliente_service.obtener_cliente(cliente_id)
            
            if not cliente:
                print(f"{Fore.RED}No se encontró un cliente con ese ID.")
                input("Presione Enter para continuar...")
                return
            
            print(f"\n{Fore.WHITE}Cliente actual: {cliente}")
            print(f"\n{Fore.YELLOW}Ingrese los nuevos valores (deje vacío para mantener el actual):")
            
            nombre = input(f"{Fore.YELLOW}Nuevo nombre: {Fore.WHITE}").strip()
            apellido = input(f"{Fore.YELLOW}Nuevo apellido: {Fore.WHITE}").strip()
            telefono = input(f"{Fore.YELLOW}Nuevo teléfono: {Fore.WHITE}").strip()
            email = input(f"{Fore.YELLOW}Nuevo email: {Fore.WHITE}").strip()
            
            actualizaciones = {}
            if nombre:
                actualizaciones['nombre'] = nombre
            if apellido:
                actualizaciones['apellido'] = apellido
            if telefono:
                actualizaciones['telefono'] = telefono
            if email:
                actualizaciones['email'] = email
            
            if actualizaciones:
                if self.cliente_service.actualizar_cliente(cliente_id, **actualizaciones):
                    print(f"\n{Fore.GREEN}✓ Cliente actualizado exitosamente!")
                else:
                    print(f"\n{Fore.RED}Error al actualizar el cliente.")
            else:
                print(f"\n{Fore.YELLOW}No se realizaron cambios.")
                
        except ValueError:
            print(f"{Fore.RED}ID inválido.")
        except Exception as e:
            print(f"\n{Fore.RED}Error: {e}")
        
        input("\nPresione Enter para continuar...")
    
    def eliminar_cliente(self):
        """Elimina un cliente (marca como inactivo)"""
        print(f"\n{Fore.CYAN}ELIMINAR CLIENTE")
        print(f"{Fore.CYAN}{'-'*20}")
        
        try:
            cliente_id = int(input(f"{Fore.YELLOW}ID del cliente: {Fore.WHITE}"))
            cliente = self.cliente_service.obtener_cliente(cliente_id)
            
            if not cliente:
                print(f"{Fore.RED}No se encontró un cliente con ese ID.")
                input("Presione Enter para continuar...")
                return
            
            print(f"\n{Fore.WHITE}Cliente a eliminar: {cliente}")
            confirmacion = input(f"\n{Fore.RED}¿Está seguro? (s/n): {Fore.WHITE}").lower()
            
            if confirmacion == 's':
                if self.cliente_service.eliminar_cliente(cliente_id):
                    print(f"\n{Fore.GREEN}✓ Cliente eliminado exitosamente!")
                else:
                    print(f"\n{Fore.RED}Error al eliminar el cliente.")
            else:
                print(f"\n{Fore.YELLOW}Operación cancelada.")
                
        except ValueError:
            print(f"{Fore.RED}ID inválido.")
        except Exception as e:
            print(f"\n{Fore.RED}Error: {e}")
        
        input("\nPresione Enter para continuar...")
    
    # Métodos de gestión de préstamos
    def crear_prestamo(self):
        """Crea un nuevo préstamo"""
        print(f"\n{Fore.CYAN}CREAR NUEVO PRÉSTAMO")
        print(f"{Fore.CYAN}{'-'*25}")
        
        try:
            cliente_id = int(input(f"{Fore.YELLOW}ID del cliente: {Fore.WHITE}"))
            cliente = self.cliente_service.obtener_cliente(cliente_id)
            
            if not cliente:
                print(f"{Fore.RED}No se encontró un cliente con ese ID.")
                input("Presione Enter para continuar...")
                return
            
            if not cliente.activo:
                print(f"{Fore.RED}No se puede crear un préstamo para un cliente inactivo.")
                input("Presione Enter para continuar...")
                return
            
            print(f"\n{Fore.WHITE}Cliente: {cliente}")
            
            monto = Decimal(input(f"{Fore.YELLOW}Monto del préstamo: {Fore.WHITE}"))
            tasa_interes = Decimal(input(f"{Fore.YELLOW}Tasa de interés anual (%): {Fore.WHITE}"))
            plazo_meses = int(input(f"{Fore.YELLOW}Plazo en meses: {Fore.WHITE}"))
            
            print(f"\n{Fore.YELLOW}Tipo de interés:")
            print(f"{Fore.WHITE}1. Simple")
            print(f"{Fore.WHITE}2. Compuesto")
            tipo_opcion = input(f"{Fore.YELLOW}Seleccione (1-2): {Fore.WHITE}")
            
            tipo_interes = "simple" if tipo_opcion == "1" else "compuesto"
            
            prestamo = self.prestamo_service.crear_prestamo(
                cliente_id, monto, tasa_interes, plazo_meses, tipo_interes
            )
            
            print(f"\n{Fore.GREEN}✓ Préstamo creado exitosamente!")
            print(f"{Fore.WHITE}ID del préstamo: {prestamo.id}")
            print(f"{Fore.WHITE}Monto total a pagar: ${prestamo.calcular_monto_total():.2f}")
            print(f"{Fore.WHITE}Cuota mensual: ${prestamo.calcular_cuota_mensual():.2f}")
            
        except ValueError as e:
            print(f"\n{Fore.RED}Error: {e}")
        except InvalidOperation:
            print(f"\n{Fore.RED}Error: Valores numéricos inválidos.")
        except Exception as e:
            print(f"\n{Fore.RED}Error inesperado: {e}")
        
        input("\nPresione Enter para continuar...")
    
    def consultar_prestamo(self):
        """Consulta un préstamo específico"""
        print(f"\n{Fore.CYAN}CONSULTAR PRÉSTAMO")
        print(f"{Fore.CYAN}{'-'*20}")
        
        try:
            prestamo_id = int(input(f"{Fore.YELLOW}ID del préstamo: {Fore.WHITE}"))
            resumen = self.prestamo_service.obtener_resumen_prestamo(prestamo_id)
            
            print(f"\n{Fore.CYAN}RESUMEN DEL PRÉSTAMO")
            print(f"{Fore.CYAN}{'='*30}")
            print(f"{Fore.WHITE}Cliente: {resumen['cliente']}")
            print(f"{Fore.WHITE}Monto original: ${resumen['resumen']['monto_original']:.2f}")
            print(f"{Fore.WHITE}Interés total: ${resumen['resumen']['interes_total']:.2f}")
            print(f"{Fore.WHITE}Monto total: ${resumen['resumen']['monto_total']:.2f}")
            print(f"{Fore.WHITE}Cuota mensual: ${resumen['resumen']['cuota_mensual']:.2f}")
            print(f"{Fore.WHITE}Saldo pendiente: ${resumen['resumen']['saldo_pendiente']:.2f}")
            print(f"{Fore.WHITE}Pagos realizados: {resumen['resumen']['pagos_realizados']}")
            print(f"{Fore.WHITE}Cuotas pendientes: {resumen['resumen']['cuotas_pendientes']}")
            
        except ValueError:
            print(f"{Fore.RED}ID inválido.")
        except Exception as e:
            print(f"\n{Fore.RED}Error: {e}")
        
        input("\nPresione Enter para continuar...")
    
    def listar_prestamos_cliente(self):
        """Lista los préstamos de un cliente específico"""
        print(f"\n{Fore.CYAN}PRÉSTAMOS DE UN CLIENTE")
        print(f"{Fore.CYAN}{'-'*30}")
        
        try:
            cliente_id = int(input(f"{Fore.YELLOW}ID del cliente: {Fore.WHITE}"))
            prestamos = self.prestamo_service.listar_prestamos_cliente(cliente_id)
            
            if prestamos:
                print(f"\n{Fore.GREEN}Préstamos encontrados:")
                self._mostrar_tabla_prestamos(prestamos)
            else:
                print(f"\n{Fore.YELLOW}El cliente no tiene préstamos registrados.")
                
        except ValueError:
            print(f"{Fore.RED}ID inválido.")
        except Exception as e:
            print(f"\n{Fore.RED}Error: {e}")
        
        input("\nPresione Enter para continuar...")
    
    def listar_prestamos_activos(self):
        """Lista todos los préstamos activos"""
        print(f"\n{Fore.CYAN}PRÉSTAMOS ACTIVOS")
        print(f"{Fore.CYAN}{'-'*20}")
        
        try:
            prestamos = self.prestamo_service.listar_prestamos_activos()
            if prestamos:
                self._mostrar_tabla_prestamos(prestamos)
            else:
                print(f"\n{Fore.YELLOW}No hay préstamos activos.")
        except Exception as e:
            print(f"\n{Fore.RED}Error: {e}")
        
        input("\nPresione Enter para continuar...")
    
    def calcular_cuota_mensual(self):
        """Calcula la cuota mensual de un préstamo"""
        print(f"\n{Fore.CYAN}CALCULAR CUOTA MENSUAL")
        print(f"{Fore.CYAN}{'-'*30}")
        
        try:
            prestamo_id = int(input(f"{Fore.YELLOW}ID del préstamo: {Fore.WHITE}"))
            cuota = self.prestamo_service.calcular_cuota_mensual(prestamo_id)
            
            print(f"\n{Fore.GREEN}Cuota mensual: ${cuota:.2f}")
            
        except ValueError:
            print(f"{Fore.RED}ID inválido.")
        except Exception as e:
            print(f"\n{Fore.RED}Error: {e}")
        
        input("\nPresione Enter para continuar...")
    
    # Métodos de gestión de pagos
    def registrar_pago(self):
        """Registra un nuevo pago"""
        print(f"\n{Fore.CYAN}REGISTRAR PAGO")
        print(f"{Fore.CYAN}{'-'*20}")
        
        try:
            prestamo_id = int(input(f"{Fore.YELLOW}ID del préstamo: {Fore.WHITE}"))
            prestamo = self.prestamo_service.obtener_prestamo(prestamo_id)
            
            if not prestamo:
                print(f"{Fore.RED}No se encontró un préstamo con ese ID.")
                input("Presione Enter para continuar...")
                return
            
            if prestamo.estado != "activo":
                print(f"{Fore.RED}No se puede registrar un pago en un préstamo no activo.")
                input("Presione Enter para continuar...")
                return
            
            print(f"\n{Fore.WHITE}Préstamo: ${prestamo.monto:.2f}")
            print(f"{Fore.WHITE}Saldo pendiente: ${prestamo.calcular_saldo_pendiente():.2f}")
            
            monto = Decimal(input(f"{Fore.YELLOW}Monto del pago: {Fore.WHITE}"))
            concepto = input(f"{Fore.YELLOW}Concepto (opcional): {Fore.WHITE}").strip()
            
            if not concepto:
                concepto = "Pago de cuota"
            
            pago = self.pago_service.registrar_pago(prestamo_id, monto, concepto)
            
            print(f"\n{Fore.GREEN}✓ Pago registrado exitosamente!")
            print(f"{Fore.WHITE}ID del pago: {pago.id}")
            print(f"{Fore.WHITE}Nuevo saldo pendiente: ${prestamo.calcular_saldo_pendiente():.2f}")
            
        except ValueError as e:
            print(f"\n{Fore.RED}Error: {e}")
        except InvalidOperation:
            print(f"\n{Fore.RED}Error: Monto inválido.")
        except Exception as e:
            print(f"\n{Fore.RED}Error inesperado: {e}")
        
        input("\nPresione Enter para continuar...")
    
    def ver_historial_pagos(self):
        """Muestra el historial de pagos de un préstamo"""
        print(f"\n{Fore.CYAN}HISTORIAL DE PAGOS")
        print(f"{Fore.CYAN}{'-'*25}")
        
        try:
            prestamo_id = int(input(f"{Fore.YELLOW}ID del préstamo: {Fore.WHITE}"))
            historial = self.pago_service.obtener_historial_pagos(prestamo_id)
            
            if historial:
                print(f"\n{Fore.GREEN}Historial de pagos:")
                headers = ["Fecha", "Monto", "Concepto", "Saldo Restante"]
                tabla = [[
                    pago['fecha'],
                    f"${pago['monto']:.2f}",
                    pago['concepto'],
                    f"${pago['saldo_restante']:.2f}"
                ] for pago in historial]
                
                print(tabulate(tabla, headers=headers, tablefmt="grid"))
            else:
                print(f"\n{Fore.YELLOW}No hay pagos registrados para este préstamo.")
                
        except ValueError:
            print(f"{Fore.RED}ID inválido.")
        except Exception as e:
            print(f"\n{Fore.RED}Error: {e}")
        
        input("\nPresione Enter para continuar...")
    
    # Métodos de reportes
    def reporte_general(self):
        """Muestra el reporte general del sistema"""
        print(f"\n{Fore.CYAN}REPORTE GENERAL DEL SISTEMA")
        print(f"{Fore.CYAN}{'='*35}")
        
        try:
            stats = self.reporte_service.generar_reporte_general()
            
            print(f"\n{Fore.WHITE}Estadísticas Generales:")
            print(f"{Fore.WHITE}• Total de clientes: {stats['total_clientes']}")
            print(f"{Fore.WHITE}• Total de préstamos: {stats['total_prestamos']}")
            print(f"{Fore.WHITE}• Monto total prestado: ${stats['monto_total_prestado']:.2f}")
            print(f"{Fore.WHITE}• Monto total pagado: ${stats['monto_total_pagado']:.2f}")
            print(f"{Fore.WHITE}• Préstamos activos: {stats['prestamos_activos']}")
            print(f"{Fore.WHITE}• Total de pagos: {stats['total_pagos']}")
            
        except Exception as e:
            print(f"\n{Fore.RED}Error: {e}")
        
        input("\nPresione Enter para continuar...")
    
    def reporte_cliente(self):
        """Muestra el reporte de un cliente específico"""
        print(f"\n{Fore.CYAN}REPORTE DE CLIENTE")
        print(f"{Fore.CYAN}{'-'*20}")
        
        try:
            cliente_id = int(input(f"{Fore.YELLOW}ID del cliente: {Fore.WHITE}"))
            reporte = self.reporte_service.generar_reporte_cliente(cliente_id)
            
            print(f"\n{Fore.WHITE}Cliente: {reporte['cliente']}")
            print(f"{Fore.WHITE}Total de préstamos: {reporte['resumen']['total_prestamos']}")
            print(f"{Fore.WHITE}Monto total prestado: ${reporte['resumen']['monto_total_prestado']:.2f}")
            print(f"{Fore.WHITE}Monto total pagado: ${reporte['resumen']['monto_total_pagado']:.2f}")
            print(f"{Fore.WHITE}Saldo total pendiente: ${reporte['resumen']['saldo_total_pendiente']:.2f}")
            
            if reporte['prestamos']:
                print(f"\n{Fore.GREEN}Préstamos del cliente:")
                self._mostrar_tabla_prestamos(reporte['prestamos'])
            
        except ValueError:
            print(f"{Fore.RED}ID inválido.")
        except Exception as e:
            print(f"\n{Fore.RED}Error: {e}")
        
        input("\nPresione Enter para continuar...")
    
    def reporte_prestamos_activos(self):
        """Muestra el reporte de préstamos activos"""
        print(f"\n{Fore.CYAN}REPORTE DE PRÉSTAMOS ACTIVOS")
        print(f"{Fore.CYAN}{'='*35}")
        
        try:
            reporte = self.reporte_service.generar_reporte_prestamos_activos()
            
            if reporte:
                print(f"\n{Fore.GREEN}Préstamos activos:")
                headers = ["ID", "Cliente", "DNI", "Monto", "Tasa %", "Plazo", "Cuota", "Saldo", "Estado"]
                tabla = [[
                    p['id_prestamo'],
                    p['cliente'],
                    p['dni'],
                    f"${p['monto_original']:.2f}",
                    f"{p['tasa_interes']:.1f}%",
                    f"{p['plazo_meses']} meses",
                    f"${p['cuota_mensual']:.2f}",
                    f"${p['saldo_pendiente']:.2f}",
                    p['estado']
                ] for p in reporte]
                
                print(tabulate(tabla, headers=headers, tablefmt="grid"))
            else:
                print(f"\n{Fore.YELLOW}No hay préstamos activos.")
                
        except Exception as e:
            print(f"\n{Fore.RED}Error: {e}")
        
        input("\nPresione Enter para continuar...")
    
    # Métodos auxiliares
    def _mostrar_tabla_clientes(self, clientes):
        """Muestra una tabla de clientes"""
        headers = ["ID", "Nombre", "Apellido", "DNI", "Teléfono", "Email", "Estado"]
        tabla = [[
            c.id,
            c.nombre,
            c.apellido,
            c.dni,
            c.telefono,
            c.email or "-",
            "Activo" if c.activo else "Inactivo"
        ] for c in clientes]
        
        print(tabulate(tabla, headers=headers, tablefmt="grid"))
    
    def _mostrar_tabla_prestamos(self, prestamos):
        """Muestra una tabla de préstamos"""
        headers = ["ID", "Cliente ID", "Monto", "Tasa %", "Plazo", "Tipo", "Estado", "Saldo"]
        tabla = [[
            p.id,
            p.cliente_id,
            f"${p.monto:.2f}",
            f"{p.tasa_interes:.1f}%",
            f"{p.plazo_meses} meses",
            p.tipo_interes.title(),
            p.estado.title(),
            f"${p.calcular_saldo_pendiente():.2f}"
        ] for p in prestamos]
        
        print(tabulate(tabla, headers=headers, tablefmt="grid"))
    
    def ejecutar(self):
        """Ejecuta el sistema principal"""
        while True:
            try:
                self.mostrar_menu_principal()
                opcion = input(f"{Fore.YELLOW}Seleccione una opción: {Fore.WHITE}")
                
                if opcion == "1":
                    self.mostrar_menu_clientes()
                elif opcion == "2":
                    self.mostrar_menu_prestamos()
                elif opcion == "3":
                    self.mostrar_menu_pagos()
                elif opcion == "4":
                    self.mostrar_menu_reportes()
                elif opcion == "5":
                    print(f"\n{Fore.GREEN}¡Gracias por usar el Sistema de Préstamos!")
                    print(f"{Fore.GREEN}¡Hasta luego!")
                    break
                else:
                    print(f"{Fore.RED}Opción inválida. Intente nuevamente.")
                    input("Presione Enter para continuar...")
                    
            except KeyboardInterrupt:
                print(f"\n\n{Fore.YELLOW}Operación cancelada por el usuario.")
                break
            except Exception as e:
                print(f"\n{Fore.RED}Error inesperado: {e}")
                input("Presione Enter para continuar...")

def main():
    """Función principal"""
    try:
        sistema = SistemaPrestamos()
        sistema.ejecutar()
    except Exception as e:
        print(f"{Fore.RED}Error fatal del sistema: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
