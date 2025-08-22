#!/usr/bin/env python3
"""
Configuración específica para el entorno de producción en Render
"""

import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class ProductionConfig:
    """Configuración para producción"""
    
    # Configuración básica
    SECRET_KEY = os.getenv('SECRET_KEY')
    DEBUG = False
    TESTING = False
    
    # Configuración de la base de datos
    DATABASE_URL = os.getenv('DATABASE_URL')
    
    # Configuración de sesiones
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Configuración de archivos
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    UPLOAD_FOLDER = 'static/uploads'
    
    # Configuración de logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    # Configuración de email
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'true').lower() == 'true'
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    
    # Configuración de WhatsApp
    WHATSAPP_API_KEY = os.getenv('WHATSAPP_API_KEY')
    WHATSAPP_PHONE_ID = os.getenv('WHATSAPP_PHONE_ID')
    
    # Configuración de seguridad
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600  # 1 hora
    
    # Configuración de caché
    CACHE_TYPE = 'simple'
    CACHE_DEFAULT_TIMEOUT = 300  # 5 minutos
    
    # Configuración de rate limiting
    RATELIMIT_ENABLED = True
    RATELIMIT_STORAGE_URL = 'memory://'
    
    # Configuración de compresión
    COMPRESS_MIMETYPES = [
        'text/html', 'text/css', 'text/xml', 'application/json',
        'application/javascript', 'application/xml+rss', 'text/plain'
    ]
    COMPRESS_LEVEL = 6
    COMPRESS_MIN_SIZE = 500
    
    @classmethod
    def get_all_config(cls):
        """Obtiene toda la configuración como diccionario"""
        return {
            'SECRET_KEY': cls.SECRET_KEY,
            'DEBUG': cls.DEBUG,
            'TESTING': cls.TESTING,
            'DATABASE_URL': cls.DATABASE_URL,
            'SESSION_COOKIE_SECURE': cls.SESSION_COOKIE_SECURE,
            'SESSION_COOKIE_HTTPONLY': cls.SESSION_COOKIE_HTTPONLY,
            'SESSION_COOKIE_SAMESITE': cls.SESSION_COOKIE_SAMESITE,
            'MAX_CONTENT_LENGTH': cls.MAX_CONTENT_LENGTH,
            'UPLOAD_FOLDER': cls.UPLOAD_FOLDER,
            'LOG_LEVEL': cls.LOG_LEVEL,
            'MAIL_SERVER': cls.MAIL_SERVER,
            'MAIL_PORT': cls.MAIL_PORT,
            'MAIL_USE_TLS': cls.MAIL_USE_TLS,
            'MAIL_USERNAME': cls.MAIL_USERNAME,
            'MAIL_PASSWORD': cls.MAIL_PASSWORD,
            'WHATSAPP_API_KEY': cls.WHATSAPP_API_KEY,
            'WHATSAPP_PHONE_ID': cls.WHATSAPP_PHONE_ID,
            'WTF_CSRF_ENABLED': cls.WTF_CSRF_ENABLED,
            'WTF_CSRF_TIME_LIMIT': cls.WTF_CSRF_TIME_LIMIT,
            'CACHE_TYPE': cls.CACHE_TYPE,
            'CACHE_DEFAULT_TIMEOUT': cls.CACHE_DEFAULT_TIMEOUT,
            'RATELIMIT_ENABLED': cls.RATELIMIT_ENABLED,
            'RATELIMIT_STORAGE_URL': cls.RATELIMIT_STORAGE_URL,
            'COMPRESS_MIMETYPES': cls.COMPRESS_MIMETYPES,
            'COMPRESS_LEVEL': cls.COMPRESS_LEVEL,
            'COMPRESS_MIN_SIZE': cls.COMPRESS_MIN_SIZE,
        }

class DevelopmentConfig:
    """Configuración para desarrollo local"""
    
    # Configuración básica
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    DEBUG = True
    TESTING = False
    
    # Configuración de la base de datos
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///data/prestamos.db')
    
    # Configuración de sesiones
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Configuración de archivos
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    UPLOAD_FOLDER = 'static/uploads'
    
    # Configuración de logging
    LOG_LEVEL = 'DEBUG'
    
    # Configuración de email
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'true').lower() == 'true'
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    
    # Configuración de WhatsApp
    WHATSAPP_API_KEY = os.getenv('WHATSAPP_API_KEY')
    WHATSAPP_PHONE_ID = os.getenv('WHATSAPP_PHONE_ID')
    
    # Configuración de seguridad
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600  # 1 hora
    
    # Configuración de caché
    CACHE_TYPE = 'simple'
    CACHE_DEFAULT_TIMEOUT = 300  # 5 minutos
    
    # Configuración de rate limiting
    RATELIMIT_ENABLED = False  # Deshabilitado en desarrollo
    
    # Configuración de compresión
    COMPRESS_MIMETYPES = [
        'text/html', 'text/css', 'text/xml', 'application/json',
        'application/javascript', 'application/xml+rss', 'text/plain'
    ]
    COMPRESS_LEVEL = 6
    COMPRESS_MIN_SIZE = 500

def get_config():
    """Obtiene la configuración según el entorno"""
    env = os.getenv('FLASK_ENV', 'development')
    
    if env == 'production':
        return ProductionConfig
    else:
        return DevelopmentConfig

def validate_production_config():
    """Valida que la configuración de producción esté completa"""
    config = ProductionConfig()
    required_vars = [
        'SECRET_KEY',
        'DATABASE_URL',
        'MAIL_USERNAME',
        'MAIL_PASSWORD'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not getattr(config, var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"⚠️ Variables de entorno faltantes para producción: {', '.join(missing_vars)}")
        return False
    
    print("✅ Configuración de producción válida")
    return True

if __name__ == "__main__":
    # Validar configuración
    env = os.getenv('FLASK_ENV', 'development')
    print(f"🔧 Entorno: {env}")
    
    if env == 'production':
        validate_production_config()
    else:
        print("🔧 Configuración de desarrollo")
    
    # Mostrar configuración actual
    config_class = get_config()
    config = config_class.get_all_config() if hasattr(config_class, 'get_all_config') else {}
    
    print("\n📋 Configuración actual:")
    for key, value in config.items():
        if key.lower().find('password') != -1 or key.lower().find('secret') != -1:
            print(f"  {key}: {'*' * len(str(value)) if value else 'None'}")
        else:
            print(f"  {key}: {value}")
