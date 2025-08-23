#!/usr/bin/env python3
"""
Archivo WSGI para el despliegue en Render
Versión ultra-simple para evitar conflictos
"""

from flask import Flask, jsonify
from datetime import datetime

# Crear aplicación Flask directamente aquí
app = Flask(__name__)
app.config['SECRET_KEY'] = 'clave_secreta_temporal_para_render'

@app.route('/')
def index():
    """Página principal"""
    return jsonify({
        'mensaje': 'Sistema de Préstamos funcionando en Render',
        'estado': 'activo',
        'timestamp': datetime.now().isoformat(),
        'version': 'hello-world-simple'
    })

@app.route('/health')
def health():
    """Ruta de salud para Render"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'Sistema de Préstamos'
    })

@app.route('/test')
def test():
    """Ruta de prueba"""
    return jsonify({
        'status': 'success',
        'message': 'Test funcionando correctamente',
        'timestamp': datetime.now().isoformat()
    })

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
