from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from app.database import Base


class Reserva(Base):
    __tablename__ = "reservas"

    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False)
    tour_id = Column(Integer, ForeignKey("tours.id"), nullable=False)
    cantidad_personas = Column(Integer, nullable=False, default=1)
    precio_total = Column(Float, nullable=False)
    estado = Column(String(50), default="confirmada")
    fecha_reserva = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    cliente = relationship("Cliente")
    tour = relationship("Tour")
