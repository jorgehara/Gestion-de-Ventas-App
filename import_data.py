import pandas as pd
from pymongo import MongoClient
from datetime import datetime
from dotenv import load_dotenv
import os

# Cargar variables de entorno
load_dotenv()

def import_initial_data():
    # Configuración de MongoDB
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
    DB_NAME = os.getenv('DB_NAME', 'crm_famago')

    # Conexión a MongoDB
    try:
        client = MongoClient(MONGO_URI)
        db = client[DB_NAME]
        clientes_collection = db['clientes']
        print(f"✓ Conexión exitosa a MongoDB: {DB_NAME}")
    except Exception as e:
        print(f"✗ Error conectando a MongoDB: {e}")
        print("  Asegúrate de que MongoDB esté corriendo en localhost:27017")
        return

    # Verificar si ya hay datos
    existing_count = clientes_collection.count_documents({})
    if existing_count > 0:
        print(f"Base de datos ya contiene {existing_count} registros")
        response = input("¿Desea limpiar y reimportar? (s/n): ")
        if response.lower() != 's':
            print("Importación cancelada")
            return

        # Limpiar datos existentes
        clientes_collection.delete_many({})
        print("Base de datos limpiada")

    # Leer archivo Excel
    file_path = 'Famago 1.9.1 - copia.xlsx'

    if not os.path.exists(file_path):
        print(f"✗ No se encontró el archivo: {file_path}")
        print("  Asegúrate de que el archivo Excel esté en el directorio del proyecto")
        return

    try:
        df = pd.read_excel(file_path)
        print(f"✓ Archivo Excel leído correctamente: {len(df)} filas")
    except Exception as e:
        print(f"✗ Error leyendo archivo Excel: {e}")
        return

    # Mapeo de columnas
    column_mapping = {
        'FECHA': 'fecha',
        'CLIENTE': 'cliente',
        'NOMBRE NEGOCIO': 'nombre_negocio',
        'LOCALIDAD': 'localidad',
        'DIRECCION': 'direccion',
        'BARRIO': 'barrio',
        'DNI': 'dni',
        'ES CLIENTE?': 'es_cliente',
        'DETALLE': 'detalle',
        'INTERES 1 ': 'interes_1',
        'INTERES 1': 'interes_1',
        'INTERES 2': 'interes_2',
        'INTERES 3': 'interes_3',
        'CANTIDAD COMPRAS': 'cantidad_compras',
        'INTENCION DE COMPRAR': 'intencion_comprar',
        'ACCION': 'accion',
        'COMENTARIO': 'comentario',
        'FECHA DE NACIMIENTO': 'fecha_nacimiento',
        'AÑOS': 'años'
    }

    df = df.rename(columns=column_mapping)

    imported_count = 0
    errors = 0
    documentos = []

    for idx, row in df.iterrows():
        try:
            # Validar que tenga al menos el campo cliente
            if pd.isna(row.get('cliente')) or not str(row.get('cliente')).strip():
                continue

            # Normalizar intención de compra
            intencion = str(row.get('intencion_comprar', 'POCA')).strip().upper()

            # Crear documento
            documento = {
                'cliente': str(row.get('cliente', '')).strip(),
                'nombre_negocio': str(row.get('nombre_negocio', '')) if pd.notna(row.get('nombre_negocio')) else None,
                'localidad': str(row.get('localidad', '')) if pd.notna(row.get('localidad')) else None,
                'direccion': str(row.get('direccion', '')) if pd.notna(row.get('direccion')) else None,
                'barrio': str(row.get('barrio', '')) if pd.notna(row.get('barrio')) else None,
                'dni': str(row.get('dni', '')) if pd.notna(row.get('dni')) else None,
                'es_cliente': str(row.get('es_cliente', '')) if pd.notna(row.get('es_cliente')) else None,
                'detalle': str(row.get('detalle', '')) if pd.notna(row.get('detalle')) else None,
                'interes_1': str(row.get('interes_1', '')) if pd.notna(row.get('interes_1')) else None,
                'interes_2': str(row.get('interes_2', '')) if pd.notna(row.get('interes_2')) else None,
                'interes_3': str(row.get('interes_3', '')) if pd.notna(row.get('interes_3')) else None,
                'cantidad_compras': str(row.get('cantidad_compras', '')) if pd.notna(row.get('cantidad_compras')) else None,
                'intencion_comprar': intencion,
                'accion': str(row.get('accion', '')) if pd.notna(row.get('accion')) else None,
                'comentario': str(row.get('comentario', '')) if pd.notna(row.get('comentario')) else None
            }

            # Fecha de registro
            if pd.notna(row.get('fecha')):
                try:
                    documento['fecha'] = pd.to_datetime(row['fecha']).to_pydatetime()
                except:
                    documento['fecha'] = datetime.now()
            else:
                documento['fecha'] = datetime.now()

            # Fecha de nacimiento
            if pd.notna(row.get('fecha_nacimiento')):
                try:
                    documento['fecha_nacimiento'] = pd.to_datetime(row['fecha_nacimiento']).to_pydatetime()
                except:
                    pass

            # Edad
            if pd.notna(row.get('años')):
                try:
                    documento['años'] = int(row['años'])
                except:
                    pass

            documentos.append(documento)
            imported_count += 1

            # Insertar en lotes de 100
            if len(documentos) >= 100:
                clientes_collection.insert_many(documentos)
                print(f"Importados {imported_count} registros...")
                documentos = []

        except Exception as e:
            errors += 1
            print(f"Error en fila {idx}: {e}")

    # Insertar documentos restantes
    if documentos:
        clientes_collection.insert_many(documentos)

    print(f"\n✅ Importación completada!")
    print(f"Total importados: {imported_count}")
    print(f"Errores: {errors}")

    # Crear índices
    clientes_collection.create_index('cliente')
    clientes_collection.create_index('localidad')
    clientes_collection.create_index('intencion_comprar')
    print("✓ Índices creados correctamente")

if __name__ == '__main__':
    import_initial_data()
