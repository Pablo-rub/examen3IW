import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { getEvents } from '../services/api';
import Map from '../components/Map';

const Home = () => {
  const [events, setEvents] = useState([]);
  const [address, setAddress] = useState('');
  const [error, setError] = useState('');
  const [coordinates, setCoordinates] = useState({ lat: 0, lon: 0 });
  const navigate = useNavigate();

  // Función para obtener latitud y longitud desde una dirección postal usando Nominatim
  const geocodeAddress = async (address) => {
    const url = `https://nominatim.openstreetmap.org/search?q=${encodeURIComponent(
      address
    )}&format=json&addressdetails=1`;
    
    try {
      const response = await fetch(url);
      if (!response.ok) {
        throw new Error('Error en la geocodificación');
      }
      const data = await response.json();
      if (data.length > 0) {
        return {
          lat: parseFloat(data[0].lat),
          lon: parseFloat(data[0].lon)
        };
      } else {
        throw new Error('No se encontraron coordenadas para la dirección proporcionada');
      }
    } catch (error) {
      console.error('Error geocodificando dirección:', error);
      throw error;
    }
  };

  const handleSearch = async () => {
    setError('');
    try {
      const { lat, lon } = await geocodeAddress(address);
      console.log('Coordenadas encontradas:', lat, lon);
      setCoordinates({ lat, lon });
      const data = await getEvents(lat, lon);
      setEvents(data);
    } catch (error) {
      console.error('Error buscando eventos:', error);
      setError('No se pudo encontrar eventos cercanos. Verifica la dirección e inténtalo de nuevo.');
    }
  };

  const isAuthenticated = !!localStorage.getItem('token');

  return (
    <div>
      <h1>Eventual</h1>
      <div>
        <input
          type="text"
          value={address}
          onChange={(e) => setAddress(e.target.value)}
          placeholder="Introduce una dirección"
        />
        <button onClick={handleSearch}>Buscar</button>
      </div>

      {error && <p style={{ color: 'red' }}>{error}</p>}

      {coordinates.lat !== 0 && coordinates.lon !== 0 && (
        <Map lat={coordinates.lat} lon={coordinates.lon} events={events} />
      )}

      {events.length > 0 && (
        <div>
          <h3>Eventos Cerca de Ti:</h3>
          <ul>
            {events.map((event) => (
              <li key={event._id}>
                <a href={`/event/${event._id}`}>{event.name}</a>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Mostrar el botón "Crear Evento" si el usuario está autenticado */}
      {isAuthenticated && (
        <button onClick={() => navigate('/create-event')}>
          Crear Evento
        </button>
      )}
    </div>
  );
};

export default Home;
