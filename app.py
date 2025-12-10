from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pandas as pd
import os
from io import BytesIO

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///clientes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max
db = SQLAlchemy(app)

class Cliente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.DateTime, default=datetime.now)
    cliente = db.Column(db.String(200), nullable=False)
    nombre_negocio = db.Column(db.String(200))
    localidad = db.Column(db.String(100))
    direccion = db.Column(db.String(200))
    barrio = db.Column(db.String(100))
    dni = db.Column(db.String(20))
    es_cliente = db.Column(db.String(20))
    detalle = db.Column(db.Text)
    interes_1 = db.Column(db.String(100))
    interes_2 = db.Column(db.String(100))
    interes_3 = db.Column(db.String(100))
    cantidad_compras = db.Column(db.String(50))
    intencion_comprar = db.Column(db.String(50), nullable=False)
    accion = db.Column(db.String(200))
    comentario = db.Column(db.Text)
    fecha_nacimiento = db.Column(db.Date)
    años = db.Column(db.Integer)

    def to_dict(self):
        return {
            'id': self.id,
            'fecha': self.fecha.strftime('%Y-%m-%d') if self.fecha else '',
            'cliente': self.cliente,
            'nombre_negocio': self.nombre_negocio or '',
            'localidad': self.localidad or '',
            'direccion': self.direccion or '',
            'barrio': self.barrio or '',
            'dni': self.dni or '',
            'es_cliente': self.es_cliente or '',
            'detalle': self.detalle or '',
            'interes_1': self.interes_1 or '',
            'interes_2': self.interes_2 or '',
            'interes_3': self.interes_3 or '',
            'cantidad_compras': self.cantidad_compras or '',
            'intencion_comprar': self.intencion_comprar,
            'accion': self.accion or '',
            'comentario': self.comentario or '',
            'fecha_nacimiento': self.fecha_nacimiento.strftime('%Y-%m-%d') if self.fecha_nacimiento else '',
            'años': self.años or ''
        }

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/clientes', methods=['GET'])
def get_clientes():
    localidad = request.args.get('localidad', '')
    intencion = request.args.get('intencion', '')
    search = request.args.get('search', '')
    
    query = Cliente.query
    
    if localidad:
        query = query.filter(Cliente.localidad.ilike(f'%{localidad}%'))
    if intencion:
        query = query.filter(Cliente.intencion_comprar.ilike(f'%{intencion}%'))
    if search:
        query = query.filter(
            db.or_(
                Cliente.cliente.ilike(f'%{search}%'),
                Cliente.nombre_negocio.ilike(f'%{search}%'),
                Cliente.comentario.ilike(f'%{search}%')
            )
        )
    
    clientes = query.order_by(Cliente.fecha.desc()).all()
    return jsonify([c.to_dict() for c in clientes])

@app.route('/api/clientes', methods=['POST'])
def add_cliente():
    data = request.json
    
    nuevo_cliente = Cliente(
        cliente=data.get('cliente'),
        nombre_negocio=data.get('nombre_negocio'),
        localidad=data.get('localidad'),
        direccion=data.get('direccion'),
        barrio=data.get('barrio'),
        dni=data.get('dni'),
        es_cliente=data.get('es_cliente'),
        detalle=data.get('detalle'),
        interes_1=data.get('interes_1'),
        interes_2=data.get('interes_2'),
        interes_3=data.get('interes_3'),
        cantidad_compras=data.get('cantidad_compras'),
        intencion_comprar=data.get('intencion_comprar'),
        accion=data.get('accion'),
        comentario=data.get('comentario')
    )
    
    if data.get('fecha_nacimiento'):
        try:
            nuevo_cliente.fecha_nacimiento = datetime.strptime(data.get('fecha_nacimiento'), '%Y-%m-%d').date()
        except:
            pass
    
    if data.get('años'):
        try:
            nuevo_cliente.años = int(data.get('años'))
        except:
            pass
    
    db.session.add(nuevo_cliente)
    db.session.commit()
    
    return jsonify(nuevo_cliente.to_dict()), 201

@app.route('/api/clientes/<int:id>', methods=['PUT'])
def update_cliente(id):
    cliente = Cliente.query.get_or_404(id)
    data = request.json
    
    cliente.cliente = data.get('cliente', cliente.cliente)
    cliente.nombre_negocio = data.get('nombre_negocio')
    cliente.localidad = data.get('localidad')
    cliente.direccion = data.get('direccion')
    cliente.barrio = data.get('barrio')
    cliente.dni = data.get('dni')
    cliente.es_cliente = data.get('es_cliente')
    cliente.detalle = data.get('detalle')
    cliente.interes_1 = data.get('interes_1')
    cliente.interes_2 = data.get('interes_2')
    cliente.interes_3 = data.get('interes_3')
    cliente.cantidad_compras = data.get('cantidad_compras')
    cliente.intencion_comprar = data.get('intencion_comprar', cliente.intencion_comprar)
    cliente.accion = data.get('accion')
    cliente.comentario = data.get('comentario')
    
    if data.get('fecha_nacimiento'):
        try:
            cliente.fecha_nacimiento = datetime.strptime(data.get('fecha_nacimiento'), '%Y-%m-%d').date()
        except:
            pass
    
    if data.get('años'):
        try:
            cliente.años = int(data.get('años'))
        except:
            pass
    
    db.session.commit()
    return jsonify(cliente.to_dict())

@app.route('/api/clientes/<int:id>', methods=['DELETE'])
def delete_cliente(id):
    cliente = Cliente.query.get_or_404(id)
    db.session.delete(cliente)
    db.session.commit()
    return '', 204

@app.route('/api/stats')
def get_stats():
    total = Cliente.query.count()
    
    intenciones = db.session.query(
        Cliente.intencion_comprar,
        db.func.count(Cliente.id)
    ).group_by(Cliente.intencion_comprar).all()
    
    return jsonify({
        'total': total,
        'por_intencion': [{'intencion': i[0], 'cantidad': i[1]} for i in intenciones]
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
        for _, row in df.iterrows():
            if pd.isna(row.get('cliente')) or not str(row.get('cliente')).strip():
                continue
                
            cliente = Cliente(
                cliente=str(row.get('cliente', '')).strip(),
                nombre_negocio=str(row.get('nombre_negocio', '')) if pd.notna(row.get('nombre_negocio')) else None,
                localidad=str(row.get('localidad', '')) if pd.notna(row.get('localidad')) else None,
                direccion=str(row.get('direccion', '')) if pd.notna(row.get('direccion')) else None,
                barrio=str(row.get('barrio', '')) if pd.notna(row.get('barrio')) else None,
                dni=str(row.get('dni', '')) if pd.notna(row.get('dni')) else None,
                es_cliente=str(row.get('es_cliente', '')) if pd.notna(row.get('es_cliente')) else None,
                detalle=str(row.get('detalle', '')) if pd.notna(row.get('detalle')) else None,
                interes_1=str(row.get('interes_1', '')) if pd.notna(row.get('interes_1')) else None,
                interes_2=str(row.get('interes_2', '')) if pd.notna(row.get('interes_2')) else None,
                interes_3=str(row.get('interes_3', '')) if pd.notna(row.get('interes_3')) else None,
                cantidad_compras=str(row.get('cantidad_compras', '')) if pd.notna(row.get('cantidad_compras')) else None,
                intencion_comprar=str(row.get('intencion_comprar', 'POCA')).strip().upper(),
                accion=str(row.get('accion', '')) if pd.notna(row.get('accion')) else None,
                comentario=str(row.get('comentario', '')) if pd.notna(row.get('comentario')) else None
            )
            
            if pd.notna(row.get('fecha')):
                try:
                    cliente.fecha = pd.to_datetime(row['fecha'])
                except:
                    cliente.fecha = datetime.now()
            else:
                cliente.fecha = datetime.now()
            
            if pd.notna(row.get('fecha_nacimiento')):
                try:
                    cliente.fecha_nacimiento = pd.to_datetime(row['fecha_nacimiento']).date()
                except:
                    pass
            
            if pd.notna(row.get('años')):
                try:
                    cliente.años = int(row['años'])
                except:
                    pass
            
            db.session.add(cliente)
            imported_count += 1
        
        db.session.commit()
        return jsonify({'message': f'{imported_count} clientes importados correctamente'})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/export-excel')
def export_excel():
    clientes = Cliente.query.all()
    
    data = []
    for c in clientes:
        data.append({
            'FECHA': c.fecha.strftime('%Y-%m-%d') if c.fecha else '',
            'CLIENTE': c.cliente,
            'NOMBRE NEGOCIO': c.nombre_negocio or '',
            'LOCALIDAD': c.localidad or '',
            'DIRECCION': c.direccion or '',
            'BARRIO': c.barrio or '',
            'DNI': c.dni or '',
            'ES CLIENTE?': c.es_cliente or '',
            'DETALLE': c.detalle or '',
            'INTERES 1': c.interes_1 or '',
            'INTERES 2': c.interes_2 or '',
            'INTERES 3': c.interes_3 or '',
            'CANTIDAD COMPRAS': c.cantidad_compras or '',
            'INTENCION DE COMPRAR': c.intencion_comprar,
            'ACCION': c.accion or '',
            'COMENTARIO': c.comentario or '',
            'FECHA DE NACIMIENTO': c.fecha_nacimiento.strftime('%Y-%m-%d') if c.fecha_nacimiento else '',
            'AÑOS': c.años or ''
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
    localidades = db.session.query(Cliente.localidad).distinct().filter(Cliente.localidad.isnot(None)).all()
    return jsonify([l[0] for l in localidades if l[0]])

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
