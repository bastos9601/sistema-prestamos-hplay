#!/usr/bin/env python3
"""
Configuración para el sistema de emails de recuperación de contraseña
"""

# Configuración SMTP para Gmail
SMTP_CONFIG = {
    'server': 'smtp.gmail.com',
    'port': 587,
    'username': 'bastosbarbaranvictor@gmail.com',  # Cambiar por tu email de Gmail
    'password': 'ldkhglaolpcofqbs'      # Cambiar por tu contraseña de aplicación
}

# Configuración del sistema
SYSTEM_CONFIG = {
    'nombre_sistema': 'Sistema de Préstamos',
    'url_base': 'http://localhost:5000',  # Cambiar en producción
    'tiempo_expiracion_codigo': 10  # Minutos
}

# Instrucciones para configurar Gmail:
"""
1. Activar la verificación en dos pasos en tu cuenta de Gmail
2. Generar una contraseña de aplicación:
   - Ve a Configuración de Google
   - Seguridad
   - Verificación en dos pasos
   - Contraseñas de aplicación
   - Genera una nueva contraseña para "Correo"
3. Usa esa contraseña en lugar de tu contraseña normal
4. Cambia 'tu_email@gmail.com' por tu email real
5. Cambia 'tu_password_app' por la contraseña de aplicación generada
"""

if __name__ == "__main__":
    print("📧 Configuración de Email para Recuperación de Contraseña")
    print("=" * 60)
    print("Para usar esta funcionalidad, debes:")
    print("1. Configurar tu cuenta de Gmail con verificación en 2 pasos")
    print("2. Generar una contraseña de aplicación")
    print("3. Actualizar este archivo con tus credenciales")
    print("4. Reiniciar la aplicación")
    print("=" * 60)
