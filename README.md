# CRM Famago - Sistema de Gestión de Clientes

Sistema web completo de CRM desarrollado con Flask y Python para gestionar clientes con funcionalidades avanzadas de filtrado, importación/exportación de Excel y dashboard estadístico.

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
- 🔒 **Base de datos SQLite** - persistencia de datos confiable
- 📱 **Totalmente responsive** - se adapta a cualquier pantalla

## 📋 Requisitos

- Python 3.8+
- pip (gestor de paquetes de Python)

## 🛠️ Instalación

### 1. Instalar dependencias

```bash
pip install flask flask-sqlalchemy openpyxl pandas --break-system-packages
```

### 2. Importar datos iniciales (opcional)

Si tienes un archivo Excel con datos existentes:

```bash
python import_data.py
```

Este script:
- Lee el archivo Excel proporcionado
- Crea la base de datos SQLite
- Importa todos los registros
- Normaliza los datos (ej: "POCA" y "poCA" → "POCA")

## 🚀 Uso

### Iniciar el servidor

```bash
python app.py
```

El servidor estará disponible en: **http://localhost:5000**

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
├── app.py                 # Aplicación Flask principal
├── import_data.py         # Script de importación inicial
├── clientes.db           # Base de datos SQLite (se crea automáticamente)
├── templates/
│   └── index.html        # Plantilla HTML con CSS y JS
└── README.md             # Este archivo
```

## 💾 Base de Datos

La aplicación usa SQLite por defecto, lo cual es ideal para:
- Despliegues pequeños/medianos (hasta 10,000 registros sin problema)
- No requiere servidor de base de datos separado
- Archivo único fácil de respaldar
- Portabilidad total

Para producción con muchos usuarios simultáneos, se puede cambiar a PostgreSQL o MySQL modificando la configuración de SQLAlchemy.

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
