"""
Sistema de Horarios ITI - Web Application
Universidad Politécnica de Victoria
Backend Flask con Cython para procesamiento de horarios
"""

from flask import Flask, render_template, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import json
from datetime import datetime
import logging

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inicializar Flask
app = Flask(__name__, 
            static_folder='../frontend',
            static_url_path='/static',
            template_folder='../frontend/pages')
CORS(app)

# Configuración
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), '../uploads')
app.config['EXPORT_FOLDER'] = os.path.join(os.path.dirname(__file__), '../exports')
app.config['SECRET_KEY'] = 'upv-horarios-iti-2025'

ALLOWED_EXTENSIONS = {'xlsx', 'xls', 'json'}

# Almacenamiento en memoria de datos procesados
datos_horarios = {
    'raw_data': None,
    'cursos': [],
    'profesores': [],
    'grupos': [],
    'aulas': [],
    'horario_generado': None,
    'grafo_conflictos': None,
    'validacion': None,
    'timestamp': None
}

def allowed_file(filename):
    """Verifica si el archivo tiene una extensión permitida"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Importar servicios
from services.parser_service_new import ParserServiceNew
from services.scheduler_service_new import SchedulerServiceNew

# Inicializar servicios básicos
parser = ParserServiceNew()
scheduler = SchedulerServiceNew()

# query y exporter se crearán bajo demanda cuando se necesiten

# Cargar datos automáticamente desde CSVs al iniciar
def cargar_datos_iniciales():
    """Carga automáticamente los CSVs al iniciar la aplicación"""
    global datos_horarios
    
    logger.info("🔄 Intentando cargar Excel por defecto...")
    
    # Intentar cargar el Excel por defecto
    excel_path = os.path.join(os.path.dirname(__file__), '../../Horarios EneAbr18 (1).xlsx')
    
    if os.path.exists(excel_path):
        try:
            datos_excel = parser.procesar_excel(excel_path)
            datos_horarios['raw_data'] = datos_excel
            datos_horarios['cursos'] = datos_excel.get('cursos', [])
            datos_horarios['profesores'] = datos_excel.get('profesores', [])
            datos_horarios['grupos'] = datos_excel.get('grupos', [])
            datos_horarios['aulas'] = datos_excel.get('aulas', [])
            datos_horarios['timestamp'] = datetime.now().isoformat()
            
            logger.info(f"✅ Datos cargados: {datos_excel.get('metadata', {})}")
            
            # Generar horarios automáticamente
            try:
                logger.info("🔄 Generando horarios con BACKTRACKING...")
                resultado = scheduler.generar_horarios(datos_excel)
                datos_horarios['horario_generado'] = resultado['horario']
                datos_horarios['grafo_conflictos'] = resultado['grafo']
                datos_horarios['validacion'] = resultado['validacion']
                logger.info(f"✅ Horarios generados: {resultado['estadisticas']}")
            except Exception as e:
                logger.warning(f"⚠️  No se pudieron generar horarios: {str(e)}")
        except Exception as e:
            logger.error(f"❌ Error cargando Excel: {str(e)}")
    else:
        logger.info("ℹ️  No hay Excel por defecto. Esperando carga manual de archivo.")

# Cargar datos al iniciar
cargar_datos_iniciales()

# ========== RUTAS PRINCIPALES ==========

@app.route('/')
def index():
    """Página principal"""
    return render_template('index.html')

@app.route('/horarios')
def horarios():
    """Página de visualización de horarios"""
    return render_template('horarios.html')

@app.route('/grafo')
def grafo():
    """Página de visualización del grafo de conflictos"""
    return render_template('grafo.html')

@app.route('/profesor')
def profesor():
    """Página de consulta por profesor"""
    return render_template('profesor.html')

@app.route('/reporte')
def reporte():
    """Página de reporte de validación"""
    return render_template('reporte.html')

# ========== RUTAS DE API ==========

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Subir y procesar archivo de horarios"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No se proporcionó archivo'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No se seleccionó archivo'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Tipo de archivo no permitido'}), 400
        
        # Guardar archivo
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        logger.info(f"Archivo guardado: {filepath}")
        
        # Procesar archivo
        from services.parser_service import ParserService
        parser = ParserService()
        
        if filename.endswith(('.xlsx', '.xls')):
            resultado = parser.procesar_excel(filepath)
        else:
            resultado = parser.procesar_json(filepath)
        
        # Guardar en memoria
        datos_horarios['raw_data'] = resultado
        datos_horarios['cursos'] = resultado.get('cursos', [])
        datos_horarios['profesores'] = resultado.get('profesores', [])
        datos_horarios['grupos'] = resultado.get('grupos', [])
        datos_horarios['aulas'] = resultado.get('aulas', [])
        datos_horarios['timestamp'] = datetime.now().isoformat()
        
        return jsonify({
            'success': True,
            'mensaje': 'Archivo procesado correctamente',
            'resumen': {
                'cursos': len(datos_horarios['cursos']),
                'profesores': len(datos_horarios['profesores']),
                'grupos': len(datos_horarios['grupos']),
                'aulas': len(datos_horarios['aulas'])
            },
            'grupos': datos_horarios['grupos']
        })
        
    except Exception as e:
        logger.error(f"Error al procesar archivo: {str(e)}", exc_info=True)
        return jsonify({'error': f'Error al procesar: {str(e)}'}), 500

@app.route('/api/generar-horarios', methods=['POST'])
def generar_horarios():
    """Generar horarios usando algoritmo de backtracking"""
    try:
        if not datos_horarios['raw_data']:
            return jsonify({'error': 'Primero debe cargar un archivo'}), 400
        
        # Generar horarios con BACKTRACKING
        resultado = scheduler.generar_horarios(datos_horarios['raw_data'])
        
        # Guardar resultado
        datos_horarios['horario_generado'] = resultado['horario']
        datos_horarios['grafo_conflictos'] = resultado['grafo']
        datos_horarios['validacion'] = resultado['validacion']
        
        return jsonify({
            'success': True,
            'mensaje': 'Horarios generados con BACKTRACKING',
            'estadisticas': resultado['estadisticas']
        })
        
    except Exception as e:
        logger.error(f"Error al generar horarios: {str(e)}", exc_info=True)
        return jsonify({'error': f'Error al generar: {str(e)}'}), 500

@app.route('/api/grupos', methods=['GET'])
def obtener_grupos():
    """Obtener lista de grupos disponibles"""
    try:
        # Si hay horarios generados, solo mostrar grupos con horarios
        if datos_horarios.get('horario_generado'):
            grupos_con_horarios = list(datos_horarios['horario_generado'].keys())
            return jsonify({
                'grupos': sorted(grupos_con_horarios)
            })
        
        # Si hay grupos en memoria, usarlos
        if datos_horarios.get('grupos'):
            return jsonify({
                'grupos': datos_horarios['grupos']
            })
        
        # Cargar grupos desde CSV como fallback
        import pandas as pd
        csv_path = os.path.join(os.path.dirname(__file__), 'data', 'grupos.csv')
        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path)
            grupos = df['codigo'].unique().tolist()
            return jsonify({
                'grupos': sorted(grupos)
            })
        
        return jsonify({'grupos': []})
    except Exception as e:
        logger.error(f"Error obteniendo grupos: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/horario/<grupo>', methods=['GET'])
def obtener_horario_grupo(grupo):
    """Obtener horario de un grupo específico"""
    try:
        if not datos_horarios['horario_generado']:
            return jsonify({'error': 'No hay horarios generados'}), 400
        
        from services.query_service import QueryService
        query = QueryService(datos_horarios)
        
        horario = query.obtener_horario_grupo(grupo)
        return jsonify(horario)
        
    except Exception as e:
        logger.error(f"Error al obtener horario: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/api/profesores', methods=['GET'])
def obtener_profesores():
    """Obtener lista de profesores"""
    try:
        return jsonify({
            'profesores': datos_horarios['profesores']
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/profesor/<nombre>', methods=['GET'])
def obtener_horario_profesor(nombre):
    """Obtener horario de un profesor específico"""
    try:
        if not datos_horarios['horario_generado']:
            return jsonify({'error': 'No hay horarios generados'}), 400
        
        from services.query_service import QueryService
        query = QueryService(datos_horarios)
        
        horario = query.obtener_horario_profesor(nombre)
        return jsonify(horario)
        
    except Exception as e:
        logger.error(f"Error al obtener horario profesor: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/api/grafo', methods=['GET'])
def obtener_grafo():
    """Obtener datos del grafo de conflictos"""
    try:
        # Si hay grafo en memoria, usarlo
        if datos_horarios.get('grafo_conflictos'):
            grafo = datos_horarios['grafo_conflictos']
            # Normalizar respuesta (enlaces -> conexiones para compatibilidad)
            return jsonify({
                'nodos': grafo.get('nodos', []),
                'conexiones': grafo.get('enlaces', []),
                'enlaces': grafo.get('enlaces', []),  # Mantener ambos para compatibilidad
                'estadisticas': {
                    'total_nodos': len(grafo.get('nodos', [])),
                    'total_conexiones': len(grafo.get('enlaces', [])),
                    'total_conflictos': len(grafo.get('enlaces', []))
                }
            })
        
        # Generar grafo básico desde CSV
        import pandas as pd
        import os
        
        cursos_path = os.path.join(os.path.dirname(__file__), 'data', 'cursos.csv')
        if not os.path.exists(cursos_path):
            return jsonify({'error': 'No hay datos disponibles'}), 400
        
        df_cursos = pd.read_csv(cursos_path)
        
        # Crear nodos desde cursos
        nodos = []
        for _, curso in df_cursos.iterrows():
            nodos.append({
                'id': curso['codigo'],
                'label': curso['codigo'],
                'nombre': curso['nombre'],
                'cuatrimestre': int(curso['cuatrimestre']),
                'tipo': 'curso',
                'conflictos': []
            })
        
        # Por ahora sin conexiones reales, solo mostrar los nodos
        grafo = {
            'nodos': nodos,
            'conexiones': [],
            'enlaces': [],
            'estadisticas': {
                'total_nodos': len(nodos),
                'total_conexiones': 0,
                'total_conflictos': 0
            }
        }
        
        return jsonify(grafo)
        
    except Exception as e:
        logger.error(f"Error al obtener grafo: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/api/validacion', methods=['GET'])
def obtener_validacion():
    """Obtener reporte de validación"""
    try:
        if not datos_horarios['validacion']:
            return jsonify({'error': 'No hay validación generada'}), 400
        
        return jsonify(datos_horarios['validacion'])
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/exportar/<formato>', methods=['GET'])
def exportar_horarios(formato):
    """Exportar horarios en diferentes formatos"""
    try:
        if not datos_horarios['horario_generado']:
            return jsonify({'error': 'No hay horarios para exportar'}), 400
        
        from services.export_service import ExportService
        exporter = ExportService(datos_horarios)
        
        if formato == 'json':
            filepath = exporter.exportar_json()
        elif formato == 'excel':
            filepath = exporter.exportar_excel()
        elif formato == 'pdf':
            filepath = exporter.exportar_pdf()
        else:
            return jsonify({'error': 'Formato no soportado'}), 400
        
        return send_file(filepath, as_attachment=True)
        
    except Exception as e:
        logger.error(f"Error al exportar: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/api/estado', methods=['GET'])
def obtener_estado():
    """Obtener estado actual del sistema"""
    return jsonify({
        'datos_cargados': datos_horarios['raw_data'] is not None,
        'horarios_generados': datos_horarios['horario_generado'] is not None,
        'grupos_disponibles': len(datos_horarios['grupos']),
        'grupos': datos_horarios['grupos'],
        'total_cursos': len(datos_horarios['cursos']),
        'total_profesores': len(datos_horarios['profesores']),
        'total_grupos': len(datos_horarios['grupos']),
        'total_aulas': len(datos_horarios['aulas']),
        'timestamp': datos_horarios['timestamp']
    })

# ========== ARCHIVOS ESTÁTICOS ==========

@app.route('/css/<path:filename>')
def serve_css(filename):
    """Servir archivos CSS"""
    css_path = os.path.join(os.path.dirname(__file__), '../frontend/css')
    return send_from_directory(css_path, filename)

@app.route('/js/<path:filename>')
def serve_js(filename):
    """Servir archivos JavaScript"""
    js_path = os.path.join(os.path.dirname(__file__), '../frontend/js')
    return send_from_directory(js_path, filename)

# ========== MANEJO DE ERRORES ==========

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Ruta no encontrada'}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Error interno: {error}", exc_info=True)
    return jsonify({'error': 'Error interno del servidor'}), 500

# ========== INICIAR APLICACIÓN ==========

if __name__ == '__main__':
    # Crear directorios si no existen
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['EXPORT_FOLDER'], exist_ok=True)
    
    # Iniciar servidor
    print("=" * 60)
    print("🎓 SISTEMA DE HORARIOS ITI - WEB")
    print("Universidad Politécnica de Victoria")
    print("=" * 60)
    print("\n🌐 Servidor iniciando en: http://localhost:5000")
    print("\n📋 Endpoints disponibles:")
    print("  - GET  /                    Página principal")
    print("  - GET  /horarios            Vista de horarios")
    print("  - GET  /grafo               Vista de grafo")
    print("  - GET  /profesor            Consulta por profesor")
    print("  - GET  /reporte             Reporte de validación")
    print("  - POST /api/upload          Subir archivo")
    print("  - POST /api/generar-horarios Generar horarios")
    print("  - GET  /api/grupos          Lista de grupos")
    print("  - GET  /api/horario/<grupo> Horario por grupo")
    print("  - GET  /api/grafo           Datos del grafo")
    print("  - GET  /api/validacion      Reporte de validación")
    print("  - GET  /api/exportar/<fmt>  Exportar horarios")
    print("\n" + "=" * 60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
