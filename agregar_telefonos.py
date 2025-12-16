from pymongo import MongoClient
from dotenv import load_dotenv
import os

# Cargar variables de entorno
load_dotenv()

# Configuración de MongoDB
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
DB_NAME = os.getenv('DB_NAME', 'crm_famago')

try:
    # Conectar a MongoDB
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    clientes_collection = db['clientes']

    print(f"Conectado a MongoDB: {DB_NAME}")

    # Actualizar todos los clientes que no tienen campo 'telefono' o tienen valor vacío/None
    resultado = clientes_collection.update_many(
        {
            '$or': [
                {'telefono': {'$exists': False}},
                {'telefono': None},
                {'telefono': ''}
            ]
        },
        {
            '$set': {'telefono': '12345'}
        }
    )

    print(f"✓ Se actualizaron {resultado.modified_count} clientes con el teléfono '12345'")
    print(f"Total de clientes en la base de datos: {clientes_collection.count_documents({})}")

except Exception as e:
    print(f"✗ Error: {e}")
