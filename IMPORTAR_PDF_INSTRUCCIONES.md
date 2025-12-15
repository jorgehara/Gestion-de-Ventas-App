# 📄 Importación de Productos desde PDF - Instrucciones

## ✅ ¿Qué se implementó?

Se agregó un **sistema completo de importación de productos desde PDF** que:

1. ✅ **Importa productos nuevos** desde el PDF de lista de precios
2. ✅ **Actualiza precios automáticamente** de productos existentes
3. ✅ **Calcula precios por día** automáticamente usando las fórmulas del sistema
4. ✅ **Detecta cambios** - Solo actualiza si el precio cambió
5. ✅ **Interfaz web fácil** - Botón para subir PDF directo desde el navegador

---

## 🚀 Cómo usar el sistema

### **Opción 1: Desde la interfaz web (RECOMENDADO)**

1. **Iniciar MongoDB:**
   ```
   Abrí el Administrador de servicios de Windows (services.msc)
   Buscá "MongoDB" y inicialo
   ```

2. **Iniciar el servidor:**
   ```bash
   python app.py
   ```

3. **Abrir el navegador:**
   - Ir a: `http://localhost:5000`
   - Click en la pestaña **"💰 Cálculos"**

4. **Importar el PDF:**
   - Click en el botón **"📄 Importar PDF"**
   - Seleccionar el archivo PDF (ej: `lista_de_precios_115.pdf`)
   - Esperar a que termine el proceso
   - ¡Listo! Verás un resumen con:
     - Cuántos productos se crearon
     - Cuántos se actualizaron
     - Cuántos no cambiaron
     - Si hubo errores

---

### **Opción 2: Desde línea de comandos (Avanzado)**

Si preferís usar el script de Python directamente:

```bash
python import_productos_pdf.py "listas_de_precios/lista_de_precios_115.pdf"
```

**Salida del script:**
```
============================================================
IMPORTACIÓN DE PRODUCTOS DESDE PDF
============================================================

📄 Procesando PDF: lista_de_precios/lista_de_precios_115.pdf

Procesando página 1/19...
Procesando página 2/19...
...
Procesando página 19/19...

✓ Se encontraron 547 productos en el PDF

============================================================
INICIANDO IMPORTACIÓN A BASE DE DATOS
============================================================

+ Creado: Caja De Dinero Acero 5 Divisiones - $173,673.00
+ Creado: Caja De Dinero Esmalte 5 Divisiones - $152,344.00
✓ Actualizado: Cajón Monedero 410x420x100 Negro - Nuevo precio: $195,468.00
...

============================================================
RESUMEN DE IMPORTACIÓN
============================================================
  ✓ Productos creados:     234
  ✓ Productos actualizados: 313
  - Sin cambios:           0
  ✗ Errores:               0
============================================================
```

---

## 🔄 ¿Cómo funciona la actualización?

El sistema es **inteligente** y actualiza automáticamente:

### **Si el producto YA EXISTE:**
- Busca por **código** (ej: `(05001)`) o por **nombre exacto**
- Compara el precio de lista
- Si el precio **cambió** → Actualiza precio de lista + precios por día
- Si el precio **no cambió** → No hace nada (ahorra tiempo)

### **Si el producto es NUEVO:**
- Lo crea con:
  - Código (si lo tiene)
  - Nombre
  - Precio de lista
  - Precios por día (calculados automáticamente)
  - Fecha de creación
  - Estado activo = true

---

## 📋 Requisitos del PDF

El PDF debe tener esta estructura (como el de Famago):

| Producto | Lista | 42 Cuotas | 84 Cuotas | ... |
|----------|-------|-----------|-----------|-----|
| (05001) Caja De Dinero... | 173.673 | 5.087 | 2.936 | ... |

**Notas importantes:**
- El sistema solo lee las columnas **Producto** y **Lista**
- Los precios por día se **calculan automáticamente** (no se leen del PDF)
- Las categorías (Línea:, Categoría:) se ignoran automáticamente

---

## 🎯 Casos de uso

### **Caso 1: Actualización mensual de precios**
```
Cada mes reciís un nuevo PDF con lista de precios actualizada:
1. Click "Importar PDF"
2. Seleccionar el nuevo PDF
3. El sistema actualiza solo los precios que cambiaron
4. ¡Listo! Los clientes ven los nuevos precios al instante
```

### **Caso 2: Agregar productos nuevos**
```
Si agregan 5 productos nuevos al catálogo:
1. Importar el PDF con todos los productos (viejos + nuevos)
2. Los productos viejos NO se duplican (se detectan por código/nombre)
3. Solo se crean los 5 productos nuevos
```

### **Caso 3: Primera importación**
```
Si estás empezando y querés cargar todo el catálogo:
1. Importar el PDF completo
2. Se crean todos los productos de cero
3. Ya tenés todo el catálogo listo para usar
```

---

## ⚙️ Archivos modificados/creados

### **Nuevos archivos:**
- ✨ `import_productos_pdf.py` - Script standalone de importación
- ✨ `IMPORTAR_PDF_INSTRUCCIONES.md` - Esta documentación

### **Archivos modificados:**
- ✏️ `app.py` - Agregado endpoint `/api/import-productos-pdf`
- ✏️ `templates/index.html` - Agregado botón "Importar PDF" + JavaScript

---

## 📊 Detalles técnicos

### **Librerías usadas:**
- `pdfplumber` - Para leer y extraer tablas del PDF
- `pymongo` - Para conectar con MongoDB
- `re` - Para extraer códigos de productos con regex

### **Endpoint API:**
```
POST /api/import-productos-pdf
Content-Type: multipart/form-data

Parámetros:
  - file: Archivo PDF

Respuesta:
{
  "success": true,
  "message": "Importación completada",
  "stats": {
    "creados": 234,
    "actualizados": 313,
    "sin_cambios": 0,
    "errores": 0
  },
  "total_procesados": 547
}
```

### **Fórmulas de cálculo:**
```python
Precio por día 42  = (Precio Lista × 1.23) / 42
Precio por día 84  = (Precio Lista × 1.42) / 84
Precio por día 135 = (Precio Lista × 1.58) / 135
Precio por día 175 = (Precio Lista × 1.75) / 175
Precio por día 220 = (Precio Lista × 1.92) / 220
```

---

## ❓ Preguntas frecuentes

**¿Puedo importar el mismo PDF varias veces?**
Sí, el sistema detecta duplicados y no los crea de nuevo.

**¿Se pierden los productos viejos al importar?**
No, solo se actualizan precios. Nunca se eliminan productos.

**¿Qué pasa si un producto ya no está en el nuevo PDF?**
El producto se mantiene en la base de datos. Si querés eliminarlo, hacelo manualmente.

**¿El PDF puede estar en cualquier formato?**
Debe tener tablas con columnas "Producto" y "Lista". El formato de Famago funciona perfecto.

**¿Puedo usar Excel en vez de PDF?**
Sí, también está el botón "Importar Excel" que ya existía.

---

## 🐛 Troubleshooting

**Error: "No se pudo conectar a MongoDB"**
- Asegurate que MongoDB esté corriendo: `services.msc` → MongoDB → Iniciar

**Error: "No se encontraron productos"**
- Verificá que el PDF tenga tablas con la columna "Producto" y "Lista"
- Probá con el PDF de ejemplo que ya funcionó: `lista_de_precios_115.pdf`

**Error: "Authentication failed"**
- MongoDB requiere autenticación. Revisá la configuración en `app.py`

**El import es muy lento:**
- Es normal con PDFs grandes (19 páginas pueden tardar 30-60 segundos)
- Procesamiento se hace página por página

---

## ✅ Próximos pasos sugeridos

- [ ] Agregar opción de "preview" antes de importar
- [ ] Exportar productos a PDF/Excel
- [ ] Historial de importaciones (cuándo y qué se importó)
- [ ] Notificaciones cuando cambian precios importantes
- [ ] Comparador de precios entre versiones de PDF

---

**¡Sistema listo para usar!** 🎉

Si tenés dudas, revisá el código en:
- `import_productos_pdf.py` - Script de importación
- `app.py` (línea 736-912) - Endpoint API
- `templates/index.html` (línea 676-687 y 1484-1525) - Interfaz web
