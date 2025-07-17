from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes import queries, system, metadata

app = FastAPI(
    title="RAG Legal API",
    description="API REST para sistema RAG de documentos legales",
    version="1.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Incluir routers
app.include_router(system.router)
app.include_router(queries.router)
app.include_router(metadata.router)

@app.get("/")
async def root():
    return {"message": "RAG Legal API - Sistema de Recuperación Augmentada por Generación"}
