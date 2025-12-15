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
    productos_collection = db['productos']
    planes_descuento_collection = db['planes_descuento']

    # Crear índices para mejorar rendimiento
    clientes_collection.create_index('cliente')
    clientes_collection.create_index('localidad')
    clientes_collection.create_index('intencion_comprar')
    productos_collection.create_index('codigo')
    productos_collection.create_index('nombre')

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

# ==========================================
# ENDPOINTS PARA PRODUCTOS Y CALCULOS
# ==========================================

def producto_to_dict(producto):
    """Convierte un documento de producto de MongoDB a diccionario con _id como string"""
    if producto:
        producto['id'] = str(producto['_id'])
        del producto['_id']

        if 'fecha_actualizacion' in producto and isinstance(producto['fecha_actualizacion'], datetime):
            producto['fecha_actualizacion'] = producto['fecha_actualizacion'].strftime('%Y-%m-%d %H:%M:%S')

    return producto

def calcular_precios_por_dia(precio_lista):
    """Calcula los precios por día según las fórmulas de recargo"""
    return {
        '42': round((precio_lista * 1.23) / 42, 3),
        '84': round((precio_lista * 1.42) / 84, 3),
        '135': round((precio_lista * 1.58) / 135, 3),
        '175': round((precio_lista * 1.75) / 175, 3),
        '220': round((precio_lista * 1.92) / 220, 3)
    }

def calcular_precio_final(precio_lista, plan):
    """
    Calcula el precio final según el plan seleccionado

    Args:
        precio_lista: Precio base del producto
        plan: Nombre del plan (ej: 'contado_efectivo', '42_dias', etc.)

    Returns:
        Dict con el desglose completo del cálculo
    """
    # Tabla de descuentos según planes
    descuentos = {
        'contado_efectivo': 34.39,
        '42_dias': 30.75,
        '84_dias': 27.1,
        '135_dias': 27.1,
        '175_dias': 27.1,
        '220_dias': 27.1
    }

    # Tabla de recargos por financiación
    recargos = {
        42: 23,
        84: 42,
        135: 58,
        175: 75,
        220: 92
    }

    if plan == 'contado_efectivo':
        descuento_porcentaje = descuentos['contado_efectivo']
        precio_final = precio_lista * (1 - descuento_porcentaje / 100)

        return {
            'tipo': 'contado',
            'precio_base': round(precio_lista, 2),
            'descuento_porcentaje': descuento_porcentaje,
            'precio_final': round(precio_final, 2),
            'cuota': None,
            'dias': None,
            'total': round(precio_final, 2)
        }
    else:
        # Extraer días del nombre del plan
        dias = int(plan.split('_')[0])

        # Calcular precio por día
        recargo_porcentaje = recargos[dias]
        precio_con_recargo = precio_lista * (1 + recargo_porcentaje / 100)
        precio_por_dia = precio_con_recargo / dias

        # Aplicar descuento
        descuento_porcentaje = descuentos[plan]
        precio_por_dia_final = precio_por_dia * (1 - descuento_porcentaje / 100)
        total = precio_por_dia_final * dias

        return {
            'tipo': 'financiado',
            'precio_base': round(precio_lista, 2),
            'recargo_porcentaje': recargo_porcentaje,
            'precio_con_recargo': round(precio_con_recargo, 2),
            'precio_por_dia_sin_descuento': round(precio_por_dia, 3),
            'descuento_porcentaje': descuento_porcentaje,
            'precio_por_dia_final': round(precio_por_dia_final, 3),
            'dias': dias,
            'total': round(total, 2)
        }

# ENDPOINTS PRODUCTOS

@app.route('/api/productos', methods=['GET'])
def get_productos():
    """Obtener todos los productos"""
    try:
        productos = list(productos_collection.find({'activo': True}).sort('nombre', 1))
        return jsonify([producto_to_dict(p) for p in productos])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/productos/<id>', methods=['GET'])
def get_producto(id):
    """Obtener un producto por ID"""
    try:
        object_id = ObjectId(id)
    except:
        return jsonify({'error': 'ID inválido'}), 400

    producto = productos_collection.find_one({'_id': object_id})

    if not producto:
        return jsonify({'error': 'Producto no encontrado'}), 404

    return jsonify(producto_to_dict(producto))

@app.route('/api/productos', methods=['POST'])
def add_producto():
    """Crear nuevo producto"""
    data = request.json

    # Validar campos requeridos
    if not data.get('nombre') or not data.get('precio_lista'):
        return jsonify({'error': 'Nombre y precio de lista son requeridos'}), 400

    try:
        precio_lista = float(data.get('precio_lista'))
    except:
        return jsonify({'error': 'Precio de lista debe ser un número'}), 400

    # Crear documento
    nuevo_producto = {
        'codigo': data.get('codigo', '').strip(),
        'nombre': data.get('nombre', '').strip(),
        'precio_lista': precio_lista,
        'fecha_actualizacion': datetime.now(),
        'activo': True
    }

    # Calcular precios por día
    precios_por_dia = calcular_precios_por_dia(precio_lista)
    nuevo_producto['precios_por_dia'] = precios_por_dia

    result = productos_collection.insert_one(nuevo_producto)
    nuevo_producto['_id'] = result.inserted_id

    return jsonify(producto_to_dict(nuevo_producto)), 201

@app.route('/api/productos/<id>', methods=['PUT'])
def update_producto(id):
    """Actualizar producto"""
    try:
        object_id = ObjectId(id)
    except:
        return jsonify({'error': 'ID inválido'}), 400

    data = request.json

    update_data = {
        'fecha_actualizacion': datetime.now()
    }

    if 'codigo' in data:
        update_data['codigo'] = data['codigo'].strip()
    if 'nombre' in data:
        update_data['nombre'] = data['nombre'].strip()
    if 'precio_lista' in data:
        try:
            precio_lista = float(data['precio_lista'])
            update_data['precio_lista'] = precio_lista
            # Recalcular precios por día
            update_data['precios_por_dia'] = calcular_precios_por_dia(precio_lista)
        except:
            return jsonify({'error': 'Precio de lista debe ser un número'}), 400

    result = productos_collection.update_one(
        {'_id': object_id},
        {'$set': update_data}
    )

    if result.matched_count == 0:
        return jsonify({'error': 'Producto no encontrado'}), 404

    producto = productos_collection.find_one({'_id': object_id})
    return jsonify(producto_to_dict(producto))

@app.route('/api/productos/<id>', methods=['DELETE'])
def delete_producto(id):
    """Eliminar producto (soft delete)"""
    try:
        object_id = ObjectId(id)
    except:
        return jsonify({'error': 'ID inválido'}), 400

    result = productos_collection.update_one(
        {'_id': object_id},
        {'$set': {'activo': False}}
    )

    if result.matched_count == 0:
        return jsonify({'error': 'Producto no encontrado'}), 404

    return '', 204

# ENDPOINT DE CALCULO

@app.route('/api/calcular', methods=['POST'])
def calcular():
    """
    Calcular precio final según producto y plan
    Body: { "producto_id": "...", "plan": "contado_efectivo" }
    """
    data = request.json

    if not data.get('producto_id') or not data.get('plan'):
        return jsonify({'error': 'producto_id y plan son requeridos'}), 400

    try:
        object_id = ObjectId(data['producto_id'])
    except:
        return jsonify({'error': 'producto_id inválido'}), 400

    producto = productos_collection.find_one({'_id': object_id})

    if not producto:
        return jsonify({'error': 'Producto no encontrado'}), 404

    plan = data['plan']
    precio_lista = producto['precio_lista']

    # Validar plan
    planes_validos = ['contado_efectivo', '42_dias', '84_dias', '135_dias', '175_dias', '220_dias']
    if plan not in planes_validos:
        return jsonify({'error': f'Plan inválido. Planes válidos: {", ".join(planes_validos)}'}), 400

    resultado = calcular_precio_final(precio_lista, plan)
    resultado['producto'] = {
        'id': str(producto['_id']),
        'codigo': producto.get('codigo', ''),
        'nombre': producto.get('nombre', '')
    }

    return jsonify(resultado)

# ENDPOINT DE IMPORTACION

@app.route('/api/import-productos-excel', methods=['POST'])
def import_productos_excel():
    """Importar productos desde Excel (hoja de precios)"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if not file.filename.endswith(('.xlsx', '.xls')):
        return jsonify({'error': 'File must be Excel format'}), 400

    try:
        # Leer Excel
        df = pd.read_excel(file)

        # Validar columnas necesarias
        if 'Producto' not in df.columns or 'Lista' not in df.columns:
            return jsonify({'error': 'Excel debe contener columnas: Producto, Lista'}), 400

        imported_count = 0
        updated_count = 0

        for _, row in df.iterrows():
            # Validar que tenga producto y precio
            if pd.isna(row.get('Producto')) or pd.isna(row.get('Lista')):
                continue

            nombre = str(row['Producto']).strip()
            precio_lista = float(row['Lista'])

            # Verificar si ya existe (por nombre)
            producto_existente = productos_collection.find_one({'nombre': nombre})

            if producto_existente:
                # Actualizar
                productos_collection.update_one(
                    {'_id': producto_existente['_id']},
                    {'$set': {
                        'precio_lista': precio_lista,
                        'precios_por_dia': calcular_precios_por_dia(precio_lista),
                        'fecha_actualizacion': datetime.now()
                    }}
                )
                updated_count += 1
            else:
                # Crear nuevo
                nuevo_producto = {
                    'codigo': '',
                    'nombre': nombre,
                    'precio_lista': precio_lista,
                    'precios_por_dia': calcular_precios_por_dia(precio_lista),
                    'fecha_actualizacion': datetime.now(),
                    'activo': True
                }
                productos_collection.insert_one(nuevo_producto)
                imported_count += 1

        return jsonify({
            'message': f'{imported_count} productos importados, {updated_count} actualizados'
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/import-productos-pdf', methods=['POST'])
def import_productos_pdf():
    """
    Importa/actualiza productos desde PDF de lista de precios
    """
    import pdfplumber
    import re

    def calcular_precios_por_dia_local(precio_lista):
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
        texto = texto.strip().replace('.', '').replace(',', '.')
        try:
            return float(texto)
        except:
            return None

    def extraer_codigo(texto):
        """Extrae código del producto"""
        if not texto:
            return None
        match = re.search(r'\(([^\)]+)\)|^(\d+)', texto.strip())
        if match:
            return match.group(1) or match.group(2)
        return None

    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No se envió ningún archivo'}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({'error': 'No se seleccionó ningún archivo'}), 400

        if not file.filename.endswith('.pdf'):
            return jsonify({'error': 'El archivo debe ser un PDF'}), 400

        # Guardar temporalmente el PDF
        temp_path = os.path.join('uploads', file.filename)
        os.makedirs('uploads', exist_ok=True)
        file.save(temp_path)

        # Procesar PDF
        productos_procesados = []

        with pdfplumber.open(temp_path) as pdf:
            for page in pdf.pages:
                table = page.extract_table()

                if not table:
                    continue

                # Buscar encabezado
                header_idx = None
                for idx, row in enumerate(table):
                    if row and any('Producto' in str(cell) for cell in row if cell):
                        header_idx = idx
                        break

                if header_idx is None:
                    continue

                # Procesar filas
                for row in table[header_idx + 1:]:
                    if not row or len(row) < 2:
                        continue

                    producto_col = row[0]
                    lista_col = row[1] if len(row) > 1 else None

                    if not producto_col or not lista_col:
                        continue

                    if 'Categoría:' in str(producto_col) or 'Línea:' in str(producto_col):
                        continue

                    codigo = extraer_codigo(producto_col)
                    nombre = producto_col

                    if codigo:
                        nombre = re.sub(r'\([^\)]+\)\s*', '', nombre).strip()
                        nombre = re.sub(r'^\d+\s+', '', nombre).strip()

                    precio_lista = limpiar_numero(lista_col)

                    if not nombre or not precio_lista or precio_lista <= 0:
                        continue

                    productos_procesados.append({
                        'codigo': codigo,
                        'nombre': nombre,
                        'precio_lista': precio_lista
                    })

        # Eliminar archivo temporal
        os.remove(temp_path)

        # Importar/actualizar en MongoDB
        stats = {
            'creados': 0,
            'actualizados': 0,
            'errores': 0,
            'sin_cambios': 0
        }

        for producto in productos_procesados:
            try:
                codigo = producto.get('codigo')
                nombre = producto['nombre']
                precio_lista = producto['precio_lista']

                precios_por_dia = calcular_precios_por_dia_local(precio_lista)

                # Buscar producto existente
                query = {}
                if codigo:
                    query = {'codigo': codigo}
                else:
                    query = {'nombre': {'$regex': f'^{re.escape(nombre)}$', '$options': 'i'}}

                producto_existente = productos_collection.find_one(query)

                if producto_existente:
                    # Actualizar solo si cambió el precio
                    if producto_existente.get('precio_lista') != precio_lista:
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
                    else:
                        stats['sin_cambios'] += 1
                else:
                    # Crear nuevo producto
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

            except Exception as e:
                stats['errores'] += 1
                print(f"Error procesando producto: {e}")

        return jsonify({
            'success': True,
            'message': f'Importación completada',
            'stats': stats,
            'total_procesados': len(productos_procesados)
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
