# CRM Famago - Sistema de Gestión de Clientes

Sistema web completo de CRM desarrollado con Flask, Python y MongoDB para gestionar clientes con funcionalidades avanzadas de filtrado, importación/exportación de Excel y dashboard estadístico.

## 🚀 Características

### Funcionalidades Principales
- ✅ **Cargar nuevos clientes** manualmente desde la interfaz
- ✅ **Importar clientes** desde archivos Excel (.xlsx)
- ✅ **Ver listado de clientes** con tabla responsive
- ✅ **Filtrar por localidad** (con búsqueda dinámica)
- ✅ **Filtrar por intención de compra** (Extrema, Mucha, Intermedia, Poca, Ya compró, Moroso)
- ✅ **Buscar** por nombre, negocio o comentario
- ✅ **Editar registros** con modal intuitivo
- ✅ **Eliminar registros** con confirmación
- ✅ **Exportar datos** a Excel

### Dashboard
- 📊 Cantidad total de clientes
- 📊 Distribución por nivel de intención de compra
- 📊 Gráfico de barras visual mostrando clientes por intención
- 📊 Cards estadísticas coloridas

### Características Técnicas
- 🎨 **Diseño moderno y responsivo** - funciona perfecto en móvil y desktop
- 🎯 **UI intuitiva** orientada a vendedores para cargar datos rápido
- ⚡ **Sin recargas de página** - actualizaciones en tiempo real con JavaScript
- 🔒 **Base de datos MongoDB** - persistencia de datos NoSQL escalable
- 📱 **Totalmente responsive** - se adapta a cualquier pantalla

## 📋 Requisitos

- Python 3.8+
- pip (gestor de paquetes de Python)
- MongoDB 4.4+ (instalado y corriendo en localhost:27017)

## 🛠️ Instalación

### 1. Instalar MongoDB

**Windows:**
```bash
# Descarga MongoDB Community Server desde:
# https://www.mongodb.com/try/download/community
# O instala con Chocolatey:
choco install mongodb
```

**macOS:**
```bash
brew tap mongodb/brew
brew install mongodb-community
brew services start mongodb-community
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install -y mongodb
sudo systemctl start mongod
sudo systemctl enable mongod
```

### 2. Instalar dependencias de Python

```bash
pip install -r requirements.txt
```

O manualmente:
```bash
pip install flask pymongo openpyxl pandas python-dotenv
```

### 3. Configurar variables de entorno

Copia el archivo `.env.example` a `.env`:
```bash
cp .env.example .env
```

El archivo `.env` contiene:
```
MONGO_URI=mongodb://localhost:27017/
DB_NAME=crm_famago
```

### 4. Importar datos iniciales (opcional)

Si tienes un archivo Excel con datos existentes:

```bash
python import_data.py
```

Este script:
- Lee el archivo Excel proporcionado
- Se conecta a MongoDB
- Importa todos los registros
- Normaliza los datos (ej: "POCA" y "poCA" → "POCA")
- Crea índices para mejorar el rendimiento

## 🚀 Uso

### Iniciar el servidor

**Linux/macOS:**
```bash
./start_server.sh
```

**Windows:**
```bash
start_server.bat
```

**O manualmente:**
```bash
python app.py
```

El servidor estará disponible en: **http://localhost:5000**

**Nota:** Asegúrate de que MongoDB esté corriendo antes de iniciar el servidor.

### Navegación

La aplicación tiene 4 pestañas principales:

#### 1. 📊 Dashboard
- Vista general con estadísticas
- Gráfico de distribución por intención
- Cards con totales por categoría

#### 2. 👥 Clientes
- Listado completo de clientes
- Filtros por localidad e intención
- Búsqueda de texto libre
- Acciones de editar/eliminar

#### 3. ➕ Nuevo Cliente
- Formulario completo para agregar clientes
- Campos requeridos: Cliente, Intención de comprar
- Todos los demás campos son opcionales

#### 4. 📥 Importar/Exportar
- **Importar:** Arrastra o selecciona un archivo Excel
- **Exportar:** Descarga todos los datos actuales en Excel

## 📊 Estructura de Datos

### Campos del Cliente

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| Fecha | Fecha | Automático | Fecha de registro |
| Cliente | Texto | Sí | Nombre del cliente |
| Nombre Negocio | Texto | No | Razón social o nombre del negocio |
| Localidad | Texto | No | Ciudad/pueblo |
| Dirección | Texto | No | Dirección física |
| Barrio | Texto | No | Barrio |
| DNI | Texto | No | Documento de identidad |
| Es Cliente? | Opción | No | SI/NO |
| Detalle | Texto largo | No | Información adicional |
| Interés 1, 2, 3 | Texto | No | Productos/servicios de interés |
| Cantidad Compras | Texto | No | Historial de compras |
| **Intención de Comprar** | Opción | **Sí** | EXTREMA/MUCHA/INTERMEDIA/POCA/YA COMPRÓ/MOROSO |
| Acción | Texto | No | Próxima acción a realizar |
| Comentario | Texto largo | No | Notas adicionales |

### Valores de Intención de Compra

- 🔴 **EXTREMA** - Máxima prioridad
- 🟠 **MUCHA** - Alta prioridad
- 🔵 **INTERMEDIA** - Prioridad media
- ⚫ **POCA** - Baja prioridad
- 🟢 **YA COMPRÓ** - Cliente convertido
- 🟤 **MOROSO** - Con deuda

## 🎨 Interfaz de Usuario

### Características de Diseño
- **Paleta de colores profesional** con degradados modernos
- **Iconos visuales** para mejor comprensión
- **Badges de colores** para identificar rápido la intención
- **Animaciones suaves** en hover y transiciones
- **Formularios grandes** y fáciles de usar
- **Modales centrados** para edición

### Responsive Design
- ✅ Desktop (1920px+)
- ✅ Laptop (1366px)
- ✅ Tablet (768px)
- ✅ Móvil (375px+)

## 🔧 API Endpoints

### GET /api/clientes
Obtener listado de clientes con filtros opcionales
```
Query params:
- search: búsqueda de texto
- localidad: filtro por localidad
- intencion: filtro por intención
```

### POST /api/clientes
Crear nuevo cliente
```json
{
  "cliente": "Juan Pérez",
  "localidad": "SAENZ PEÑA",
  "intencion_comprar": "MUCHA"
}
```

### PUT /api/clientes/{id}
Actualizar cliente existente

### DELETE /api/clientes/{id}
Eliminar cliente

### GET /api/stats
Obtener estadísticas generales

### POST /api/import-excel
Importar archivo Excel

### GET /api/export-excel
Descargar datos en Excel

### GET /api/localidades
Obtener lista de localidades únicas

## 📦 Estructura del Proyecto

```
crm-famago/
├── app.py                  # Aplicación Flask principal con PyMongo
├── import_data.py          # Script de importación inicial a MongoDB
├── templates/
│   └── index.html         # Plantilla HTML con CSS y JS
├── requirements.txt       # Dependencias de Python
├── .env                   # Variables de entorno (MongoDB)
├── .env.example          # Ejemplo de configuración
├── start_server.sh       # Script de inicio para Linux/macOS
├── start_server.bat      # Script de inicio para Windows
└── README.md             # Este archivo
```

## 💾 Base de Datos

La aplicación usa **MongoDB**, lo cual ofrece:
- **Escalabilidad** - maneja fácilmente miles o millones de registros
- **Flexibilidad** - esquema flexible para adaptarse a cambios
- **Rendimiento** - consultas rápidas con índices optimizados
- **Cloud-ready** - fácil migración a MongoDB Atlas (cloud)
- **Agregaciones** - estadísticas y reportes avanzados

### Configuración de MongoDB

**Local (desarrollo):**
```
MONGO_URI=mongodb://localhost:27017/
DB_NAME=crm_famago
```

**MongoDB Atlas (producción):**
```
MONGO_URI=mongodb+srv://usuario:contraseña@cluster.mongodb.net/?retryWrites=true&w=majority
DB_NAME=crm_famago
```

### Colecciones

- **clientes** - Almacena toda la información de clientes
  - Índices en: `cliente`, `localidad`, `intencion_comprar`

## 🔒 Seguridad

**Nota:** Esta versión es para uso interno/local. Para producción considerar:
- Autenticación de usuarios
- HTTPS
- Validación de entrada más estricta
- Rate limiting
- Sanitización de datos

## 🎯 Casos de Uso

### Vendedores
1. Agregar prospectos rápidamente desde el campo
2. Actualizar intención de compra después de cada contacto
3. Priorizar visitas según nivel de intención
4. Ver qué zonas tienen más prospectos

### Gerentes
1. Ver dashboard con estadísticas generales
2. Identificar zonas con mayor potencial
3. Exportar datos para análisis externo
4. Monitorear conversión (YA COMPRÓ)

### Administración
1. Importar listas masivas desde Excel
2. Mantener base de datos actualizada
3. Exportar reportes periódicos
4. Auditar comentarios y acciones

## 🚀 Mejoras Futuras Sugeridas

- [ ] Sistema de usuarios con login
- [ ] Historial de cambios por cliente
- [ ] Notificaciones de seguimiento
- [ ] Integración con WhatsApp/Email
- [ ] Reportes PDF automatizados
- [ ] Mapas de ubicación de clientes
- [ ] Sistema de tareas/recordatorios
- [ ] Análisis predictivo con ML

## 📞 Soporte

Para problemas o sugerencias, revisar los logs de la aplicación en la consola donde se ejecuta `python app.py`.

## 📝 Licencia

Uso interno - Famago 2025
