import React, { useEffect } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

const Map = ({ lat, lon, events }) => {
  useEffect(() => {
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

    // Limpiar el mapa al desmontar
    return () => {
      map.remove();
    };
  }, [lat, lon, events]);

  return (
    <div id="map" style={{ height: '400px', width: '100%', marginTop: '20px' }}></div>
  );
};

export default Map;
