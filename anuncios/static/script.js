console.log('script.js loaded'); // Verificación de carga

window.initializeMap = function(elementId, lat, lon, events = []) {
    console.log(`initializeMap called for ${elementId} with:`, lat, lon, events); // Verificación de llamada

    // Crear o eliminar el mapa previo si existe
    if (window.maps && window.maps[elementId]) {
        window.maps[elementId].remove();
    }

    const mapElement = document.getElementById(elementId);
    if (!mapElement) {
        console.log(`Elemento del mapa con ID ${elementId} no encontrado`);
        return;
    }

    // Inicializar el mapa
    const map = L.map(elementId).setView([lat, lon], 13);

    // Usar OpenStreetMap como proveedor de mapas
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap contributors',
    }).addTo(map);

    // Marcador para la ubicación principal
    L.marker([lat, lon]).addTo(map)
        .bindPopup('<b>Ubicación</b>')
        .openPopup();

    // Marcadores para eventos cercanos (solo para el mapa de home)
    events.forEach(event => {
        if (event.lat && event.lon) { // Verificar que existen coordenadas
            L.marker([event.lat, event.lon]).addTo(map)
                .bindPopup(`<b>${event.name}</b><br/>Organizador: ${event.organizer}`);
        }
    });

    // Guardar la instancia del mapa para futuros usos
    window.maps = window.maps || {};
    window.maps[elementId] = map;
};