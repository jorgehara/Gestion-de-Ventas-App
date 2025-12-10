# Guía Rápida de Instalación - CRM Famago

Esta guía te ayudará a instalar y ejecutar el CRM Famago en menos de 10 minutos.

## Paso 1: Instalar MongoDB

### Windows

**Opción A: Instalador oficial**
1. Descarga MongoDB Community Server desde: https://www.mongodb.com/try/download/community
2. Ejecuta el instalador y sigue las instrucciones
3. Durante la instalación, marca "Install MongoDB as a Service"
4. MongoDB se iniciará automáticamente

**Opción B: Chocolatey**
```powershell
choco install mongodb
net start MongoDB
```

### macOS

```bash
brew tap mongodb/brew
brew install mongodb-community
brew services start mongodb-community
```

### Linux (Ubuntu/Debian)

```bash
sudo apt-get update
sudo apt-get install -y mongodb
sudo systemctl start mongod
sudo systemctl enable mongod
```

## Paso 2: Verificar que MongoDB esté corriendo

```bash
# Intentar conectar a MongoDB
mongosh

# Si se conecta exitosamente, verás algo como:
# Current Mongosh Log ID: ...
# Connecting to: mongodb://127.0.0.1:27017/

# Escribe 'exit' para salir
exit
```

## Paso 3: Instalar dependencias de Python

Abre una terminal en el directorio del proyecto y ejecuta:

```bash
pip install -r requirements.txt
```

Si tienes problemas con permisos:
```bash
pip install -r requirements.txt --user
```

## Paso 4: Configurar variables de entorno (Opcional)

El archivo `.env` ya está creado con la configuración por defecto:

```
MONGO_URI=mongodb://localhost:27017/
DB_NAME=crm_famago
```

Si necesitas cambiar la configuración, edita el archivo `.env`.

## Paso 5: Importar datos iniciales (Opcional)

Si tienes el archivo Excel con datos existentes:

```bash
python import_data.py
```

Este paso es opcional. Puedes empezar con la base de datos vacía y agregar clientes manualmente desde la interfaz.

## Paso 6: Iniciar el servidor

### Windows
```bash
start_server.bat
```

### Linux/macOS
```bash
chmod +x start_server.sh
./start_server.sh
```

### Manual
```bash
python app.py
```

## Paso 7: Acceder a la aplicación

Abre tu navegador y ve a: **http://localhost:5000**

¡Listo! Ya puedes usar el CRM.

---

## Solución de Problemas

### Error: "No module named 'pymongo'"

Solución: Instala las dependencias
```bash
pip install pymongo
```

### Error: "Error conectando a MongoDB"

Solución: Verifica que MongoDB esté corriendo
```bash
# Windows
net start MongoDB

# macOS
brew services start mongodb-community

# Linux
sudo systemctl start mongod
```

### Error: "Port 5000 is already in use"

Solución: Cambia el puerto en `app.py` (última línea):
```python
app.run(debug=True, host='0.0.0.0', port=8000)  # Cambiar 5000 por 8000
```

### MongoDB no se instala

Solución alternativa: Usa MongoDB Atlas (gratis)
1. Crea una cuenta en https://www.mongodb.com/cloud/atlas
2. Crea un cluster gratis
3. Obtén tu connection string
4. Actualiza el archivo `.env`:
```
MONGO_URI=mongodb+srv://usuario:contraseña@cluster.mongodb.net/?retryWrites=true&w=majority
DB_NAME=crm_famago
```

---

## Próximos Pasos

Una vez que la aplicación esté corriendo:

1. **Dashboard** - Ve las estadísticas generales
2. **Clientes** - Explora el listado (vacío si no importaste datos)
3. **Nuevo Cliente** - Agrega tu primer cliente de prueba
4. **Importar/Exportar** - Sube un archivo Excel o descarga los datos

## Comandos Útiles

```bash
# Ver si MongoDB está corriendo
# Windows: tasklist | find "mongod"
# macOS/Linux: ps aux | grep mongod

# Detener MongoDB
# Windows: net stop MongoDB
# macOS: brew services stop mongodb-community
# Linux: sudo systemctl stop mongod

# Ver los logs de la aplicación
# Los logs aparecen en la terminal donde ejecutaste app.py

# Acceder a MongoDB directamente
mongosh
use crm_famago
db.clientes.find().limit(5)
```

---

## Requisitos del Sistema

- **Python:** 3.8 o superior
- **MongoDB:** 4.4 o superior
- **RAM:** Mínimo 2GB
- **Disco:** 500MB libres
- **Navegador:** Chrome, Firefox, Edge o Safari (versiones recientes)

---

**¿Necesitas ayuda?** Revisa el archivo `README.md` para documentación completa.
