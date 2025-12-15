"""
Script de prueba para el sistema de cálculos
Prueba con el ejemplo real: Caja De Dinero Acero 5 Divisiones
"""
import requests
import json

BASE_URL = 'http://localhost:5000/api'

def test_crear_producto():
    """Crear producto de prueba"""
    print("\n" + "="*60)
    print("1. CREANDO PRODUCTO DE PRUEBA")
    print("="*60)

    data = {
        'codigo': 'TEST001',
        'nombre': 'Caja De Dinero Acero 5 Divisiones',
        'precio_lista': 173673
    }

    response = requests.post(f'{BASE_URL}/productos', json=data)

    if response.status_code == 201:
        producto = response.json()
        print(f"✓ Producto creado exitosamente")
        print(f"  ID: {producto['id']}")
        print(f"  Nombre: {producto['nombre']}")
        print(f"  Precio Lista: ${producto['precio_lista']:,.2f}")
        print(f"\n  Precios por día calculados:")
        for dias, precio in producto['precios_por_dia'].items():
            print(f"    {dias} días: ${precio:,.3f}")
        return producto['id']
    else:
        print(f"✗ Error: {response.json()}")
        return None

def test_calcular_contado(producto_id):
    """Probar cálculo de contado efectivo"""
    print("\n" + "="*60)
    print("2. CALCULANDO PRECIO CONTADO EFECTIVO")
    print("="*60)

    data = {
        'producto_id': producto_id,
        'plan': 'contado_efectivo'
    }

    response = requests.post(f'{BASE_URL}/calcular', json=data)

    if response.status_code == 200:
        resultado = response.json()
        print(f"✓ Cálculo exitoso")
        print(f"  Producto: {resultado['producto']['nombre']}")
        print(f"  Precio Base: ${resultado['precio_base']:,.2f}")
        print(f"  Descuento: {resultado['descuento_porcentaje']}%")
        print(f"  PRECIO FINAL: ${resultado['total']:,.2f}")

        # Verificar cálculo
        esperado = 173673 * (1 - 0.3439)
        print(f"\n  Verificación:")
        print(f"    Calculado: ${resultado['total']:,.2f}")
        print(f"    Esperado:  ${esperado:,.2f}")
        print(f"    ✓ Correcto" if abs(resultado['total'] - esperado) < 1 else "    ✗ Error")
    else:
        print(f"✗ Error: {response.json()}")

def test_calcular_42_dias(producto_id):
    """Probar cálculo de 42 días"""
    print("\n" + "="*60)
    print("3. CALCULANDO PRECIO 42 DÍAS")
    print("="*60)

    data = {
        'producto_id': producto_id,
        'plan': '42_dias'
    }

    response = requests.post(f'{BASE_URL}/calcular', json=data)

    if response.status_code == 200:
        resultado = response.json()
        print(f"✓ Cálculo exitoso")
        print(f"  Producto: {resultado['producto']['nombre']}")
        print(f"  Precio Base: ${resultado['precio_base']:,.2f}")
        print(f"  Recargo Financiación: +{resultado['recargo_porcentaje']}%")
        print(f"  Precio con Recargo: ${resultado['precio_con_recargo']:,.2f}")
        print(f"  Precio por Día (sin desc.): ${resultado['precio_por_dia_sin_descuento']:,.3f}")
        print(f"  Descuento: {resultado['descuento_porcentaje']}%")
        print(f"  Precio por Día Final: ${resultado['precio_por_dia_final']:,.3f}")
        print(f"  Días: {resultado['dias']}")
        print(f"  TOTAL: ${resultado['total']:,.2f}")

        # Verificar cálculo
        precio_con_recargo = 173673 * 1.23
        precio_por_dia = precio_con_recargo / 42
        precio_por_dia_final = precio_por_dia * (1 - 0.3075)
        total_esperado = precio_por_dia_final * 42

        print(f"\n  Verificación paso a paso:")
        print(f"    Precio base: ${173673:,.2f}")
        print(f"    + 23% recargo: ${precio_con_recargo:,.2f}")
        print(f"    / 42 días: ${precio_por_dia:,.3f}")
        print(f"    - 30.75% desc: ${precio_por_dia_final:,.3f}")
        print(f"    × 42 días: ${total_esperado:,.2f}")
        print(f"\n    Calculado: ${resultado['total']:,.2f}")
        print(f"    Esperado:  ${total_esperado:,.2f}")
        print(f"    ✓ Correcto" if abs(resultado['total'] - total_esperado) < 1 else "    ✗ Error")
    else:
        print(f"✗ Error: {response.json()}")

def test_calcular_todos_planes(producto_id):
    """Probar todos los planes"""
    print("\n" + "="*60)
    print("4. CALCULANDO TODOS LOS PLANES")
    print("="*60)

    planes = {
        'contado_efectivo': 'Contado Efectivo',
        '42_dias': '42 Días',
        '84_dias': '84 Días',
        '135_dias': '135 Días',
        '175_dias': '175 Días',
        '220_dias': '220 Días'
    }

    print(f"\n{'Plan':<20} {'Precio Final':>15} {'Cuota/Día':>15}")
    print("-" * 60)

    for plan_key, plan_nombre in planes.items():
        data = {
            'producto_id': producto_id,
            'plan': plan_key
        }

        response = requests.post(f'{BASE_URL}/calcular', json=data)

        if response.status_code == 200:
            resultado = response.json()
            cuota = resultado.get('precio_por_dia_final', '-')
            cuota_str = f"${cuota:,.3f}" if cuota != '-' else '-'
            print(f"{plan_nombre:<20} ${resultado['total']:>14,.2f} {cuota_str:>15}")
        else:
            print(f"{plan_nombre:<20} ERROR")

def main():
    print("\n")
    print("=" * 60)
    print(" " * 10 + "PRUEBA DEL SISTEMA DE CALCULOS")
    print("=" * 60)

    try:
        # Crear producto
        producto_id = test_crear_producto()

        if producto_id:
            # Probar cálculos
            test_calcular_contado(producto_id)
            test_calcular_42_dias(producto_id)
            test_calcular_todos_planes(producto_id)

            print("\n" + "="*60)
            print("✓ TODAS LAS PRUEBAS COMPLETADAS")
            print("="*60 + "\n")

    except requests.exceptions.ConnectionError:
        print("\n✗ Error: No se pudo conectar al servidor")
        print("  Asegúrate de que Flask esté corriendo en http://localhost:5000\n")
    except Exception as e:
        print(f"\n✗ Error inesperado: {e}\n")

if __name__ == '__main__':
    main()
