"""
WSGI Entry Point
Para usar con Gunicorn en producción
"""
from app import app

if __name__ == "__main__":
    app.run()
