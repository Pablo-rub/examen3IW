from motor.motor_asyncio import AsyncIOMotorClient
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

client = AsyncIOMotorClient(MONGO_URI)
db = client["examen3IW"]

# Crear índice geoespacial para las coordenadas de los eventos
async def create_geo_index():
    await db.events.create_index([("location", "2dsphere")])

# Ejecutar la creación del índice al iniciar
async def main():
    await create_geo_index()

# Check if there's an existing event loop
try:
    loop = asyncio.get_running_loop()
except RuntimeError:
    loop = None

if loop and loop.is_running():
    # If there's a running event loop, create a task
    asyncio.create_task(main())
else:
    # Otherwise, run the event loop
    asyncio.run(main())