@echo off
echo ========================================
echo Subir CRM Famago al VPS
echo ========================================
echo.

REM Solicitar IP y usuario del VPS
set /p VPS_IP="Ingresa la IP del VPS: "
set /p VPS_USER="Ingresa el usuario SSH (default: root): "
if "%VPS_USER%"=="" set VPS_USER=root

echo.
echo Configuracion:
echo   Usuario: %VPS_USER%
echo   IP: %VPS_IP%
echo.
pause

REM Crear archivo temporal sin archivos innecesarios
echo Comprimiendo proyecto...
tar -czf crm-famago.tar.gz ^
  --exclude=*.db ^
  --exclude=*.sqlite ^
  --exclude=__pycache__ ^
  --exclude=venv ^
  --exclude=.git ^
  --exclude=*.pyc ^
  --exclude=backups ^
  .

if errorlevel 1 (
    echo Error al comprimir el proyecto
    pause
    exit /b 1
)

echo OK - Proyecto comprimido
echo.

REM Subir al VPS
echo Subiendo al VPS...
scp crm-famago.tar.gz %VPS_USER%@%VPS_IP%:/tmp/

if errorlevel 1 (
    echo Error al subir el archivo
    pause
    exit /b 1
)

echo OK - Archivo subido
echo.

REM Conectar y descomprimir
echo Conectando al VPS para descomprimir...
ssh %VPS_USER%@%VPS_IP% "cd /var/www && sudo tar -xzf /tmp/crm-famago.tar.gz && sudo rm /tmp/crm-famago.tar.gz && echo 'Proyecto descomprimido en /var/www'"

echo.
echo ========================================
echo Subida completada
echo ========================================
echo.
echo Ahora conectate al VPS y ejecuta:
echo   cd /var/www/crm-famago
echo   chmod +x deploy.sh
echo   sudo ./deploy.sh
echo.
pause
