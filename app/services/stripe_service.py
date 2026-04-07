"""Servicio de pagos con Stripe."""

import os
import stripe


def configurar_stripe():
    stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")


def crear_link_pago(reserva_id: int, descripcion: str, monto_usd: float,
                     email_cliente: str = None) -> dict:
    """Crea una sesión de pago de Stripe y retorna el link.

    Args:
        reserva_id: ID de la reserva (para metadata)
        descripcion: Descripción del tour
        monto_usd: Monto total en USD
        email_cliente: Email del cliente (opcional)
    """
    configurar_stripe()

    if not stripe.api_key:
        # Modo simulación
        link = f"https://checkout.stripe.com/pay/simulado_{reserva_id}"
        print(f"[Stripe SIMULADO] Reserva {reserva_id} | USD {monto_usd} | Link: {link}")
        return {"url": link, "session_id": f"sim_{reserva_id}", "simulado": True}

    base_url = os.environ.get("BASE_URL", "http://localhost:8000")

    session_params = {
        "payment_method_types": ["card"],
        "line_items": [{
            "price_data": {
                "currency": "usd",
                "product_data": {"name": descripcion},
                "unit_amount": int(monto_usd * 100),
            },
            "quantity": 1,
        }],
        "mode": "payment",
        "success_url": f"{base_url}/pagos/exito?reserva_id={reserva_id}",
        "cancel_url": f"{base_url}/pagos/cancelado?reserva_id={reserva_id}",
        "metadata": {"reserva_id": str(reserva_id)},
    }

    if email_cliente:
        session_params["customer_email"] = email_cliente

    session = stripe.checkout.Session.create(**session_params)

    return {"url": session.url, "session_id": session.id, "simulado": False}
