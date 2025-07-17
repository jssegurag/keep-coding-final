from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes.queries import router as queries_router

app = FastAPI(
    title="API REST RAG Expedientes Jurídicos",
    version="1.0.0",
    description="API REST para servir el sistema RAG a múltiples frontends (Streamlit, Gradio, etc.)."
)

# Configuración básica de CORS (permitir todos los orígenes para desarrollo)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar el router de consultas
app.include_router(queries_router)

@app.get("/api/v1/system/health", tags=["Sistema"])
def health_check():
    """Endpoint de salud para verificar que la API está corriendo."""
    return {"status": "ok", "message": "API REST RAG en funcionamiento"}
