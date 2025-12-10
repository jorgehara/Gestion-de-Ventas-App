# Guía de Deployment en VPS - CRM Famago

Esta guía te ayudará a desplegar la aplicación en un VPS (Ubuntu/Debian) en producción.

## 📋 Requisitos Previos

- VPS con Ubuntu 20.04+ o Debian 11+
- Acceso root o sudo
- Dominio apuntando a tu VPS (opcional pero recomendado)
- Mínimo 1GB RAM, 1 CPU, 10GB disco

---

## Paso 1: Preparar el VPS

### 1.1 Conectarse al VPS

```bash
ssh root@tu-vps-ip
# O si tienes usuario con sudo:
ssh usuario@tu-vps-ip
```

### 1.2 Actualizar el sistema

```bash
sudo apt update && sudo apt upgrade -y
```

### 1.3 Instalar dependencias básicas

```bash
sudo apt install -y git curl wget nano ufw
```

---

## Paso 2: Instalar Python 3

```bash
# Verificar versión de Python
python3 --version

# Si no está instalado o es menor a 3.8:
sudo apt install -y python3 python3-pip python3-venv
```

---

## Paso 3: Instalar MongoDB

### 3.1 Importar la clave pública de MongoDB

```bash
curl -fsSL https://www.mongodb.org/static/pgp/server-7.0.asc | \
   sudo gpg -o /usr/share/keyrings/mongodb-server-7.0.gpg --dearmor
```

### 3.2 Crear el archivo de lista de fuentes

**Ubuntu 22.04:**
```bash
echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-7.0.gpg ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list
```

**Ubuntu 20.04:**
```bash
echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-7.0.gpg ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/7.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list
```

### 3.3 Instalar MongoDB

```bash
sudo apt update
sudo apt install -y mongodb-org
```

### 3.4 Iniciar y habilitar MongoDB

```bash
sudo systemctl start mongod
sudo systemctl enable mongod
sudo systemctl status mongod
```

---

## Paso 4: Configurar MongoDB Seguro

### 4.1 Crear usuario administrador

```bash
mongosh
```

Dentro de mongosh:
```javascript
use admin
db.createUser({
  user: "admin",
  pwd: "TuPasswordSeguro123!",
  roles: ["userAdminAnyDatabase", "readWriteAnyDatabase"]
})
exit
```

### 4.2 Crear usuario para la aplicación

```bash
mongosh
```

```javascript
use crm_famago
db.createUser({
  user: "crm_user",
  pwd: "PasswordSeguroDelCRM456!",
  roles: [{role: "readWrite", db: "crm_famago"}]
})
exit
```

### 4.3 Habilitar autenticación

```bash
sudo nano /etc/mongod.conf
```

Busca la sección `security` y modifícala:
```yaml
security:
  authorization: enabled
```

Reinicia MongoDB:
```bash
sudo systemctl restart mongod
```

---

## Paso 5: Clonar el Proyecto

### 5.1 Crear directorio para aplicaciones

```bash
sudo mkdir -p /var/www
cd /var/www
```

### 5.2 Clonar desde Git (si tienes repo)

```bash
sudo git clone https://github.com/tu-usuario/crm-famago.git
cd crm-famago
```

### 5.3 O subir archivos manualmente

Desde tu PC local:
```bash
# Comprimir el proyecto
tar -czf crm-famago.tar.gz Gestion-de-Ventas-App/

# Subir al VPS
scp crm-famago.tar.gz usuario@tu-vps-ip:/var/www/

# En el VPS, descomprimir
cd /var/www
sudo tar -xzf crm-famago.tar.gz
sudo mv Gestion-de-Ventas-App crm-famago
```

### 5.4 Establecer permisos

```bash
sudo chown -R $USER:$USER /var/www/crm-famago
cd /var/www/crm-famago
```

---

## Paso 6: Configurar el Entorno Python

### 6.1 Crear entorno virtual

```bash
python3 -m venv venv
source venv/bin/activate
```

### 6.2 Instalar dependencias

```bash
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn
```

---

## Paso 7: Configurar Variables de Entorno

### 7.1 Crear archivo .env de producción

```bash
nano .env
```

Contenido:
```bash
# MongoDB Producción
MONGO_URI=mongodb://crm_user:PasswordSeguroDelCRM456!@localhost:27017/crm_famago?authSource=crm_famago
DB_NAME=crm_famago

# Flask
FLASK_ENV=production
SECRET_KEY=tu-clave-secreta-super-larga-y-aleatoria-123456789
```

### 7.2 Proteger el archivo .env

```bash
chmod 600 .env
```

---

## Paso 8: Modificar app.py para Producción

### 8.1 Editar app.py

```bash
nano app.py
```

Cambia la última línea de:
```python
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
```

A:
```python
if __name__ == '__main__':
    app.run(debug=False, host='127.0.0.1', port=5000)
```

---

## Paso 9: Instalar y Configurar Gunicorn

### 9.1 Crear archivo wsgi.py

```bash
nano wsgi.py
```

Contenido:
```python
from app import app

if __name__ == "__main__":
    app.run()
```

### 9.2 Probar Gunicorn

```bash
gunicorn --bind 127.0.0.1:5000 wsgi:app
```

Si funciona, presiona Ctrl+C para detenerlo.

---

## Paso 10: Crear Servicio Systemd

### 10.1 Crear archivo de servicio

```bash
sudo nano /etc/systemd/system/crm-famago.service
```

Contenido:
```ini
[Unit]
Description=CRM Famago - Gunicorn
After=network.target mongod.service

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/crm-famago
Environment="PATH=/var/www/crm-famago/venv/bin"
ExecStart=/var/www/crm-famago/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:5000 wsgi:app --access-logfile /var/log/crm-famago/access.log --error-logfile /var/log/crm-famago/error.log

[Install]
WantedBy=multi-user.target
```

### 10.2 Crear directorio para logs

```bash
sudo mkdir -p /var/log/crm-famago
sudo chown -R www-data:www-data /var/log/crm-famago
```

### 10.3 Ajustar permisos del proyecto

```bash
sudo chown -R www-data:www-data /var/www/crm-famago
```

### 10.4 Iniciar y habilitar el servicio

```bash
sudo systemctl daemon-reload
sudo systemctl start crm-famago
sudo systemctl enable crm-famago
sudo systemctl status crm-famago
```

---

## Paso 11: Instalar y Configurar Nginx

### 11.1 Instalar Nginx

```bash
sudo apt install -y nginx
```

### 11.2 Crear configuración del sitio

```bash
sudo nano /etc/nginx/sites-available/crm-famago
```

Contenido:
```nginx
server {
    listen 80;
    server_name tu-dominio.com www.tu-dominio.com;
    # O si no tienes dominio, usa tu IP:
    # server_name tu-vps-ip;

    # Logs
    access_log /var/log/nginx/crm-famago-access.log;
    error_log /var/log/nginx/crm-famago-error.log;

    # Proxy a Gunicorn
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Timeouts
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
    }

    # Archivos estáticos (si los agregas en el futuro)
    location /static {
        alias /var/www/crm-famago/static;
        expires 30d;
    }

    # Aumentar tamaño máximo de upload para Excel
    client_max_body_size 20M;
}
```

### 11.3 Habilitar el sitio

```bash
sudo ln -s /etc/nginx/sites-available/crm-famago /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## Paso 12: Configurar Firewall

```bash
# Habilitar UFW
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw enable
sudo ufw status
```

---

## Paso 13: Configurar SSL con Let's Encrypt (Opcional pero Recomendado)

### 13.1 Instalar Certbot

```bash
sudo apt install -y certbot python3-certbot-nginx
```

### 13.2 Obtener certificado SSL

```bash
sudo certbot --nginx -d tu-dominio.com -d www.tu-dominio.com
```

Sigue las instrucciones. Certbot configurará automáticamente Nginx para usar HTTPS.

### 13.3 Renovación automática

```bash
sudo systemctl status certbot.timer
```

---

## Paso 14: Importar Datos Iniciales (Opcional)

### 14.1 Subir archivo Excel al VPS

Desde tu PC:
```bash
scp "Famago 1.9.1 - copia.xlsx" usuario@tu-vps-ip:/var/www/crm-famago/
```

### 14.2 Importar datos

En el VPS:
```bash
cd /var/www/crm-famago
source venv/bin/activate
python import_data.py
```

---

## Paso 15: Verificar el Deployment

### 15.1 Verificar servicios

```bash
sudo systemctl status mongod
sudo systemctl status crm-famago
sudo systemctl status nginx
```

### 15.2 Ver logs

```bash
# Logs de la aplicación
sudo tail -f /var/log/crm-famago/error.log

# Logs de Nginx
sudo tail -f /var/log/nginx/crm-famago-error.log

# Logs de systemd
sudo journalctl -u crm-famago -f
```

### 15.3 Acceder a la aplicación

Abre tu navegador:
- Con dominio: `https://tu-dominio.com`
- Sin dominio: `http://tu-vps-ip`

---

## 🔐 Seguridad Adicional

### Configurar fail2ban

```bash
sudo apt install -y fail2ban
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

### Cambiar puerto SSH (opcional)

```bash
sudo nano /etc/ssh/sshd_config
# Cambiar: Port 22
# Por: Port 2222
sudo systemctl restart sshd

# Actualizar firewall
sudo ufw allow 2222/tcp
sudo ufw delete allow OpenSSH
```

### Deshabilitar login root

```bash
sudo nano /etc/ssh/sshd_config
# Cambiar: PermitRootLogin yes
# Por: PermitRootLogin no
sudo systemctl restart sshd
```

---

## 📊 Monitoreo

### Instalar htop

```bash
sudo apt install -y htop
htop
```

### Verificar uso de recursos

```bash
# CPU y memoria
free -h
df -h

# Procesos de la app
ps aux | grep gunicorn

# Conexiones MongoDB
mongosh --authenticationDatabase admin -u admin -p
use crm_famago
db.currentOp()
```

---

## 🔄 Actualizaciones Futuras

### Script de actualización

Crea `update.sh`:
```bash
nano /var/www/crm-famago/update.sh
```

Contenido:
```bash
#!/bin/bash
cd /var/www/crm-famago

# Backup de datos
mongodump --uri="mongodb://crm_user:PasswordSeguroDelCRM456!@localhost:27017/crm_famago?authSource=crm_famago" --out=./backup-$(date +%Y%m%d)

# Actualizar código (si usas Git)
git pull origin main

# Actualizar dependencias
source venv/bin/activate
pip install -r requirements.txt

# Reiniciar servicio
sudo systemctl restart crm-famago

echo "✅ Actualización completada"
```

Dar permisos:
```bash
chmod +x update.sh
```

---

## 🗄️ Backup Automático

### Script de backup

```bash
sudo nano /usr/local/bin/backup-crm.sh
```

Contenido:
```bash
#!/bin/bash
BACKUP_DIR="/var/backups/crm-famago"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup MongoDB
mongodump --uri="mongodb://crm_user:PasswordSeguroDelCRM456!@localhost:27017/crm_famago?authSource=crm_famago" --out=$BACKUP_DIR/mongo-$DATE

# Comprimir
cd $BACKUP_DIR
tar -czf mongo-$DATE.tar.gz mongo-$DATE
rm -rf mongo-$DATE

# Eliminar backups antiguos (más de 7 días)
find $BACKUP_DIR -name "mongo-*.tar.gz" -mtime +7 -delete

echo "✅ Backup completado: $BACKUP_DIR/mongo-$DATE.tar.gz"
```

Dar permisos:
```bash
sudo chmod +x /usr/local/bin/backup-crm.sh
```

### Configurar cron para backup diario

```bash
sudo crontab -e
```

Agregar:
```
0 2 * * * /usr/local/bin/backup-crm.sh >> /var/log/crm-famago/backup.log 2>&1
```

---

## 🐛 Troubleshooting

### La aplicación no inicia

```bash
# Ver logs detallados
sudo journalctl -u crm-famago -n 50

# Verificar que MongoDB esté corriendo
sudo systemctl status mongod

# Probar manualmente
cd /var/www/crm-famago
source venv/bin/activate
python app.py
```

### Nginx muestra 502 Bad Gateway

```bash
# Verificar que Gunicorn esté corriendo
sudo systemctl status crm-famago

# Verificar que esté escuchando en el puerto correcto
sudo netstat -tlnp | grep 5000

# Reiniciar servicios
sudo systemctl restart crm-famago
sudo systemctl restart nginx
```

### Error de conexión a MongoDB

```bash
# Verificar autenticación
mongosh --authenticationDatabase crm_famago -u crm_user -p

# Verificar la URI en .env
cat /var/www/crm-famago/.env
```

---

## 📝 Comandos Útiles

```bash
# Reiniciar aplicación
sudo systemctl restart crm-famago

# Ver logs en tiempo real
sudo journalctl -u crm-famago -f

# Verificar estado de todos los servicios
sudo systemctl status mongod nginx crm-famago

# Reiniciar todos los servicios
sudo systemctl restart mongod nginx crm-famago

# Backup manual
sudo /usr/local/bin/backup-crm.sh

# Verificar espacio en disco
df -h

# Ver procesos de la app
ps aux | grep gunicorn
```

---

## ✅ Checklist Final

- [ ] VPS actualizado
- [ ] Python 3.8+ instalado
- [ ] MongoDB instalado y corriendo
- [ ] MongoDB con autenticación configurada
- [ ] Usuario de MongoDB para la app creado
- [ ] Proyecto clonado/subido a /var/www/crm-famago
- [ ] Entorno virtual creado y activado
- [ ] Dependencias instaladas (incluyendo gunicorn)
- [ ] Archivo .env configurado con credenciales correctas
- [ ] wsgi.py creado
- [ ] Servicio systemd creado y habilitado
- [ ] Nginx instalado y configurado
- [ ] Firewall configurado (UFW)
- [ ] SSL configurado (si tienes dominio)
- [ ] Datos importados (opcional)
- [ ] Backup automático configurado
- [ ] Aplicación accesible desde el navegador

---

**¡Tu aplicación está en producción!** 🎉

Accede a: `https://tu-dominio.com` o `http://tu-vps-ip`
