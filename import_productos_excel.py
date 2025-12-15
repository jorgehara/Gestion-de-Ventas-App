"""
Script para importar/actualizar productos desde Excel de lista de precios
Procesa el Excel y actualiza la base de datos MongoDB
"""
import pandas as pd
import re
from pymongo import MongoClient
from datetime import datetime
import sys
import os

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

def extraer_codigo(texto):
    """Extrae código del producto (puede estar entre paréntesis o ser número/alfanumérico)"""
    if not texto or pd.isna(texto):
        return None

    texto = str(texto).strip()

    # Buscar patrón (XXXXX) - código entre paréntesis
    match = re.search(r'\(([^\)]+)\)', texto)
    if match:
        return match.group(1).strip()

    # Si no hay paréntesis, buscar código al inicio (números o alfanumérico)
    match = re.match(r'^([\w\-\/]+)\s+', texto)
    if match:
        return match.group(1).strip()

    return None

def limpiar_nombre_producto(texto, codigo=None):
    """Limpia el nombre del producto removiendo el código"""
    if not texto or pd.isna(texto):
        return None

    nombre = str(texto).strip()

    # Remover código entre paréntesis
    nombre = re.sub(r'\([^\)]+\)\s*', '', nombre)

    # Si hay código, removerlo del inicio
    if codigo:
        # Escapar caracteres especiales en el código para regex
        codigo_escaped = re.escape(codigo)
        nombre = re.sub(f'^{codigo_escaped}\\s+', '', nombre)

    return nombre.strip()

def procesar_hoja(df, nombre_hoja):
    """
    Procesa una hoja del Excel y extrae productos
    Retorna lista de productos de esa hoja
    """
    productos = []

    print(f"  Procesando hoja '{nombre_hoja}' ({len(df)} filas)...")

    for idx, row in df.iterrows():
        try:
            # Obtener valores de las columnas
            unnamed_0 = row.get('Unnamed: 0')  # Puede contener código
            producto_col = row.get('Producto')  # Puede contener código + nombre
            unnamed_2 = row.get('Unnamed: 2')   # Puede contener nombre
            precio_lista_col = row.get('Lista')

            # Saltar filas sin precio
            if pd.isna(precio_lista_col):
                continue

            # Saltar filas de categoría o línea
            if pd.notna(producto_col):
                producto_str = str(producto_col)
                if 'Categoría:' in producto_str or 'Linea:' in producto_str or 'Línea:' in producto_str:
                    continue

            codigo = None
            nombre = None

            # CASO 1: Código y nombre en columna "Producto"
            # Ejemplo: "140 (05001) Caja De Dinero Acero 5 Divisiones"
            if pd.notna(producto_col):
                codigo = extraer_codigo(producto_col)
                nombre = limpiar_nombre_producto(producto_col, codigo)

            # CASO 2: Código en "Unnamed: 0" y nombre en "Unnamed: 2"
            # Ejemplo: unnamed_0 = "90557/56 (28323)", unnamed_2 = "Canasto De Mano..."
            elif pd.notna(unnamed_0) and pd.notna(unnamed_2):
                codigo = extraer_codigo(unnamed_0)
                nombre = str(unnamed_2).strip()

            # CASO 3: Solo nombre en "Unnamed: 2" (sin código)
            elif pd.notna(unnamed_2):
                nombre = str(unnamed_2).strip()

            # Validar que tengamos nombre y precio
            if not nombre or pd.isna(precio_lista_col):
                continue

            precio_lista = float(precio_lista_col)

            # Validar precio positivo
            if precio_lista <= 0:
                continue

            productos.append({
                'codigo': codigo,
                'nombre': nombre,
                'precio_lista': precio_lista
            })

        except Exception as e:
            print(f"ERROR en fila {idx}: {e}")
            continue

    print(f"    -> Encontrados {len(productos)} productos en esta hoja")
    return productos

def procesar_excel(excel_path):
    """
    Extrae productos de todas las hojas del Excel
    Retorna lista de productos: [{codigo, nombre, precio_lista}, ...]
    """
    todos_los_productos = []

    # Leer todas las hojas del Excel
    excel_file = pd.ExcelFile(excel_path)

    print(f"\nArchivo Excel contiene {len(excel_file.sheet_names)} hoja(s)")
    print(f"Hojas: {', '.join(excel_file.sheet_names)}\n")

    # Procesar cada hoja
    for nombre_hoja in excel_file.sheet_names:
        df = pd.read_excel(excel_path, sheet_name=nombre_hoja)
        productos_hoja = procesar_hoja(df, nombre_hoja)
        todos_los_productos.extend(productos_hoja)

    return todos_los_productos

def importar_productos_db(productos, actualizar_existentes=True):
    """
    Importa/actualiza productos en MongoDB

    Args:
        productos: Lista de productos extraídos del Excel
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
                        print(f"OK Actualizado: {nombre} - Nuevo precio: ${precio_lista:,.2f}")
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
            print(f"ERROR procesando '{producto.get('nombre', 'UNKNOWN')}': {e}")

    client.close()
    return stats

def main(excel_path):
    """Función principal"""
    print("\n" + "="*60)
    print("IMPORTACIÓN DE PRODUCTOS DESDE EXCEL")
    print("="*60 + "\n")

    # Verificar que el archivo existe
    if not os.path.exists(excel_path):
        print(f"ERROR: No se encontro el archivo '{excel_path}'")
        return

    print(f"Procesando Excel: {excel_path}\n")

    # Extraer productos del Excel
    productos = procesar_excel(excel_path)

    print(f"\nSe encontraron {len(productos)} productos en el Excel\n")

    if len(productos) == 0:
        print("ADVERTENCIA: No se encontraron productos para importar")
        return

    # Mostrar algunos ejemplos
    print("Ejemplos de productos encontrados:")
    for i, p in enumerate(productos[:5], 1):
        codigo_str = f"({p['codigo']})" if p['codigo'] else "(sin código)"
        print(f"  {i}. {codigo_str} {p['nombre']} - ${p['precio_lista']:,.2f}")

    if len(productos) > 5:
        print(f"  ... y {len(productos) - 5} productos más")

    # Confirmar importación
    print("\n" + "="*60)
    print("INICIANDO IMPORTACIÓN A BASE DE DATOS")
    print("="*60 + "\n")

    # Importar a MongoDB
    stats = importar_productos_db(productos, actualizar_existentes=True)

    # Mostrar resumen
    print("\n" + "="*60)
    print("RESUMEN DE IMPORTACIÓN")
    print("="*60)
    print(f"  OK Productos creados:     {stats['creados']}")
    print(f"  OK Productos actualizados: {stats['actualizados']}")
    print(f"  -- Sin cambios:           {stats['sin_cambios']}")
    print(f"  ERROR:                    {stats['errores']}")
    print("="*60 + "\n")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Uso: python import_productos_excel.py <ruta_al_excel>")
        print("Ejemplo: python import_productos_excel.py 'listas_de_precios/lista_de_precios_115.xlsx'")
        sys.exit(1)

    excel_path = sys.argv[1]
    main(excel_path)
