import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class DatabaseConfig:
    """Configuración de la base de datos"""
    
    # Configuración para desarrollo local
    DATABASE_URL_LOCAL = "postgresql://localhost/prestamos_db"
    
    # Configuración para Render (PostgreSQL)
    DATABASE_URL_RENDER = os.getenv('DATABASE_URL')
    
    # Configuración para SQLite (fallback)
    SQLITE_DATABASE = "data/prestamos.db"
    
    @classmethod
    def get_database_url(cls):
        """Obtiene la URL de la base de datos según el entorno"""
        if cls.DATABASE_URL_RENDER:
            # Render proporciona DATABASE_URL en formato postgres://
            # Necesitamos convertirla a postgresql:// para psycopg2
            if cls.DATABASE_URL_RENDER.startswith('postgres://'):
                return cls.DATABASE_URL_RENDER.replace('postgres://', 'postgresql://', 1)
            return cls.DATABASE_URL_RENDER
        elif os.getenv('FLASK_ENV') == 'development':
            return cls.DATABASE_URL_LOCAL
        else:
            return cls.SQLITE_DATABASE
    
    @classmethod
    def is_postgresql(cls):
        """Verifica si estamos usando PostgreSQL"""
        return cls.get_database_url().startswith('postgresql://')
    
    @classmethod
    def get_database_config(cls):
        """Obtiene la configuración completa de la base de datos"""
        if cls.is_postgresql():
            return {
                'database_url': cls.get_database_url(),
                'type': 'postgresql',
                'pool_size': 10,
                'max_overflow': 20,
                'pool_timeout': 30,
                'pool_recycle': 1800,
            }
        else:
            return {
                'database_url': cls.SQLITE_DATABASE,
                'type': 'sqlite',
            }

class AppConfig:
    """Configuración general de la aplicación"""
    
    # Configuración básica
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('FLASK_ENV') == 'development'
    
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
    SESSION_COOKIE_SECURE = os.getenv('FLASK_ENV') != 'development'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Configuración de archivos
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = 'static/uploads'
    
    # Configuración de logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    @classmethod
    def get_all_config(cls):
        """Obtiene toda la configuración como diccionario"""
        return {
            'database': DatabaseConfig.get_database_config(),
            'app': {
                'secret_key': cls.SECRET_KEY,
                'debug': cls.DEBUG,
                'mail_server': cls.MAIL_SERVER,
                'mail_port': cls.MAIL_PORT,
                'mail_use_tls': cls.MAIL_USE_TLS,
                'mail_username': cls.MAIL_USERNAME,
                'mail_password': cls.MAIL_PASSWORD,
                'whatsapp_api_key': cls.WHATSAPP_API_KEY,
                'whatsapp_phone_id': cls.WHATSAPP_PHONE_ID,
                'session_cookie_secure': cls.SESSION_COOKIE_SECURE,
                'session_cookie_httponly': cls.SESSION_COOKIE_HTTPONLY,
                'session_cookie_samesite': cls.SESSION_COOKIE_SAMESITE,
                'max_content_length': cls.MAX_CONTENT_LENGTH,
                'upload_folder': cls.UPLOAD_FOLDER,
                'log_level': cls.LOG_LEVEL,
            }
        }

# Configuración para diferentes entornos
class DevelopmentConfig(AppConfig):
    """Configuración para desarrollo"""
    DEBUG = True
    FLASK_ENV = 'development'

class ProductionConfig(AppConfig):
    """Configuración para producción"""
    DEBUG = False
    FLASK_ENV = 'production'

class TestingConfig(AppConfig):
    """Configuración para testing"""
    DEBUG = True
    TESTING = True
    FLASK_ENV = 'testing'

# Mapeo de configuraciones
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def get_config():
    """Obtiene la configuración según el entorno"""
    env = os.getenv('FLASK_ENV', 'default')
    return config.get(env, config['default'])
