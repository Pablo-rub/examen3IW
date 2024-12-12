from fastapi import HTTPException
from google.oauth2 import id_token
from google.auth.transport import requests
import os
from dotenv import load_dotenv  # Importar load_dotenv

load_dotenv()  # Cargar variables de entorno

clientId = os.getenv("GOOGLE_CLIENT_ID")

def get_google_user(token: str):
    try:
        CLIENT_ID = clientId
        if not CLIENT_ID:
            raise ValueError("CLIENT_ID no está definido")
        idinfo = id_token.verify_oauth2_token(token, requests.Request(), CLIENT_ID)
        return idinfo
    except ValueError as e:
        raise HTTPException(status_code=401, detail=f"Token de Google inválido o expirado: {str(e)}")