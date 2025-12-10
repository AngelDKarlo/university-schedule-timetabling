"""
Servicio de parsing NUEVO - Procesa correctamente el Excel de la UPV
"""

import pandas as pd
import os
import re
import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

class ParserServiceNew:
    """Parser mejorado para procesar Excel de horarios UPV"""
    
    def __init__(self):
        self.data_dir = os.path.join(os.path.dirname(__file__), '../data')
        
    def procesar_excel(self, filepath: str) -> Dict[str, Any]:
        """
        Procesa el Excel de la UPV correctamente
        
        Args:
            filepath: Ruta al archivo Excel
            
        Returns:
            Diccionario con datos procesados
        """
        logger.info(f"📊 Procesando Excel: {filepath}")
        
        try:
            # Leer Excel
            df = pd.read_excel(filepath, sheet_name='Matriz ITI', header=None)
            
            # Extraer profesores (fila 1, desde columna 4)
            profesores = self._extraer_profesores(df)
            
            # Extraer cursos y grupos
            cursos, grupos = self._extraer_cursos_y_grupos(df, profesores)
            
            # Generar aulas
            aulas = [f"Aula-{i}" for i in range(1, 16)]
            
            resultado = {
                'cursos': cursos,
                'profesores': list(profesores.values()),
                'grupos': grupos,
                'aulas': aulas,
                'metadata': {
                    'total_cursos': len(cursos),
                    'total_profesores': len(profesores),
                    'total_grupos': len(grupos),
                    'total_aulas': len(aulas)
                }
            }
            
            logger.info(f"✅ Excel procesado: {resultado['metadata']}")
            return resultado
            
        except Exception as e:
            logger.error(f"❌ Error procesando Excel: {str(e)}", exc_info=True)
            raise
    
    def _extraer_profesores(self, df: pd.DataFrame) -> Dict[int, Dict]:
        """Extrae profesores de la fila 1"""
        profesores = {}
        
        # Fila 1, desde columna 4 en adelante
        for idx in range(4, df.shape[1]):
            nombre = df.iloc[1, idx]
            if pd.notna(nombre) and str(nombre).strip() and str(nombre).strip() != 'Resta':
                nombre = str(nombre).strip()
                profesores[idx] = {
                    'id': f"PROF_{len(profesores) + 1}",
                    'nombre': nombre,
                    'horas_asignadas': 0,
                    'cursos': []
                }
        
        logger.info(f"📋 {len(profesores)} profesores extraídos")
        return profesores
    
    def _extraer_cursos_y_grupos(self, df: pd.DataFrame, profesores: Dict) -> tuple:
        """Extrae cursos y grupos del Excel"""
        cursos = []
        grupos_set = set()
        
        # Grupos detectados en filas específicas
        grupos_info = {
            4: ['ITI-1V'],
            13: ['ITI-2M1', 'ITI-2M2'],  # Matutino tiene 2 grupos
            21: ['ITI-2V'],
            30: ['ITI-4V'],
            39: ['ITI-5M1', 'ITI-5M2'],  # Matutino tiene 2 grupos
            47: ['ITI-5V'],
            56: ['ITI-7V'],
            65: ['ITI-8M'],
            73: ['ITI-8V']
        }
        
        # Procesar cada sección de grupos
        for fila_inicio, lista_grupos in grupos_info.items():
            # Leer cursos hasta encontrar la siguiente sección o línea vacía
            fila_actual = fila_inicio + 1
            
            while fila_actual < df.shape[0]:
                nombre_curso = df.iloc[fila_actual, 0]
                
                # Si llegamos a otra sección o línea vacía, terminar
                if pd.isna(nombre_curso) or str(nombre_curso).strip() in ['', 'Totales', 'Horas restantes']:
                    break
                
                # Si encontramos otro grupo, terminar
                if 'ITI' in str(nombre_curso) and ('Matutino' in str(nombre_curso) or 'Vespertino' in str(nombre_curso)):
                    break
                
                nombre_curso = str(nombre_curso).strip()
                
                # Saltar líneas de encabezado
                if nombre_curso in ['Inglés I', 'Inglés II', 'Inglés IV', 'Inglés V', 'Inglés VII', 'Inglés VIII', 
                                   'Valores del Ser', 'Estancia I', 'Estancia II']:
                    fila_actual += 1
                    continue
                
                # Obtener número de grupos y horas
                num_grupos_curso = df.iloc[fila_actual, 1]
                horas_semana = df.iloc[fila_actual, 2]
                
                if pd.isna(num_grupos_curso) or num_grupos_curso == 0:
                    fila_actual += 1
                    continue
                
                num_grupos_curso = int(num_grupos_curso)
                horas_semana = int(horas_semana) if pd.notna(horas_semana) else 0
                
                # Encontrar profesor asignado (primera celda con horas > 0)
                profesor_asignado = None
                for col_idx, prof_info in profesores.items():
                    horas = df.iloc[fila_actual, col_idx]
                    if pd.notna(horas) and float(horas) > 0:
                        profesor_asignado = prof_info['nombre']
                        prof_info['horas_asignadas'] += float(horas)
                        break
                
                # Crear cursos para cada grupo
                for grupo_nombre in lista_grupos:
                    grupos_set.add(grupo_nombre)
                    
                    curso_id = f"CURSO_{len(cursos) + 1}"
                    curso = {
                        'id': curso_id,
                        'nombre': nombre_curso,
                        'grupo': grupo_nombre,
                        'horas_semana': horas_semana,
                        'profesor': profesor_asignado,
                        'aula': None,
                        'horarios': []
                    }
                    
                    cursos.append(curso)
                    
                    # Actualizar cursos del profesor
                    if profesor_asignado:
                        for prof_info in profesores.values():
                            if prof_info['nombre'] == profesor_asignado:
                                if curso_id not in prof_info['cursos']:
                                    prof_info['cursos'].append(curso_id)
                
                fila_actual += 1
        
        logger.info(f"📚 {len(cursos)} cursos extraídos en {len(grupos_set)} grupos")
        return cursos, sorted(list(grupos_set))
    
    def cargar_csvs_automaticamente(self) -> Dict[str, Any]:
        """Mantener compatibilidad con CSVs (método legacy)"""
        logger.info("ℹ️  Usando CSVs legacy - Se recomienda subir Excel")
        
        # Retornar datos vacíos para forzar uso de Excel
        return {
            'cursos': [],
            'profesores': [],
            'grupos': [],
            'aulas': [],
            'metadata': {
                'total_cursos': 0,
                'total_profesores': 0,
                'total_grupos': 0,
                'total_aulas': 0
            }
        }
