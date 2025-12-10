import pandas as pd
from app import app, db, Cliente
from datetime import datetime

def import_initial_data():
    with app.app_context():
        # Check if database already has data
        if Cliente.query.count() > 0:
            print(f"Base de datos ya contiene {Cliente.query.count()} registros")
            response = input("¿Desea limpiar y reimportar? (s/n): ")
            if response.lower() != 's':
                print("Importación cancelada")
                return
            
            # Clear existing data
            Cliente.query.delete()
            db.session.commit()
            print("Base de datos limpiada")
        
        # Read Excel file
        file_path = '/mnt/user-data/uploads/Famago_1_9_1_-_copia.xlsx'
        df = pd.read_excel(file_path)
        
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
        
        for idx, row in df.iterrows():
            try:
                if pd.isna(row.get('cliente')) or not str(row.get('cliente')).strip():
                    continue
                
                # Normalize intencion_comprar
                intencion = str(row.get('intencion_comprar', 'POCA')).strip().upper()
                if intencion in ['POCA', 'POCA']:
                    intencion = 'POCA'
                
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
                    intencion_comprar=intencion,
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
                
                if imported_count % 100 == 0:
                    print(f"Importados {imported_count} registros...")
                    
            except Exception as e:
                errors += 1
                print(f"Error en fila {idx}: {e}")
        
        db.session.commit()
        print(f"\n✅ Importación completada!")
        print(f"Total importados: {imported_count}")
        print(f"Errores: {errors}")

if __name__ == '__main__':
    import_initial_data()
