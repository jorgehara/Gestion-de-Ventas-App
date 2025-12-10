@echo off
echo ======================================
echo 🚀 CRM Famago - Iniciando servidor...
echo ======================================
echo.

REM Verificar si MongoDB está corriendo
tasklist /FI "IMAGENAME eq mongod.exe" 2>NUL | find /I /N "mongod.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo ✓ MongoDB está corriendo
) else (
    echo ⚠️  MongoDB no está corriendo
    echo.
    echo    Para iniciar MongoDB, ejecuta:
    echo    - Windows: net start MongoDB
    echo    - O inicia MongoDB Compass
    echo.
    set /p continuar="¿Desea continuar de todos modos? (s/n): "
    if /i not "%continuar%"=="s" exit /b 1
)

echo ✓ Base de datos MongoDB: crm_famago
echo 🌐 El servidor estará disponible en: http://localhost:5000
echo.
echo Para detener el servidor, presiona Ctrl+C
echo.
echo ======================================
echo.

python app.py
pause
