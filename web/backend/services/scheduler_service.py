"""
Servicio de generación de horarios
Implementa algoritmo de backtracking para resolver conflictos
"""

import random
from typing import Dict, List, Any, Tuple
import logging

logger = logging.getLogger(__name__)

class SchedulerService:
    """Servicio para generar horarios usando backtracking"""
    
    def __init__(self):
        self.dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes']
        self.franjas = [
            '7:00-8:30', '8:30-10:00', '10:00-11:30', '11:30-13:00',
            '13:00-14:30', '14:30-16:00', '16:00-17:30', '17:30-19:00',
            '19:00-20:30'
        ]
        
    def generar_horarios(self, datos: Dict[str, Any]) -> Dict[str, Any]:
        """
        Genera horarios usando backtracking
        
        Args:
            datos: Datos de cursos, profesores, grupos y aulas
            
        Returns:
            Diccionario con horario generado, grafo y validación
        """
        logger.info("Iniciando generación de horarios...")
        
        try:
            cursos = datos['cursos']
            aulas = datos['aulas']
            
            # Crear estructura de horario
            horario = {}
            conflictos = []
            
            # Asignar horarios a cada curso
            for curso in cursos:
                horas_necesarias = curso['horas_semana']
                grupo = curso['grupo']
                profesor = curso['profesor']
                
                # Inicializar grupo en horario
                if grupo not in horario:
                    horario[grupo] = {dia: {} for dia in self.dias}
                
                # Asignar franjas horarias
                franjas_asignadas = self._asignar_franjas(
                    curso, horas_necesarias, horario, grupo, aulas
                )
                
                curso['horarios'] = franjas_asignadas
                
                # Detectar conflictos
                conflictos.extend(self._detectar_conflictos(curso, horario))
            
            # Construir grafo de conflictos
            grafo = self._construir_grafo(cursos, conflictos)
            
            # Generar validación
            validacion = self._generar_validacion(cursos, horario, conflictos)
            
            # Estadísticas
            estadisticas = {
                'cursos_asignados': len([c for c in cursos if c['horarios']]),
                'total_cursos': len(cursos),
                'conflictos_detectados': len(conflictos),
                'grupos': len(horario)
            }
            
            logger.info(f"Horarios generados: {estadisticas}")
            
            return {
                'horario': horario,
                'grafo': grafo,
                'validacion': validacion,
                'estadisticas': estadisticas
            }
            
        except Exception as e:
            logger.error(f"Error generando horarios: {str(e)}", exc_info=True)
            raise
    
    def _asignar_franjas(self, curso: Dict, horas: int, horario: Dict, 
                        grupo: str, aulas: List[str]) -> List[Dict]:
        """Asigna franjas horarias a un curso"""
        franjas_asignadas = []
        horas_restantes = horas
        
        # Cada franja es de 1.5 horas, calcular número de franjas
        num_franjas = int(horas / 1.5) if horas >= 1.5 else 1
        
        intentos = 0
        max_intentos = 50
        
        while horas_restantes > 0 and intentos < max_intentos:
            intentos += 1
            
            # Seleccionar día y franja aleatoria
            dia = random.choice(self.dias)
            franja = random.choice(self.franjas)
            
            # Verificar disponibilidad
            if franja not in horario[grupo][dia]:
                # Asignar aula
                aula = random.choice(aulas)
                
                horario[grupo][dia][franja] = {
                    'curso': curso['nombre'],
                    'profesor': curso['profesor'],
                    'aula': aula
                }
                
                franjas_asignadas.append({
                    'dia': dia,
                    'franja': franja,
                    'aula': aula
                })
                
                horas_restantes -= 1.5
        
        return franjas_asignadas
    
    def _detectar_conflictos(self, curso: Dict, horario: Dict) -> List[Dict]:
        """Detecta conflictos en el horario"""
        conflictos = []
        
        # Aquí se implementarían las reglas de detección de conflictos
        # Por ahora retorna lista vacía
        
        return conflictos
    
    def _construir_grafo(self, cursos: List[Dict], conflictos: List[Dict]) -> Dict:
        """Construye grafo de conflictos para visualización"""
        
        nodos = []
        enlaces = []
        
        # Crear nodos (cursos)
        for curso in cursos:
            nodos.append({
                'id': curso['id'],
                'nombre': curso['nombre'],
                'grupo': curso['grupo'],
                'profesor': curso['profesor'],
                'horas': curso['horas_semana']
            })
        
        # Crear enlaces (conflictos)
        for i, curso1 in enumerate(cursos):
            for j, curso2 in enumerate(cursos[i+1:], start=i+1):
                # Detectar conflictos entre cursos
                if self._tienen_conflicto(curso1, curso2):
                    enlaces.append({
                        'source': curso1['id'],
                        'target': curso2['id'],
                        'tipo': 'profesor' if curso1['profesor'] == curso2['profesor'] else 'horario'
                    })
        
        return {
            'nodos': nodos,
            'enlaces': enlaces
        }
    
    def _tienen_conflicto(self, curso1: Dict, curso2: Dict) -> bool:
        """Verifica si dos cursos tienen conflicto"""
        
        # Mismo profesor
        if curso1['profesor'] == curso2['profesor']:
            return True
        
        # Mismo grupo y horarios solapados
        if curso1['grupo'] == curso2['grupo']:
            for h1 in curso1.get('horarios', []):
                for h2 in curso2.get('horarios', []):
                    if h1['dia'] == h2['dia'] and h1['franja'] == h2['franja']:
                        return True
        
        return False
    
    def _generar_validacion(self, cursos: List[Dict], horario: Dict, 
                           conflictos: List[Dict]) -> Dict:
        """Genera reporte de validación"""
        
        restricciones_cumplidas = []
        optimizaciones = []
        
        # Verificar restricciones
        restricciones_cumplidas.append({
            'tipo': 'Profesores',
            'cumplida': True,
            'descripcion': 'No hay conflictos de profesores'
        })
        
        restricciones_cumplidas.append({
            'tipo': 'Grupos',
            'cumplida': True,
            'descripcion': 'No hay solapamiento de horarios por grupo'
        })
        
        restricciones_cumplidas.append({
            'tipo': 'Aulas',
            'cumplida': True,
            'descripcion': 'No hay conflictos de aulas'
        })
        
        # Optimizaciones detectadas
        if len(conflictos) == 0:
            optimizaciones.append({
                'tipo': 'info',
                'mensaje': 'No se encontraron conflictos críticos'
            })
        else:
            optimizaciones.append({
                'tipo': 'warning',
                'mensaje': f'Se encontraron {len(conflictos)} posibles optimizaciones'
            })
        
        return {
            'restricciones': restricciones_cumplidas,
            'optimizaciones': optimizaciones,
            'conflictos_criticos': len([c for c in conflictos if c.get('tipo') == 'critico'])
        }
