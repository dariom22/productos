"""
Estados del flujo de reserva:

1. presupuesto_enviado   - El agente armó y envió el presupuesto al cliente
2. presupuesto_aceptado  - El cliente aceptó el presupuesto
3. esperando_proveedor   - Se contactó al proveedor por WhatsApp
4. proveedor_confirmo    - El proveedor confirmó (puede incluir cambios)
5. cambios_enviados      - Se enviaron los cambios del proveedor al cliente
6. cliente_confirmo      - El cliente confirmó la propuesta final
7. pago_pendiente        - Se envió el link de pago por Stripe
8. pagado                - El cliente pagó
9. pax_solicitado        - Se pidió el número de PAX al proveedor
10. pax_enviado          - Se envió el PAX al cliente (COMPLETADO)
11. cancelado            - Cancelado en cualquier punto
"""

from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from app.database import Base


ESTADOS_VALIDOS = [
    "presupuesto_enviado",
    "presupuesto_aceptado",
    "esperando_proveedor",
    "proveedor_confirmo",
    "cambios_enviados",
    "cliente_confirmo",
    "pago_pendiente",
    "pagado",
    "pax_solicitado",
    "pax_enviado",
    "cancelado",
]


class Reserva(Base):
    __tablename__ = "reservas"

    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False)
    tour_id = Column(Integer, ForeignKey("tours.id"), nullable=False)
    proveedor_id = Column(Integer, ForeignKey("proveedores.id"))
    cantidad_personas = Column(Integer, nullable=False, default=1)
    precio_unitario = Column(Float, nullable=False)
    precio_total = Column(Float, nullable=False)
    estado = Column(String(50), default="presupuesto_enviado")
    notas_proveedor = Column(Text)
    numero_pax = Column(String(100))
    stripe_payment_link = Column(String(500))
    stripe_session_id = Column(String(200))
    fecha_creacion = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    fecha_actualizacion = Column(DateTime, default=lambda: datetime.now(timezone.utc),
                                  onupdate=lambda: datetime.now(timezone.utc))

    cliente = relationship("Cliente")
    tour = relationship("Tour")
    proveedor = relationship("Proveedor")
    mensajes = relationship("MensajeFlujo", back_populates="reserva",
                            order_by="MensajeFlujo.fecha")


class MensajeFlujo(Base):
    """Log de todos los mensajes del flujo de una reserva."""
    __tablename__ = "mensajes_flujo"

    id = Column(Integer, primary_key=True, index=True)
    reserva_id = Column(Integer, ForeignKey("reservas.id"), nullable=False)
    origen = Column(String(50), nullable=False)  # "cliente", "proveedor", "agente", "sistema"
    mensaje = Column(Text, nullable=False)
    fecha = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    reserva = relationship("Reserva", back_populates="mensajes")
