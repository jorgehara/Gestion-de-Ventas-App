# Sistema de Cálculos - IMPLEMENTADO

## ¿Qué se agregó al sistema?

Se implementó completamente la nueva funcionalidad de **Cálculos de Precios** con las siguientes características:

### 1. **Nueva Pestaña "Cálculos"** 💰

La interfaz incluye:
- **Gestión de Productos**: Tabla con listado completo de productos
- **Precios calculados automáticamente**: Para cada plan (42, 84, 135, 175, 220 días)
- **Calculadora Interactiva**: Selecciona producto + plan y obtén el precio final al instante
- **Importación desde Excel**: Carga directa de la lista de precios

### 2. **Fórmulas de Cálculo Implementadas**

#### Contado Efectivo:
```
Precio Final = Precio de Lista × (1 - 34.39%)
```

#### Planes Financiados (42, 84, 135, 175, 220 días):
```
Paso 1: Aplicar recargo por financiación
  - 42 días:  +23%
  - 84 días:  +42%
  - 135 días: +58%
  - 175 días: +75%
  - 220 días: +92%

Paso 2: Calcular precio por día
  Precio por Día = (Precio Lista × (1 + Recargo%)) / Días

Paso 3: Aplicar descuento
  - 42 días:  30.75%
  - 84 días:  27.1%
  - 135 días: 27.1%
  - 175 días: 27.1%
  - 220 días: 27.1%

Paso 4: Calcular precio final
  Precio Final = Precio por Día × (1 - Descuento%) × Días
```

### 3. **API Backend (Flask)**

Nuevos endpoints agregados a `app.py`:

```
GET    /api/productos              - Listar todos los productos
GET    /api/productos/<id>         - Obtener un producto
POST   /api/productos              - Crear producto
PUT    /api/productos/<id>         - Actualizar producto
DELETE /api/productos/<id>         - Eliminar producto

POST   /api/calcular               - Calcular precio final
POST   /api/import-productos-excel - Importar desde Excel
```

### 4. **Base de Datos (MongoDB)**

Nueva colección `productos`:
```javascript
{
  _id: ObjectId,
  codigo: String,
  nombre: String,
  precio_lista: Number,
  precios_por_dia: {
    '42': Number,
    '84': Number,
    '135': Number,
    '175': Number,
    '220': Number
  },
  fecha_actualizacion: Date,
  activo: Boolean
}
```

---

## 🚀 Cómo usar el sistema

### Paso 1: Iniciar MongoDB

En Windows:
```bash
# Opción 1: Servicio de Windows (si está instalado como servicio)
net start MongoDB

# Opción 2: Iniciar manualmente
mongod --dbpath "C:\data\db"
```

### Paso 2: Iniciar el servidor Flask

```bash
python app.py
```

Verás:
```
✓ Conexión exitosa a MongoDB: crm_famago
 * Running on http://0.0.0.0:5000
```

### Paso 3: Abrir el navegador

Ir a: **http://localhost:5000**

### Paso 4: Usar la pestaña Cálculos

1. **Importar productos desde Excel:**
   - Click en "Importar Lista de Precios"
   - Selecciona el archivo `listas_de_precios/listas_precios.jpeg` (o cualquier Excel con columnas "Producto" y "Lista")
   - El sistema cargará todos los productos y calculará automáticamente los precios por día

2. **Crear producto manualmente:**
   - Click en "Nuevo Producto"
   - Ingresa código (opcional), nombre y precio de lista
   - Los precios por día se calcularán automáticamente

3. **Calcular precios:**
   - Selecciona un producto del dropdown
   - Selecciona un plan de pago
   - Verás instantáneamente:
     - Precio base
     - Recargos/descuentos aplicados
     - Precio por día (si aplica)
     - **Precio Final** destacado

---

## 📊 Ejemplo Práctico

**Producto:** Caja De Dinero Acero 5 Divisiones
**Precio de Lista:** $173.673

### Contado Efectivo:
```
Precio Lista:    $173.673
Descuento:       34,39%
───────────────────────────
Precio Final:    $113.941
```

### Plan 42 Días:
```
Precio Lista:           $173.673
Recargo +23%:           $213.618
Precio por Día:         $5.086
Descuento 30,75%:
Precio por Día Final:   $3.523
───────────────────────────────
Total (42 × $3.523):    $147.966
```

---

## 🧪 Pruebas Automáticas

Ejecutar el script de prueba:
```bash
python test_calculos.py
```

Este script:
- Crea un producto de prueba
- Calcula precios para todos los planes
- Verifica que los cálculos sean correctos
- Muestra tabla comparativa de todos los planes

---

## 📁 Archivos Modificados/Creados

### Archivos Modificados:
- ✏️ `app.py` - Agregados endpoints de productos y cálculos
- ✏️ `templates/index.html` - Nueva pestaña Cálculos y calculadora

### Archivos Creados:
- ✨ `test_calculos.py` - Script de pruebas
- ✨ `CALCULOS_README.md` - Esta documentación

---

## 🎨 Interfaz de Usuario

La nueva pestaña **Cálculos** incluye:

### Sección 1: Tabla de Productos
- Listado completo con código, nombre, precio lista
- Precios por día precalculados para todos los planes
- Botones de editar/eliminar por producto
- Botón "Nuevo Producto" y "Importar Lista de Precios"

### Sección 2: Calculadora Interactiva
- Selector de producto (dropdown)
- Selector de plan de pago (dropdown)
- **Resultado dinámico** con:
  - Desglose paso a paso del cálculo
  - Precio final destacado en verde
  - Diseño visual atractivo con gradientes

---

## 💡 Ventajas del Sistema

✅ **Cálculos automáticos** - No más Excel manual
✅ **Actualización en tiempo real** - Cambia el precio de lista y todos los planes se recalculan
✅ **Importación rápida** - Carga toda tu lista de precios en segundos
✅ **Interfaz intuitiva** - Fácil de usar para vendedores
✅ **Desglose transparente** - Muestra cómo se llegó al precio final
✅ **Base de datos centralizada** - Todos los productos en un solo lugar

---

## 🔧 Próximas Mejoras Posibles

- [ ] Exportar resultados de cálculos a PDF
- [ ] Agregar más planes de pago personalizados
- [ ] Historial de cotizaciones
- [ ] Impresión directa de cotizaciones
- [ ] Descuentos por región configurable
- [ ] Comparador de planes lado a lado

---

## 📞 Soporte

Si tienes dudas o encuentras algún error:
1. Verifica que MongoDB esté corriendo
2. Revisa los logs del servidor Flask
3. Ejecuta el script de prueba para validar cálculos

---

**¡Sistema listo para usar!** 🎉
