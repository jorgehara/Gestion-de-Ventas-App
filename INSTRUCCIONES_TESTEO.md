# Instrucciones para Testear la Importación de PDF

## 📋 Resumen del Problema

Cuando intentas importar un PDF en el VPS, obtienes el error:
```
Error al importar PDF: Failed to fetch
```

Este error significa que el **navegador no pudo comunicarse con el servidor** para completar la importación del PDF.

---

## ✅ Solución en 3 Pasos

### Paso 1: Testear en Localhost (OPCIONAL)

Si quieres verificar que el código funciona en tu PC local primero:

1. **Iniciar MongoDB** (si no está corriendo):
   - En Windows: Abre "Servicios" → Busca "MongoDB" → Click derecho → Iniciar
   - O ejecuta como administrador: `net start MongoDB`

2. **Iniciar el servidor Flask**:
   ```bash
   cd "C:\Users\JorgeHaraDevs\Desktop\Gestion-de-Ventas-App"
   python app.py
   ```

3. **Probar la importación**:
   - Abre el navegador en: http://localhost:5000
   - Ve a la pestaña **Cálculos**
   - Click en **📄 Importar PDF**
   - Selecciona un PDF de lista de precios
   - Verifica que funcione

**Si funciona en localhost pero NO en el VPS**, el problema está en la configuración del VPS (continúa con Paso 2).

---

### Paso 2: Aplicar Soluciones en el VPS

El problema en el VPS es por **timeouts** y **tamaño de archivo**. Sigue estos pasos:

#### 2.1 Conectarte al VPS

```bash
ssh usuario@tu-vps-ip
```

#### 2.2 Instalar pdfplumber (si no está instalado)

```bash
cd /var/www/crm-famago
source venv/bin/activate
pip install pdfplumber
```

#### 2.3 Crear directorio 'uploads' con permisos

```bash
cd /var/www/crm-famago
mkdir -p uploads
sudo chown www-data:www-data uploads
sudo chmod 755 uploads
```

#### 2.4 Configurar Nginx (IMPORTANTE)

Edita la configuración de Nginx:

```bash
sudo nano /etc/nginx/sites-available/crm-famago
```

**BUSCA** la sección `location /` y **MODIFÍCALA** para que se vea así:

```nginx
location / {
    proxy_pass http://127.0.0.1:5000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;

    # TIMEOUTS AUMENTADOS (para procesar PDFs grandes)
    proxy_connect_timeout 600s;
    proxy_send_timeout 600s;
    proxy_read_timeout 600s;

    proxy_request_buffering off;
}
```

**TAMBIÉN BUSCA** la línea `client_max_body_size` o agrégala dentro del bloque `server`:

```nginx
server {
    listen 80;
    server_name tu-dominio.com;

    # TAMAÑO MÁXIMO DE ARCHIVO (50MB)
    client_max_body_size 50M;
    client_body_timeout 300s;

    # ... resto de la configuración
}
```

**Guardar**: Ctrl+O → Enter → Ctrl+X

**Verificar sintaxis**:
```bash
sudo nginx -t
```

Si dice "syntax is ok", reinicia Nginx:
```bash
sudo systemctl restart nginx
```

#### 2.5 Configurar Gunicorn

Edita el servicio:

```bash
sudo nano /etc/systemd/system/crm-famago.service
```

**BUSCA** la línea `ExecStart` y **AGREGA** `--timeout 600`:

```ini
ExecStart=/var/www/crm-famago/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:5000 --timeout 600 wsgi:app --access-logfile /var/log/crm-famago/access.log --error-logfile /var/log/crm-famago/error.log
```

**Guardar** (Ctrl+O → Enter → Ctrl+X) y reiniciar:

```bash
sudo systemctl daemon-reload
sudo systemctl restart crm-famago
```

#### 2.6 Verificar que todo esté corriendo

```bash
sudo systemctl status crm-famago
sudo systemctl status nginx
```

Ambos deben mostrar "active (running)" en verde.

---

### Paso 3: Probar la Importación

1. Abre tu aplicación en el navegador (tu dominio o IP del VPS)
2. Ve a la pestaña **Cálculos**
3. Click en **📄 Importar PDF**
4. Selecciona un PDF de lista de precios
5. Espera unos segundos (puede tardar)
6. **Debería mostrar**: "✓ Importación completada: X productos nuevos creados..."

---

## 🔍 Si Sigue sin Funcionar

### Ver los logs de error

```bash
# Ver últimos errores de la aplicación
sudo tail -50 /var/log/crm-famago/error.log

# Ver errores de Nginx
sudo tail -50 /var/log/nginx/crm-famago-error.log

# Ver logs del sistema
sudo journalctl -u crm-famago -n 50
```

### Verificar memoria y espacio

```bash
# Memoria disponible
free -h

# Espacio en disco
df -h
```

### Probar con un PDF pequeño

Si tienes un PDF muy grande (>10MB), intenta con uno más pequeño primero para descartar problemas de memoria.

---

## 📊 Script de Verificación Rápida

Ejecuta este comando en el VPS para verificar todo:

```bash
echo "=== VERIFICACIÓN CRM ==="
echo ""
echo "1. Directorio uploads:"
ls -la /var/www/crm-famago/uploads/ 2>/dev/null || echo "   NO EXISTE - Crear con: mkdir -p /var/www/crm-famago/uploads && sudo chown www-data:www-data /var/www/crm-famago/uploads"
echo ""
echo "2. pdfplumber instalado:"
cd /var/www/crm-famago && source venv/bin/activate && pip list | grep pdfplumber || echo "   NO INSTALADO - Instalar con: pip install pdfplumber"
echo ""
echo "3. Servicios activos:"
systemctl is-active crm-famago && echo "   crm-famago: ACTIVO" || echo "   crm-famago: INACTIVO"
systemctl is-active nginx && echo "   nginx: ACTIVO" || echo "   nginx: INACTIVO"
systemctl is-active mongod && echo "   mongod: ACTIVO" || echo "   mongod: INACTIVO"
echo ""
echo "4. Memoria disponible:"
free -h | grep "Mem:"
echo ""
echo "5. Últimos errores:"
sudo tail -3 /var/log/crm-famago/error.log 2>/dev/null || echo "   Sin logs"
```

---

## 🎯 Causa Más Probable del Error

El error "Failed to fetch" en el VPS es **99% seguro** causado por:

1. **Timeouts de Nginx muy cortos** → El procesamiento del PDF tarda más de lo que Nginx espera
2. **Límite de tamaño de archivo** → El PDF es más grande de lo permitido (por defecto 1MB en Nginx)

**La solución del Paso 2.4 (Nginx) es la MÁS IMPORTANTE** ✨

---

## ✅ Checklist Final

- [ ] Conectado al VPS por SSH
- [ ] Instalado `pdfplumber` en el venv
- [ ] Creado directorio `uploads/` con permisos
- [ ] Modificado Nginx (timeouts a 600s)
- [ ] Modificado Nginx (client_max_body_size a 50M)
- [ ] Modificado Gunicorn (--timeout 600)
- [ ] Reiniciado nginx y crm-famago
- [ ] Probado importar PDF desde navegador
- [ ] **¡FUNCIONA!** 🎉

---

## 📞 Resumen para Testeo

**SI ESTÁS APURADO**, solo haz esto en el VPS:

```bash
# 1. Conectar
ssh usuario@tu-vps-ip

# 2. Instalar dependencia
cd /var/www/crm-famago
source venv/bin/activate
pip install pdfplumber

# 3. Crear directorio
mkdir -p uploads
sudo chown www-data:www-data uploads

# 4. Editar Nginx (agregar timeouts y client_max_body_size)
sudo nano /etc/nginx/sites-available/crm-famago
# Ver el archivo SOLUCION_PDF_VPS.md para los cambios exactos

# 5. Editar Gunicorn (agregar --timeout 600)
sudo nano /etc/systemd/system/crm-famago.service

# 6. Reiniciar todo
sudo nginx -t
sudo systemctl restart nginx
sudo systemctl daemon-reload
sudo systemctl restart crm-famago

# 7. Probar desde el navegador
```

---

**Fecha:** 2025-12-15
**Archivos relacionados:**
- `SOLUCION_PDF_VPS.md` - Solución detallada paso a paso
- `test_pdf_import.py` - Script de prueba para localhost
