/**
 * SISTEMA DE HORARIOS ITI - JavaScript Principal
 * Funciones compartidas entre todas las páginas
 */

// API Base URL
const API_BASE = '';

// ========== UTILIDADES GENERALES ==========

/**
 * Muestra una alerta temporal
 */
function showAlert(message, type = 'info') {
    const container = document.getElementById('alertContainer');
    if (!container) return;
    
    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    alert.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'times-circle' : 'info-circle'}"></i>
        <span>${message}</span>
    `;
    
    container.appendChild(alert);
    
    setTimeout(() => {
        alert.style.animation = 'slideIn 0.3s ease reverse';
        setTimeout(() => alert.remove(), 300);
    }, 5000);
}

/**
 * Realiza petición GET a la API
 */
async function apiGet(endpoint) {
    try {
        const response = await fetch(`${API_BASE}${endpoint}`);
        if (!response.ok) {
            throw new Error(`Error ${response.status}: ${response.statusText}`);
        }
        return await response.json();
    } catch (error) {
        console.error('Error en GET:', error);
        showAlert(`Error: ${error.message}`, 'error');
        throw error;
    }
}

/**
 * Realiza petición POST a la API
 */
async function apiPost(endpoint, data = null) {
    try {
        const options = {
            method: 'POST',
            headers: data instanceof FormData ? {} : {'Content-Type': 'application/json'}
        };
        
        if (data) {
            options.body = data instanceof FormData ? data : JSON.stringify(data);
        }
        
        const response = await fetch(`${API_BASE}${endpoint}`, options);
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || `Error ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error('Error en POST:', error);
        showAlert(`Error: ${error.message}`, 'error');
        throw error;
    }
}

/**
 * Verifica el estado del sistema
 */
async function checkSystemStatus() {
    try {
        const estado = await apiGet('/api/estado');
        return estado;
    } catch (error) {
        console.error('Error verificando estado:', error);
        return null;
    }
}

/**
 * Formatea el nombre de un día
 */
function formatDay(day) {
    const days = {
        'monday': 'Lunes',
        'tuesday': 'Martes',
        'wednesday': 'Miércoles',
        'thursday': 'Jueves',
        'friday': 'Viernes',
        'saturday': 'Sábado',
        'sunday': 'Domingo'
    };
    return days[day.toLowerCase()] || day;
}

/**
 * Formatea una franja horaria
 */
function formatTimeSlot(slot) {
    return slot; // Por ahora retorna tal cual
}

/**
 * Exporta horarios en formato especificado
 */
async function exportar(formato) {
    try {
        showAlert(`Generando archivo ${formato.toUpperCase()}...`, 'info');
        
        const response = await fetch(`${API_BASE}/api/exportar/${formato}`);
        if (!response.ok) {
            throw new Error('Error al exportar');
        }
        
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `horarios_${new Date().getTime()}.${formato === 'pdf' ? 'pdf' : formato === 'excel' ? 'xlsx' : 'json'}`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
        
        showAlert(`Archivo ${formato.toUpperCase()} descargado exitosamente`, 'success');
    } catch (error) {
        console.error('Error exportando:', error);
        showAlert(`Error al exportar: ${error.message}`, 'error');
    }
}

/**
 * Trunca texto largo
 */
function truncate(text, maxLength = 50) {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
}

/**
 * Capitaliza primera letra
 */
function capitalize(text) {
    return text.charAt(0).toUpperCase() + text.slice(1).toLowerCase();
}

/**
 * Obtiene color por grupo
 */
function getGroupColor(grupo) {
    const colors = [
        '#9b59b6', '#3498db', '#e74c3c', '#f39c12', 
        '#1abc9c', '#34495e', '#16a085', '#27ae60'
    ];
    const hash = grupo.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0);
    return colors[hash % colors.length];
}

/**
 * Formatea tamaño de archivo
 */
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

/**
 * Debounce function
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// ========== INICIALIZACIÓN ==========

document.addEventListener('DOMContentLoaded', async () => {
    console.log('Sistema de Horarios ITI - Inicializado');
    
    // Verificar estado del sistema
    const estado = await checkSystemStatus();
    if (estado) {
        console.log('Estado del sistema:', estado);
    }
});

// ========== EXPORTAR FUNCIONES ==========

window.showAlert = showAlert;
window.apiGet = apiGet;
window.apiPost = apiPost;
window.checkSystemStatus = checkSystemStatus;
window.exportar = exportar;
window.formatDay = formatDay;
window.formatTimeSlot = formatTimeSlot;
window.truncate = truncate;
window.capitalize = capitalize;
window.getGroupColor = getGroupColor;
window.formatFileSize = formatFileSize;
window.debounce = debounce;
