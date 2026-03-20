"""Handlers que ejecutan las herramientas del agente contra la base de datos."""

from sqlalchemy.orm import Session

from app.models.tours import Tour
from app.models.clientes import Cliente
from app.models.reservas import Reserva


def buscar_tours(db: Session, destino: str = None, categoria: str = None,
                 precio_maximo: float = None, duracion_maxima: int = None) -> str:
    query = db.query(Tour).filter(Tour.cupos_disponibles > 0)

    if destino:
        query = query.filter(Tour.destino.ilike(f"%{destino}%"))
    if categoria:
        query = query.filter(Tour.categoria.ilike(f"%{categoria}%"))
    if precio_maximo:
        query = query.filter(Tour.precio <= precio_maximo)
    if duracion_maxima:
        query = query.filter(Tour.duracion_dias <= duracion_maxima)

    tours = query.all()
    if not tours:
        return "No se encontraron tours con esos criterios."

    resultados = []
    for t in tours:
        resultados.append(
            f"ID: {t.id} | {t.nombre} - {t.destino} | "
            f"{t.duracion_dias} días | USD {t.precio} | "
            f"Cupos: {t.cupos_disponibles} | Categoría: {t.categoria}"
        )
    return "\n".join(resultados)


def obtener_detalle_tour(db: Session, tour_id: int) -> str:
    tour = db.query(Tour).filter(Tour.id == tour_id).first()
    if not tour:
        return f"No se encontró un tour con ID {tour_id}."

    return (
        f"Tour: {tour.nombre}\n"
        f"Destino: {tour.destino}\n"
        f"Descripción: {tour.descripcion}\n"
        f"Duración: {tour.duracion_dias} días\n"
        f"Precio: USD {tour.precio} por persona\n"
        f"Cupos disponibles: {tour.cupos_disponibles}\n"
        f"Fecha de salida: {tour.fecha_salida}\n"
        f"Incluye: {tour.incluye}\n"
        f"Categoría: {tour.categoria}"
    )


def crear_reserva(db: Session, nombre_cliente: str, email_cliente: str,
                   tour_id: int, cantidad_personas: int,
                   telefono_cliente: str = None,
                   documento_cliente: str = None) -> str:
    tour = db.query(Tour).filter(Tour.id == tour_id).first()
    if not tour:
        return f"No se encontró el tour con ID {tour_id}."

    if tour.cupos_disponibles < cantidad_personas:
        return (
            f"No hay suficientes cupos. Disponibles: {tour.cupos_disponibles}, "
            f"solicitados: {cantidad_personas}."
        )

    cliente = db.query(Cliente).filter(Cliente.email == email_cliente).first()
    if not cliente:
        cliente = Cliente(
            nombre=nombre_cliente,
            email=email_cliente,
            telefono=telefono_cliente,
            documento=documento_cliente
        )
        db.add(cliente)
        db.flush()

    precio_total = tour.precio * cantidad_personas
    reserva = Reserva(
        cliente_id=cliente.id,
        tour_id=tour.id,
        cantidad_personas=cantidad_personas,
        precio_total=precio_total
    )
    db.add(reserva)
    tour.cupos_disponibles -= cantidad_personas
    db.commit()
    db.refresh(reserva)

    return (
        f"Reserva creada exitosamente!\n"
        f"ID Reserva: {reserva.id}\n"
        f"Tour: {tour.nombre} - {tour.destino}\n"
        f"Cliente: {nombre_cliente} ({email_cliente})\n"
        f"Personas: {cantidad_personas}\n"
        f"Precio total: USD {precio_total}\n"
        f"Estado: {reserva.estado}"
    )


def consultar_reserva(db: Session, email: str = None,
                       reserva_id: int = None) -> str:
    if reserva_id:
        reserva = db.query(Reserva).filter(Reserva.id == reserva_id).first()
        if not reserva:
            return f"No se encontró la reserva con ID {reserva_id}."
        return _formatear_reserva(reserva)

    if email:
        cliente = db.query(Cliente).filter(Cliente.email == email).first()
        if not cliente:
            return f"No se encontró un cliente con email {email}."
        reservas = db.query(Reserva).filter(
            Reserva.cliente_id == cliente.id
        ).all()
        if not reservas:
            return "No se encontraron reservas para ese cliente."
        return "\n---\n".join(_formatear_reserva(r) for r in reservas)

    return "Necesito un email o un ID de reserva para buscar."


def cancelar_reserva(db: Session, reserva_id: int) -> str:
    reserva = db.query(Reserva).filter(Reserva.id == reserva_id).first()
    if not reserva:
        return f"No se encontró la reserva con ID {reserva_id}."

    if reserva.estado == "cancelada":
        return "Esta reserva ya estaba cancelada."

    tour = db.query(Tour).filter(Tour.id == reserva.tour_id).first()
    if tour:
        tour.cupos_disponibles += reserva.cantidad_personas

    reserva.estado = "cancelada"
    db.commit()

    return (
        f"Reserva {reserva_id} cancelada exitosamente. "
        f"Se liberaron {reserva.cantidad_personas} cupos."
    )


def _formatear_reserva(reserva: Reserva) -> str:
    return (
        f"Reserva ID: {reserva.id}\n"
        f"Tour: {reserva.tour.nombre} - {reserva.tour.destino}\n"
        f"Cliente: {reserva.cliente.nombre}\n"
        f"Personas: {reserva.cantidad_personas}\n"
        f"Precio total: USD {reserva.precio_total}\n"
        f"Estado: {reserva.estado}\n"
        f"Fecha: {reserva.fecha_reserva}"
    )


HANDLER_MAP = {
    "buscar_tours": buscar_tours,
    "obtener_detalle_tour": obtener_detalle_tour,
    "crear_reserva": crear_reserva,
    "consultar_reserva": consultar_reserva,
    "cancelar_reserva": cancelar_reserva,
}
