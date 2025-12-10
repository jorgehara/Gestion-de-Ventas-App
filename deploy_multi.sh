#!/bin/bash

# Script de despliegue para VPS con múltiples proyectos
# Este script NO modifica Nginx, solo configura la aplicación

set -e

echo "===================================="
echo " Deploy Gestión Ventas (Multi-VPS)"
echo "===================================="
echo ""

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

APP_DIR="/root/Gestion-de-Ventas-App"
APP_USER="root"
APP_PORT=5001  # Puerto interno para esta app

# 1. Verificar que MongoDB está corriendo
echo -e "${YELLOW}[1/5] Verificando MongoDB...${NC}"
if systemctl is-active --quiet mongod || systemctl is-active --quiet mongodb; then
    echo -e "${GREEN} MongoDB está activo${NC}"
else
    echo -e "${RED} MongoDB no está corriendo${NC}"
    echo "Inicia MongoDB con: systemctl start mongod"
    exit 1
fi

# 2. Crear entorno virtual
echo -e "${YELLOW}[2/5] Configurando entorno virtual...${NC}"
cd $APP_DIR
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
echo -e "${GREEN} Entorno virtual listo${NC}"

# 3. Instalar/actualizar dependencias
echo -e "${YELLOW}[3/5] Instalando dependencias...${NC}"
pip install --upgrade pip
pip install -r requirements.txt
echo -e "${GREEN} Dependencias instaladas${NC}"

# 4. Configurar .env
echo -e "${YELLOW}[4/5] Configurando variables de entorno...${NC}"
if [ ! -f .env ]; then
    cat > .env << EOF
# MongoDB
MONGO_URI=mongodb://localhost:27017/
DB_NAME=crm_famago

# Producción
FLASK_ENV=production

# Ruta base para la app (cambiar si quieres otra ruta)
APP_PREFIX=/ventas
EOF
    echo -e "${GREEN} Archivo .env creado${NC}"
else
    # Agregar APP_PREFIX si no existe
    if ! grep -q "APP_PREFIX" .env; then
        echo "" >> .env
        echo "# Ruta base para la app" >> .env
        echo "APP_PREFIX=/ventas" >> .env
        echo -e "${GREEN} APP_PREFIX agregado a .env${NC}"
    else
        echo -e "${GREEN} .env ya configurado${NC}"
    fi
fi

# 5. Crear/actualizar servicio systemd
echo -e "${YELLOW}[5/5] Configurando servicio systemd...${NC}"
cat > /etc/systemd/system/gestion-ventas.service << EOF
[Unit]
Description=Gestion de Ventas App - Flask Application
After=network.target mongod.service

[Service]
Type=notify
User=$APP_USER
WorkingDirectory=$APP_DIR
Environment="PATH=$APP_DIR/venv/bin"
ExecStart=$APP_DIR/venv/bin/gunicorn --bind 127.0.0.1:$APP_PORT --workers 2 --timeout 120 wsgi:application
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable gestion-ventas.service
systemctl restart gestion-ventas.service
echo -e "${GREEN} Servicio configurado e iniciado${NC}"

# Verificar que el servicio está corriendo
sleep 2
if systemctl is-active --quiet gestion-ventas; then
    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}   Aplicación desplegada correctamente${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo "La aplicación está corriendo en el puerto interno: $APP_PORT"
    echo ""
    echo -e "${YELLOW}SIGUIENTE PASO: Configurar Nginx${NC}"
    echo ""
    echo "Agrega esto a tu configuración de Nginx:"
    echo ""
    echo "  location /ventas/ {"
    echo "      proxy_pass http://127.0.0.1:$APP_PORT/ventas/;"
    echo "      proxy_set_header Host \$host;"
    echo "      proxy_set_header X-Real-IP \$remote_addr;"
    echo "      proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;"
    echo "      proxy_set_header X-Forwarded-Proto \$scheme;"
    echo "      client_max_body_size 20M;"
    echo "  }"
    echo ""
    echo "Luego ejecuta: systemctl reload nginx"
    echo ""
    echo "Comandos útiles:"
    echo "  - Ver logs:          journalctl -u gestion-ventas -f"
    echo "  - Reiniciar:         systemctl restart gestion-ventas"
    echo "  - Ver estado:        systemctl status gestion-ventas"
else
    echo ""
    echo -e "${RED} Error: El servicio no se inició correctamente${NC}"
    echo "Ver logs con: journalctl -u gestion-ventas -n 50"
    exit 1
fi
