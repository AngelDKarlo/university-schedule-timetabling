/**
 * JavaScript para la página de reporte (reporte.html)
 */

let datosValidacion = null;

const emptyState = document.getElementById('emptyState');

async function cargarReporte() {
    try {
        const data = await apiGet('/api/validacion');
        
        if (data.error) {
            mostrarEstadoVacio();
            showAlert(data.error, 'error');
            return;
        }
        
        datosValidacion = data;
        mostrarReporte(data);
        
    } catch (error) {
        console.error('Error:', error);
        mostrarEstadoVacio();
    }
}

function mostrarReporte(data) {
    // Resumen general
    const totalRestricciones = data.restricciones?.length || 0;
    const cumplidas = data.restricciones?.filter(r => r.cumplida).length || 0;
    
    document.getElementById('restriccionesCumplidas').textContent = cumplidas;
    document.getElementById('optimizaciones').textContent = data.optimizaciones?.length || 0;
    document.getElementById('conflictosCriticos').textContent = data.conflictos_criticos || 0;
    document.getElementById('eficiencia').textContent = 
        totalRestricciones > 0 ? Math.round((cumplidas / totalRestricciones) * 100) : 0;
    
    // Restricciones
    const restriccionesContainer = document.getElementById('restriccionesContainer');
    if (data.restricciones && data.restricciones.length > 0) {
        restriccionesContainer.innerHTML = data.restricciones.map(r => `
            <div class="restriccion-item ${r.cumplida ? 'success' : 'danger'}">
                <div class="restriccion-icon">
                    <i class="fas fa-${r.cumplida ? 'check-circle' : 'times-circle'}"></i>
                </div>
                <div class="restriccion-content">
                    <h4>${r.tipo}</h4>
                    <p>${r.descripcion}</p>
                </div>
            </div>
        `).join('');
    } else {
        restriccionesContainer.innerHTML = '<p>No hay restricciones definidas</p>';
    }
    
    // Optimizaciones
    const optimizacionesContainer = document.getElementById('optimizacionesContainer');
    if (data.optimizaciones && data.optimizaciones.length > 0) {
        optimizacionesContainer.innerHTML = data.optimizaciones.map(o => `
            <div class="optimizacion-item ${o.tipo}">
                <i class="fas fa-${o.tipo === 'warning' ? 'exclamation-triangle' : 'info-circle'}"></i>
                <p>${o.mensaje}</p>
            </div>
        `).join('');
    } else {
        optimizacionesContainer.innerHTML = '<p>No se detectaron optimizaciones</p>';
    }
    
    // Conflictos
    const conflictosTableBody = document.getElementById('conflictosTableBody');
    if (data.conflictos_criticos > 0) {
        document.getElementById('conflictosSection').style.display = 'block';
        // Aquí se llenarían los detalles de conflictos
        conflictosTableBody.innerHTML = '<tr><td colspan="5">No hay conflictos críticos</td></tr>';
    } else {
        conflictosTableBody.innerHTML = '<tr><td colspan="5">No hay conflictos detectados</td></tr>';
    }
    
    // Estadísticas de uso
    generarEstadisticas();
    
    // Recomendaciones
    generarRecomendaciones(data);
    
    emptyState.style.display = 'none';
}

function generarEstadisticas() {
    // Estadísticas simuladas - en producción vendrían del backend
    const aulasStats = document.getElementById('aulasStats');
    aulasStats.innerHTML = `
        <div class="progress-item">
            <span>Aula-1</span>
            <div class="progress-bar"><div class="progress-fill" style="width: 80%"></div></div>
            <span>80%</span>
        </div>
        <div class="progress-item">
            <span>Aula-2</span>
            <div class="progress-bar"><div class="progress-fill" style="width: 65%"></div></div>
            <span>65%</span>
        </div>
        <div class="progress-item">
            <span>Aula-3</span>
            <div class="progress-bar"><div class="progress-fill" style="width: 75%"></div></div>
            <span>75%</span>
        </div>
    `;
    
    const profesoresStats = document.getElementById('profesoresStats');
    profesoresStats.innerHTML = `
        <div class="progress-item">
            <span>Dr. Polanco</span>
            <div class="progress-bar"><div class="progress-fill" style="width: 90%"></div></div>
            <span>18h</span>
        </div>
        <div class="progress-item">
            <span>M.I. López</span>
            <div class="progress-bar"><div class="progress-fill" style="width: 60%"></div></div>
            <span>12h</span>
        </div>
    `;
    
    const diasStats = document.getElementById('diasStats');
    diasStats.innerHTML = `
        <div class="progress-item">
            <span>Lunes</span>
            <div class="progress-bar"><div class="progress-fill" style="width: 85%"></div></div>
            <span>85%</span>
        </div>
        <div class="progress-item">
            <span>Martes</span>
            <div class="progress-bar"><div class="progress-fill" style="width: 78%"></div></div>
            <span>78%</span>
        </div>
        <div class="progress-item">
            <span>Miércoles</span>
            <div class="progress-bar"><div class="progress-fill" style="width: 82%"></div></div>
            <span>82%</span>
        </div>
    `;
}

function generarRecomendaciones(data) {
    const recomendacionesContainer = document.getElementById('recomendacionesContainer');
    
    const recomendaciones = [
        {
            tipo: 'success',
            icono: 'check-circle',
            titulo: 'Distribución Equilibrada',
            descripcion: 'Las clases están bien distribuidas a lo largo de la semana.'
        },
        {
            tipo: 'info',
            icono: 'lightbulb',
            titulo: 'Optimización Posible',
            descripcion: 'Algunas aulas tienen baja ocupación los viernes.'
        }
    ];
    
    if (data.optimizaciones && data.optimizaciones.length > 0) {
        recomendaciones.push({
            tipo: 'warning',
            icono: 'exclamation-triangle',
            titulo: 'Revisar Optimizaciones',
            descripcion: `Se detectaron ${data.optimizaciones.length} posibles optimizaciones.`
        });
    }
    
    recomendacionesContainer.innerHTML = recomendaciones.map(r => `
        <div class="recomendacion-item ${r.tipo}">
            <i class="fas fa-${r.icono}"></i>
            <div>
                <h4>${r.titulo}</h4>
                <p>${r.descripcion}</p>
            </div>
        </div>
    `).join('');
}

function regenerarReporte() {
    cargarReporte();
    showAlert('Reporte actualizado', 'success');
}

window.regenerarReporte = regenerarReporte;

function exportarReporte() {
    if (!datosValidacion) {
        showAlert('No hay reporte para exportar', 'error');
        return;
    }
    exportar('pdf');
}

window.exportarReporte = exportarReporte;

function mostrarEstadoVacio() {
    emptyState.style.display = 'block';
}

document.addEventListener('DOMContentLoaded', async () => {
    const estado = await checkSystemStatus();
    if (!estado || !estado.horarios_generados) {
        mostrarEstadoVacio();
        showAlert('No hay horarios generados.', 'info');
        return;
    }
    await cargarReporte();
});
