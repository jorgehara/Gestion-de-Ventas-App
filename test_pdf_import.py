"""
Script de prueba para importación de PDF
Prueba el endpoint de importación de PDF localmente
"""

import requests
import os

def test_pdf_import_local():
    """Prueba la importación de PDF en localhost"""

    print("=" * 60)
    print("TEST: Importación de PDF - Localhost")
    print("=" * 60)

    # URL del servidor local
    url = "http://localhost:5000/api/import-productos-pdf"

    # Buscar archivo PDF en el directorio actual
    pdf_files = [f for f in os.listdir('.') if f.endswith('.pdf')]

    if not pdf_files:
        print("❌ No se encontró ningún archivo PDF en el directorio actual")
        print("\nPor favor, coloca un archivo PDF de lista de precios en el directorio")
        return False

    pdf_file = pdf_files[0]
    print(f"📄 Archivo PDF encontrado: {pdf_file}")

    try:
        # Abrir archivo y enviarlo
        with open(pdf_file, 'rb') as f:
            files = {'file': (pdf_file, f, 'application/pdf')}

            print(f"\n📤 Enviando petición a {url}...")
            response = requests.post(url, files=files, timeout=120)

            print(f"\n📊 Código de respuesta: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                print("\n✅ ÉXITO - Respuesta del servidor:")
                print(f"   - Mensaje: {data.get('message', 'N/A')}")
                if 'stats' in data:
                    stats = data['stats']
                    print(f"   - Productos creados: {stats.get('creados', 0)}")
                    print(f"   - Productos actualizados: {stats.get('actualizados', 0)}")
                    print(f"   - Sin cambios: {stats.get('sin_cambios', 0)}")
                    print(f"   - Errores: {stats.get('errores', 0)}")
                    print(f"   - Total procesados: {data.get('total_procesados', 0)}")
                return True
            else:
                print(f"\n❌ ERROR - El servidor respondió con código {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data.get('error', 'Error desconocido')}")
                except:
                    print(f"   Respuesta: {response.text[:200]}")
                return False

    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR DE CONEXIÓN")
        print("   El servidor no está corriendo en http://localhost:5000")
        print("\n   Solución:")
        print("   1. Abre otra terminal")
        print("   2. Ejecuta: python app.py")
        print("   3. Vuelve a ejecutar este test")
        return False

    except requests.exceptions.Timeout:
        print("\n❌ TIMEOUT")
        print("   La petición tardó más de 120 segundos")
        print("   Esto puede indicar que el PDF es muy grande o hay un problema en el procesamiento")
        return False

    except Exception as e:
        print(f"\n❌ ERROR INESPERADO: {e}")
        return False

def test_server_running():
    """Verifica si el servidor está corriendo"""
    print("\n" + "=" * 60)
    print("TEST: Verificar servidor")
    print("=" * 60)

    try:
        response = requests.get("http://localhost:5000/", timeout=5)
        print(f"✅ Servidor respondiendo en http://localhost:5000")
        print(f"   Código: {response.status_code}")
        return True
    except requests.exceptions.ConnectionError:
        print("❌ Servidor NO está corriendo en http://localhost:5000")
        return False
    except Exception as e:
        print(f"❌ Error al verificar servidor: {e}")
        return False

def test_dependencies():
    """Verifica que las dependencias necesarias estén instaladas"""
    print("\n" + "=" * 60)
    print("TEST: Verificar dependencias")
    print("=" * 60)

    dependencies = {
        'pdfplumber': 'Necesario para leer PDFs',
        'flask': 'Framework web',
        'pymongo': 'Driver de MongoDB',
        'requests': 'Para hacer peticiones HTTP'
    }

    all_ok = True
    for dep, description in dependencies.items():
        try:
            __import__(dep)
            print(f"✅ {dep:15} - {description}")
        except ImportError:
            print(f"❌ {dep:15} - {description} [NO INSTALADO]")
            all_ok = False

    if not all_ok:
        print("\n⚠️  Instala las dependencias faltantes con:")
        print("   pip install -r requirements.txt")

    return all_ok

if __name__ == "__main__":
    print("\n🧪 SUITE DE PRUEBAS - Importación de PDF\n")

    # Test 1: Dependencias
    deps_ok = test_dependencies()

    # Test 2: Servidor corriendo
    server_ok = test_server_running()

    # Test 3: Importar PDF
    if deps_ok and server_ok:
        pdf_ok = test_pdf_import_local()
    else:
        print("\n⚠️  Saltando test de importación (dependencias o servidor no disponibles)")
        pdf_ok = False

    # Resumen
    print("\n" + "=" * 60)
    print("RESUMEN DE PRUEBAS")
    print("=" * 60)
    print(f"Dependencias:     {'✅ OK' if deps_ok else '❌ FALLÓ'}")
    print(f"Servidor:         {'✅ OK' if server_ok else '❌ FALLÓ'}")
    print(f"Importación PDF:  {'✅ OK' if pdf_ok else '❌ FALLÓ'}")
    print("=" * 60)

    if deps_ok and server_ok and pdf_ok:
        print("\n🎉 ¡Todas las pruebas pasaron exitosamente!")
        print("\nSi funciona en localhost pero NO en el VPS, el problema es:")
        print("1. Configuración de Nginx (timeouts o client_max_body_size)")
        print("2. Permisos del directorio 'uploads' en el VPS")
        print("3. Memoria insuficiente en el VPS")
        print("4. Dependencia pdfplumber no instalada en el VPS")
    else:
        print("\n❌ Algunas pruebas fallaron. Revisa los errores arriba.")
