// Sistema de Préstamos - JavaScript Principal

// Configuración global
const APP_CONFIG = {
    apiBaseUrl: '',
    refreshInterval: 30000, // 30 segundos
    animationDuration: 300
};

// Clase principal de la aplicación
class SistemaPrestamosApp {
    constructor() {
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.setupTooltips();
        this.setupAnimations();
        this.setupAutoRefresh();
        console.log('🚀 Sistema de Préstamos Web inicializado');
    }

    setupEventListeners() {
        // Event listeners globales
        document.addEventListener('DOMContentLoaded', () => {
            this.handlePageLoad();
        });

        // Event listeners para formularios
        this.setupFormValidation();
        
        // Event listeners para tablas
        this.setupTableInteractions();
    }

    setupTooltips() {
        // Inicializar tooltips de Bootstrap
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }

    setupAnimations() {
        // Agregar animaciones a elementos que entran en viewport
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('fade-in-up');
                }
            });
        }, observerOptions);

        // Observar cards y elementos importantes
        document.querySelectorAll('.card, .btn, .table').forEach(el => {
            observer.observe(el);
        });
    }

    setupAutoRefresh() {
        // Actualizar estadísticas automáticamente si estamos en la página principal
        if (window.location.pathname === '/') {
            setInterval(() => {
                this.refreshStats();
            }, APP_CONFIG.refreshInterval);
        }
    }

    setupFormValidation() {
        // Validación en tiempo real para formularios
        document.querySelectorAll('form').forEach(form => {
            const inputs = form.querySelectorAll('input[required], select[required], textarea[required]');
            
            inputs.forEach(input => {
                input.addEventListener('blur', () => this.validateField(input));
                input.addEventListener('input', () => this.clearFieldValidation(input));
            });

            // Validación al enviar formulario
            form.addEventListener('submit', (e) => this.validateForm(e));
        });
    }

    setupTableInteractions() {
        // Hacer filas de tabla clickeables
        document.querySelectorAll('.table tbody tr').forEach(row => {
            row.addEventListener('click', (e) => {
                // No activar si se hace clic en botones o enlaces
                if (e.target.tagName === 'BUTTON' || e.target.tagName === 'A' || e.target.closest('button') || e.target.closest('a')) {
                    return;
                }
                
                this.handleTableRowClick(row);
            });
        });

        // Búsqueda en tiempo real para tablas
        document.querySelectorAll('.search-input').forEach(input => {
            input.addEventListener('input', (e) => this.handleTableSearch(e.target));
        });
    }

    validateField(field) {
        const value = field.value.trim();
        const isValid = value.length > 0;
        
        if (isValid) {
            field.classList.remove('is-invalid');
            field.classList.add('is-valid');
        } else {
            field.classList.remove('is-valid');
            field.classList.add('is-invalid');
        }
        
        return isValid;
    }

    clearFieldValidation(field) {
        field.classList.remove('is-invalid', 'is-valid');
    }

    validateForm(event) {
        const form = event.target;
        const inputs = form.querySelectorAll('input[required], select[required], textarea[required]');
        let isValid = true;

        inputs.forEach(input => {
            if (!this.validateField(input)) {
                isValid = false;
            }
        });

        if (!isValid) {
            event.preventDefault();
            this.showNotification('Por favor, complete todos los campos obligatorios', 'error');
        }
    }

    handleTableRowClick(row) {
        // Agregar efecto visual al hacer clic
        row.style.backgroundColor = 'rgba(13, 110, 253, 0.1)';
        setTimeout(() => {
            row.style.backgroundColor = '';
        }, 200);

        // Aquí puedes agregar lógica para mostrar detalles o editar
        const rowId = row.dataset.id;
        if (rowId) {
            console.log('Fila seleccionada:', rowId);
        }
    }

    handleTableSearch(input) {
        const searchTerm = input.value.toLowerCase();
        const table = input.closest('.card').querySelector('table');
        const rows = table.querySelectorAll('tbody tr');

        rows.forEach(row => {
            const text = row.textContent.toLowerCase();
            if (text.includes(searchTerm)) {
                row.style.display = '';
                row.classList.add('fade-in-up');
            } else {
                row.style.display = 'none';
            }
        });
    }

    async refreshStats() {
        try {
            const response = await fetch('/api/reporte-general');
            const data = await response.json();
            
            if (data.error) {
                console.error('Error al actualizar estadísticas:', data.error);
                return;
            }

            // Actualizar estadísticas en la página
            this.updateStatsDisplay(data);
            
        } catch (error) {
            console.error('Error al actualizar estadísticas:', error);
        }
    }

    updateStatsDisplay(stats) {
        // Actualizar contadores en tiempo real
        const elements = {
            'total_clientes': '.stats-card .card-body h2:first-child',
            'total_prestamos': '.stats-card .card-body h2:nth-child(2)',
            'monto_total_prestado': '.stats-card .card-body h2:nth-child(3)',
            'prestamos_activos': '.stats-card .card-body h2:nth-child(4)'
        };

        Object.entries(elements).forEach(([key, selector]) => {
            const element = document.querySelector(selector);
            if (element && stats[key] !== undefined) {
                const currentValue = element.textContent;
                const newValue = key.includes('monto') ? 
                    `$${stats[key].toLocaleString('es-ES', {minimumFractionDigits: 2})}` : 
                    stats[key];
                
                if (currentValue !== newValue) {
                    element.textContent = newValue;
                    element.style.animation = 'fadeInUp 0.5s ease-out';
                }
            }
        });
    }

    showNotification(message, type = 'info') {
        // Crear notificación personalizada
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        notification.style.cssText = `
            top: 20px;
            right: 20px;
            z-index: 9999;
            min-width: 300px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        `;
        
        notification.innerHTML = `
            <i class="fas fa-${type === 'error' ? 'exclamation-triangle' : 'info-circle'} me-2"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        document.body.appendChild(notification);

        // Auto-remover después de 5 segundos
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 5000);
    }

    handlePageLoad() {
        // Lógica específica de cada página
        const currentPage = window.location.pathname;
        
        switch (currentPage) {
            case '/':
                this.initDashboard();
                break;
            case '/clientes':
                this.initClientesPage();
                break;
            case '/prestamos':
                this.initPrestamosPage();
                break;
            case '/pagos':
                this.initPagosPage();
                break;
            case '/reportes':
                this.initReportesPage();
                break;
        }
    }

    initDashboard() {
        // Inicializar dashboard
        console.log('Dashboard inicializado');
    }

    initClientesPage() {
        // Inicializar página de clientes
        console.log('Página de clientes inicializada');
    }

    initPrestamosPage() {
        // Inicializar página de préstamos
        console.log('Página de préstamos inicializada');
    }

    initPagosPage() {
        // Inicializar página de pagos
        console.log('Página de pagos inicializada');
    }

    initReportesPage() {
        // Inicializar página de reportes
        console.log('Página de reportes inicializada');
    }
}

// Utilidades globales
const Utils = {
    formatCurrency: (amount) => {
        return new Intl.NumberFormat('es-ES', {
            style: 'currency',
            currency: 'USD'
        }).format(amount);
    },

    formatDate: (date) => {
        return new Intl.DateTimeFormat('es-ES', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        }).format(new Date(date));
    },

    debounce: (func, wait) => {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },

    showLoading: () => {
        // Mostrar indicador de carga
        const loading = document.createElement('div');
        loading.id = 'loading-overlay';
        loading.innerHTML = `
            <div class="d-flex justify-content-center align-items-center h-100">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Cargando...</span>
                </div>
            </div>
        `;
        loading.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(255,255,255,0.8);
            z-index: 9999;
            display: flex;
            justify-content: center;
            align-items: center;
        `;
        document.body.appendChild(loading);
    },

    hideLoading: () => {
        const loading = document.getElementById('loading-overlay');
        if (loading) {
            loading.remove();
        }
    }
};

// Inicializar aplicación cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    window.app = new SistemaPrestamosApp();
});

// Exportar para uso global
window.Utils = Utils;
