import axios from 'axios';

const API_URL = process.env.REACT_APP_BACKEND_URL + '/api/events';

const getAuthToken = () => {
  return localStorage.getItem('token');
};

export const getEvents = async (lat, lon) => {
  try {
    const response = await fetch(`${API_URL}?lat=${lat}&lon=${lon}`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();
    console.log("data", data);
    return data;
  } catch (error) {
    console.error('Error fetching events:', error);
    throw error;
  }
};

export const getEventDetails = async (id) => {
  try {
    const response = await fetch(`${API_URL}/${id}`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching event details:', error);
    throw error;
  }
};

export const createEvent = async (event) => {
  const token = getAuthToken();
  if (!token) {
    throw new Error('No estás autenticado. Por favor, inicia sesión.');
  }

  try {
    const response = await axios.post(API_URL, event, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
    return response.data;
  } catch (error) {
    console.error('Error creando evento:', error);
    throw error;
  }
};

export const updateEvent = async (id, event) => {
  const token = getAuthToken();
  if (!token) {
    throw new Error('No estás autenticado. Por favor, inicia sesión.');
  }

  try {
    const response = await axios.put(`${API_URL}/${id}`, event, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
    return response.data;
  } catch (error) {
    console.error('Error actualizando evento:', error);
    throw error;
  }
};

export const deleteEvent = async (id) => {
  const token = getAuthToken();
  if (!token) {
    throw new Error('No estás autenticado. Por favor, inicia sesión.');
  }

  try {
    const response = await axios.delete(`${API_URL}/${id}`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
    return response.data;
  } catch (error) {
    console.error('Error eliminando evento:', error);
    throw error;
  }
};