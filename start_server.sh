#!/bin/bash

echo "======================================"
echo "🚀 CRM Famago - Iniciando servidor..."
echo "======================================"
echo ""

# Verificar si MongoDB está corriendo
if ! pgrep -x "mongod" > /dev/null; then
    echo "⚠️  MongoDB no está corriendo"
    echo ""
    echo "   Para iniciar MongoDB, ejecuta:"
    echo "   - macOS: brew services start mongodb-community"
    echo "   - Linux: sudo systemctl start mongod"
    echo ""
    read -p "¿Desea continuar de todos modos? (s/n): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Ss]$ ]]; then
        exit 1
    fi
fi

echo "✓ MongoDB está corriendo"
echo "✓ Base de datos MongoDB: crm_famago"
echo "🌐 El servidor estará disponible en: http://localhost:5000"
echo ""
echo "Para detener el servidor, presiona Ctrl+C"
echo ""
echo "======================================"
echo ""

python3 app.py
