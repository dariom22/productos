"""Punto de entrada de la aplicación - Viajes Fantásticos."""

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI

from app.database import Base, engine, SessionLocal
from app.routes import chat, tours, reservas
from app.routes import whatsapp_webhook, pagos
from app.data.seed import seed_database

# Crear tablas
Base.metadata.create_all(bind=engine)

# Cargar datos de ejemplo
db = SessionLocal()
seed_database(db)
db.close()

app = FastAPI(
    title="Viajes Fantásticos - Agente de Tours",
    description=(
        "Agente inteligente para agencia de tours.\n\n"
        "**Flujo completo:**\n"
        "1. Cliente consulta tours → 2. Agente arma presupuesto → "
        "3. Cliente acepta → 4. Se contacta proveedor (WhatsApp) → "
        "5. Proveedor confirma → 6. Cliente confirma → "
        "7. Link de pago (Stripe) → 8. Pago OK → "
        "9. Se pide PAX al proveedor → 10. PAX enviado al cliente"
    ),
    version="2.0.0",
)

app.include_router(chat.router)
app.include_router(tours.router)
app.include_router(reservas.router)
app.include_router(whatsapp_webhook.router)
app.include_router(pagos.router)


@app.get("/")
def root():
    return {
        "nombre": "Viajes Fantásticos",
        "version": "2.0",
        "descripcion": "Agente inteligente para agencia de tours con flujo completo",
        "endpoints": {
            "chat": "POST /chat/ - Hablar con el agente",
            "tours": "GET /tours/ - Ver tours disponibles",
            "reservas": "GET /reservas/ - Ver reservas",
            "webhook_whatsapp": "POST /webhook/whatsapp - Webhook de Twilio",
            "webhook_stripe": "POST /pagos/webhook/stripe - Webhook de Stripe",
            "docs": "GET /docs - Documentación interactiva (Swagger)",
        },
    }
