# ✅ Checklist de Instalación - CRM Famago

Use este checklist para verificar que todo esté configurado correctamente.

## Antes de empezar

- [ ] Python 3.8+ instalado
  ```bash
  python --version
  # Debe mostrar: Python 3.8.x o superior
  ```

- [ ] pip instalado
  ```bash
  pip --version
  # Debe mostrar la versión de pip
  ```

## Paso 1: MongoDB

- [ ] MongoDB instalado
  ```bash
  # Windows
  mongod --version

  # macOS/Linux
  mongod --version

  # Debe mostrar: db version v4.4.x o superior
  ```

- [ ] MongoDB corriendo
  ```bash
  # Windows
  net start MongoDB
  # O verificar: tasklist | find "mongod"

  # macOS
  brew services list
  # Debe mostrar: mongodb-community started

  # Linux
  sudo systemctl status mongod
  # Debe mostrar: active (running)
  ```

- [ ] MongoDB accesible
  ```bash
  mongosh
  # Debe conectarse sin errores
  # Luego escribe: exit
  ```

## Paso 2: Dependencias de Python

- [ ] Navegaste al directorio del proyecto
  ```bash
  cd ruta/al/proyecto/Gestion-de-Ventas-App
  ```

- [ ] Instalaste las dependencias
  ```bash
  pip install -r requirements.txt
  # Debe instalar: Flask, pymongo, openpyxl, pandas, python-dotenv
  ```

- [ ] Verificaste que pymongo esté instalado
  ```bash
  python -c "import pymongo; print(pymongo.__version__)"
  # Debe mostrar: 4.6.x
  ```

## Paso 3: Configuración

- [ ] Existe el archivo `.env` en el directorio raíz
  ```bash
  # Windows
  dir .env

  # macOS/Linux
  ls -la .env
  ```

- [ ] El archivo `.env` contiene la configuración correcta
  ```
  MONGO_URI=mongodb://localhost:27017/
  DB_NAME=crm_famago
  ```

## Paso 4: Archivos del Proyecto

- [ ] Verificaste que existen los archivos principales
  - [ ] app.py
  - [ ] import_data.py
  - [ ] index.html
  - [ ] requirements.txt
  - [ ] .env

## Paso 5: Importación de Datos (Opcional)

Si tienes el archivo Excel con datos:

- [ ] El archivo Excel está en el directorio del proyecto
  ```
  Famago 1.9.1 - copia.xlsx
  ```

- [ ] Ejecutaste el script de importación
  ```bash
  python import_data.py
  ```

- [ ] La importación fue exitosa
  ```
  ✓ Conexión exitosa a MongoDB: crm_famago
  ✓ Archivo Excel leído correctamente: XXXX filas
  ...
  ✅ Importación completada!
  Total importados: XXXX
  Errores: 0
  ✓ Índices creados correctamente
  ```

## Paso 6: Iniciar el Servidor

- [ ] Iniciaste el servidor
  ```bash
  # Windows
  start_server.bat

  # macOS/Linux
  ./start_server.sh

  # O manualmente
  python app.py
  ```

- [ ] El servidor inició sin errores
  ```
  ✓ Conexión exitosa a MongoDB: crm_famago
  * Serving Flask app 'app'
  * Debug mode: on
  * Running on http://0.0.0.0:5000
  ```

## Paso 7: Verificar la Aplicación

- [ ] Abriste el navegador en http://localhost:5000

- [ ] La página carga correctamente

- [ ] Probaste cada pestaña:
  - [ ] Dashboard - Muestra estadísticas
  - [ ] Clientes - Muestra la tabla
  - [ ] Nuevo Cliente - Formulario funcional
  - [ ] Importar/Exportar - Botones visibles

## Paso 8: Pruebas Funcionales

- [ ] Crear un cliente de prueba
  - Ir a "Nuevo Cliente"
  - Llenar al menos: Cliente, Intención de Comprar
  - Clic en "Guardar"
  - Debe aparecer mensaje de éxito

- [ ] Ver el cliente creado
  - Ir a "Clientes"
  - Debe aparecer en la tabla

- [ ] Editar el cliente
  - Clic en botón "Editar"
  - Modificar algún campo
  - Guardar
  - Debe actualizarse

- [ ] Filtrar clientes
  - Usar el filtro de búsqueda
  - Debe filtrar la tabla

- [ ] Ver estadísticas
  - Ir a "Dashboard"
  - Debe mostrar al menos 1 cliente
  - El gráfico debe aparecer

- [ ] Exportar a Excel
  - Ir a "Importar/Exportar"
  - Clic en "Exportar a Excel"
  - Debe descargar un archivo .xlsx

## Verificación de MongoDB

- [ ] Verificaste los datos en MongoDB
  ```bash
  mongosh
  use crm_famago
  db.clientes.countDocuments()
  # Debe mostrar el número de clientes

  db.clientes.findOne()
  # Debe mostrar un documento de ejemplo

  exit
  ```

---

## ¿Algo no funciona?

### Si MongoDB no inicia:

**Windows:**
```bash
# Verifica el servicio
services.msc
# Busca "MongoDB" y asegúrate que esté "Running"

# O inicia manualmente
net start MongoDB
```

**macOS:**
```bash
# Reinicia el servicio
brew services restart mongodb-community

# Verifica los logs
tail -f /opt/homebrew/var/log/mongodb/mongo.log
```

**Linux:**
```bash
# Reinicia el servicio
sudo systemctl restart mongod

# Verifica los logs
sudo journalctl -u mongod -f
```

### Si las dependencias fallan:

```bash
# Actualiza pip
python -m pip install --upgrade pip

# Reinstala las dependencias
pip install -r requirements.txt --force-reinstall
```

### Si el puerto 5000 está ocupado:

Edita `app.py` (última línea):
```python
app.run(debug=True, host='0.0.0.0', port=8000)  # Cambia 5000 por 8000
```

Luego accede a: http://localhost:8000

---

## ✅ Todo listo!

Si marcaste todos los checkboxes, tu instalación está completa y la aplicación está funcionando correctamente.

**Próximos pasos:**
1. Empieza a usar la aplicación para gestionar tus clientes
2. Importa tus datos desde Excel si aún no lo hiciste
3. Explora las funcionalidades de filtrado y búsqueda
4. Revisa el dashboard para ver estadísticas

**Documentación adicional:**
- `README.md` - Documentación completa
- `INSTALACION.md` - Guía de instalación detallada
- `CAMBIOS_MONGODB.md` - Información sobre la migración a MongoDB
- `GUIA_RAPIDA.md` - Guía de uso rápido

---

**¿Necesitas ayuda?**
Revisa la sección de solución de problemas en `INSTALACION.md`
