// Script de diagnóstico para la consola del navegador
// Copiar y pegar este código en la consola del navegador (F12) en la página de reportes

console.log("🚀 Iniciando diagnóstico de consola...");

// Función para probar la API de préstamos activos
async function testPrestamosActivos() {
    console.log("🔍 Probando API de préstamos activos...");
    
    try {
        const response = await fetch('/api/prestamos-activos');
        console.log("📡 Status:", response.status);
        console.log("📋 Headers:", response.headers);
        
        if (response.ok) {
            const data = await response.json();
            console.log("✅ Datos recibidos:", data);
            console.log("📊 Tipo:", typeof data);
            console.log("📊 Longitud:", Array.isArray(data) ? data.length : "No es array");
            
            if (Array.isArray(data)) {
                data.forEach((prestamo, index) => {
                    console.log(`📋 Préstamo ${index + 1}:`, prestamo);
                });
            }
        } else {
            const errorText = await response.text();
            console.error("❌ Error en la respuesta:", errorText);
        }
    } catch (error) {
        console.error("❌ Error al hacer la petición:", error);
    }
}

// Función para probar la API de reporte general
async function testReporteGeneral() {
    console.log("🔍 Probando API de reporte general...");
    
    try {
        const response = await fetch('/api/reporte-general');
        console.log("📡 Status:", response.status);
        
        if (response.ok) {
            const data = await response.json();
            console.log("✅ Datos recibidos:", data);
            console.log("📊 Préstamos activos:", data.prestamos_activos);
        } else {
            const errorText = await response.text();
            console.error("❌ Error en la respuesta:", errorText);
        }
    } catch (error) {
        console.error("❌ Error al hacer la petición:", error);
    }
}

// Función para verificar el estado del DOM
function verificarDOM() {
    console.log("🔍 Verificando elementos del DOM...");
    
    const prestamosActivos = document.getElementById('prestamosActivos');
    const estadoSistema = document.getElementById('estadoSistema');
    
    console.log("📋 Elemento prestamosActivos:", prestamosActivos);
    console.log("📋 Elemento estadoSistema:", estadoSistema);
    
    if (prestamosActivos) {
        console.log("📊 Contenido de prestamosActivos:", prestamosActivos.innerHTML);
    }
    
    if (estadoSistema) {
        console.log("📊 Contenido de estadoSistema:", estadoSistema.innerHTML);
    }
}

// Función para probar la función cargarPrestamosActivos
function testCargarPrestamosActivos() {
    console.log("🔍 Probando función cargarPrestamosActivos...");
    
    if (typeof cargarPrestamosActivos === 'function') {
        console.log("✅ Función cargarPrestamosActivos existe");
        try {
            cargarPrestamosActivos();
            console.log("✅ Función ejecutada sin errores");
        } catch (error) {
            console.error("❌ Error al ejecutar la función:", error);
        }
    } else {
        console.error("❌ Función cargarPrestamosActivos no existe");
    }
}

// Ejecutar todas las pruebas
console.log("🧪 Ejecutando todas las pruebas...");
console.log("=" * 50);

testReporteGeneral();
testPrestamosActivos();
verificarDOM();
testCargarPrestamosActivos();

console.log("=" * 50);
console.log("✅ Diagnóstico completado");
