import pandas as pd
import json

# Leer el archivo Excel
xl = pd.ExcelFile('Famago 1.9.1 - COMPLETA CON TODAS LAS HOJAS.xlsx')
df = pd.read_excel(xl, sheet_name='CALCULOS', header=None)

# Guardar información en un archivo
with open('calculos_analysis.txt', 'w', encoding='utf-8') as f:
    f.write("="*80 + "\n")
    f.write("ANALISIS DE LA HOJA CALCULOS\n")
    f.write("="*80 + "\n\n")

    f.write(f"Dimensiones: {df.shape[0]} filas x {df.shape[1]} columnas\n\n")

    f.write("="*80 + "\n")
    f.write("PRIMERAS 40 FILAS (todas las columnas con datos)\n")
    f.write("="*80 + "\n\n")

    # Mostrar las primeras 40 filas
    for idx in range(min(40, len(df))):
        f.write(f"\n--- FILA {idx} ---\n")
        for col_idx, val in enumerate(df.iloc[idx]):
            if pd.notna(val):
                f.write(f"  Col {col_idx:2d}: {val}\n")

    f.write("\n" + "="*80 + "\n")
    f.write("RESUMEN DE ESTRUCTURA\n")
    f.write("="*80 + "\n\n")

    # Identificar columnas que más se usan
    for col_idx in range(df.shape[1]):
        non_empty = df.iloc[:, col_idx].notna().sum()
        if non_empty > 0:
            f.write(f"Columna {col_idx:2d}: {non_empty} celdas con datos\n")

print("Analisis guardado en calculos_analysis.txt")
