#!/usr/bin/env python3
"""
Sistema de Envío de WhatsApp Directo
====================================

Este módulo permite enviar mensajes por WhatsApp usando enlaces directos
sin necesidad de API de WhatsApp Business.
"""

import urllib.parse
import webbrowser
import os

class WhatsAppSender:
    """Maneja el envío de mensajes por WhatsApp usando enlaces directos"""
    
    def __init__(self):
        print("📱 WhatsApp Sender configurado para envío directo")
    
    def enviar_mensaje(self, telefono: str, mensaje: str) -> bool:
        """Envía un mensaje por WhatsApp usando enlace directo"""
        try:
            # Formatear número de teléfono
            telefono_formateado = self._formatear_telefono(telefono)
            
            # Codificar el mensaje para la URL
            mensaje_codificado = urllib.parse.quote(mensaje)
            
            # Crear enlace de WhatsApp
            url_whatsapp = f"https://wa.me/{telefono_formateado}?text={mensaje_codificado}"
            
            # Abrir en navegador
            webbrowser.open(url_whatsapp)
            
            print(f"✅ Enlace de WhatsApp abierto para {telefono}")
            print(f"📱 Número: {telefono_formateado}")
            print(f"🔗 URL: {url_whatsapp}")
            
            return True
                
        except Exception as e:
            print(f"❌ Error al abrir WhatsApp: {e}")
            return False
    
    def enviar_pagare_whatsapp(self, telefono: str, pagare_texto: str) -> bool:
        """Envía un pagaré por WhatsApp usando enlace directo"""
        try:
            # Formatear número de teléfono
            telefono_formateado = self._formatear_telefono(telefono)
            
            # Preparar mensaje del pagaré
            mensaje_pagare = f"📋 *PAGARÉ GENERADO*\n\n{pagare_texto}"
            
            # Codificar el mensaje para la URL
            mensaje_codificado = urllib.parse.quote(mensaje_pagare)
            
            # Crear enlace de WhatsApp
            url_whatsapp = f"https://wa.me/{telefono_formateado}?text={mensaje_codificado}"
            
            # Abrir en navegador
            webbrowser.open(url_whatsapp)
            
            print(f"✅ Pagaré enviado por WhatsApp a {telefono}")
            print(f"📱 Número: {telefono_formateado}")
            print(f"🔗 URL: {url_whatsapp}")
            
            return True
                
        except Exception as e:
            print(f"❌ Error al enviar pagaré por WhatsApp: {e}")
            return False
    
    def _formatear_telefono(self, telefono: str) -> str:
        """Formatea el número de teléfono para WhatsApp (Perú)"""
        # Remover caracteres especiales
        telefono = telefono.replace("+", "").replace("-", "").replace(" ", "").replace("(", "").replace(")", "")
        
        # Si el número ya tiene código de país, no hacer nada
        if telefono.startswith("51") or telefono.startswith("54") or telefono.startswith("1") or telefono.startswith("33"):
            return telefono
        
        # Para números peruanos, agregar código +51 si no está
        if len(telefono) == 9:  # Número peruano típico (9 dígitos)
            telefono = "51" + telefono
        elif len(telefono) == 8:  # Número peruano sin código de área
            telefono = "51" + telefono
        elif len(telefono) == 10:  # Número con código de área (ej: 01, 02, etc.)
            telefono = "51" + telefono
        
        return telefono
    
    def generar_enlace_whatsapp(self, telefono: str, mensaje: str = "") -> str:
        """Genera un enlace de WhatsApp para usar manualmente"""
        telefono_formateado = self._formatear_telefono(telefono)
        
        if mensaje:
            mensaje_codificado = urllib.parse.quote(mensaje)
            return f"https://wa.me/{telefono_formateado}?text={mensaje_codificado}"
        else:
            return f"https://wa.me/{telefono_formateado}"
    
    def abrir_chat_whatsapp(self, telefono: str) -> bool:
        """Abre solo el chat de WhatsApp sin mensaje predefinido"""
        try:
            telefono_formateado = self._formatear_telefono(telefono)
            url_whatsapp = f"https://wa.me/{telefono_formateado}"
            
            webbrowser.open(url_whatsapp)
            print(f"✅ Chat de WhatsApp abierto para {telefono}")
            return True
            
        except Exception as e:
            print(f"❌ Error al abrir chat de WhatsApp: {e}")
            return False
