"""
Servicio de consultas
Obtiene información específica de horarios, profesores y grupos
"""

from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)

class QueryService:
    """Servicio para consultar información de horarios"""
    
    def __init__(self, datos_horarios: Dict):
        self.datos = datos_horarios
        
    def obtener_horario_grupo(self, grupo: str) -> Dict[str, Any]:
        """
        Obtiene el horario de un grupo específico
        
        Args:
            grupo: Nombre del grupo (ej: ITI-11, ITI-21)
            
        Returns:
            Diccionario con horario del grupo
        """
        try:
            horario_generado = self.datos.get('horario_generado', {})
            
            if grupo not in horario_generado:
                return {'error': f'Grupo {grupo} no encontrado'}
            
            horario_grupo = horario_generado[grupo]
            
            # Formatear para visualización
            horario_formateado = {
                'grupo': grupo,
                'dias': {}
            }
            
            for dia, franjas in horario_grupo.items():
                horario_formateado['dias'][dia] = []
                for franja, datos in sorted(franjas.items()):
                    horario_formateado['dias'][dia].append({
                        'franja': franja,
                        'curso': datos['curso'],
                        'profesor': datos['profesor'],
                        'aula': datos['aula']
                    })
            
            return horario_formateado
            
        except Exception as e:
            logger.error(f"Error obteniendo horario de grupo: {str(e)}", exc_info=True)
            return {'error': str(e)}
    
    def obtener_horario_profesor(self, nombre_profesor: str) -> Dict[str, Any]:
        """
        Obtiene el horario de un profesor específico
        
        Args:
            nombre_profesor: Nombre completo del profesor
            
        Returns:
            Diccionario con horario del profesor
        """
        try:
            horario_generado = self.datos.get('horario_generado', {})
            
            # Buscar todas las clases del profesor
            clases_profesor = []
            
            for grupo, horario_grupo in horario_generado.items():
                for dia, franjas in horario_grupo.items():
                    for franja, datos in franjas.items():
                        if datos['profesor'] == nombre_profesor:
                            clases_profesor.append({
                                'dia': dia,
                                'franja': franja,
                                'curso': datos['curso'],
                                'grupo': grupo,
                                'aula': datos['aula']
                            })
            
            # Organizar por día
            horario_por_dia = {}
            for clase in clases_profesor:
                dia = clase['dia']
                if dia not in horario_por_dia:
                    horario_por_dia[dia] = []
                horario_por_dia[dia].append(clase)
            
            # Obtener información del profesor
            profesor_info = None
            for prof in self.datos.get('profesores', []):
                if prof['nombre'] == nombre_profesor:
                    profesor_info = prof
                    break
            
            return {
                'profesor': nombre_profesor,
                'info': profesor_info,
                'clases': clases_profesor,
                'horario_por_dia': horario_por_dia,
                'total_clases': len(clases_profesor)
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo horario de profesor: {str(e)}", exc_info=True)
            return {'error': str(e)}
    
    def obtener_estadisticas(self) -> Dict[str, Any]:
        """Obtiene estadísticas generales del sistema"""
        try:
            return {
                'total_cursos': len(self.datos.get('cursos', [])),
                'total_profesores': len(self.datos.get('profesores', [])),
                'total_grupos': len(self.datos.get('grupos', [])),
                'total_aulas': len(self.datos.get('aulas', [])),
                'horarios_generados': self.datos.get('horario_generado') is not None
            }
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas: {str(e)}")
            return {'error': str(e)}
