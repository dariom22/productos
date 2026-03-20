"""Agente principal de la agencia de tours usando Claude API."""

import os

import anthropic
from sqlalchemy.orm import Session

from app.agent.tools import TOOLS
from app.agent.tool_handlers import HANDLER_MAP

SYSTEM_PROMPT = """Eres un agente de atención al cliente de una agencia de tours llamada "Viajes Fantásticos".

Tu rol es:
- Ayudar a los clientes a encontrar el tour perfecto para ellos
- Responder preguntas sobre destinos, precios, duración e itinerarios
- Gestionar reservas (crear, consultar y cancelar)
- Ser amable, entusiasta y profesional

Reglas:
- Siempre responde en español
- Si el cliente quiere reservar, asegurate de pedirle: nombre completo, email, y cantidad de personas
- Antes de confirmar una reserva, mostrá el resumen con el precio total
- Si no hay tours disponibles para lo que busca, sugerí alternativas
- Usá las herramientas disponibles para buscar tours y gestionar reservas
"""


def run_agent(user_message: str, db: Session,
              conversation_history: list = None) -> dict:
    """Ejecuta el agente con un mensaje del usuario y retorna la respuesta."""
    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

    if conversation_history is None:
        conversation_history = []

    conversation_history.append({"role": "user", "content": user_message})

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        tools=TOOLS,
        messages=conversation_history,
    )

    while response.stop_reason == "tool_use":
        tool_results = []
        assistant_content = response.content

        for block in response.content:
            if block.type == "tool_use":
                tool_name = block.name
                tool_input = block.input
                handler = HANDLER_MAP.get(tool_name)

                if handler:
                    result = handler(db, **tool_input)
                else:
                    result = f"Herramienta '{tool_name}' no disponible."

                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": result
                })

        conversation_history.append({"role": "assistant", "content": assistant_content})
        conversation_history.append({"role": "user", "content": tool_results})

        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=conversation_history,
        )

    assistant_text = ""
    for block in response.content:
        if hasattr(block, "text"):
            assistant_text += block.text

    conversation_history.append({"role": "assistant", "content": response.content})

    return {
        "response": assistant_text,
        "conversation_history": conversation_history,
    }
