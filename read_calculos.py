import pandas as pd
import sys

# Leer el archivo Excel
xl = pd.ExcelFile('Famago 1.9.1 - COMPLETA CON TODAS LAS HOJAS.xlsx')
df = pd.read_excel(xl, sheet_name='CALCULOS', header=None)

print("Dimensiones de la hoja CALCULOS:")
print(f"Filas: {df.shape[0]}, Columnas: {df.shape[1]}")
print("\n" + "="*80)
print("Primeras 30 filas y 15 columnas:")
print("="*80)

# Mostrar las primeras filas y columnas
for idx in range(min(30, len(df))):
    row_data = []
    for col in range(min(15, len(df.columns))):
        val = df.iloc[idx, col]
        if pd.isna(val):
            row_data.append("---")
        else:
            row_data.append(str(val)[:30])
    print(f"Fila {idx:2d}: {' | '.join(row_data)}")

print("\n" + "="*80)
print("Analizando estructura...")
print("="*80)

# Buscar filas que parezcan encabezados
for idx in range(min(10, len(df))):
    non_empty = df.iloc[idx].notna().sum()
    if non_empty > 5:
        print(f"Fila {idx} tiene {non_empty} celdas con datos")
