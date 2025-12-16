"""
Script para verificar productos en la base de datos
"""
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
DB_NAME = os.getenv('DB_NAME', 'crm_famago')

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
productos_collection = db['productos']

print("\n" + "="*80)
print("VERIFICACIÓN DE PRODUCTOS EN BD")
print("="*80 + "\n")

# Total productos
total = productos_collection.count_documents({})
print(f"Total productos en BD: {total}")

# Productos activos
activos = productos_collection.count_documents({'activo': True})
print(f"Productos activos: {activos}")

# Productos inactivos
inactivos = productos_collection.count_documents({'activo': False})
print(f"Productos inactivos: {inactivos}")

# Productos sin campo activo
sin_campo = productos_collection.count_documents({'activo': {'$exists': False}})
print(f"Productos sin campo 'activo': {sin_campo}\n")

# Mostrar todos los productos
print("="*80)
print("TODOS LOS PRODUCTOS:")
print("="*80 + "\n")

for i, prod in enumerate(productos_collection.find(), 1):
    codigo = prod.get('codigo', 'sin código')
    nombre = prod.get('nombre', 'sin nombre')
    precio = prod.get('precio_lista', 0)
    activo = prod.get('activo', 'NO DEFINIDO')

    print(f"{i}. ({codigo}) {nombre[:60]}")
    print(f"   Precio: ${precio:,.2f}")
    print(f"   Activo: {activo}")
    print(f"   _id: {prod['_id']}\n")

client.close()
