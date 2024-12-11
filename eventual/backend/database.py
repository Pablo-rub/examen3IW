from motor.motor_asyncio import AsyncIOMotorClient
import os

MONGO_URI = os.getenv("MONGO_URI")

client = AsyncIOMotorClient(MONGO_URI)
db = client["examen3IW"]

# Crear índice geoespacial para las coordenadas de los eventos
async def create_geo_index():
    await db.events.create_index([("lat", "2dsphere"), ("lon", "2dsphere")])

# Ejecutar la creación del índice al iniciar
import asyncio
asyncio.run(create_geo_index())