# 🚀 GUÍA DE INICIO RÁPIDO - CRM Famago

## Inicio Inmediato

### Opción 1: Inicio Rápido (recomendado)
```bash
./start_server.sh
```

### Opción 2: Inicio Manual
```bash
python3 app.py
```

Luego abre tu navegador en: **http://localhost:5000**

---

## ✅ La aplicación ya está lista para usar

✨ **Base de datos precargada** con 1,665 clientes del Excel original
✨ **Todo funcionando** - no necesitas configurar nada más

---

## 🎯 Tareas Comunes

### 1️⃣ Ver Dashboard
- Haz clic en la pestaña "📊 Dashboard"
- Verás estadísticas y gráficos de tus clientes

### 2️⃣ Ver Listado de Clientes
- Haz clic en "👥 Clientes"
- Usa los filtros para buscar por localidad o intención
- Usa la barra de búsqueda para encontrar clientes específicos

### 3️⃣ Agregar Nuevo Cliente
- Haz clic en "➕ Nuevo Cliente"
- Llena el formulario (solo Cliente e Intención son obligatorios)
- Haz clic en "Guardar Cliente"

### 4️⃣ Editar un Cliente
- En la tabla de clientes, haz clic en el botón ✏️ 
- Modifica los datos en el modal
- Haz clic en "Guardar Cambios"

### 5️⃣ Eliminar un Cliente
- En la tabla de clientes, haz clic en el botón 🗑️
- Confirma la eliminación

### 6️⃣ Exportar a Excel
- Ve a "📥 Importar/Exportar"
- Haz clic en "Descargar Excel"
- Se descargará un archivo con todos tus clientes actuales

### 7️⃣ Importar desde Excel
- Ve a "📥 Importar/Exportar"
- Haz clic en la zona de carga o arrastra un archivo .xlsx
- Los datos se importarán automáticamente

---

## 🎨 Colores de Intención de Compra

| Color | Intención | Significado |
|-------|-----------|-------------|
| 🔴 Rojo | EXTREMA | Máxima prioridad - contactar YA |
| 🟠 Naranja | MUCHA | Alta prioridad - seguimiento cercano |
| 🔵 Azul | INTERMEDIA | Prioridad media - seguimiento regular |
| ⚫ Gris | POCA | Baja prioridad - seguimiento ocasional |
| 🟢 Verde | YA COMPRÓ | Cliente convertido ✅ |
| 🟤 Marrón | MOROSO | Requiere atención especial ⚠️ |

---

## 📱 Acceso desde Móvil/Tablet

La aplicación es **totalmente responsive**:

1. Asegúrate de que tu móvil/tablet esté en la misma red que la computadora
2. Encuentra la IP de tu computadora:
   - Windows: `ipconfig`
   - Mac/Linux: `ifconfig` o `ip addr`
3. En el móvil, abre: `http://[IP-DE-TU-PC]:5000`
   - Ejemplo: `http://192.168.1.100:5000`

---

## 💾 Respaldo de Datos

Tu base de datos está en el archivo: `instance/clientes.db`

**Para hacer respaldo:**
```bash
cp instance/clientes.db backup_$(date +%Y%m%d).db
```

**Para restaurar respaldo:**
```bash
cp backup_20250101.db instance/clientes.db
```

---

## ❓ Resolución de Problemas

### El servidor no inicia
```bash
# Verifica que tienes las dependencias
pip install flask flask-sqlalchemy openpyxl pandas --break-system-packages
```

### Error de puerto en uso
```bash
# Cambia el puerto en app.py, línea final:
# app.run(debug=True, host='0.0.0.0', port=5001)  # Usa 5001 en vez de 5000
```

### La base de datos se corrompió
```bash
# Elimina la BD actual y reimporta
rm -rf instance/
python3 import_data.py
```

---

## 🔥 Tips Pro

1. **Prioriza por color**: Los clientes con intención "EXTREMA" (rojo) deben contactarse primero
2. **Usa comentarios**: Agrega notas detalladas en cada cliente para recordar conversaciones
3. **Filtra inteligentemente**: Combina filtros de localidad + intención para planificar visitas
4. **Exporta regularmente**: Haz backup semanalmente exportando a Excel
5. **Busca rápido**: Usa Ctrl+F en tu navegador para buscar en la tabla visible

---

## 📞 Atajos de Teclado

| Tecla | Acción |
|-------|--------|
| `Ctrl + F` | Buscar en página |
| `Tab` | Navegar entre campos del formulario |
| `Enter` | Enviar formulario |
| `Esc` | Cerrar modal de edición |

---

## 🎓 Mejores Prácticas

### Para Vendedores:
- ✅ Actualiza la intención después de cada contacto
- ✅ Agrega comentarios con fecha de último contacto
- ✅ Marca acción siguiente (ej: "Llamar el lunes")
- ✅ Completa intereses para ofrecer productos relevantes

### Para Gerentes:
- ✅ Revisa dashboard diariamente
- ✅ Prioriza zonas con más clientes "EXTREMA" o "MUCHA"
- ✅ Exporta reportes semanales
- ✅ Analiza conversión (cuántos pasaron a "YA COMPRÓ")

---

## 🆘 Soporte

Si encuentras algún problema:

1. Revisa la consola donde ejecutaste `python3 app.py`
2. Los errores aparecerán ahí con detalles
3. Para reiniciar limpio: Ctrl+C para detener, luego `python3 app.py` de nuevo

---

**¡Listo para usar! Que tengas excelentes ventas 🎯📈**
