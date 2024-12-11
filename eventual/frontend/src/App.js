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
          <Route path="/" element={<Home />} />
          <Route path="/event/:id" element={<EventDetails />} />
          <Route path="/login" element={<Login />} />
          <Route path="/logs" element={<Logs />} />
          <Route 
            path="/create-event" 
            element={
              <PrivateRoute>
                <CreateEvent />
              </PrivateRoute>
            } 
          />
          {/* Añadir rutas protegidas similares para modificar y eliminar eventos */}
        </Routes>
      </Router>
    </GoogleOAuthProvider>
  );
}

export default App;
