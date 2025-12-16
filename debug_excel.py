"""
Script de debug para ver exactamente qué está leyendo del Excel
"""
import pandas as pd
import re

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

# Leer Excel
excel_path = "listas_de_precios/lista_de_precios_115.xlsx"
excel_file = pd.ExcelFile(excel_path)

print(f"Hojas encontradas: {len(excel_file.sheet_names)}")
print(f"Nombres: {excel_file.sheet_names}\n")

total_productos = 0

# Procesar primera hoja en detalle
nombre_hoja = excel_file.sheet_names[0]
df = pd.read_excel(excel_path, sheet_name=nombre_hoja)

print(f"="*80)
print(f"HOJA: {nombre_hoja}")
print(f"="*80)
print(f"Total filas: {len(df)}")
print(f"Columnas: {df.columns.tolist()}\n")

productos_encontrados = 0

for idx, row in df.iterrows():
    # Obtener valores de las columnas
    unnamed_0 = row.get('Unnamed: 0')
    producto_col = row.get('Producto')
    unnamed_2 = row.get('Unnamed: 2')
    precio_lista_col = row.get('Lista')

    # Saltar filas sin precio
    if pd.isna(precio_lista_col):
        continue

    # Saltar filas de categoría o línea
    if pd.notna(producto_col):
        producto_str = str(producto_col)
        if 'Categoría:' in producto_str or 'Linea:' in producto_str or 'Línea:' in producto_str:
            print(f"Fila {idx}: CATEGORIA/LINEA - {producto_str}")
            continue

    codigo = None
    nombre = None

    # CASO 1: Código y nombre en columna "Producto"
    if pd.notna(producto_col):
        codigo = extraer_codigo(producto_col)
        nombre = limpiar_nombre_producto(producto_col, codigo)

        print(f"Fila {idx}: CASO 1")
        print(f"  producto_col: '{producto_col}'")
        print(f"  codigo extraído: '{codigo}'")
        print(f"  nombre limpio: '{nombre}'")
        print(f"  precio: {precio_lista_col}")

    # CASO 2: Código en "Unnamed: 0" y nombre en "Unnamed: 2"
    elif pd.notna(unnamed_0) and pd.notna(unnamed_2):
        codigo = extraer_codigo(unnamed_0)
        nombre = str(unnamed_2).strip()

        print(f"Fila {idx}: CASO 2")
        print(f"  unnamed_0: '{unnamed_0}'")
        print(f"  unnamed_2: '{unnamed_2}'")
        print(f"  codigo extraído: '{codigo}'")
        print(f"  nombre: '{nombre}'")
        print(f"  precio: {precio_lista_col}")

    # CASO 3: Solo nombre en "Unnamed: 2" (sin código)
    elif pd.notna(unnamed_2):
        nombre = str(unnamed_2).strip()

        print(f"Fila {idx}: CASO 3")
        print(f"  unnamed_2: '{unnamed_2}'")
        print(f"  nombre: '{nombre}'")
        print(f"  precio: {precio_lista_col}")

    if nombre and pd.notna(precio_lista_col) and float(precio_lista_col) > 0:
        productos_encontrados += 1
        print(f"  ✓ PRODUCTO VÁLIDO #{productos_encontrados}\n")
    else:
        print(f"  ✗ NO VÁLIDO (nombre={nombre}, precio={precio_lista_col})\n")

print(f"\n{'='*80}")
print(f"RESUMEN HOJA '{nombre_hoja}':")
print(f"Total productos válidos encontrados: {productos_encontrados}")
print(f"{'='*80}\n")
