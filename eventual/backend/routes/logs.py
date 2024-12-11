from fastapi import APIRouter, Depends, HTTPException
from typing import List
from models import LoginLog
from database import db
from token_verification import get_google_user
from fastapi.security import OAuth2PasswordBearer

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@router.get("/logs", response_model=List[LoginLog])
async def get_logs(token: str = Depends(oauth2_scheme)):
    # Obtener el usuario actual
    user_info = get_google_user(token)
    user_email = user_info.get("email")

    # Verificar si el usuario es administrador
    admin_emails = ["admin@tudominio.com"]  # Reemplaza con los emails reales de admin
    if user_email not in admin_emails:
        raise HTTPException(status_code=403, detail="No tienes permiso para acceder a los logs.")

    # Obtener los logs ordenados descendentemente por timestamp
    logs_cursor = db.login_logs.find().sort("timestamp", -1).limit(100)
    logs = []
    async for log in logs_cursor:
        logs.append({
            "timestamp": log.get("timestamp"),
            "user_email": log.get("user_email"),
            "expiration": log.get("expiration"),
            "token": log.get("token")
        })
    return logs