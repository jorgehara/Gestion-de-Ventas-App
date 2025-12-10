# 🚀 Resumen: Deploy a VPS Ya Configurado

## Archivos Listos para Deploy

Tu proyecto ahora incluye:
- ✅ `wsgi.py` - Entry point para Gunicorn
- ✅ `deploy.sh` - Script automático de deployment
- ✅ `update.sh` - Script de actualización
- ✅ `upload_to_vps.bat` - Script Windows para subir archivos
- ✅ `requirements.txt` - Con gunicorn incluido

---

## 🎯 3 Pasos para Deploy

### Opción 1: Deploy Automático (Recomendado)

#### Desde Windows (tu PC):

1. **Subir archivos al VPS**
   ```cmd
   upload_to_vps.bat
   ```
   - Ingresa la IP del VPS
   - Ingresa tu usuario SSH
   - El script comprimirá y subirá todo automáticamente

2. **Conectarse al VPS**
   ```bash
   ssh usuario@tu-vps-ip
   ```

3. **Ejecutar script de deployment**
   ```bash
   cd /var/www/crm-famago
   chmod +x deploy.sh
   sudo ./deploy.sh
   ```

El script configurará automáticamente:
- ✅ Entorno virtual de Python
- ✅ Instalación de dependencias
- ✅ Servicio systemd
- ✅ Nginx
- ✅ Logs
- ✅ Permisos

**¡Listo!** Tu aplicación estará corriendo.

---

### Opción 2: Deploy Manual

Si prefieres hacerlo paso a paso:

1. **Comprimir proyecto** (en tu PC)
   ```bash
   tar -czf crm-famago.tar.gz --exclude=*.db --exclude=venv --exclude=.git .
   ```

2. **Subir al VPS**
   ```bash
   scp crm-famago.tar.gz usuario@tu-vps-ip:/tmp/
   ```

3. **En el VPS**
   ```bash
   # Descomprimir
   cd /var/www
   sudo tar -xzf /tmp/crm-famago.tar.gz
   cd crm-famago

   # Crear entorno virtual
   python3 -m venv venv
   source venv/bin/activate

   # Instalar dependencias
   pip install -r requirements.txt

   # Configurar .env
   nano .env
   # Edita las credenciales de MongoDB

   # Crear servicio systemd
   sudo nano /etc/systemd/system/crm-famago.service
   # Copia el contenido de DEPLOY_RAPIDO.md

   # Iniciar servicio
   sudo systemctl daemon-reload
   sudo systemctl start crm-famago
   sudo systemctl enable crm-famago

   # Configurar Nginx
   sudo nano /etc/nginx/sites-available/crm-famago
   # Copia el contenido de DEPLOY_RAPIDO.md

   # Habilitar sitio
   sudo ln -s /etc/nginx/sites-available/crm-famago /etc/nginx/sites-enabled/
   sudo systemctl reload nginx
   ```

---

## 📝 Configuración Requerida

### Archivo .env (en el VPS)

```bash
MONGO_URI=mongodb://usuario:password@localhost:27017/crm_famago?authSource=crm_famago
DB_NAME=crm_famago
FLASK_ENV=production
SECRET_KEY=tu-clave-secreta-muy-larga-123456789
```

### Credenciales MongoDB

Si aún no tienes usuario en MongoDB:
```bash
mongosh
use crm_famago
db.createUser({
  user: "crm_user",
  pwd: "TuPasswordSeguro123!",
  roles: [{role: "readWrite", db: "crm_famago"}]
})
exit
```

---

## 🔄 Actualizaciones Futuras

Cuando hagas cambios en el código:

1. **Subir cambios al VPS**
   ```bash
   scp -r * usuario@tu-vps-ip:/var/www/crm-famago/
   ```

2. **Ejecutar script de actualización**
   ```bash
   ssh usuario@tu-vps-ip
   cd /var/www/crm-famago
   chmod +x update.sh
   ./update.sh
   ```

O manualmente:
```bash
sudo systemctl restart crm-famago
```

---

## ✅ Verificación

Una vez desplegado:

1. **Verificar servicios**
   ```bash
   sudo systemctl status crm-famago
   sudo systemctl status mongod
   sudo systemctl status nginx
   ```

2. **Ver logs**
   ```bash
   sudo journalctl -u crm-famago -f
   ```

3. **Acceder desde el navegador**
   - Con dominio: `http://tu-dominio.com`
   - Con IP: `http://tu-vps-ip`

---

## 🐛 Solución de Problemas

### Servicio no inicia
```bash
sudo journalctl -u crm-famago -n 50
```

### Error de MongoDB
```bash
sudo systemctl status mongod
mongosh --eval "db.adminCommand('ping')"
```

### Error 502 en Nginx
```bash
# Verificar que Gunicorn esté corriendo
sudo systemctl status crm-famago

# Verificar puerto
sudo netstat -tlnp | grep 5000
```

### Reiniciar todo
```bash
sudo systemctl restart mongod
sudo systemctl restart crm-famago
sudo systemctl restart nginx
```

---

## 📦 Estructura en el VPS

```
/var/www/crm-famago/
├── app.py
├── wsgi.py                    ← Entry point
├── import_data.py
├── templates/
│   └── index.html
├── venv/                      ← Entorno virtual
├── requirements.txt
├── .env                       ← Configuración
├── deploy.sh                  ← Script de deployment
└── update.sh                  ← Script de actualización

/etc/systemd/system/
└── crm-famago.service         ← Servicio systemd

/etc/nginx/sites-available/
└── crm-famago                 ← Configuración Nginx

/var/log/crm-famago/
├── access.log
└── error.log
```

---

## 🎯 Comandos Útiles

```bash
# Ver estado
sudo systemctl status crm-famago

# Reiniciar app
sudo systemctl restart crm-famago

# Ver logs en tiempo real
sudo journalctl -u crm-famago -f

# Ver logs de Nginx
sudo tail -f /var/log/nginx/error.log

# Backup MongoDB
mongodump --db crm_famago --out ./backup-$(date +%Y%m%d)

# Verificar uso de recursos
htop
free -h
df -h
```

---

## 📚 Documentación Completa

- `DEPLOY_VPS.md` - Guía completa desde cero
- `DEPLOY_RAPIDO.md` - Guía rápida con VPS configurado
- `INSTALACION.md` - Instalación local
- `README.md` - Documentación general

---

## ✨ ¡Todo Listo!

Tu aplicación CRM Famago está preparada para producción con:
- ✅ Servidor WSGI (Gunicorn)
- ✅ Reverse proxy (Nginx)
- ✅ Servicio systemd (auto-inicio)
- ✅ Logs configurados
- ✅ Scripts de deployment y actualización
- ✅ Seguridad básica

**Siguiente paso:** Ejecuta `upload_to_vps.bat` y luego `deploy.sh` en el VPS.
