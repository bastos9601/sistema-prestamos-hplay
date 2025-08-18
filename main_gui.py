#!/usr/bin/env python3
"""
Sistema de Préstamos de Dinero - Interfaz Gráfica
=================================================

Una interfaz moderna y fácil de usar para gestionar préstamos de dinero.
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from tkinter.scrolledtext import ScrolledText
import os
from decimal import Decimal, InvalidOperation
from datetime import date

# Importar módulos del sistema
from database import Database
from services import ClienteService, PrestamoService, PagoService, ReporteService

class SistemaPrestamosGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Sistema de Préstamos de Dinero")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f0f0f0')
        
        # Inicializar servicios
        self.db = Database()
        self.cliente_service = ClienteService(self.db)
        self.prestamo_service = PrestamoService(self.db)
        self.pago_service = PagoService(self.db)
        self.reporte_service = ReporteService(self.db)
        
        self.setup_ui()
        
    def setup_ui(self):
        """Configura la interfaz de usuario principal"""
        # Frame principal
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Título principal
        title_label = ttk.Label(
            main_frame, 
            text="🏦 SISTEMA DE PRÉSTAMOS DE DINERO", 
            font=('Arial', 20, 'bold')
        )
        title_label.pack(pady=(0, 30))
        
        # Frame de botones principales
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X, pady=20)
        
        # Botones principales
        ttk.Button(
            buttons_frame, 
            text="👥 Gestión de Clientes", 
            command=self.mostrar_ventana_clientes,
            style='Accent.TButton'
        ).pack(side=tk.LEFT, padx=10, expand=True, fill=tk.X)
        
        ttk.Button(
            buttons_frame, 
            text="💰 Gestión de Préstamos", 
            command=self.mostrar_ventana_prestamos,
            style='Accent.TButton'
        ).pack(side=tk.LEFT, padx=10, expand=True, fill=tk.X)
        
        ttk.Button(
            buttons_frame, 
            text="💳 Gestión de Pagos", 
            command=self.mostrar_ventana_pagos,
            style='Accent.TButton'
        ).pack(side=tk.LEFT, padx=10, expand=True, fill=tk.X)
        
        ttk.Button(
            buttons_frame, 
            text="📊 Reportes", 
            command=self.mostrar_ventana_reportes,
            style='Accent.TButton'
        ).pack(side=tk.LEFT, padx=10, expand=True, fill=tk.X)
        
        # Frame de estadísticas rápidas
        stats_frame = ttk.LabelFrame(main_frame, text="📈 Estadísticas Rápidas", padding=20)
        stats_frame.pack(fill=tk.X, pady=20)
        
        # Botón para actualizar estadísticas
        ttk.Button(
            stats_frame, 
            text="🔄 Actualizar Estadísticas", 
            command=self.actualizar_estadisticas
        ).pack(pady=(0, 10))
        
        # Frame para mostrar estadísticas
        self.stats_display = ScrolledText(stats_frame, height=8, width=80)
        self.stats_display.pack(fill=tk.X)
        
        # Cargar estadísticas iniciales
        self.actualizar_estadisticas()
        
        # Configurar estilos
        self.configurar_estilos()
        
    def configurar_estilos(self):
        """Configura los estilos de la interfaz"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configurar colores
        style.configure('Accent.TButton', 
                       background='#007acc', 
                       foreground='white',
                       font=('Arial', 10, 'bold'))
        
        style.configure('Title.TLabel', 
                       font=('Arial', 16, 'bold'),
                       foreground='#333333')
        
    def actualizar_estadisticas(self):
        """Actualiza las estadísticas mostradas"""
        try:
            stats = self.reporte_service.generar_reporte_general()
            
            stats_text = f"""
📊 ESTADÍSTICAS DEL SISTEMA
{'='*50}

👥 Total de Clientes: {stats['total_clientes']}
💰 Total de Préstamos: {stats['total_prestamos']}
💵 Monto Total Prestado: ${stats['monto_total_prestado']:,.2f}
💳 Monto Total Pagado: ${stats['monto_total_pagado']:,.2f}
📈 Préstamos Activos: {stats['prestamos_activos']}
🔄 Total de Pagos: {stats['total_pagos']}

Última actualización: {date.today().strftime('%d/%m/%Y')}
            """
            
            self.stats_display.delete(1.0, tk.END)
            self.stats_display.insert(1.0, stats_text)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar estadísticas: {e}")
    
    def mostrar_ventana_clientes(self):
        """Muestra la ventana de gestión de clientes"""
        VentanaClientes(self.root, self.cliente_service, self.actualizar_estadisticas)
    
    def mostrar_ventana_prestamos(self):
        """Muestra la ventana de gestión de préstamos"""
        from ventanas_adicionales import VentanaPrestamos
        VentanaPrestamos(self.root, self.prestamo_service, self.actualizar_estadisticas)
    
    def mostrar_ventana_pagos(self):
        """Muestra la ventana de gestión de pagos"""
        from ventanas_adicionales import VentanaPagos
        VentanaPagos(self.root, self.pago_service, self.actualizar_estadisticas)
    
    def mostrar_ventana_reportes(self):
        """Muestra la ventana de reportes"""
        from ventanas_adicionales import VentanaReportes
        VentanaReportes(self.root, self.reporte_service)
    
    def ejecutar(self):
        """Ejecuta la aplicación"""
        self.root.mainloop()

class VentanaClientes:
    def __init__(self, parent, cliente_service, callback_actualizar):
        self.ventana = tk.Toplevel(parent)
        self.ventana.title("Gestión de Clientes")
        self.ventana.geometry("800x600")
        self.ventana.configure(bg='#f0f0f0')
        
        self.cliente_service = cliente_service
        self.callback_actualizar = callback_actualizar
        
        self.setup_ui()
        self.cargar_clientes()
    
    def setup_ui(self):
        """Configura la interfaz de la ventana de clientes"""
        # Frame principal
        main_frame = ttk.Frame(self.ventana)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Título
        ttk.Label(main_frame, text="👥 GESTIÓN DE CLIENTES", 
                 style='Title.TLabel').pack(pady=(0, 20))
        
        # Frame de botones
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Button(buttons_frame, text="➕ Nuevo Cliente", 
                  command=self.nuevo_cliente).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="🔍 Buscar", 
                  command=self.buscar_cliente).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="✏️ Editar", 
                  command=self.editar_cliente).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="🗑️ Eliminar", 
                  command=self.eliminar_cliente).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="🔄 Actualizar", 
                  command=self.cargar_clientes).pack(side=tk.LEFT, padx=5)
        
        # Frame de búsqueda
        search_frame = ttk.Frame(main_frame)
        search_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(search_frame, text="Buscar:").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        self.search_entry.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
        self.search_var.trace('w', self.filtrar_clientes)
        
        # Treeview para clientes
        columns = ('ID', 'Nombre', 'Apellido', 'DNI', 'Teléfono', 'Email', 'Estado')
        self.tree = ttk.Treeview(main_frame, columns=columns, show='headings', height=15)
        
        # Configurar columnas
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind doble clic para editar
        self.tree.bind('<Double-1>', self.editar_cliente)
    
    def cargar_clientes(self):
        """Carga la lista de clientes"""
        try:
            # Limpiar tree
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Cargar clientes
            clientes = self.cliente_service.listar_clientes()
            for cliente in clientes:
                self.tree.insert('', 'end', values=(
                    cliente.id,
                    cliente.nombre,
                    cliente.apellido,
                    cliente.dni,
                    cliente.telefono,
                    cliente.email or "-",
                    "Activo" if cliente.activo else "Inactivo"
                ))
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar clientes: {e}")
    
    def filtrar_clientes(self, *args):
        """Filtra clientes según el término de búsqueda"""
        termino = self.search_var.get().strip()
        if not termino:
            self.cargar_clientes()
            return
        
        try:
            # Limpiar tree
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Buscar clientes
            clientes = self.cliente_service.buscar_cliente(termino)
            for cliente in clientes:
                self.tree.insert('', 'end', values=(
                    cliente.id,
                    cliente.nombre,
                    cliente.apellido,
                    cliente.dni,
                    cliente.telefono,
                    cliente.email or "-",
                    "Activo" if cliente.activo else "Inactivo"
                ))
                
        except Exception as e:
            messagebox.showerror("Error", f"Error en la búsqueda: {e}")
    
    def nuevo_cliente(self):
        """Abre diálogo para nuevo cliente"""
        dialog = DialogoCliente(self.ventana, self.cliente_service)
        if dialog.resultado:
            self.cargar_clientes()
            self.callback_actualizar()
    
    def editar_cliente(self):
        """Edita el cliente seleccionado"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Seleccione un cliente para editar")
            return
        
        item = self.tree.item(selection[0])
        cliente_id = item['values'][0]
        
        try:
            cliente = self.cliente_service.obtener_cliente(cliente_id)
            if cliente:
                dialog = DialogoCliente(self.ventana, self.cliente_service, cliente)
                if dialog.resultado:
                    self.cargar_clientes()
                    self.callback_actualizar()
            else:
                messagebox.showerror("Error", "Cliente no encontrado")
        except Exception as e:
            messagebox.showerror("Error", f"Error al obtener cliente: {e}")
    
    def eliminar_cliente(self):
        """Elimina el cliente seleccionado"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Seleccione un cliente para eliminar")
            return
        
        item = self.tree.item(selection[0])
        cliente_id = item['values'][0]
        nombre = item['values'][1]
        
        if messagebox.askyesno("Confirmar", f"¿Está seguro de eliminar al cliente {nombre}?"):
            try:
                if self.cliente_service.eliminar_cliente(cliente_id):
                    messagebox.showinfo("Éxito", "Cliente eliminado correctamente")
                    self.cargar_clientes()
                    self.callback_actualizar()
                else:
                    messagebox.showerror("Error", "No se pudo eliminar el cliente")
            except Exception as e:
                messagebox.showerror("Error", f"Error al eliminar cliente: {e}")

class DialogoCliente:
    def __init__(self, parent, cliente_service, cliente=None):
        self.ventana = tk.Toplevel(parent)
        self.ventana.title("Nuevo Cliente" if not cliente else "Editar Cliente")
        self.ventana.geometry("400x300")
        self.ventana.configure(bg='#f0f0f0')
        self.ventana.transient(parent)
        self.ventana.grab_set()
        
        self.cliente_service = cliente_service
        self.cliente = cliente
        self.resultado = False
        
        self.setup_ui()
        if cliente:
            self.cargar_datos()
    
    def setup_ui(self):
        """Configura la interfaz del diálogo"""
        main_frame = ttk.Frame(self.ventana)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Título
        title = "➕ NUEVO CLIENTE" if not self.cliente else "✏️ EDITAR CLIENTE"
        ttk.Label(main_frame, text=title, style='Title.TLabel').pack(pady=(0, 20))
        
        # Campos
        ttk.Label(main_frame, text="Nombre:").pack(anchor=tk.W)
        self.nombre_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.nombre_var, width=40).pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(main_frame, text="Apellido:").pack(anchor=tk.W)
        self.apellido_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.apellido_var, width=40).pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(main_frame, text="DNI:").pack(anchor=tk.W)
        self.dni_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.dni_var, width=40).pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(main_frame, text="Teléfono:").pack(anchor=tk.W)
        self.telefono_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.telefono_var, width=40).pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(main_frame, text="Email (opcional):").pack(anchor=tk.W)
        self.email_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.email_var, width=40).pack(fill=tk.X, pady=(0, 20))
        
        # Botones
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X)
        
        ttk.Button(buttons_frame, text="💾 Guardar", 
                  command=self.guardar).pack(side=tk.RIGHT, padx=5)
        ttk.Button(buttons_frame, text="❌ Cancelar", 
                  command=self.ventana.destroy).pack(side=tk.RIGHT, padx=5)
    
    def cargar_datos(self):
        """Carga los datos del cliente para editar"""
        self.nombre_var.set(self.cliente.nombre)
        self.apellido_var.set(self.cliente.apellido)
        self.dni_var.set(self.cliente.dni)
        self.telefono_var.set(self.cliente.telefono)
        self.email_var.set(self.cliente.email or "")
    
    def guardar(self):
        """Guarda el cliente"""
        try:
            nombre = self.nombre_var.get().strip()
            apellido = self.apellido_var.get().strip()
            dni = self.dni_var.get().strip()
            telefono = self.telefono_var.get().strip()
            email = self.email_var.get().strip()
            
            if not all([nombre, apellido, dni, telefono]):
                messagebox.showerror("Error", "Los campos nombre, apellido, DNI y teléfono son obligatorios")
                return
            
            if self.cliente:
                # Actualizar cliente existente
                if self.cliente_service.actualizar_cliente(
                    self.cliente.id, 
                    nombre=nombre, 
                    apellido=apellido, 
                    telefono=telefono, 
                    email=email
                ):
                    messagebox.showinfo("Éxito", "Cliente actualizado correctamente")
                    self.resultado = True
                    self.ventana.destroy()
                else:
                    messagebox.showerror("Error", "No se pudo actualizar el cliente")
            else:
                # Crear nuevo cliente
                nuevo_cliente = self.cliente_service.crear_cliente(
                    nombre, apellido, dni, telefono, email
                )
                messagebox.showinfo("Éxito", f"Cliente creado con ID: {nuevo_cliente.id}")
                self.resultado = True
                self.ventana.destroy()
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar cliente: {e}")

def main():
    """Función principal"""
    try:
        app = SistemaPrestamosGUI()
        app.ejecutar()
    except Exception as e:
        messagebox.showerror("Error Fatal", f"Error fatal del sistema: {e}")

if __name__ == "__main__":
    main()
