"""
Script de diagnóstico para verificar conexión a MongoDB y datos
"""
from pymongo import MongoClient
import sys

# Configuración MongoDB
MONGO_URI = 'mongodb://localhost:27017/'
DB_NAME = 'crm_famago'

def diagnosticar():
    print("\n" + "="*60)
    print("DIAGNÓSTICO DE CONEXIÓN Y DATOS")
    print("="*60 + "\n")

    # 1. Intentar conectar a MongoDB
    print("1. Probando conexión a MongoDB...")
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        # Forzar conexión
        client.server_info()
        print("   OK - Conexión exitosa a MongoDB\n")
    except Exception as e:
        print(f"   ERROR - No se pudo conectar a MongoDB: {e}\n")
        print("   Posibles soluciones:")
        print("   - Verifica que MongoDB esté corriendo: sudo systemctl status mongod")
        print("   - Inicia MongoDB si está detenido: sudo systemctl start mongod")
        return

    # 2. Verificar base de datos
    print(f"2. Verificando base de datos '{DB_NAME}'...")
    try:
        db = client[DB_NAME]
        collections = db.list_collection_names()
        print(f"   OK - Base de datos encontrada")
        print(f"   Colecciones: {', '.join(collections) if collections else 'Ninguna'}\n")
    except Exception as e:
        print(f"   ERROR: {e}\n")
        return

    # 3. Verificar colección de productos
    print("3. Verificando colección 'productos'...")
    try:
        productos_collection = db['productos']
        total_productos = productos_collection.count_documents({})
        print(f"   Total de productos en la BD: {total_productos}\n")

        if total_productos == 0:
            print("   ADVERTENCIA: No hay productos en la base de datos")
            print("   Necesitas correr el script de importación\n")
        else:
            # Mostrar algunos ejemplos
            print("   Ejemplos de productos:")
            for i, prod in enumerate(productos_collection.find().limit(5), 1):
                codigo = prod.get('codigo', 'sin código')
                nombre = prod.get('nombre', 'sin nombre')
                precio = prod.get('precio_lista', 0)
                print(f"   {i}. ({codigo}) {nombre} - ${precio:,.2f}")
            print()

    except Exception as e:
        print(f"   ERROR: {e}\n")
        return

    # 4. Verificar colección de clientes
    print("4. Verificando colección 'clientes'...")
    try:
        clientes_collection = db['clientes']
        total_clientes = clientes_collection.count_documents({})
        print(f"   Total de clientes en la BD: {total_clientes}\n")
    except Exception as e:
        print(f"   ERROR: {e}\n")

    # 5. Verificar colección de calculos
    print("5. Verificando colección 'calculos'...")
    try:
        calculos_collection = db['calculos']
        total_calculos = calculos_collection.count_documents({})
        print(f"   Total de cálculos en la BD: {total_calculos}\n")
    except Exception as e:
        print(f"   ERROR: {e}\n")

    print("="*60)
    print("DIAGNÓSTICO COMPLETADO")
    print("="*60 + "\n")

    client.close()

if __name__ == '__main__':
    diagnosticar()
