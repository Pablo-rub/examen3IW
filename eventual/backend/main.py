from fastapi import FastAPI
from routes import events, logs  # Importar logs
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include your routes
app.include_router(events.router, prefix="/api/events", tags=["Eventos"])
app.include_router(logs.router, prefix="/api", tags=["Logs"])  # Incluir logs

# Start the server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)