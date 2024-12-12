console.log('script.js loaded'); // Verificación de carga

window.initializeMap = function(lat, lon, events) {
    console.log('initializeMap called with:', lat, lon, events); // Verificación de llamada

    // Crear o eliminar el mapa previo si existe
    if (window.map) {
        window.map.remove();
    }

    const mapElement = document.getElementById('map');
    if (!mapElement) {
        console.log('Elemento del mapa no encontrado');
        return;
    }

    // Inicializar el mapa
    window.map = L.map('map').setView([lat, lon], 13);

    // Usar OpenStreetMap como proveedor de mapas
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap contributors',
    }).addTo(window.map);

    // Marcador para la ubicación buscada
    L.marker([lat, lon]).addTo(window.map)
        .bindPopup('<b>Ubicación Buscada</b>')
        .openPopup();

    // Marcadores para eventos cercanos
    events.forEach(event => {
        if (event.lat && event.lon) { // Verificar que existen coordenadas
            L.marker([event.lat, event.lon]).addTo(window.map)
                .bindPopup(`<b>${event.name}</b><br/>Organizador: ${event.organizer}`);
        }
    });
};