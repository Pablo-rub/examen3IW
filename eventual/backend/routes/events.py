from fastapi import APIRouter, HTTPException, Depends
from models import Event
from database import db
from bson import ObjectId
from typing import List
from token_verification import get_google_user
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime
from math import radians, cos, sin, sqrt, atan2

security = HTTPBearer()

router = APIRouter()

def event_serializer(event) -> dict:
    event["_id"] = str(event["_id"])
    return event

def calculate_distance(lat1, lon1, lat2, lon2):
    # Convertir de grados a radianes
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    # Fórmula de Haversine
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    # Radio de la Tierra en kilómetros
    r = 6371
    return r * c

@router.get("/", response_model=List[Event])
async def get_events(lat: float, lon: float):
    events_cursor = db.events.find()
    events = []
    async for event in events_cursor:
        event_distance = calculate_distance(lat, lon, event['lat'], event['lon'])
        if event_distance <= 10:  # Filtrar eventos dentro de 10 km
            events.append(event)
    return events

@router.get("/{event_id}", response_model=Event)
async def get_event(event_id: str):
    event = await db.events.find_one({"_id": ObjectId(event_id)})
    if event:
        return event_serializer(event)
    raise HTTPException(status_code=404, detail="Evento no encontrado")

@router.post("/", response_model=Event)
async def create_event(event: Event, credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    user_info = get_google_user(token)
    event_data = event.dict()
    event_data["organizer"] = user_info["email"]
    result = await db.events.insert_one(event_data)
    return event_serializer(event_data)

@router.put("/{event_id}", response_model=Event)
async def update_event(event_id: str, event: Event, credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    user_info = get_google_user(token)
    organizer_email = user_info["email"]

    existing_event = await db.events.find_one({"_id": ObjectId(event_id)})
    if not existing_event:
        raise HTTPException(status_code=404, detail="Evento no encontrado")

    if existing_event["organizer"] != organizer_email:
        raise HTTPException(status_code=403, detail="No tienes permiso para modificar este evento")

    update_data = event.dict(exclude_unset=True)
    update_data["timestamp"] = datetime.fromisoformat(update_data["timestamp"])
    await db.events.update_one({"_id": ObjectId(event_id)}, {"$set": update_data})

    updated_event = await db.events.find_one({"_id": ObjectId(event_id)})
    return event_serializer(updated_event)

@router.delete("/{event_id}")
async def delete_event(event_id: str, credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    user_info = get_google_user(token)
    organizer_email = user_info["email"]

    existing_event = await db.events.find_one({"_id": ObjectId(event_id)})
    if not existing_event:
        raise HTTPException(status_code=404, detail="Evento no encontrado")

    if existing_event["organizer"] != organizer_email:
        raise HTTPException(status_code=403, detail="No tienes permiso para eliminar este evento")

    await db.events.delete_one({"_id": ObjectId(event_id)})
    return {"message": "Evento eliminado exitosamente"}
