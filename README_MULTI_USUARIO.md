# Sistema de Préstamos Multi-Usuario

## 🚀 Características del Sistema

### Sistema Multi-Usuario con Aislamiento de Datos
- **Administrador**: Puede crear usuarios y ver todos los datos del sistema
- **Usuarios**: Pueden usar todas las funcionalidades pero solo ven sus propios datos
- **Aislamiento Total**: Cada usuario tiene su propia base de datos virtual
- **Seguridad**: Los usuarios no pueden acceder a datos de otros usuarios

### Roles de Usuario
1. **Admin**: Acceso completo al sistema, puede crear usuarios
2. **Supervisor**: Puede ver usuarios, crear/editar clientes, préstamos y pagos
3. **Operador**: Puede crear y ver clientes, préstamos y pagos
4. **Consultor**: Solo puede ver información (sin modificar)

## 🛠️ Instalación y Configuración

### 1. Requisitos
```bash
Python 3.7+
Flask
Flask-WTF
```

### 2. Instalación
```bash
# Clonar el repositorio
git clone <url-del-repositorio>
cd prestamos-sistem

# Instalar dependencias
pip install -r requirements.txt

# Inicializar el sistema
python inicializar_sistema.py
```

### 3. Configuración Inicial
El script `inicializar_sistema.py` crea automáticamente:
- Usuario administrador: `admin` / `admin123`
- Estructura de base de datos
- Archivos de configuración

## 🔐 Sistema de Autenticación

### Login
- Accede a `/login` con tus credenciales
- El sistema verifica permisos en cada operación
- Sesiones seguras con timeout configurable

### Cambio de Contraseña
- Los usuarios pueden cambiar su propia contraseña
- Contraseñas hasheadas con SHA-256
- No se almacenan contraseñas en texto plano

## 👥 Gestión de Usuarios

### Crear Usuarios (Solo Admin)
1. Accede a `/usuarios`
2. Haz clic en "Nuevo Usuario"
3. Completa el formulario con:
   - Username único
   - Nombre completo
   - Email (opcional)
   - Rol (supervisor, operador, consultor)
   - Contraseña

### Editar Usuarios
- Los usuarios pueden editar su propia información
- Los admins pueden editar cualquier usuario
- Los usuarios pueden editar usuarios que crearon

### Eliminar Usuarios
- Solo marcan como inactivos (no se eliminan físicamente)
- Los usuarios no pueden eliminar su propia cuenta

## 📊 Funcionalidades por Usuario

### Clientes
- **Crear**: Cada usuario crea sus propios clientes
- **Ver**: Solo ven sus propios clientes (los admins ven todos)
- **Editar**: Solo pueden editar sus propios clientes
- **Eliminar**: Solo pueden eliminar sus propios clientes

### Préstamos
- **Crear**: Solo para clientes propios
- **Ver**: Solo sus propios préstamos
- **Editar**: Solo sus propios préstamos
- **Eliminar**: Solo sus propios préstamos

### Pagos
- **Registrar**: Solo para préstamos propios
- **Ver**: Solo sus propios pagos
- **Eliminar**: Solo sus propios pagos

### Reportes
- **Generales**: Estadísticas de sus propios datos
- **Por Cliente**: Solo para clientes propios
- **Préstamos Activos**: Solo sus préstamos activos

## 🔒 Seguridad y Permisos

### Aislamiento de Datos
- Cada registro tiene un `usuario_id` asociado
- Las consultas filtran automáticamente por usuario
- Los admins pueden ver todos los datos
- Los usuarios solo ven sus propios datos

### Verificación de Permisos
- Decoradores `@permiso_requerido()` en cada ruta
- Verificación de roles en tiempo de ejecución
- Validación de acceso a recursos específicos

### Protección de Rutas
- Todas las rutas requieren autenticación
- Verificación de permisos antes de cada operación
- Redirección automática si no hay permisos

## 📁 Estructura de Archivos

```
prestamos-sistem/
├── app.py                 # Aplicación principal Flask
├── models.py             # Modelos de datos (Usuario, Cliente, Préstamo, Pago)
├── database.py           # Capa de acceso a datos con aislamiento
├── services.py           # Lógica de negocio con filtros por usuario
├── forms.py              # Formularios web
├── inicializar_sistema.py # Script de inicialización
├── templates/            # Plantillas HTML
├── static/               # Archivos estáticos (CSS, JS)
└── data/                 # Base de datos JSON
```

## 🚀 Uso del Sistema

### 1. Primer Acceso
```bash
# Inicializar sistema
python inicializar_sistema.py

# Ejecutar aplicación
python app.py

# Acceder a http://localhost:5000
# Login: admin / admin123
```

### 2. Crear Usuarios Adicionales
1. Accede como administrador
2. Ve a `/usuarios` → "Nuevo Usuario"
3. Crea usuarios con diferentes roles
4. Cada usuario tendrá acceso independiente

### 3. Gestión de Datos
- Cada usuario crea sus propios clientes
- Los préstamos se asocian automáticamente al usuario
- Los pagos se registran con el usuario que los crea
- Los reportes muestran solo datos del usuario

## 🔧 Configuración Avanzada

### Cambiar Configuración de Sesión
En `app.py`:
```python
app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 hora
app.config['SECRET_KEY'] = 'tu_clave_secreta_aqui'
```

### Modificar Roles y Permisos
En `models.py`, clase `Usuario`:
```python
def _get_permisos_por_rol(self, rol: str) -> list:
    # Personalizar permisos por rol
```

### Cambiar Estructura de Base de Datos
Los archivos JSON se almacenan en `data/`:
- `usuarios.json`: Usuarios del sistema
- `clientes.json`: Clientes con usuario_id
- `prestamos.json`: Préstamos con usuario_id
- `pagos.json`: Pagos con usuario_id

## 🐛 Solución de Problemas

### Error de Permisos
- Verifica que el usuario tenga el rol correcto
- Confirma que los permisos estén configurados
- Revisa la sesión del usuario

### Datos No Visibles
- Verifica que el usuario_id esté correctamente asignado
- Confirma que el aislamiento esté funcionando
- Revisa los logs de la aplicación

### Problemas de Login
- Verifica que el usuario esté activo
- Confirma que la contraseña sea correcta
- Revisa que la base de datos esté accesible

## 📈 Escalabilidad

### Ventajas del Sistema Multi-Usuario
- **Independencia**: Cada usuario trabaja de forma aislada
- **Seguridad**: No hay acceso cruzado entre usuarios
- **Flexibilidad**: Fácil agregar nuevos usuarios y roles
- **Auditoría**: Trazabilidad completa de operaciones

### Consideraciones de Rendimiento
- Filtros automáticos en todas las consultas
- Índices por usuario_id en la base de datos
- Caché de permisos en sesión del usuario

## 🤝 Contribución

### Reportar Bugs
1. Verifica que no sea un problema de permisos
2. Confirma que el usuario tenga el rol correcto
3. Revisa los logs de la aplicación
4. Proporciona pasos para reproducir el problema

### Sugerencias de Mejoras
- Nuevos roles y permisos
- Funcionalidades adicionales
- Mejoras en la interfaz de usuario
- Optimizaciones de rendimiento

## 📄 Licencia

Este proyecto está bajo la licencia especificada en el archivo `LICENSE`.

---

**¡El sistema está listo para usar con múltiples usuarios de forma segura y aislada!** 🎉
