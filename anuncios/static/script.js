function initializeMap(lat, lon, events) {
    // Verificar si el mapa ya está inicializado y destruirlo
    if (typeof map !== 'undefined') {
        map.remove();
    }

    const mapElement = document.getElementById('map');
    if (!mapElement) return;

    const map = L.map('map').setView([lat, lon], 13);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap contributors',
    }).addTo(map);

    // Marcador para la ubicación buscada
    L.marker([lat, lon]).addTo(map)
        .bindPopup('<b>Ubicación Buscada</b>')
        .openPopup();

    // Marcadores para eventos cercanos
    events.forEach(event => {
        L.marker([event.lat, event.lon]).addTo(map)
            .bindPopup(`<b>${event.name}</b><br/>Organizador: ${event.organizer}`);
    });
}