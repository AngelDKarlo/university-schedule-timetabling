"""
Servicio de parseo de archivos Excel y JSON
Procesa archivos de entrada y extrae información de horarios
"""

import pandas as pd
import json
import re
import os
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)

class ParserService:
    """Servicio para parsear archivos de horarios"""
    
    def __init__(self):
        self.profesores_map = {}
        self.grupos_set = set()
        self.aulas_set = set()
        self.cursos_list = []
        self.data_dir = os.path.join(os.path.dirname(__file__), '../data')
    
    def cargar_csvs_automaticamente(self) -> Dict[str, Any]:
        """
        Carga automáticamente los archivos CSV del directorio data/
        
        Returns:
            Diccionario con datos procesados de los CSVs
        """
        logger.info(f"Cargando CSVs desde: {self.data_dir}")
        
        try:
            # Verificar que existe el directorio
            if not os.path.exists(self.data_dir):
                logger.warning(f"Directorio {self.data_dir} no existe")
                return None
            
            # Cargar cada CSV
            cursos_csv = os.path.join(self.data_dir, 'cursos.csv')
            profesores_csv = os.path.join(self.data_dir, 'profesores.csv')
            grupos_csv = os.path.join(self.data_dir, 'grupos.csv')
            aulas_csv = os.path.join(self.data_dir, 'aulas.csv')
            
            if not all(os.path.exists(f) for f in [cursos_csv, profesores_csv, grupos_csv, aulas_csv]):
                logger.warning("Faltan archivos CSV necesarios")
                return None
            
            # Leer CSVs
            df_cursos = pd.read_csv(cursos_csv, encoding='utf-8')
            df_profesores = pd.read_csv(profesores_csv, encoding='utf-8')
            df_grupos = pd.read_csv(grupos_csv, encoding='utf-8')
            df_aulas = pd.read_csv(aulas_csv, encoding='utf-8')
            
            # Procesar cursos
            cursos = []
            for _, row in df_cursos.iterrows():
                curso = {
                    'id': int(row['id']),
                    'nombre': str(row['nombre']),
                    'grupo': str(row['grupo']),
                    'profesor': {
                        'id': int(row['profesor_id']),
                        'nombre': str(row['profesor_nombre'])
                    },
                    'horario': {
                        'dia': str(row['dia']),
                        'hora_inicio': str(row['hora_inicio']),
                        'hora_fin': str(row['hora_fin'])
                    },
                    'aula': {
                        'id': int(row['aula_id']),
                        'nombre': str(row['aula_nombre'])
                    },
                    'horas_semana': int(row['horas_semana'])
                }
                cursos.append(curso)
            
            # Procesar profesores
            profesores = []
            for _, row in df_profesores.iterrows():
                profesor = {
                    'id': int(row['id']),
                    'nombre': str(row['nombre']),
                    'email': str(row['email']),
                    'horas_disponibles': int(row['horas_disponibles']),
                    'cursos_asignados': []
                }
                # Contar cursos asignados
                cursos_prof = df_cursos[df_cursos['profesor_id'] == row['id']]
                if not cursos_prof.empty:
                    profesor['cursos_asignados'] = cursos_prof['nombre'].unique().tolist()
                    profesor['horas_asignadas'] = len(cursos_prof)
                else:
                    profesor['horas_asignadas'] = 0
                
                profesores.append(profesor)
            
            # Procesar grupos
            grupos = df_grupos['codigo'].tolist()
            
            # Procesar aulas
            aulas = []
            for _, row in df_aulas.iterrows():
                aula = {
                    'id': int(row['id']),
                    'codigo': str(row['codigo']),
                    'nombre': str(row['nombre']),
                    'capacidad': int(row['capacidad']),
                    'tipo': str(row['tipo'])
                }
                aulas.append(aula)
            
            resultado = {
                'cursos': cursos,
                'profesores': profesores,
                'grupos': grupos,
                'aulas': aulas,
                'metadata': {
                    'total_cursos': len(cursos),
                    'total_profesores': len(profesores),
                    'total_grupos': len(grupos),
                    'total_aulas': len(aulas)
                }
            }
            
            logger.info(f"✅ CSVs cargados: {resultado['metadata']}")
            return resultado
                
        except Exception as e:
            logger.error(f"Error cargando CSVs: {str(e)}", exc_info=True)
            return None
        
    def procesar_excel(self, filepath: str) -> Dict[str, Any]:
        """
        Procesa archivo Excel con formato UPV
        
        Args:
            filepath: Ruta al archivo Excel
            
        Returns:
            Diccionario con datos procesados
        """
        logger.info(f"Procesando Excel: {filepath}")
        
        try:
            # Leer Excel
            df = pd.read_excel(filepath, sheet_name=0)
            
            # Limpiar y procesar datos
            self._procesar_dataframe(df)
            
            resultado = {
                'cursos': self.cursos_list,
                'profesores': list(self.profesores_map.values()),
                'grupos': sorted(list(self.grupos_set)),
                'aulas': sorted(list(self.aulas_set)),
                'metadata': {
                    'total_cursos': len(self.cursos_list),
                    'total_profesores': len(self.profesores_map),
                    'total_grupos': len(self.grupos_set),
                    'total_aulas': len(self.aulas_set)
                }
            }
            
            logger.info(f"Excel procesado: {resultado['metadata']}")
            return resultado
            
        except Exception as e:
            logger.error(f"Error procesando Excel: {str(e)}", exc_info=True)
            raise
    
    def _procesar_dataframe(self, df: pd.DataFrame):
        """Procesa el DataFrame y extrae información"""
        
        # Mapeo de columnas de profesores (índices 4 en adelante)
        columnas_profesores = df.columns[4:]
        
        for idx, profesor_col in enumerate(columnas_profesores, start=4):
            profesor_nombre = str(profesor_col).strip()
            if profesor_nombre and profesor_nombre != 'nan':
                self.profesores_map[idx] = {
                    'id': idx,
                    'nombre': profesor_nombre,
                    'horas_asignadas': 0,
                    'cursos': []
                }
        
        # Procesar filas de cursos
        for index, row in df.iterrows():
            try:
                nombre_curso = str(row.iloc[0]).strip()
                
                # Saltar filas vacías o de encabezado
                if pd.isna(nombre_curso) or nombre_curso in ['', 'nan', 'grupos']:
                    continue
                
                # Detectar grupo
                grupos = int(row.iloc[1]) if pd.notna(row.iloc[1]) else 0
                if grupos == 0:
                    continue
                
                # Horas por semana
                horas_semana = int(row.iloc[2]) if pd.notna(row.iloc[2]) else 0
                
                # Procesar cada grupo
                for grupo_num in range(1, grupos + 1):
                    curso_id = f"CURSO_{len(self.cursos_list) + 1}"
                    
                    # Buscar profesor asignado
                    profesor_asignado = None
                    for col_idx in range(4, len(row)):
                        horas = row.iloc[col_idx]
                        if pd.notna(horas) and horas > 0:
                            if col_idx in self.profesores_map:
                                profesor_asignado = self.profesores_map[col_idx]['nombre']
                                self.profesores_map[col_idx]['horas_asignadas'] += horas
                                self.profesores_map[col_idx]['cursos'].append(curso_id)
                                break
                    
                    # Determinar grupo y turno
                    grupo_nombre = self._determinar_grupo(nombre_curso, grupos, grupo_num)
                    self.grupos_set.add(grupo_nombre)
                    
                    # Crear curso
                    curso = {
                        'id': curso_id,
                        'nombre': nombre_curso,
                        'grupo': grupo_nombre,
                        'horas_semana': horas_semana,
                        'profesor': profesor_asignado,
                        'aula': None,  # Se asignará después
                        'horarios': []  # Se asignará después
                    }
                    
                    self.cursos_list.append(curso)
                    
            except Exception as e:
                logger.warning(f"Error procesando fila {index}: {str(e)}")
                continue
        
        # Generar aulas (15 aulas como en el ejemplo)
        for i in range(1, 16):
            self.aulas_set.add(f"Aula-{i}")
    
    def _determinar_grupo(self, nombre_curso: str, total_grupos: int, grupo_num: int) -> str:
        """Determina el nombre del grupo basado en el nombre del curso"""
        
        # Buscar patrones como "ITI 1-1", "Vespertino", "Matutino"
        if 'Vespertino' in nombre_curso:
            turno = 'V'
        elif 'Matutino' in nombre_curso:
            turno = 'M'
        else:
            turno = 'V'  # Por defecto vespertino
        
        # Buscar cuatrimestre
        match = re.search(r'(\d+)', nombre_curso)
        if match:
            cuatrimestre = match.group(1)
        else:
            cuatrimestre = '1'
        
        # Construir nombre del grupo
        if total_grupos > 1:
            return f"ITI-{cuatrimestre}{turno}{grupo_num}"
        else:
            return f"ITI-{cuatrimestre}{turno}"
    
    def procesar_json(self, filepath: str) -> Dict[str, Any]:
        """
        Procesa archivo JSON con formato estándar
        
        Args:
            filepath: Ruta al archivo JSON
            
        Returns:
            Diccionario con datos procesados
        """
        logger.info(f"Procesando JSON: {filepath}")
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                datos = json.load(f)
            
            # Validar estructura
            if not all(k in datos for k in ['cursos', 'profesores', 'grupos', 'aulas']):
                raise ValueError("JSON no tiene la estructura correcta")
            
            logger.info(f"JSON procesado: {len(datos['cursos'])} cursos")
            return datos
            
        except Exception as e:
            logger.error(f"Error procesando JSON: {str(e)}", exc_info=True)
            raise
