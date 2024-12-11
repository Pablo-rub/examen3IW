import axios from 'axios';

const API_URL = 'http://localhost:8000/api/events';

export const getEvents = async (lat, lon) => {
  try {
    const response = await fetch(`http://localhost:8000/api/events?lat=${lat}&lon=${lon}`);
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

// Función para crear un evento
export const createEvent = async (event) => {
  try {
    const response = await axios.post(API_URL, event);
    return response.data;
  } catch (error) {
    console.error('Error creando evento:', error);
    throw error;
  }
};

// Función para actualizar un evento
export const updateEvent = async (id, event) => {
  try {
    const response = await axios.put(`${API_URL}/${id}`, event);
    return response.data;
  } catch (error) {
    console.error('Error actualizando evento:', error);
    throw error;
  }
};

// Función para eliminar un evento
export const deleteEvent = async (id) => {
  try {
    const response = await axios.delete(`${API_URL}/${id}`);
    return response.data;
  } catch (error) {
    console.error('Error eliminando evento:', error);
    throw error;
  }
};