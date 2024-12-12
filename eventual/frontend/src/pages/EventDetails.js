import React, { useState, useEffect } from 'react';
import { getEventDetails, updateEvent, deleteEvent } from '../services/api';
import { useParams, useNavigate } from 'react-router-dom';
import Map from '../components/Map';
import jwt_decode from 'jwt-decode';

const EventDetails = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [event, setEvent] = useState(null);
  const [isEditing, setIsEditing] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    place: '',
    timestamp: '',
    image: ''
  });
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchEvent = async () => {
      try {
        const data = await getEventDetails(id);
        setEvent(data);
        setFormData({
          name: data.name,
          place: data.place,
          timestamp: data.timestamp,
          image: data.image || ''
        });
      } catch (err) {
        console.error('Error fetching event details:', err);
        setError('Error al obtener los detalles del evento.');
      }
    };
    fetchEvent();
  }, [id]);

  const handleInputChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleUpdate = async () => {
    const token = localStorage.getItem('token');
    if (!token) {
      navigate('/login'); // Redirigir al login si no está autenticado
      return;
    }

    try {
      await updateEvent(id, formData);
      setIsEditing(false);
      const updatedEvent = await getEventDetails(id);
      setEvent(updatedEvent);
    } catch (err) {
      console.error('Error updating event:', err);
      setError('Error actualizando el evento.');
      if (err.response && err.response.status === 401) {
        navigate('/login');
      }
    }
  };

  const handleDelete = async () => {
    const confirmDelete = window.confirm('¿Estás seguro de que deseas eliminar este evento?');
    if (!confirmDelete) return;

    const token = localStorage.getItem('token');
    if (!token) {
      navigate('/login'); // Redirigir al login si no está autenticado
      return;
    }

    try {
      await deleteEvent(id);
      navigate('/');
    } catch (err) {
      console.error('Error deleting event:', err);
      setError('Error eliminando el evento.');
      if (err.response && err.response.status === 401) {
        navigate('/login');
      }
    }
  };

  const handleBack = () => {
    navigate('/');
  };

  if (!event) {
    return <div>Cargando...</div>;
  }

  const isAuthenticated = !!localStorage.getItem('token');
  const userEmail = isAuthenticated ? jwt_decode(localStorage.getItem('token')).email : null;
  const isOrganizer = isAuthenticated && userEmail === event.organizer;

  return (
    <div>
      <h1>{event.name}</h1>
      {error && <p style={{ color: 'red' }}>{error}</p>}
      {isEditing ? (
        <div>
          <input
            type="text"
            name="name"
            value={formData.name}
            onChange={handleInputChange}
          />
          <input
            type="datetime-local"
            name="timestamp"
            value={formData.timestamp}
            onChange={handleInputChange}
          />
          <input
            type="text"
            name="place"
            value={formData.place}
            onChange={handleInputChange}
          />
          {/* Puedes agregar otros campos editables aquí */}
          <button onClick={handleUpdate}>Guardar</button>
          <button onClick={() => setIsEditing(false)}>Cancelar</button>
        </div>
      ) : (
        <div>
          <p>Lugar: {event.place}</p>
          <p>Fecha y Hora: {new Date(event.timestamp).toLocaleString()}</p>
          {/* Mostrar otros detalles del evento */}
          {event.image && (
            <img src={event.image} alt={event.name} style={{ maxWidth: '300px' }} />
          )}
          <Map lat={event.lat} lon={event.lon} events={[event]} />
          {isOrganizer && (
            <>
              <button onClick={() => setIsEditing(true)}>Modificar</button>
              <button onClick={handleDelete}>Eliminar</button>
            </>
          )}
          <button onClick={handleBack}>Volver</button> {/* Botón para volver a la página principal */}
        </div>
      )}
    </div>
  );
};

export default EventDetails;
