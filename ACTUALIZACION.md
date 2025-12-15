# =€ Guía de Actualización en Producción

Esta guía te muestra cómo actualizar tu aplicación en el VPS después de hacer cambios en el código.

## =Ë Tabla de Contenidos

1. [Opción Rápida (Script Automático)](#opción-1-script-automático-recomendado)
2. [Opción Manual (Paso a Paso)](#opción-2-manual-paso-a-paso)
3. [Comandos Útiles](#comandos-útiles)
4. [Solución de Problemas](#solución-de-problemas)

---

## Opción 1: Script Automático (RECOMENDADO)

### Desde tu PC Local

```bash
# 1. Agregar cambios
git add .

# 2. Crear commit
git commit -m "Descripción de tus cambios"

# 3. Subir al repositorio
git push origin main

# 4. Conectarse al VPS
ssh root@TU_IP_DEL_VPS
# o si usas otro usuario:
ssh tu_usuario@TU_IP_DEL_VPS
```

### En el VPS

```bash
# 1. Ir al directorio del proyecto
cd /root/Gestion-de-Ventas-App

# 2. Ejecutar script de actualización
bash update.sh
```

**¡Listo!** El script automáticamente:
-  Descarga los últimos cambios con `git pull`
-  Crea backup de la base de datos
-  Actualiza las dependencias de Python
-  Reinicia el servicio
-  Limpia caché de Python
-  Verifica que todo funcione

---

## Opción 2: Manual (Paso a Paso)

### 1ã Desde tu PC Local

```bash
# Ver archivos modificados
git status

# Agregar todos los cambios
git add .

# O agregar archivos específicos
git add templates/index.html
git add app.py

# Crear commit con mensaje descriptivo
git commit -m "Fix: Corregir edición de clientes"

# Subir cambios al repositorio
git push origin main
```

### 2ã Conectarse al VPS

```bash
# Conectar por SSH
ssh root@TU_IP_DEL_VPS

# Si usas un puerto específico
ssh -p PUERTO root@TU_IP_DEL_VPS
```

### 3ã En el VPS - Actualizar Código

```bash
# Ir al directorio del proyecto
cd /root/Gestion-de-Ventas-App

# Verificar estado actual
git status

# Descargar últimos cambios
git pull origin main
```

### 4ã Actualizar Dependencias (solo si cambiaron)

```bash
# Si modificaste requirements.txt, actualizar dependencias
source venv/bin/activate
pip install -r requirements.txt --upgrade
```

### 5ã Reiniciar el Servicio

```bash
# Reiniciar la aplicación
sudo systemctl restart gestion-ventas

# Verificar que se reinició correctamente
sudo systemctl status gestion-ventas

# Debería mostrar: "Active: active (running)"
```

### 6ã Verificar Logs (Opcional)

```bash
# Ver logs en tiempo real
sudo journalctl -u gestion-ventas -f

# Presiona Ctrl+C para salir

# Ver últimos 50 logs
sudo journalctl -u gestion-ventas -n 50
```

### 7ã Salir del VPS

```bash
exit
```

---

## =à Comandos Útiles

### Gestión del Servicio

```bash
# Ver estado del servicio
sudo systemctl status gestion-ventas

# Reiniciar servicio
sudo systemctl restart gestion-ventas

# Detener servicio
sudo systemctl stop gestion-ventas

# Iniciar servicio
sudo systemctl start gestion-ventas

# Recargar configuración
sudo systemctl daemon-reload
```

### Ver Logs

```bash
# Ver logs en tiempo real (live)
sudo journalctl -u gestion-ventas -f

# Ver últimos 50 logs
sudo journalctl -u gestion-ventas -n 50

# Ver últimos 100 logs
sudo journalctl -u gestion-ventas -n 100

# Ver logs con fecha específica
sudo journalctl -u gestion-ventas --since "2024-01-15 14:00"

# Ver logs de hoy
sudo journalctl -u gestion-ventas --since today
```

### Git

```bash
# Ver estado
git status

# Ver últimos commits
git log --oneline -5

# Ver diferencias
git diff

# Descartar cambios locales
git reset --hard origin/main
```

### Nginx

```bash
# Estado de Nginx
sudo systemctl status nginx

# Reiniciar Nginx
sudo systemctl restart nginx

# Ver logs de error de Nginx
sudo tail -f /var/log/nginx/error.log

# Ver logs de acceso de Nginx
sudo tail -f /var/log/nginx/access.log
```

### MongoDB

```bash
# Estado de MongoDB
sudo systemctl status mongod

# Reiniciar MongoDB
sudo systemctl restart mongod

# Conectarse a MongoDB
mongo

# O con mongosh (versiones nuevas)
mongosh
```

---

## =' Solución de Problemas

### El servicio no inicia después de actualizar

```bash
# 1. Ver los logs para identificar el error
sudo journalctl -u gestion-ventas -n 50

# 2. Verificar que el entorno virtual está activo
cd /root/Gestion-de-Ventas-App
source venv/bin/activate

# 3. Probar correr la app manualmente
python app.py

# Si hay error de dependencias:
pip install -r requirements.txt --upgrade
```

### Error de permisos

```bash
# Asegurarse de que los archivos tengan los permisos correctos
sudo chown -R root:root /root/Gestion-de-Ventas-App

# Dar permisos de ejecución al script
chmod +x update.sh
```

### Git pull falla por conflictos

```bash
# Ver qué archivos tienen conflictos
git status

# Opción 1: Descartar cambios locales y usar versión remota
git reset --hard origin/main
git pull origin main

# Opción 2: Guardar cambios locales temporalmente
git stash
git pull origin main
git stash pop  # Esto puede crear conflictos que debes resolver manualmente
```

### Nginx muestra 502 Bad Gateway

```bash
# Verificar que el servicio Python está corriendo
sudo systemctl status gestion-ventas

# Si no está corriendo, iniciarlo
sudo systemctl start gestion-ventas

# Verificar que está escuchando en el puerto 5000
sudo netstat -tlnp | grep 5000

# Revisar configuración de Nginx
sudo nginx -t

# Si hay errores, reiniciar Nginx
sudo systemctl restart nginx
```

### La base de datos no tiene datos

```bash
# Verificar que MongoDB está corriendo
sudo systemctl status mongod

# Conectarse a MongoDB y verificar
mongosh
use crm_famago
db.clientes.count()
exit
```

### Error "Cannot connect to MongoDB"

```bash
# Verificar que MongoDB está corriendo
sudo systemctl status mongod

# Si no está corriendo
sudo systemctl start mongod

# Verificar configuración en .env
cat .env

# Debería mostrar:
# MONGO_URI=mongodb://localhost:27017/
# DB_NAME=crm_famago
```

---

## =Ý Checklist de Actualización

Antes de actualizar en producción, verifica:

- [ ] Los cambios funcionan correctamente en tu entorno local
- [ ] Has hecho commit de todos los cambios
- [ ] Has hecho push al repositorio
- [ ] Tienes acceso SSH al VPS
- [ ] (Opcional) Has creado un backup de la base de datos

Después de actualizar:

- [ ] El servicio se reinició correctamente
- [ ] Los logs no muestran errores
- [ ] La aplicación responde en el navegador
- [ ] La funcionalidad actualizada funciona correctamente

---

## <¯ Resumen Rápido

**Flujo completo de actualización:**

1. **Local**: `git add . && git commit -m "mensaje" && git push`
2. **VPS**: `ssh root@IP`
3. **VPS**: `cd /root/Gestion-de-Ventas-App`
4. **VPS**: `bash update.sh`
5. **Verificar**: Abrir navegador y probar

**Tiempo estimado**: 2-5 minutos

---

## =Þ Contacto

Si encuentras problemas que no puedes resolver con esta guía:

1. Revisa los logs: `sudo journalctl -u gestion-ventas -n 100`
2. Verifica que todos los servicios estén activos
3. Intenta reiniciar todos los servicios:
   ```bash
   sudo systemctl restart gestion-ventas
   sudo systemctl restart nginx
   sudo systemctl restart mongod
   ```

---

**Última actualización**: 2025-12-15
