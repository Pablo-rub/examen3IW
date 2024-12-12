import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import Home from './pages/Home';
import EventDetails from './pages/EventDetails';
import CreateEvent from './pages/CreateEvent';
import Login from './pages/Login';
import Logs from './pages/Logs';
import PrivateRoute from './components/PrivateRoute'; // Importar PrivateRoute
import { GoogleOAuthProvider } from '@react-oauth/google';

const clientId = process.env.REACT_APP_GOOGLE_CLIENT_ID;

function App() {
  return (
    <GoogleOAuthProvider clientId={clientId}>
      <Router>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/" element={<Home />} /> {/* Ruta pública */}
          <Route path="/event/:id" element={<EventDetails />} /> {/* Ruta pública */}
          <Route path="/create-event" element={<PrivateRoute><CreateEvent /></PrivateRoute>} /> {/* Ruta protegida */}
          <Route path="/logs" element={<PrivateRoute><Logs /></PrivateRoute>} /> {/* Ruta protegida */}
        </Routes>
      </Router>
    </GoogleOAuthProvider>
  );
}

export default App;
