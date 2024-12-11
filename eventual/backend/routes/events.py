from fastapi import APIRouter, HTTPException, Depends
from models import Event
from database import db
from bson import ObjectId
from typing import List
from token_verification import get_google_user
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

router = APIRouter()

rango = 100  # Distancia máxima para considerar eventos próximos

def event_serializer(event) -> dict:
    event["_id"] = str(event["_id"])
    return event

@router.get("/", response_model=List[Event])
async def get_events(lat: float, lon: float):
    events = await db.events.find({
        "lat": {"$gte": lat - rango, "$lte": lat + rango},
        "lon": {"$gte": lon - rango, "$lte": lon + rango}
    }).sort("timestamp").to_list(100)

    toReturn = [event_serializer(event) for event in events]
    return toReturn

@router.get("/{event_id}", response_model=Event)
async def get_event(event_id: str):
    event = await db.events.find_one({"_id": ObjectId(event_id)})
    if event:
        return event_serializer(event)
    raise HTTPException(status_code=404, detail="Evento no encontrado")

@router.post("/", response_model=Event)
async def create_event(event: Event, token: str = Depends(oauth2_scheme)):
    # Obtener los datos del usuario autenticado usando el token de Google
    user_info = get_google_user(token)
    organizer_email = user_info["email"]  # Obtener el email del organizador

    # Asignar el organizador al evento
    event_dict = event.dict()
    event_dict["organizer"] = organizer_email
    event_dict["timestamp"] = datetime.fromisoformat(event_dict["timestamp"])

    # Insertar el evento en la base de datos
    result = await db.events.insert_one(event_dict)
    event_dict["_id"] = str(result.inserted_id)
    return event_dict

@router.put("/{event_id}", response_model=Event)
async def update_event(event_id: str, event: Event, token: str = Depends(oauth2_scheme)):
    # Obtener los datos del usuario autenticado usando el token de Google
    user_info = get_google_user(token)
    organizer_email = user_info["email"]

    # Buscar el evento existente
    existing_event = await db.events.find_one({"_id": ObjectId(event_id)})
    if not existing_event:
        raise HTTPException(status_code=404, detail="Evento no encontrado")

    # Verificar que el usuario sea el organizador
    if existing_event["organizer"] != organizer_email:
        raise HTTPException(status_code=403, detail="No tienes permiso para modificar este evento")

    # Actualizar el evento
    update_data = event.dict(exclude_unset=True)
    update_data["timestamp"] = datetime.fromisoformat(update_data["timestamp"])
    await db.events.update_one({"_id": ObjectId(event_id)}, {"$set": update_data})

    # Retornar el evento actualizado
    updated_event = await db.events.find_one({"_id": ObjectId(event_id)})
    return event_serializer(updated_event)

@router.delete("/{event_id}")
async def delete_event(event_id: str, token: str = Depends(oauth2_scheme)):
    # Obtener los datos del usuario autenticado usando el token de Google
    user_info = get_google_user(token)
    organizer_email = user_info["email"]

    # Buscar el evento existente
    existing_event = await db.events.find_one({"_id": ObjectId(event_id)})
    if not existing_event:
        raise HTTPException(status_code=404, detail="Evento no encontrado")

    # Verificar que el usuario sea el organizador
    if existing_event["organizer"] != organizer_email:
        raise HTTPException(status_code=403, detail="No tienes permiso para eliminar este evento")

    # Eliminar el evento
    await db.events.delete_one({"_id": ObjectId(event_id)})
    return {"message": "Evento eliminado exitosamente"}
