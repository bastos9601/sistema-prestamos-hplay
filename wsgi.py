#!/usr/bin/env python3
"""
Archivo WSGI para producción
"""

import os
import sys

# Agregar el directorio del proyecto al path
sys.path.insert(0, os.path.dirname(__file__))

# Importar la aplicación Flask
from app import app

if __name__ == "__main__":
    app.run()
