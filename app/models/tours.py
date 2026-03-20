from sqlalchemy import Column, Integer, String, Float, Text, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Proveedor(Base):
    __tablename__ = "proveedores"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(200), nullable=False)
    whatsapp = Column(String(50), nullable=False)
    email = Column(String(200))
    especialidad = Column(String(200))

    tours = relationship("Tour", back_populates="proveedor")


class Tour(Base):
    __tablename__ = "tours"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(200), nullable=False)
    destino = Column(String(200), nullable=False)
    descripcion = Column(Text)
    duracion_dias = Column(Integer, nullable=False)
    precio_base = Column(Float, nullable=False)
    cupos_disponibles = Column(Integer, nullable=False, default=0)
    fecha_salida = Column(Date)
    incluye = Column(Text)
    categoria = Column(String(100))
    proveedor_id = Column(Integer, ForeignKey("proveedores.id"))

    proveedor = relationship("Proveedor", back_populates="tours")
