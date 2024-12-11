from fastapi import HTTPException
from fastapi.security import OAuth2PasswordBearer
import requests

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_google_user(token: str):
    # Llamamos a la API de Google para obtener el usuario autenticado con el token
    response = requests.get(
        'https://www.googleapis.com/oauth2/v3/userinfo',
        headers={'Authorization': f'Bearer {token}'}
    )
    if response.status_code != 200:
        raise HTTPException(status_code=401, detail="Token de Google inválido o expirado")
    return response.json()  # Retorna el diccionario con los datos del usuario
