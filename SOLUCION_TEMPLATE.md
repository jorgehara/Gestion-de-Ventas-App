# Solución: TemplateNotFound Error

## Problema

Al iniciar el servidor Flask, aparecía el siguiente error:

```
jinja2.exceptions.TemplateNotFound: index.html
```

## Causa

Flask busca los archivos de templates en una carpeta específica llamada `templates/` en la raíz del proyecto. El archivo `index.html` estaba ubicado en el directorio raíz en lugar de dentro de esta carpeta.

## Solución Aplicada

Se creó la carpeta `templates/` y se movió `index.html` dentro de ella:

```bash
mkdir templates
mv index.html templates/
```

## Estructura Correcta

```
Gestion-de-Ventas-App/
├── app.py
├── import_data.py
├── templates/              ← Carpeta requerida por Flask
│   └── index.html         ← Archivo movido aquí
├── requirements.txt
├── .env
└── ...
```

## Verificación

Después de mover el archivo, el servidor Flask debe iniciar correctamente:

```bash
python app.py
```

Y al acceder a http://localhost:5000 la página debe cargar sin problemas.

## Convención de Flask

Esta es la estructura estándar de Flask:

```
proyecto_flask/
├── app.py                  # Aplicación principal
├── templates/              # Templates HTML (Jinja2)
│   ├── index.html
│   ├── base.html
│   └── ...
├── static/                 # Archivos estáticos (CSS, JS, imágenes)
│   ├── css/
│   ├── js/
│   └── img/
└── ...
```

En este proyecto, como todo el CSS y JavaScript están integrados en `index.html`, solo necesitamos la carpeta `templates/`.

## Alternativa (No Recomendada)

Si quisieras mantener el archivo en la raíz, podrías cambiar la configuración de Flask en `app.py`:

```python
app = Flask(__name__, template_folder='.')
```

Pero esto NO es recomendado porque rompe las convenciones de Flask y puede causar problemas en el futuro.

---

**Problema resuelto:** ✅ El archivo `index.html` ahora está en `templates/index.html` y Flask lo encuentra correctamente.
