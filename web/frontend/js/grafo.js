/**
 * JavaScript para la página del grafo (grafo.html)
 * Visualización interactiva del grafo de conflictos con D3.js
 */

let datosGrafo = null;
let simulation = null;
let svg = null;
let g = null;

// ========== FUNCIONES ==========

/**
 * Carga los datos del grafo desde la API
 */
async function cargarGrafo() {
    try {
        const data = await apiGet('/api/grafo');
        
        if (data.error) {
            showAlert(data.error, 'error');
            return;
        }
        
        datosGrafo = data;
        
        // Actualizar estadísticas
        document.getElementById('totalNodos').textContent = data.estadisticas?.total_nodos || data.nodos.length;
        document.getElementById('totalEnlaces').textContent = data.estadisticas?.total_conexiones || (data.conexiones?.length || 0);
        document.getElementById('totalConflictos').textContent = data.estadisticas?.total_conflictos || 0;
        
        // Renderizar grafo
        renderizarGrafo(data);
        
    } catch (error) {
        console.error('Error cargando grafo:', error);
        showAlert('Error al cargar el grafo', 'error');
    }
}

/**
 * Renderiza el grafo usando D3.js
 */
function renderizarGrafo(data) {
    // Limpiar SVG anterior
    d3.select('#grafoSvg').selectAll('*').remove();
    
    const container = document.getElementById('grafoContainer');
    const width = container.clientWidth;
    const height = container.clientHeight;
    
    // Crear SVG
    svg = d3.select('#grafoSvg')
        .attr('width', width)
        .attr('height', height)
        .attr('viewBox', [0, 0, width, height]);
    
    // Grupo principal para zoom
    g = svg.append('g');
    
    // Configurar zoom
    const zoom = d3.zoom()
        .scaleExtent([0.2, 5])
        .on('zoom', (event) => {
            g.attr('transform', event.transform);
        });
    
    svg.call(zoom);
    
    // Copiar datos para no mutar los originales
    const nodos = data.nodos.map(d => ({...d}));
    const enlaces = (data.conexiones || data.enlaces || []).map(d => ({...d}));
    
    // Crear simulación de fuerzas MEJORADA
    simulation = d3.forceSimulation(nodos)
        .force('link', d3.forceLink(enlaces)
            .id(d => d.id)
            .distance(150)
            .strength(0.5))
        .force('charge', d3.forceManyBody()
            .strength(-500)
            .distanceMax(400))
        .force('center', d3.forceCenter(width / 2, height / 2))
        .force('collision', d3.forceCollide()
            .radius(50)
            .strength(0.8))
        .force('x', d3.forceX(width / 2).strength(0.1))
        .force('y', d3.forceY(height / 2).strength(0.1));
    
    // Definir marcadores de flecha para los enlaces
    if (enlaces.length > 0) {
        svg.append('defs').selectAll('marker')
            .data(['profesor', 'horario'])
            .enter().append('marker')
            .attr('id', d => `arrow-${d}`)
            .attr('viewBox', '0 -5 10 10')
            .attr('refX', 35)
            .attr('refY', 0)
            .attr('markerWidth', 6)
            .attr('markerHeight', 6)
            .attr('orient', 'auto')
            .append('path')
            .attr('d', 'M0,-5L10,0L0,5')
            .attr('fill', d => d === 'profesor' ? '#e74c3c' : '#3498db');
    }
    
    // Crear enlaces
    const link = g.append('g')
        .attr('class', 'enlaces')
        .selectAll('line')
        .data(enlaces)
        .enter()
        .append('line')
        .attr('class', d => `enlace enlace-${d.tipo}`)
        .attr('stroke', d => d.tipo === 'profesor' ? '#e74c3c' : '#3498db')
        .attr('stroke-width', 3)
        .attr('stroke-opacity', 0.6)
        .attr('marker-end', d => `url(#arrow-${d.tipo})`);
    
    // Crear grupos de nodos
    const node = g.append('g')
        .attr('class', 'nodos')
        .selectAll('g')
        .data(nodos)
        .enter()
        .append('g')
        .attr('class', 'nodo')
        .call(d3.drag()
            .on('start', dragstarted)
            .on('drag', dragged)
            .on('end', dragended));
    
    // Círculos de nodos con efecto de sombra
    node.append('circle')
        .attr('r', 30)
        .attr('fill', d => getGroupColor(d.grupo))
        .attr('stroke', '#fff')
        .attr('stroke-width', 3)
        .attr('filter', 'drop-shadow(0px 2px 4px rgba(0,0,0,0.3))')
        .style('cursor', 'pointer');
    
    // Texto de nodos (iniciales)
    node.append('text')
        .attr('text-anchor', 'middle')
        .attr('dy', '.35em')
        .attr('fill', '#fff')
        .attr('font-weight', 'bold')
        .attr('font-size', '14px')
        .attr('pointer-events', 'none')
        .text(d => obtenerIniciales(d.nombre));
    
    // Etiquetas debajo de los nodos
    node.append('text')
        .attr('text-anchor', 'middle')
        .attr('dy', '3.5em')
        .attr('fill', '#333')
        .attr('font-size', '10px')
        .attr('font-weight', '500')
        .attr('pointer-events', 'none')
        .text(d => d.grupo);
    
    // Tooltip
    const tooltip = d3.select('body').selectAll('#tooltip')
        .data([null])
        .join('div')
        .attr('id', 'tooltip')
        .style('position', 'absolute')
        .style('display', 'none')
        .style('background', 'rgba(0,0,0,0.8)')
        .style('color', '#fff')
        .style('padding', '10px')
        .style('border-radius', '5px')
        .style('font-size', '12px')
        .style('pointer-events', 'none')
        .style('z-index', '1000');
    
    node.on('mouseover', (event, d) => {
        // Resaltar nodo
        d3.select(event.currentTarget).select('circle')
            .transition().duration(200)
            .attr('r', 35)
            .attr('stroke-width', 4);
        
        tooltip
            .style('display', 'block')
            .html(`
                <strong>${d.nombre}</strong><br>
                <small>Grupo: ${d.grupo}</small><br>
                <small>Profesor: ${d.profesor || 'Sin asignar'}</small><br>
                <small>Horas/semana: ${d.horas}</small>
            `);
    })
    .on('mousemove', (event) => {
        tooltip
            .style('left', (event.pageX + 15) + 'px')
            .style('top', (event.pageY - 15) + 'px');
    })
    .on('mouseout', (event) => {
        d3.select(event.currentTarget).select('circle')
            .transition().duration(200)
            .attr('r', 30)
            .attr('stroke-width', 3);
        
        tooltip.style('display', 'none');
    })
    .on('click', (event, d) => {
        mostrarDetallesNodo(d);
    });
    
    // Actualizar posiciones en cada tick
    simulation.on('tick', () => {
        link
            .attr('x1', d => d.source.x)
            .attr('y1', d => d.source.y)
            .attr('x2', d => d.target.x)
            .attr('y2', d => d.target.y);
        
        node.attr('transform', d => `translate(${d.x},${d.y})`);
    });
    
    // Zoom inicial para centrar el grafo
    svg.transition().duration(750).call(
        zoom.transform,
        d3.zoomIdentity.translate(0, 0).scale(0.8)
    );
}

/**
 * Funciones de drag para D3
 */
function dragstarted(event, d) {
    if (!event.active) simulation.alphaTarget(0.3).restart();
    d.fx = d.x;
    d.fy = d.y;
}

function dragged(event, d) {
    d.fx = event.x;
    d.fy = event.y;
}

function dragended(event, d) {
    if (!event.active) simulation.alphaTarget(0);
    d.fx = null;
    d.fy = null;
}

/**
 * Obtiene las iniciales de un nombre
 */
function obtenerIniciales(nombre) {
    const palabras = nombre.split(' ').filter(p => p.length > 2);
    if (palabras.length === 1) return palabras[0].substring(0, 2).toUpperCase();
    return palabras.map(p => p[0]).join('').substring(0, 3).toUpperCase();
}

/**
 * Obtiene color por grupo
 */
function getGroupColor(grupo) {
    const colores = {
        'ITI-1V': '#3498db',    // Azul
        'ITI-2M1': '#e74c3c',   // Rojo
        'ITI-2M2': '#e67e22',   // Naranja
        'ITI-2V': '#9b59b6',    // Púrpura
        'ITI-4V': '#1abc9c',    // Turquesa
        'ITI-5M1': '#f39c12',   // Amarillo oscuro
        'ITI-5M2': '#d35400',   // Naranja oscuro
        'ITI-5V': '#16a085',    // Verde azulado
        'ITI-7V': '#27ae60',    // Verde
        'ITI-8M': '#2980b9',    // Azul oscuro
        'ITI-8V': '#8e44ad'     // Morado
    };
    
    return colores[grupo] || '#95a5a6'; // Gris por defecto
}

/**
 * Muestra detalles de un nodo
 */
function mostrarDetallesNodo(nodo) {
    document.getElementById('detalleNombre').textContent = nodo.nombre;
    document.getElementById('detalleGrupo').textContent = nodo.grupo;
    document.getElementById('detalleProfesor').textContent = nodo.profesor || 'Sin asignar';
    document.getElementById('detalleHoras').textContent = nodo.horas;
    
    // Buscar conflictos
    const conflictos = datosGrafo.enlaces.filter(
        e => e.source.id === nodo.id || e.target.id === nodo.id
    );
    
    const conflictosContainer = document.getElementById('detalleConflictos');
    if (conflictos.length > 0) {
        conflictosContainer.innerHTML = `
            <h5><i class="fas fa-exclamation-triangle"></i> Conflictos (${conflictos.length})</h5>
            <ul>
                ${conflictos.map(c => {
                    const otroNodo = c.source.id === nodo.id ? c.target : c.source;
                    return `<li>${c.tipo === 'profesor' ? 'Profesor' : 'Horario'}: ${otroNodo.nombre}</li>`;
                }).join('')}
            </ul>
        `;
    } else {
        conflictosContainer.innerHTML = '<p>Sin conflictos detectados</p>';
    }
    
    detallesNodo.style.display = 'block';
    detallesNodo.scrollIntoView({ behavior: 'smooth' });
}

/**
 * Cierra el panel de detalles
 */
function cerrarDetalles() {
    detallesNodo.style.display = 'none';
}

window.cerrarDetalles = cerrarDetalles;

/**
 * Aplica filtros al grafo
 */
function aplicarFiltros() {
    if (!datosGrafo) return;
    
    const tipo = filtroTipo.value;
    
    let nodosFiltrados = [...datosGrafo.nodos];
    let enlacesFiltrados = [...datosGrafo.enlaces || []];
    
    if (tipo === 'profesor') {
        enlacesFiltrados = enlacesFiltrados.filter(e => e.tipo === 'profesor');
    } else if (tipo === 'horario') {
        enlacesFiltrados = enlacesFiltrados.filter(e => e.tipo === 'horario');
    }
    
    renderizarGrafo({
        nodos: nodosFiltrados,
        enlaces: enlacesFiltrados
    });
}

/**
 * Reinicia la vista del grafo
 */
function reiniciarVista() {
    if (!datosGrafo) return;
    
    filtroTipo.value = 'todos';
    
    renderizarGrafo(datosGrafo);
}

/**
 * Descarga el grafo como SVG
 */
function descargarGrafo() {
    if (!svg) {
        showAlert('No hay grafo para descargar', 'error');
        return;
    }
    
    const svgData = document.getElementById('grafoSvg').outerHTML;
    const blob = new Blob([svgData], { type: 'image/svg+xml' });
    const url = URL.createObjectURL(blob);
    
    const a = document.createElement('a');
    a.href = url;
    a.download = `grafo_horarios_${new Date().getTime()}.svg`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    showAlert('Grafo descargado exitosamente', 'success');
}

window.descargarGrafo = descargarGrafo;

/**
 * Toggle pantalla completa
 */
function toggleFullscreen() {
    const container = document.getElementById('grafoContainer');
    if (!document.fullscreenElement) {
        container.requestFullscreen();
    } else {
        document.exitFullscreen();
    }
}

window.toggleFullscreen = toggleFullscreen;

// ========== INICIALIZACIÓN ==========

document.addEventListener('DOMContentLoaded', async () => {
    console.log('Página de grafo cargada');
    
    // Obtener elementos del DOM
    const btnActualizar = document.getElementById('btnActualizar');
    const btnReiniciar = document.getElementById('btnReiniciar');
    const filtroTipo = document.getElementById('filtroTipo');
    
    // Registrar event listeners
    if (btnActualizar) {
        btnActualizar.addEventListener('click', () => cargarGrafo());
    }
    
    if (btnReiniciar) {
        btnReiniciar.addEventListener('click', () => reiniciarVista());
    }
    
    if (filtroTipo) {
        filtroTipo.addEventListener('change', () => aplicarFiltros());
    }
    
    // Cargar grafo directamente
    await cargarGrafo();
});
