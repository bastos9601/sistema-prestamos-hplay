#!/usr/bin/env python3
"""
Archivo WSGI para el despliegue en Render
Sistema de Préstamos Completo - Versión Render
"""

import os
from app_render import app

if __name__ == "__main__":
    # Configuración para producción
    port = int(os.environ.get("PORT", 5000))
    
    # Configurar para producción
    app.config['FLASK_ENV'] = 'production'
    app.config['DEBUG'] = False
    
    # Ejecutar la aplicación
    app.run(host='0.0.0.0', port=port)
