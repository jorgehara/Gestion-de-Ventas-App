from flask import Flask, render_template, request, jsonify, send_file
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
import pandas as pd
import os
from io import BytesIO
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

# Configuración de MongoDB
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
DB_NAME = os.getenv('DB_NAME', 'crm_famago')

# Conexión a MongoDB
try:
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    clientes_collection = db['clientes']

    # Crear índices para mejorar rendimiento
    clientes_collection.create_index('cliente')
    clientes_collection.create_index('localidad')
    clientes_collection.create_index('intencion_comprar')

    print(f"✓ Conexión exitosa a MongoDB: {DB_NAME}")
except Exception as e:
    print(f"✗ Error conectando a MongoDB: {e}")
    print("  Asegúrate de que MongoDB esté corriendo en localhost:27017")
    exit(1)

def cliente_to_dict(cliente):
    """Convierte un documento de MongoDB a diccionario con _id como string"""
    if cliente:
        cliente['id'] = str(cliente['_id'])
        del cliente['_id']

        # Convertir datetime a string
        if 'fecha' in cliente and isinstance(cliente['fecha'], datetime):
            cliente['fecha'] = cliente['fecha'].strftime('%Y-%m-%d')
        if 'fecha_nacimiento' in cliente and isinstance(cliente['fecha_nacimiento'], datetime):
            cliente['fecha_nacimiento'] = cliente['fecha_nacimiento'].strftime('%Y-%m-%d')

        # Asegurar que todos los campos existan con valores por defecto
        campos_default = {
            'cliente': '',
            'nombre_negocio': '',
            'localidad': '',
            'direccion': '',
            'barrio': '',
            'dni': '',
            'es_cliente': '',
            'detalle': '',
            'interes_1': '',
            'interes_2': '',
            'interes_3': '',
            'cantidad_compras': '',
            'intencion_comprar': 'POCA',
            'accion': '',
            'comentario': '',
            'años': ''
        }

        for campo, default in campos_default.items():
            if campo not in cliente:
                cliente[campo] = default

    return cliente

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/clientes', methods=['GET'])
def get_clientes():
    localidad = request.args.get('localidad', '')
    intencion = request.args.get('intencion', '')
    search = request.args.get('search', '')

    # Construir filtro de MongoDB
    filtro = {}

    if localidad:
        filtro['localidad'] = {'$regex': localidad, '$options': 'i'}
    if intencion:
        filtro['intencion_comprar'] = {'$regex': intencion, '$options': 'i'}
    if search:
        filtro['$or'] = [
            {'cliente': {'$regex': search, '$options': 'i'}},
            {'nombre_negocio': {'$regex': search, '$options': 'i'}},
            {'comentario': {'$regex': search, '$options': 'i'}}
        ]

    # Buscar y ordenar por fecha descendente
    clientes = list(clientes_collection.find(filtro).sort('fecha', -1))

    return jsonify([cliente_to_dict(c) for c in clientes])

@app.route('/api/clientes', methods=['POST'])
def add_cliente():
    data = request.json

    # Crear nuevo documento
    nuevo_cliente = {
        'fecha': datetime.now(),
        'cliente': data.get('cliente', '').strip(),
        'nombre_negocio': data.get('nombre_negocio', '').strip() or None,
        'localidad': data.get('localidad', '').strip() or None,
        'direccion': data.get('direccion', '').strip() or None,
        'barrio': data.get('barrio', '').strip() or None,
        'dni': data.get('dni', '').strip() or None,
        'es_cliente': data.get('es_cliente', '').strip() or None,
        'detalle': data.get('detalle', '').strip() or None,
        'interes_1': data.get('interes_1', '').strip() or None,
        'interes_2': data.get('interes_2', '').strip() or None,
        'interes_3': data.get('interes_3', '').strip() or None,
        'cantidad_compras': data.get('cantidad_compras', '').strip() or None,
        'intencion_comprar': data.get('intencion_comprar', 'POCA').strip().upper(),
        'accion': data.get('accion', '').strip() or None,
        'comentario': data.get('comentario', '').strip() or None
    }

    # Campos opcionales de fecha y edad
    if data.get('fecha_nacimiento'):
        try:
            nuevo_cliente['fecha_nacimiento'] = datetime.strptime(data.get('fecha_nacimiento'), '%Y-%m-%d')
        except:
            pass

    if data.get('años'):
        try:
            nuevo_cliente['años'] = int(data.get('años'))
        except:
            pass

    # Insertar en MongoDB
    result = clientes_collection.insert_one(nuevo_cliente)
    nuevo_cliente['_id'] = result.inserted_id

    return jsonify(cliente_to_dict(nuevo_cliente)), 201

@app.route('/api/clientes/<id>', methods=['GET'])
def get_cliente(id):
    """Obtener un cliente específico por ID"""
    try:
        object_id = ObjectId(id)
    except:
        return jsonify({'error': 'ID inválido'}), 400

    cliente = clientes_collection.find_one({'_id': object_id})

    if not cliente:
        return jsonify({'error': 'Cliente no encontrado'}), 404

    return jsonify(cliente_to_dict(cliente))

@app.route('/api/clientes/<id>', methods=['PUT'])
def update_cliente(id):
    try:
        object_id = ObjectId(id)
    except:
        return jsonify({'error': 'ID inválido'}), 400

    data = request.json

    # Construir documento de actualización
    update_data = {}

    campos = [
        'cliente', 'nombre_negocio', 'localidad', 'direccion', 'barrio',
        'dni', 'es_cliente', 'detalle', 'interes_1', 'interes_2', 'interes_3',
        'cantidad_compras', 'intencion_comprar', 'accion', 'comentario'
    ]

    for campo in campos:
        if campo in data:
            valor = data[campo]
            if valor is not None and str(valor).strip():
                update_data[campo] = valor if campo != 'intencion_comprar' else valor.upper()
            else:
                update_data[campo] = None

    # Campos especiales
    if data.get('fecha_nacimiento'):
        try:
            update_data['fecha_nacimiento'] = datetime.strptime(data.get('fecha_nacimiento'), '%Y-%m-%d')
        except:
            pass

    if data.get('años'):
        try:
            update_data['años'] = int(data.get('años'))
        except:
            pass

    # Actualizar en MongoDB
    result = clientes_collection.update_one(
        {'_id': object_id},
        {'$set': update_data}
    )

    if result.matched_count == 0:
        return jsonify({'error': 'Cliente no encontrado'}), 404

    # Obtener cliente actualizado
    cliente_actualizado = clientes_collection.find_one({'_id': object_id})
    return jsonify(cliente_to_dict(cliente_actualizado))

@app.route('/api/clientes/<id>', methods=['DELETE'])
def delete_cliente(id):
    try:
        object_id = ObjectId(id)
    except:
        return jsonify({'error': 'ID inválido'}), 400

    result = clientes_collection.delete_one({'_id': object_id})

    if result.deleted_count == 0:
        return jsonify({'error': 'Cliente no encontrado'}), 404

    return '', 204

@app.route('/api/stats')
def get_stats():
    total = clientes_collection.count_documents({})

    # Agregación para contar por intención
    pipeline = [
        {
            '$group': {
                '_id': '$intencion_comprar',
                'cantidad': {'$sum': 1}
            }
        }
    ]

    intenciones = list(clientes_collection.aggregate(pipeline))

    return jsonify({
        'total': total,
        'por_intencion': [
            {'intencion': i['_id'], 'cantidad': i['cantidad']}
            for i in intenciones
        ]
    })

@app.route('/api/import-excel', methods=['POST'])
def import_excel():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if not file.filename.endswith(('.xlsx', '.xls')):
        return jsonify({'error': 'File must be Excel format'}), 400

    try:
        df = pd.read_excel(file)

        # Mapeo de columnas Excel a campos de base de datos
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
        documentos = []

        for _, row in df.iterrows():
            # Validar que tenga al menos el campo cliente
            if pd.isna(row.get('cliente')) or not str(row.get('cliente')).strip():
                continue

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
                'intencion_comprar': str(row.get('intencion_comprar', 'POCA')).strip().upper(),
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

        # Insertar todos los documentos en MongoDB
        if documentos:
            clientes_collection.insert_many(documentos)

        return jsonify({'message': f'{imported_count} clientes importados correctamente'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/export-excel')
def export_excel():
    clientes = list(clientes_collection.find())

    data = []
    for c in clientes:
        data.append({
            'FECHA': c.get('fecha').strftime('%Y-%m-%d') if c.get('fecha') else '',
            'CLIENTE': c.get('cliente', ''),
            'NOMBRE NEGOCIO': c.get('nombre_negocio', ''),
            'LOCALIDAD': c.get('localidad', ''),
            'DIRECCION': c.get('direccion', ''),
            'BARRIO': c.get('barrio', ''),
            'DNI': c.get('dni', ''),
            'ES CLIENTE?': c.get('es_cliente', ''),
            'DETALLE': c.get('detalle', ''),
            'INTERES 1': c.get('interes_1', ''),
            'INTERES 2': c.get('interes_2', ''),
            'INTERES 3': c.get('interes_3', ''),
            'CANTIDAD COMPRAS': c.get('cantidad_compras', ''),
            'INTENCION DE COMPRAR': c.get('intencion_comprar', ''),
            'ACCION': c.get('accion', ''),
            'COMENTARIO': c.get('comentario', ''),
            'FECHA DE NACIMIENTO': c.get('fecha_nacimiento').strftime('%Y-%m-%d') if c.get('fecha_nacimiento') else '',
            'AÑOS': c.get('años', '')
        })

    df = pd.DataFrame(data)

    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Clientes')
    output.seek(0)

    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=f'clientes_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
    )

@app.route('/api/localidades')
def get_localidades():
    # Obtener localidades únicas usando aggregation
    pipeline = [
        {
            '$match': {
                'localidad': {'$ne': None, '$ne': ''}
            }
        },
        {
            '$group': {
                '_id': '$localidad'
            }
        },
        {
            '$sort': {'_id': 1}
        }
    ]

    localidades = list(clientes_collection.aggregate(pipeline))
    return jsonify([l['_id'] for l in localidades])

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
