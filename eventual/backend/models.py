from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class Event(BaseModel):
    _id: str
    name: str
    timestamp: datetime
    place: str
    lat: float
    lon: float
    organizer: str
    image: Optional[str] = None

class LoginLog(BaseModel):
    timestamp: datetime
    user_email: str
    expiration: datetime
    token: str
