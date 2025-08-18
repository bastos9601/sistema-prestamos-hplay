#!/usr/bin/env python3
"""
Ventanas Adicionales para el Sistema de Préstamos
=================================================

Ventanas para gestión de préstamos, pagos y reportes.
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from tkinter.scrolledtext import ScrolledText
from decimal import Decimal, InvalidOperation
from datetime import date

class VentanaPrestamos:
    def __init__(self, parent, prestamo_service, callback_actualizar):
        self.ventana = tk.Toplevel(parent)
        self.ventana.title("Gestión de Préstamos")
        self.ventana.geometry("1000x700")
        self.ventana.configure(bg='#f0f0f0')
        
        self.prestamo_service = prestamo_service
        self.callback_actualizar = callback_actualizar
        
        self.setup_ui()
        self.cargar_prestamos()
    
    def setup_ui(self):
        """Configura la interfaz de la ventana de préstamos"""
        main_frame = ttk.Frame(self.ventana)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Título
        ttk.Label(main_frame, text="💰 GESTIÓN DE PRÉSTAMOS", 
                 style='Title.TLabel').pack(pady=(0, 20))
        
        # Frame de botones
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Button(buttons_frame, text="➕ Nuevo Préstamo", 
                  command=self.nuevo_prestamo).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="🔍 Consultar", 
                  command=self.consultar_prestamo).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="📋 Ver Cliente", 
                  command=self.ver_prestamos_cliente).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="🔄 Actualizar", 
                  command=self.cargar_prestamos).pack(side=tk.LEFT, padx=5)
        
        # Treeview para préstamos
        columns = ('ID', 'Cliente ID', 'Monto', 'Tasa %', 'Plazo', 'Tipo', 'Estado', 'Saldo')
        self.tree = ttk.Treeview(main_frame, columns=columns, show='headings', height=20)
        
        # Configurar columnas
        for col in columns:
            self.tree.heading(col, text=col)
            if col in ['Monto', 'Saldo']:
                self.tree.column(col, width=120)
            elif col == 'Tipo':
                self.tree.column(col, width=80)
            else:
                self.tree.column(col, width=100)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind doble clic para consultar
        self.tree.bind('<Double-1>', self.consultar_prestamo)
    
    def cargar_prestamos(self):
        """Carga la lista de préstamos"""
        try:
            # Limpiar tree
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Cargar préstamos activos
            prestamos = self.prestamo_service.listar_prestamos_activos()
            for prestamo in prestamos:
                self.tree.insert('', 'end', values=(
                    prestamo.id,
                    prestamo.cliente_id,
                    f"${prestamo.monto:,.2f}",
                    f"{prestamo.tasa_interes:.1f}%",
                    f"{prestamo.plazo_meses} meses",
                    prestamo.tipo_interes.title(),
                    prestamo.estado.title(),
                    f"${prestamo.calcular_saldo_pendiente():,.2f}"
                ))
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar préstamos: {e}")
    
    def nuevo_prestamo(self):
        """Abre diálogo para nuevo préstamo"""
        dialog = DialogoPrestamo(self.ventana, self.prestamo_service)
        if dialog.resultado:
            self.cargar_prestamos()
            self.callback_actualizar()
    
    def consultar_prestamo(self):
        """Consulta el préstamo seleccionado"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Seleccione un préstamo para consultar")
            return
        
        item = self.tree.item(selection[0])
        prestamo_id = item['values'][0]
        
        try:
            resumen = self.prestamo_service.obtener_resumen_prestamo(prestamo_id)
            self.mostrar_resumen_prestamo(resumen)
        except Exception as e:
            messagebox.showerror("Error", f"Error al obtener resumen: {e}")
    
    def ver_prestamos_cliente(self):
        """Muestra préstamos de un cliente específico"""
        cliente_id = simpledialog.askinteger("Cliente", "Ingrese el ID del cliente:")
        if cliente_id:
            try:
                prestamos = self.prestamo_service.listar_prestamos_cliente(cliente_id)
                if prestamos:
                    self.mostrar_prestamos_cliente(cliente_id, prestamos)
                else:
                    messagebox.showinfo("Info", "El cliente no tiene préstamos")
            except Exception as e:
                messagebox.showerror("Error", f"Error al obtener préstamos: {e}")
    
    def mostrar_resumen_prestamo(self, resumen):
        """Muestra el resumen de un préstamo"""
        dialog = tk.Toplevel(self.ventana)
        dialog.title("Resumen del Préstamo")
        dialog.geometry("500x400")
        dialog.configure(bg='#f0f0f0')
        dialog.transient(self.ventana)
        dialog.grab_set()
        
        main_frame = ttk.Frame(dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        ttk.Label(main_frame, text="📋 RESUMEN DEL PRÉSTAMO", 
                 style='Title.TLabel').pack(pady=(0, 20))
        
        info_text = f"""
Cliente: {resumen['cliente']}
Monto Original: ${resumen['resumen']['monto_original']:,.2f}
Interés Total: ${resumen['resumen']['interes_total']:,.2f}
Monto Total: ${resumen['resumen']['monto_total']:,.2f}
Cuota Mensual: ${resumen['resumen']['cuota_mensual']:,.2f}
Saldo Pendiente: ${resumen['resumen']['saldo_pendiente']:,.2f}
Pagos Realizados: {resumen['resumen']['pagos_realizados']}
Cuotas Pendientes: {resumen['resumen']['cuotas_pendientes']}
        """
        
        text_widget = ScrolledText(main_frame, height=15, width=60)
        text_widget.pack(fill=tk.BOTH, expand=True)
        text_widget.insert(1.0, info_text)
        text_widget.config(state=tk.DISABLED)
        
        ttk.Button(main_frame, text="Cerrar", 
                  command=dialog.destroy).pack(pady=20)
    
    def mostrar_prestamos_cliente(self, cliente_id, prestamos):
        """Muestra los préstamos de un cliente específico"""
        dialog = tk.Toplevel(self.ventana)
        dialog.title(f"Préstamos del Cliente {cliente_id}")
        dialog.geometry("800x500")
        dialog.configure(bg='#f0f0f0')
        dialog.transient(self.ventana)
        dialog.grab_set()
        
        main_frame = ttk.Frame(dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        ttk.Label(main_frame, text=f"💰 PRÉSTAMOS DEL CLIENTE {cliente_id}", 
                 style='Title.TLabel').pack(pady=(0, 20))
        
        # Treeview para préstamos del cliente
        columns = ('ID', 'Monto', 'Tasa %', 'Plazo', 'Tipo', 'Estado', 'Saldo')
        tree = ttk.Treeview(main_frame, columns=columns, show='headings', height=15)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)
        
        for prestamo in prestamos:
            tree.insert('', 'end', values=(
                prestamo.id,
                f"${prestamo.monto:,.2f}",
                f"{prestamo.tasa_interes:.1f}%",
                f"{prestamo.plazo_meses} meses",
                prestamo.tipo_interes.title(),
                prestamo.estado.title(),
                f"${prestamo.calcular_saldo_pendiente():,.2f}"
            ))
        
        tree.pack(fill=tk.BOTH, expand=True)
        ttk.Button(main_frame, text="Cerrar", 
                  command=dialog.destroy).pack(pady=20)

class VentanaPagos:
    def __init__(self, parent, pago_service, callback_actualizar):
        self.ventana = tk.Toplevel(parent)
        self.ventana.title("Gestión de Pagos")
        self.ventana.geometry("900x600")
        self.ventana.configure(bg='#f0f0f0')
        
        self.pago_service = pago_service
        self.callback_actualizar = callback_actualizar
        
        self.setup_ui()
    
    def setup_ui(self):
        """Configura la interfaz de la ventana de pagos"""
        main_frame = ttk.Frame(self.ventana)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Título
        ttk.Label(main_frame, text="💳 GESTIÓN DE PAGOS", 
                 style='Title.TLabel').pack(pady=(0, 20))
        
        # Frame de botones
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Button(buttons_frame, text="➕ Registrar Pago", 
                  command=self.registrar_pago).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="📋 Ver Historial", 
                  command=self.ver_historial).pack(side=tk.LEFT, padx=5)
        
        # Frame de información
        info_frame = ttk.LabelFrame(main_frame, text="ℹ️ Información", padding=20)
        info_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(info_frame, text="Para registrar un pago, haga clic en 'Registrar Pago'").pack()
        ttk.Label(info_frame, text="Para ver el historial de pagos de un préstamo, haga clic en 'Ver Historial'").pack()
    
    def registrar_pago(self):
        """Abre diálogo para registrar pago"""
        dialog = DialogoPago(self.ventana, self.pago_service)
        if dialog.resultado:
            self.callback_actualizar()
    
    def ver_historial(self):
        """Muestra el historial de pagos de un préstamo"""
        prestamo_id = simpledialog.askinteger("Préstamo", "Ingrese el ID del préstamo:")
        if prestamo_id:
            try:
                historial = self.pago_service.obtener_historial_pagos(prestamo_id)
                if historial:
                    self.mostrar_historial_pagos(prestamo_id, historial)
                else:
                    messagebox.showinfo("Info", "No hay pagos registrados para este préstamo")
            except Exception as e:
                messagebox.showerror("Error", f"Error al obtener historial: {e}")
    
    def mostrar_historial_pagos(self, prestamo_id, historial):
        """Muestra el historial de pagos"""
        dialog = tk.Toplevel(self.ventana)
        dialog.title(f"Historial de Pagos - Préstamo {prestamo_id}")
        dialog.geometry("700x500")
        dialog.configure(bg='#f0f0f0')
        dialog.transient(self.ventana)
        dialog.grab_set()
        
        main_frame = ttk.Frame(dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        ttk.Label(main_frame, text=f"📋 HISTORIAL DE PAGOS - PRÉSTAMO {prestamo_id}", 
                 style='Title.TLabel').pack(pady=(0, 20))
        
        # Treeview para historial
        columns = ('Fecha', 'Monto', 'Concepto', 'Saldo Restante')
        tree = ttk.Treeview(main_frame, columns=columns, show='headings', height=15)
        
        for col in columns:
            tree.heading(col, text=col)
            if col == 'Monto':
                tree.column(col, width=120)
            elif col == 'Saldo Restante':
                tree.column(col, width=140)
            else:
                tree.column(col, width=150)
        
        for pago in historial:
            tree.insert('', 'end', values=(
                pago['fecha'],
                f"${pago['monto']:,.2f}",
                pago['concepto'],
                f"${pago['saldo_restante']:,.2f}"
            ))
        
        tree.pack(fill=tk.BOTH, expand=True)
        ttk.Button(main_frame, text="Cerrar", 
                  command=dialog.destroy).pack(pady=20)

class VentanaReportes:
    def __init__(self, parent, reporte_service):
        self.ventana = tk.Toplevel(parent)
        self.ventana.title("Reportes del Sistema")
        self.ventana.geometry("800x600")
        self.ventana.configure(bg='#f0f0f0')
        
        self.reporte_service = reporte_service
        
        self.setup_ui()
    
    def setup_ui(self):
        """Configura la interfaz de la ventana de reportes"""
        main_frame = ttk.Frame(self.ventana)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Título
        ttk.Label(main_frame, text="📊 REPORTES DEL SISTEMA", 
                 style='Title.TLabel').pack(pady=(0, 20))
        
        # Frame de botones
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Button(buttons_frame, text="📈 Reporte General", 
                  command=self.reporte_general).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="👤 Reporte Cliente", 
                  command=self.reporte_cliente).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="💰 Préstamos Activos", 
                  command=self.reporte_prestamos_activos).pack(side=tk.LEFT, padx=5)
        
        # Frame de reporte
        self.reporte_frame = ttk.LabelFrame(main_frame, text="📋 Reporte", padding=20)
        self.reporte_frame.pack(fill=tk.BOTH, expand=True)
        
        # Área de texto para mostrar reportes
        self.texto_reporte = ScrolledText(self.reporte_frame, height=20, width=80)
        self.texto_reporte.pack(fill=tk.BOTH, expand=True)
        
        # Cargar reporte general por defecto
        self.reporte_general()
    
    def reporte_general(self):
        """Muestra el reporte general del sistema"""
        try:
            stats = self.reporte_service.generar_reporte_general()
            
            reporte_text = f"""
📊 REPORTE GENERAL DEL SISTEMA
{'='*50}

👥 Total de Clientes: {stats['total_clientes']}
💰 Total de Préstamos: {stats['total_prestamos']}
💵 Monto Total Prestado: ${stats['monto_total_prestado']:,.2f}
💳 Monto Total Pagado: ${stats['monto_total_pagado']:,.2f}
📈 Préstamos Activos: {stats['prestamos_activos']}
🔄 Total de Pagos: {stats['total_pagos']}

Última actualización: {date.today().strftime('%d/%m/%Y')}
            """
            
            self.texto_reporte.delete(1.0, tk.END)
            self.texto_reporte.insert(1.0, reporte_text)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar reporte: {e}")
    
    def reporte_cliente(self):
        """Muestra el reporte de un cliente específico"""
        cliente_id = simpledialog.askinteger("Cliente", "Ingrese el ID del cliente:")
        if cliente_id:
            try:
                reporte = self.reporte_service.generar_reporte_cliente(cliente_id)
                
                reporte_text = f"""
👤 REPORTE DEL CLIENTE
{'='*30}

Cliente: {reporte['cliente']}
Total de Préstamos: {reporte['resumen']['total_prestamos']}
Monto Total Prestado: ${reporte['resumen']['monto_total_prestado']:,.2f}
Monto Total Pagado: ${reporte['resumen']['monto_total_pagado']:,.2f}
Saldo Total Pendiente: ${reporte['resumen']['saldo_total_pendiente']:,.2f}

PRÉSTAMOS DEL CLIENTE:
{'-'*30}
                """
                
                for prestamo in reporte['prestamos']:
                    reporte_text += f"""
ID: {prestamo.id}
Monto: ${prestamo.monto:,.2f}
Tasa: {prestamo.tasa_interes:.1f}%
Plazo: {prestamo.plazo_meses} meses
Tipo: {prestamo.tipo_interes.title()}
Estado: {prestamo.estado.title()}
Saldo: ${prestamo.calcular_saldo_pendiente():,.2f}
{'-'*20}
                    """
                
                self.texto_reporte.delete(1.0, tk.END)
                self.texto_reporte.insert(1.0, reporte_text)
                
            except Exception as e:
                messagebox.showerror("Error", f"Error al generar reporte: {e}")
    
    def reporte_prestamos_activos(self):
        """Muestra el reporte de préstamos activos"""
        try:
            reporte = self.reporte_service.generar_reporte_prestamos_activos()
            
            reporte_text = f"""
💰 REPORTE DE PRÉSTAMOS ACTIVOS
{'='*40}

Total de Préstamos Activos: {len(reporte)}

DETALLE DE PRÉSTAMOS:
{'-'*30}
            """
            
            for prestamo in reporte:
                reporte_text += f"""
ID: {prestamo['id_prestamo']}
Cliente: {prestamo['cliente']}
DNI: {prestamo['dni']}
Monto Original: ${prestamo['monto_original']:,.2f}
Tasa de Interés: {prestamo['tasa_interes']:.1f}%
Plazo: {prestamo['plazo_meses']} meses
Cuota Mensual: ${prestamo['cuota_mensual']:,.2f}
Saldo Pendiente: ${prestamo['saldo_pendiente']:,.2f}
Estado: {prestamo['estado']}
{'-'*20}
                """
            
            self.texto_reporte.delete(1.0, tk.END)
            self.texto_reporte.insert(1.0, reporte_text)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar reporte: {e}")

class DialogoPrestamo:
    def __init__(self, parent, prestamo_service):
        self.ventana = tk.Toplevel(parent)
        self.ventana.title("Nuevo Préstamo")
        self.ventana.geometry("500x400")
        self.ventana.configure(bg='#f0f0f0')
        self.ventana.transient(parent)
        self.ventana.grab_set()
        
        self.prestamo_service = prestamo_service
        self.resultado = False
        
        self.setup_ui()
    
    def setup_ui(self):
        """Configura la interfaz del diálogo"""
        main_frame = ttk.Frame(self.ventana)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Título
        ttk.Label(main_frame, text="💰 NUEVO PRÉSTAMO", 
                 style='Title.TLabel').pack(pady=(0, 20))
        
        # Campos
        ttk.Label(main_frame, text="ID del Cliente:").pack(anchor=tk.W)
        self.cliente_id_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.cliente_id_var, width=40).pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(main_frame, text="Monto del Préstamo:").pack(anchor=tk.W)
        self.monto_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.monto_var, width=40).pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(main_frame, text="Tasa de Interés Anual (%):").pack(anchor=tk.W)
        self.tasa_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.tasa_var, width=40).pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(main_frame, text="Plazo en Meses:").pack(anchor=tk.W)
        self.plazo_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.plazo_var, width=40).pack(fill=tk.X, pady=(0, 10))
        
        # Tipo de interés
        ttk.Label(main_frame, text="Tipo de Interés:").pack(anchor=tk.W)
        self.tipo_var = tk.StringVar(value="simple")
        tipo_frame = ttk.Frame(main_frame)
        tipo_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Radiobutton(tipo_frame, text="Simple", variable=self.tipo_var, 
                       value="simple").pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(tipo_frame, text="Compuesto", variable=self.tipo_var, 
                       value="compuesto").pack(side=tk.LEFT, padx=10)
        
        # Botones
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X)
        
        ttk.Button(buttons_frame, text="💾 Crear Préstamo", 
                  command=self.crear_prestamo).pack(side=tk.RIGHT, padx=5)
        ttk.Button(buttons_frame, text="❌ Cancelar", 
                  command=self.ventana.destroy).pack(side=tk.RIGHT, padx=5)
    
    def crear_prestamo(self):
        """Crea el nuevo préstamo"""
        try:
            cliente_id = int(self.cliente_id_var.get().strip())
            monto = Decimal(self.monto_var.get().strip())
            tasa_interes = Decimal(self.tasa_var.get().strip())
            plazo_meses = int(self.plazo_var.get().strip())
            tipo_interes = self.tipo_var.get()
            
            if not all([cliente_id, monto, tasa_interes, plazo_meses]):
                messagebox.showerror("Error", "Todos los campos son obligatorios")
                return
            
            prestamo = self.prestamo_service.crear_prestamo(
                cliente_id, monto, tasa_interes, plazo_meses, tipo_interes
            )
            
            messagebox.showinfo("Éxito", 
                              f"Préstamo creado con ID: {prestamo.id}\n"
                              f"Monto total a pagar: ${prestamo.calcular_monto_total():,.2f}\n"
                              f"Cuota mensual: ${prestamo.calcular_cuota_mensual():,.2f}")
            
            self.resultado = True
            self.ventana.destroy()
            
        except ValueError as e:
            messagebox.showerror("Error", f"Error en los datos: {e}")
        except InvalidOperation:
            messagebox.showerror("Error", "Valores numéricos inválidos")
        except Exception as e:
            messagebox.showerror("Error", f"Error al crear préstamo: {e}")

class DialogoPago:
    def __init__(self, parent, pago_service):
        self.ventana = tk.Toplevel(parent)
        self.ventana.title("Registrar Pago")
        self.ventana.geometry("400x300")
        self.ventana.configure(bg='#f0f0f0')
        self.ventana.transient(parent)
        self.ventana.grab_set()
        
        self.pago_service = pago_service
        self.resultado = False
        
        self.setup_ui()
    
    def setup_ui(self):
        """Configura la interfaz del diálogo"""
        main_frame = ttk.Frame(self.ventana)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Título
        ttk.Label(main_frame, text="💳 REGISTRAR PAGO", 
                 style='Title.TLabel').pack(pady=(0, 20))
        
        # Campos
        ttk.Label(main_frame, text="ID del Préstamo:").pack(anchor=tk.W)
        self.prestamo_id_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.prestamo_id_var, width=40).pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(main_frame, text="Monto del Pago:").pack(anchor=tk.W)
        self.monto_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.monto_var, width=40).pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(main_frame, text="Concepto (opcional):").pack(anchor=tk.W)
        self.concepto_var = tk.StringVar(value="Pago de cuota")
        ttk.Entry(main_frame, textvariable=self.concepto_var, width=40).pack(fill=tk.X, pady=(0, 20))
        
        # Botones
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X)
        
        ttk.Button(buttons_frame, text="💾 Registrar Pago", 
                  command=self.registrar_pago).pack(side=tk.RIGHT, padx=5)
        ttk.Button(buttons_frame, text="❌ Cancelar", 
                  command=self.ventana.destroy).pack(side=tk.RIGHT, padx=5)
    
    def registrar_pago(self):
        """Registra el pago"""
        try:
            prestamo_id = int(self.prestamo_id_var.get().strip())
            monto = Decimal(self.monto_var.get().strip())
            concepto = self.concepto_var.get().strip()
            
            if not all([prestamo_id, monto]):
                messagebox.showerror("Error", "ID del préstamo y monto son obligatorios")
                return
            
            if not concepto:
                concepto = "Pago de cuota"
            
            pago = self.pago_service.registrar_pago(prestamo_id, monto, concepto)
            
            messagebox.showinfo("Éxito", f"Pago registrado con ID: {pago.id}")
            
            self.resultado = True
            self.ventana.destroy()
            
        except ValueError as e:
            messagebox.showerror("Error", f"Error en los datos: {e}")
        except InvalidOperation:
            messagebox.showerror("Error", "Monto inválido")
        except Exception as e:
            messagebox.showerror("Error", f"Error al registrar pago: {e}")
