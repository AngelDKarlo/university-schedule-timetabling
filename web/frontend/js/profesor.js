/**
 * JavaScript para la página de profesor (profesor.html)
 */

let profesoresData = [];
let profesorActual = null;

const profesorSelect = document.getElementById('profesorSelect');
const btnBuscar = document.getElementById('btnBuscar');
const infoProfesorSection = document.getElementById('infoProfesorSection');
const listaProfesoresSection = document.getElementById('listaProfesoresSection');
const emptyState = document.getElementById('emptyState');
const searchProfesor = document.getElementById('searchProfesor');

// Event Listeners
btnBuscar.addEventListener('click', buscarProfesor);
searchProfesor.addEventListener('input', debounce(filtrarProfesores, 300));

async function cargarProfesores() {
    try {
        const data = await apiGet('/api/profesores');
        profesoresData = data.profesores || [];
        
        if (profesoresData.length === 0) {
            mostrarEstadoVacio();
            return;
        }
        
        // Llenar select
        profesorSelect.innerHTML = '<option value="">Seleccionar profesor...</option>';
        profesoresData.forEach(prof => {
            const option = document.createElement('option');
            option.value = prof.nombre;
            option.textContent = prof.nombre;
            profesorSelect.appendChild(option);
        });
        
        // Mostrar grid de profesores
        mostrarGridProfesores(profesoresData);
        
    } catch (error) {
        console.error('Error:', error);
        mostrarEstadoVacio();
    }
}

async function buscarProfesor() {
    const nombreProfesor = profesorSelect.value;
    if (!nombreProfesor) {
        showAlert('Selecciona un profesor', 'error');
        return;
    }
    
    try {
        const data = await apiGet(`/api/profesor/${encodeURIComponent(nombreProfesor)}`);
        
        if (data.error) {
            showAlert(data.error, 'error');
            return;
        }
        
        profesorActual = data;
        mostrarInfoProfesor(data);
        
    } catch (error) {
        console.error('Error:', error);
    }
}

function mostrarInfoProfesor(data) {
    document.getElementById('profesorNombre').textContent = data.profesor;
    document.getElementById('profesorCurso').textContent = data.info?.curso || '';
    document.getElementById('totalClases').textContent = data.total_clases || 0;
    document.getElementById('horasAsignadas').textContent = data.info?.horas_asignadas || 0;
    
    // Clases asignadas
    const clasesContainer = document.getElementById('clasesContainer');
    clasesContainer.innerHTML = data.clases.map(clase => `
        <div class="clase-card">
            <h4>${clase.curso}</h4>
            <p><i class="fas fa-users"></i> ${clase.grupo}</p>
            <p><i class="fas fa-clock"></i> ${clase.dia} - ${clase.franja}</p>
            <p><i class="fas fa-door-open"></i> ${clase.aula}</p>
        </div>
    `).join('');
    
    // Horario semanal
    const horarioBody = document.getElementById('horarioProfesorBody');
    horarioBody.innerHTML = data.clases
        .sort((a, b) => {
            const dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes'];
            return dias.indexOf(a.dia) - dias.indexOf(b.dia);
        })
        .map(clase => `
            <tr>
                <td>${clase.dia}</td>
                <td>${clase.franja}</td>
                <td>${clase.curso}</td>
                <td>${clase.grupo}</td>
                <td>${clase.aula}</td>
            </tr>
        `).join('');
    
    // Disponibilidad
    mostrarDisponibilidad(data.horario_por_dia);
    
    infoProfesorSection.style.display = 'block';
    infoProfesorSection.scrollIntoView({ behavior: 'smooth' });
}

function mostrarDisponibilidad(horarioPorDia) {
    const dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes'];
    const franjas = ['7:00-8:30', '8:30-10:00', '10:00-11:30', '11:30-13:00',
                     '13:00-14:30', '14:30-16:00', '16:00-17:30', '17:30-19:00', '19:00-20:30'];
    
    const grid = document.getElementById('disponibilidadGrid');
    let html = '<div class="disp-header"><div></div>';
    
    dias.forEach(dia => {
        html += `<div class="disp-dia">${dia.substring(0, 3)}</div>`;
    });
    html += '</div>';
    
    franjas.forEach(franja => {
        html += `<div class="disp-row"><div class="disp-franja">${franja}</div>`;
        dias.forEach(dia => {
            const ocupado = horarioPorDia[dia]?.some(c => c.franja === franja);
            const cellClass = ocupado ? 'ocupado' : 'libre';
            const cellId = `cell-${dia}-${franja.replace(/:/g, '-')}`;
            html += `<div class="disp-cell ${cellClass}" 
                          id="${cellId}"
                          data-dia="${dia}" 
                          data-franja="${franja}"
                          onclick="toggleDisponibilidad('${dia}', '${franja}', ${ocupado})"
                          title="${ocupado ? 'Click para marcar como disponible' : 'Click para marcar como ocupado'}">
                ${ocupado ? '<i class="fas fa-times"></i>' : '<i class="fas fa-check"></i>'}
            </div>`;
        });
        html += '</div>';
    });
    
    grid.innerHTML = html;
}

function mostrarGridProfesores(profesores) {
    const grid = document.getElementById('profesoresGrid');
    grid.innerHTML = profesores.map(prof => `
        <div class="profesor-card" onclick="seleccionarProfesor('${prof.nombre}')">
            <div class="profesor-avatar-small">
                <i class="fas fa-user-circle"></i>
            </div>
            <div class="profesor-info">
                <h4>${prof.nombre}</h4>
                <p><i class="fas fa-book"></i> ${prof.cursos?.length || 0} cursos</p>
                <p><i class="fas fa-clock"></i> ${prof.horas_asignadas || 0} horas</p>
            </div>
        </div>
    `).join('');
}

function seleccionarProfesor(nombre) {
    profesorSelect.value = nombre;
    buscarProfesor();
}

window.seleccionarProfesor = seleccionarProfesor;

function filtrarProfesores() {
    const busqueda = searchProfesor.value.toLowerCase();
    const filtrados = profesoresData.filter(prof => 
        prof.nombre.toLowerCase().includes(busqueda)
    );
    mostrarGridProfesores(filtrados);
}

function exportarProfesor() {
    if (!profesorActual) {
        showAlert('No hay profesor seleccionado', 'error');
        return;
    }
    exportar('pdf');
}

window.exportarProfesor = exportarProfesor;

// Nueva función para cambiar disponibilidad
function toggleDisponibilidad(dia, franja, estaOcupado) {
    if (!profesorActual) return;
    
    const cellId = `cell-${dia}-${franja.replace(/:/g, '-')}`;
    const cell = document.getElementById(cellId);
    
    if (!cell) return;
    
    // Cambiar estado visual
    if (estaOcupado) {
        // Marcar como disponible
        cell.classList.remove('ocupado');
        cell.classList.add('libre');
        cell.innerHTML = '<i class="fas fa-check"></i>';
        cell.title = 'Click para marcar como ocupado';
        cell.setAttribute('onclick', `toggleDisponibilidad('${dia}', '${franja}', false)`);
        
        showAlert(`${dia} ${franja} marcado como DISPONIBLE`, 'success');
    } else {
        // Marcar como ocupado
        cell.classList.remove('libre');
        cell.classList.add('ocupado');
        cell.innerHTML = '<i class="fas fa-times"></i>';
        cell.title = 'Click para marcar como disponible';
        cell.setAttribute('onclick', `toggleDisponibilidad('${dia}', '${franja}', true)`);
        
        showAlert(`${dia} ${franja} marcado como OCUPADO`, 'info');
    }
    
    // Aquí podrías guardar los cambios en el servidor
    // await guardarDisponibilidad(profesorActual.profesor, dia, franja, !estaOcupado);
}

window.toggleDisponibilidad = toggleDisponibilidad;

function mostrarEstadoVacio() {
    emptyState.style.display = 'block';
    infoProfesorSection.style.display = 'none';
    listaProfesoresSection.style.display = 'none';
}

document.addEventListener('DOMContentLoaded', async () => {
    const estado = await checkSystemStatus();
    if (!estado || !estado.horarios_generados) {
        mostrarEstadoVacio();
        showAlert('No hay horarios generados.', 'info');
        return;
    }
    await cargarProfesores();
});
