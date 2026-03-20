"""Endpoints REST para gestión de reservas."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import get_db
from app.models.reservas import Reserva

router = APIRouter(prefix="/reservas", tags=["Reservas"])


class ReservaResponse(BaseModel):
    id: int
    cliente_id: int
    tour_id: int
    cantidad_personas: int
    precio_total: float
    estado: str
    fecha_reserva: datetime

    model_config = {"from_attributes": True}


@router.get("/", response_model=list[ReservaResponse])
def listar_reservas(db: Session = Depends(get_db)):
    """Lista todas las reservas."""
    return db.query(Reserva).all()


@router.get("/{reserva_id}", response_model=ReservaResponse)
def obtener_reserva(reserva_id: int, db: Session = Depends(get_db)):
    """Obtiene una reserva por su ID."""
    reserva = db.query(Reserva).filter(Reserva.id == reserva_id).first()
    if not reserva:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")
    return reserva
