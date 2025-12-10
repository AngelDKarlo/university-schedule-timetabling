#!/home/angel/Politecnica/Estructuras de Datos/pf/venv/bin/python3
"""
Script temporal para analizar el Excel y entender la estructura
"""
import pandas as pd
import os

os.chdir('/home/angel/Politecnica/Estructuras de Datos/pf')

# Leer Excel
df = pd.read_excel('Horarios EneAbr18 (1).xlsx', sheet_name='Matriz ITI', header=None)

print("📊 ESTRUCTURA DEL EXCEL")
print("="*80)
print(f"Dimensiones: {df.shape}")
print(f"\nPrimera fila (encabezados):")
print(df.iloc[0, :10].tolist())

print(f"\nSegunda fila (profesores):")
print(df.iloc[1, 4:10].tolist())

print("\n📋 GRUPOS DETECTADOS:")
grupos_encontrados = []
for idx, row in df.iterrows():
    valor = str(row.iloc[0]).strip()
    if 'ITI' in valor and ('Matutino' in valor or 'Vespertino' in valor):
        print(f"  Fila {idx}: {valor}")
        grupos_encontrados.append((idx, valor))

print(f"\n✅ Total grupos encontrados: {len(grupos_encontrados)}")

print("\n📚 EJEMPLO DE CURSO (Algoritmos):")
for idx, row in df.iterrows():
    valor = str(row.iloc[0]).strip()
    if valor == 'Algoritmos':
        print(f"  Fila {idx}: {row.iloc[0:4].tolist()}")
        print(f"  Horas profesores: {[x for x in row.iloc[4:10].tolist() if pd.notna(x) and x != 0]}")
        break
