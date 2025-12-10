/**
 * JavaScript para la página de inicio (index.html)
 * Maneja la carga de archivos y generación de horarios
 */

let archivoSeleccionado = null;

// ========== ELEMENTOS DEL DOM ==========

const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const fileInfo = document.getElementById('fileInfo');
const fileName = document.getElementById('fileName');
const fileSize = document.getElementById('fileSize');
const removeFileBtn = document.getElementById('removeFile');
const processingStatus = document.getElementById('processingStatus');
const resumenSection = document.getElementById('resumenSection');
const resultadoSection = document.getElementById('resultadoSection');
const btnGenerar = document.getElementById('btnGenerar');
const generationStatus = document.getElementById('generationStatus');

// ========== CARGA INICIAL ==========

// Al cargar la página, verificar si hay datos precargados
document.addEventListener('DOMContentLoaded', async () => {
    await verificarDatosPrecargados();
});

// ========== EVENT LISTENERS ==========

// Drag and drop
uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.style.borderColor = '#6b3fa0';
    uploadArea.style.background = '#f9f5ff';
});

uploadArea.addEventListener('dragleave', () => {
    uploadArea.style.borderColor = '#8e5bc5';
    uploadArea.style.background = '#f5f5f5';
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.style.borderColor = '#8e5bc5';
    uploadArea.style.background = '#f5f5f5';
    
    const file = e.dataTransfer.files[0];
    if (file) {
        handleFileSelect(file);
    }
});

// Click para seleccionar archivo
fileInput.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (file) {
        handleFileSelect(file);
    }
});

// Remover archivo
removeFileBtn.addEventListener('click', () => {
    archivoSeleccionado = null;
    fileInput.value = '';
    uploadArea.style.display = 'block';
    fileInfo.style.display = 'none';
    resumenSection.style.display = 'none';
    resultadoSection.style.display = 'none';
});

// Generar horarios
btnGenerar.addEventListener('click', generarHorarios);

// ========== FUNCIONES ==========

/**
 * Maneja la selección de archivo
 */
function handleFileSelect(file) {
    // Validar tipo de archivo
    const validTypes = [
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'application/vnd.ms-excel',
        'application/json'
    ];
    
    if (!validTypes.includes(file.type) && 
        !file.name.endsWith('.xlsx') && 
        !file.name.endsWith('.xls') && 
        !file.name.endsWith('.json')) {
        showAlert('Tipo de archivo no válido. Use Excel (.xlsx, .xls) o JSON (.json)', 'error');
        return;
    }
    
    // Validar tamaño (max 16MB)
    if (file.size > 16 * 1024 * 1024) {
        showAlert('El archivo es demasiado grande (máx. 16MB)', 'error');
        return;
    }
    
    archivoSeleccionado = file;
    
    // Mostrar información del archivo
    fileName.textContent = file.name;
    fileSize.textContent = formatFileSize(file.size);
    
    uploadArea.style.display = 'none';
    fileInfo.style.display = 'block';
    
    // Subir archivo automáticamente
    uploadFile();
}

/**
 * Sube el archivo al servidor
 */
async function uploadFile() {
    if (!archivoSeleccionado) return;
    
    try {
        processingStatus.style.display = 'block';
        
        const formData = new FormData();
        formData.append('file', archivoSeleccionado);
        
        const resultado = await apiPost('/api/upload', formData);
        
        processingStatus.style.display = 'none';
        
        if (resultado.success) {
            showAlert('Archivo procesado correctamente', 'success');
            mostrarResumen(resultado.resumen);
        } else {
            showAlert('Error al procesar archivo', 'error');
        }
    } catch (error) {
        processingStatus.style.display = 'none';
        console.error('Error:', error);
    }
}

/**
 * Muestra el resumen de datos cargados
 */
function mostrarResumen(resumen) {
    document.getElementById('totalCursos').textContent = resumen.cursos || 0;
    document.getElementById('totalProfesores').textContent = resumen.profesores || 0;
    document.getElementById('totalGrupos').textContent = resumen.grupos || 0;
    document.getElementById('totalAulas').textContent = resumen.aulas || 0;
    
    resumenSection.style.display = 'block';
    
    // Scroll suave al resumen
    resumenSection.scrollIntoView({ behavior: 'smooth', block: 'center' });
}

/**
 * Genera los horarios
 */
async function generarHorarios() {
    try {
        btnGenerar.disabled = true;
        generationStatus.style.display = 'block';
        
        const resultado = await apiPost('/api/generar-horarios');
        
        generationStatus.style.display = 'none';
        btnGenerar.disabled = false;
        
        if (resultado.success) {
            mostrarResultado(resultado.estadisticas);
            showAlert('Horarios generados exitosamente', 'success');
        } else {
            showAlert('Error al generar horarios', 'error');
        }
    } catch (error) {
        generationStatus.style.display = 'none';
        btnGenerar.disabled = false;
        console.error('Error:', error);
    }
}

/**
 * Muestra el resultado de la generación
 */
function mostrarResultado(estadisticas) {
    const mensaje = `
        Se generaron horarios para ${estadisticas.grupos} grupos con 
        ${estadisticas.cursos_asignados} de ${estadisticas.total_cursos} cursos asignados.
    `;
    
    document.getElementById('resultadoMensaje').textContent = mensaje;
    
    resultadoSection.style.display = 'block';
    
    // Scroll suave al resultado
    resultadoSection.scrollIntoView({ behavior: 'smooth', block: 'center' });
}

/**
 * Verifica si hay datos precargados desde CSVs
 */
async function verificarDatosPrecargados() {
    try {
        const estado = await apiGet('/api/estado');
        
        // Si hay datos cargados, mostrarlos automáticamente
        if (estado.datos_cargados) {
            console.log('✅ Datos precargados detectados:', estado);
            
            // Ocultar sección de carga
            document.querySelector('.upload-section').style.display = 'none';
            
            // Mostrar mensaje de datos precargados
            const uploadSection = document.querySelector('.upload-section');
            const mensaje = document.createElement('div');
            mensaje.className = 'card';
            mensaje.innerHTML = `
                <div class="card-body" style="text-align: center; padding: 2rem;">
                    <i class="fas fa-check-circle" style="font-size: 3rem; color: #28a745; margin-bottom: 1rem;"></i>
                    <h3 style="color: #6b3fa0; margin-bottom: 0.5rem;">✅ Datos Cargados Automáticamente</h3>
                    <p style="color: #666; margin-bottom: 1.5rem;">
                        Los horarios han sido cargados desde los archivos CSV del sistema
                    </p>
                    <button class="btn btn-secondary" onclick="location.reload()">
                        <i class="fas fa-upload"></i> Cargar otro archivo
                    </button>
                </div>
            `;
            uploadSection.parentNode.insertBefore(mensaje, uploadSection);
            
            // Mostrar resumen
            mostrarResumen({
                cursos: estado.total_cursos || 0,
                profesores: estado.total_profesores || 0,
                grupos: estado.total_grupos || 0,
                aulas: estado.total_aulas || 0
            }, estado.grupos || []);
            
            // Si ya hay horarios generados, mostrar resultado
            if (estado.horarios_generados) {
                mostrarResultado({
                    grupos: estado.total_grupos || 0,
                    cursos_asignados: estado.total_cursos || 0,
                    total_cursos: estado.total_cursos || 0
                });
            }
        }
    } catch (error) {
        console.log('ℹ️ No hay datos precargados, esperando carga manual');
    }
}

// ========== INICIALIZACIÓN ==========

document.addEventListener('DOMContentLoaded', async () => {
    console.log('Página de inicio cargada');
    
    // Verificar si ya hay datos cargados
    const estado = await checkSystemStatus();
    if (estado && estado.datos_cargados) {
        showAlert('Hay datos previamente cargados', 'info');
    }
});
