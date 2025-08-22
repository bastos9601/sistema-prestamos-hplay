# 📱 Sistema de WhatsApp Directo para Préstamos

## 📋 Descripción

Este sistema permite enviar pagarés y mensajes por WhatsApp directamente desde la interfaz web, sin necesidad de configurar APIs de WhatsApp Business. Simplemente hace clic en el botón y se abre WhatsApp Web en tu navegador.

## ✨ Características

- **Envío Directo**: No requiere configuración de API
- **Botón en Acciones**: Aparece en la columna de acciones de préstamos y clientes
- **Pagaré Automático**: Genera y envía pagarés completos
- **Chat Directo**: Abre WhatsApp para cualquier cliente
- **Multi-usuario**: Compatible con tu sistema existente

## 🚀 Cómo Funciona

### 1. **En Préstamos** - Botón de Pagaré
- En la tabla de préstamos, cada fila tiene un botón **📱** (WhatsApp)
- Al hacer clic, se genera automáticamente el pagaré
- Se abre WhatsApp Web con el mensaje predefinido
- Solo necesitas hacer clic en "Enviar"

### 2. **En Clientes** - Botón de Chat
- En la tabla de clientes, cada fila tiene un botón **📱** (WhatsApp)
- Al hacer clic, se abre directamente el chat de WhatsApp
- Puedes escribir cualquier mensaje personalizado

## 📱 Botones Agregados

### En Préstamos (Columna Acciones)
```
[👁️] [💳] [📱] [🗑️]
Ver   Pago  Pagaré Eliminar
```

### En Clientes (Columna Acciones)
```
[✏️] [📱] [🗑️]
Edit  WhatsApp Eliminar
```

## 🔧 Funcionalidades Técnicas

### Generación de Pagaré
- **Formato**: Texto completo con emojis y formato profesional
- **Contenido**: Datos del cliente, préstamo, condiciones y firma
- **Cálculos**: Intereses, cuotas mensuales, total a pagar
- **Envío**: Se abre WhatsApp Web con el mensaje listo

### Envío por WhatsApp
- **Método**: Enlaces directos `wa.me`
- **Formato**: Números internacionales (+54 para Argentina)
- **Navegador**: Se abre automáticamente en tu navegador
- **Mensaje**: Predefinido para pagarés, personalizable para chats

## 📁 Archivos Modificados

### Nuevos Archivos
- **`whatsapp_sender.py`** - Sistema de envío directo
- **`pagare_generator.py`** - Generador de pagarés
- **`test_whatsapp_directo.py`** - Script de prueba

### Archivos Modificados
- **`app.py`** - Nuevas rutas API para WhatsApp
- **`templates/prestamos.html`** - Botón de pagaré
- **`templates/clientes.html`** - Botón de WhatsApp
- **`services.py`** - Integración con generador de pagarés

## 🧪 Pruebas

### Probar Sistema Completo
```bash
python test_pagare.py
```

### Probar WhatsApp Directo
```bash
python test_whatsapp_directo.py
```

## 📋 Ejemplo de Uso

### 1. Crear Cliente
- Ve a **Clientes** → **+ Nuevo Cliente**
- Completa: Nombre, Apellido, DNI, **Teléfono**, Email
- **Importante**: El teléfono es obligatorio para WhatsApp

### 2. Crear Préstamo
- Ve a **Préstamos** → **+ Nuevo Préstamo**
- Selecciona el cliente y completa los datos
- Se genera automáticamente el pagaré

### 3. Enviar Pagaré
- En la tabla de préstamos, busca el préstamo
- Haz clic en el botón **📱** (WhatsApp)
- Se abre WhatsApp Web con el pagaré completo
- Haz clic en "Enviar"

### 4. Chat Directo
- En la tabla de clientes, busca el cliente
- Haz clic en el botón **📱** (WhatsApp)
- Se abre el chat de WhatsApp
- Escribe tu mensaje personalizado

## 🎯 Ventajas del Sistema

### ✅ **Fácil de Usar**
- Un solo clic para enviar pagarés
- No requiere configuración técnica
- Funciona inmediatamente

### ✅ **Sin Costos**
- No hay APIs de pago
- No hay límites de mensajes
- No hay configuraciones complejas

### ✅ **Profesional**
- Pagarés con formato profesional
- Mensajes predefinidos
- Integración completa con el sistema

### ✅ **Flexible**
- Envío de pagarés automático
- Chat personalizado para clientes
- Funciona con cualquier número

## 🔍 Solución de Problemas

### WhatsApp no se abre
- **Verificar**: Navegador no bloquea popups
- **Solución**: Permitir popups para tu sitio

### Número no válido
- **Verificar**: Formato del teléfono (+54 9 11 1234-5678)
- **Solución**: Usar formato internacional

### Botón no aparece
- **Verificar**: Cliente tiene teléfono registrado
- **Solución**: Editar cliente y agregar teléfono

### Error al generar pagaré
- **Verificar**: Datos del préstamo completos
- **Solución**: Revisar que todos los campos estén llenos

## 📚 API Endpoints

### Enviar Pagaré
```
POST /api/enviar-pagare/<prestamo_id>
```

### Abrir WhatsApp
```
POST /api/abrir-whatsapp/<cliente_id>
```

## 🎉 ¡Listo para Usar!

El sistema está completamente integrado y funcionando:

1. **Los botones aparecen automáticamente** en las tablas
2. **Los pagarés se generan** con un clic
3. **WhatsApp se abre** en tu navegador
4. **No hay configuración** adicional necesaria

---

**¡Disfruta enviando pagarés y mensajes por WhatsApp de forma fácil y profesional! 🚀**
