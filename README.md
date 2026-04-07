# Viajes Fantásticos - Agente de Tours

Agente inteligente para una agencia de tours. Usa Claude como motor de IA para atender clientes, buscar tours y gestionar reservas.

## Instalación

```bash
pip install -r requirements.txt
```

## Configuración

Crear un archivo `.env` con tu API key de Anthropic:

```bash
cp .env.example .env
# Editar .env con tu ANTHROPIC_API_KEY
```

## Ejecutar

```bash
uvicorn main:app --reload
```

La API estará disponible en `http://localhost:8000`.
La documentación interactiva (Swagger) en `http://localhost:8000/docs`.

## Endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | `/chat/` | Enviar mensaje al agente |
| DELETE | `/chat/{session_id}` | Limpiar conversación |
| GET | `/tours/` | Listar tours disponibles |
| GET | `/tours/{id}` | Detalle de un tour |
| GET | `/reservas/` | Listar reservas |
| GET | `/reservas/{id}` | Detalle de una reserva |

## Ejemplo de uso del chat

```bash
curl -X POST http://localhost:8000/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": "Hola, quiero ir a la playa", "session_id": "user1"}'
```

## Tours precargados

La app viene con 8 tours de ejemplo: Patagonia, Machu Picchu, Cancún, Kenia, Roma, Iguazú, Río de Janeiro y Mendoza.
