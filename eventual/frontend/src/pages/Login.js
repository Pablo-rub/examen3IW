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

    // Enviar el token al backend para autenticar
    fetch(`${process.env.REACT_APP_BACKEND_URL}/login/authorized`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        token: response.credential, // El token de Google
      }),
    })
      .then((res) => res.json())
      .then((data) => {
        if (data.success) {
          // Guardar el token en localStorage
          localStorage.setItem('token', response.credential);
          navigate('/');  // Redirigir al home
        } else {
          alert(data.message || 'Error en el login');
        }
      })
      .catch((error) => {
        console.error('Error durante la autenticación:', error);
        alert('Error en el login');
      });
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
