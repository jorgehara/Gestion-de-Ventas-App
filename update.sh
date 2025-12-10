#!/bin/bash

# Script de Actualización para CRM Famago
# Ejecutar en el VPS después de subir nuevos cambios

set -e

echo "=================================="
echo "🔄 CRM Famago - Script de Actualización"
echo "=================================="
echo ""

SERVICE_NAME="crm-famago"

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ $1${NC}"
}

# Verificar que estamos en el directorio correcto
if [ ! -f "app.py" ]; then
    echo "✗ Este script debe ejecutarse desde el directorio del proyecto"
    exit 1
fi

print_info "Iniciando actualización..."
echo ""

# 1. Backup de base de datos
print_info "Creando backup de MongoDB..."
BACKUP_DIR="./backups"
mkdir -p $BACKUP_DIR
BACKUP_FILE="$BACKUP_DIR/backup-$(date +%Y%m%d_%H%M%S)"

if command -v mongodump &> /dev/null; then
    mongodump --db crm_famago --out $BACKUP_FILE --quiet
    print_success "Backup creado: $BACKUP_FILE"
else
    print_info "mongodump no disponible, saltando backup"
fi
echo ""

# 2. Actualizar dependencias
print_info "Actualizando dependencias..."
source venv/bin/activate
pip install -r requirements.txt --quiet --upgrade
print_success "Dependencias actualizadas"
echo ""

# 3. Reiniciar servicio
print_info "Reiniciando servicio..."
sudo systemctl restart $SERVICE_NAME
sleep 2

if sudo systemctl is-active --quiet $SERVICE_NAME; then
    print_success "Servicio reiniciado correctamente"
else
    echo "✗ Error al reiniciar el servicio"
    echo "  Ver logs: sudo journalctl -u $SERVICE_NAME -n 50"
    exit 1
fi
echo ""

# 4. Limpiar caché
print_info "Limpiando caché de Python..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
print_success "Caché limpiado"
echo ""

echo "=================================="
print_success "¡Actualización completada!"
echo "=================================="
echo ""
print_info "Verificar estado: sudo systemctl status $SERVICE_NAME"
print_info "Ver logs: sudo journalctl -u $SERVICE_NAME -f"
echo ""
