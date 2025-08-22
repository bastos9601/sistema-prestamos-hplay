# 🚀 Guía de Despliegue en Render

## 📋 **Resumen del Despliegue**

Esta guía te ayudará a desplegar tu Sistema de Préstamos en Render con PostgreSQL.

## 🎯 **Qué vamos a hacer:**

1. **Crear base de datos PostgreSQL en Render**
2. **Desplegar la aplicación web Flask**
3. **Migrar datos de SQLite/JSON a PostgreSQL**
4. **Configurar variables de entorno**
5. **Probar la aplicación en producción**

---

## 🔧 **Paso 1: Preparar el Proyecto**

### **1.1 Verificar archivos necesarios**

Asegúrate de tener estos archivos en tu proyecto:

```
prestamos-sistem/
├── app.py                    # ✅ Aplicación principal
├── requirements.txt          # ✅ Dependencias
├── render.yaml              # ✅ Configuración de Render
├── migrate_to_postgresql.py # ✅ Script de migración
├── database_postgresql.py   # ✅ Adaptador PostgreSQL
├── config_production.py     # ✅ Configuración producción
└── data/                    # ✅ Datos actuales
    ├── usuarios.json
    ├── clientes.json
    ├── prestamos.json
    └── pagos.json
```

### **1.2 Instalar dependencias localmente (opcional)**

```bash
pip install -r requirements.txt
```

---

## 🌐 **Paso 2: Crear Cuenta en Render**

### **2.1 Registrarse en Render**

1. Ve a [render.com](https://render.com)
2. Haz clic en "Get Started"
3. Regístrate con GitHub, GitLab o email
4. Verifica tu cuenta

### **2.2 Conectar repositorio**

1. Haz clic en "New +"
2. Selecciona "Web Service"
3. Conecta tu repositorio de GitHub/GitLab
4. Selecciona el repositorio del proyecto

---

## 🗄️ **Paso 3: Crear Base de Datos PostgreSQL**

### **3.1 Crear servicio de base de datos**

1. En Render, haz clic en "New +"
2. Selecciona "PostgreSQL"
3. Configura:
   - **Name**: `prestamos-db`
   - **Database**: `prestamos`
   - **User**: `prestamos_user`
   - **Region**: El más cercano a ti
   - **Plan**: `Free` (para empezar)

### **3.2 Obtener información de conexión**

1. Una vez creada, haz clic en la base de datos
2. Ve a "Connections"
3. Copia la **Internal Database URL**
4. Anota también:
   - **Database**: `prestamos`
   - **User**: `prestamos_user`
   - **Password**: (se genera automáticamente)

---

## 🚀 **Paso 4: Desplegar la Aplicación Web**

### **4.1 Crear servicio web**

1. En Render, haz clic en "New +"
2. Selecciona "Web Service"
3. Conecta tu repositorio
4. Configura:

```
Name: prestamos-web
Environment: Python 3
Build Command: pip install -r requirements.txt
Start Command: gunicorn app:app
```

### **4.2 Configurar variables de entorno**

En la sección "Environment Variables", agrega:

```
FLASK_ENV=production
SECRET_KEY=tu-clave-secreta-muy-larga-y-segura
DATABASE_URL=postgresql://prestamos_user:password@host:port/prestamos
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=tu-email@gmail.com
MAIL_PASSWORD=tu-password-de-aplicacion
LOG_LEVEL=INFO
```

### **4.3 Configurar la base de datos**

En "Environment Variables", agrega:

```
DATABASE_URL=postgresql://prestamos_user:password@host:port/prestamos
```

**Nota**: Reemplaza `password`, `host`, `port` con los valores reales de tu base de datos.

---

## 🔄 **Paso 5: Migrar Datos a PostgreSQL**

### **5.1 Ejecutar migración automática**

Una vez desplegada la aplicación, Render ejecutará automáticamente:

```bash
pip install -r requirements.txt
gunicorn app:app
```

### **5.2 Verificar migración**

1. Ve a tu aplicación web desplegada
2. Intenta hacer login
3. Verifica que los datos estén disponibles

### **5.3 Migración manual (si es necesario)**

Si necesitas migrar manualmente:

```bash
# En tu máquina local
python migrate_to_postgresql.py
```

---

## ⚙️ **Paso 6: Configuración Avanzada**

### **6.1 Configurar dominio personalizado**

1. En tu servicio web, ve a "Settings"
2. En "Custom Domains", agrega tu dominio
3. Configura DNS según las instrucciones

### **6.2 Configurar SSL**

Render proporciona SSL automático para:
- Dominios `.onrender.com`
- Dominios personalizados

### **6.3 Configurar backups**

1. En tu base de datos PostgreSQL
2. Ve a "Backups"
3. Configura backups automáticos

---

## 🧪 **Paso 7: Probar la Aplicación**

### **7.1 Verificar funcionalidades**

1. **Login/Logout**: ✅
2. **Gestión de usuarios**: ✅
3. **Gestión de clientes**: ✅
4. **Gestión de préstamos**: ✅
5. **Gestión de pagos**: ✅
6. **Reportes**: ✅
7. **Recuperación de contraseña**: ✅

### **7.2 Verificar base de datos**

1. Ve a tu base de datos en Render
2. Verifica que las tablas se crearon
3. Verifica que los datos estén presentes

---

## 🔍 **Paso 8: Monitoreo y Logs**

### **8.1 Ver logs en tiempo real**

1. En tu servicio web, ve a "Logs"
2. Monitorea errores y actividad

### **8.2 Configurar alertas**

1. En "Settings" > "Alerts"
2. Configura notificaciones por email

---

## 🚨 **Solución de Problemas Comunes**

### **Problema 1: Error de conexión a base de datos**

**Síntoma**: `psycopg2.OperationalError: could not connect to server`

**Solución**:
1. Verifica que `DATABASE_URL` esté correcta
2. Asegúrate de que la base de datos esté activa
3. Verifica que el usuario tenga permisos

### **Problema 2: Error de dependencias**

**Síntoma**: `ModuleNotFoundError: No module named 'psycopg2'`

**Solución**:
1. Verifica que `requirements.txt` incluya `psycopg2-binary`
2. Asegúrate de que el build command sea correcto

### **Problema 3: Error de migración**

**Síntoma**: `relation "usuarios" does not exist`

**Solución**:
1. Ejecuta el script de migración manualmente
2. Verifica que las tablas se creen correctamente

### **Problema 4: Error de permisos**

**Síntoma**: `permission denied for table usuarios`

**Solución**:
1. Verifica que el usuario de la base de datos tenga permisos
2. Ejecuta `GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO prestamos_user;`

---

## 📊 **Monitoreo de Rendimiento**

### **Métricas a monitorear**

1. **Tiempo de respuesta**: < 2 segundos
2. **Uso de CPU**: < 80%
3. **Uso de memoria**: < 80%
4. **Conexiones de BD**: < 80% del pool

### **Herramientas de monitoreo**

1. **Render Dashboard**: Métricas básicas
2. **Logs**: Errores y actividad
3. **Health Checks**: Estado del servicio

---

## 🔒 **Seguridad en Producción**

### **Configuraciones de seguridad**

1. **SECRET_KEY**: Cambia la clave por defecto
2. **HTTPS**: Siempre habilitado
3. **Cookies seguras**: Configuradas automáticamente
4. **Rate limiting**: Habilitado en producción

### **Variables sensibles**

Nunca commits estas variables:
- `SECRET_KEY`
- `DATABASE_URL`
- `MAIL_PASSWORD`
- `WHATSAPP_API_KEY`

---

## 📈 **Escalabilidad**

### **Planes de Render**

- **Free**: Para desarrollo y pruebas
- **Starter**: $7/mes - Para uso básico
- **Standard**: $25/mes - Para producción
- **Pro**: $50/mes - Para alto tráfico

### **Cuándo escalar**

1. **Free → Starter**: Cuando superes los límites del plan gratuito
2. **Starter → Standard**: Cuando tengas > 100 usuarios activos
3. **Standard → Pro**: Cuando tengas > 1000 usuarios activos

---

## 🔄 **Actualizaciones y Deployment**

### **Deployment automático**

1. Render detecta cambios en tu repositorio
2. Ejecuta build automáticamente
3. Despliega la nueva versión

### **Rollback**

1. En "Deploys", selecciona una versión anterior
2. Haz clic en "Promote"
3. La versión anterior se activa

---

## 📞 **Soporte y Recursos**

### **Documentación oficial**

- [Render Docs](https://render.com/docs)
- [PostgreSQL en Render](https://render.com/docs/databases)
- [Python en Render](https://render.com/docs/deploy-python)

### **Comunidad**

- [Render Community](https://community.render.com)
- [Stack Overflow](https://stackoverflow.com/questions/tagged/render)

### **Contacto de soporte**

- **Email**: support@render.com
- **Chat**: Disponible en el dashboard

---

## 🎉 **¡Felicidades!**

Tu Sistema de Préstamos está ahora desplegado en Render con PostgreSQL.

### **URLs importantes**

- **Aplicación web**: `https://tu-app.onrender.com`
- **Dashboard de Render**: `https://dashboard.render.com`
- **Base de datos**: `https://dashboard.render.com/databases`

### **Próximos pasos**

1. **Configurar dominio personalizado**
2. **Configurar backups automáticos**
3. **Implementar monitoreo avanzado**
4. **Configurar CI/CD con GitHub Actions**

---

## 📝 **Checklist de Despliegue**

- [ ] Cuenta en Render creada
- [ ] Repositorio conectado
- [ ] Base de datos PostgreSQL creada
- [ ] Variables de entorno configuradas
- [ ] Aplicación desplegada
- [ ] Datos migrados
- [ ] Funcionalidades probadas
- [ ] SSL configurado
- [ ] Logs monitoreados
- [ ] Backup configurado

---

**¡Tu aplicación está lista para producción! 🚀**
