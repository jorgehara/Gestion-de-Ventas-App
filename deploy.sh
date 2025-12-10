#!/bin/bash

# Script de despliegue automático para Gestión de Ventas App
# Para Ubuntu/Debian en VPS

set -e  # Salir si hay algún error

echo "===================================="
echo "  Despliegue Gestión de Ventas App"
echo "===================================="
echo ""

# Colores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # Sin color

APP_DIR="/root/Gestion-de-Ventas-App"
APP_USER="root"
DOMAIN="tu-dominio.com"  # Cambia esto por tu dominio o IP

# 1. Actualizar sistema e instalar dependencias
echo -e "${YELLOW}[1/9] Actualizando sistema e instalando dependencias...${NC}"
apt-get update
apt-get install -y python3 python3-pip python3-venv nginx mongodb-org || apt-get install -y python3 python3-pip python3-venv nginx mongodb

# 2. Iniciar MongoDB
echo -e "${YELLOW}[2/9] Iniciando MongoDB...${NC}"
systemctl start mongod || systemctl start mongodb
systemctl enable mongod || systemctl enable mongodb
echo -e "${GREEN} MongoDB iniciado${NC}"

# 3. Crear entorno virtual
echo -e "${YELLOW}[3/9] Configurando entorno virtual de Python...${NC}"
cd $APP_DIR
python3 -m venv venv
source venv/bin/activate
echo -e "${GREEN} Entorno virtual creado${NC}"

# 4. Instalar dependencias Python
echo -e "${YELLOW}[4/9] Instalando dependencias Python...${NC}"
pip install --upgrade pip
pip install -r requirements.txt
echo -e "${GREEN} Dependencias instaladas${NC}"

# 5. Crear archivo .env si no existe
echo -e "${YELLOW}[5/9] Configurando variables de entorno...${NC}"
if [ ! -f .env ]; then
    cat > .env << EOF
# Configuración de MongoDB
MONGO_URI=mongodb://localhost:27017/
DB_NAME=crm_famago

# Producción
FLASK_ENV=production
EOF
    echo -e "${GREEN} Archivo .env creado${NC}"
else
    echo -e "${GREEN} Archivo .env ya existe${NC}"
fi

# 6. Importar datos iniciales (si existe el archivo Excel)
echo -e "${YELLOW}[6/9] Verificando datos iniciales...${NC}"
if [ -f "Famago 1.9.1 - copia.xlsx" ]; then
    echo "Se encontró archivo Excel. ¿Desea importar los datos? (s/n)"
    read -t 10 -n 1 respuesta || respuesta="n"
    echo ""
    if [ "$respuesta" = "s" ] || [ "$respuesta" = "S" ]; then
        python3 import_data.py
        echo -e "${GREEN} Datos importados${NC}"
    else
        echo -e "${YELLOW}˜ Importación omitida${NC}"
    fi
else
    echo -e "${YELLOW}˜ No se encontró archivo Excel para importar${NC}"
fi

# 7. Crear servicio systemd
echo -e "${YELLOW}[7/9] Configurando servicio systemd...${NC}"
cat > /etc/systemd/system/gestion-ventas.service << EOF
[Unit]
Description=Gestion de Ventas App - Flask Application
After=network.target mongodb.service

[Service]
Type=notify
User=$APP_USER
WorkingDirectory=$APP_DIR
Environment="PATH=$APP_DIR/venv/bin"
ExecStart=$APP_DIR/venv/bin/gunicorn --bind 127.0.0.1:5000 --workers 2 --timeout 120 app:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable gestion-ventas.service
systemctl restart gestion-ventas.service
echo -e "${GREEN} Servicio configurado e iniciado${NC}"

# 8. Configurar Nginx
echo -e "${YELLOW}[8/9] Configurando Nginx...${NC}"
cat > /etc/nginx/sites-available/gestion-ventas << EOF
server {
    listen 80;
    server_name $DOMAIN;

    client_max_body_size 20M;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_read_timeout 120s;
    }
}
EOF

# Habilitar sitio
ln -sf /etc/nginx/sites-available/gestion-ventas /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Verificar configuración
nginx -t

# Reiniciar Nginx
systemctl restart nginx
systemctl enable nginx
echo -e "${GREEN} Nginx configurado${NC}"

# 9. Verificar estado
echo -e "${YELLOW}[9/9] Verificando servicios...${NC}"
echo ""

# Verificar MongoDB
if systemctl is-active --quiet mongod || systemctl is-active --quiet mongodb; then
    echo -e "${GREEN} MongoDB: Activo${NC}"
else
    echo -e "${RED} MongoDB: Inactivo${NC}"
fi

# Verificar aplicación
if systemctl is-active --quiet gestion-ventas; then
    echo -e "${GREEN} Aplicación: Activa${NC}"
else
    echo -e "${RED} Aplicación: Inactiva${NC}"
    echo -e "${YELLOW}  Revisar logs: journalctl -u gestion-ventas -n 50${NC}"
fi

# Verificar Nginx
if systemctl is-active --quiet nginx; then
    echo -e "${GREEN} Nginx: Activo${NC}"
else
    echo -e "${RED} Nginx: Inactivo${NC}"
fi

echo ""
echo "===================================="
echo -e "${GREEN}  ¡Despliegue completado!${NC}"
echo "===================================="
echo ""
echo "Tu aplicación debería estar disponible en:"
echo "  http://$DOMAIN"
echo "  http://$(hostname -I | awk '{print $1}')"
echo ""
echo "Comandos útiles:"
echo "  - Ver logs de la app:    journalctl -u gestion-ventas -f"
echo "  - Reiniciar app:         systemctl restart gestion-ventas"
echo "  - Ver estado:            systemctl status gestion-ventas"
echo "  - Reiniciar Nginx:       systemctl restart nginx"
echo "  - Ver logs de Nginx:     tail -f /var/log/nginx/error.log"
echo ""
