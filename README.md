# 🏦 Sistema de Préstamos de Dinero

Un sistema completo y moderno para gestionar préstamos de dinero con interfaz web, sistema de roles y permisos granulares.

## ✨ Características Principales

- 🔐 **Sistema de Autenticación** con roles y permisos
- 👥 **Gestión de Clientes** completa (CRUD)
- 💰 **Gestión de Préstamos** con diferentes tipos de interés
- 💳 **Sistema de Pagos** con seguimiento de saldos
- 📊 **Reportes y Estadísticas** en tiempo real
- 🎨 **Interfaz Web Moderna** con Bootstrap 5
- 📱 **Diseño Responsive** para todos los dispositivos
- 🛡️ **Seguridad CSRF** y validación de formularios

## 🎭 Roles de Usuario

### 👑 Administrador
- Acceso completo al sistema
- Gestión de usuarios
- Todas las operaciones CRUD

### 👨‍💼 Supervisor
- Crear, editar y ver registros
- Sin eliminación de datos
- Acceso a reportes

### 👷 Operador
- Crear y ver registros
- Sin edición ni eliminación
- Acceso básico a reportes

### 👁️ Consultor
- Solo visualización de reportes
- Sin modificaciones
- Acceso limitado

## 🚀 Despliegue en Render

### Opción 1: Despliegue Automático (Recomendado)

1. **Fork o clona** este repositorio en GitHub
2. **Conecta tu repositorio** a Render
3. **Crea un nuevo Web Service** en Render
4. **Selecciona tu repositorio** y branch
5. **Configura las variables de entorno**:
   - `SECRET_KEY`: Clave secreta para Flask
   - `FLASK_ENV`: `production`
6. **Deploy automático** - Render detectará la configuración

### Opción 2: Despliegue Manual

1. **Crea un nuevo Web Service** en Render
2. **Configura el build command**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Configura el start command**:
   ```bash
   gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 30
   ```
4. **Configura las variables de entorno** como en la opción 1

## 🛠️ Instalación Local

### Requisitos
- Python 3.9+
- pip

### Pasos de Instalación

1. **Clona el repositorio**:
   ```bash
   git clone <tu-repositorio>
   cd prestamos-sistem
   ```

2. **Instala las dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Ejecuta la aplicación**:
   ```bash
   python iniciar_web.py
   ```

4. **Abre tu navegador** en `http://localhost:5000`

## 🔐 Usuarios por Defecto

- **Admin**: `admin` / `admin123`
- **Supervisor**: `supervisor` / `super123`
- **Operador**: `operador` / `oper123`
- **Consultor**: `consultor` / `cons123`

## 📁 Estructura del Proyecto

```
prestamos-sistem/
├── app.py                 # Aplicación principal Flask
├── models.py              # Modelos de datos
├── database.py            # Capa de persistencia
├── services.py            # Lógica de negocio
├── forms.py               # Formularios WTForms
├── templates/             # Plantillas HTML
├── static/                # Archivos estáticos
├── data/                  # Base de datos JSON
├── requirements.txt       # Dependencias Python
├── render.yaml           # Configuración Render
├── gunicorn.conf.py      # Configuración Gunicorn
├── Procfile              # Configuración Render
└── runtime.txt           # Versión Python
```

## 🌐 Variables de Entorno

### Desarrollo Local
```bash
export FLASK_ENV=development
export SECRET_KEY=tu_clave_secreta_aqui
```

### Producción (Render)
- `SECRET_KEY`: Generada automáticamente por Render
- `FLASK_ENV`: `production`
- `PORT`: Puerto asignado por Render

## 🔧 Configuración de Producción

### Gunicorn
- **Workers**: 2 (configurable en `gunicorn.conf.py`)
- **Timeout**: 30 segundos
- **Bind**: `0.0.0.0:$PORT`

### Seguridad
- **CSRF Protection**: Activado
- **Session Security**: Configurado
- **Input Validation**: WTForms

## 📊 Monitoreo y Logs

### Render Dashboard
- **Build Logs**: Visibles en tiempo real
- **Runtime Logs**: Accesibles desde el dashboard
- **Health Checks**: Automáticos en `/`

### Logs Locales
```bash
# Ver logs de la aplicación
tail -f app.log

# Ver logs de Gunicorn
tail -f gunicorn.log
```

## 🚨 Solución de Problemas

### Error de Dependencias
```bash
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

### Error de Puerto
- Verifica que el puerto 5000 esté libre
- Usa `python iniciar_web.py` para desarrollo local

### Error de Base de Datos
- Verifica que la carpeta `data/` exista
- Los archivos JSON se crean automáticamente

## 🤝 Contribuciones

1. **Fork** el proyecto
2. **Crea** una rama para tu feature
3. **Commit** tus cambios
4. **Push** a la rama
5. **Abre** un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 📞 Soporte

Si tienes problemas o preguntas:
1. Revisa los logs de la aplicación
2. Verifica la configuración de Render
3. Abre un issue en GitHub

---

**¡Disfruta usando tu Sistema de Préstamos en la nube! 🎉**
