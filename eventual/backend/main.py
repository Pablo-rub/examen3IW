from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import events, logs

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    # Permitir solicitudes desde localhost:3000 y Vercel
    allow_origins=["http://localhost:3000",
                    "https://examen3-iw-frontend-ey2m6py1w-pablos-projects-7bf36973.vercel.app"],
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

@app.get("/")
def read_root():
    return {"message": "API is running!"}