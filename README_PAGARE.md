# 🏦 Sistema de Pagaré Automático con WhatsApp

## 📋 Descripción

Este sistema genera automáticamente pagarés cuando se crea un préstamo y los envía por WhatsApp al cliente. Los pagarés incluyen todos los detalles del préstamo y se guardan como archivos HTML para fácil visualización.

## ✨ Características

- **Generación Automática**: Los pagarés se crean automáticamente al crear un préstamo
- **Envío por WhatsApp**: Integración con WhatsApp Business API
- **Formato Profesional**: Pagarés en formato HTML con diseño atractivo
- **Almacenamiento Local**: Los pagarés se guardan como archivos HTML
- **Multi-usuario**: Compatible con el sistema multi-usuario existente

## 🚀 Instalación

### 1. Dependencias

```bash
pip install python-dotenv requests
```

### 2. Configuración de WhatsApp

1. **Crear archivo .env**:
   ```bash
   # Copia el contenido de env_example.txt a un archivo .env
   cp env_example.txt .env
   ```

2. **Configurar WhatsApp Business API**:
   - Ve a [Facebook Developers](https://developers.facebook.com/)
   - Crea una nueva aplicación
   - Agrega el producto "WhatsApp Business API"
   - Configura tu número de teléfono de WhatsApp Business
   - Obtén el **Phone Number ID** y **Access Token**

3. **Editar archivo .env**:
   ```env
   WHATSAPP_PHONE_NUMBER_ID=tu_phone_number_id_real
   WHATSAPP_ACCESS_TOKEN=tu_access_token_real
   WHATSAPP_VERIFY_TOKEN=mi_token_secreto_123
   ```

## 📱 Uso del Sistema

### 1. Crear Cliente

Primero crea un cliente con número de teléfono:

```python
from models import Cliente
from services import ClienteService

cliente = Cliente(
    id=1,
    nombre="Juan",
    apellido="Pérez",
    dni="12345678",
    telefono="+54 9 11 1234-5678",
    email="juan@email.com",
    usuario_id=1
)
```

### 2. Crear Préstamo

Al crear un préstamo, se genera automáticamente el pagaré:

```python
from services import PrestamoService
from decimal import Decimal

prestamo_service = PrestamoService(db)

prestamo = prestamo_service.crear_prestamo(
    cliente_id=1,
    monto=Decimal('50000.0'),
    plazo_dias=90,
    tasa_interes=Decimal('5.0'),
    descripcion="Préstamo personal",
    usuario_id=1,
    es_admin=False
)
```

### 3. Pagaré Automático

El sistema:
1. ✅ Genera el pagaré en formato texto y HTML
2. ✅ Guarda el pagaré como archivo HTML
3. ✅ Envía el pagaré por WhatsApp al cliente
4. ✅ Registra el envío en los logs

## 📁 Estructura de Archivos

```
prestamos-sistem/
├── pagare_generator.py      # Generador de pagarés
├── whatsapp_sender.py       # Envío por WhatsApp
├── config_whatsapp.py       # Configuración de WhatsApp
├── test_pagare.py          # Script de prueba
├── env_example.txt         # Ejemplo de configuración
├── pagarés/                # Directorio de pagarés generados
│   └── pagare_000001_12345678_20250822_085624.html
└── README_PAGARE.md        # Este archivo
```

## 🧪 Pruebas

### Probar sin WhatsApp

```bash
python test_pagare.py
```

Este script:
- Crea un cliente y préstamo de prueba
- Genera el pagaré en texto y HTML
- Guarda el archivo HTML
- Muestra instrucciones de configuración

### Verificar configuración

```bash
python config_whatsapp.py
```

## 📋 Formato del Pagaré

El pagaré incluye:

- **Encabezado**: Título y número de préstamo
- **Datos del Cliente**: Nombre, DNI, teléfono, email
- **Detalles del Préstamo**: Monto, plazo, tasa, cuota mensual
- **Condiciones**: Términos y condiciones del préstamo
- **Firma**: Espacio para firma del cliente
- **Información de Contacto**: Teléfono y prestamista

## 🔧 Configuración Avanzada

### Personalizar Plantilla

Edita `pagare_generator.py` para modificar:
- Estilo del pagaré
- Información mostrada
- Formato de fechas
- Cálculos de intereses

### Webhook de WhatsApp

Para recibir mensajes de WhatsApp:

1. Configura `WHATSAPP_WEBHOOK_URL` en `.env`
2. Agrega rutas de webhook en `app.py`
3. Usa `whatsapp_sender.py` para procesar mensajes

## 🚨 Solución de Problemas

### WhatsApp no configurado

```
⚠️  WhatsApp no configurado. Configura las variables de entorno:
   WHATSAPP_PHONE_NUMBER_ID
   WHATSAPP_ACCESS_TOKEN
   WHATSAPP_VERIFY_TOKEN
```

**Solución**: Configura el archivo `.env` con tus credenciales de WhatsApp.

### Error de envío

```
❌ Error al enviar mensaje: 400
```

**Solución**: Verifica que el número de teléfono esté en formato internacional.

### Archivo no encontrado

```
❌ Error al guardar pagaré
```

**Solución**: Verifica permisos de escritura en el directorio.

## 📚 API Reference

### PagareGenerator

```python
class PagareGenerator:
    def generar_pagare(cliente, prestamo) -> str
    def generar_pagare_html(cliente, prestamo) -> str
    def enviar_pagare_whatsapp(cliente, prestamo) -> bool
    def guardar_pagare_archivo(cliente, prestamo, directorio="pagarés") -> str
```

### WhatsAppSender

```python
class WhatsAppSender:
    def enviar_mensaje(telefono, mensaje) -> bool
    def enviar_pagare_whatsapp(telefono, pagare_html) -> bool
    def enviar_mensaje_template(telefono, template_name, variables) -> bool
```

## 🎯 Próximos Pasos

1. **Configurar WhatsApp**: Sigue las instrucciones de configuración
2. **Probar Sistema**: Ejecuta `python test_pagare.py`
3. **Integrar en App**: Los pagarés se generan automáticamente
4. **Personalizar**: Modifica la plantilla según tus necesidades
5. **Webhook**: Configura para recibir mensajes de WhatsApp

## 📞 Soporte

Si tienes problemas:

1. Verifica la configuración de WhatsApp
2. Revisa los logs de error
3. Ejecuta el script de prueba
4. Verifica que las dependencias estén instaladas

---

**¡El sistema de pagaré está listo para usar! 🎉**
