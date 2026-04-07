"""Endpoints y webhooks de pagos (Stripe)."""

import os
import stripe
from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.reservas import Reserva, MensajeFlujo
from app.models.tours import Proveedor
from app.services.whatsapp import pedir_pax_proveedor, notificar_cliente

router = APIRouter(prefix="/pagos", tags=["Pagos"])


@router.get("/exito")
def pago_exitoso(reserva_id: int, db: Session = Depends(get_db)):
    """Página de éxito después del pago en Stripe."""
    reserva = db.query(Reserva).filter(Reserva.id == reserva_id).first()
    if not reserva:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")

    if reserva.estado == "pago_pendiente":
        reserva.estado = "pax_solicitado"
        db.add(MensajeFlujo(reserva_id=reserva.id, origen="sistema",
                             mensaje="Pago completado via Stripe"))

        # Pedir PAX al proveedor
        proveedor = db.query(Proveedor).filter(
            Proveedor.id == reserva.proveedor_id
        ).first()
        if proveedor:
            info = (
                f"Reserva #{reserva.id} - {reserva.tour.nombre}\n"
                f"Cliente: {reserva.cliente.nombre}\n"
                f"Personas: {reserva.cantidad_personas}"
            )
            pedir_pax_proveedor(proveedor.whatsapp, info)

        if reserva.cliente.whatsapp:
            notificar_cliente(
                reserva.cliente.whatsapp,
                f"✅ Pago recibido! Reserva #{reserva.id}. "
                f"Estamos gestionando tu PAX con el proveedor."
            )

        db.commit()

    return {
        "mensaje": "¡Pago exitoso!",
        "reserva_id": reserva.id,
        "tour": reserva.tour.nombre,
        "estado": reserva.estado,
    }


@router.get("/cancelado")
def pago_cancelado(reserva_id: int):
    """Página cuando el cliente cancela el pago."""
    return {
        "mensaje": "Pago cancelado. Podés volver a intentarlo desde el chat.",
        "reserva_id": reserva_id,
    }


@router.post("/webhook/stripe")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    """Webhook de Stripe para confirmar pagos automáticamente."""
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    webhook_secret = os.environ.get("STRIPE_WEBHOOK_SECRET")

    if webhook_secret and sig_header:
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, webhook_secret
            )
        except (ValueError, stripe.error.SignatureVerificationError):
            raise HTTPException(status_code=400, detail="Webhook inválido")
    else:
        import json
        event = json.loads(payload)

    if event.get("type") == "checkout.session.completed":
        session = event["data"]["object"]
        reserva_id = session.get("metadata", {}).get("reserva_id")
        if reserva_id:
            reserva = db.query(Reserva).filter(
                Reserva.id == int(reserva_id)
            ).first()
            if reserva and reserva.estado == "pago_pendiente":
                reserva.estado = "pax_solicitado"
                db.add(MensajeFlujo(
                    reserva_id=reserva.id, origen="sistema",
                    mensaje=f"Pago confirmado via webhook. Session: {session.get('id')}"
                ))
                db.commit()

    return {"received": True}
