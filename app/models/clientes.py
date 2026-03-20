from sqlalchemy import Column, Integer, String
from app.database import Base


class Cliente(Base):
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(200), nullable=False)
    email = Column(String(200))
    telefono = Column(String(50))
    whatsapp = Column(String(50))
    documento = Column(String(50))
    canal = Column(String(20), default="web")  # "web" o "whatsapp"
