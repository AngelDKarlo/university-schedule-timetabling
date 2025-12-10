"""
Servicio de exportación
Exporta horarios a diferentes formatos (JSON, Excel, PDF)
"""

import json
import os
from datetime import datetime
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class ExportService:
    """Servicio para exportar horarios"""
    
    def __init__(self, datos_horarios: Dict):
        self.datos = datos_horarios
        self.export_folder = os.path.join(os.path.dirname(__file__), '../../exports')
        os.makedirs(self.export_folder, exist_ok=True)
        
    def exportar_json(self) -> str:
        """Exporta horarios a JSON"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'horarios_{timestamp}.json'
            filepath = os.path.join(self.export_folder, filename)
            
            datos_exportar = {
                'horarios': self.datos.get('horario_generado', {}),
                'cursos': self.datos.get('cursos', []),
                'profesores': self.datos.get('profesores', []),
                'grupos': self.datos.get('grupos', []),
                'metadata': {
                    'generado': datetime.now().isoformat(),
                    'version': '2.0'
                }
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(datos_exportar, f, indent=2, ensure_ascii=False)
            
            logger.info(f"JSON exportado: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error exportando JSON: {str(e)}", exc_info=True)
            raise
    
    def exportar_excel(self) -> str:
        """Exporta horarios a Excel"""
        try:
            import pandas as pd
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'horarios_{timestamp}.xlsx'
            filepath = os.path.join(self.export_folder, filename)
            
            # Crear un writer de Excel
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                # Exportar cada grupo en una hoja
                for grupo, horario in self.datos.get('horario_generado', {}).items():
                    # Crear DataFrame del horario
                    dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes']
                    franjas = sorted(set(
                        franja for dia_franjas in horario.values() 
                        for franja in dia_franjas.keys()
                    ))
                    
                    df_data = []
                    for franja in franjas:
                        fila = {'Hora': franja}
                        for dia in dias:
                            if dia in horario and franja in horario[dia]:
                                datos = horario[dia][franja]
                                fila[dia] = f"{datos['curso']}\n{datos['profesor']}\n{datos['aula']}"
                            else:
                                fila[dia] = ''
                        df_data.append(fila)
                    
                    df = pd.DataFrame(df_data)
                    df.to_excel(writer, sheet_name=grupo, index=False)
            
            logger.info(f"Excel exportado: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error exportando Excel: {str(e)}", exc_info=True)
            raise
    
    def exportar_pdf(self) -> str:
        """Exporta horarios a PDF"""
        try:
            from reportlab.lib.pagesizes import letter, landscape
            from reportlab.lib import colors
            from reportlab.lib.styles import getSampleStyleSheet
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'horarios_{timestamp}.pdf'
            filepath = os.path.join(self.export_folder, filename)
            
            doc = SimpleDocTemplate(filepath, pagesize=landscape(letter))
            elements = []
            styles = getSampleStyleSheet()
            
            # Título
            title = Paragraph("<b>HORARIOS ITI - UPV</b>", styles['Title'])
            elements.append(title)
            elements.append(Spacer(1, 20))
            
            # Crear tabla para cada grupo
            for grupo, horario in self.datos.get('horario_generado', {}).items():
                # Subtítulo del grupo
                subtitle = Paragraph(f"<b>Grupo: {grupo}</b>", styles['Heading2'])
                elements.append(subtitle)
                elements.append(Spacer(1, 10))
                
                # Preparar datos de la tabla
                dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes']
                franjas = sorted(set(
                    franja for dia_franjas in horario.values() 
                    for franja in dia_franjas.keys()
                ))
                
                # Encabezados
                data = [['Hora'] + dias]
                
                # Filas
                for franja in franjas:
                    fila = [franja]
                    for dia in dias:
                        if dia in horario and franja in horario[dia]:
                            datos = horario[dia][franja]
                            celda = f"{datos['curso']}\n{datos['profesor']}\n{datos['aula']}"
                            fila.append(celda)
                        else:
                            fila.append('')
                    data.append(fila)
                
                # Crear tabla
                table = Table(data)
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.purple),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                
                elements.append(table)
                elements.append(Spacer(1, 30))
            
            # Generar PDF
            doc.build(elements)
            
            logger.info(f"PDF exportado: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error exportando PDF: {str(e)}", exc_info=True)
            raise
