# 📊 Diagrama del Problema: "Failed to fetch" al Importar PDF

## Flujo Normal (Cuando Funciona)

```
[Navegador]
    ↓ (1) Usuario sube PDF
    ↓
[Nginx]
    ↓ (2) Reenvía a Gunicorn
    ↓
[Gunicorn/Flask App]
    ↓ (3) Procesa PDF con pdfplumber
    ↓ (4) Lee productos
    ↓ (5) Guarda en MongoDB
    ↓ (6) Responde: "Importación completada"
    ↑
[Nginx]
    ↑ (7) Reenvía respuesta
    ↑
[Navegador]
    ↑ (8) Muestra mensaje de éxito
```

**Tiempo total:** ~30-60 segundos (dependiendo del tamaño del PDF)

---

## Flujo con Error (En el VPS)

```
[Navegador]
    ↓ (1) Usuario sube PDF
    ↓
[Nginx] (Timeout por defecto: 60 segundos)
    ↓ (2) Reenvía a Gunicorn
    ↓
[Gunicorn/Flask App]
    ↓ (3) Procesa PDF con pdfplumber
    ↓ (4) Lee productos... (puede tardar 2-3 minutos)
    ↓
[Nginx] ⏱️  **¡TIMEOUT! Se cansó de esperar**
    ↓
    ❌ Nginx cierra la conexión (después de 60 segundos)
    ↓
[Navegador]
    ❌ Muestra: "Error al importar PDF: Failed to fetch"

[Gunicorn/Flask App] (sigue procesando sin saberlo)
    ↓ (5) Termina de procesar
    ↓ (6) Guarda en MongoDB
    ↓ (7) Responde: "Importación completada"
    ↓
    ⚠️  Pero Nginx ya cerró la conexión!
    ❌ La respuesta se pierde
```

---

## Causas del Problema

### 1. Timeouts de Nginx (PRINCIPAL)

Por defecto, Nginx espera **60 segundos** para una respuesta.

Si el PDF es grande o tiene muchos productos:
- Leer el PDF: 10-20 segundos
- Procesar productos: 20-40 segundos
- Guardar en MongoDB: 10-20 segundos
- **Total:** 40-80 segundos ❌ **SUPERA EL TIMEOUT**

### 2. Tamaño Máximo de Archivo

Por defecto, Nginx acepta archivos de **1MB** máximo.

Si tu PDF es de 5MB → **Nginx lo rechaza** antes de enviarlo a Flask.

### 3. Timeout de Gunicorn

Por defecto, Gunicorn mata los workers que tardan más de **30 segundos**.

---

## La Solución

### Aumentar Timeouts en Nginx

```nginx
location / {
    # De 60s → 600s (10 minutos)
    proxy_read_timeout 600s;
    proxy_send_timeout 600s;
    proxy_connect_timeout 600s;
}
```

### Aumentar Tamaño Máximo

```nginx
server {
    # De 1MB → 50MB
    client_max_body_size 50M;
}
```

### Aumentar Timeout en Gunicorn

```bash
# De 30s → 600s (10 minutos)
gunicorn --timeout 600 wsgi:app
```

---

## Comparación: Antes vs Después

### ANTES (Con error)
```
Nginx timeout:     60s  ❌
Gunicorn timeout:  30s  ❌
Tamaño máximo:     1MB  ❌
Resultado: Failed to fetch cuando el PDF tarda más de 60s
```

### DESPUÉS (Corregido)
```
Nginx timeout:     600s ✅ (10 minutos)
Gunicorn timeout:  600s ✅ (10 minutos)
Tamaño máximo:     50MB ✅
Resultado: Funciona incluso con PDFs grandes
```

---

## ¿Por qué Funciona en Localhost pero NO en el VPS?

### En Localhost
```
[Navegador] → [Flask directamente] (sin Nginx)
```
- No hay timeouts de proxy
- No hay límites de tamaño adicionales
- Flask espera todo lo necesario

### En el VPS
```
[Navegador] → [Nginx] → [Gunicorn] → [Flask]
```
- Nginx agrega timeouts
- Nginx agrega límites de tamaño
- Gunicorn agrega timeouts
- **Más capas = más lugares donde puede fallar**

---

## Verificación Visual del Fix

### Antes de aplicar el fix:
```
Usuario → [PDF 5MB] → Nginx ❌ "File too large"
Usuario → [PDF 2MB] → Nginx → Gunicorn → Flask (procesando...)
                       ↓ (60s)
                       ❌ Timeout!

Navegador: "Failed to fetch" ❌
```

### Después de aplicar el fix:
```
Usuario → [PDF 5MB] → Nginx ✅ "OK, 50MB límite"
                       ↓
                       Gunicorn → Flask (procesando...)
                       ↓ (2 minutos)
                       ↓ (sin timeout, espera 10 min)
                       ✅ "Importación completada"
                       ↓
Navegador: "✅ 150 productos importados" ✅
```

---

## Logs para Debugging

### Si ves esto en los logs de Nginx:
```
upstream timed out (110: Connection timed out)
```
→ **Necesitas aumentar `proxy_read_timeout`**

### Si ves esto en el navegador:
```
413 Request Entity Too Large
```
→ **Necesitas aumentar `client_max_body_size`**

### Si ves esto en los logs de Gunicorn:
```
[CRITICAL] WORKER TIMEOUT
```
→ **Necesitas aumentar `--timeout` en Gunicorn**

---

## Resumen en 3 Líneas

1. **Problema:** Nginx se cansa de esperar (timeout) mientras Flask procesa el PDF
2. **Causa:** Timeouts por defecto muy cortos (60s) + límite de tamaño pequeño (1MB)
3. **Solución:** Aumentar timeouts a 600s y tamaño máximo a 50MB

**El archivo más importante a modificar:** `/etc/nginx/sites-available/crm-famago` ✨

---

**Creado:** 2025-12-15
**Archivos relacionados:**
- `RESUMEN_SOLUCION_PDF.md` - Solución rápida
- `SOLUCION_PDF_VPS.md` - Solución completa
- `INSTRUCCIONES_TESTEO.md` - Guía de testeo
