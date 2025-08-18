# Configuración de Gunicorn para producción
import os

# Configuración del servidor
bind = "0.0.0.0:10000"
workers = 2
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
timeout = 30
keepalive = 2

# Configuración de logging
accesslog = "-"
errorlog = "-"
loglevel = "info"

# Configuración de seguridad
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# Configuración de procesos
preload_app = True
daemon = False
pidfile = "/tmp/gunicorn.pid"
user = None
group = None
tmp_upload_dir = None

# Configuración de SSL (si es necesario)
# keyfile = None
# certfile = None

# Configuración de hooks
def on_starting(server):
    server.log.info("Iniciando Sistema de Préstamos...")

def on_reload(server):
    server.log.info("Recargando Sistema de Préstamos...")

def on_exit(server):
    server.log.info("Cerrando Sistema de Préstamos...")
