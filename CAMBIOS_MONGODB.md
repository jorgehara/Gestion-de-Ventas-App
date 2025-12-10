# Resumen de Migración a MongoDB

## ✅ Cambios Completados

### 1. Archivos Modificados

#### `requirements.txt`
- ❌ Eliminado: `Flask-SQLAlchemy==3.1.1`
- ✅ Agregado: `pymongo==4.6.1`
- ✅ Agregado: `python-dotenv==1.0.0`

#### `app.py` (324 líneas → 402 líneas)
**Cambios principales:**
- ❌ Removido: SQLAlchemy y modelo ORM
- ✅ Agregado: PyMongo y conexión a MongoDB
- ✅ Función helper `cliente_to_dict()` para convertir documentos
- ✅ Todas las rutas adaptadas a operaciones MongoDB:
  - `find()` en lugar de `query.all()`
  - `insert_one()` en lugar de `db.session.add()`
  - `update_one()` en lugar de `db.session.commit()`
  - `delete_one()` en lugar de `db.session.delete()`
  - `aggregate()` para estadísticas
- ✅ Manejo de ObjectId de MongoDB
- ✅ Validación de conexión al inicio
- ✅ Creación automática de índices

#### `import_data.py` (116 líneas → 163 líneas)
**Cambios principales:**
- ❌ Removido: Dependencias de SQLAlchemy
- ✅ Agregado: Conexión directa a MongoDB con PyMongo
- ✅ Importación en lotes (cada 100 registros)
- ✅ Mejor manejo de errores
- ✅ Creación de índices al finalizar

#### `start_server.sh`
- ✅ Agregado: Verificación de que MongoDB esté corriendo
- ✅ Agregado: Mensajes informativos sobre MongoDB
- ✅ Agregado: Opción de continuar si MongoDB no está corriendo

#### `README.md`
**Secciones actualizadas:**
- ✅ Descripción del proyecto (menciona MongoDB)
- ✅ Características técnicas
- ✅ Requisitos (incluye MongoDB 4.4+)
- ✅ Instalación completa de MongoDB (Windows, macOS, Linux)
- ✅ Configuración de variables de entorno
- ✅ Comandos de inicio
- ✅ Estructura del proyecto actualizada
- ✅ Sección de base de datos reescrita
- ✅ Instrucciones para MongoDB Atlas

### 2. Archivos Nuevos

#### `.env`
```
MONGO_URI=mongodb://localhost:27017/
DB_NAME=crm_famago
```

#### `.env.example`
Plantilla de configuración con ejemplos para MongoDB local y Atlas

#### `start_server.bat`
Script de inicio para Windows con verificación de MongoDB

#### `INSTALACION.md`
Guía completa paso a paso:
- Instalación de MongoDB por sistema operativo
- Instalación de dependencias
- Configuración
- Inicio del servidor
- Solución de problemas comunes
- Comandos útiles

#### `CAMBIOS_MONGODB.md` (este archivo)
Documentación de todos los cambios realizados

---

## 🔄 Comparación: SQLite vs MongoDB

| Aspecto | SQLite (Antes) | MongoDB (Ahora) |
|---------|----------------|-----------------|
| **Tipo de BD** | SQL relacional | NoSQL documento |
| **Archivo** | clientes.db | Base de datos crm_famago |
| **ORM** | SQLAlchemy | PyMongo (driver nativo) |
| **Esquema** | Rígido (tablas) | Flexible (colecciones) |
| **Escalabilidad** | Limitada | Alta |
| **Consultas** | SQL | Filtros JSON |
| **Índices** | Automáticos en PK | Creados manualmente |
| **Agregaciones** | GROUP BY | Pipeline de agregación |
| **Cloud** | No nativo | MongoDB Atlas |

---

## 📊 Estructura de Datos en MongoDB

### Colección: `clientes`

```javascript
{
  _id: ObjectId("..."),                    // ID único de MongoDB
  fecha: ISODate("2024-01-15T10:30:00Z"), // Fecha de registro
  cliente: "Juan Pérez",                   // Nombre del cliente
  nombre_negocio: "Almacén Don Juan",     // Nombre del negocio
  localidad: "SAENZ PEÑA",                // Ciudad/pueblo
  direccion: "Av. San Martin 123",        // Dirección
  barrio: "Centro",                        // Barrio
  dni: "12345678",                         // DNI
  es_cliente: "SI",                        // ¿Es cliente?
  detalle: "Cliente frecuente",            // Detalles
  interes_1: "Azúcar",                     // Producto 1
  interes_2: "Yerba",                      // Producto 2
  interes_3: "Aceite",                     // Producto 3
  cantidad_compras: "5 veces",             // Historial
  intencion_comprar: "MUCHA",              // Intención (POCA, INTERMEDIA, MUCHA, EXTREMA, YA COMPRÓ, MOROSO)
  accion: "Llamar la próxima semana",     // Próxima acción
  comentario: "Buen pagador",              // Notas
  fecha_nacimiento: ISODate("1980-05-20"), // Fecha de nacimiento
  años: 44                                 // Edad
}
```

### Índices Creados

```javascript
db.clientes.createIndex({ cliente: 1 })
db.clientes.createIndex({ localidad: 1 })
db.clientes.createIndex({ intencion_comprar: 1 })
```

---

## 🚀 Ventajas de la Migración

### Rendimiento
- ✅ Consultas más rápidas con índices optimizados
- ✅ Agregaciones nativas para estadísticas
- ✅ Sin overhead de ORM

### Escalabilidad
- ✅ Soporta millones de documentos
- ✅ Sharding para distribución de datos
- ✅ Replicación para alta disponibilidad

### Flexibilidad
- ✅ Esquema flexible (agregar campos sin migraciones)
- ✅ Documentos anidados si se necesitan en el futuro
- ✅ Consultas complejas con pipeline de agregación

### Deployment
- ✅ Fácil migración a MongoDB Atlas (cloud)
- ✅ Backups automáticos en Atlas
- ✅ Monitoreo y alertas incluidas

---

## 🔧 Operaciones Comunes

### Conectarse a MongoDB directamente

```bash
mongosh
use crm_famago
```

### Ver todos los clientes

```javascript
db.clientes.find().limit(10).pretty()
```

### Contar clientes por intención

```javascript
db.clientes.aggregate([
  { $group: { _id: "$intencion_comprar", count: { $sum: 1 } } }
])
```

### Buscar clientes de una localidad

```javascript
db.clientes.find({ localidad: "SAENZ PEÑA" })
```

### Ver índices

```javascript
db.clientes.getIndexes()
```

### Hacer backup

```bash
mongodump --db crm_famago --out ./backup
```

### Restaurar backup

```bash
mongorestore --db crm_famago ./backup/crm_famago
```

---

## ⚠️ Consideraciones Importantes

### Para desarrollo local:
- Asegúrate de que MongoDB esté corriendo antes de iniciar la app
- Los datos se almacenan en MongoDB local (no en archivo .db)
- Usa `mongosh` para inspeccionar los datos directamente

### Para producción:
- Considera usar MongoDB Atlas (cloud)
- Configura autenticación en MongoDB
- Habilita SSL/TLS
- Configura backups automáticos
- Monitorea el rendimiento

### Migración de datos existentes:
Si tenías datos en SQLite:
1. Exporta desde SQLite a Excel
2. Usa la función de importación de Excel en la app
3. Los datos se importarán automáticamente a MongoDB

---

## 📝 Notas de Compatibilidad

### API REST
✅ No hay cambios en la API REST. Todas las rutas siguen funcionando igual:
- `GET /api/clientes`
- `POST /api/clientes`
- `PUT /api/clientes/<id>`
- `DELETE /api/clientes/<id>`
- `GET /api/stats`
- `GET /api/localidades`
- `POST /api/import-excel`
- `GET /api/export-excel`

### Frontend
✅ No requiere cambios. El archivo `index.html` funciona sin modificaciones.

### Funcionalidades
✅ Todas las funcionalidades originales se mantienen:
- CRUD de clientes
- Filtros por localidad e intención
- Búsqueda de texto
- Dashboard con estadísticas
- Importación/exportación de Excel
- Edición en modal
- Validaciones

---

## 🎯 Próximos Pasos Sugeridos

1. **Instalar MongoDB** siguiendo `INSTALACION.md`
2. **Instalar dependencias:** `pip install -r requirements.txt`
3. **Importar datos** (si tienes Excel): `python import_data.py`
4. **Iniciar servidor:** `./start_server.sh` o `start_server.bat`
5. **Acceder a la app:** http://localhost:5000

---

**Fecha de migración:** 2024
**Versión anterior:** SQLite + SQLAlchemy
**Versión actual:** MongoDB + PyMongo
**Estado:** ✅ Completado y listo para usar
