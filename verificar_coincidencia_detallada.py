#!/usr/bin/env python3
"""
Verificación DETALLADA - Análisis completo de coincidencia
"""

import pandas as pd
import os

os.chdir('/home/angel/Politecnica/Estructuras de Datos/pf')

# Leer la Matriz ITI del Excel
df = pd.read_excel('Horarios EneAbr18 (1).xlsx', sheet_name='Matriz ITI', header=None)

print("=" * 120)
print("🔍 VERIFICACIÓN DETALLADA - ANÁLISIS COMPLETO DE COINCIDENCIA")
print("=" * 120)
print()

# Estructura esperada según el documento compartido
estructura_documento = [
    {
        "seccion": "Primer Cuatrimestre - Vespertino (ITI 1-1)",
        "materias": [
            {"nombre": "Inglés I", "grupos": 0, "horas_materia": 5, "horas_semana": 0},
            {"nombre": "Valores del Ser", "grupos": 0, "horas_materia": 3, "horas_semana": 0},
            {"nombre": "Algoritmos", "grupos": 1, "horas_materia": 6, "horas_semana": 6},
            {"nombre": "Herramientas Ofimáticas", "grupos": 1, "horas_materia": 4, "horas_semana": 4},
            {"nombre": "Introducción a la ITI", "grupos": 1, "horas_materia": 3, "horas_semana": 3},
            {"nombre": "Arquitectura de Computadoras", "grupos": 1, "horas_materia": 5, "horas_semana": 5},
            {"nombre": "Matemáticas Básicas", "grupos": 1, "horas_materia": 6, "horas_semana": 6},
        ]
    },
    {
        "seccion": "Segundo Cuatrimestre - Matutino (ITI 2-1, ITI 2-2)",
        "materias": [
            {"nombre": "Lógica Computacional", "grupos": 0, "horas_materia": 5, "horas_semana": 0},
            {"nombre": "Inteligencia Emocional", "grupos": 2, "horas_materia": 3, "horas_semana": 6},
            {"nombre": "", "grupos": 2, "horas_materia": 6, "horas_semana": 12},  # Fila vacía
            {"nombre": "Herramientas Multimedia", "grupos": 2, "horas_materia": 4, "horas_semana": 8},
            {"nombre": "Fundamentos de Redes", "grupos": 2, "horas_materia": 5, "horas_semana": 10},
            {"nombre": "Fundamentos de Física", "grupos": 2, "horas_materia": 6, "horas_semana": 12},
            {"nombre": "Matemáticas Discretas", "grupos": 2, "horas_materia": 6, "horas_semana": 12},
        ]
    },
    {
        "seccion": "Segundo Cuatrimestre - Vespertino (ITI 2-3)",
        "materias": [
            {"nombre": "Inglés II", "grupos": 0, "horas_materia": 5, "horas_semana": 0},
            {"nombre": "Inteligencia Emocional", "grupos": 1, "horas_materia": 3, "horas_semana": 3},
            {"nombre": "Lógica Computacional", "grupos": 1, "horas_materia": 6, "horas_semana": 6},
            {"nombre": "Herramientas Multimedia", "grupos": 1, "horas_materia": 4, "horas_semana": 4},
            {"nombre": "Fundamentos de Redes", "grupos": 1, "horas_materia": 5, "horas_semana": 5},
            {"nombre": "Fundamentos de Física", "grupos": 1, "horas_materia": 6, "horas_semana": 6},
            {"nombre": "Matemáticas Discretas", "grupos": 1, "horas_materia": 6, "horas_semana": 6},
        ]
    },
    {
        "seccion": "Cuarto Cuatrimestre - Vespertino (ITI 4-1)",
        "materias": [
            {"nombre": "Inglés IV", "grupos": 0, "horas_materia": 6, "horas_semana": 0},
            {"nombre": "Habilidades del Pensamiento", "grupos": 1, "horas_materia": 4, "horas_semana": 4},
            {"nombre": "Introducción a la Programación Orientada a Objetos", "grupos": 1, "horas_materia": 6, "horas_semana": 6},
            {"nombre": "Introducción a las Bases de Datos", "grupos": 1, "horas_materia": 5, "horas_semana": 5},
            {"nombre": "Switcheo y Wireless", "grupos": 1, "horas_materia": 6, "horas_semana": 6},
            {"nombre": "Álgebra Lineal", "grupos": 1, "horas_materia": 6, "horas_semana": 6},
            {"nombre": "Estancia I", "grupos": 1, "horas_materia": 0, "horas_semana": 0},
        ]
    },
]

# Obtener datos del Excel
materias_excel = {}
seccion_actual = None

for idx, row in df.iterrows():
    nombre = str(row.iloc[0]).strip()
    
    # Detectar secciones
    if 'Cuatrimestre' in nombre or 'Matutino' in nombre or 'Vespertino' in nombre:
        if 'Primer Cuatrimestre' in nombre:
            seccion_actual = "Primer Cuatrimestre"
        elif 'Segundo Cuatrimestre' in nombre:
            seccion_actual = "Segundo Cuatrimestre"
        elif 'Cuarto Cuatrimestre' in nombre:
            seccion_actual = "Cuarto Cuatrimestre"
        elif 'Matutino' in nombre and seccion_actual:
            seccion_actual = f"{seccion_actual} - Matutino"
        elif 'Vespertino' in nombre and seccion_actual:
            if 'ITI 1-1' in nombre:
                seccion_actual = "Primer Cuatrimestre - Vespertino (ITI 1-1)"
            elif 'ITI 2-3' in nombre:
                seccion_actual = "Segundo Cuatrimestre - Vespertino (ITI 2-3)"
            elif 'ITI 4-1' in nombre:
                seccion_actual = "Cuarto Cuatrimestre - Vespertino (ITI 4-1)"
        continue
    
    # Saltar filas vacías o de control
    if nombre in ['', 'nan', 'Horas Asignadas', 'Totales', 'Horas restantes']:
        continue
    
    # Extraer datos
    grupos = int(row.iloc[1]) if pd.notna(row.iloc[1]) else 0
    horas_materia = int(row.iloc[2]) if pd.notna(row.iloc[2]) else 0
    horas_semana = int(row.iloc[3]) if pd.notna(row.iloc[3]) else 0
    
    if seccion_actual:
        if seccion_actual not in materias_excel:
            materias_excel[seccion_actual] = []
        materias_excel[seccion_actual].append({
            "nombre": nombre,
            "grupos": grupos,
            "horas_materia": horas_materia,
            "horas_semana": horas_semana
        })

# Comparar
total_verificaciones = 0
coincidencias_exactas = 0
diferencias = []

for seccion_doc in estructura_documento:
    nombre_seccion = seccion_doc["seccion"]
    print(f"\n{'='*120}")
    print(f"📚 {nombre_seccion}")
    print(f"{'='*120}")
    print(f"{'Materia':<60} {'Grupos':^10} {'H.Mat':^10} {'H.Sem':^10} {'Estado':^15}")
    print(f"{'-'*120}")
    
    materias_doc = seccion_doc["materias"]
    materias_excel_seccion = materias_excel.get(nombre_seccion, [])
    
    for mat_doc in materias_doc:
        nombre = mat_doc["nombre"]
        
        # Buscar en Excel
        mat_excel = next((m for m in materias_excel_seccion if m["nombre"] == nombre), None)
        
        if mat_excel:
            # Comparar
            coincide_grupos = mat_doc["grupos"] == mat_excel["grupos"]
            coincide_horas_mat = mat_doc["horas_materia"] == mat_excel["horas_materia"]
            coincide_horas_sem = mat_doc["horas_semana"] == mat_excel["horas_semana"]
            
            total_verificaciones += 3
            
            if coincide_grupos and coincide_horas_mat and coincide_horas_sem:
                status = "✅ COINCIDE"
                coincidencias_exactas += 3
            else:
                status = "❌ DIFIERE"
                if not coincide_grupos:
                    diferencias.append(f"{nombre_seccion} - {nombre}: Grupos (Doc:{mat_doc['grupos']}, Excel:{mat_excel['grupos']})")
                else:
                    coincidencias_exactas += 1
                if not coincide_horas_mat:
                    diferencias.append(f"{nombre_seccion} - {nombre}: Horas/Materia (Doc:{mat_doc['horas_materia']}, Excel:{mat_excel['horas_materia']})")
                else:
                    coincidencias_exactas += 1
                if not coincide_horas_sem:
                    diferencias.append(f"{nombre_seccion} - {nombre}: Horas/Semana (Doc:{mat_doc['horas_semana']}, Excel:{mat_excel['horas_semana']})")
                else:
                    coincidencias_exactas += 1
            
            print(f"{nombre:<60} {mat_excel['grupos']:^10} {mat_excel['horas_materia']:^10} {mat_excel['horas_semana']:^10} {status:^15}")
        else:
            if nombre:  # Solo reportar si no es fila vacía
                print(f"{nombre:<60} {'':^10} {'':^10} {'':^10} {'⚠️ NO EN EXCEL':^15}")

print("\n" + "=" * 120)
print("📊 RESUMEN FINAL")
print("=" * 120)
print(f"Total de verificaciones: {total_verificaciones}")
print(f"Coincidencias exactas: {coincidencias_exactas}")
print(f"Diferencias: {total_verificaciones - coincidencias_exactas}")
print(f"\n🎯 PORCENTAJE DE COINCIDENCIA: {(coincidencias_exactas/total_verificaciones*100):.2f}%")

if diferencias:
    print("\n" + "=" * 120)
    print("⚠️  LISTA DE DIFERENCIAS ENCONTRADAS:")
    print("=" * 120)
    for i, diff in enumerate(diferencias, 1):
        print(f"{i}. {diff}")
else:
    print("\n✅ ¡COINCIDENCIA 100%! Todos los datos son idénticos.")

print("\n" + "=" * 120)
