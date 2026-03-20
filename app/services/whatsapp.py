"""Servicio de WhatsApp usando Twilio."""

import os
from twilio.rest import Client


def get_twilio_client():
    account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
    auth_token = os.environ.get("TWILIO_AUTH_TOKEN")
    if not account_sid or not auth_token:
        return None
    return Client(account_sid, auth_token)


def enviar_whatsapp(destino: str, mensaje: str) -> dict:
    """Envía un mensaje de WhatsApp vía Twilio.

    Args:
        destino: Número con formato 'whatsapp:+5491112345678'
        mensaje: Texto del mensaje
    """
    client = get_twilio_client()
    from_number = os.environ.get("TWILIO_WHATSAPP_FROM", "whatsapp:+14155238886")

    if not client:
        # Modo simulación si no hay credenciales
        print(f"[WhatsApp SIMULADO] Para: {destino} | Mensaje: {mensaje}")
        return {"status": "simulado", "to": destino, "body": mensaje}

    if not destino.startswith("whatsapp:"):
        destino = f"whatsapp:{destino}"

    message = client.messages.create(
        body=mensaje,
        from_=from_number,
        to=destino
    )
    return {"status": message.status, "sid": message.sid, "to": destino}


def notificar_proveedor(whatsapp_proveedor: str, reserva_info: str) -> dict:
    """Notifica al proveedor sobre una nueva solicitud."""
    mensaje = (
        f"🏖️ *Nueva solicitud de tour*\n\n"
        f"{reserva_info}\n\n"
        f"Por favor respondé CONFIRMO para confirmar o enviá los cambios que necesites."
    )
    return enviar_whatsapp(whatsapp_proveedor, mensaje)


def pedir_pax_proveedor(whatsapp_proveedor: str, reserva_info: str) -> dict:
    """Pide el número de PAX al proveedor después del pago."""
    mensaje = (
        f"✅ *Pago confirmado*\n\n"
        f"{reserva_info}\n\n"
        f"Por favor enviá el número de PAX para este tour."
    )
    return enviar_whatsapp(whatsapp_proveedor, mensaje)


def notificar_cliente(whatsapp_cliente: str, mensaje: str) -> dict:
    """Envía un mensaje al cliente por WhatsApp."""
    return enviar_whatsapp(whatsapp_cliente, mensaje)
