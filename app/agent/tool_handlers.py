"""Handlers que ejecutan las herramientas del agente contra la BD y servicios."""

from sqlalchemy.orm import Session

from app.models.tours import Tour, Proveedor
from app.models.clientes import Cliente
from app.models.reservas import Reserva, MensajeFlujo
from app.services.whatsapp import notificar_proveedor, pedir_pax_proveedor, notificar_cliente
from app.services.stripe_service import crear_link_pago


def buscar_tours(db: Session, destino: str = None, categoria: str = None,
                 precio_maximo: float = None, duracion_maxima: int = None) -> str:
    query = db.query(Tour).filter(Tour.cupos_disponibles > 0)
    if destino:
        query = query.filter(Tour.destino.ilike(f"%{destino}%"))
    if categoria:
        query = query.filter(Tour.categoria.ilike(f"%{categoria}%"))
    if precio_maximo:
        query = query.filter(Tour.precio_base <= precio_maximo)
    if duracion_maxima:
        query = query.filter(Tour.duracion_dias <= duracion_maxima)

    tours = query.all()
    if not tours:
        return "No se encontraron tours con esos criterios."

    lineas = []
    for t in tours:
        lineas.append(
            f"ID: {t.id} | {t.nombre} - {t.destino} | "
            f"{t.duracion_dias} días | USD {t.precio_base}/persona | "
            f"Cupos: {t.cupos_disponibles} | Categoría: {t.categoria}"
        )
    return "\n".join(lineas)


def detalle_tour(db: Session, tour_id: int) -> str:
    tour = db.query(Tour).filter(Tour.id == tour_id).first()
    if not tour:
        return f"No se encontró tour con ID {tour_id}."

    proveedor_info = ""
    if tour.proveedor:
        proveedor_info = f"\nProveedor: {tour.proveedor.nombre}"

    return (
        f"Tour: {tour.nombre}\nDestino: {tour.destino}\n"
        f"Descripción: {tour.descripcion}\nDuración: {tour.duracion_dias} días\n"
        f"Precio: USD {tour.precio_base} por persona\n"
        f"Cupos disponibles: {tour.cupos_disponibles}\n"
        f"Fecha de salida: {tour.fecha_salida}\n"
        f"Incluye: {tour.incluye}\nCategoría: {tour.categoria}{proveedor_info}"
    )


def crear_presupuesto(db: Session, tour_id: int, nombre_cliente: str,
                       cantidad_personas: int, email_cliente: str = None,
                       whatsapp_cliente: str = None) -> str:
    tour = db.query(Tour).filter(Tour.id == tour_id).first()
    if not tour:
        return f"No se encontró tour con ID {tour_id}."
    if tour.cupos_disponibles < cantidad_personas:
        return f"No hay suficientes cupos. Disponibles: {tour.cupos_disponibles}."

    # Buscar o crear cliente
    cliente = None
    if email_cliente:
        cliente = db.query(Cliente).filter(Cliente.email == email_cliente).first()
    if not cliente:
        cliente = Cliente(
            nombre=nombre_cliente, email=email_cliente,
            whatsapp=whatsapp_cliente
        )
        db.add(cliente)
        db.flush()

    precio_total = tour.precio_base * cantidad_personas
    reserva = Reserva(
        cliente_id=cliente.id, tour_id=tour.id,
        proveedor_id=tour.proveedor_id,
        cantidad_personas=cantidad_personas,
        precio_unitario=tour.precio_base, precio_total=precio_total,
        estado="presupuesto_enviado"
    )
    db.add(reserva)
    db.flush()

    _log_mensaje(db, reserva.id, "agente",
                 f"Presupuesto creado: {tour.nombre} x{cantidad_personas} = USD {precio_total}")
    db.commit()
    db.refresh(reserva)

    return (
        f"✅ Presupuesto creado (Reserva #{reserva.id})\n\n"
        f"Tour: {tour.nombre}\nDestino: {tour.destino}\n"
        f"Fecha: {tour.fecha_salida}\nDuración: {tour.duracion_dias} días\n"
        f"Personas: {cantidad_personas}\n"
        f"Precio por persona: USD {tour.precio_base}\n"
        f"TOTAL: USD {precio_total}\n"
        f"Incluye: {tour.incluye}\n\n"
        f"Estado: Esperando confirmación del cliente."
    )


def cliente_acepta_presupuesto(db: Session, reserva_id: int) -> str:
    reserva = db.query(Reserva).filter(Reserva.id == reserva_id).first()
    if not reserva:
        return f"Reserva {reserva_id} no encontrada."
    if reserva.estado != "presupuesto_enviado":
        return f"La reserva está en estado '{reserva.estado}', no se puede aceptar el presupuesto."

    reserva.estado = "esperando_proveedor"
    _log_mensaje(db, reserva.id, "cliente", "Aceptó el presupuesto")

    # Contactar al proveedor por WhatsApp
    proveedor = db.query(Proveedor).filter(Proveedor.id == reserva.proveedor_id).first()
    if proveedor:
        info = (
            f"Tour: {reserva.tour.nombre}\n"
            f"Destino: {reserva.tour.destino}\n"
            f"Fecha: {reserva.tour.fecha_salida}\n"
            f"Personas: {reserva.cantidad_personas}\n"
            f"Cliente: {reserva.cliente.nombre}\n"
            f"Reserva ID: {reserva.id}"
        )
        notificar_proveedor(proveedor.whatsapp, info)
        _log_mensaje(db, reserva.id, "agente",
                     f"Se contactó al proveedor {proveedor.nombre} por WhatsApp")

    db.commit()
    return (
        f"✅ Presupuesto aceptado. Se contactó al proveedor por WhatsApp.\n"
        f"Estado: Esperando respuesta del proveedor.\n"
        f"Te avisamos apenas tengamos novedades."
    )


def proveedor_responde(db: Session, reserva_id: int, confirma: bool,
                        notas: str = None, nuevo_precio: float = None) -> str:
    reserva = db.query(Reserva).filter(Reserva.id == reserva_id).first()
    if not reserva:
        return f"Reserva {reserva_id} no encontrada."

    if confirma:
        reserva.estado = "proveedor_confirmo"
        reserva.notas_proveedor = notas
        _log_mensaje(db, reserva.id, "proveedor", f"Confirmó. Notas: {notas or 'Sin notas'}")

        # Notificar al cliente
        msg = f"✅ El proveedor confirmó tu tour!\nReserva #{reserva.id}: {reserva.tour.nombre}"
        if notas:
            msg += f"\nNotas del proveedor: {notas}"
        msg += "\n\n¿Confirmás para proceder al pago?"

        if reserva.cliente.whatsapp:
            notificar_cliente(reserva.cliente.whatsapp, msg)

        db.commit()
        return f"Proveedor confirmó. Se notificó al cliente.\nEstado: proveedor_confirmo"
    else:
        reserva.estado = "cambios_enviados"
        reserva.notas_proveedor = notas
        if nuevo_precio:
            reserva.precio_unitario = nuevo_precio
            reserva.precio_total = nuevo_precio * reserva.cantidad_personas

        _log_mensaje(db, reserva.id, "proveedor", f"Propuso cambios: {notas}")

        msg = (
            f"⚠️ El proveedor propone cambios para tu tour (Reserva #{reserva.id}):\n"
            f"{notas or 'Ver detalles'}"
        )
        if nuevo_precio:
            msg += f"\nNuevo precio: USD {reserva.precio_total} total"
        msg += "\n\n¿Aceptás los cambios o preferís cancelar?"

        if reserva.cliente.whatsapp:
            notificar_cliente(reserva.cliente.whatsapp, msg)

        db.commit()
        return f"Cambios del proveedor enviados al cliente.\nEstado: cambios_enviados"


def cliente_confirma_final(db: Session, reserva_id: int) -> str:
    reserva = db.query(Reserva).filter(Reserva.id == reserva_id).first()
    if not reserva:
        return f"Reserva {reserva_id} no encontrada."
    if reserva.estado not in ("proveedor_confirmo", "cambios_enviados"):
        return f"La reserva está en estado '{reserva.estado}', no se puede confirmar."

    # Crear link de pago con Stripe
    descripcion = f"{reserva.tour.nombre} - {reserva.tour.destino} x{reserva.cantidad_personas}"
    pago = crear_link_pago(
        reserva_id=reserva.id,
        descripcion=descripcion,
        monto_usd=reserva.precio_total,
        email_cliente=reserva.cliente.email
    )

    reserva.estado = "pago_pendiente"
    reserva.stripe_payment_link = pago["url"]
    reserva.stripe_session_id = pago.get("session_id")
    _log_mensaje(db, reserva.id, "agente", f"Link de pago generado: {pago['url']}")

    # Enviar link por WhatsApp si tiene
    if reserva.cliente.whatsapp:
        msg = (
            f"💳 *Link de pago para tu tour*\n\n"
            f"Tour: {reserva.tour.nombre}\n"
            f"Total: USD {reserva.precio_total}\n\n"
            f"Pagá acá: {pago['url']}"
        )
        notificar_cliente(reserva.cliente.whatsapp, msg)

    db.commit()
    return (
        f"✅ Link de pago generado:\n{pago['url']}\n\n"
        f"Total: USD {reserva.precio_total}\n"
        f"Estado: pago_pendiente\n"
        f"{'(Modo simulación - no es un link real)' if pago.get('simulado') else ''}"
    )


def registrar_pago(db: Session, reserva_id: int) -> str:
    reserva = db.query(Reserva).filter(Reserva.id == reserva_id).first()
    if not reserva:
        return f"Reserva {reserva_id} no encontrada."

    reserva.estado = "pax_solicitado"
    _log_mensaje(db, reserva.id, "sistema", "Pago recibido exitosamente")

    # Pedir PAX al proveedor
    proveedor = db.query(Proveedor).filter(Proveedor.id == reserva.proveedor_id).first()
    if proveedor:
        info = (
            f"Reserva #{reserva.id}\n"
            f"Tour: {reserva.tour.nombre}\n"
            f"Cliente: {reserva.cliente.nombre}\n"
            f"Personas: {reserva.cantidad_personas}\n"
            f"Fecha: {reserva.tour.fecha_salida}"
        )
        pedir_pax_proveedor(proveedor.whatsapp, info)
        _log_mensaje(db, reserva.id, "agente", "Se solicitó el número de PAX al proveedor")

    if reserva.cliente.whatsapp:
        notificar_cliente(reserva.cliente.whatsapp,
                          f"✅ Pago recibido para Reserva #{reserva.id}! "
                          f"Estamos gestionando tu número de PAX con el proveedor.")

    db.commit()
    return (
        f"✅ Pago registrado para Reserva #{reserva.id}.\n"
        f"Se solicitó el PAX al proveedor por WhatsApp.\n"
        f"Estado: pax_solicitado"
    )


def proveedor_envia_pax(db: Session, reserva_id: int, numero_pax: str) -> str:
    reserva = db.query(Reserva).filter(Reserva.id == reserva_id).first()
    if not reserva:
        return f"Reserva {reserva_id} no encontrada."

    reserva.numero_pax = numero_pax
    reserva.estado = "pax_enviado"
    _log_mensaje(db, reserva.id, "proveedor", f"Número de PAX: {numero_pax}")

    # Enviar PAX al cliente
    if reserva.cliente.whatsapp:
        msg = (
            f"🎉 *Tu tour está confirmado!*\n\n"
            f"Tour: {reserva.tour.nombre}\n"
            f"Destino: {reserva.tour.destino}\n"
            f"Fecha: {reserva.tour.fecha_salida}\n"
            f"Número de PAX: {numero_pax}\n\n"
            f"¡Buen viaje! 🌍"
        )
        notificar_cliente(reserva.cliente.whatsapp, msg)
        _log_mensaje(db, reserva.id, "agente", f"PAX enviado al cliente: {numero_pax}")

    db.commit()
    return (
        f"✅ PAX enviado al cliente.\n"
        f"Número de PAX: {numero_pax}\n"
        f"Estado: pax_enviado (COMPLETADO)\n"
        f"🎉 Reserva #{reserva.id} finalizada exitosamente!"
    )


def cancelar_reserva(db: Session, reserva_id: int, motivo: str = None) -> str:
    reserva = db.query(Reserva).filter(Reserva.id == reserva_id).first()
    if not reserva:
        return f"Reserva {reserva_id} no encontrada."
    if reserva.estado == "cancelado":
        return "Esta reserva ya estaba cancelada."

    tour = db.query(Tour).filter(Tour.id == reserva.tour_id).first()
    if tour:
        tour.cupos_disponibles += reserva.cantidad_personas

    reserva.estado = "cancelado"
    _log_mensaje(db, reserva.id, "sistema", f"Cancelada. Motivo: {motivo or 'No especificado'}")
    db.commit()
    return f"Reserva #{reserva_id} cancelada. Se liberaron {reserva.cantidad_personas} cupos."


def ver_estado_reserva(db: Session, reserva_id: int = None, email: str = None) -> str:
    if reserva_id:
        reserva = db.query(Reserva).filter(Reserva.id == reserva_id).first()
        if not reserva:
            return f"Reserva {reserva_id} no encontrada."
        return _formato_reserva_completo(reserva)

    if email:
        cliente = db.query(Cliente).filter(Cliente.email == email).first()
        if not cliente:
            return f"No se encontró cliente con email {email}."
        reservas = db.query(Reserva).filter(Reserva.cliente_id == cliente.id).all()
        if not reservas:
            return "No hay reservas para este cliente."
        return "\n---\n".join(_formato_reserva_completo(r) for r in reservas)

    return "Necesito un ID de reserva o email para buscar."


def _formato_reserva_completo(reserva: Reserva) -> str:
    lineas = [
        f"Reserva #{reserva.id}",
        f"Tour: {reserva.tour.nombre} - {reserva.tour.destino}",
        f"Cliente: {reserva.cliente.nombre}",
        f"Personas: {reserva.cantidad_personas}",
        f"Precio total: USD {reserva.precio_total}",
        f"Estado: {reserva.estado}",
    ]
    if reserva.notas_proveedor:
        lineas.append(f"Notas proveedor: {reserva.notas_proveedor}")
    if reserva.stripe_payment_link:
        lineas.append(f"Link de pago: {reserva.stripe_payment_link}")
    if reserva.numero_pax:
        lineas.append(f"PAX: {reserva.numero_pax}")

    if reserva.mensajes:
        lineas.append("\nHistorial:")
        for m in reserva.mensajes:
            lineas.append(f"  [{m.origen}] {m.mensaje}")

    return "\n".join(lineas)


def _log_mensaje(db: Session, reserva_id: int, origen: str, mensaje: str):
    db.add(MensajeFlujo(reserva_id=reserva_id, origen=origen, mensaje=mensaje))


HANDLER_MAP = {
    "buscar_tours": buscar_tours,
    "detalle_tour": detalle_tour,
    "crear_presupuesto": crear_presupuesto,
    "cliente_acepta_presupuesto": cliente_acepta_presupuesto,
    "proveedor_responde": proveedor_responde,
    "cliente_confirma_final": cliente_confirma_final,
    "registrar_pago": registrar_pago,
    "proveedor_envia_pax": proveedor_envia_pax,
    "cancelar_reserva": cancelar_reserva,
    "ver_estado_reserva": ver_estado_reserva,
}
