#!/usr/bin/env python3
"""
Generador de Pagarés Automático
===============================

Este módulo genera pagarés automáticamente cuando se crea un préstamo
y los envía por WhatsApp al cliente.
"""

import json
import os
from datetime import datetime, timedelta
from models import Cliente, Prestamo
from whatsapp_sender import WhatsAppSender

class PagareGenerator:
    """Genera pagarés automáticamente para préstamos"""
    
    def __init__(self):
        self.whatsapp = WhatsAppSender()
    
    def generar_pagare(self, cliente: Cliente, prestamo: Prestamo) -> str:
        """Genera el contenido del pagaré"""
        
        # Calcular fechas importantes
        fecha_actual = datetime.now()
        fecha_vencimiento = fecha_actual + timedelta(days=prestamo.plazo_dias)
        
        # Formatear fechas
        fecha_actual_str = fecha_actual.strftime("%d/%m/%Y")
        fecha_vencimiento_str = fecha_vencimiento.strftime("%d/%m/%Y")
        
        # Calcular valores del préstamo
        monto_prestamo = float(prestamo.monto)
        total_intereses = float(prestamo.calcular_interes_total())
        total_a_pagar = float(prestamo.calcular_monto_total())
        cuota_diaria = float(prestamo.calcular_cuota_diaria())
        
        pagare = f"""
🏦 **PAGARÉ DE PRÉSTAMO PERSONAL**

📅 **Fecha de Emisión:** {fecha_actual_str}
⏰ **Fecha de Vencimiento:** {fecha_vencimiento_str}
🆔 **Número de Préstamo:** #{prestamo.id:06d}

👤 **DATOS DEL CLIENTE:**
   Nombre: {cliente.nombre} {cliente.apellido}
   DNI: {cliente.dni}
   Teléfono: {cliente.telefono}
   Email: {cliente.email}

💰 **DETALLES DEL PRÉSTAMO:**
   Monto Solicitado: ${monto_prestamo:,.2f}
   Plazo: {prestamo.plazo_dias} días
   Tasa de Interés: {float(prestamo.tasa_interes)}% anual
   Tipo de Interés: {prestamo.tipo_interes}
   Cuota Diaria: ${cuota_diaria:,.2f}
   Total de Intereses: ${total_intereses:,.2f}
   Total a Pagar: ${total_a_pagar:,.2f}

📋 **CONDICIONES:**
   • El cliente se compromete a pagar la cuota diaria de ${cuota_diaria:,.2f}
   • El préstamo se pagará en {prestamo.plazo_dias} días
   • En caso de mora, se aplicarán intereses adicionales
   • El préstamo debe ser cancelado en su totalidad al vencimiento
   • Cualquier consulta contactar al prestamista

✍️ **FIRMA DEL CLIENTE:**
   _________________
   {cliente.nombre} {cliente.apellido}
   DNI: {cliente.dni}

📱 **Contacto:** {cliente.telefono}
🏢 **Prestamista:** Sistema de Préstamos
        """
        
        return pagare.strip()
    
    def generar_pagare_html(self, cliente: Cliente, prestamo: Prestamo) -> str:
        """Genera el pagaré en formato HTML para mejor presentación"""
        
        fecha_actual = datetime.now()
        fecha_vencimiento = fecha_actual + timedelta(days=prestamo.plazo_dias)
        
        fecha_actual_str = fecha_actual.strftime("%d/%m/%Y")
        fecha_vencimiento_str = fecha_vencimiento.strftime("%d/%m/%Y")
        
        # Calcular valores del préstamo
        monto_prestamo = float(prestamo.monto)
        total_intereses = float(prestamo.calcular_interes_total())
        total_a_pagar = float(prestamo.calcular_monto_total())
        cuota_diaria = float(prestamo.calcular_cuota_diaria())
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Pagaré #{prestamo.id:06d}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ text-align: center; border-bottom: 2px solid #333; padding-bottom: 10px; margin-bottom: 20px; }}
        .section {{ margin: 15px 0; }}
        .section-title {{ font-weight: bold; color: #2c3e50; margin-bottom: 10px; }}
        .data-row {{ margin: 5px 0; }}
        .amount {{ font-size: 18px; font-weight: bold; color: #e74c3c; }}
        .signature {{ margin-top: 30px; text-align: center; }}
        .signature-line {{ border-top: 1px solid #333; width: 200px; margin: 10px auto; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🏦 PAGARÉ DE PRÉSTAMO PERSONAL</h1>
        <p><strong>Fecha:</strong> {fecha_actual_str} | <strong>Vencimiento:</strong> {fecha_vencimiento_str}</p>
        <p><strong>Número:</strong> #{prestamo.id:06d}</p>
    </div>
    
    <div class="section">
        <div class="section-title">👤 DATOS DEL CLIENTE:</div>
        <div class="data-row"><strong>Nombre:</strong> {cliente.nombre} {cliente.apellido}</div>
        <div class="data-row"><strong>DNI:</strong> {cliente.dni}</div>
        <div class="data-row"><strong>Teléfono:</strong> {cliente.telefono}</div>
        <div class="data-row"><strong>Email:</strong> {cliente.email}</div>
    </div>
    
    <div class="section">
        <div class="section-title">💰 DETALLES DEL PRÉSTAMO:</div>
        <div class="data-row"><strong>Monto Solicitado:</strong> <span class="amount">${monto_prestamo:,.2f}</span></div>
        <div class="data-row"><strong>Plazo:</strong> {prestamo.plazo_dias} días</div>
        <div class="data-row"><strong>Tasa de Interés:</strong> {float(prestamo.tasa_interes)}% anual</div>
        <div class="data-row"><strong>Tipo de Interés:</strong> {prestamo.tipo_interes}</div>
        <div class="data-row"><strong>Cuota Diaria:</strong> <span class="amount">${cuota_diaria:,.2f}</span></div>
        <div class="data-row"><strong>Total de Intereses:</strong> <span class="amount">${total_intereses:,.2f}</span></div>
        <div class="data-row"><strong>Total a Pagar:</strong> <span class="amount">${total_a_pagar:,.2f}</span></div>
    </div>
    
    <div class="section">
        <div class="section-title">📋 CONDICIONES:</div>
        <div class="data-row">• El cliente se compromete a pagar la cuota diaria de ${cuota_diaria:,.2f}</div>
        <div class="data-row">• El préstamo se pagará en {prestamo.plazo_dias} días</div>
        <div class="data-row">• En caso de mora, se aplicarán intereses adicionales</div>
        <div class="data-row">• El préstamo debe ser cancelado en su totalidad al vencimiento</div>
        <div class="data-row">• Cualquier consulta contactar al prestamista</div>
    </div>
    
    <div class="signature">
        <div class="signature-line"></div>
        <p><strong>{cliente.nombre} {cliente.apellido}</strong></p>
        <p>DNI: {cliente.dni}</p>
    </div>
    
    <div class="section" style="margin-top: 40px;">
        <div class="data-row"><strong>📱 Contacto:</strong> {cliente.telefono}</div>
        <div class="data-row"><strong>🏢 Prestamista:</strong> Sistema de Préstamos</div>
    </div>
</body>
</html>
        """
        
        return html
    
    def enviar_pagare_whatsapp(self, cliente: Cliente, prestamo: Prestamo) -> bool:
        """Envía el pagaré por WhatsApp al cliente"""
        try:
            # Generar el pagaré
            pagare_texto = self.generar_pagare(cliente, prestamo)
            
            # Usar el WhatsAppSender corregido para formatear el número
            mensaje = f"📋 *PAGARÉ GENERADO*\n\n{pagare_texto}"
            
            # Enviar mensaje usando el WhatsAppSender que ya formatea correctamente para Perú
            resultado = self.whatsapp.enviar_mensaje(cliente.telefono, mensaje)
            
            if resultado:
                print(f"✅ Pagaré enviado por WhatsApp a {cliente.nombre} {cliente.apellido}")
                return True
            else:
                print(f"❌ Error al enviar pagaré por WhatsApp a {cliente.nombre} {cliente.apellido}")
                return False
                
        except Exception as e:
            print(f"❌ Error al generar/enviar pagaré: {e}")
            return False
    
    def guardar_pagare_archivo(self, cliente: Cliente, prestamo: Prestamo, directorio: str = "pagarés") -> str:
        """Guarda el pagaré como archivo HTML"""
        try:
            # Crear directorio si no existe
            if not os.path.exists(directorio):
                os.makedirs(directorio)
            
            # Generar nombre del archivo
            fecha = datetime.now().strftime("%Y%m%d_%H%M%S")
            nombre_archivo = f"pagare_{prestamo.id:06d}_{cliente.dni}_{fecha}.html"
            ruta_archivo = os.path.join(directorio, nombre_archivo)
            
            # Generar HTML y guardar
            html_content = self.generar_pagare_html(cliente, prestamo)
            
            with open(ruta_archivo, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            print(f"✅ Pagaré guardado en: {ruta_archivo}")
            return ruta_archivo
            
        except Exception as e:
            print(f"❌ Error al guardar pagaré: {e}")
            return None
