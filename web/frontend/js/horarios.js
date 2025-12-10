/**
 * JavaScript para la página de horarios (horarios.html)
 * Maneja la visualización de horarios por grupo
 */

let gruposDisponibles = [];
let horarioActual = null;

// ========== ELEMENTOS DEL DOM ==========

const grupoSelect = document.getElementById('grupoSelect');
const btnCargarHorario = document.getElementById('btnCargarHorario');
const horarioSection = document.getElementById('horarioSection');
const emptyState = document.getElementById('emptyState');
const horarioTableBody = document.getElementById('horarioTableBody');
const horarioTitulo = document.getElementById('horarioTitulo');
const leyendaSection = document.getElementById('leyendaSection');

// ========== EVENT LISTENERS ==========

btnCargarHorario.addEventListener('click', cargarHorario);

grupoSelect.addEventListener('change', (e) => {
    if (e.target.value) {
        btnCargarHorario.disabled = false;
    }
});

// ========== FUNCIONES ==========

/**
 * Carga los grupos disponibles
 */
async function cargarGrupos() {
    try {
        const data = await apiGet('/api/grupos');
        gruposDisponibles = data.grupos || [];
        
        if (gruposDisponibles.length === 0) {
            mostrarEstadoVacio();
            return;
        }
        
        // Llenar el select
        grupoSelect.innerHTML = '<option value="">Seleccionar grupo...</option>';
        gruposDisponibles.forEach(grupo => {
            const option = document.createElement('option');
            option.value = grupo;
            option.textContent = grupo;
            grupoSelect.appendChild(option);
        });
        
    } catch (error) {
        console.error('Error cargando grupos:', error);
        mostrarEstadoVacio();
    }
}

/**
 * Carga el horario del grupo seleccionado
 */
async function cargarHorario() {
    const grupoSeleccionado = grupoSelect.value;
    if (!grupoSeleccionado) {
        showAlert('Selecciona un grupo', 'error');
        return;
    }
    
    try {
        const data = await apiGet(`/api/horario/${grupoSeleccionado}`);
        
        if (data.error) {
            showAlert(data.error, 'error');
            return;
        }
        
        horarioActual = data;
        mostrarHorario(data);
        
    } catch (error) {
        console.error('Error cargando horario:', error);
    }
}

/**
 * Muestra el horario en la tabla
 */
function mostrarHorario(horarioData) {
    // Actualizar título
    horarioTitulo.textContent = `Horario - ${horarioData.grupo}`;
    
    // Obtener todas las franjas horarias únicas
    const franjas = obtenerFranjas(horarioData.dias);
    
    // Limpiar tabla
    horarioTableBody.innerHTML = '';
    
    // Crear filas
    franjas.forEach(franja => {
        const row = document.createElement('tr');
        
        // Columna de hora
        const horaCell = document.createElement('td');
        horaCell.className = 'hora-column';
        horaCell.textContent = franja;
        row.appendChild(horaCell);
        
        // Columnas de días
        const dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes'];
        dias.forEach(dia => {
            const cell = document.createElement('td');
            
            // Buscar clase en esta franja y día
            const clase = buscarClase(horarioData.dias, dia, franja);
            
            if (clase) {
                cell.innerHTML = crearCeldaClase(clase);
            }
            
            row.appendChild(cell);
        });
        
        horarioTableBody.appendChild(row);
    });
    
    // Mostrar secciones
    emptyState.style.display = 'none';
    horarioSection.style.display = 'block';
    leyendaSection.style.display = 'block';
    
    // Scroll a la tabla
    horarioSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

/**
 * Obtiene todas las franjas horarias del horario
 */
function obtenerFranjas(dias) {
    const franjasSet = new Set();
    
    Object.values(dias).forEach(clasesDia => {
        clasesDia.forEach(clase => {
            franjasSet.add(clase.franja);
        });
    });
    
    // Ordenar franjas
    return Array.from(franjasSet).sort((a, b) => {
        const horaA = parseInt(a.split(':')[0]);
        const horaB = parseInt(b.split(':')[0]);
        return horaA - horaB;
    });
}

/**
 * Busca una clase específica en un día y franja
 */
function buscarClase(dias, dia, franja) {
    if (!dias[dia]) return null;
    
    return dias[dia].find(clase => clase.franja === franja);
}

/**
 * Crea el HTML para una celda de clase
 */
function crearCeldaClase(clase) {
    // Extraer valores seguros
    const curso = clase.curso || 'Sin asignar';
    const profesor = typeof clase.profesor === 'string' ? clase.profesor : (clase.profesor?.nombre || 'Sin asignar');
    const aula = typeof clase.aula === 'string' ? clase.aula : (clase.aula?.nombre || 'Sin asignar');
    
    return `
        <div class="clase-cell">
            <div class="clase-nombre">
                <i class="fas fa-book"></i> ${curso}
            </div>
            <div class="clase-profesor">
                <i class="fas fa-user-tie"></i> ${profesor}
            </div>
            <div class="clase-aula">
                <i class="fas fa-door-open"></i> ${aula}
            </div>
        </div>
    `;
}

/**
 * Muestra el estado vacío
 */
function mostrarEstadoVacio() {
    emptyState.style.display = 'block';
    horarioSection.style.display = 'none';
    leyendaSection.style.display = 'none';
}

/**
 * Exporta el horario actual
 */
async function exportarHorario() {
    if (!horarioActual) {
        showAlert('No hay horario cargado', 'error');
        return;
    }
    
    // Reutilizar la función global de exportar
    await exportar('excel');
}

// Hacer disponible globalmente
window.exportarHorario = exportarHorario;

// ========== INICIALIZACIÓN ==========

document.addEventListener('DOMContentLoaded', async () => {
    console.log('Página de horarios cargada');
    
    // Verificar estado del sistema
    const estado = await checkSystemStatus();
    
    if (!estado || !estado.horarios_generados) {
        mostrarEstadoVacio();
        showAlert('No hay horarios generados. Ve a Inicio para cargar datos.', 'info');
        return;
    }
    
    // Cargar grupos
    await cargarGrupos();
});
