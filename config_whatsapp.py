#!/usr/bin/env python3
"""
Configuración de WhatsApp Business API
=====================================

Este archivo contiene la configuración necesaria para integrar
WhatsApp Business API con el sistema de préstamos.
"""

import os
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

class WhatsAppConfig:
    """Configuración de WhatsApp Business API"""
    
    # Configuración de la API
    API_URL = os.getenv('WHATSAPP_API_URL', 'https://graph.facebook.com/v17.0')
    PHONE_NUMBER_ID = os.getenv('WHATSAPP_PHONE_NUMBER_ID', '')
    ACCESS_TOKEN = os.getenv('WHATSAPP_ACCESS_TOKEN', '')
    VERIFY_TOKEN = os.getenv('WHATSAPP_VERIFY_TOKEN', '')
    
    # Configuración del webhook
    WEBHOOK_URL = os.getenv('WHATSAPP_WEBHOOK_URL', '')
    
    @classmethod
    def esta_configurado(cls) -> bool:
        """Verifica si WhatsApp está configurado correctamente"""
        return all([
            cls.PHONE_NUMBER_ID,
            cls.ACCESS_TOKEN,
            cls.VERIFY_TOKEN
        ])
    
    @classmethod
    def mostrar_configuracion(cls):
        """Muestra la configuración actual de WhatsApp"""
        print("📱 Configuración de WhatsApp Business API:")
        print("=" * 50)
        
        print(f"🔗 API URL: {cls.API_URL}")
        print(f"📞 Phone Number ID: {cls.PHONE_NUMBER_ID or '❌ No configurado'}")
        print(f"🔑 Access Token: {'✅ Configurado' if cls.ACCESS_TOKEN else '❌ No configurado'}")
        print(f"🔐 Verify Token: {cls.VERIFY_TOKEN or '❌ No configurado'}")
        print(f"🌐 Webhook URL: {cls.WEBHOOK_URL or '❌ No configurado'}")
        
        if cls.esta_configurado():
            print("\n✅ WhatsApp está configurado correctamente")
        else:
            print("\n❌ WhatsApp no está configurado")
            print("\n📋 Para configurar WhatsApp:")
            print("1. Crea un archivo .env en la raíz del proyecto")
            print("2. Agrega las siguientes variables:")
            print("   WHATSAPP_API_URL=https://graph.facebook.com/v17.0")
            print("   WHATSAPP_PHONE_NUMBER_ID=tu_phone_number_id")
            print("   WHATSAPP_ACCESS_TOKEN=tu_access_token")
            print("   WHATSAPP_VERIFY_TOKEN=tu_verify_token")
            print("   WHATSAPP_WEBHOOK_URL=tu_webhook_url")

def crear_archivo_env():
    """Crea un archivo .env de ejemplo"""
    env_content = """# Configuración de WhatsApp Business API
# ================================================

# URL de la API de Facebook (no cambiar)
WHATSAPP_API_URL=https://graph.facebook.com/v17.0

# ID del número de teléfono de WhatsApp Business
# Obtener desde: https://developers.facebook.com/apps/
WHATSAPP_PHONE_NUMBER_ID=123456789012345

# Token de acceso permanente
# Obtener desde: https://developers.facebook.com/apps/
WHATSAPP_ACCESS_TOKEN=tu_access_token_aqui

# Token de verificación del webhook
# Puede ser cualquier string que elijas
WHATSAPP_VERIFY_TOKEN=mi_token_secreto_123

# URL del webhook (opcional, para recibir mensajes)
# Debe ser HTTPS y accesible públicamente
WHATSAPP_WEBHOOK_URL=https://tudominio.com/webhook/whatsapp

# ================================================
# INSTRUCCIONES DE CONFIGURACIÓN:
# ================================================
# 1. Ve a https://developers.facebook.com/
# 2. Crea una nueva aplicación o usa una existente
# 3. Agrega el producto "WhatsApp Business API"
# 4. Configura el número de teléfono de WhatsApp Business
# 5. Obtén el Phone Number ID y Access Token
# 6. Copia estos valores en las variables de arriba
# 7. Reinicia la aplicación
"""
    
    try:
        with open('.env', 'w', encoding='utf-8') as f:
            f.write(env_content)
        print("✅ Archivo .env creado exitosamente")
        print("📝 Edita el archivo .env con tus credenciales de WhatsApp")
        return True
    except Exception as e:
        print(f"❌ Error al crear archivo .env: {e}")
        return False

def verificar_whatsapp():
    """Verifica la configuración de WhatsApp"""
    config = WhatsAppConfig()
    config.mostrar_configuracion()
    
    if not config.esta_configurado():
        print("\n🔧 ¿Quieres crear un archivo .env de ejemplo?")
        respuesta = input("Escribe 'SI' para crear: ")
        
        if respuesta.upper() == 'SI':
            crear_archivo_env()

if __name__ == "__main__":
    verificar_whatsapp()
