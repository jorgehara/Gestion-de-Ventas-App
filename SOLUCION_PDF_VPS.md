# Solución: Error "Failed to fetch" al importar PDF en VPS

## 🔍 Diagnóstico del Problema

El error "Failed to fetch" al importar PDF en el VPS puede ocurrir por varias razones:

1. **Timeouts de Nginx** - El procesamiento del PDF tarda mucho
2. **Tamaño del archivo** - Límite de carga muy pequeño
3. **Falta de dependencias** - pdfplumber no instalado en el VPS
4. **Permisos de directorio** - El directorio 'uploads' no existe o no tiene permisos
5. **Memoria insuficiente** - El VPS no tiene suficiente RAM

---

## ✅ Soluciones Paso a Paso

### Paso 1: Probar en Localhost PRIMERO

Antes de intentar solucionar en el VPS, asegúrate que funciona localmente:

```bash
# En tu PC local, ejecuta el script de prueba
python test_pdf_import.py
```

Si falla en localhost, el problema es el código. Si funciona en localhost pero NO en el VPS, continúa con los siguientes pasos.

---

### Paso 2: Verificar dependencias en el VPS

Conéctate a tu VPS y verifica que pdfplumber esté instalado:

```bash
ssh usuario@tu-vps-ip
cd /var/www/crm-famago
source venv/bin/activate

# Verificar si pdfplumber está instalado
pip list | grep pdfplumber

# Si NO está instalado, instalarlo:
pip install pdfplumber

# Reiniciar el servicio
sudo systemctl restart crm-famago
```

---

### Paso 3: Crear directorio 'uploads' con permisos correctos

El código necesita crear archivos temporales en `uploads/`:

```bash
cd /var/www/crm-famago

# Crear directorio uploads si no existe
mkdir -p uploads

# Dar permisos al usuario www-data (el que corre gunicorn)
sudo chown -R www-data:www-data uploads
sudo chmod 755 uploads

# Verificar permisos
ls -la uploads
```

---

### Paso 4: Aumentar timeouts y tamaño máximo en Nginx

Edita la configuración de Nginx:

```bash
sudo nano /etc/nginx/sites-available/crm-famago
```

**BUSCA** la configuración existente y **MODIFICA** así:

```nginx
server {
    listen 80;
    server_name tu-dominio.com;

    # ... (otras configuraciones)

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # ⭐ AUMENTAR TIMEOUTS (importante para PDFs grandes)
        proxy_connect_timeout 600s;
        proxy_send_timeout 600s;
        proxy_read_timeout 600s;

        # ⭐ Evitar que nginx haga buffering de archivos grandes
        proxy_request_buffering off;
    }

    # ⭐ AUMENTAR TAMAÑO MÁXIMO de archivo a 50MB
    client_max_body_size 50M;

    # ⭐ AUMENTAR TIMEOUT del cliente
    client_body_timeout 300s;
}
```

**Guardar** (Ctrl+O, Enter, Ctrl+X) y **probar configuración**:

```bash
sudo nginx -t
```

Si dice "syntax is ok", reinicia Nginx:

```bash
sudo systemctl restart nginx
```

---

### Paso 5: Aumentar timeouts en Gunicorn

Edita el servicio de systemd:

```bash
sudo nano /etc/systemd/system/crm-famago.service
```

**BUSCA** la línea `ExecStart` y **MODIFICA** para agregar `--timeout 600`:

```ini
[Service]
# ... (otras configuraciones)
ExecStart=/var/www/crm-famago/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:5000 --timeout 600 wsgi:app --access-logfile /var/log/crm-famago/access.log --error-logfile /var/log/crm-famago/error.log
```

**Guardar** y recargar:

```bash
sudo systemctl daemon-reload
sudo systemctl restart crm-famago
```

---

### Paso 6: Verificar logs en caso de error

Si sigue fallando, revisa los logs:

```bash
# Logs de la aplicación
sudo tail -f /var/log/crm-famago/error.log

# Logs de Nginx
sudo tail -f /var/log/nginx/crm-famago-error.log

# Logs del sistema
sudo journalctl -u crm-famago -f
```

---

### Paso 7: Mejorar el código para manejar archivos grandes

Si los PDFs son muy grandes, considera mejorar `app.py` para procesar en chunks.

Edita `app.py` en el VPS:

```bash
cd /var/www/crm-famago
source venv/bin/activate
nano app.py
```

**BUSCA** la sección de `@app.route('/api/import-productos-pdf', methods=['POST'])` (línea ~736) y **AGREGA** validación al inicio de la función:

```python
@app.route('/api/import-productos-pdf', methods=['POST'])
def import_productos_pdf():
    """
    Importa/actualiza productos desde PDF de lista de precios
    """
    import pdfplumber
    import re

    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No se envió ningún archivo'}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({'error': 'No se seleccionó ningún archivo'}), 400

        if not file.filename.endswith('.pdf'):
            return jsonify({'error': 'El archivo debe ser un PDF'}), 400

        # ⭐ VALIDAR TAMAÑO DEL ARCHIVO (máximo 20MB)
        file.seek(0, 2)  # Ir al final del archivo
        file_size = file.tell()  # Obtener tamaño
        file.seek(0)  # Volver al inicio

        if file_size > 20 * 1024 * 1024:  # 20MB
            return jsonify({'error': 'El archivo PDF es demasiado grande (máximo 20MB)'}), 400

        # Continúa el código existente...
```

**Guardar** y reiniciar:

```bash
sudo systemctl restart crm-famago
```

---

## 🧪 Probar la Solución

Después de aplicar los cambios, prueba desde el navegador:

1. Ve a la pestaña **Cálculos** en tu aplicación web
2. Haz clic en **📄 Importar PDF**
3. Selecciona un archivo PDF de lista de precios
4. Observa la consola del navegador (F12) para ver errores

Si aún falla, verifica:

```bash
# En el VPS
cd /var/www/crm-famago
sudo tail -30 /var/log/crm-famago/error.log
```

---

## 🚀 Script de Verificación Completa para VPS

Crea este script en el VPS para verificar todo:

```bash
nano ~/check-crm.sh
```

Contenido:

```bash
#!/bin/bash

echo "=========================================="
echo "VERIFICACIÓN CRM FAMAGO"
echo "=========================================="

# 1. Verificar directorio uploads
echo -e "\n1. Directorio uploads:"
if [ -d "/var/www/crm-famago/uploads" ]; then
    echo "   ✅ Existe"
    ls -la /var/www/crm-famago/uploads
else
    echo "   ❌ NO existe"
    echo "   Creando..."
    mkdir -p /var/www/crm-famago/uploads
    sudo chown www-data:www-data /var/www/crm-famago/uploads
fi

# 2. Verificar pdfplumber
echo -e "\n2. Dependencia pdfplumber:"
cd /var/www/crm-famago
source venv/bin/activate
if pip list | grep -q pdfplumber; then
    echo "   ✅ Instalado"
    pip list | grep pdfplumber
else
    echo "   ❌ NO instalado"
fi

# 3. Verificar servicios
echo -e "\n3. Servicios:"
echo "   MongoDB:"
systemctl is-active --quiet mongod && echo "      ✅ Activo" || echo "      ❌ Inactivo"

echo "   CRM Famago:"
systemctl is-active --quiet crm-famago && echo "      ✅ Activo" || echo "      ❌ Inactivo"

echo "   Nginx:"
systemctl is-active --quiet nginx && echo "      ✅ Activo" || echo "      ❌ Inactivo"

# 4. Verificar timeouts de Nginx
echo -e "\n4. Configuración Nginx:"
if grep -q "proxy_read_timeout 600s" /etc/nginx/sites-available/crm-famago; then
    echo "   ✅ Timeouts configurados correctamente"
else
    echo "   ⚠️  Timeouts NO configurados (ver SOLUCION_PDF_VPS.md)"
fi

if grep -q "client_max_body_size 50M" /etc/nginx/sites-available/crm-famago; then
    echo "   ✅ Tamaño máximo configurado (50M)"
else
    echo "   ⚠️  Tamaño máximo NO configurado (ver SOLUCION_PDF_VPS.md)"
fi

# 5. Verificar logs recientes
echo -e "\n5. Últimos errores (si hay):"
sudo tail -5 /var/log/crm-famago/error.log

echo -e "\n=========================================="
echo "Verificación completada"
echo "=========================================="
```

Ejecutar:

```bash
chmod +x ~/check-crm.sh
~/check-crm.sh
```

---

## 📋 Checklist de Solución

Marca cada paso conforme lo completes:

- [ ] Probado en localhost (funciona ✅)
- [ ] Conectado al VPS por SSH
- [ ] Instalado `pdfplumber` en el venv del VPS
- [ ] Creado directorio `uploads/` con permisos `www-data`
- [ ] Modificado Nginx: timeouts a 600s
- [ ] Modificado Nginx: `client_max_body_size` a 50M
- [ ] Modificado Gunicorn: `--timeout 600`
- [ ] Reiniciado todos los servicios
- [ ] Verificado logs (sin errores)
- [ ] Probado importar PDF desde navegador
- [ ] **¡FUNCIONA!** 🎉

---

## 🔧 Solución Rápida (Copy-Paste)

Si tienes prisa, ejecuta estos comandos en el VPS:

```bash
# Conectarse al VPS
ssh usuario@tu-vps-ip

# Ir al directorio del proyecto
cd /var/www/crm-famago

# Activar entorno virtual
source venv/bin/activate

# Instalar pdfplumber
pip install pdfplumber

# Crear directorio uploads
mkdir -p uploads
sudo chown www-data:www-data uploads

# Editar Nginx (abre el editor, modifica según Paso 4, guarda)
sudo nano /etc/nginx/sites-available/crm-famago

# Verificar y reiniciar Nginx
sudo nginx -t
sudo systemctl restart nginx

# Editar servicio (abre el editor, modifica según Paso 5, guarda)
sudo nano /etc/systemd/system/crm-famago.service

# Recargar y reiniciar servicio
sudo systemctl daemon-reload
sudo systemctl restart crm-famago

# Verificar que todo esté corriendo
sudo systemctl status crm-famago nginx mongod

# Listo! Prueba importar PDF desde el navegador
```

---

## 💡 Prevención de Errores Futuros

Para evitar este tipo de errores en futuras funcionalidades:

1. **Siempre prueba en localhost primero**
2. **Documentar dependencias** en `requirements.txt`
3. **Configurar timeouts generosos** en producción
4. **Validar tamaños de archivo** en el código
5. **Logs detallados** para debugging

---

## 📞 ¿Sigue sin funcionar?

Si después de todos estos pasos aún no funciona:

1. Ejecuta el script de verificación: `~/check-crm.sh`
2. Revisa los logs: `sudo tail -50 /var/log/crm-famago/error.log`
3. Verifica memoria del VPS: `free -h`
4. Verifica espacio en disco: `df -h`
5. Intenta con un PDF más pequeño (< 1MB) para descartar problemas de tamaño

---

**Última actualización:** 2025-12-15
