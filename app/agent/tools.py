"""Herramientas del agente para gestionar el flujo completo de tours."""

TOOLS = [
    {
        "name": "buscar_tours",
        "description": "Busca tours disponibles. Filtra por destino, categoría, precio o duración.",
        "input_schema": {
            "type": "object",
            "properties": {
                "destino": {"type": "string", "description": "Destino del tour"},
                "categoria": {"type": "string", "description": "Categoría: aventura, playa, cultural, naturaleza"},
                "precio_maximo": {"type": "number", "description": "Precio máximo en USD"},
                "duracion_maxima": {"type": "integer", "description": "Duración máxima en días"},
            },
            "required": []
        }
    },
    {
        "name": "detalle_tour",
        "description": "Obtiene detalles completos de un tour por ID.",
        "input_schema": {
            "type": "object",
            "properties": {
                "tour_id": {"type": "integer", "description": "ID del tour"}
            },
            "required": ["tour_id"]
        }
    },
    {
        "name": "crear_presupuesto",
        "description": "Crea un presupuesto para el cliente. Registra al cliente y genera la reserva en estado 'presupuesto_enviado'. Usa esto cuando el cliente muestra interés concreto en un tour.",
        "input_schema": {
            "type": "object",
            "properties": {
                "tour_id": {"type": "integer", "description": "ID del tour"},
                "nombre_cliente": {"type": "string", "description": "Nombre completo"},
                "email_cliente": {"type": "string", "description": "Email del cliente"},
                "whatsapp_cliente": {"type": "string", "description": "WhatsApp del cliente"},
                "cantidad_personas": {"type": "integer", "description": "Cantidad de personas"},
            },
            "required": ["tour_id", "nombre_cliente", "cantidad_personas"]
        }
    },
    {
        "name": "cliente_acepta_presupuesto",
        "description": "El cliente aceptó el presupuesto. Cambia estado a 'presupuesto_aceptado' y contacta al proveedor por WhatsApp.",
        "input_schema": {
            "type": "object",
            "properties": {
                "reserva_id": {"type": "integer", "description": "ID de la reserva"}
            },
            "required": ["reserva_id"]
        }
    },
    {
        "name": "proveedor_responde",
        "description": "Registra la respuesta del proveedor (confirmación o cambios).",
        "input_schema": {
            "type": "object",
            "properties": {
                "reserva_id": {"type": "integer", "description": "ID de la reserva"},
                "confirma": {"type": "boolean", "description": "True si confirma, False si propone cambios"},
                "notas": {"type": "string", "description": "Notas o cambios propuestos por el proveedor"},
                "nuevo_precio": {"type": "number", "description": "Nuevo precio si hubo cambios"},
            },
            "required": ["reserva_id", "confirma"]
        }
    },
    {
        "name": "cliente_confirma_final",
        "description": "El cliente confirma la propuesta final (después de que el proveedor confirmó). Genera el link de pago de Stripe.",
        "input_schema": {
            "type": "object",
            "properties": {
                "reserva_id": {"type": "integer", "description": "ID de la reserva"}
            },
            "required": ["reserva_id"]
        }
    },
    {
        "name": "registrar_pago",
        "description": "Registra que el pago fue completado. Contacta al proveedor para pedir el número de PAX.",
        "input_schema": {
            "type": "object",
            "properties": {
                "reserva_id": {"type": "integer", "description": "ID de la reserva"}
            },
            "required": ["reserva_id"]
        }
    },
    {
        "name": "proveedor_envia_pax",
        "description": "El proveedor envía el número de PAX. Se le pasa al cliente.",
        "input_schema": {
            "type": "object",
            "properties": {
                "reserva_id": {"type": "integer", "description": "ID de la reserva"},
                "numero_pax": {"type": "string", "description": "Número de PAX del tour"},
            },
            "required": ["reserva_id", "numero_pax"]
        }
    },
    {
        "name": "cancelar_reserva",
        "description": "Cancela una reserva en cualquier estado.",
        "input_schema": {
            "type": "object",
            "properties": {
                "reserva_id": {"type": "integer", "description": "ID de la reserva"},
                "motivo": {"type": "string", "description": "Motivo de la cancelación"},
            },
            "required": ["reserva_id"]
        }
    },
    {
        "name": "ver_estado_reserva",
        "description": "Consulta el estado actual de una reserva y su historial.",
        "input_schema": {
            "type": "object",
            "properties": {
                "reserva_id": {"type": "integer", "description": "ID de la reserva"},
                "email": {"type": "string", "description": "Email del cliente para buscar reservas"},
            },
            "required": []
        }
    },
]
