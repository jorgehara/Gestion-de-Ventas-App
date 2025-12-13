##para produccion
cd /root/Gestion-de-Ventas-App
source venv/bin/activate
exec gunicorn --bind 0.0.0.0:8001 --workers 4 --timeout 120 app:app

