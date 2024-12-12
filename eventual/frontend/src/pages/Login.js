import React from 'react';
import { GoogleLogin } from '@react-oauth/google';
import { useNavigate } from 'react-router-dom';
import jwt_decode from "jwt-decode";

const Login = () => {
  const navigate = useNavigate();

  const onSuccess = (response) => {
    // Decodificar el token si es necesario
    const decoded = jwt_decode(response.credential);
    console.log(decoded);

    // Guardar el token en localStorage
    localStorage.setItem('token', response.credential);

    // Redirigir al home
    navigate('/');
  };

  const onFailure = (error) => {
    console.error('Error en la autenticación:', error);
    alert('Error en el login');
  };

  return (
    <div>
      <h2>Inicio de Sesión</h2>
      <GoogleLogin
        onSuccess={onSuccess}
        onError={onFailure}
      />
    </div>
  );
};

export default Login;
