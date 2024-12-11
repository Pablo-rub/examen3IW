import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getEventDetails, updateEvent, deleteEvent } from '../services/api';
import Map from '../components/Map';

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
    const fetchEventDetails = async () => {
      try {
        const data = await getEventDetails(id);
        setEvent(data);
        setFormData({
          name: data.name,
          place: data.place,
          timestamp: new Date(data.timestamp).toISOString().slice(0,16),
          image: data.image || ''
        });
      } catch (err) {
        console.error('Error fetching event details:', err);
        setError('Error al obtener los detalles del evento.');
      }
    };
    fetchEventDetails();
  }, [id]);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

  const handleUpdate = async () => {
    try {
      await updateEvent(id, formData);
      setIsEditing(false);
      const updatedEvent = await getEventDetails(id);
      setEvent(updatedEvent);
    } catch (err) {
      console.error('Error actualizando evento:', err);
      setError('Error al actualizar el evento.');
    }
  };

  const handleDelete = async () => {
    try {
      await deleteEvent(id);
      navigate('/');
    } catch (err) {
      console.error('Error eliminando evento:', err);
      setError('Error al eliminar el evento.');
    }
  };

  if (!event) return <p>Cargando detalles del evento...</p>;

  return (
    <div>
      {isEditing ? (
        <div>
          <h1>Modificar Evento</h1>
          {error && <p style={{ color: 'red' }}>{error}</p>}
          <label>Nombre:</label>
          <input
            type="text"
            name="name"
            value={formData.name}
            onChange={handleInputChange}
            required
          />
          <label>Lugar:</label>
          <input
            type="text"
            name="place"
            value={formData.place}
            onChange={handleInputChange}
            required
          />
          <label>Fecha y Hora:</label>
          <input
            type="datetime-local"
            name="timestamp"
            value={formData.timestamp}
            onChange={handleInputChange}
            required
          />
          <label>Imagen:</label>
          <input
            type="text"
            name="image"
            value={formData.image}
            onChange={handleInputChange}
          />
          <button onClick={handleUpdate}>Guardar</button>
          <button onClick={() => setIsEditing(false)}>Cancelar</button>
        </div>
      ) : (
        <div>
          <h1>{event.name}</h1>
          <p>Organizador: {event.organizer}</p>
          <p>Fecha: {new Date(event.timestamp).toLocaleString()}</p>
          <p>Lugar: {event.place}</p>
          {event.image && <img src={event.image} alt={event.name} style={{ maxWidth: '300px' }} />}
          <Map lat={event.lat} lon={event.lon} />
          <button onClick={() => setIsEditing(true)}>Modificar</button>
          <button onClick={handleDelete}>Eliminar</button>
        </div>
      )}
    </div>
  );
};

export default EventDetails;
