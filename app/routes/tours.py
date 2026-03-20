"""Endpoints REST para tours y proveedores."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import date

from app.database import get_db
from app.models.tours import Tour, Proveedor

router = APIRouter(prefix="/tours", tags=["Tours"])


class TourResponse(BaseModel):
    id: int
    nombre: str
    destino: str
    descripcion: str | None
    duracion_dias: int
    precio_base: float
    cupos_disponibles: int
    fecha_salida: date | None
    incluye: str | None
    categoria: str | None
    proveedor_id: int | None

    model_config = {"from_attributes": True}


@router.get("/", response_model=list[TourResponse])
def listar_tours(db: Session = Depends(get_db)):
    """Lista todos los tours disponibles."""
    return db.query(Tour).filter(Tour.cupos_disponibles > 0).all()


@router.get("/{tour_id}", response_model=TourResponse)
def obtener_tour(tour_id: int, db: Session = Depends(get_db)):
    """Obtiene un tour por su ID."""
    tour = db.query(Tour).filter(Tour.id == tour_id).first()
    if not tour:
        raise HTTPException(status_code=404, detail="Tour no encontrado")
    return tour
