import React, { useState } from 'react';
import { createEvent } from '../services/api';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

const CreateEvent = () => {
  const [name, setName] = useState('');
  const [timestamp, setTimestamp] = useState('');
  const [place, setPlace] = useState('');
  const [lat, setLat] = useState('');
  const [lon, setLon] = useState('');
  const [organizer, setOrganizer] = useState('');
  const [image, setImage] = useState(null);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();

    let imageUrl = '';
    if (image) {
      const formData = new FormData();
      formData.append('file', image);
      formData.append('upload_preset', process.env.REACT_APP_CLOUDINARY_UPLOAD_PRESET);

      try {
        const res = await axios.post(
          `https://api.cloudinary.com/v1_1/${process.env.REACT_APP_CLOUDINARY_CLOUD_NAME}/image/upload`,
          formData
        );
        imageUrl = res.data.secure_url; // Esta es la URL que debes guardar
        console.log('URL de la imagen:', imageUrl); // Para verificar que se obtiene la URL
      } catch (err) {
        console.error('Error al subir la imagen:', err);
        setError('Error al subir la imagen.');
        return;
      }
    }

    const event = {
      name,
      timestamp,
      place,
      lat: parseFloat(lat),
      lon: parseFloat(lon),
      organizer,
      image: imageUrl, // Incluir la URL de la imagen en el evento
    };

    try {
      await createEvent(event);
      navigate('/');
    } catch (err) {
      console.error('Error creando evento:', err);
      setError('Error creando el evento.');
      if (err.message.includes('No estás autenticado')) {
        navigate('/login');
      }
    }
  };

  return (
    <div>
      <h1>Crear Evento</h1>
      {error && <p style={{ color: 'red' }}>{error}</p>}
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          placeholder="Nombre del Evento"
          value={name}
          onChange={(e) => setName(e.target.value)}
          required
        />
        <input
          type="datetime-local"
          value={timestamp}
          onChange={(e) => setTimestamp(e.target.value)}
          required
        />
        <input
          type="text"
          placeholder="Lugar"
          value={place}
          onChange={(e) => setPlace(e.target.value)}
          required
        />
        <input
          type="number"
          value={lat}
          onChange={(e) => setLat(e.target.value)}
          placeholder="Latitud"
          required
        />
        <input
          type="number"
          value={lon}
          onChange={(e) => setLon(e.target.value)}
          placeholder="Longitud"
          required
        />
        <input
          type="email"
          value={organizer}
          onChange={(e) => setOrganizer(e.target.value)}
          placeholder="Email del organizador"
          required
        />
        <input
          type="file"
          accept="image/*"
          onChange={(e) => setImage(e.target.files[0])}
        />
        <button type="submit">Crear Evento</button>
      </form>
    </div>
  );
};

export default CreateEvent;
