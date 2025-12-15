"""
Script para importar/actualizar productos desde PDF de lista de precios
Procesa el PDF y actualiza la base de datos MongoDB
"""
import pdfplumber
import re
from pymongo import MongoClient
from datetime import datetime
import sys

# Configuración MongoDB
MONGO_URI = 'mongodb://localhost:27017/'
DB_NAME = 'crm_famago'

def calcular_precios_por_dia(precio_lista):
    """Calcula los precios por día según las fórmulas de recargo"""
    return {
        '42': round((precio_lista * 1.23) / 42, 3),
        '84': round((precio_lista * 1.42) / 84, 3),
        '135': round((precio_lista * 1.58) / 135, 3),
        '175': round((precio_lista * 1.75) / 175, 3),
        '220': round((precio_lista * 1.92) / 220, 3)
    }

def limpiar_numero(texto):
    """Limpia y convierte texto a número"""
    if not texto or texto.strip() == '':
        return None
    # Remover espacios, puntos de miles y convertir coma decimal a punto
    texto = texto.strip().replace('.', '').replace(',', '.')
    try:
        return float(texto)
    except:
        return None

def extraer_codigo(texto):
    """Extrae código del producto (puede estar entre paréntesis o ser número)"""
    if not texto:
        return None
    # Buscar patrón (XXXXX) o solo números al inicio
    match = re.search(r'\(([^\)]+)\)|^(\d+)', texto.strip())
    if match:
        return match.group(1) or match.group(2)
    return None

def procesar_pdf(pdf_path):
    """
    Extrae productos del PDF
    Retorna lista de productos: [{codigo, nombre, precio_lista}, ...]
    """
    productos = []

    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, 1):
            print(f"Procesando página {page_num}/{len(pdf.pages)}...")

            # Extraer tabla
            table = page.extract_table()

            if not table:
                continue

            # Buscar la fila de encabezado
            header_idx = None
            for idx, row in enumerate(table):
                if row and any('Producto' in str(cell) for cell in row if cell):
                    header_idx = idx
                    break

            if header_idx is None:
                continue

            # Procesar filas de datos
            for row in table[header_idx + 1:]:
                if not row or len(row) < 2:
                    continue

                producto_col = row[0]
                lista_col = row[1] if len(row) > 1 else None

                # Saltar filas vacías o de categoría
                if not producto_col or not lista_col:
                    continue

                # Saltar si es encabezado de categoría (empieza con "Categoría:" o "Línea:")
                if 'Categoría:' in str(producto_col) or 'Línea:' in str(producto_col):
                    continue

                # Extraer código
                codigo = extraer_codigo(producto_col)

                # Limpiar nombre del producto (remover código si existe)
                nombre = producto_col
                if codigo:
                    # Remover código entre paréntesis
                    nombre = re.sub(r'\([^\)]+\)\s*', '', nombre).strip()
                    # Remover código al inicio si es número
                    nombre = re.sub(r'^\d+\s+', '', nombre).strip()

                # Extraer precio de lista
                precio_lista = limpiar_numero(lista_col)

                # Validar datos mínimos
                if not nombre or not precio_lista or precio_lista <= 0:
                    continue

                productos.append({
                    'codigo': codigo,
                    'nombre': nombre,
                    'precio_lista': precio_lista
                })

    return productos

def importar_productos_db(productos, actualizar_existentes=True):
    """
    Importa/actualiza productos en MongoDB

    Args:
        productos: Lista de productos extraídos del PDF
        actualizar_existentes: Si True, actualiza precios de productos existentes

    Returns:
        dict con estadísticas: {creados, actualizados, errores}
    """
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    productos_collection = db['productos']

    stats = {
        'creados': 0,
        'actualizados': 0,
        'errores': 0,
        'sin_cambios': 0
    }

    for producto in productos:
        try:
            codigo = producto.get('codigo')
            nombre = producto['nombre']
            precio_lista = producto['precio_lista']

            # Calcular precios por día
            precios_por_dia = calcular_precios_por_dia(precio_lista)

            # Buscar producto existente por código o nombre
            query = {}
            if codigo:
                query = {'codigo': codigo}
            else:
                query = {'nombre': {'$regex': f'^{re.escape(nombre)}$', '$options': 'i'}}

            producto_existente = productos_collection.find_one(query)

            if producto_existente:
                # Producto existe
                if actualizar_existentes:
                    # Verificar si hay cambios en el precio
                    if producto_existente.get('precio_lista') != precio_lista:
                        # Actualizar precios
                        productos_collection.update_one(
                            {'_id': producto_existente['_id']},
                            {
                                '$set': {
                                    'precio_lista': precio_lista,
                                    'precios_por_dia': precios_por_dia,
                                    'fecha_actualizacion': datetime.now()
                                }
                            }
                        )
                        stats['actualizados'] += 1
                        print(f"✓ Actualizado: {nombre} - Nuevo precio: ${precio_lista:,.2f}")
                    else:
                        stats['sin_cambios'] += 1
                else:
                    stats['sin_cambios'] += 1
            else:
                # Producto nuevo - crear
                nuevo_producto = {
                    'codigo': codigo,
                    'nombre': nombre,
                    'precio_lista': precio_lista,
                    'precios_por_dia': precios_por_dia,
                    'fecha_creacion': datetime.now(),
                    'fecha_actualizacion': datetime.now(),
                    'activo': True
                }

                productos_collection.insert_one(nuevo_producto)
                stats['creados'] += 1
                print(f"+ Creado: {nombre} - ${precio_lista:,.2f}")

        except Exception as e:
            stats['errores'] += 1
            print(f"✗ Error procesando '{producto.get('nombre', 'UNKNOWN')}': {e}")

    client.close()
    return stats

def main(pdf_path):
    """Función principal"""
    print("\n" + "="*60)
    print("IMPORTACIÓN DE PRODUCTOS DESDE PDF")
    print("="*60 + "\n")

    print(f"📄 Procesando PDF: {pdf_path}\n")

    # Extraer productos del PDF
    productos = procesar_pdf(pdf_path)

    print(f"\n✓ Se encontraron {len(productos)} productos en el PDF\n")

    if len(productos) == 0:
        print("⚠ No se encontraron productos para importar")
        return

    # Confirmar importación
    print("="*60)
    print("INICIANDO IMPORTACIÓN A BASE DE DATOS")
    print("="*60 + "\n")

    # Importar a MongoDB
    stats = importar_productos_db(productos, actualizar_existentes=True)

    # Mostrar resumen
    print("\n" + "="*60)
    print("RESUMEN DE IMPORTACIÓN")
    print("="*60)
    print(f"  ✓ Productos creados:     {stats['creados']}")
    print(f"  ✓ Productos actualizados: {stats['actualizados']}")
    print(f"  - Sin cambios:           {stats['sin_cambios']}")
    print(f"  ✗ Errores:               {stats['errores']}")
    print("="*60 + "\n")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Uso: python import_productos_pdf.py <ruta_al_pdf>")
        print("Ejemplo: python import_productos_pdf.py 'listas_de_precios/lista_de_precios_115.pdf'")
        sys.exit(1)

    pdf_path = sys.argv[1]
    main(pdf_path)
