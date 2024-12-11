import React, { useState, useEffect } from 'react';
import axios from 'axios';

const Logs = () => {
  const [logs, setLogs] = useState([]);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchLogs = async () => {
      try {
        const token = localStorage.getItem('token');
        const response = await axios.get(`${process.env.REACT_APP_BACKEND_URL}/logs`, {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        });
        setLogs(response.data);
      } catch (err) {
        console.error('Error fetching logs:', err);
        setError('No se pudo obtener los registros.');
      }
    };

    fetchLogs();
  }, []);

  return (
    <div>
      <h2>Registros de Inicio de Sesión</h2>
      {error && <p style={{ color: 'red' }}>{error}</p>}
      {logs.length > 0 ? (
        <table>
          <thead>
            <tr>
              <th>Timestamp</th>
              <th>Email</th>
              <th>Caducidad</th>
              <th>Token</th>
            </tr>
          </thead>
          <tbody>
            {logs.map((log) => (
              <tr key={log.token}> {/* Usar el token como key ya que es único */}
                <td>{new Date(log.timestamp).toLocaleString()}</td>
                <td>{log.user_email}</td>
                <td>{new Date(log.expiration).toLocaleString()}</td>
                <td>{log.token}</td>
              </tr>
            ))}
          </tbody>
        </table>
      ) : (
        <p>No hay registros disponibles.</p>
      )}
    </div>
  );
};

export default Logs;