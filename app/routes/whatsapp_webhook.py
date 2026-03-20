"""Webhook para recibir mensajes de WhatsApp vía Twilio."""

from fastapi import APIRouter, Depends, Form
from sqlalchemy.orm import Session

from app.database import get_db
from app.agent.tour_agent import run_agent
from app.services.whatsapp import enviar_whatsapp

router = APIRouter(prefix="/webhook", tags=["Webhooks"])

# Conversaciones de WhatsApp (por número de teléfono)
wa_conversations: dict[str, list] = {}


@router.post("/whatsapp")
def whatsapp_incoming(
    Body: str = Form(""),
    From: str = Form(""),
    To: str = Form(""),
    db: Session = Depends(get_db),
):
    """Recibe mensajes de WhatsApp vía Twilio webhook.

    Twilio envía los mensajes como form-data con campos Body, From, To, etc.
    """
    numero = From.replace("whatsapp:", "")
    mensaje = Body.strip()

    if not mensaje:
        return {"status": "empty"}

    # Usar el número como session_id
    history = wa_conversations.get(numero, [])
    result = run_agent(mensaje, db, history)
    wa_conversations[numero] = result["conversation_history"]

    # Responder por WhatsApp
    enviar_whatsapp(From, result["response"])

    return {"status": "ok", "to": From}
