from sqlalchemy import Column, Integer, String, Float, Text, Date
from app.database import Base


class Tour(Base):
    __tablename__ = "tours"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(200), nullable=False)
    destino = Column(String(200), nullable=False)
    descripcion = Column(Text)
    duracion_dias = Column(Integer, nullable=False)
    precio = Column(Float, nullable=False)
    cupos_disponibles = Column(Integer, nullable=False, default=0)
    fecha_salida = Column(Date)
    incluye = Column(Text)
    categoria = Column(String(100))
