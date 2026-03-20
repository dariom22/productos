"""Definición de herramientas (tools) que el agente puede usar."""

TOOLS = [
    {
        "name": "buscar_tours",
        "description": "Busca tours disponibles. Puede filtrar por destino, categoría, rango de precio o duración.",
        "input_schema": {
            "type": "object",
            "properties": {
                "destino": {
                    "type": "string",
                    "description": "Destino del tour (ej: 'Bariloche', 'Cancún')"
                },
                "categoria": {
                    "type": "string",
                    "description": "Categoría del tour (ej: 'aventura', 'playa', 'cultural', 'naturaleza')"
                },
                "precio_maximo": {
                    "type": "number",
                    "description": "Precio máximo en USD"
                },
                "duracion_maxima": {
                    "type": "integer",
                    "description": "Duración máxima en días"
                }
            },
            "required": []
        }
    },
    {
        "name": "obtener_detalle_tour",
        "description": "Obtiene los detalles completos de un tour específico por su ID.",
        "input_schema": {
            "type": "object",
            "properties": {
                "tour_id": {
                    "type": "integer",
                    "description": "ID del tour"
                }
            },
            "required": ["tour_id"]
        }
    },
    {
        "name": "crear_reserva",
        "description": "Crea una nueva reserva para un tour. Necesita datos del cliente y el tour.",
        "input_schema": {
            "type": "object",
            "properties": {
                "nombre_cliente": {
                    "type": "string",
                    "description": "Nombre completo del cliente"
                },
                "email_cliente": {
                    "type": "string",
                    "description": "Email del cliente"
                },
                "telefono_cliente": {
                    "type": "string",
                    "description": "Teléfono del cliente"
                },
                "documento_cliente": {
                    "type": "string",
                    "description": "Número de documento del cliente"
                },
                "tour_id": {
                    "type": "integer",
                    "description": "ID del tour a reservar"
                },
                "cantidad_personas": {
                    "type": "integer",
                    "description": "Cantidad de personas para la reserva"
                }
            },
            "required": ["nombre_cliente", "email_cliente", "tour_id", "cantidad_personas"]
        }
    },
    {
        "name": "consultar_reserva",
        "description": "Consulta el estado de una reserva existente por email del cliente o ID de reserva.",
        "input_schema": {
            "type": "object",
            "properties": {
                "email": {
                    "type": "string",
                    "description": "Email del cliente"
                },
                "reserva_id": {
                    "type": "integer",
                    "description": "ID de la reserva"
                }
            },
            "required": []
        }
    },
    {
        "name": "cancelar_reserva",
        "description": "Cancela una reserva existente.",
        "input_schema": {
            "type": "object",
            "properties": {
                "reserva_id": {
                    "type": "integer",
                    "description": "ID de la reserva a cancelar"
                }
            },
            "required": ["reserva_id"]
        }
    }
]
