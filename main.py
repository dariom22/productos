"""Punto de entrada de la aplicación."""

from fastapi import FastAPI

from app.database import Base, engine, SessionLocal
from app.routes import chat, tours, reservas
from app.data.seed import seed_database

# Crear tablas
Base.metadata.create_all(bind=engine)

# Cargar datos de ejemplo
db = SessionLocal()
seed_database(db)
db.close()

app = FastAPI(
    title="Viajes Fantásticos - Agente de Tours",
    description="API con agente inteligente para una agencia de tours. "
                "Permite buscar tours, hacer reservas y consultar información mediante chat.",
    version="1.0.0",
)

app.include_router(chat.router)
app.include_router(tours.router)
app.include_router(reservas.router)


@app.get("/")
def root():
    return {
        "nombre": "Viajes Fantásticos",
        "descripcion": "Agente inteligente para agencia de tours",
        "endpoints": {
            "chat": "POST /chat/ - Hablar con el agente",
            "tours": "GET /tours/ - Ver tours disponibles",
            "reservas": "GET /reservas/ - Ver reservas",
            "docs": "GET /docs - Documentación interactiva (Swagger)",
        },
    }
