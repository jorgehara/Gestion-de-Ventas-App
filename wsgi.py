"""
WSGI Entry Point
Para usar con Gunicorn en producción con soporte para subrutas
"""
import os
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.wrappers import Response
from app import app

# Configurar la ruta base (por defecto /ventas)
# Puedes cambiar esto en el archivo .env con: APP_PREFIX=/otra-ruta
APP_PREFIX = os.getenv('APP_PREFIX', '/ventas')

# Si APP_PREFIX está vacío o es '/', usar la app directamente
if not APP_PREFIX or APP_PREFIX == '/':
    application = app
else:
    # Usar DispatcherMiddleware para montar la app en una subruta
    application = DispatcherMiddleware(
        Response('Not Found', status=404),
        {APP_PREFIX: app}
    )

if __name__ == "__main__":
    app.run()
