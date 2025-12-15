# 🚨 SOLUCIÓN RÁPIDA: Error "Failed to fetch" al Importar PDF

## El Problema

Al intentar importar un PDF en el VPS, sale este error:
```
Error al importar PDF: Failed to fetch
```

## La Causa

El servidor **tarda mucho** procesando el PDF y Nginx "se cansa de esperar" (timeout).

## La Solución (5 minutos)

### 1. Conectar al VPS
```bash
ssh usuario@tu-vps-ip
```

### 2. Instalar pdfplumber
```bash
cd /var/www/crm-famago
source venv/bin/activate
pip install pdfplumber
```

### 3. Crear directorio para archivos temporales
```bash
mkdir -p uploads
sudo chown www-data:www-data uploads
```

### 4. Modificar Nginx (EL MÁS IMPORTANTE)
```bash
sudo nano /etc/nginx/sites-available/crm-famago
```

**Busca la sección `location /` y agrégale estos timeouts:**

```nginx
location / {
    proxy_pass http://127.0.0.1:5000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;

    # AGREGAR ESTAS LÍNEAS:
    proxy_connect_timeout 600s;
    proxy_send_timeout 600s;
    proxy_read_timeout 600s;
    proxy_request_buffering off;
}
```

**También busca `client_max_body_size` en el bloque `server` (o agrégalo):**

```nginx
server {
    # ... otras configuraciones ...

    # AGREGAR ESTAS LÍNEAS:
    client_max_body_size 50M;
    client_body_timeout 300s;

    # ... resto de configuraciones ...
}
```

Guardar: `Ctrl+O` → `Enter` → `Ctrl+X`

### 5. Modificar Gunicorn
```bash
sudo nano /etc/systemd/system/crm-famago.service
```

**Busca la línea `ExecStart` y agrégale `--timeout 600`:**

```ini
ExecStart=/var/www/crm-famago/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:5000 --timeout 600 wsgi:app --access-logfile /var/log/crm-famago/access.log --error-logfile /var/log/crm-famago/error.log
```

Guardar: `Ctrl+O` → `Enter` → `Ctrl+X`

### 6. Reiniciar todo
```bash
sudo nginx -t                           # Verificar sintaxis
sudo systemctl restart nginx            # Reiniciar Nginx
sudo systemctl daemon-reload            # Recargar systemd
sudo systemctl restart crm-famago       # Reiniciar app
```

### 7. Verificar
```bash
sudo systemctl status nginx crm-famago
```

Ambos deben decir "active (running)" en verde.

### 8. Probar

- Abre tu app en el navegador
- Ve a la pestaña **Cálculos**
- Click en **📄 Importar PDF**
- Selecciona un PDF
- **¡Debería funcionar!** 🎉

---

## Si Sigue sin Funcionar

Ver logs de errores:
```bash
sudo tail -30 /var/log/crm-famago/error.log
```

---

## Archivos de Ayuda

- `SOLUCION_PDF_VPS.md` - Solución completa paso a paso
- `INSTRUCCIONES_TESTEO.md` - Guía detallada de testeo
- `test_pdf_import.py` - Script para probar en localhost

---

**Tiempo estimado:** 5-10 minutos
**Probabilidad de éxito:** 99%

La clave está en los **timeouts de Nginx** (Paso 4) ✨
