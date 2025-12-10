# Deploy Rápido - VPS Ya Configurado

Guía rápida para subir el proyecto a un VPS que ya tiene todo instalado.

## 📦 Paso 1: Preparar el Proyecto para Subir

En tu PC local:

```bash
cd "C:\Users\JorgeHaraDevs\Desktop\Gestion-de-Ventas-App"

# Crear archivo wsgi.py si no existe
echo "from app import app

if __name__ == '__main__':
    app.run()" > wsgi.py

# Agregar gunicorn a requirements.txt si no está
echo "gunicorn==21.2.0" >> requirements.txt
```

## 📤 Paso 2: Comprimir y Subir al VPS

### Opción A: Usando SCP (recomendado)

En tu PC:
```bash
# Comprimir el proyecto (excluyendo archivos innecesarios)
tar -czf crm-famago.tar.gz \
  --exclude='*.db' \
  --exclude='__pycache__' \
  --exclude='venv' \
  --exclude='.git' \
  Gestion-de-Ventas-App/

# Subir al VPS
scp crm-famago.tar.gz usuario@tu-vps-ip:/tmp/
```

### Opción B: Usando Git

Si tu proyecto está en GitHub:
```bash
# En el VPS
git clone https://github.com/tu-usuario/crm-famago.git /var/www/crm-famago
```

## 🖥️ Paso 3: En el VPS - Descomprimir y Configurar

Conéctate al VPS:
```bash
ssh usuario@tu-vps-ip
```

Luego ejecuta:
```bash
# Ir al directorio web
cd /var/www

# Descomprimir
sudo tar -xzf /tmp/crm-famago.tar.gz
sudo mv Gestion-de-Ventas-App crm-famago

# Establecer permisos
sudo chown -R www-data:www-data /var/www/crm-famago
cd /var/www/crm-famago
```

## 🐍 Paso 4: Configurar Entorno Python

```bash
cd /var/www/crm-famago

# Crear entorno virtual
python3 -m venv venv

# Activar entorno virtual
source venv/bin/activate

# Actualizar pip
pip install --upgrade pip

# Instalar dependencias
pip install -r requirements.txt
```

## ⚙️ Paso 5: Configurar Variables de Entorno

```bash
cd /var/www/crm-famago
nano .env
```

Contenido:
```bash
# MongoDB (ajusta según tu configuración)
MONGO_URI=mongodb://usuario:password@localhost:27017/crm_famago?authSource=crm_famago
DB_NAME=crm_famago

# Flask
FLASK_ENV=production
SECRET_KEY=genera-una-clave-secreta-larga-123456789
```

Proteger el archivo:
```bash
chmod 600 .env
```

## 🔧 Paso 6: Crear wsgi.py

Si no lo creaste antes:
```bash
nano wsgi.py
```

Contenido:
```python
from app import app

if __name__ == "__main__":
    app.run()
```

## 🚀 Paso 7: Crear Servicio Systemd

```bash
sudo nano /etc/systemd/system/crm-famago.service
```

Contenido:
```ini
[Unit]
Description=CRM Famago
After=network.target mongod.service

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/crm-famago
Environment="PATH=/var/www/crm-famago/venv/bin"
ExecStart=/var/www/crm-famago/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:5000 wsgi:app

[Install]
WantedBy=multi-user.target
```

Iniciar el servicio:
```bash
sudo systemctl daemon-reload
sudo systemctl start crm-famago
sudo systemctl enable crm-famago
sudo systemctl status crm-famago
```

## 🌐 Paso 8: Configurar Nginx

```bash
sudo nano /etc/nginx/sites-available/crm-famago
```

Contenido:
```nginx
server {
    listen 80;
    server_name tu-dominio.com;  # O tu IP

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    client_max_body_size 20M;
}
```

Habilitar el sitio:
```bash
sudo ln -s /etc/nginx/sites-available/crm-famago /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## 📊 Paso 9: Importar Datos (Opcional)

Si tienes el archivo Excel:

```bash
# Subir archivo desde tu PC
scp "Famago 1.9.1 - copia.xlsx" usuario@tu-vps-ip:/var/www/crm-famago/

# En el VPS
cd /var/www/crm-famago
source venv/bin/activate
python import_data.py
```

## ✅ Paso 10: Verificar

```bash
# Ver estado del servicio
sudo systemctl status crm-famago

# Ver logs
sudo journalctl -u crm-famago -f

# Probar en el navegador
curl http://localhost:5000
```

Accede desde tu navegador: `http://tu-dominio.com` o `http://tu-vps-ip`

---

## 🔄 Comandos Útiles para Actualizaciones Futuras

```bash
# Subir cambios
scp -r Gestion-de-Ventas-App/* usuario@tu-vps-ip:/var/www/crm-famago/

# En el VPS, reiniciar
sudo systemctl restart crm-famago
```

## 🐛 Si algo no funciona

```bash
# Ver logs de la aplicación
sudo journalctl -u crm-famago -n 50

# Ver logs de Nginx
sudo tail -f /var/log/nginx/error.log

# Verificar que MongoDB esté corriendo
sudo systemctl status mongod

# Verificar que el puerto 5000 esté en uso
sudo netstat -tlnp | grep 5000

# Reiniciar todo
sudo systemctl restart crm-famago nginx
```

---

## 📋 Resumen de Rutas

- **Proyecto:** `/var/www/crm-famago`
- **Entorno virtual:** `/var/www/crm-famago/venv`
- **Templates:** `/var/www/crm-famago/templates/index.html`
- **Config Nginx:** `/etc/nginx/sites-available/crm-famago`
- **Servicio systemd:** `/etc/systemd/system/crm-famago.service`
- **Variables de entorno:** `/var/www/crm-famago/.env`

---

**¡Listo!** Tu aplicación debe estar corriendo en producción 🎉
