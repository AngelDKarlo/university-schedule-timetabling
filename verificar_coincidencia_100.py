#!/usr/bin/env python3
"""
Script para verificar coincidencia 100% entre documento y sistema
"""

import pandas as pd
import os

os.chdir('/home/angel/Politecnica/Estructuras de Datos/pf')

# Leer la Matriz ITI del Excel
df = pd.read_excel('Horarios EneAbr18 (1).xlsx', sheet_name='Matriz ITI', header=None)

print("=" * 100)
print("🔍 VERIFICACIÓN DE COINCIDENCIA 100% - DOCUMENTO vs SISTEMA")
print("=" * 100)
print()

# Datos a verificar del documento compartido
documento = {
    # Primer Cuatrimestre - Vespertino (ITI 1-1)
    "Algoritmos": {"grupos": 1, "horas": 6, "profesor_col": 15},  # M.I. Arturo G. Mascorro
    "Herramientas Ofimáticas": {"grupos": 1, "horas": 4, "profesor_col": 25},  # M.I. Erendira
    "Introducción a la ITI": {"grupos": 1, "horas": 3, "profesor_col": 17},  # Ing. Hugo E. Treviño
    "Arquitectura de Computadoras": {"grupos": 1, "horas": 5, "profesor_col": 16},  # M.I. Hugo O. Camargo
    "Matemáticas Básicas": {"grupos": 1, "horas": 6, "profesor_col": 23},  # M.I. Luis R. De la Fuente
    
    # Segundo Cuatrimestre - Matutino (ITI 2-1, ITI 2-2)
    "Inteligencia Emocional_M": {"grupos": 2, "horas_total": 6, "profesores": [(34, 3), (35, 3)]},
    "Lógica Computacional_M": {"grupos": 2, "horas_total": 12, "profesor_col": 11},  # M.C.A. Jorge Arturo
    "Herramientas Multimedia_M": {"grupos": 2, "horas_total": 8, "profesor_col": 11},
    "Fundamentos de Redes_M": {"grupos": 2, "horas_total": 10, "profesores": [(13, 5), (17, 5)]},
    "Fundamentos de Física_M": {"grupos": 2, "horas_total": 12, "profesor_col": 31},
    "Matemáticas Discretas_M": {"grupos": 2, "horas_total": 12, "profesores": [(23, 6), (24, 6)]},
    
    # Segundo Cuatrimestre - Vespertino (ITI 2-3)
    "Inteligencia Emocional_V": {"grupos": 1, "horas": 3, "profesor_col": 35},
    "Lógica Computacional_V": {"grupos": 1, "horas": 6, "profesor_col": 26},  # M.C. Carlos Orozco
    "Herramientas Multimedia_V": {"grupos": 1, "horas": 4, "profesor_col": 25},
    "Fundamentos de Redes_V": {"grupos": 1, "horas": 5, "profesor_col": 17},
    "Fundamentos de Física_V": {"grupos": 1, "horas": 6, "profesor_col": 31},
    "Matemáticas Discretas_V": {"grupos": 1, "horas": 6, "profesor_col": 7},
    
    # Cuarto Cuatrimestre - Vespertino (ITI 4-1)
    "Habilidades del Pensamiento": {"grupos": 1, "horas": 4, "profesor_col": None},  # Sin asignar
    "Introducción a la Programación Orientada a Objetos": {"grupos": 1, "horas": 6, "profesor_col": 27},
    "Introducción a las Bases de Datos": {"grupos": 1, "horas": 5, "profesor_col": 29},
    "Switcheo y Wireless": {"grupos": 1, "horas": 6, "profesor_col": 16},
    "Álgebra Lineal": {"grupos": 1, "horas": 6, "profesor_col": 31},
}

# Nombres de profesores (columna -> nombre)
profesores = {
    5: "Dr. Jean-Michael Recher",
    6: "Dr. Alberto García Robledo",
    7: "Dra. Karla E. Vázquez Ortiz",
    8: "Dr. Hector Hugo Avilés Arriaga",
    9: "Dr. Said Polanco Martagón",
    10: "Dr. Marco A. Nuño Maganda",
    11: "M.C.A. Jorge Arturo Hernández Almazan",
    12: "M.S.I. Mario H. Rodriguez Chávez",
    13: "M.C. Jorge O. Jasso Luna",
    14: "M.A.T. Hiram Herrera Rivas",
    15: "M.S.I. Alma Delia Amaya Vázquez",
    16: "M.S.I. José Fidencio López Luna",
    17: "M.I. Manuel Ruiz Méndez",
    18: "M.T.I. Israel Pulido Picazo",
    19: "M.S.I. Marina Cristal Flores Flores",
    20: "M.I. Arturo G. Mascorro Cienfuegos",
    21: "M.I. Hugo O. Camargo",
    22: "Ing. Hugo E. Treviño",
    23: "M.I. Adriana Lizeth Trujillo",
    24: "M.I. Luis R. De la Fuente",
    25: "M.I. Erendira Guitierrez Meza",
    26: "M.C. Maribel Marin Castro",
    27: "M.C. Carlos Orozco Garcia",
    28: "Ing. Juan Manuel Ornelas Llerena",
    29: "Eduardo Patricio González Nuño",
    30: "Lic. Myriam Ornelas Llerena",
    31: "Luis F. Castillo Cortés",
    32: "Lic. Carlos Castillo",
    33: "Fernando Requena",
    34: "Oscar Romero de la Cruz",
    35: "Alma Leticia Valdéz García",
}

# Buscar cada curso en el Excel
total_verificaciones = 0
coincidencias = 0
diferencias = []

print("📋 VERIFICANDO CADA MATERIA...")
print()

# Obtener índices de filas por nombre de materia
materias_indices = {}
for idx, row in df.iterrows():
    materia = str(row.iloc[0]).strip()
    if materia and materia not in ['', 'nan', 'Horas Asignadas', 'Primer Cuatrimestre', 'Segundo Cuatrimestre', 
                                    'Cuarto Cuatrimestre', 'Quinto Cuatrimestre', 'Septimo Cuatrimestre', 
                                    'Octavo Cuatrimestre', 'Totales', 'Horas restantes']:
        if not materia.startswith('Vespertino') and not materia.startswith('Matutino') and not materia.startswith('Inglés'):
            materias_indices[materia] = idx

for materia, datos_doc in documento.items():
    # Normalizar nombre de materia
    materia_buscar = materia.replace("_M", "").replace("_V", "")
    
    if materia_buscar in materias_indices:
        idx = materias_indices[materia_buscar]
        row = df.iloc[idx]
        
        # Verificar grupos
        grupos_excel = int(row.iloc[1]) if pd.notna(row.iloc[1]) else 0
        grupos_doc = datos_doc.get('grupos', datos_doc.get('horas_total', 0) // datos_doc.get('horas', 1))
        
        # Verificar horas
        horas_excel = int(row.iloc[2]) if pd.notna(row.iloc[2]) else 0
        horas_doc = datos_doc.get('horas', datos_doc.get('horas_total', 0))
        
        total_verificaciones += 2  # grupos + horas
        
        coincide_grupos = grupos_excel == grupos_doc
        coincide_horas = horas_excel == horas_doc
        
        if coincide_grupos:
            coincidencias += 1
        else:
            diferencias.append(f"❌ {materia}: GRUPOS - Doc: {grupos_doc}, Excel: {grupos_excel}")
            
        if coincide_horas:
            coincidencias += 1
        else:
            diferencias.append(f"❌ {materia}: HORAS - Doc: {horas_doc}, Excel: {horas_excel}")
        
        # Mostrar resultado
        status_grupos = "✅" if coincide_grupos else "❌"
        status_horas = "✅" if coincide_horas else "❌"
        print(f"{status_grupos}{status_horas} {materia_buscar:50s} | Grupos: {grupos_excel} | Horas: {horas_excel}")
    else:
        print(f"⚠️  {materia_buscar:50s} | NO ENCONTRADA EN EXCEL")

print()
print("=" * 100)
print(f"📊 RESUMEN DE VERIFICACIÓN")
print("=" * 100)
print(f"Total de verificaciones: {total_verificaciones}")
print(f"Coincidencias: {coincidencias}")
print(f"Diferencias: {total_verificaciones - coincidencias}")
print(f"Porcentaje de coincidencia: {(coincidencias/total_verificaciones*100):.2f}%")
print()

if diferencias:
    print("⚠️  DIFERENCIAS ENCONTRADAS:")
    print()
    for diff in diferencias:
        print(diff)
else:
    print("✅ ¡COINCIDENCIA 100%!")

print()
print("=" * 100)
