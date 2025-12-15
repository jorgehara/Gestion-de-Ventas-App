import pandas as pd

df = pd.read_excel('listas_de_precios/lista_de_precios_115.xlsx')

print("Columnas:", df.columns.tolist())
print("\n" + "="*80)
print("FILAS CON DATOS:")
print("="*80)

for idx, row in df.iterrows():
    # Solo mostrar filas que tengan datos relevantes
    producto = row.get('Producto')
    unnamed_2 = row.get('Unnamed: 2')
    unnamed_3 = row.get('Unnamed: 3')
    lista = row.get('Lista')

    if pd.notna(producto) or pd.notna(lista):
        print(f"\nFila {idx}:")
        print(f"  Producto: {producto}")
        print(f"  Unnamed: 2: {unnamed_2}")
        print(f"  Unnamed: 3: {unnamed_3}")
        print(f"  Lista: {lista}")
