#!/usr/bin/env python3
"""
Generador de Comprobantes de Pago
=================================

Este módulo genera comprobantes de pago en formato texto y HTML
para ser enviados por WhatsApp.
"""

from datetime import datetime
from decimal import Decimal
from typing import Dict, Any

class ComprobanteGenerator:
    """Genera comprobantes de pago para envío por WhatsApp"""
    
    def __init__(self):
        self.template_html = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Comprobante de Pago</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }
        .comprobante { background: white; padding: 30px; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); max-width: 500px; margin: 0 auto; }
        .header { text-align: center; border-bottom: 3px solid #28a745; padding-bottom: 20px; margin-bottom: 25px; }
        .logo { font-size: 2.5em; margin-bottom: 10px; }
        .titulo { color: #28a745; font-size: 1.8em; font-weight: bold; margin: 0; }
        .subtitulo { color: #666; font-size: 1.1em; margin: 5px 0; }
        .seccion { margin: 20px 0; }
        .seccion h3 { color: #333; border-bottom: 2px solid #eee; padding-bottom: 8px; margin-bottom: 15px; }
        .campo { display: flex; justify-content: space-between; margin: 10px 0; padding: 8px 0; border-bottom: 1px solid #f0f0f0; }
        .campo .etiqueta { font-weight: bold; color: #555; }
        .campo .valor { color: #333; text-align: right; }
        .monto { font-size: 1.2em; font-weight: bold; color: #28a745; }
        .saldo { font-size: 1.1em; font-weight: bold; color: #ffc107; }
        .footer { text-align: center; margin-top: 30px; padding-top: 20px; border-top: 2px solid #eee; color: #666; font-size: 0.9em; }
        .estado { display: inline-block; padding: 5px 15px; border-radius: 20px; font-weight: bold; font-size: 0.9em; }
        .estado.pagado { background-color: #d4edda; color: #155724; }
        .estado.pendiente { background-color: #fff3cd; color: #856404; }
    </style>
</head>
<body>
    <div class="comprobante">
        <div class="header">
            <div class="logo">💰</div>
            <h1 class="titulo">COMPROBANTE DE PAGO</h1>
            <p class="subtitulo">Sistema de Préstamos</p>
        </div>
        
        <div class="seccion">
            <h3>📋 INFORMACIÓN DEL PAGO</h3>
            <div class="campo">
                <span class="etiqueta">Número de Comprobante:</span>
                <span class="valor">#{comprobante_id}</span>
            </div>
            <div class="campo">
                <span class="etiqueta">Fecha y Hora:</span>
                <span class="valor">{fecha_hora}</span>
            </div>
            <div class="campo">
                <span class="etiqueta">Monto Pagado:</span>
                <span class="valor monto">${monto_pagado}</span>
            </div>
            <div class="campo">
                <span class="etiqueta">Concepto:</span>
                <span class="valor">{concepto}</span>
            </div>
        </div>
        
        <div class="seccion">
            <h3>🏦 DETALLES DEL PRÉSTAMO</h3>
            <div class="campo">
                <span class="etiqueta">Número de Préstamo:</span>
                <span class="valor">#{prestamo_id}</span>
            </div>
            <div class="campo">
                <span class="etiqueta">Monto Original:</span>
                <span class="valor">${monto_prestamo}</span>
            </div>
            <div class="campo">
                <span class="etiqueta">Total con Intereses:</span>
                <span class="valor">${total_prestamo}</span>
            </div>
            <div class="campo">
                <span class="etiqueta">Saldo Pendiente:</span>
                <span class="valor saldo">${saldo_pendiente}</span>
            </div>
        </div>
        
        <div class="seccion">
            <h3>👤 DATOS DEL CLIENTE</h3>
            <div class="campo">
                <span class="etiqueta">Nombre:</span>
                <span class="valor">{nombre_cliente}</span>
            </div>
            <div class="campo">
                <span class="etiqueta">DNI:</span>
                <span class="valor">{dni_cliente}</span>
            </div>
            <div class="campo">
                <span class="etiqueta">Teléfono:</span>
                <span class="valor">{telefono_cliente}</span>
            </div>
        </div>
        
        <div class="footer">
            <p>Este comprobante es válido como constancia de pago</p>
            <p>Generado automáticamente por el Sistema de Préstamos</p>
        </div>
    </div>
</body>
</html>
        """
    
    def generar_comprobante(self, pago: Dict[str, Any], prestamo: Dict[str, Any], cliente: Dict[str, Any]) -> str:
        """Genera un comprobante de pago en formato texto para WhatsApp"""
        
        # Formatear fecha y hora
        fecha_pago = datetime.fromisoformat(pago['fecha'])
        fecha_formateada = fecha_pago.strftime("%d/%m/%Y")
        hora_formateada = fecha_pago.strftime("%H:%M")
        
        # Calcular montos
        monto_pagado = float(pago['monto'])
        saldo_pendiente = float(pago.get('saldo_despues', 0))
        
        comprobante = f"""💳 *COMPROBANTE DE PAGO*

📅 *Fecha:* {fecha_formateada}
⏰ *Hora:* {hora_formateada}
🆔 *Comprobante:* #{pago['id']}

💰 *Monto Pagado:* ${monto_pagado:.2f}
📝 *Concepto:* {pago['concepto']}

🏦 *DETALLES DEL PRÉSTAMO*
📋 *Préstamo:* #{prestamo['id']}
💵 *Monto Original:* ${float(prestamo['monto']):.2f}
📊 *Total con Intereses:* ${float(prestamo.get('monto_total', prestamo['monto'])):.2f}
⚖️ *Saldo Pendiente:* ${saldo_pendiente:.2f}

👤 *DATOS DEL CLIENTE*
👨‍💼 *Nombre:* {cliente['nombre']} {cliente['apellido']}
🆔 *DNI:* {cliente['dni']}
📱 *Teléfono:* {cliente['telefono']}

✅ *Estado:* Pago Registrado
📱 *Generado:* Sistema de Préstamos

---
*Este comprobante es válido como constancia de pago*"""
        
        return comprobante
    
    def generar_comprobante_html(self, pago: Dict[str, Any], prestamo: Dict[str, Any], cliente: Dict[str, Any]) -> str:
        """Genera un comprobante de pago en formato HTML"""
        
        # Formatear fecha y hora
        fecha_pago = datetime.fromisoformat(pago['fecha'])
        fecha_hora = fecha_pago.strftime("%d/%m/%Y %H:%M")
        
        # Calcular montos
        monto_pagado = float(pago['monto'])
        saldo_pendiente = float(pago.get('saldo_despues', 0))
        monto_prestamo = float(prestamo['monto'])
        total_prestamo = float(prestamo.get('monto_total', prestamo['monto']))
        
        # Reemplazar variables en el template
        html = self.template_html.format(
            comprobante_id=pago['id'],
            fecha_hora=fecha_hora,
            monto_pagado=f"{monto_pagado:.2f}",
            concepto=pago['concepto'],
            prestamo_id=prestamo['id'],
            monto_prestamo=f"{monto_prestamo:.2f}",
            total_prestamo=f"{total_prestamo:.2f}",
            saldo_pendiente=f"{saldo_pendiente:.2f}",
            nombre_cliente=cliente['nombre'],
            dni_cliente=cliente['dni'],
            telefono_cliente=cliente['telefono']
        )
        
        return html
    
    def guardar_comprobante_archivo(self, pago: Dict[str, Any], prestamo: Dict[str, Any], cliente: Dict[str, Any], 
                                   directorio: str = "comprobantes") -> str:
        """Guarda el comprobante HTML en un archivo"""
        import os
        
        # Crear directorio si no existe
        os.makedirs(directorio, exist_ok=True)
        
        # Generar nombre del archivo
        fecha_pago = datetime.fromisoformat(pago['fecha'])
        nombre_archivo = f"comprobante_pago_{pago['id']}_{fecha_pago.strftime('%Y%m%d_%H%M%S')}.html"
        ruta_archivo = os.path.join(directorio, nombre_archivo)
        
        # Generar y guardar HTML
        html = self.generar_comprobante_html(pago, prestamo, cliente)
        with open(ruta_archivo, 'w', encoding='utf-8') as f:
            f.write(html)
        
        return ruta_archivo
