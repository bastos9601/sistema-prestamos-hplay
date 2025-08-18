# Sistema de Préstamos de Dinero

Un sistema completo y profesional para gestionar préstamos de dinero con cálculo de intereses, gestión de clientes, pagos y reportes detallados.

## 🚀 Características Principales

### 📊 Gestión de Clientes
- Registro completo de clientes con DNI único
- Búsqueda por nombre, apellido o DNI
- Actualización de información personal
- Control de estado activo/inactivo

### 💰 Gestión de Préstamos
- Creación de préstamos con diferentes tipos de interés
- **Interés Simple**: Cálculo tradicional I = P × r × t
- **Interés Compuesto**: Cálculo compuesto A = P × (1 + r)^t
- Cálculo automático de cuotas mensuales
- Control de estado del préstamo

### 💳 Sistema de Pagos
- Registro de pagos con conceptos personalizables
- Cálculo automático de saldos pendientes
- Historial completo de pagos
- Actualización automática del estado del préstamo

### 📈 Reportes y Estadísticas
- Reporte general del sistema
- Reportes individuales por cliente
- Listado de préstamos activos
- Estadísticas financieras detalladas

## 🛠️ Requisitos del Sistema

- **Python 3.7+**
- **Sistema Operativo**: Windows, macOS, Linux
- **Memoria**: Mínimo 512MB RAM
- **Almacenamiento**: 100MB de espacio libre
- **Navegador Web**: Chrome, Firefox, Safari, Edge (para versión web)
- **Interfaz Gráfica**: Tkinter (incluido con Python, para versión desktop)

## 📦 Instalación

### 1. Clonar o descargar el proyecto
```bash
git clone <url-del-repositorio>
cd prestamos-sistem
```

### 2. Crear entorno virtual (recomendado)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

**Notas importantes:**
- **Flask**: Framework web para la versión web
- **Tkinter**: Viene incluido con Python por defecto (para versión desktop)
- **Navegador**: Cualquier navegador moderno para la versión web

## 🚀 Uso del Sistema

### 🌐 Versión Web (MUY RECOMENDADO)

#### **Opción 1: Con Datos de Ejemplo (Para Pruebas)**
```bash
python run_web.py
```
**Características:**
- ✅ Interfaz web moderna y responsive
- ✅ Accesible desde cualquier navegador
- ✅ Funciona en móviles y tablets
- ✅ Datos de ejemplo incluidos
- ✅ Se abre automáticamente en el navegador

#### **Opción 2: Sin Datos de Ejemplo (Para Producción)**
```bash
python iniciar_web.py
```
**Características:**
- ✅ Interfaz web moderna y responsive
- ✅ Accesible desde cualquier navegador
- ✅ Funciona en móviles y tablets
- ✅ Sistema limpio sin datos predefinidos
- ✅ Se abre automáticamente en el navegador
- ✅ Listo para crear clientes y préstamos manualmente

#### **Opción 3: Solo Aplicación Web (Más Simple)**
```bash
python app.py
```
**Características:**
- ✅ Solo inicia la aplicación web
- ✅ No abre el navegador automáticamente
- ✅ Sistema limpio sin datos predefinidos

### 🖥️ Interfaz Gráfica (Tkinter)
```bash
python main_gui.py
```

### 📟 Interfaz de Consola
```bash
python main.py
```

### 📚 Ejemplo con Datos
```bash
python ejemplo_gui.py
```

### Navegación por Menús

#### 🏠 Menú Principal
- **1. Gestión de Clientes** - Administrar información de clientes
- **2. Gestión de Préstamos** - Crear y administrar préstamos
- **3. Gestión de Pagos** - Registrar pagos y ver historiales
- **4. Reportes** - Generar reportes y estadísticas
- **5. Salir** - Cerrar el sistema

#### 👥 Gestión de Clientes
- **1. Registrar nuevo cliente** - Crear nuevo cliente
- **2. Buscar cliente** - Buscar por nombre, apellido o DNI
- **3. Listar todos los clientes** - Ver todos los clientes activos
- **4. Actualizar cliente** - Modificar información existente
- **5. Eliminar cliente** - Marcar como inactivo
- **6. Volver al menú principal**

#### 💰 Gestión de Préstamos
- **1. Crear nuevo préstamo** - Crear préstamo para cliente existente
- **2. Consultar préstamo** - Ver detalles completos de un préstamo
- **3. Listar préstamos de un cliente** - Ver todos los préstamos de un cliente
- **4. Listar préstamos activos** - Ver todos los préstamos activos
- **5. Calcular cuota mensual** - Calcular cuota de un préstamo específico
- **6. Volver al menú principal**

#### 💳 Gestión de Pagos
- **1. Registrar pago** - Registrar nuevo pago de un préstamo
- **2. Ver historial de pagos** - Ver todos los pagos de un préstamo
- **3. Volver al menú principal**

#### 📊 Reportes
- **1. Reporte general del sistema** - Estadísticas generales
- **2. Reporte de un cliente** - Información detallada de un cliente
- **3. Reporte de préstamos activos** - Lista de préstamos activos
- **4. Volver al menú principal**

## 📊 Tipos de Interés

### Interés Simple
```
I = P × r × t
```
Donde:
- **I** = Interés total
- **P** = Principal (monto del préstamo)
- **r** = Tasa de interés mensual (tasa anual ÷ 12)
- **t** = Tiempo en meses

### Interés Compuesto
```
A = P × (1 + r)^t
I = A - P
```
Donde:
- **A** = Monto final
- **P** = Principal (monto del préstamo)
- **r** = Tasa de interés mensual (tasa anual ÷ 12)
- **t** = Tiempo en meses
- **I** = Interés total

## 💾 Almacenamiento de Datos

El sistema utiliza archivos JSON para almacenar la información:
- `data/clientes.json` - Información de clientes
- `data/prestamos.json` - Información de préstamos
- `data/pagos.json` - Historial de pagos

Los datos se guardan automáticamente en cada operación.

## 🔧 Estructura del Proyecto

```
prestamos-sistem/
├── 🌐 VERSIÓN WEB (MUY RECOMENDADA)
│   ├── app.py                    # Aplicación Flask principal
│   ├── run_web.py               # Script para ejecutar con datos de ejemplo
│   ├── iniciar_web.py           # Script para ejecutar sin datos de ejemplo
│   ├── templates/                # Plantillas HTML
│   │   ├── base.html            # Plantilla base
│   │   ├── index.html           # Dashboard principal
│   │   ├── clientes.html        # Gestión de clientes
│   │   └── nuevo_cliente.html   # Formulario nuevo cliente
│   └── static/                   # Archivos estáticos
│       ├── css/style.css        # Estilos personalizados
│       └── js/app.js            # JavaScript principal
├── 🖥️ INTERFAZ GRÁFICA
│   ├── main_gui.py              # Aplicación principal con Tkinter
│   ├── ventanas_adicionales.py  # Ventanas para préstamos, pagos y reportes
│   └── ejemplo_gui.py           # Script con datos de ejemplo + Tkinter
├── 📟 INTERFAZ CONSOLA
│   └── main.py                  # Aplicación con interfaz de consola
├── 🔧 MÓDULOS DEL SISTEMA
│   ├── models.py                # Modelos de datos (Cliente, Prestamo, Pago)
│   ├── database.py              # Sistema de base de datos JSON
│   └── services.py              # Lógica de negocio y servicios
├── 📦 CONFIGURACIÓN
│   ├── requirements.txt          # Dependencias del proyecto
│   └── README.md                # Este archivo
└── 💾 DATOS
    └── data/                    # Directorio de datos (se crea automáticamente)
        ├── clientes.json
        ├── prestamos.json
        └── pagos.json
```

## 📝 Ejemplos de Uso

### 1. Crear un Cliente
```
Menú Principal → 1. Gestión de Clientes → 1. Registrar nuevo cliente
Nombre: Juan
Apellido: Pérez
DNI: 12345678
Teléfono: 555-0123
Email: juan.perez@email.com
```

### 2. Crear un Préstamo
```
Menú Principal → 2. Gestión de Préstamos → 1. Crear nuevo préstamo
ID del cliente: 1
Monto del préstamo: 10000
Tasa de interés anual (%): 12
Plazo en meses: 24
Tipo de interés: 1 (Simple)
```

### 3. Registrar un Pago
```
Menú Principal → 3. Gestión de Pagos → 1. Registrar pago
ID del préstamo: 1
Monto del pago: 500
Concepto: Pago de cuota mensual
```

## ⚠️ Consideraciones Importantes

- **Backup**: Realice copias de seguridad regulares del directorio `data/`
- **Validaciones**: El sistema incluye validaciones para evitar datos incorrectos
- **Seguridad**: Los datos se almacenan localmente en archivos JSON
- **Escalabilidad**: Para uso empresarial, considere migrar a una base de datos relacional

## 🐛 Solución de Problemas

### Error: "No module named 'colorama'"
```bash
pip install colorama
```

### Error: "No module named 'tabulate'"
```bash
pip install tabulate
```

### Error: "No module named 'python-dateutil'"
```bash
pip install python-dateutil
```

### Los datos no se guardan
- Verifique que el directorio `data/` tenga permisos de escritura
- Asegúrese de que haya suficiente espacio en disco

## 🔮 Próximas Funcionalidades

- [x] ✅ Interfaz gráfica con Tkinter
- [x] ✅ Interfaz web con Flask
- [ ] Exportación de reportes a PDF/Excel
- [ ] Sistema de notificaciones para vencimientos
- [ ] Múltiples monedas
- [ ] Cálculo de intereses moratorios
- [ ] Backup automático de datos
- [ ] Sistema de usuarios y permisos
- [ ] API REST completa
- [ ] Autenticación y autorización

## 📞 Soporte

Si encuentra algún problema o tiene sugerencias:
1. Revise la documentación
2. Verifique que todas las dependencias estén instaladas
3. Consulte los logs de error en la consola

## 📄 Licencia

Este proyecto es de código abierto y está disponible bajo la licencia MIT.

## 👨‍💻 Autor

Sistema de Préstamos - Versión 1.0

---

**¡Disfrute usando el Sistema de Préstamos de Dinero!** 🎉
