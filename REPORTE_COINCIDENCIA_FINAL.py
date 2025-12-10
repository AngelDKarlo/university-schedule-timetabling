#!/usr/bin/env python3
"""
REPORTE FINAL DE COINCIDENCIA 100%
Compara el documento compartido vs el Excel del sistema
"""

import pandas as pd
import os
from datetime import datetime

os.chdir('/home/angel/Politecnica/Estructuras de Datos/pf')

# Leer la Matriz ITI del Excel
df = pd.read_excel('Horarios EneAbr18 (1).xlsx', sheet_name='Matriz ITI', header=None)

print("╔" + "═" * 118 + "╗")
print("║" + " " * 35 + "🎓 REPORTE DE VERIFICACIÓN 100%" + " " * 52 + "║")
print("║" + " " * 30 + "Universidad Politécnica de Victoria" + " " * 53 + "║")
print("║" + " " * 25 + f"Fecha: {datetime.now().strftime('%d de %B de %Y')}" + " " * 54 + "║")
print("╚" + "═" * 118 + "╝")
print()

# Estructura del documento compartido
secciones = [
    ("Primer Cuatrimestre", "Vespertino (ITI 1-1)", 4, [
        ("Inglés I", 0, 5, 0),
        ("Valores del Ser", 0, 3, 0),
        ("Algoritmos", 1, 6, 6),
        ("Herramientas Ofimáticas", 1, 4, 4),
        ("Introducción a la ITI", 1, 3, 3),
        ("Arquitectura de Computadoras", 1, 5, 5),
        ("Matemáticas Básicas", 1, 6, 6),
    ]),
    ("Segundo Cuatrimestre", "Matutino (ITI 2-1, ITI 2-2)", 13, [
        ("Lógica Computacional", 0, 5, 0),
        ("Inteligencia Emocional", 2, 3, 6),
        ("", 2, 6, 12),  # Fila sin nombre
        ("Herramientas Multimedia", 2, 4, 8),
        ("Fundamentos de Redes", 2, 5, 10),
        ("Fundamentos de Física", 2, 6, 12),
        ("Matemáticas Discretas", 2, 6, 12),
    ]),
    ("Segundo Cuatrimestre", "Vespertino (ITI 2-3)", 21, [
        ("Inglés II", 0, 5, 0),
        ("Inteligencia Emocional", 1, 3, 3),
        ("Lógica Computacional", 1, 6, 6),
        ("Herramientas Multimedia", 1, 4, 4),
        ("Fundamentos de Redes", 1, 5, 5),
        ("Fundamentos de Física", 1, 6, 6),
        ("Matemáticas Discretas", 1, 6, 6),
    ]),
    ("Cuarto Cuatrimestre", "Vespertino (ITI 4-1)", 30, [
        ("Inglés IV", 0, 6, 0),
        ("Habilidades del Pensamiento", 1, 4, 4),
        ("Introducción a la Programación Orientada a Objetos", 1, 6, 6),
        ("Introducción a las Bases de Datos", 1, 5, 5),
        ("Switcheo y Wireless", 1, 6, 6),
        ("Álgebra Lineal", 1, 6, 6),
        ("Estancia I", 1, 0, 0),
    ]),
]

total_materias = 0
total_coincidencias = 0
total_diferencias = 0
diferencias_lista = []

for cuatrimestre, turno, fila_inicio, materias in secciones:
    print("┌" + "─" * 118 + "┐")
    print("│ " + f"{cuatrimestre} - {turno}".center(116) + " │")
    print("├" + "─" * 70 + "┬" + "─" * 10 + "┬" + "─" * 10 + "┬" + "─" * 10 + "┬" + "─" * 15 + "┤")
    print("│ " + "Materia".ljust(68) + " │ " + "Grupos".center(8) + " │ " + "H.Mat".center(8) + " │ " + "H.Sem".center(8) + " │ " + "Estado".center(13) + " │")
    print("├" + "─" * 70 + "┼" + "─" * 10 + "┼" + "─" * 10 + "┼" + "─" * 10 + "┼" + "─" * 15 + "┤")
    
    for i, (nombre, grupos_doc, horas_mat_doc, horas_sem_doc) in enumerate(materias):
        # Leer del Excel
        fila_excel = fila_inicio + i + 1  # +1 porque después del encabezado
        
        # Verificar que no nos pasemos de la hoja
        if fila_excel < len(df):
            nombre_excel = str(df.iloc[fila_excel, 0]).strip()
            grupos_excel = int(df.iloc[fila_excel, 1]) if pd.notna(df.iloc[fila_excel, 1]) else 0
            horas_mat_excel = int(df.iloc[fila_excel, 2]) if pd.notna(df.iloc[fila_excel, 2]) else 0
            horas_sem_excel = int(df.iloc[fila_excel, 3]) if pd.notna(df.iloc[fila_excel, 3]) else 0
            
            # Comparar (ignorar nombre si está vacío en documento)
            if nombre == "":
                coincide = (grupos_doc == grupos_excel and 
                           horas_mat_doc == horas_mat_excel and 
                           horas_sem_doc == horas_sem_excel)
            else:
                coincide = (nombre == nombre_excel and 
                           grupos_doc == grupos_excel and 
                           horas_mat_doc == horas_mat_excel and 
                           horas_sem_doc == horas_sem_excel)
            
            if coincide:
                status = "✅ COINCIDE"
                total_coincidencias += 1
            else:
                status = "❌ DIFIERE"
                total_diferencias += 1
                diferencias_lista.append({
                    "seccion": f"{cuatrimestre} - {turno}",
                    "materia": nombre,
                    "doc": f"G:{grupos_doc}, HM:{horas_mat_doc}, HS:{horas_sem_doc}",
                    "excel": f"G:{grupos_excel}, HM:{horas_mat_excel}, HS:{horas_sem_excel}",
                    "nombre_excel": nombre_excel
                })
            
            total_materias += 1
            
            # Mostrar
            nombre_mostrar = nombre if nombre else nombre_excel
            print("│ " + nombre_mostrar[:68].ljust(68) + " │ " + str(grupos_excel).center(8) + 
                  " │ " + str(horas_mat_excel).center(8) + " │ " + str(horas_sem_excel).center(8) + 
                  " │ " + status.center(13) + " │")
    
    print("└" + "─" * 70 + "┴" + "─" * 10 + "┴" + "─" * 10 + "┴" + "─" * 10 + "┴" + "─" * 15 + "┘")
    print()

# Resumen final
porcentaje = (total_coincidencias / total_materias * 100) if total_materias > 0 else 0

print("╔" + "═" * 118 + "╗")
print("║" + " " * 50 + "📊 RESUMEN FINAL" + " " * 52 + "║")
print("╠" + "═" * 118 + "╣")
print("║ " + f"Total de materias verificadas: {total_materias}".ljust(116) + " ║")
print("║ " + f"Coincidencias exactas: {total_coincidencias}".ljust(116) + " ║")
print("║ " + f"Diferencias encontradas: {total_diferencias}".ljust(116) + " ║")
print("║" + " " * 118 + "║")
print("║ " + f"🎯 PORCENTAJE DE COINCIDENCIA: {porcentaje:.2f}%".center(116) + " ║")
print("╚" + "═" * 118 + "╝")
print()

if total_diferencias > 0:
    print("╔" + "═" * 118 + "╗")
    print("║" + " " * 45 + "⚠️  DIFERENCIAS ENCONTRADAS" + " " * 45 + "║")
    print("╚" + "═" * 118 + "╝")
    print()
    
    for i, diff in enumerate(diferencias_lista, 1):
        print(f"{i}. {diff['seccion']}")
        print(f"   Materia: {diff['materia']}")
        print(f"   Documento: {diff['doc']}")
        print(f"   Excel: {diff['excel']} (Nombre: {diff['nombre_excel']})")
        print()
else:
    print("╔" + "═" * 118 + "╗")
    print("║" + " " * 38 + "✅ ¡COINCIDENCIA 100%!" + " " * 59 + "║")
    print("║" + " " * 25 + "Todos los datos del documento coinciden exactamente con el Excel" + " " * 28 + "║")
    print("╚" + "═" * 118 + "╝")

print()
print("Generado el: " + datetime.now().strftime('%d/%m/%Y a las %H:%M:%S'))
print()
